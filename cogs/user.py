from discord.ext import commands
from database.users import Users
from sqlalchemy import exc


class User(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Ready User")

    @commands.command(aliases=["changename"])
    async def register(self, ctx: commands.Context, in_game_name: str):
        try:
            id = ctx.message.author.id
            user = await Users.get(id)
            if user == None:
                await Users.create(id=ctx.message.author.id, in_game_name=in_game_name)
            else:
                await Users.update(id, in_game_name=in_game_name)
            await ctx.send(f"Welcome {in_game_name}")
        except exc.IntegrityError:
            await ctx.send("A user already chose that name!")
        except Exception as e:
            await ctx.send(f"Error: {e}")


# this setup function needs to be in every cog in order for the bot to be able to load it
async def setup(bot):
    await bot.add_cog(User(bot))
