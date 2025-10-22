"""
NewsTagger — Title-based classification (improved)
- Title (+ Description if present) only
- Strong-keywords: allow single-hit classification when present
- Min matches configurable (default=2)
- Avoid generic Technology terms
- Exports reason/score/hits for transparency

Usage:
  python src/news_tagger.py
  python src/news_tagger.py --data ./data --out ./output --top 12 --min-matches 2
  python src/news_tagger.py --disable-strong
"""

import os
import re
import json
import argparse
import unicodedata
from datetime import datetime
from collections import Counter, defaultdict
from typing import List, Dict, Optional, Tuple

import pandas as pd

from taxonomy import TAXONOMY, DEFAULT_CATEGORY

# Optional STRONG_KEYWORDS support (safe fallback if not defined in taxonomy.py)
try:
    from taxonomy import STRONG_KEYWORDS  # type: ignore
except Exception:
    STRONG_KEYWORDS = {}  # no strong keywords defined


# =============================
# Config / constants
# =============================

# overly generic tech terms (avoid easy false positives)
GENERIC_TECH_TERMS = {
    "tecnologia", "technology",
    "datos", "data",
    "plataforma", "platform",
    "software"
}

# Stopwords for top-words extraction (lightweight)
COMMON_STOPWORDS = {
    # Spanish
    "el", "la", "los", "las", "y", "en", "de", "del", "un", "una", "que", "por", "con", "a", "o",
    "se", "al", "como", "su", "sus", "para", "es", "son", "fue", "ser", "esta", "este", "estos",
    # English
    "the", "and", "of", "in", "to", "for", "on", "is", "are", "be", "as", "by", "it", "that", "at",
    # Portuguese (basic)
    "o", "a", "os", "as", "de", "do", "da", "e", "em", "para", "que", "com", "no", "na"
}

# Known places for tiny GPE heuristic (kept from earlier version)
KNOWN_LOCATIONS = [
    "costa rica", "estados unidos", "ee uu", "mexico", "espana", "españa", "argentina", "brasil",
    "colombia", "chile", "peru", "reino unido", "gran bretana", "francia", "alemania", "italia",
    "japon", "china", "lima", "bogota", "sao paulo", "rio de janeiro",
    "united states", "mexico", "spain", "argentina", "brazil", "colombia", "chile", "peru",
    "united kingdom", "france", "germany", "italy", "japan", "china", "london", "madrid",
    "paris", "berlin", "rome", "tokyo", "beijing", "lisbon", "porto", "portugal",
]


# =============================
# Utilities
# =============================

def normalize_text_remove_accents(text: str) -> str:
    """Lowercase + accent stripping (for robust keyword matching)."""
    if not isinstance(text, str):
        return ""
    normalized = unicodedata.normalize("NFKD", text)
    without_accents = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    return without_accents.lower()


def read_text_file(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def list_text_files(folder: str) -> List[str]:
    if not os.path.isdir(folder):
        return []
    paths = [os.path.join(folder, name) for name in os.listdir(folder) if name.lower().endswith(".txt")]
    paths.sort()
    return paths


def ensure_directory_exists(folder: str):
    os.makedirs(folder, exist_ok=True)


def tokenize_alpha_words(text: str) -> List[str]:
    """Return simple alphabetic tokens (keeps letters incl. ñ/Ñ)."""
    return re.findall(r"[a-zA-ZáéíóúÁÉÍÓÚñÑ]+", text)


# =============================
# Header parsing (Title / Description)
# =============================

HEADER_PATTERNS = {
    "title": re.compile(r"^Title:\s*(.*)$", flags=re.IGNORECASE | re.MULTILINE),
    # We don't write Description by default, but support it if present
    "description": re.compile(r"^Description:\s*(.*)$", flags=re.IGNORECASE | re.MULTILINE),
}

def parse_header_fields(full_text: str) -> Dict[str, Optional[str]]:
    """Extract Title and (if present) Description from the header lines."""
    title_match = HEADER_PATTERNS["title"].search(full_text)
    desc_match = HEADER_PATTERNS["description"].search(full_text)
    title = title_match.group(1).strip() if title_match else ""
    description = desc_match.group(1).strip() if desc_match else ""
    return {"title": title, "description": description}


# =============================
# Heuristic entity extraction (from title/description text)
# =============================

def extract_entities_basic(text_for_entities: str, max_items: int = 15) -> Dict[str, List[str]]:
    """
    Very lightweight heuristics applied to (title + description):
      - DATE: simple formats
      - ENTITIES: 2–4 capitalized token sequences
      - GPE: presence of places from a small curated list
    """
    normalized_for_search = normalize_text_remove_accents(text_for_entities)

    # Dates
    date_pattern = re.compile(
        r"(\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|\b\d{4}\b|"
        r"\b\d{1,2}\s+de\s+[a-z]+?\s+de\s+\d{4}\b|"
        r"\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{1,2},\s+\d{4}\b)",
        flags=re.IGNORECASE
    )
    found_dates = list(dict.fromkeys(date_pattern.findall(text_for_entities)))

    # Capitalized multi-word sequences
    cap_sequence_pattern = re.compile(
        r"\b([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(?:\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+){1,3})\b"
    )
    raw_candidates = cap_sequence_pattern.findall(text_for_entities)
    banned_leading_words = {"El", "La", "Los", "Las", "Un", "Una", "De", "Del", "Y", "En", "Da", "Do", "A"}
    entity_candidates = []
    for candidate in raw_candidates:
        if all(tok not in banned_leading_words for tok in candidate.split()):
            entity_candidates.append(candidate)
    unique_entities = list(dict.fromkeys(entity_candidates))[:max_items]

    # GPE detection
    gpe_found = []
    for place in KNOWN_LOCATIONS:
        if place in normalized_for_search:
            gpe_found.append(place)
    unique_gpe = list(dict.fromkeys(gpe_found))[:max_items]

    return {"DATE": found_dates[:max_items], "ENTITIES": unique_entities, "GPE": unique_gpe}


# =============================
# Classification helpers
# =============================

def collect_category_hits(text_for_matching: str) -> Dict[str, List[str]]:
    """
    Return dict[category] -> list of matched keywords.
    - text_for_matching must be lowercase & accent-free.
    - Skips generic Technology terms.
    """
    hits: Dict[str, List[str]] = {cat: [] for cat in TAXONOMY.keys()}
    for category, keyword_list in TAXONOMY.items():
        for keyword in keyword_list:
            normalized_keyword = normalize_text_remove_accents(keyword)

            # Skip overly generic tech terms to reduce false positives
            if category == "Technology" and normalized_keyword in GENERIC_TECH_TERMS:
                continue

            if re.search(rf"\b{re.escape(normalized_keyword)}\b", text_for_matching) or \
               normalized_keyword in text_for_matching:
                hits[category].append(normalized_keyword)
    return hits


def has_strong_hit(category: str, normalized_text: str) -> Tuple[bool, Optional[str]]:
    """
    Check if any strong keyword for `category` is present. Returns (bool, matched_keyword_or_None).
    """
    strong_list = STRONG_KEYWORDS.get(category, [])
    for kw in strong_list:
        nk = normalize_text_remove_accents(kw)
        if re.search(rf"\b{re.escape(nk)}\b", normalized_text) or nk in normalized_text:
            return True, nk
    return False, None


def select_category_with_reason(
    normalized_text: str,
    hits: Dict[str, List[str]],
    min_matches: int,
    allow_strong: bool
) -> Tuple[str, str, int, Dict[str, List[str]]]:
    """
    Decide final category using:
      - Highest score (=len(hits[cat]))
      - If best_score >= min_matches -> accept
      - Else, if allow_strong and category has a strong keyword -> accept
      - Else -> General
    Returns: (category, reason, best_score, hits)
    """
    scores = {cat: len(words) for cat, words in hits.items()}
    if not scores:
        return DEFAULT_CATEGORY, "no_hits", 0, hits

    best_category, best_score = max(scores.items(), key=lambda kv: kv[1])

    # Accept by score threshold
    if best_score >= min_matches and best_category:
        return best_category, f"score>={min_matches} ({best_score})", best_score, hits

    # Try strong keyword exception
    if allow_strong and best_category:
        ok, kw = has_strong_hit(best_category, normalized_text)
        if ok:
            return best_category, f"strong_keyword:{kw}", best_score, hits

    return DEFAULT_CATEGORY, "fallback:General", best_score, hits


# =============================
# Per-article analysis (TITLE-BASED)
# =============================

def analyze_news_article_from_title(file_path: str, top_n_words: int,
                                    min_matches: int,
                                    allow_strong: bool) -> Dict:
    """
    Analyze a news article using only Title (+ Description if present) from the header.
    """
    full_text = read_text_file(file_path)
    header = parse_header_fields(full_text)

    title = header.get("title", "") or ""
    description = header.get("description", "") or ""

    # Text to analyze/classify
    text_to_classify = (title + " " + description).strip()
    if not text_to_classify:
        # Fallback: use whole file if title not found (rare)
        text_to_classify = full_text

    # Normalize for matching
    normalized_for_matching = normalize_text_remove_accents(text_to_classify)

    # Tokens & top-N (from title/description only)
    tokens = [t.lower() for t in tokenize_alpha_words(text_to_classify)]
    normalized_tokens = [normalize_text_remove_accents(t) for t in tokens]
    filtered_tokens = [t for t in normalized_tokens if t not in COMMON_STOPWORDS and len(t) > 2]
    top_word_pairs = Counter(filtered_tokens).most_common(top_n_words)
    most_frequent_words = [w for w, _ in top_word_pairs]

    # Entities (from title/description)
    extracted_entities = extract_entities_basic(text_to_classify)

    # Category classification (collect hits + decide with reason)
    hits = collect_category_hits(normalized_for_matching)
    category, reason, score, all_hits = select_category_with_reason(
        normalized_for_matching, hits, min_matches, allow_strong
    )

    return {
        "file": os.path.basename(file_path),
        "title": title,
        "category": category,
        "category_reason": reason,
        "category_score": score,
        "category_hits": {k: v for k, v in all_hits.items() if v},  # only non-empty
        "most_frequent_words": most_frequent_words,
        "entities": extracted_entities.get("ENTITIES", []),
        "gpe": extracted_entities.get("GPE", []),
        "dates": extracted_entities.get("DATE", []),
    }


# =============================
# CLI / processing
# =============================

def main():
    parser = argparse.ArgumentParser(
        description="NewsTagger v1 (pandas, title-based) — keyword classifier + strong-keywords + basic entities"
    )
    parser.add_argument("--data", default="./data", help="Folder containing .txt news files")
    parser.add_argument("--out", default="./output", help="Output folder for JSON/CSV reports")
    parser.add_argument("--top", type=int, default=12, help="Top-N words to display per article")
    parser.add_argument("--min-matches", type=int, default=2, help="Minimum keyword hits to accept a category (without strong keyword)")
    parser.add_argument("--disable-strong", action="store_true", help="Disable strong-keyword single-hit acceptance")
    args = parser.parse_args()

    ensure_directory_exists(args.out)

    input_files = list_text_files(args.data)
    if not input_files:
        print(f"[Warn] No .txt files found in: {args.data}")
        return

    analyzed_articles: List[Dict] = []
    for path in input_files:
        try:
            article_result = analyze_news_article_from_title(
                file_path=path,
                top_n_words=args.top,
                min_matches=args.min_matches,
                allow_strong=(not args.disable_strong)
            )
            analyzed_articles.append(article_result)
        except Exception as exc:
            print(f"[Error] Failed processing {path}: {exc}")

    # Timestamped output filenames
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    json_output_path = os.path.join(args.out, f"report-{timestamp}.json")
    csv_output_path = os.path.join(args.out, f"report-{timestamp}.csv")
    summary_output_path = os.path.join(args.out, f"summary-{timestamp}.csv")

    # JSON export (detailed)
    with open(json_output_path, "w", encoding="utf-8") as jf:
        json.dump(analyzed_articles, jf, ensure_ascii=False, indent=2)

    # Flatten list fields for CSV
    flattened_rows = []
    for r in analyzed_articles:
        flattened_rows.append({
            "file": r.get("file", ""),
            "title": r.get("title", ""),
            "category": r.get("category", ""),
            "category_reason": r.get("category_reason", ""),
            "category_score": r.get("category_score", 0),
            "category_hits": ";".join([f"{k}:{','.join(v)}" for k, v in (r.get("category_hits", {}) or {}).items()]),
            "most_frequent_words": ";".join(r.get("most_frequent_words", [])),
            "entities": ";".join(r.get("entities", [])),
            "gpe": ";".join(r.get("gpe", [])),
            "dates": ";".join(r.get("dates", [])),
        })

    # CSV export (via pandas)
    df = pd.DataFrame(flattened_rows)
    df.to_csv(csv_output_path, index=False, encoding="utf-8")

    # Category summary (simple counts)
    summary = df["category"].value_counts().reset_index()
    summary.columns = ["category", "count"]
    summary.to_csv(summary_output_path, index=False, encoding="utf-8")

    print(f"[OK] Processed {len(analyzed_articles)} articles (title-based).")
    print(f"JSON: {json_output_path}")
    print(f"CSV : {csv_output_path}")
    print(f"Summary by category: {summary_output_path}")
    print("Tip: open the CSV in LibreOffice/Excel for a quick review.")


if __name__ == "__main__":
    main()
