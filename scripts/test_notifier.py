import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent))

from utils.notifier import send_telegram_message
send_telegram_message("✅ *Test Message:* Telegram bot is working!")
