from discord.ext import commands
from database.user import User
from sqlalchemy import exc
from .utils.assets import CHARACTERS


class UserCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Ready User")

    @commands.command(aliases=["changename", "changeName", "change_name"])
    async def register(self, ctx: commands.Context, in_game_name: str):
        try:
            id = ctx.message.author.id
            user = await User.get(id)
            if user == None:
                await User.create(id=ctx.message.author.id, in_game_name=in_game_name)
            else:
                await User.update(id, in_game_name=in_game_name)
            await ctx.send(f"Welcome {in_game_name}")
        except exc.IntegrityError:
            await ctx.send("A user already chose that name!")

    @commands.command(aliases=["set", "setcharacter", "setCharacter"])
    async def set_character(self, ctx: commands.Context, character: str):
        id = ctx.message.author.id
        user = await User.get(id)
        if user == None:
            await ctx.send(
                "Please register yourself with $register <in_game_name> first!"
            )
            return

        if character.capitalize() not in CHARACTERS:
            await ctx.send(
                "Character does not exist, check playable characters with $characters"
            )
            return

        await User.update(id, current_character=character)
        await ctx.send("Character has updated!")

    async def cog_command_error(
        self, ctx: commands.Context, error: commands.CommandError
    ):
        await ctx.send(f"Error with user cog: {error}")
        raise error


# this setup function needs to be in every cog in order for the bot to be able to load it
async def setup(bot):
    await bot.add_cog(UserCog(bot))
