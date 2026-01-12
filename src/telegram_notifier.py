"""Telegram notification handler for price alerts."""

import requests
from typing import Optional


class TelegramNotifier:
    """Send notifications via Telegram Bot API."""

    BASE_URL = "https://api.telegram.org/bot"

    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id

    def send_message(self, message: str) -> bool:
        """Send a text message to the configured chat."""
        url = f"{self.BASE_URL}{self.bot_token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "HTML"
        }

        response = requests.post(url, json=payload)

        if response.status_code == 200:
            return True

        print(f"Failed to send Telegram message: {response.status_code} - {response.text}")
        return False

    def send_price_alert(
        self,
        days: int,
        alert_type: str,
        current_rate: float,
        target_rate: float,
        condition: str,
        description: Optional[str] = None
    ) -> bool:
        """Send a formatted price alert message."""
        type_label = "Colocador (Lender)" if alert_type == "colocador" else "Tomador (Borrower)"
        condition_text = "reached" if condition in (">=", "==") else "dropped to"

        message = (
            f"🔔 <b>Caucion Price Alert!</b>\n\n"
            f"📊 <b>Plazo:</b> {days} day(s)\n"
            f"📈 <b>Type:</b> {type_label}\n"
            f"💰 <b>Current Rate:</b> {current_rate:.2f}%\n"
            f"🎯 <b>Target Rate:</b> {target_rate:.2f}%\n"
            f"📌 <b>Condition:</b> {condition} {condition_text}\n"
        )

        if description:
            message += f"\n📝 <i>{description}</i>"

        return self.send_message(message)

    def send_startup_message(self) -> bool:
        """Send a message indicating the price checker has started."""
        message = "✅ <b>Cauciones Price Checker Started</b>\n\nMonitoring prices..."
        return self.send_message(message)

    def send_error_message(self, error: str) -> bool:
        """Send an error notification."""
        message = f"❌ <b>Error in Price Checker</b>\n\n{error}"
        return self.send_message(message)
