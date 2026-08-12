#!/usr/bin/env python3
"""
Fetch real-time token prices from Binance API for all symbols in symbols.txt
"""

import requests
import json
import sys
from pathlib import Path
from collections import defaultdict

def load_symbols(symbols_file):
    """Load trading symbols from file"""
    symbols = []
    try:
        with open(symbols_file, 'r') as f:
            for line in f:
                symbol = line.strip()
                if symbol and not symbol.startswith('#'):
                    symbols.append(symbol)
    except FileNotFoundError:
        print(f"Error: {symbols_file} not found")
        sys.exit(1)
    return symbols

def fetch_all_prices():
    """Fetch all prices at once from Binance API"""
    try:
        url = "https://api.binance.com/api/v3/ticker/price"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return {item['symbol']: float(item['price']) for item in response.json()}
    except requests.exceptions.RequestException as e:
        print(f"Error fetching prices: {e}")
        return {}

def fetch_price_single(symbol):
    """Fetch price for a single symbol"""
    try:
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        return float(data['price'])
    except requests.exceptions.RequestException:
        return None

def parse_symbol(symbol):
    """Parse symbol to extract base and quote assets"""
    # Common quote currencies
    quotes = ['USDT', 'BUSD', 'USDC', 'BTC', 'ETH', 'BNB', 'TUSD', 'PAX', 'EUR', 'GBP', 'TRY', 'BIDR', 'BKRW', 'BRL', 'DAI', 'IDRT', 'NGN', 'RUB', 'ZAR', 'AUD']
    
    for quote in sorted(quotes, key=len, reverse=True):
        if symbol.endswith(quote):
            base = symbol[:-len(quote)]
            return base, quote
    return symbol, 'UNKNOWN'

def organize_by_quote(symbols_with_prices):
    """Organize prices by quote currency"""
    organized = defaultdict(list)
    for symbol, price in symbols_with_prices:
        base, quote = parse_symbol(symbol)
        organized[quote].append({
            'symbol': symbol,
            'base': base,
            'quote': quote,
            'price': price
        })
    
    # Sort each quote group by base asset
    for quote in organized:
        organized[quote].sort(key=lambda x: x['base'])
    
    return organized

def save_prices_json(prices_data, output_file):
    """Save prices to JSON file"""
    with open(output_file, 'w') as f:
        json.dump(prices_data, f, indent=2)
    print(f"✓ Saved prices to {output_file}")

def save_prices_csv(symbols_with_prices, output_file):
    """Save prices to CSV file"""
    with open(output_file, 'w') as f:
        f.write("symbol,base,quote,price\n")
        for symbol, price in symbols_with_prices:
            base, quote = parse_symbol(symbol)
            f.write(f"{symbol},{base},{quote},{price}\n")
    print(f"✓ Saved prices to {output_file}")

def main():
    # Paths
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent
    symbols_file = repo_root / "data" / "symbols.txt"
    output_dir = repo_root / "data" / "prices"
    output_dir.mkdir(exist_ok=True)
    
    print("📊 Binance Price Fetcher")
    print("-" * 50)
    
    # Load symbols
    print("Loading symbols...")
    symbols = load_symbols(symbols_file)
    print(f"✓ Loaded {len(symbols)} trading pairs")
    
    # Fetch prices
    print("\nFetching prices from Binance API...")
    all_prices = fetch_all_prices()
    
    if not all_prices:
        print("⚠ Could not fetch prices. Check your internet connection.")
        sys.exit(1)
    
    # Get prices for our symbols
    symbols_with_prices = []
    missing_count = 0
    
    for symbol in symbols:
        if symbol in all_prices:
            symbols_with_prices.append((symbol, all_prices[symbol]))
        else:
            missing_count += 1
    
    print(f"✓ Fetched prices for {len(symbols_with_prices)} pairs")
    if missing_count > 0:
        print(f"⚠ {missing_count} symbols not found")
    
    # Organize by quote currency
    print("\nOrganizing by quote currency...")
    organized = organize_by_quote(symbols_with_prices)
    print(f"✓ Found {len(organized)} different quote currencies")
    
    # Save outputs
    print("\nSaving data...")
    
    # JSON format
    json_output = output_dir / "prices.json"
    prices_json = {
        'timestamp': __import__('datetime').datetime.now().isoformat(),
        'total_pairs': len(symbols_with_prices),
        'pairs': organized
    }
    save_prices_json(prices_json, json_output)
    
    # CSV format
    csv_output = output_dir / "prices.csv"
    save_prices_csv(symbols_with_prices, csv_output)
    
    # Summary by quote
    summary_output = output_dir / "summary.json"
    summary = {}
    for quote in organized:
        summary[quote] = {
            'count': len(organized[quote]),
            'sample': organized[quote][:3]  # First 3 pairs
        }
    save_prices_json(summary, summary_output)
    
    print("\n" + "=" * 50)
    print("📈 SUMMARY BY QUOTE CURRENCY")
    print("=" * 50)
    for quote in sorted(organized.keys()):
        count = len(organized[quote])
        print(f"{quote:8} : {count:4} pairs")
    
    print("\n✅ Complete! Files saved to: data/prices/")

if __name__ == "__main__":
    main()
