from discord.ext import commands
from datetime import datetime
from discord import Embed
from typing import Optional
from database.user import User
from database.database import async_db_session
from sqlalchemy.future import select
from database.user_game import UserGame, GameResult
from database.user_character import UserCharacter
from .utils.assets import CHARACTERS
from sqlalchemy import desc
from sqlalchemy.orm import selectinload
from itertools import groupby
from operator import attrgetter


class InfoCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Ready Info")

    @commands.command(
        aliases=["memberinfo", "userinfo"],
        brief="Display user info",
        description="Displays user in game name, current character and elo",
    )
    async def user_info(
        self,
        ctx,
        name: Optional[str] = commands.parameter(
            description="The in game name of the user. If left blank will use the caller"
        ),
    ):
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

    @commands.command(
        brief="Displays playable characters",
        description="Displays all characters that users can use",
    )
    async def characters(self, ctx):
        await ctx.send(", ".join(CHARACTERS))

    @commands.command(
        aliases=["leaderboards"],
        brief="Player rankings",
        description="Prints out user rankings based off of elo",
    )
    async def leaderboard(self, ctx):
        query = select(User).where(User.viewable == True).order_by(desc(User.elo))
        users = (await async_db_session.execute(query)).scalars()
        embed = Embed(
            title=f"User Leaderboards",
        )

        rank = ""
        name = ""
        elo = ""

        for idx, user in enumerate(users):
            rank += f"{idx+1}\n"
            name += f"{user.in_game_name}\n"
            elo += f"{user.elo}\n"

        embed.add_field(name="Rank", value=rank, inline=True)
        embed.add_field(name="Name", value=name, inline=True)
        embed.add_field(name="Elo", value=elo, inline=True)

        await ctx.send(embed=embed)

    @commands.command(
        aliases=[
            "characterleaderboard",
            "characterleaderboards",
            "character_leaderboards",
        ],
        brief="Character rankings",
        description="Prints out character rankings based off of character elo",
    )
    async def character_leaderboard(self, ctx):
        query = (
            select(UserCharacter)
            .order_by(desc(UserCharacter.elo))
            .options(selectinload(UserCharacter.user))
        )
        user_characters = (await async_db_session.execute(query)).scalars()
        name = ""
        character = ""
        elo = ""

        for user_character in user_characters:
            if user_character.user.viewable is False:
                continue
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

    @commands.command(
        aliases=["winrates"],
        brief="Player win rates",
        description="Prints out all player win rates",
    )
    async def win_rates(self, ctx):
        query = (
            select(User)
            .where(User.viewable == True)
            .order_by(desc(User.elo))
            .options(selectinload(User.user_game_history))
        )
        users = (await async_db_session.execute(query)).scalars()

        embed = Embed(
            title=f"Win Rates",
        )

        name = ""
        win_loss = ""
        win_rate = ""

        for idx, user in enumerate(users):
            wins = sum(
                1
                for game in user.user_game_history
                if game.game_result == GameResult.winner
            )
            losses = len(user.user_game_history) - wins

            name += f"{idx+1}. {user.in_game_name}\n"
            win_loss += f"{wins}-{losses}\n"
            win_rate += (
                f"0%\n"
                if len(user.user_game_history) == 0
                else f"{round((wins/(losses + wins)) * 100, 1)}%\n"
            )

        embed.add_field(name="Name", value=name, inline=True)
        embed.add_field(name="Win-Loss", value=win_loss, inline=True)
        embed.add_field(name="Win Rate", value=win_rate, inline=True)

        await ctx.send(embed=embed)

    @commands.command(
        aliases=["winrate"],
        brief="Individual character win rates",
        description="Prints out character win rates for a specified player",
    )
    async def win_rate(
        self,
        ctx,
        name: Optional[str] = commands.parameter(
            description="The in game name of the player to display. If left blank will use the caller",
        ),
    ):
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

    @commands.command(
        aliases=["matchHistory", "matchhistory"],
        brief="Player match history",
        description="Prints out the last 50 games for a player sorted by date",
    )
    async def match_history(
        self,
        ctx,
        name: Optional[str] = commands.parameter(
            description="The in game name of the player to view. If left blank, will use the caller"
        ),
    ):
        query = None
        if name is None:
            query = (
                select(User)
                .where(User.id == ctx.message.author.id)
                .options(selectinload(User.user_game_history))
            )
        else:
            query = (
                select(User)
                .where(User.in_game_name == name)
                .options(selectinload(User.user_game_history))
            )
        user = (await async_db_session.execute(query)).scalar()

        if user is None:
            await ctx.send("Player not found")
            return

        embed = Embed(
            title=f"Match History {user.in_game_name}",
        )

        character = ""
        vs = ""
        elo = ""
        for user_game in user.user_game_history[::-1]:
            query = (
                select(UserGame)
                .where(
                    (UserGame.game_id == user_game.game_id)
                    & (UserGame.user_id != user.id)
                )
                .options(selectinload(UserGame.user))
            )

            vs_user_game = (await async_db_session.execute(query)).scalar()

            if vs_user_game is None:
                continue

            character += f"{user_game.character}\n"
            vs += f"{vs_user_game.user.in_game_name}-{vs_user_game.character}\n"
            elo += "+" if user_game.game_result == GameResult.winner else ""
            elo += f"{user_game.user_elo_change}\n"

        embed.add_field(name="Character", value=character, inline=True)
        embed.add_field(name="VS", value=vs, inline=True)
        embed.add_field(name="Elo", value=elo, inline=True)

        await ctx.send(embed=embed)

    async def cog_command_error(
        self, ctx: commands.Context, error: commands.CommandError
    ):
        await ctx.send(f"Error with info cog: {error}")
        raise error


# this setup function needs to be in every cog in order for the bot to be able to load it
async def setup(bot):
    await bot.add_cog(InfoCog(bot))
