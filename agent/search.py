import os
import logging
import requests
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def extract_text_from_html(html_content):
    """Extract useful textual content from HTML."""
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        # Remove script and style elements
        for script_or_style in soup(['script', 'style', 'noscript', 'header', 'footer', 'nav', 'aside']):
            script_or_style.decompose()
        
        text = soup.get_text(separator=' ', strip=True)
        return text
    except Exception as e:
        logging.error(f"Failed to parse HTML: {e}")
        return ""

def fetch_page(url, timeout=15):
    """Fetch a page and return its raw text, truncated to a reasonable length."""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/115.0.0.0 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        text = extract_text_from_html(response.text)
        # Truncate to ~10,000 characters to not consume too much LLM context
        return text[:10000]
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching {url}: {e}")
        return None

def perform_search(query, max_results=2):
    """
    Run a web search for the query using Google Search (via Serper API).
    
    To use this, you must sign up for a free API key at https://serper.dev/
    and add SERPER_API_KEY to your .env file.
    
    If no API key is provided, this will log an error and return empty results.
    """
    api_key = os.getenv("SERPER_API_KEY")
    if not api_key:
        logging.error("SERPER_API_KEY is missing. Cannot search Google.")
        # Fallback to duckduckgo just in case they want a fallback, but per request, we want Google.
        logging.warning("Please add SERPER_API_KEY to your .env to enable Google Search.")
        return []
        
    results = []
    headers = {
        'X-API-KEY': api_key,
        'Content-Type': 'application/json'
    }
    payload = {
        "q": query,
        "num": max_results
    }
    
    try:
        response = requests.post("https://google.serper.dev/search", json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        # Parse organic results
        organic = data.get("organic", [])
        for res in organic[:max_results]:
            results.append({
                "title": res.get("title", ""),
                "url": res.get("link", "")
            })
    except Exception as e:
        logging.error(f"Google Search failed for query '{query}': {e}")
        
    return results

def run_searches(sources):
    """
    Given a list of source configurations, fetch candidate opportunities.
    Returns a list of candidate dictionaries.
    """
    candidates = []
    
    for source in sources:
        name = source.get("name", "Unknown Source")
        url_or_query = source.get("url", "")
        source_type = source.get("type", "fixed_page")
        
        logging.info(f"Processing source: {name} ({source_type})")
        
        if source_type == "fixed_page":
            text = fetch_page(url_or_query)
            if text:
                candidates.append({
                    "source_name": name,
                    "url": url_or_query,
                    "title": name,
                    "raw_text": text
                })
        
        elif source_type == "search_query":
            search_results = perform_search(url_or_query, max_results=2)
            for res in search_results:
                url = res["url"]
                title = res["title"]
                logging.info(f"  Fetching search result: {title} - {url}")
                text = fetch_page(url)
                if text:
                    candidates.append({
                        "source_name": f"{name} (Search Result)",
                        "url": url,
                        "title": title,
                        "raw_text": text
                    })
        else:
            logging.warning(f"Unknown source type '{source_type}' for source '{name}'")
            
    return candidates
