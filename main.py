#!/usr/bin/env python3
"""Entry point for the Cauciones Price Checker."""

from src.price_checker import run_price_check

if __name__ == "__main__":
    success = run_price_check()
    exit(0 if success else 1)
