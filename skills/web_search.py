import urllib.request
import urllib.parse
import json
import sys

def search_ddg(query, count=5):
    """
    Performs a lightweight search using DuckDuckGo's HTML endpoint safely without API keys.
    """
    try:
        url = 'https://html.duckduckgo.com/html/?q=' + urllib.parse.quote(query)
        req = urllib.request.Request(
            url, 
            data=None, 
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        )
        with urllib.request.urlopen(req) as response:
            html = response.read().decode('utf-8')
            
        results = []
        
        # Super lightweight custom parser so we don't strictly require beautifulsoup for basic searches
        chunks = html.split('a class="result__url" href="')
        
        for chunk in chunks[1:]:
            if len(results) >= count:
                break
            
            try:
                link = chunk.split('"')[0]
                
                # Extract title
                title_start_tag = '<h2 class="result__title">'
                title_end_tag = '</h2>'
                if title_start_tag in chunk:
                    title_chunk = chunk.split(title_start_tag)[1].split(title_end_tag)[0]
                    title = title_chunk.split('>')[-2].split('<')[0].strip()
                else:
                    title = "Unknown Title"
                
                # Extract snippet
                snippet_start = 'class="result__snippet'
                if snippet_start in chunk:
                    snippet = chunk.split(snippet_start)[1].split('>')[1].split('<')[0].strip()
                else:
                    snippet = ""

                # Try to clean up DDG tracker wrapper
                if link.startswith('//duckduckgo.com/l/?uddg='):
                    link = urllib.parse.unquote(link.split('uddg=')[1].split('&')[0])

                if link and title:
                    results.append({
                        "title": title,
                        "url": link,
                        "snippet": snippet
                    })
            except Exception as e:
                continue
                
        return json.dumps(results, indent=2)
                
    except Exception as e:
        return json.dumps({"error": str(e)})

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Missing query argument. Usage: python web_search.py <query> [count]"}))
        sys.exit(1)
        
    query = sys.argv[1]
    count = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    
    print(search_ddg(query, count))
