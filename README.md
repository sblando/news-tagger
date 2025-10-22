# 📰 NewsTagger v1

Tiny, explainable tooling to **download**, **tag**, and **summarize** a small news corpus. 

## What it does
- Fetches news via **NewsData.io** → `.txt` files in `./data`
- Classifies with a simple keyword **taxonomy** 
- Extracts light signals: frequent words, rough entities, date tokens, guessed locations
- Exports per-article **CSV/JSON** + a **category summary** CSV

## Layout
~~~
tools/download_news.py   # fetch TXT into ./data
src/news_tagger.py       # tagging + light extraction + exports
src/taxonomy.py          # categories + keywords
data/                    # generated
output/                  # generated (reports)
requirements.txt
~~~

## Quickstart

### 1) Environment 
~~~
python -m venv .venv
~~~

**Windows**
~~~
.venv\Scripts\Activate.ps1
pip install -U pip -r requirements.txt
~~~


### 2) Download news (needs a free NewsData.io API key)

**Minimal**
~~~
python tools/download_news.py --api-key YOUR_API_KEY
~~~

**Custom**
~~~
python tools/download_news.py \
  --api-key YOUR_API_KEY \
  --countries us,mx,es,ar,br \
  --categories business,technology \
  --per-country 5 \
  --out ./data
~~~

### 3) Tag & export

**Windows**
~~~
python src\news_tagger.py
~~~

**Options (example)**
~~~
--data ./data --out ./output --top 12 --min-matches 2 --disable-strong
~~~

## Outputs
~~~
output/report-YYYYMMDD-HHMMSS.csv
output/report-YYYYMMDD-HHMMSS.json
output/summary-YYYYMMDD-HHMMSS.csv
~~~

## Notes
- Language auto-set: `en` for `US/GB`, `es` otherwise (override with `--language-all`)
- Basic de-dup by link/title
- Headline-first by design; extend to body text if available

## Requirements
~~~
pandas>=2.2.0
requests>=2.31.0
~~~


