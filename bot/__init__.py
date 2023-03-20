import discord
from discord.ext.commands import Bot as BotBase
from database.database import async_db_session
from discord import Embed, DMChannel
from datetime import datetime


COMMAND_PREFIX = "$"
COGS = ["info", "user"]


class Bot(BotBase):
    def __init__(self) -> None:
        self.COMMAND_PREFIX = COMMAND_PREFIX
        self.guild = None
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True
        super().__init__(
            command_prefix=COMMAND_PREFIX,
            description="Smash Ranking Bot",
            intents=intents,
        )

    async def load_extensions(self):
        for cog in COGS:
            await self.load_extension(f"cogs.{cog}")

    async def start(self, token: str):
        await self.load_extensions()
        await async_db_session.init()
        await async_db_session.create_all()
        await super().start(token=token)

    async def on_connect(self):
        print("bot connected")

    async def on_disconnect(self):
        print("bot disconnected")

    async def on_ready(self):
        print("ready up")


bot = Bot()
