from discord.ext import commands
from datetime import datetime
from discord import Embed
from typing import Optional
from database.user import User
from database.database import async_db_session
from sqlalchemy.future import select
from database.user_game import UserGame, GameResult
from database.user_character import UserCharacter
from database.game import Game
from .utils.assets import CHARACTERS
from sqlalchemy import desc
from sqlalchemy.orm import selectinload
from itertools import groupby
from operator import attrgetter


class InfoCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["memberinfo", "userinfo"])
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

    @commands.command(aliases=["leaderboards"])
    async def leaderboard(self, ctx):
        query = select(User).order_by(desc(User.elo))
        users = (await async_db_session.execute(query)).all()
        embed = Embed(
            title=f"User Leaderboards",
        )

        rank = ""
        name = ""
        elo = ""

        for idx, user in enumerate(users):
            user = user[0]
            rank += f"{idx+1}\n"
            name += f"{user.in_game_name}\n"
            elo += f"{user.elo}\n"

        embed.add_field(name="Rank", value=rank, inline=True)
        embed.add_field(name="Name", value=name, inline=True)
        embed.add_field(name="Elo", value=elo, inline=True)

        await ctx.send(embed=embed)

    @commands.command(aliases=["characterleaderboard, characterleaderboards"])
    async def character_leaderboard(self, ctx):
        query = (
            select(UserCharacter)
            .order_by(desc(UserCharacter.elo))
            .options(selectinload(UserCharacter.user))
        )
        user_characters = (await async_db_session.execute(query)).all()
        name = ""
        character = ""
        elo = ""

        for user_character in user_characters:
            user_character = user_character[0]
            name += f"{user_character.user.in_game_name}\n"
            character += f"{user_character.character}\n"
            elo += f"{user_character.elo}\n"

        embed = Embed(
            title=f"Character Leaderboards",
        )

        embed.add_field(name="Name", value=name, inline=True)
        embed.add_field(name="Character", value=character, inline=True)
        embed.add_field(name="Elo", value=elo, inline=True)

        await ctx.send(embed=embed)

    @commands.command(aliases=["winrates"])
    async def win_rates(self, ctx):
        query = (
            select(User)
            .order_by(desc(User.elo))
            .options(selectinload(User.user_game_history))
        )
        users = (await async_db_session.execute(query)).all()
        embed = Embed(
            title=f"Win Rates",
        )

        name = ""
        win_loss = ""
        win_rate = ""

        for user in users:
            user: User = user[0]
            wins = sum(
                1
                for game in user.user_game_history
                if game.game_result == GameResult.winner
            )
            losses = len(user.user_game_history) - wins

            name += f"{user.in_game_name}\n"
            win_loss += f"{wins}/{losses}\n"
            win_rate += (
                f"0%\n"
                if len(user.user_game_history) == 0
                else f"{round((wins/(losses + wins)) * 100, 1)}%\n"
            )

        embed.add_field(name="Name", value=name, inline=True)
        embed.add_field(name="Win/Loss", value=win_loss, inline=True)
        embed.add_field(name="Win Rate", value=win_rate, inline=True)

        await ctx.send(embed=embed)

    @commands.command(aliases=["winrate"])
    async def win_rate(self, ctx, name: Optional[str]):
        user = None

        if name is None:
            user = await User.get(ctx.message.author.id)
        else:
            user = await User.get_from_name(name)

        if user is None:
            await ctx.send("User not found")
            return

        query = (
            select(UserGame)
            .where(UserGame.user_id == user.id)
            .order_by(UserGame.character)
        )

        user_games = (await async_db_session.execute(query)).scalars().all()

        # Materialize the subiterators to lists
        characters_dict = {
            k: list(g) for k, g in groupby(user_games, attrgetter("character"))
        }
        embed = Embed(
            title=f"{user.in_game_name} Win Rates",
        )

        characters = ""
        win_loss = ""
        win_rate = ""

        for character, games in characters_dict.items():
            wins = sum(1 for game in games if game.game_result == GameResult.winner)
            losses = len(games) - wins

            characters += f"{character}\n"
            win_loss += f"{wins}/{losses}\n"
            win_rate += (
                f"0%\n"
                if len(games) == 0
                else f"{round((wins/(losses + wins)) * 100, 1)}%\n"
            )

        embed.add_field(name="Character", value=characters, inline=True)
        embed.add_field(name="Win/Loss", value=win_loss, inline=True)
        embed.add_field(name="Win Rate", value=win_rate, inline=True)

        await ctx.send(embed=embed)

    async def cog_command_error(
        self, ctx: commands.Context, error: commands.CommandError
    ):
        await ctx.send(f"Error with info cog: {error}")
        raise error


# this setup function needs to be in every cog in order for the bot to be able to load it
async def setup(bot):
    await bot.add_cog(InfoCog(bot))
