class PlayerStrategy:
    """Defines the economic risk tolerance and bidding behavior of a player."""
    def __init__(self, name: str, buy_buffer: int, build_buffer: int, auction_base_mult: float, auction_set_mult: float, auction_buffer: int):
        self.name = name
        # Cash buffer required to buy an unowned property from the bank
        self.buy_buffer = buy_buffer 
        # Cash buffer required to build a house/hotel
        self.build_buffer = build_buffer 
        # Multiplier of base price player is willing to bid in an auction
        self.auction_base_mult = auction_base_mult 
        # Multiplier of base price willing to bid IF the property completes a monopoly set
        self.auction_set_mult = auction_set_mult 
        # Minimum cash they refuse to dip below during an auction
        self.auction_buffer = auction_buffer 

# Pre-configured AI Profiles
BALANCED_STRATEGY = PlayerStrategy("Balanced", buy_buffer=100, build_buffer=150, auction_base_mult=1.0, auction_set_mult=2.0, auction_buffer=10)
AGGRESSIVE_STRATEGY = PlayerStrategy("Aggressive", buy_buffer=0, build_buffer=10, auction_base_mult=1.5, auction_set_mult=2.5, auction_buffer=0)
CONSERVATIVE_STRATEGY = PlayerStrategy("Conservative", buy_buffer=300, build_buffer=400, auction_base_mult=0.5, auction_set_mult=1.5, auction_buffer=50)