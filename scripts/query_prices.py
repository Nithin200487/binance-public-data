#!/usr/bin/env python3
"""
Query token prices from the saved data
"""

import json
import sys
from pathlib import Path

def load_prices(prices_file):
    """Load prices from JSON file"""
    try:
        with open(prices_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: {prices_file} not found. Run fetch_prices.py first.")
        sys.exit(1)

def search_token(query, prices_data):
    """Search for a token by symbol or base asset"""
    query = query.upper()
    results = []
    
    for quote, pairs in prices_data['pairs'].items():
        for pair in pairs:
            if query in pair['symbol'] or query in pair['base']:
                results.append({
                    'symbol': pair['symbol'],
                    'base': pair['base'],
                    'quote': pair['quote'],
                    'price': pair['price']
                })
    
    return results

def get_price(symbol, prices_data):
    """Get price for a specific symbol"""
    symbol = symbol.upper()
    for quote, pairs in prices_data['pairs'].items():
        for pair in pairs:
            if pair['symbol'] == symbol:
                return pair
    return None

def list_by_quote(quote, prices_data):
    """List all pairs for a specific quote currency"""
    quote = quote.upper()
    if quote in prices_data['pairs']:
        return prices_data['pairs'][quote]
    return []

def main():
    # Get prices data path
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent
    prices_file = repo_root / "data" / "prices" / "prices.json"
    
    if not prices_file.exists():
        print("❌ Price data not found. Run: python scripts/fetch_prices.py")
        sys.exit(1)
    
    prices_data = load_prices(prices_file)
    
    print("📊 Token Price Query Tool")
    print("-" * 50)
    print(f"Last updated: {prices_data['timestamp']}")
    print(f"Total pairs: {prices_data['total_pairs']}")
    print("\nCommands:")
    print("  price <SYMBOL>      - Get price for specific symbol (e.g., BTCUSDT)")
    print("  search <TOKEN>      - Search for a token (e.g., BTC, ADA)")
    print("  list <QUOTE>        - List all pairs for quote currency (e.g., USDT)")
    print("  quotes              - Show all quote currencies")
    print("  exit                - Exit program")
    print("-" * 50)
    
    while True:
        try:
            user_input = input("\n> ").strip().split()
            if not user_input:
                continue
            
            command = user_input[0].lower()
            
            if command == "exit":
                print("Goodbye!")
                break
            
            elif command == "price" and len(user_input) > 1:
                symbol = user_input[1].upper()
                result = get_price(symbol, prices_data)
                if result:
                    print(f"✓ {result['symbol']}: {result['price']} {result['quote']}")
                else:
                    print(f"✗ Symbol '{symbol}' not found")
            
            elif command == "search" and len(user_input) > 1:
                query = user_input[1].upper()
                results = search_token(query, prices_data)
                if results:
                    print(f"\n✓ Found {len(results)} results for '{query}':")
                    for r in results[:10]:
                        print(f"  {r['symbol']:15} {r['price']:>15.8f}")
                    if len(results) > 10:
                        print(f"  ... and {len(results) - 10} more")
                else:
                    print(f"✗ No results for '{query}'")
            
            elif command == "list" and len(user_input) > 1:
                quote = user_input[1].upper()
                pairs = list_by_quote(quote, prices_data)
                if pairs:
                    print(f"\n✓ {len(pairs)} pairs for {quote}:")
                    for p in pairs[:15]:
                        print(f"  {p['symbol']:15} {p['price']:>15.8f}")
                    if len(pairs) > 15:
                        print(f"  ... and {len(pairs) - 15} more")
                else:
                    print(f"✗ Quote '{quote}' not found")
            
            elif command == "quotes":
                quotes = sorted(prices_data['pairs'].keys())
                print(f"\n✓ Available quote currencies ({len(quotes)}):")
                for quote in quotes:
                    count = len(prices_data['pairs'][quote])
                    print(f"  {quote:8} : {count:4} pairs")
            
            else:
                print("Unknown command. Try: price, search, list, quotes, exit")
        
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
