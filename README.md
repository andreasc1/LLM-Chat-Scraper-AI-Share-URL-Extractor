# Live Chat Scraper – AI Share URL Extractor

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://www.python.org/)  
[![Playwright](https://img.shields.io/badge/Playwright-Automation-green)](https://playwright.dev/)  
[![AI Vibe](https://img.shields.io/badge/Vibe%20Coded-AI-purple)](#)

A Python tool that scrapes chat content from **live share URLs** of **ChatGPT, Claude, and Grok**.

It first pulls URLs from the **Web Archive CDX API**:

- `https://web.archive.org/cdx/search/cdx?url=chatgpt.com/share/*&output=txt&collapse=urlkey&fl=original&page=/`
- `https://web.archive.org/cdx/search/cdx?url=https://claude.ai/share/*&output=txt&collapse=urlkey&fl=original&page=/`
- `https://web.archive.org/cdx/search/cdx?url=grok.com/s/*&output=txt&collapse=urlkey&fl=original&page=/`

Then it uses **Playwright** to open each live page, handle JavaScript-rendered content, strip out UI clutter, and save only the **clean chat messages** to a text file.

✨ Built for speed, simplicity, and fun – and of course, **vibe coded using AI** 🤖

---

## Features

🔎 Fetches share URLs from Web Archive CDX API  
 📂 Scrapes **ChatGPT**, **Claude**, and **Grok** share pages  
 🧹 Filters out UI/boilerplate text, saving **only clean chat content**  
 🎛️ Interactive CLI: scrape **All**, a **Range**, or a **Number** of URLs  
 🕵️ Random User-Agents + delays to avoid detection  
 ⚡ Uses **Playwright** for robust JavaScript rendering

---

## Installation

1. Clone the repo:
   ```bash
   git clone git@github.com:andreasc1/LLM-Chat-Scraper-AI-Share-URL-Extractor.git
   cd LLM-Chat-Scraper-AI-Share-URL-Extractor
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Install Playwright browsers (first-time setup only):
   ```bash
   playwright install
   ```

### Run the script:

**Interactive mode:**

```bash
python scraper.py
```

**Non-interactive mode (great for Docker):**

```bash
# Scrape all sources, first 5 URLs each with 10 parallel workers
python scraper.py --source 0 --mode number --count 5 --parallel 10

# Scrape only ChatGPT, first 50 URLs with 20 parallel workers
python scraper.py --source 1 --mode number --count 50 --parallel 20

# Scrape Claude, URLs 50-100 with 5 parallel workers (be gentle)
python scraper.py --source 2 --mode range --range "50-100" --parallel 5

# Scrape all URLs from Grok with maximum speed
python scraper.py --source 3 --mode all --parallel 15
```

## Script Arguments

### `--source` (Source Selection)

Selects which chatbot platform to scrape:

- `0` - All sources (ChatGPT, Claude, and Grok)
- `1` - ChatGPT only
- `2` - Claude only
- `3` - Grok only

**Example:** `--source 1` scrapes only ChatGPT share URLs

### `--mode` (URL Selection Mode)

Determines how many URLs to scrape:

- `all` - Scrape all found URLs (can be thousands)
- `range` - Scrape a specific range of URLs (requires `--range`)
- `number` - Scrape the first N URLs (requires `--count`)

**Example:** `--mode number` limits scraping to a specific count

### `--range` (URL Range)

When using `--mode range`, specifies which URLs to scrape by position.
Format: `"start-end"` (1-indexed)

**Example:** `--range "50-100"` scrapes URLs 50 through 100

### `--count` (URL Count)

When using `--mode number`, specifies how many URLs to scrape from the beginning.

**Example:** `--count 20` scrapes the first 20 URLs found

### `--parallel` (Parallel Workers)

Number of concurrent browser instances for faster scraping.

- Default: 10
- Higher values = faster but more resource intensive
- Lower values = slower but gentler on target sites

**Example:** `--parallel 5` uses 5 concurrent workers

### `--proxy` (Proxy Server)

Optional proxy server for requests (useful for privacy or bypassing restrictions).
Supports SOCKS5 and HTTP proxies.

**Example:** `--proxy socks5://127.0.0.1:9050` routes traffic through Tor
You’ll be prompted to:

Select a source (ChatGPT, Claude, or Grok)

Choose whether to scrape All, a Range, or a Specific number of URLs

The script will fetch, scrape, and save results into a text file (e.g. scraped_content.txt).

---

## Docker Usage

### Interactive Mode (with Docker Compose)

For interactive usage where you want to select options via prompts:

```bash
# Build and run interactively
docker-compose up --build

# Or run without rebuilding
docker-compose up
```

This will start the container with an interactive terminal where you can select sources and scraping options.

### Unattended Mode (with Docker Compose)

For automated/unattended usage with predefined parameters:

```bash
# Run with specific parameters (no interaction required)
docker-compose run --rm scraper python scraper.py --source 1 --mode number --count 20 --parallel 10

# Examples for different scenarios:
# Scrape all ChatGPT URLs with 15 parallel workers
docker-compose run --rm scraper python scraper.py --source 1 --mode all --parallel 15

# Scrape first 50 Claude URLs with 5 parallel workers
docker-compose run --rm scraper python scraper.py --source 2 --mode number --count 50 --parallel 5

# Scrape Grok URLs 100-200 with 8 parallel workers
docker-compose run --rm scraper python scraper.py --source 3 --mode range --range "100-200" --parallel 8
```

### Manual Docker Build

If you prefer building and running manually:

```bash
# Build the image
docker build -t chat-scraper .

# Run unattended with custom parameters
docker run --rm -v $(pwd)/output:/app/output chat-scraper --source 0 --mode number --count 20 --parallel 10

# Run interactively
docker run --rm -it -v $(pwd)/output:/app/output chat-scraper
```

The output will be saved to the `./output/` directory on your host machine.

---

### Demo:

![me](assets/demo.gif)

### Example output:

```
Fetching share URLs for ChatGPT...
✅ Found 103347 URLs for ChatGPT.
Scrape (A)ll, (R)ange, or (N)umber? R
Enter range (1-103347): 888-891

 Scraping: https://chatgpt.com/share/714ea0c0-04b4-40e4-8c02-2e0059b4d854
✅ Scraped successfully.

🔹 Scraping: https://chatgpt.com/share/675489e9-36e8-800e-a8b8-0d4d296a0a6b
✅ Scraped successfully.
```

### Results output:

The cleaned results are saved in:

```
scraped_content.txt
```

⭐ If you found this useful, don’t forget to star the repo!
