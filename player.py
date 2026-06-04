class Player:
    """Tracks cash balances, property inventories, jail states, and bankrupt profiles."""
    def __init__(self, name: str, starting_cash: int = 1500):
        self.name = name
        self.position = 1
        self.cash = starting_cash
        self.is_bankrupt = False
        
        # Jail state tracking parameters
        self.is_in_jail = False
        self.turns_in_jail = 0
        
        self.owned_properties = set()
        self.buildings = {}

    def change_cash(self, amount: int) -> None:
        self.cash += amount
        if self.cash < 0:
            self.is_bankrupt = True

    def reset_for_new_game(self) -> None:
        self.position = 1
        self.cash = 1500
        self.is_bankrupt = False
        self.is_in_jail = False
        self.turns_in_jail = 0
        self.owned_properties.clear()
        self.buildings.clear()

    def count_owned_in_group(self, group_name: str, board_registry: dict) -> int:
        count = 0
        for pid in self.owned_properties:
            if board_registry[pid][1] == group_name:
                count += 1
        return count