# This example requires the 'message_content' intent.
import asyncio
from dotenv import load_dotenv
from glob import glob
from database.database import async_db_session

load_dotenv()
import os
from discord.ext import commands
import logging
from cogs import *
from bot import bot

# Logger Configuration
logger = logging.getLogger("discord")
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")
handler.setFormatter(
    logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s")
)
logger.addHandler(handler)

asyncio.run(bot.start(os.environ.get("BOT_TOKEN")))
