from discord.ext import commands
from datetime import datetime
from discord import Embed, Member
from typing import Optional
from database.users import Users
from database.database import async_db_session
from sqlalchemy.future import select


class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="userinfo", aliases=["memberinfo"])
    async def user_info(self, ctx, name: Optional[str]):
        try:
            user = None

            if name is not None:
                query = select(Users).where(Users.in_game_name == name)
                result = (await async_db_session.execute(query)).first()
                user = None if result is None else result[0]
            else:
                id = ctx.message.author.id
                user = await Users.get(id)

            if user is None:
                await ctx.send("No information available for this user")
                return

            embed = Embed(title="User information", timestamp=datetime.utcnow())

            fields = [("Name", user.in_game_name, True), ("Elo", user.elo, True)]

            for name, value, inline in fields:
                embed.add_field(name=name, value=value, inline=inline)

            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(e)

    @commands.Cog.listener()
    async def on_ready(self):
        print("READY UP")


# this setup function needs to be in every cog in order for the bot to be able to load it
async def setup(bot):
    await bot.add_cog(Info(bot))
