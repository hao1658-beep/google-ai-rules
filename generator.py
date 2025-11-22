#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
generator.py
每天运行一次：
1. 从公开规则源拉取最新 Google AI / Gemini / DeepMind 相关域名
2. 过滤出跟 google / gemini / ai 相关的域名
3. 去重、去掉已经手写在 google-ai.conf 里的域名
4. 把新域名以 DOMAIN-SUFFIX,xxx,PROXY 形式追加到 google-ai.conf
"""

import re
import requests
from pathlib import Path

# 公开规则源（以后想加可以在这里扩展）
SOURCE_URLS = [
    # blackmatrix7 Gemini 规则（含 gemini / deepmind 等）
    "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Surge/Gemini/Gemini.list",
    # 一个常见的 AI 平台合集规则（里面也有 Gemini 相关域名）
    "https://raw.githubusercontent.com/limbopro/Profiles4limbo/main/AI_Platforms.list",
]

# 仓库中的主配置文件
CONF_PATH = Path("google-ai.conf")


def fetch_google_ai_domains() -> set:
    """从多个远程规则源中抓取可能属于 Google AI / Gemini 的域名"""
    domains: set[str] = set()

    for url in SOURCE_URLS:
        try:
            print(f"[+] Fetching from {url}")
            resp = requests.get(url, timeout=15)
            resp.raise_for_status()
            text = resp.text
        except Exception as e:
            print(f"[!] Failed to fetch {url}: {e}")
            continue

        for line in text.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            # 支持类似：
            # DOMAIN-SUFFIX,gemini.google.com
            # DOMAIN,ai.google.dev
            m = re.search(r"\bDOMAIN(?:-SUFFIX)?\s*,\s*([^,]+)", line)
            if not m:
                continue

            d = m.group(1).strip()

            # 只要 Google / Gemini / DeepMind 相关
            low = d.lower()
            if "google" not in low:
                continue
            if not any(k in low for k in ["gemini", "ai.", "aistudio", "deepmind", "palm", "makersuite", "bard"]):
                continue

            # 简单排除明显非域名
            if "." not in d:
                continue

            domains.add(d)

    print(f"[+] Collected {len(domains)} candidate domains")
    return domains


def read_existing_domains_from_conf(conf_text: str) -> set:
    """从现有 google-ai.conf 中读出已经存在的 DOMAIN-SUFFIX 域名，避免重复"""
    existing: set[str] = set()
    for line in conf_text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        m = re.search(r"DOMAIN-SUFFIX\s*,\s*([^,]+)", line)
        if m:
            existing.add(m.group(1).strip())
    return existing


def main() -> None:
    if not CONF_PATH.exists():
        raise SystemExit("google-ai.conf not found. Please create it first.")

    base_text = CONF_PATH.read_text(encoding="utf-8")

    # 1. 读取现有已经写死的域名
    existing = read_existing_domains_from_conf(base_text)
    print(f"[+] Existing DOMAIN-SUFFIX entries: {len(existing)}")

    # 2. 抓取远程规则中的候选域名
    candidates = fetch_google_ai_domains()

    # 3. 过滤掉已存在的
    new_domains = sorted(d for d in candidates if d not in existing)
    print(f"[+] New domains to append: {len(new_domains)}")

    # 4. 生成新的配置文本
    lines = base_text.rstrip().splitlines()
    lines.append("")  # 确保有一个空行
    lines.append("# ==== Auto generated Google AI domains (PROXY) ====")

    for d in new_domains:
        lines.append(f"DOMAIN-SUFFIX,{d},PROXY")

    new_text = "\n".join(lines) + "\n"
    CONF_PATH.write_text(new_text, encoding="utf-8")
    print("[+] google-ai.conf updated.")


if __name__ == "__main__":
    main()
