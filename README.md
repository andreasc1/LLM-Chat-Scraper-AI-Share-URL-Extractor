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
- 🔎 Fetches share URLs from Web Archive CDX API  
- 📂 Scrapes **ChatGPT**, **Claude**, and **Grok** share pages  
- 🧹 Filters out UI/boilerplate text, saving **only clean chat content**  
- 🎛️ Interactive CLI: scrape **All**, a **Range**, or a **Number** of URLs  
- 🕵️ Random User-Agents + delays to avoid detection  
- ⚡ Uses **Playwright** for robust JavaScript rendering  

---

## Installation  

1. Clone the repo:  
   ```bash
   git clone https://github.com/yourusername/live-chat-scraper.git
   cd live-chat-scraper
   ```
Install dependencies:

   ```bash
  pip install -r requirements.txt
  ```
  Install Playwright browsers (first-time setup only):
  ```bash
  playwright install
  Usage
  ```
Run the script:

  ```bash
  Copy code
  python scraper.py
  ```
You’ll be prompted to:

Select a source (ChatGPT, Claude, or Grok)

Choose whether to scrape All, a Range, or a Specific number of URLs

The script will fetch, scrape, and save results into a text file (e.g. scraped_content.txt).

Example
  ```
Fetching share URLs for ChatGPT...
✅ Found 103347 URLs for ChatGPT.
Scrape (A)ll, (R)ange, or (N)umber? R
Enter range (1-103347): 888-891

🔹 Scraping: https://chatgpt.com/share/714ea0c0-04b4-40e4-8c02-2e0059b4d854
✅ Scraped successfully.

🔹 Scraping: https://chatgpt.com/share/675489e9-36e8-800e-a8b8-0d4d296a0a6b
✅ Scraped successfully.
  ```
The cleaned results are saved in:
  ```

scraped_content.txt
  ```

⭐ If you found this useful, don’t forget to star the repo!

