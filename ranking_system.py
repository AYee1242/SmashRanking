class RankingSystem:
    """A system to compute the next ratings after two players face off in a match"""

    def __init__(
        self, k_factor: int = 32, scale_factor: int = 32, exponent_base: int = 10
    ) -> None:
        """
        Args:
            k_factor (int, optional): maximum ratings change from a single game. Defaults to 32.
            scale_factor (int, optional): measures how much a 1 point of difference in the rating will affect the score. Defaults to 32.
            exponent_base (int, optional): exponent base when calculating expected player score. Defaults to 10.
        """
        self.k_factor = k_factor
        self.scale_factor = scale_factor
        self.exponent_base = exponent_base

    def expectedPlayerScore(self, rating_difference: int) -> float:
        """Computes the probability that a player would win

        Args:
            rating_difference (int): difference in rating between opponent and the player

        Returns:
            float: The probability that a player would win expressed within [0,1]
        """
        exponent = rating_difference / self.scale_factor
        return 1 / (1 + (self.exponent_base) ^ exponent)

    def nextRating(self, cur_rating: int, expected_score: float, score: int) -> int:
        """Computes the next rating of a player

        Args:
            cur_rating (int): rating of the player before the match
            expected_score (float): The probability that the player would win
            score (int): the score that the player achieved by winning/losing the game

        Returns:
            int: the new rating of the player
        """
        delta = round(self.k_factor * (score - expected_score))
        return cur_rating + delta

    def computeNextRatings(
        self, winner_rating: int, loser_rating: int
    ) -> tuple[int, int]:
        """Determines the next ratings between two players

        Args:
            winner_rating (int): the rating of the winner before the match
            loser_rating (int): the rating of the loser before the match

        Returns:
            tuple[int, int]: the new ratings with winner coming first
        """
        winner_rating_diff = loser_rating - winner_rating
        loser_rating_diff = winner_rating - loser_rating

        expected_winner_score = self.expectedPlayerScore(winner_rating_diff)
        expected_loser_score = self.expectedPlayerScore(loser_rating_diff)

        new_winner_rating = self.nextRating(winner_rating, expected_winner_score, 1)
        new_loser_rating = self.nextRating(loser_rating, expected_loser_score, 0)

        return new_winner_rating, new_loser_rating
