import requests

def get_ticker_from_company_name(company_name):
    try:
        url = "https://query1.finance.yahoo.com/v1/finance/search"
        params = {
            'q': company_name,
            'quotesCount': 5,
            'newsCount': 0
        }
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, params=params, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            quotes = data.get('quotes', [])
            
            if quotes:
                first_symbol = quotes[0].get('symbol')
                if first_symbol:
                    return first_symbol
            return None
        else:
            return None
            
    except requests.exceptions.Timeout:
        return None
    except requests.exceptions.ConnectionError:
        return None
    except Exception as e:
        return None