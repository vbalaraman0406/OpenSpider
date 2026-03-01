import urllib.request
import urllib.parse
import sys
import os

try:
    from bs4 import BeautifulSoup
    import markdownify
except ImportError:
    print("Error: Missing dependencies. Please run 'pip install beautifulsoup4 markdownify'")
    sys.exit(1)

def fetch_and_convert(url, max_chars=50000):
    """
    Fetches a URL, strips out script/style tags, and returns clean Markdown.
    """
    if not url.startswith('http'):
        url = 'https://' + url

    try:
        req = urllib.request.Request(
            url, 
            data=None, 
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        )
        with urllib.request.urlopen(req) as response:
            html = response.read().decode('utf-8', errors='ignore')
            
        soup = BeautifulSoup(html, 'html.parser')
        
        # Kill all script and style elements
        for script in soup(["script", "style", "nav", "footer", "iframe", "noscript"]):
            script.extract()
            
        # Get purely the main content if possible, else the body
        main_content = soup.find('main') or soup.find('article') or soup.find('body') or soup
            
        # Convert to Markdown
        md = markdownify.markdownify(str(main_content), heading_style="ATX", strip=['img', 'a'])
        
        # Clean up excessive newlines
        lines = [line.strip() for line in md.splitlines()]
        clean_md = '\n'.join(line for line in lines if line)
        
        # Truncate if it's insanely long
        if len(clean_md) > max_chars:
            clean_md = clean_md[:max_chars] + f"\n\n... [TRUNCATED after {max_chars} characters]"
            
        return clean_md
                
    except Exception as e:
        return f"Error fetching {url}: {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Error: Missing URL argument. Usage: python web_fetch.py <url> [max_chars]")
        sys.exit(1)
        
    url = sys.argv[1]
    max_chars = int(sys.argv[2]) if len(sys.argv) > 2 else 50000
    
    output = fetch_and_convert(url, max_chars)
    print(output)
