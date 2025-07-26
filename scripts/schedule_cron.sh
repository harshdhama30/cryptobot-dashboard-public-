#!/bin/bash
# Schedule daily run at 09:00 via cron
(crontab -l 2>/dev/null; \
 echo "0 9 * * * cd ~/Downloads/crypto_bot_complete && source venv/bin/activate && python main.py >> ~/Downloads/crypto_bot_complete/logs/bot.log 2>&1") | crontab -
echo "Cron job scheduled: daily at 09:00."
