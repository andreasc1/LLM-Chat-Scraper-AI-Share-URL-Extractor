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
async def scrape_chat_live(page, url, source_name):
    """
    Scrape chat messages from a live share URL.
    """
    try:
        print(f"\n🔹 Scraping ({source_name}): {url}")
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
            print("⚠ No chat messages found.")
            return None

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

        return "\n\n".join(filtered).strip() if filtered else None

    except Exception as e:
        print(f"❌ Error scraping {url}: {e}")
        return None

# ----------------------------
# Helper: choose URLs
# ----------------------------
def select_urls(urls):
    while True:
        choice = input("Scrape (A)ll, (R)ange, or (N)umber? ").upper()
        if choice == "A":
            return urls
        elif choice == "R":
            try:
                start, end = map(int, input(f"Enter range (1-{len(urls)}): ").split("-"))
                if 1 <= start <= end <= len(urls):
                    return urls[start-1:end]
            except:
                pass
            print("❌ Invalid range.")
        elif choice == "N":
            try:
                count = int(input(f"Enter number of URLs (1-{len(urls)}): "))
                if 1 <= count <= len(urls):
                    return urls[:count]
            except:
                print("❌ Invalid number.")
        else:
            print("❌ Invalid choice.")

# ----------------------------
# Main async function
# ----------------------------
async def main():
    parser = argparse.ArgumentParser(description="Scrape live chatbot share URLs.")
    parser.add_argument("--proxy", help="SOCKS/HTTP proxy (e.g., socks5://127.0.0.1:9050)")
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

    output_file = "scraped_content.txt"
    if os.path.exists(output_file):
        os.remove(output_file)

    # ----------------------------
    # Select source(s)
    # ----------------------------
    print("Select a source:")
    print("  0: All")
    for i, s in enumerate(sources):
        print(f"  {i+1}: {s['name']}")
    choice = input("Enter choice: ")

    if choice == "0":
        selected_sources = sources
    elif choice.isdigit() and 1 <= int(choice) <= len(sources):
        selected_sources = [sources[int(choice)-1]]
    else:
        print("❌ Invalid choice.")
        return

    async with async_playwright() as p:
        launch_opts = {"headless": True}
        if args.proxy:
            launch_opts["proxy"] = {"server": args.proxy}
        browser = await p.chromium.launch(**launch_opts)
        page = await browser.new_page(user_agent=random.choice(user_agents))

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
            urls_to_scrape = select_urls(urls)
            print(f"▶ Scraping {len(urls_to_scrape)} URLs from {source['name']}...\n")

            with open(output_file, "a", encoding="utf-8") as f:
                for i, url in enumerate(urls_to_scrape):
                    await page.set_extra_http_headers({"User-Agent": random.choice(user_agents)})
                    text = await scrape_chat_live(page, url, source["name"])
                    if text:
                        f.write(f"--- Start of {url} ---\n{text}\n--- End of {url} ---\n\n")
                    print(f"Processed {i+1}/{len(urls_to_scrape)}")
                    time.sleep(random.uniform(2, 4))  # polite delay

        await browser.close()

    print(f"\n✅ Scraping complete! Saved to '{output_file}'")

# ----------------------------
# Run
# ----------------------------
if __name__ == "__main__":
    asyncio.run(main())
