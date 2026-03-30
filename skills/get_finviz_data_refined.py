import requests
from bs4 import BeautifulSoup
import pandas as pd

def get_market_summary_finviz():
    url = "https://finviz.com/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    market_data = {
        'top_gainers': [],
        'top_losers': [],
        'sector_performance': []
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
        soup = BeautifulSoup(response.text, 'html.parser')

        # --- Top Gainers --- 
        # Finviz often has a table with id 'screener-content' or similar for these lists
        # Let's look for tables that might contain 'Top Gainers'
        gainers_table = soup.find('table', class_='table-condensed', width='100%') # This class is often used for such tables
        if gainers_table:
            # Look for a header that says 'Top Gainers' or similar to identify the correct table
            # This is a heuristic, might need adjustment if Finviz changes layout
            for caption in gainers_table.find_all('td', class_='table-top'):
                if 'Top Gainers' in caption.text:
                    # Assuming the actual data is in the next sibling table or within this one
                    # This part is tricky without seeing the live HTML
                    # For now, let's assume the data is in rows following the caption
                    current_table = caption.find_parent('table')
                    if current_table:
                        rows = current_table.find_all('tr')
                        for row in rows[1:6]: # Get top 5, skipping header
                            cols = row.find_all('td')
                            if len(cols) >= 3:
                                try:
                                    market_data['top_gainers'].append({
                                        'ticker': cols[0].text.strip(),
                                        'name': cols[1].text.strip(),
                                        'change_percent': float(cols[2].text.strip('%'))
                                    })
                                except (ValueError, IndexError):
                                    pass
                    break # Found gainers table, move on

        # --- Top Losers --- 
        # Similar logic for losers
        losers_table = soup.find('table', class_='table-condensed', width='100%')
        if losers_table:
            for caption in losers_table.find_all('td', class_='table-top'):
                if 'Top Losers' in caption.text:
                    current_table = caption.find_parent('table')
                    if current_table:
                        rows = current_table.find_all('tr')
                        for row in rows[1:6]: # Get top 5, skipping header
                            cols = row.find_all('td')
                            if len(cols) >= 3:
                                try:
                                    market_data['top_losers'].append({
                                        'ticker': cols[0].text.strip(),
                                        'name': cols[1].text.strip(),
                                        'change_percent': float(cols[2].text.strip('%'))
                                    })
                                except (ValueError, IndexError):
                                    pass
                    break

        # --- Sector Performance --- 
        # This is usually in a separate section, often a heatmap or a table.
        # Finviz has a 'Sectors' link, but for a quick summary, we might find a table on the homepage.
        # Let's look for a table with sector data. This is highly dependent on Finviz's current layout.
        sector_table = soup.find('table', class_='table-condensed', width='100%') # Re-using this class, might be different
        if sector_table:
            for caption in sector_table.find_all('td', class_='table-top'):
                if 'Sectors' in caption.text:
                    current_table = caption.find_parent('table')
                    if current_table:
                        rows = current_table.find_all('tr')
                        for row in rows[1:]: # Skip header
                            cols = row.find_all('td')
                            if len(cols) >= 2:
                                try:
                                    market_data['sector_performance'].append({
                                        'sector': cols[0].text.strip(),
                                        'change_percent': float(cols[1].text.strip('%'))
                                    })
                                except (ValueError, IndexError):
                                    pass
                    break

    except requests.exceptions.RequestException as e:
        print(f"Error fetching Finviz data: {e}")
    except Exception as e:
        print(f"An unexpected error occurred during Finviz scraping: {e}")

    return market_data

if __name__ == '__main__':
    finviz_data = get_market_summary_finviz()
    print(finviz_data)
