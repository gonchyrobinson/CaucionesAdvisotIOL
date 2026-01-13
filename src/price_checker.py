"""Main price checking logic for cauciones alerts."""

import json
import os
from pathlib import Path
from typing import Optional

from .iol_client import IOLClient
from .telegram_notifier import TelegramNotifier


def load_alerts_config(config_path: Optional[str] = None) -> dict:
    """Load alerts configuration from JSON file."""
    if config_path is None:
        # Default to alerts_config.json in project root
        config_path = Path(__file__).parent.parent / "alerts_config.json"

    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def check_condition(current_value: float, target_value: float, condition: str) -> bool:
    """Check if the current value meets the condition against target."""
    if condition == ">=":
        return current_value >= target_value
    elif condition == "<=":
        return current_value <= target_value
    elif condition == ">":
        return current_value > target_value
    elif condition == "<":
        return current_value < target_value
    elif condition == "==":
        return abs(current_value - target_value) < 0.01
    return False


def get_rate_from_caucion(caucion_data: dict, rate_type: str) -> Optional[float]:
    """Extract the appropriate rate from caucion data."""
    # Try different field names the API might use
    if rate_type == "colocador":
        return (
            caucion_data.get("tasaColocadora") or 
            caucion_data.get("precioCompra") or
            caucion_data.get("puntas", {}).get("precioCompra")
        )
    elif rate_type == "tomador":
        return (
            caucion_data.get("tasaTomadora") or 
            caucion_data.get("precioVenta") or
            caucion_data.get("puntas", {}).get("precioVenta")
        )
    return None


def run_price_check():
    """Main function to check prices and send alerts."""
    # Load credentials from environment variables
    iol_username = os.environ.get("IOL_USERNAME")
    iol_password = os.environ.get("IOL_PASSWORD")
    telegram_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    telegram_chat_id = os.environ.get("TELEGRAM_CHAT_ID")

    # Validate required environment variables
    if not all([iol_username, iol_password, telegram_token, telegram_chat_id]):
        print("Error: Missing required environment variables")
        print("Required: IOL_USERNAME, IOL_PASSWORD, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID")
        return False

    # Initialize clients
    iol_client = IOLClient(iol_username, iol_password)
    notifier = TelegramNotifier(telegram_token, telegram_chat_id)

    # Load alerts configuration
    try:
        config = load_alerts_config()
    except FileNotFoundError:
        notifier.send_error_message("alerts_config.json not found")
        return False
    except json.JSONDecodeError as e:
        notifier.send_error_message(f"Invalid JSON in config: {e}")
        return False

    alerts = config.get("alerts", [])

    if not alerts:
        print("No alerts configured")
        return True

    # Fetch cauciones data
    cauciones = iol_client.get_cauciones()

    if not cauciones:
        notifier.send_error_message("Failed to fetch cauciones data from IOL API")
        return False

    # Build a lookup by days (plazo) - handle different field names
    cauciones_by_days = {}
    for c in cauciones:
        days_key = c.get("plazo") or c.get("diasVencimiento") or c.get("cantidadDias")
        if days_key:
            cauciones_by_days[days_key] = c
            print(f"Found caucion: {days_key} days - {c}")
    
    if not cauciones_by_days:
        print("Warning: Could not parse cauciones data. Raw data sample:")
        print(cauciones[:2] if len(cauciones) > 2 else cauciones)

    # Check each enabled alert
    alerts_triggered = 0

    for alert in alerts:
        if not alert.get("enabled", True):
            continue

        days = alert.get("days")
        rate_type = alert.get("type")
        target_rate = alert.get("target_rate")
        condition = alert.get("condition", ">=")
        description = alert.get("description")

        # Get caucion data for the specified days
        caucion_data = cauciones_by_days.get(days)

        if caucion_data is None:
            print(f"No caucion data found for {days} day(s)")
            continue

        # Get the current rate
        current_rate = get_rate_from_caucion(caucion_data, rate_type)

        if current_rate is None:
            print(f"Could not get {rate_type} rate for {days} day(s)")
            continue

        # Check if condition is met
        if check_condition(current_rate, target_rate, condition):
            print(f"Alert triggered: {days}d {rate_type} {current_rate:.2f}% {condition} {target_rate:.2f}%")
            notifier.send_price_alert(
                days=days,
                alert_type=rate_type,
                current_rate=current_rate,
                target_rate=target_rate,
                condition=condition,
                description=description
            )
            alerts_triggered += 1
        else:
            print(f"No alert: {days}d {rate_type} {current_rate:.2f}% (target: {condition} {target_rate:.2f}%)")

    print(f"Price check complete. {alerts_triggered} alert(s) triggered.")
    return True


if __name__ == "__main__":
    run_price_check()
