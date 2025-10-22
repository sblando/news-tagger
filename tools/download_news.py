# -*- coding: utf-8 -*-
"""
Download a small corpus of news articles (plain text files) from multiple countries
using the NewsData.io API, suitable for the NewsTagger v1 project.

Usage:
  python3 tools/download_news.py --api-key YOUR_API_KEY
  python3 tools/download_news.py --api-key YOUR_API_KEY --countries us,mx,es,ar,br,co,cl,pe,cr,gb --per-country 1
  python3 tools/download_news.py --api-key YOUR_API_KEY --out ./data --categories business,technology

Notes:
- Language is auto-set: 'en' for US/GB, 'es' for others (you can override with --language-all).
- De-duplicates by link/title.
- Writes files like: data/US_001.txt, data/MX_001.txt, ...

"""

import os
import re
import time
import json
import argparse
from pathlib import Path
from typing import List, Dict, Set, Optional

import requests


API_URL = "https://newsdata.io/api/1/news"


DEFAULT_COUNTRIES = ["us", "mx", "es", "ar", "br", "co", "cl", "pe", "cr", "gb"]


def choose_language_for_country(country: str) -> str:
    """Heuristic: English for US/GB, Spanish otherwise."""
    if country.lower() in {"us", "gb"}:
        return "en"
    return "es"


def sanitize_text(s: Optional[str]) -> str:
    if not s:
        return ""
    # Normalize whitespace and strip control chars
    s = s.replace("\u00A0", " ")
    s = re.sub(r"\s+", " ", s).strip()
    return s


def pick_best_content(item: Dict) -> str:
    # Prefer 'content'; fall back to 'full_description' or 'description'
    for key in ("content", "full_description", "description"):
        val = item.get(key)
        if val and isinstance(val, str) and val.strip():
            return val
    return ""


def fetch_country_news(api_key: str,
                       country: str,
                       per_country: int,
                       categories: Optional[List[str]] = None,
                       language_all: Optional[str] = None,
                       sleep_seconds: float = 0.6) -> List[Dict]:
    """
    Fetch 'per_country' news items for the given country.
    Handles pagination via 'nextPage'. De-duplicates by link/title locally.
    """
    collected = []
    seen_links: Set[str] = set()
    seen_titles: Set[str] = set()

    params = {
        "apikey": api_key,
        "country": country.lower(),
    }

    # Language selection
    if language_all:
        params["language"] = language_all
    else:
        params["language"] = choose_language_for_country(country)

    # Categories (comma-separated)
    if categories:
        params["category"] = ",".join(categories)

    next_page = None

    while len(collected) < per_country:
        if next_page:
            params["page"] = next_page

        resp = requests.get(API_URL, params=params, timeout=20)
        if resp.status_code != 200:
            print(f"[{country.upper()}] HTTP {resp.status_code}: {resp.text[:200]}")
            break

        data = resp.json()
        results = data.get("results") or []

        if not results:
            print(f"[{country.upper()}] No more results.")
            break

        for item in results:
            if len(collected) >= per_country:
                break

            title = sanitize_text(item.get("title"))
            link = sanitize_text(item.get("link"))

            # Skip if missing both title and link
            if not title and not link:
                continue

            if link and link in seen_links:
                continue
            if title and title in seen_titles:
                continue

            content = sanitize_text(pick_best_content(item))
            if not content:
                # If there is absolutely no textual content, skip
                continue

            record = {
                "country": country.lower(),
                "language": params["language"],
                "title": title or "(no title)",
                "link": link or "(no link)",
                "pubDate": sanitize_text(item.get("pubDate")),
                "source_id": sanitize_text(item.get("source_id")),
                "category": item.get("category") or [],
                "content": content,
            }

            collected.append(record)
            if link:
                seen_links.add(link)
            if title:
                seen_titles.add(title)

        # Pagination
        next_page = data.get("nextPage")
        if not next_page:
            break

        # Be polite with the API
        time.sleep(sleep_seconds)

    return collected


def write_plain_text(out_dir: Path, country: str, idx: int, record: Dict) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    fname = f"{country.upper()}_{idx:03d}.txt"
    path = out_dir / fname

    header = [
        f"Title: {record['title']}",
        f"Date: {record.get('pubDate', '')}",
        f"Source: {record.get('source_id', '')}",
        f"Country: {record.get('country', '').upper()}",
        f"Language: {record.get('language', '')}",
        f"Link: {record.get('link', '')}",
        "",
        "----- CONTENT -----",
        "",
    ]
    body = record["content"]

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(header))
        f.write(body if body.startswith("\n") else "\n" + body)

    return path


def main():
    parser = argparse.ArgumentParser(description="Download a small international news corpus from NewsData.io")
    parser.add_argument("--api-key", required=True, help="Your NewsData.io API key")
    parser.add_argument("--countries", default=",".join(DEFAULT_COUNTRIES),
                        help="Comma-separated ISO2 country codes (e.g., us,mx,es,ar,br,co,cl,pe,cr,gb)")
    parser.add_argument("--per-country", type=int, default=1, help="How many articles per country (default: 1)")
    parser.add_argument("--out", default="./data", help="Output directory for .txt files (default: ./data)")
    parser.add_argument("--categories", default="",
                        help="Optional comma-separated categories (e.g., business,technology,top)")
    parser.add_argument("--language-all", default="",
                        help="Force a single language for all requests (e.g., en or es); leave empty for auto")
    args = parser.parse_args()

    api_key = args.api_key.strip()
    out_dir = Path(args.out)
    countries = [c.strip().lower() for c in args.countries.split(",") if c.strip()]
    categories = [c.strip().lower() for c in args.categories.split(",") if c.strip()] if args.categories else None
    language_all = args.language_all.strip().lower() or None

    total_written = 0

    for c in countries:
        print(f"[{c.upper()}] Fetching up to {args.per_country} article(s)...")
        items = fetch_country_news(
            api_key=api_key,
            country=c,
            per_country=args.per_country,
            categories=categories,
            language_all=language_all
        )
        if not items:
            print(f"[{c.upper()}] No items saved.")
            continue

        for i, rec in enumerate(items, start=1):
            path = write_plain_text(out_dir, c, i, rec)
            total_written += 1
            print(f"  - Saved: {path}")

    print(f"\nDone. Total files written: {total_written}")


if __name__ == "__main__":
    main()
