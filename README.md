# Cauciones Price Alert Pipeline

Automated GitHub Actions pipeline that monitors InvertirOnline cauciones (short-term repo) prices and sends Telegram notifications when target prices are reached.

## Features

- Checks cauciones prices every 5 minutes via GitHub Actions
- Supports both colocador (lender) and tomador (borrower) rates
- Configurable price alerts via JSON file
- Telegram notifications with formatted messages
- Easy to customize and extend

## Setup

### 1. Create a Telegram Bot

1. Open Telegram and search for [@BotFather](https://t.me/BotFather)
2. Send `/newbot` and follow the prompts to create a new bot
3. Copy the **bot token** provided by BotFather

### 2. Get Your Telegram Chat ID

1. Search for [@userinfobot](https://t.me/userinfobot) on Telegram
2. Start a conversation with it
3. Copy your **chat ID** from the response

### 3. Configure GitHub Secrets

Go to your repository **Settings** > **Secrets and variables** > **Actions** and add:

| Secret | Description |
|--------|-------------|
| `IOL_USERNAME` | Your InvertirOnline account username |
| `IOL_PASSWORD` | Your InvertirOnline account password |
| `TELEGRAM_BOT_TOKEN` | Bot token from BotFather |
| `TELEGRAM_CHAT_ID` | Your Telegram chat ID |

### 4. Configure Price Alerts

Edit `alerts_config.json` to define your price alerts:

```json
{
  "alerts": [
    {
      "symbol": "CAUCI1",
      "days": 1,
      "type": "colocador",
      "condition": ">=",
      "target_rate": 35.5,
      "enabled": true,
      "description": "Alert when 1-day caucion lender rate reaches 35.5%"
    }
  ]
}
```

#### Alert Configuration Options

| Field | Description |
|-------|-------------|
| `symbol` | Caucion symbol (informational) |
| `days` | Number of days (plazo): 1, 7, 14, etc. |
| `type` | Rate type: `colocador` (lender) or `tomador` (borrower) |
| `condition` | Comparison: `>=`, `<=`, `>`, `<`, `==` |
| `target_rate` | Target rate percentage |
| `enabled` | Set to `false` to disable an alert |
| `description` | Optional description for the alert message |

### 5. Deploy

Push your changes to GitHub and the workflow will automatically run every 5 minutes.

To test immediately, go to **Actions** > **Check Cauciones Prices** > **Run workflow**.

## Local Testing

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables (PowerShell)
$env:IOL_USERNAME="your_username"
$env:IOL_PASSWORD="your_password"
$env:TELEGRAM_BOT_TOKEN="your_bot_token"
$env:TELEGRAM_CHAT_ID="your_chat_id"

# Run the price checker
python main.py
```

## Project Structure

```
├── .github/
│   └── workflows/
│       └── check_prices.yml     # GitHub Actions workflow
├── src/
│   ├── __init__.py
│   ├── price_checker.py         # Main price checking logic
│   ├── iol_client.py            # InvertirOnline API client
│   └── telegram_notifier.py     # Telegram notification handler
├── alerts_config.json           # User-configurable price alerts
├── main.py                      # Entry point
├── requirements.txt             # Python dependencies
└── README.md
```

## Notes

- GitHub Actions minimum scheduling interval is 5 minutes
- The InvertirOnline API requires valid account credentials
- Alerts are only sent when conditions are met (no spam)
- The workflow can be manually triggered for testing
