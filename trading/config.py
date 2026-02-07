"""Trading configuration constants."""

from pathlib import Path

WATCHLIST = ["SPY", "QQQ", "AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "META", "TSLA", "AMD"]
DEFAULT_CASH = 100000
DEFAULT_PERIOD = "2y"
DB_PATH = Path(__file__).parent / "data" / "market_data.db"
RESULTS_PATH = Path(__file__).parent / "results"
