import httpx
from selectolax.parser import HTMLParser

def scrape_static_page(url: str, selector: str):
    response = httpx.get(url)
    response.raise_for_status()
    html = HTMLParser(response.text)
    # Extract data using CSS selector
    return [node.text() for node in html.css(selector)]

# Example usage:
if __name__ == "__main__":
    titles = scrape_static_page('https://docs.blender.org/api/current/info_overview.html', 'body')
    print(titles)