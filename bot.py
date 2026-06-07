import asyncio
import logging
import os
from telegram import Bot
from telegram.constants import ParseMode
from monitor import MatchMonitor

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHANNEL_ID = os.environ["CHANNEL_ID"]
FD_API_KEY = os.environ["FD_API_KEY"]

async def main():
    bot = Bot(token=BOT_TOKEN)
    monitor = MatchMonitor(api_key=FD_API_KEY, bot=bot, channel_id=CHANNEL_ID)
    logger.info("🚀 World Cup Bot started!")
    await monitor.run()

if __name__ == "__main__":
    asyncio.run(main())
