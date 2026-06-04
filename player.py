from strategy import PlayerStrategy, BALANCED_STRATEGY

class Player:
    """Tracks cash balances, property inventories, jail states, and mortgages."""
    # Added strategy parameter with a default fallback
    def __init__(self, name: str, starting_cash: int = 1500, strategy: PlayerStrategy = BALANCED_STRATEGY):
        self.name = name
        self.strategy = strategy
        self.position = 1
        self.cash = starting_cash
        self.is_bankrupt = False
        
        self.is_in_jail = False
        self.turns_in_jail = 0
        self.goojf_cards = 0
        
        self.owned_properties = set()
        self.mortgaged_properties = set()  
        self.buildings = {}

    def change_cash(self, amount: int) -> None:
        self.cash += amount

    def reset_for_new_game(self) -> None:
        self.position = 1
        self.cash = 1500
        self.is_bankrupt = False
        self.is_in_jail = False
        self.turns_in_jail = 0
        self.goojf_cards = 0
        self.owned_properties.clear()
        self.mortgaged_properties.clear()
        self.buildings.clear()

    def count_owned_in_group(self, group_name: str, board_registry: dict) -> int:
        return sum(1 for pid in self.owned_properties if board_registry[pid][1] == group_name)
        
    def has_mortgaged_in_group(self, group_name: str, board_registry: dict) -> bool:
        return any(board_registry[pid][1] == group_name for pid in self.mortgaged_properties)