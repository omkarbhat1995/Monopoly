class Player:
    """Tracks cash balances, property inventories, jail states, and mortgages."""
    def __init__(self, name: str, starting_cash: int = 1500):
        self.name = name
        self.position = 1
        self.cash = starting_cash
        self.is_bankrupt = False
        
        self.is_in_jail = False
        self.turns_in_jail = 0
        self.goojf_cards = 0
        
        self.owned_properties = set()
        self.mortgaged_properties = set()  # Tracks IDs of mortgaged land
        self.buildings = {}

    def change_cash(self, amount: int) -> None:
        """Adjusts cash. Bankruptcy is now handled externally by the liquidation engine."""
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
        count = 0
        for pid in self.owned_properties:
            if board_registry[pid][1] == group_name:
                count += 1
        return count
        
    def has_mortgaged_in_group(self, group_name: str, board_registry: dict) -> bool:
        """Checks if any property in a color group is currently mortgaged."""
        for pid in self.mortgaged_properties:
            if board_registry[pid][1] == group_name:
                return True
        return False