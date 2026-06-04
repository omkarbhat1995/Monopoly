class Player:
    """Tracks cash balances, bankrupt flags, and board placement coordinates."""
    def __init__(self, starting_cash: int = 1500):
        self.position = 1
        self.cash = starting_cash
        self.is_bankrupt = False

    def change_cash(self, amount: int) -> None:
        """Modifies player liquidity reserves and handles insolvency thresholds."""
        self.cash += amount
        if self.cash < 0:
            self.is_bankrupt = True

    def reset_for_new_game(self) -> None:
        """Restores properties to defaults for clean standalone batch runs."""
        self.position = 1
        self.cash = 1500
        self.is_bankrupt = False