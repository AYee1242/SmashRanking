from discord.ext import commands
from datetime import datetime
from discord import Embed, Member
from typing import Optional
from database.user import User
from database.character import Character
from database.database import async_db_session
from sqlalchemy.future import select


class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # @commands.command(name="process_game", aliases=["game", "processGame"])
    # async def process_match(self, ctx, winner, loser, winner_champ: Optional[str], loser_champ: Optional[str]):

    # @commands.Cog.listener()
    # async def on_ready(self):
    #     print("READY UP")


# this setup function needs to be in every cog in order for the bot to be able to load it
async def setup(bot):
    await bot.add_cog(Info(bot))
