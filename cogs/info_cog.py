from discord.ext import commands
from datetime import datetime
from discord import Embed
from typing import Optional
from database.user import User
from database.database import async_db_session
from sqlalchemy.future import select
from database.user_game import UserGame
from database.game import Game
from .utils.assets import CHARACTERS


class InfoCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="userinfo", aliases=["memberinfo"])
    async def user_info(self, ctx, name: Optional[str]):
        user = None

        if name is not None:
            query = select(User).where(User.in_game_name == name)
            result = (await async_db_session.execute(query)).first()
            user = None if result is None else result[0]
        else:
            id = ctx.message.author.id
            user: User = await User.get(id)

        if user is None:
            await ctx.send("No information available for this user")
            return

        embed = Embed(title="User information", timestamp=datetime.utcnow())

        fields = [
            ("Name", user.in_game_name, True),
            ("Elo", user.elo, True),
            (
                "Current Character",
                "Nobody" if user.current_character is None else user.current_character,
                True,
            ),
        ]

        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)

        await ctx.send(embed=embed)

    @commands.command()
    async def characters(self, ctx):
        await ctx.send("\n".join(CHARACTERS))

    async def cog_command_error(
        self, ctx: commands.Context, error: commands.CommandError
    ):
        await ctx.send(f"Error with info cog: {error}")
        raise error


# this setup function needs to be in every cog in order for the bot to be able to load it
async def setup(bot):
    await bot.add_cog(InfoCog(bot))
