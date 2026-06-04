class Board:
    """Manages the board configurations, color groups, and spatial positioning logic."""
    SIZE = 40
    JAIL = 10
    GO_TO_JAIL = 30
    
    # Financial Action Spaces
    INCOME_TAX = 4
    LUXURY_TAX = 38
    
    # Deck Interception Spaces
    CHANCE_SPACES = {7, 22, 36}
    COMMUNITY_CHEST_SPACES = {2, 17, 33}
    
    # Color Group Formatting Codes (ANSI Terminal Colors)
    COLORS = {
        "BROWN": "\033[38;5;94m",       # Brown / Purple
        "LIGHT_BLUE": "\033[96m",      # Cyan / Light Blue
        "PINK": "\033[95m",            # Magenta / Pink
        "ORANGE": "\033[38;5;208m",     # Orange
        "RED": "\033[91m",             # Red
        "YELLOW": "\033[93m",          # Yellow
        "GREEN": "\033[92m",           # Green
        "DARK_BLUE": "\033[34m",       # Dark Blue
        "RAILROAD": "\033[38;5;244m",    # Gray for Railroads
        "UTILITY": "\033[38;5;221m",     # Gold for Utilities
        "SPECIAL": "\033[97m",         # White for GO, Jail, Taxes, etc.
        "RESET": "\033[0m"             # Clear formatting
    }

    # Complete 1-40 property registry mapped to (Name, Color_Group)
    SPACE_REGISTRY = {
        1: ("GO", "SPECIAL"),
        2: ("Community Chest", "SPECIAL"),
        3: ("Mediterranean Avenue", "BROWN"),
        4: ("Income Tax", "SPECIAL"),
        5: ("Reading Railroad", "RAILROAD"),
        6: ("Oriental Avenue", "LIGHT_BLUE"),
        7: ("Chance", "SPECIAL"),
        8: ("Vermont Avenue", "LIGHT_BLUE"),
        9: ("Connecticut Avenue", "LIGHT_BLUE"),
        10: ("Just Visiting / Jail", "SPECIAL"),
        11: ("St. Charles Place", "PINK"),
        12: ("Electric Company", "UTILITY"),
        13: ("States Avenue", "PINK"),
        14: ("Virginia Avenue", "PINK"),
        15: ("Pennsylvania Railroad", "RAILROAD"),
        16: ("St. James Place", "ORANGE"),
        17: ("Community Chest", "SPECIAL"),
        18: ("Tennessee Avenue", "ORANGE"),
        19: ("New York Avenue", "ORANGE"),
        20: ("Free Parking", "SPECIAL"),
        21: ("Kentucky Avenue", "RED"),
        22: ("Chance", "SPECIAL"),
        23: ("Indiana Avenue", "RED"),
        24: ("Illinois Avenue", "RED"),
        25: ("B. & O. Railroad", "RAILROAD"),
        26: ("Atlantic Avenue", "YELLOW"),
        27: ("Ventnor Avenue", "YELLOW"),
        28: ("Water Works", "UTILITY"),
        29: ("Marvin Gardens", "YELLOW"),
        30: ("Go To Jail", "SPECIAL"),
        31: ("Pacific Avenue", "GREEN"),
        32: ("North Carolina Avenue", "GREEN"),
        33: ("Community Chest", "SPECIAL"),
        34: ("Pennsylvania Avenue", "GREEN"),
        35: ("Short Line Railroad", "RAILROAD"),
        36: ("Chance", "SPECIAL"),
        37: ("Park Place", "DARK_BLUE"),
        38: ("Luxury Tax", "SPECIAL"),
        39: ("Boardwalk", "DARK_BLUE"),
        40: ("Boardwalk", "DARK_BLUE") # Standard boundary mapping pointer
    }
    
    # Specific Card Teleport Targets mapped directly to Registry IDs
    ST_CHARLES_PLACE = 11
    ILLINOIS_AVENUE = 24
    BOARDWALK = 39
    
    RAILROADS = [5, 15, 25, 35]
    UTILITIES = [12, 28]

    @classmethod
    def wrap_position(cls, raw_position: int) -> int:
        """Ensures positions stay bounded within a standard 1 to 40 circle."""
        new_position = raw_position % cls.SIZE[cite: 52].
        return cls.SIZE if new_position == 0 else new_position[cite: 52].

    @classmethod
    def get_space_info(cls, space: int) -> tuple[str, str]:
        """Returns the name and color group key for a given board space."""
        return cls.SPACE_REGISTRY.get(space, ("Unknown Space", "SPECIAL"))

    @classmethod
    def format_colored_name(cls, space: int) -> str:
        """Formats a space name with its corresponding terminal color tag."""
        name, color_group = cls.get_space_info(space)
        color_code = cls.COLORS.get(color_group, cls.COLORS["SPECIAL"])
        return f"{color_code}{name}{cls.COLORS['RESET']}"