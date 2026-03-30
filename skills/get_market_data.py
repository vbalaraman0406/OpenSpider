import yfinance as yf
import datetime

def get_index_data(ticker):
    try:
        # Get data for the last 2 trading days to calculate daily change
        data = yf.download(ticker, period="2d", interval="1d")
        
        if data.empty or len(data) < 2:
            # If not enough data for 2 days, try a longer period to ensure we get previous day's close
            data = yf.download(ticker, period="5d", interval="1d")
            if data.empty or len(data) < 2:
                print(f"Not enough trading data for {ticker} in the last 5 days.")
                return None

        # Get the latest two trading days' data
        latest_day_data = data.iloc[-1]
        previous_day_data = data.iloc[-2]

        closing_price = latest_day_data['Close']
        trading_volume = latest_day_data['Volume']
        
        daily_change = 0.0
        daily_change_percent = 0.0

        previous_close = previous_day_data['Close']
        daily_change = closing_price - previous_close
        if previous_close != 0:
            daily_change_percent = (daily_change / previous_close) * 100

        return {
            'closing_price': round(closing_price, 2),
            'daily_change': round(daily_change, 2),
            'daily_change_percent': round(daily_change_percent, 2),
            'trading_volume': int(trading_volume)
        }
    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")
        return None

if __name__ == '__main__':
    sp500_data = get_index_data('^GSPC')
    nasdaq_data = get_index_data('^IXIC')

    print("S&P 500 Data:", sp500_data)
    print("NASDAQ Data:", nasdaq_data)
