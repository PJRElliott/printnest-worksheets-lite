#!/usr/bin/env python3
"""
PrintNest Worksheets Pro — Brand Setup
=======================================
Run this ONCE after installing the skill into ~/.claude/skills/
It replaces __YOUR_BRAND__ / __YOUR_SHOP__ placeholders inside all
generator scripts and metadata files with your actual brand & Etsy
shop name.

Usage:
    python3 ~/.claude/skills/printnest-worksheets-pro/setup.py

You can re-run anytime to change the brand.
"""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CFG_PATH = ROOT / "brand.json"

DEFAULT_CFG = {
    "brand_name": "YourBrand",
    "etsy_shop_url_path": "YourShop",
    "author": "YourBrand Press",
    "copyright_year": "2026",
}


def prompt(label: str, default: str) -> str:
    ans = input(f"{label} [{default}]: ").strip()
    return ans or default


def load_or_init_config() -> dict:
    if CFG_PATH.exists():
        cfg = json.loads(CFG_PATH.read_text())
        print(f"\nLoaded existing brand.json:")
        for k, v in cfg.items():
            print(f"  {k} = {v}")
        if prompt("Reuse these values? (y/n)", "y").lower().startswith("y"):
            return cfg

    print("\n=== PrintNest Worksheets Pro: Brand Setup ===")
    cfg = {
        "brand_name": prompt("Brand name (shown on every PDF footer)", DEFAULT_CFG["brand_name"]),
        "etsy_shop_url_path": prompt("Etsy shop URL path (etsy.com/shop/<this>)", DEFAULT_CFG["etsy_shop_url_path"]),
        "author": prompt("Author/publisher name (printed on PDF title page)", DEFAULT_CFG["author"]),
        "copyright_year": prompt("Copyright year", DEFAULT_CFG["copyright_year"]),
    }
    CFG_PATH.write_text(json.dumps(cfg, indent=2, ensure_ascii=False))
    print(f"\nSaved -> {CFG_PATH}")
    return cfg


def replace_in_tree(cfg: dict) -> int:
    """Walk scripts/ and references/, replace placeholders with config values."""
    replacements = [
        ("__YOUR_BRAND__", cfg["brand_name"]),
        ("__YOUR_SHOP__", cfg["etsy_shop_url_path"]),
    ]
    targets = []
    for d in ("scripts", "references"):
        for ext in (".py", ".json", ".md", ".txt"):
            targets.extend((ROOT / d).rglob(f"*{ext}"))

    touched = 0
    for f in targets:
        try:
            text = f.read_text()
        except UnicodeDecodeError:
            continue
        orig = text
        for old, new in replacements:
            text = text.replace(old, new)
        if text != orig:
            f.write_text(text)
            touched += 1
    return touched


def main():
    cfg = load_or_init_config()
    n = replace_in_tree(cfg)
    print(f"\nReplaced placeholders in {n} files.")
    print("\nSetup complete. You can now run:")
    print(f"  python3 {ROOT}/scripts/generate_math.py --book math_kg")
    print(f"  python3 {ROOT}/scripts/generate_alphabet.py --book alphabet_prek")
    print("Or ask Claude: \"Math Workbook を Kindergarten向けに作って\"")


if __name__ == "__main__":
    main()
