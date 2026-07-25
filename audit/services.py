import time
import requests
from bs4 import BeautifulSoup
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from .utils import get_default_headers, count_words

class AuditError(Exception):
    """Base exception for audit application errors."""
    pass

class InvalidUrlError(AuditError):
    """Raised when the URL format is invalid or unsupported."""
    pass

class TimeoutError(AuditError):
    """Raised when the target website takes too long to respond."""
    pass

class NonHtmlResponseError(AuditError):
    """Raised when the target website returns content other than HTML."""
    pass

class WebsiteUnreachableError(AuditError):
    """Raised when the website is down, blocked, or connection is refused."""
    pass

def analyze_url(url):
    """
    Fetches the given URL, calculates performance, and extracts SEO-related metrics.
    
    Raises custom AuditError exceptions on failures.
    """
    # 1. Validate URL
    validator = URLValidator()
    try:
        validator(url)
    except ValidationError:
        raise InvalidUrlError("Please enter a valid URL (including http:// or https://).")
        
    if not (url.startswith('http://') or url.startswith('https://')):
        raise InvalidUrlError("URL must start with http:// or https://.")

    headers = get_default_headers()
    
    # 2. Fetch webpage with response timing
    start_time = time.perf_counter()
    try:
        # Use a reasonable timeout (e.g. 10 seconds)
        response = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
    except requests.exceptions.Timeout:
        raise TimeoutError("The request timed out. The website took too long to respond.")
    except (requests.exceptions.ConnectionError, requests.exceptions.URLRequired):
        raise WebsiteUnreachableError("The website is unreachable. Please verify the URL or try again later.")
    except requests.exceptions.RequestException as e:
        raise WebsiteUnreachableError(f"Failed to reach the website: {str(e)}")
        
    end_time = time.perf_counter()
    
    # Calculate response time in milliseconds
    elapsed_ms = int((end_time - start_time) * 1000)
    response_time_str = f"{elapsed_ms} ms"
    
    # 3. Check response Content-Type
    content_type = response.headers.get('Content-Type', '')
    if 'text/html' not in content_type:
        raise NonHtmlResponseError("The request returned a non-HTML response. Only HTML webpages can be audited.")
        
    # 4. Parse content using BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Title
    title = None
    if soup.title and soup.title.string:
        title = soup.title.string.strip()
    elif soup.title:
        title = soup.title.text.strip()
        
    # Meta Description
    meta_desc = None
    meta_tag = soup.find('meta', attrs={'name': lambda x: x and x.lower() == 'description'})
    if meta_tag and meta_tag.get('content'):
        meta_desc = meta_tag.get('content').strip()
        
    # H1 Count
    h1_count = len(soup.find_all('h1'))
    
    # Images missing alt text
    images = soup.find_all('img')
    images_missing_alt = 0
    for img in images:
        if not img.has_attr('alt') or not img['alt'].strip():
            images_missing_alt += 1
            
    # Word Count (inside body, script/styles ignored)
    body = soup.find('body')
    if body:
        word_count = count_words(body)
    else:
        word_count = count_words(soup)
        
    return {
        "status": response.status_code,
        "response_time": response_time_str,
        "title": title,
        "meta_description": meta_desc,
        "h1_count": h1_count,
        "images_missing_alt": images_missing_alt,
        "word_count": word_count
    }
