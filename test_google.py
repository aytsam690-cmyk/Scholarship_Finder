import requests
from bs4 import BeautifulSoup
import urllib.parse

def google_search(query, num_results=5):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }
    url = f"https://www.google.com/search?q={urllib.parse.quote(query)}&num={num_results}"
    resp = requests.get(url, headers=headers)
    soup = BeautifulSoup(resp.text, 'html.parser')
    results = []
    for a in soup.find_all('a'):
        href = a.get('href', '')
        if '/url?q=' in href:
            # extract the actual URL
            link = href.split('/url?q=')[1].split('&')[0]
            link = urllib.parse.unquote(link)
            if link.startswith('http') and 'google' not in link:
                title_div = a.find('h3')
                title = title_div.text if title_div else link
                results.append({"title": title, "url": link})
                if len(results) >= num_results:
                    break
    return results

if __name__ == "__main__":
    res = google_search("test internship", num_results=2)
    for r in res:
        print(r)


