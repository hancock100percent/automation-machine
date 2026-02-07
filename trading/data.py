"""Market data pipeline using yfinance with SQLite caching."""

import sqlite3
from datetime import date

import pandas as pd
import yfinance as yf

from trading.config import DB_PATH, WATCHLIST


def _ensure_db() -> sqlite3.Connection:
    """Create the database and ohlcv table if they don't exist."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("""
        CREATE TABLE IF NOT EXISTS ohlcv (
            ticker TEXT NOT NULL,
            date TEXT NOT NULL,
            open REAL,
            high REAL,
            low REAL,
            close REAL,
            volume INTEGER,
            PRIMARY KEY (ticker, date)
        )
    """)
    conn.commit()
    return conn


def _has_data_for_today(conn: sqlite3.Connection, ticker: str) -> bool:
    """Check if the database already contains data for today's date."""
    today = date.today().isoformat()
    row = conn.execute(
        "SELECT 1 FROM ohlcv WHERE ticker = ? AND date = ? LIMIT 1",
        (ticker, today),
    ).fetchone()
    return row is not None


def download_historical(ticker: str, period: str = "2y") -> pd.DataFrame:
    """Download historical OHLCV data for a single ticker.

    Uses SQLite cache -- skips the download if data for today already exists.
    Returns a pandas DataFrame with columns: date, open, high, low, close, volume.
    """
    conn = _ensure_db()

    if _has_data_for_today(conn, ticker):
        df = pd.read_sql_query(
            "SELECT date, open, high, low, close, volume FROM ohlcv WHERE ticker = ? ORDER BY date",
            conn,
            params=(ticker,),
        )
        conn.close()
        df["date"] = pd.to_datetime(df["date"])
        return df

    # Download from Yahoo Finance
    data = yf.download(ticker, period=period, progress=False, auto_adjust=True)

    if data.empty:
        conn.close()
        return pd.DataFrame(columns=["date", "open", "high", "low", "close", "volume"])

    # Flatten multi-level columns if present (yfinance sometimes returns MultiIndex)
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    data = data.reset_index()
    data.columns = [c.lower() for c in data.columns]

    # Ensure we have the expected columns
    data = data.rename(columns={"adj close": "close"})
    data = data[["date", "open", "high", "low", "close", "volume"]]
    data["date"] = pd.to_datetime(data["date"]).dt.date.astype(str)

    # Upsert into SQLite
    rows = [(ticker, r["date"], r["open"], r["high"], r["low"], r["close"], int(r["volume"])) for _, r in data.iterrows()]
    conn.executemany(
        "INSERT OR REPLACE INTO ohlcv (ticker, date, open, high, low, close, volume) VALUES (?, ?, ?, ?, ?, ?, ?)",
        rows,
    )
    conn.commit()
    conn.close()

    data["date"] = pd.to_datetime(data["date"])
    return data


def get_watchlist_data(tickers: list[str] | None = None) -> dict[str, pd.DataFrame]:
    """Download historical data for all tickers in the watchlist.

    Returns a dict mapping ticker -> DataFrame.
    """
    if tickers is None:
        tickers = WATCHLIST

    results = {}
    for ticker in tickers:
        print(f"  Fetching {ticker}...")
        results[ticker] = download_historical(ticker)
    return results
