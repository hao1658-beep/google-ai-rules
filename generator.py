#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
generator.py
每天运行一次更新以下平台域名：
1. Google AI / Gemini / DeepMind
2. OpenAI / ChatGPT
3. Claude / Anthropic

输出：
- google-ai.conf
- openai.conf
- claude.conf
- all-ai.conf（所有平台合并）
"""

import re
import requests
from pathlib import Path


# ------------------------------
# 规则源 URL（可随时扩展）
# ------------------------------

GOOGLE_SOURCES = [
    "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Surge/Gemini/Gemini.list",
    "https://raw.githubusercontent.com/limbopro/Profiles4limbo/main/AI_Platforms.list",
]

OPENAI_SOURCES = [
    "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Surge/OpenAI/OpenAI.list",
    "https://raw.githubusercontent.com/limbopro/Profiles4limbo/main/OpenAI.list",
]

CLAUDE_SOURCES = [
    "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Surge/Claude/Claude.list",
    "https://raw.githubusercontent.com/limbopro/Profiles4limbo/main/Claude.list",
]


# ------------------------------
# 输出文件路径
# ------------------------------
GOOGLE_CONF = Path("google-ai.conf")
OPENAI_CONF = Path("openai.conf")
CLAUDE_CONF = Path("claude.conf")
ALL_CONF = Path("all-ai.conf")


# ------------------------------
# 工具函数：拉取域名
# ------------------------------
def fetch_domains(urls: list, keywords: list) -> set:
    domains: set[str] = set()

    for url in urls:
        try:
            print(f"[+] Fetching {url}")
            r = requests.get(url, timeout=15)
            r.raise_for_status()
            text = r.text
        except Exception as e:
            print(f"[!] Fetch failed: {url} → {e}")
            continue

        for line in text.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            m = re.search(r"\bDOMAIN(?:-SUFFIX)?\s*,\s*([^,]+)", line)
            if not m:
                continue

            d = m.group(1).strip().lower()

            if any(k in d for k in keywords):
                if "." in d:
                    domains.add(d)

    return domains


# ------------------------------
# 写文件 helper
# ------------------------------
def write_conf(path: Path, domains: list, title="# Auto generated"):
    lines = [title]
    for d in domains:
        lines.append(f"DOMAIN-SUFFIX,{d},PROXY")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"[+] Updated: {path}")


# ------------------------------
# 主程序
# ------------------------------
def main():
    print("========== Updating AI Rules ==========")

    # -------------------------
    # Google AI / Gemini
    # -------------------------
    google = fetch_domains(
        GOOGLE_SOURCES,
        ["google", "gemini", "deepmind", "aistudio", "bard", "makersuite", "palm"]
    )
    google = sorted(google)
    write_conf(GOOGLE_CONF, google, "# ==== Google AI / Gemini ====")

    # -------------------------
    # OpenAI / ChatGPT
    # -------------------------
    openai = fetch_domains(
        OPENAI_SOURCES,
        ["openai", "chatgpt", "oaiusercontent", "sora", "api.openai"]
    )
    openai = sorted(openai)
    write_conf(OPENAI_CONF, openai, "# ==== OpenAI ====")

    # -------------------------
    # Claude / Anthropic
    # -------------------------
    claude = fetch_domains(
        CLAUDE_SOURCES,
        ["anthropic", "claude", "claude-api"]
    )
    claude = sorted(claude)
    write_conf(CLAUDE_CONF, claude, "# ==== Claude / Anthropic ====")

    # -------------------------
    # 合并 all-ai.conf
    # -------------------------
    all_domains = sorted(set(google) | set(openai) | set(claude))
    write_conf(ALL_CONF, all_domains, "# ==== All AI Platforms Combined ====")

    print("[+] All tasks completed.")


if __name__ == "__main__":
    main()
