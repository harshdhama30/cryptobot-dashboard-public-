# ~/Downloads/crypto_bot_complete/modules/telegram_integration.py

import os
import time
from telegram import Bot

def request_approval(trade_decisions, timeout=300):
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id_str = os.getenv("TELEGRAM_CHAT_ID", "").strip()

    if not bot_token or not chat_id_str:
        # No Telegram config → auto‑approve
        print("⚠️ Telegram token/ID not set – skipping approval.")
        return True

    bot = Bot(token=bot_token)
    chat_id = int(chat_id_str)

    # Send approval request
    message = "🔔 Please approve or reject these trades (reply YES or NO):\n"
    for coin, action in trade_decisions.items():
        message += f"{coin}: {action}\n"
    bot.send_message(chat_id=chat_id, text=message)

    # Wait for YES/NO reply
    start = time.time()
    while time.time() - start < timeout:
        updates = bot.get_updates()
        for u in updates:
            txt = u.message.text.strip().lower()
            if txt == "yes":
                return True
            if txt == "no":
                return False
        time.sleep(5)

    # Timeout → auto‑approve
    return True
