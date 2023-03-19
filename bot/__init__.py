import discord
from discord.ext.commands import Bot as BotBase
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from database.database import async_db_session


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

    async def on_messssage(self, message):
        pass


# bot = commands.Bot(command_prefix="$", description=description, intents=intents)
bot = Bot()


# @bot.event
# async def on_ready():
#     print(f"We have logged in as {bot.user}")


# bot.run(os.environ.get("BOT_TOKEN"), log_handler=handler, log_level=logging.DEBUG)
