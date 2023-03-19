from discord.ext import commands
from database.users import Users


class User(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("READY")

    @commands.command()
    async def register(self, ctx, in_game_name: str):
        try:
            await Users.create(id=ctx.message.author.id, in_game_name=in_game_name)
            await ctx.send("Registration Complete!")
        except Exception as e:
            print(e)
            await ctx.send(f"Error creating user: {e}")


# this setup function needs to be in every cog in order for the bot to be able to load it
async def setup(bot):
    await bot.add_cog(User(bot))
