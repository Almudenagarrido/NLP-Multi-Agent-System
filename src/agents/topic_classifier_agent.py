# finance_classifier.py
import re
from typing import Dict, List

class TopicClassifier:
    """
    Classifies text queries into one of three finance topics:
      - 'markets_trading'
      - 'corporate_business'
      - 'crypto_digital_assets'
    """

    def __init__(self):
        self.categories: Dict[str, List[str]] = {
            "markets_trading": [
                "stock", "share", "price", "market", "index", "trading", "analyst",
                "investor", "valuation", "forecast", "target", "gain", "drop", "rise",
                "sell", "buy", "portfolio", "sector", "nasdaq", "sp500"
            ],
            "corporate_business": [
                "product", "launch", "service", "deal", "partnership", "ceo", "executive",
                "earnings", "revenue", "sales", "strategy", "business", "expansion",
                "brand", "subsidiary", "factory", "plant", "supply", "production"
            ],
            "crypto_digital_assets": [
                "bitcoin", "crypto", "blockchain", "token", "ethereum", "web3",
                "nft", "wallet", "coinbase", "exchange", "cryptoasset", "mining",
                "fold", "binance", "defi"
            ],
        }

    def classify(self, query: str) -> str:
        """
        Classify a text query into one of the three categories.
        """
        query_lower = query.lower()
        scores = {
            category: sum(
                bool(re.search(rf"\b{kw}\b", query_lower)) for kw in keywords
            )
            for category, keywords in self.categories.items()
        }
        best_category = max(scores, key=scores.get)
        if all(score == 0 for score in scores.values()):
            best_category = "corporate_business"

        return best_category

