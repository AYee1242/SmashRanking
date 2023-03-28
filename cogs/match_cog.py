from discord.ext import commands
from datetime import datetime
from discord import Embed, Member
from typing import Optional
from database.user import User
from database.user_character import UserCharacter
from database.game import Game
from database.user_game import UserGame, GameResult
from database.database import async_db_session
from .utils.ranking_system import RankingSystem
from .utils.assets import CHARACTERS


class MatchCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ranking_system = RankingSystem()

    @commands.Cog.listener()
    async def on_ready(self):
        print("Ready Match")

    @commands.command(
        aliases=["game", "processgame", "processmatch"],
        brief="Process smash game",
        description="Logs a smash game and updates elo for users and characters",
    )
    async def process_match(
        self,
        ctx,
        winner_name=commands.parameter(description="Winner's in game name"),
        loser_name=commands.parameter(description="Loser's in game name"),
        winner_character: Optional[str] = commands.parameter(
            description="Winner's character. If left blank will use the winner's predefined character"
        ),
        loser_character: Optional[str] = commands.parameter(
            description="Loser's character. If left blank will use the loser's predefined character"
        ),
    ):
        winner, loser = await User.get_from_name(winner_name), await User.get_from_name(
            loser_name
        )
        if winner is None:
            await ctx.send("Winner does not exist!")
            return

        if loser is None:
            await ctx.send("Loser does not exist!")
            return

        if winner_character is not None and loser_character is None:
            await ctx.send("Must specify both winner and loser champ")
            return

        if winner_character is None:
            if winner.current_character is None:
                await ctx.send("Please specify the winner's character")
                return
            winner_character = winner.current_character

        if loser_character is None:
            if loser.current_character is None:
                await ctx.send("Please specify the winner's character")
                return
            loser_character = loser.current_character

        if winner_character.title() not in CHARACTERS:
            await ctx.send(
                "Winner character does not exist, check playable characters with $characters"
            )
            return

        if loser_character.title() not in CHARACTERS:
            await ctx.send(
                "Loser character does not exist, check playable characters with $characters"
            )
            return

        needed_members = {int(winner.id), int(loser.id)}
        cancel_process = False

        def check(reaction, user):  # Our check for the reaction
            nonlocal cancel_process
            if user.id not in needed_members:
                return False

            if str(reaction.emoji) == "❌":
                cancel_process = True
                return True

            if str(reaction.emoji) == "✅":
                needed_members.remove(user.id)

            return len(needed_members) == 0

        msg = await ctx.send(
            f"Please confirm that {winner_name} as {winner_character} beat {loser_name} as {loser_character}"
        )  # Message to react to
        await msg.add_reaction("✅")
        await msg.add_reaction("❌")
        await self.bot.wait_for("reaction_add", check=check)  # Wait for a reaction

        if cancel_process:
            await ctx.send("Game cancelled")
            return

        # get user character
        winner_character_record = await UserCharacter.get_from_user_and_character(
            winner.id, winner_character
        )
        loser_character_record = await UserCharacter.get_from_user_and_character(
            loser.id, loser_character
        )

        (
            winner_user_rating_change,
            loser_user_rating_change,
        ) = self.ranking_system.compute_next_ratings(winner.elo, loser.elo)
        (
            winner_character_rating_change,
            loser_character_rating_change,
        ) = self.ranking_system.compute_next_ratings(
            winner_character_record.elo, loser_character_record.elo
        )

        winner.elo += winner_user_rating_change
        winner_character_record.elo += winner_character_rating_change
        loser.elo += loser_user_rating_change
        loser_character_record.elo += loser_character_rating_change

        # updating elo
        try:
            await async_db_session.commit()
        except Exception as e:
            await async_db_session.rollback()
            raise e

        # create the game instance
        game = await Game.create(date=datetime.now())
        await UserGame.create(
            game_result=GameResult.winner,
            user_elo_change=winner_user_rating_change,
            character_elo_change=winner_character_rating_change,
            character=winner_character,
            user_id=winner.id,
            game_id=game.id,
        )
        await UserGame.create(
            game_result=GameResult.loser,
            user_elo_change=loser_user_rating_change,
            character_elo_change=loser_character_rating_change,
            character=loser_character,
            user_id=loser.id,
            game_id=game.id,
        )

        await ctx.send(
            f"successfully processed match \n {winner_name}: +{winner_user_rating_change} overall elo and +{winner_character_rating_change} {winner_character} elo \n {loser_name}: {loser_user_rating_change} overall elo and {loser_character_rating_change} {loser_character} elo"
        )

    async def cog_command_error(
        self, ctx: commands.Context, error: commands.CommandError
    ):
        await ctx.send(f"Error with match cog: {error}")
        raise error


# this setup function needs to be in every cog in order for the bot to be able to load it
async def setup(bot):
    await bot.add_cog(MatchCog(bot))
