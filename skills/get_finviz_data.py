import requests
from bs4 import BeautifulSoup

def get_market_summary():
    url = "https://finviz.com/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
        soup = BeautifulSoup(response.text, 'html.parser')

        market_summary = {}

        # S&P 500 and NASDAQ data
        # Finviz often has a table with major index performance
        # This is a general approach, may need adjustment based on Finviz's current HTML structure
        # Looking for a table with class 't-row-base' or similar for indices
        index_table = soup.find('table', class_='t-row-base')
        if index_table:
            rows = index_table.find_all('tr')
            for row in rows:
                cols = row.find_all('td')
                if len(cols) > 1:
                    index_name = cols[0].text.strip()
                    if 'S&P 500' in index_name or 'NASDAQ' in index_name:
                        # Assuming structure: Name, Last, Change, %Change, High, Low, Volume
                        try:
                            last_price = float(cols[1].text.replace(',', ''))
                            change = float(cols[2].text.replace(',', ''))
                            percent_change = float(cols[3].text.strip('%'))
                            # Volume might be in a different column or not directly available for indices
                            # For now, we'll focus on price and change
                            market_summary[index_name] = {
                                'closing_price': last_price,
                                'daily_change': change,
                                'daily_change_percent': percent_change
                            }
                        except (ValueError, IndexError):
                            pass

        # Top Gainers, Top Losers, Most Active (often in separate tables or sections)
        # This part is highly dependent on Finviz's HTML structure and might require specific selectors
        # For demonstration, let's assume there are tables with specific IDs or classes
        # This is a placeholder and will likely need refinement.
        gainers = []
        losers = []
        
        # Example: Find tables for gainers/losers. This is a common pattern.
        # You'd look for specific table headers or surrounding divs.
        # For now, let's just try to find any tables that might contain this data.
        all_tables = soup.find_all('table')
        for table in all_tables:
            # Heuristic: look for common headers like 'Gainers', 'Losers'
            if 'Gainers' in table.text or 'Top Gainers' in table.text:
                # Parse gainers table
                for row in table.find_all('tr')[1:]:
                    cols = row.find_all('td')
                    if len(cols) > 2:
                        try:
                            gainers.append({
                                'ticker': cols[0].text.strip(),
                                'name': cols[1].text.strip(),
                                'change_percent': float(cols[2].text.strip('%'))
                            })
                        except (ValueError, IndexError):
                            pass
            elif 'Losers' in table.text or 'Top Losers' in table.text:
                # Parse losers table
                for row in table.find_all('tr')[1:]:
                    cols = row.find_all('td')
                    if len(cols) > 2:
                        try:
                            losers.append({
                                'ticker': cols[0].text.strip(),
                                'name': cols[1].text.strip(),
                                'change_percent': float(cols[2].text.strip('%'))
                            })
                        except (ValueError, IndexError):
                            pass
        
        market_summary['top_gainers'] = gainers[:5] # Limit to top 5
        market_summary['top_losers'] = losers[:5]   # Limit to top 5

        # Sector Performance - Finviz has a heatmap, but getting structured data is hard via simple scrape
        # Will skip for now or look for a simpler table if available.

        return market_summary

    except requests.exceptions.RequestException as e:
        print(f"Error fetching Finviz data: {e}")
        return None

if __name__ == '__main__':
    data = get_market_summary()
    if data:
        print(data)
    else:
        print("Failed to retrieve market summary from Finviz.")