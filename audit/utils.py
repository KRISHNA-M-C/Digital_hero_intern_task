import re

def get_default_headers():
    """
    Returns standard browser headers to simulate a real user request,
    reducing the likelihood of getting blocked by targets.
    """
    return {
        'User-Agent': (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/120.0.0.0 Safari/537.36'
        ),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
    }

def count_words(body_soup):
    """
    Extracts visible text from the BeautifulSoup body element,
    excluding script and style tag contents, and returns an approximate word count.
    """
    if not body_soup:
        return 0
    
    # Clone or work on the soup safely (we can just extract in place if it's already a copy,
    # or remove script/style tags from it).
    # Since we might want to keep the original, we will decompose script and style.
    for element in body_soup(["script", "style"]):
        element.decompose()
        
    text = body_soup.get_text(separator=' ')
    # Clean up whitespace and split words
    words = re.findall(r'\b\w+\b', text)
    return len(words)
