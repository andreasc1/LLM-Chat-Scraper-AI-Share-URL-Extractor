import asyncio
import random
import time
import os
import argparse
import requests
from playwright.async_api import async_playwright

# ----------------------------
# Scraper function
# ----------------------------
async def scrape_chat_live(context, url, source_name, semaphore):
    """
    Scrape chat messages from a live share URL using a browser context.
    """
    async with semaphore:  # Limit concurrent requests
        page = None
        try:
            print(f"🔹 Scraping ({source_name}): {url}")
            page = await context.new_page()
            
            # Set random user agent
            user_agents = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"
            ]
            await page.set_extra_http_headers({"User-Agent": random.choice(user_agents)})
            
            await page.goto(url, timeout=30000)  # 30s timeout

            # Selectors per source
            if source_name == "ChatGPT":
                chat_selector = 'div.prose p'
            elif source_name == "Claude":
                chat_selector = 'div[class*="Text"]'  # adjust if needed
            elif source_name == "Grok":
                chat_selector = 'div[class*="message"] p'  # adjust if needed
            else:
                chat_selector = 'p'

            await page.wait_for_selector(chat_selector, timeout=30000)
            elements = await page.locator(chat_selector).all()
            if not elements:
                print(f"⚠ No chat messages found for {url}")
                return url, None

            messages = []
            for elem in elements:
                text = await elem.inner_text()
                if len(text.split()) > 5:
                    messages.append(text.strip())

            # Remove unwanted boilerplate text
            unwanted_phrases = [
                "Log in", "Sign up", "can make mistakes",
                "Temporary Chat", "Skip to content", "By messaging", "What can I help with"
            ]
            filtered = [m for m in messages if not any(u.lower() in m.lower() for u in unwanted_phrases)]
            
            result = "\n\n".join(filtered).strip() if filtered else None
            print(f"✅ Scraped {url} - {len(filtered) if filtered else 0} messages")
            return url, result

        except Exception as e:
            print(f"❌ Error scraping {url}: {e}")
            return url, None
        finally:
            if page:
                await page.close()
            # Add small delay to be polite
            await asyncio.sleep(random.uniform(0.5, 1.5))

# ----------------------------
# Helper: choose URLs
# ----------------------------
def select_urls(urls, mode="all", range_str=None, count=None):
    if mode == "all":
        return urls
    elif mode == "range" and range_str:
        try:
            start, end = map(int, range_str.split("-"))
            if 1 <= start <= end <= len(urls):
                return urls[start-1:end]
        except:
            print("❌ Invalid range format. Using all URLs.")
            return urls
    elif mode == "number" and count:
        if 1 <= count <= len(urls):
            return urls[:count]
        else:
            print(f"❌ Invalid count {count}. Using all URLs.")
            return urls
    return urls

# ----------------------------
# Main async function
# ----------------------------
async def main():
    parser = argparse.ArgumentParser(description="Scrape live chatbot share URLs.")
    parser.add_argument("--proxy", help="SOCKS/HTTP proxy (e.g., socks5://127.0.0.1:9050)")
    parser.add_argument("--source", type=int, choices=[0, 1, 2, 3], default=0, 
                       help="Source selection: 0=All, 1=ChatGPT, 2=Claude, 3=Grok")
    parser.add_argument("--mode", choices=["all", "range", "number"], default="all",
                       help="URL selection mode")
    parser.add_argument("--range", help="Range for URLs (e.g., '1-10')")
    parser.add_argument("--count", type=int, help="Number of URLs to scrape")
    parser.add_argument("--parallel", type=int, default=10, 
                       help="Number of parallel workers (default: 10)")
    args = parser.parse_args()

    sources = [
        {"name": "ChatGPT", "url": "https://web.archive.org/cdx/search/cdx?url=chatgpt.com/share/*&output=txt&collapse=urlkey&fl=original&page=/"},
        {"name": "Claude",  "url": "https://web.archive.org/cdx/search/cdx?url=https://claude.ai/share/*&output=txt&collapse=urlkey&fl=original&page=/"},
        {"name": "Grok",    "url": "https://web.archive.org/cdx/search/cdx?url=grok.com/s/*&output=txt&collapse=urlkey&fl=original&page=/"}
    ]

    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"
    ]

    # Use output directory if running in Docker, otherwise current directory
    output_dir = "/app/output" if os.path.exists("/app/output") else "."
    output_file = os.path.join(output_dir, "scraped_content.txt")
    if os.path.exists(output_file):
        os.remove(output_file)

    # ----------------------------
    # Select source(s)
    # ----------------------------
    if args.source == 0:
        selected_sources = sources
        print("🔹 Selected: All sources")
    else:
        selected_sources = [sources[args.source-1]]
        print(f"🔹 Selected: {sources[args.source-1]['name']}")

    # Create semaphore to limit concurrent requests
    semaphore = asyncio.Semaphore(args.parallel)
    
    async with async_playwright() as p:
        launch_opts = {"headless": True}
        if args.proxy:
            launch_opts["proxy"] = {"server": args.proxy}
        browser = await p.chromium.launch(**launch_opts)
        context = await browser.new_context()

        for source in selected_sources:
            # ----------------------------
            # Fetch share URLs
            # ----------------------------
            print(f"\nFetching share URLs for {source['name']}...")
            try:
                headers = {"User-Agent": random.choice(user_agents)}
                resp = requests.get(source["url"], headers=headers, timeout=30)
                resp.raise_for_status()
                urls = list(set(resp.text.strip().split("\n")))
            except Exception as e:
                print(f"❌ Error fetching URLs for {source['name']}: {e}")
                continue

            if not urls:
                print(f"⚠ No URLs found for {source['name']}.")
                continue

            print(f"✅ Found {len(urls)} URLs for {source['name']}.")
            urls_to_scrape = select_urls(urls, args.mode, args.range, args.count)
            print(f"▶ Scraping {len(urls_to_scrape)} URLs from {source['name']} with {args.parallel} parallel workers...\n")

            # ----------------------------
            # Parallel scraping with incremental saving
            # ----------------------------
            tasks = [
                scrape_chat_live(context, url, source["name"], semaphore) 
                for url in urls_to_scrape
            ]
            
            # Process in batches and save incrementally to reduce memory usage
            batch_size = args.parallel * 2  # Process 2x parallel workers at a time
            successful_scrapes = 0
            
            for i in range(0, len(tasks), batch_size):
                batch = tasks[i:i + batch_size]
                print(f"Processing batch {i//batch_size + 1}/{(len(tasks) + batch_size - 1)//batch_size}")
                batch_results = await asyncio.gather(*batch, return_exceptions=True)
                
                # Save results immediately after each batch completes
                with open(output_file, "a", encoding="utf-8") as f:
                    for result in batch_results:
                        if isinstance(result, tuple) and len(result) == 2:
                            url, text = result
                            if text:
                                f.write(f"--- Start of {url} ---\n{text}\n--- End of {url} ---\n\n")
                                successful_scrapes += 1
                
                # Progress update
                completed = min(i + batch_size, len(tasks))
                print(f"Completed {completed}/{len(tasks)} URLs - {successful_scrapes} successful so far")
            
            print(f"✅ {source['name']}: {successful_scrapes}/{len(urls_to_scrape)} URLs scraped successfully")

        await browser.close()

    print(f"\n✅ Scraping complete! Saved to '{output_file}'")

# ----------------------------
# Run
# ----------------------------
if __name__ == "__main__":
    asyncio.run(main())
