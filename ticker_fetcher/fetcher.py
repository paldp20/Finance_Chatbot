import os
import time
import yfinance as yf
import mysql.connector
import pandas_market_calendars as mcal
import pandas as pd
import traceback
import pytz
from datetime import datetime
 
DB_USER = os.environ.get('DB_USER')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
DB_NAME = 'tickers_db'
DB_HOST = 'db'
DB_PORT = 3306
 
def connect_to_db():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "db"),
        port=os.getenv("DB_PORT", 3306),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
    )
 
def wait_for_db():
    while True:
        try:
            conn = connect_to_db()
            conn.close()
            return
        except mysql.connector.Error:
            print("Unable to connect to the database. Retrying in 5 seconds...")
            time.sleep(5)

def is_market_open():
    # Get the NSE market calendar
    nse = mcal.get_calendar('NSE')

    # Get the current timestamp in IST
    ist = pytz.timezone("Asia/Kolkata")
    now = datetime.now(ist)
    print("Now in IST:", now)

    # Get market schedule for today in UTC
    market_schedule = nse.schedule(start_date=now.date(), end_date=now.date())

    # If no trading today (holiday/weekend)
    if market_schedule.empty:
        print("Market is closed today (weekend or holiday).")
        return False

    # Extract market open and close times in UTC and convert them to IST
    market_open = market_schedule.iloc[0]['market_open'].tz_convert("Asia/Kolkata")
    market_close = market_schedule.iloc[0]['market_close'].tz_convert("Asia/Kolkata")

    print("Market open (IST):", market_open)
    print("Market close (IST):", market_close)

    # Check if current time is within market hours
    market_open_now = market_open <= now <= market_close
    print("Is market open now:", market_open_now)
    return market_open_now

# def is_market_open():
#     # Get the NYSE calendar
#     nyse = mcal.get_calendar('NYSE')
 
#     # Get the current timestamp and make it timezone-naive
#     now = pd.Timestamp.now(tz='UTC').tz_localize(None)
#     print("Now its:",now)
 
#     # Get the market open and close times for today
#     market_schedule = nyse.schedule(start_date=now, end_date=now)
 
#     # If the market isn't open at all today (e.g., a weekend or holiday)
#     if market_schedule.empty:
#         print('market is empty')
#         return False
 
#     # Today's schedule
#     print("Today's schedule")
 
#     # Check if the current time is within the trading hours
#     market_open = market_schedule.iloc[0]['market_open'].tz_localize(None)
#     market_close = market_schedule.iloc[0]['market_close'].tz_localize(None)
#     print("market_open",market_open)
#     print("market_close",market_close)
 
#     market_open_now = market_open <= now <= market_close
#     print("Is market open now:",market_open_now)
#     return market_open_now
 
def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

#extra
def create_ticker_table():
    conn = connect_to_db()
    cursor = conn.cursor()
    
    create_table_query = """
    CREATE TABLE IF NOT EXISTS ticker_history (
        id INT AUTO_INCREMENT PRIMARY KEY,
        ticker VARCHAR(70),
        open DECIMAL(10, 2),
        high DECIMAL(10, 2),
        low DECIMAL(10, 2),
        close DECIMAL(10, 2),
        volume INT,
        datetime DATETIME
    );
    """
    
    cursor.execute(create_table_query)
    conn.commit()
    cursor.close()
    conn.close()
 
if __name__ == "__main__":
 
    wait_for_db()
    create_ticker_table()
    print("-"*50)
    # tickers = ["AAPL", "GOOGL"]  # Add or modify the tickers you want
    tickers = ["TCS.NS", "RELIANCE.NS", "INFY.NS"]
   
    print("Perform backfill once")
    # historical_backfill(tickers)
    data = yf.download(tickers, period="5d", interval="1m", group_by="ticker", timeout=10) # added timeout
    print("Data fetched from yfinance.")
    print("Head")
    print(data.head().to_string())
    print("Tail")
    print(data.head().to_string())
    print("-"*50)
    print("Inserting data")
    ticker_data = []
    for ticker in tickers:
        for idx, row in data[ticker].iterrows():
            ticker_data.append({
                'ticker': ticker,
                'open': row['Open'],
                'high': row['High'],
                'low': row['Low'],
                'close': row['Close'],
                'volume': row['Volume'],
                'datetime': idx.strftime('%Y-%m-%d %H:%M:%S')
            })
    # Insert data in bulk
    batch_size=200
    conn = connect_to_db()
    cursor = conn.cursor()
 
    # Create a placeholder SQL query
    query = """INSERT INTO ticker_history (ticker, open, high, low, close, volume, datetime)
               VALUES (%s, %s, %s, %s, %s, %s, %s)"""
 
    # Convert the data into a list of tuples
    data_tuples = []
    for record in ticker_data:
        for key, value in record.items():
            if pd.isna(value):
                record[key] = None
        data_tuples.append((record['ticker'], record['open'], record['high'], record['low'],
                            record['close'], record['volume'], record['datetime']))
 
    # Insert records in chunks/batches
    for chunk in chunks(data_tuples, batch_size):
        cursor.executemany(query, chunk)
        print(f"Inserted batch of {len(chunk)} records")
 
    conn.commit()
    cursor.close()
    conn.close()
    print("-"*50)
    # Wait until starting to insert live values
    time.sleep(60)

    print("Starting live data collection...")

    max_iterations = 5  # Stop after 10 updates
    iteration_count = 0

    market_was_open = False
    try:
       while iteration_count < max_iterations:
            if is_market_open():
                iteration_count += 1
                print(f"Market is open. Fetching data. Iteration {iteration_count}/{max_iterations}")

                market_was_open = True
                print("Market is open. Fetching data.")
    
                print("Fetching data from yfinance...")
                data = yf.download(tickers, period="1d", interval="1m", group_by="ticker", timeout=10) # added timeout
                print("Data fetched from yfinance.")
                print(data.head().to_string())
            
                ticker_data = []
    
                for ticker in tickers:
                    latest_data = data[ticker].iloc[-1]
                    ticker_data.append({
                        'ticker': ticker,
                        'open': latest_data['Open'],
                        'high': latest_data['High'],
                        'low': latest_data['Low'],
                        'close': latest_data['Close'],
                        'volume': latest_data['Volume'],
                        'datetime': latest_data.name.strftime('%Y-%m-%d %H:%M:%S')
                    })
    
                    # Insert the data
                    conn = connect_to_db()
                    cursor = conn.cursor()
                    print("Inserting data")
                    total_tickers = len(ticker_data)
                    for record in ticker_data:
                        for key, value in record.items():
                            if pd.isna(value):
                                record[key] = "NULL"
                        query = f"""INSERT INTO ticker_history (ticker, open, high, low, close, volume, datetime)
                                    VALUES (
                                        '{record['ticker']}',{record['open']},{record['high']},{record['low']},{record['close']},{record['volume']},'{record['datetime']}')"""
                        print(query)
                        cursor.execute(query)
                    print("Data inserted")
                    conn.commit()
                    cursor.close()
                    conn.close()
                print("Inserted data, waiting for the next batch in one minute.")
                print("-"*50)
                time.sleep(60)
            else:
                if market_was_open:
                    print("Market has closed for the day. Exiting.")
                    break
                else:
                    print("Market not open yet. Waiting...")
                    print("-"*50)
                    time.sleep(60)  # Wait for 60 seconds before checking again
                    break
    except KeyboardInterrupt:
        print("\nStopped by user")