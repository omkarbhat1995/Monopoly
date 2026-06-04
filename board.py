class Board:
    """Manages the board configurations, color groups, property pricing, and spatial logic."""
    SIZE = 40
    JAIL = 10
    GO_TO_JAIL = 30
    
    INCOME_TAX = 4
    LUXURY_TAX = 38
    
    CHANCE_SPACES = {7, 22, 36}
    COMMUNITY_CHEST_SPACES = {2, 17, 33}
    
    COLORS = {
        "BROWN": "\033[38;5;94m",       
        "LIGHT_BLUE": "\033[96m",      
        "PINK": "\033[95m",            
        "ORANGE": "\033[38;5;208m",     
        "RED": "\033[91m",             
        "YELLOW": "\033[93m",          
        "GREEN": "\033[92m",           
        "DARK_BLUE": "\033[34m",       
        "RAILROAD": "\033[38;5;244m",    
        "UTILITY": "\033[38;5;221m",     
        "SPECIAL": "\033[97m",         
        "RESET": "\033[0m"             
    }

    # Registry structure: space_id: (Name, Group, Cost, House_Cost, [Rent_0, Rent_1, Rent_2, Rent_3, Rent_4, Rent_Hotel])
    # Non-purchasable spaces have a Cost of 0.
    SPACE_REGISTRY = {
        1:  ("GO", "SPECIAL", 0, 0, [0]),
        2:  ("Community Chest", "SPECIAL", 0, 0, [0]),
        3:  ("Mediterranean Avenue", "BROWN", 60, 50, [2, 10, 30, 90, 160, 250]),
        4:  ("Income Tax", "SPECIAL", 0, 0, [0]),
        5:  ("Reading Railroad", "RAILROAD", 200, 0, [25, 50, 100, 200]), # Rents scaled by number owned
        6:  ("Oriental Avenue", "LIGHT_BLUE", 100, 50, [6, 30, 90, 270, 400, 550]),
        7:  ("Chance", "SPECIAL", 0, 0, [0]),
        8:  ("Vermont Avenue", "LIGHT_BLUE", 100, 50, [6, 30, 90, 270, 400, 550]),
        9:  ("Connecticut Avenue", "LIGHT_BLUE", 120, 50, [8, 40, 100, 300, 450, 600]),
        10: ("Just Visiting / Jail", "SPECIAL", 0, 0, [0]),
        11: ("St. Charles Place", "PINK", 140, 100, [10, 50, 150, 450, 625, 750]),
        12: ("Electric Company", "UTILITY", 150, 0, [4, 10]), # Multipliers for 1 or 2 utilities
        13: ("States Avenue", "PINK", 140, 100, [10, 50, 150, 450, 625, 750]),
        14: ("Virginia Avenue", "PINK", 160, 100, [12, 60, 180, 500, 700, 900]),
        15: ("Pennsylvania Railroad", "RAILROAD", 200, 0, [25, 50, 100, 200]),
        16: ("St. James Place", "ORANGE", 180, 100, [14, 70, 200, 550, 750, 950]),
        17: ("Community Chest", "SPECIAL", 0, 0, [0]),
        18: ("Tennessee Avenue", "ORANGE", 180, 100, [14, 70, 200, 550, 750, 950]),
        19: ("New York Avenue", "ORANGE", 200, 100, [16, 80, 220, 600, 800, 1000]),
        20: ("Free Parking", "SPECIAL", 0, 0, [0]),
        21: ("Kentucky Avenue", "RED", 220, 150, [18, 90, 250, 700, 875, 1050]),
        22: ("Chance", "SPECIAL", 0, 0, [0]),
        23: ("Indiana Avenue", "RED", 220, 150, [18, 90, 250, 700, 875, 1050]),
        24: ("Illinois Avenue", "RED", 240, 150, [20, 100, 300, 750, 925, 1100]),
        25: ("B. & O. Railroad", "RAILROAD", 200, 0, [25, 50, 100, 200]),
        26: ("Atlantic Avenue", "YELLOW", 260, 150, [22, 110, 330, 800, 975, 1150]),
        27: ("Ventnor Avenue", "YELLOW", 260, 150, [22, 110, 330, 800, 975, 1150]),
        28: ("Water Works", "UTILITY", 150, 0, [4, 10]),
        29: ("Marvin Gardens", "YELLOW", 280, 150, [24, 120, 360, 850, 1025, 1200]),
        30: ("Go To Jail", "SPECIAL", 0, 0, [0]),
        31: ("Pacific Avenue", "GREEN", 300, 200, [26, 130, 390, 900, 1100, 1275]),
        32: ("North Carolina Avenue", "GREEN", 300, 200, [26, 130, 390, 900, 1100, 1275]),
        33: ("Community Chest", "SPECIAL", 0, 0, [0]),
        34: ("Pennsylvania Avenue", "GREEN", 320, 200, [28, 150, 450, 1000, 1200, 1400]),
        35: ("Short Line Railroad", "RAILROAD", 200, 0, [25, 50, 100, 200]),
        36: ("Chance", "SPECIAL", 0, 0, [0]),
        37: ("Park Place", "DARK_BLUE", 350, 200, [35, 175, 500, 1100, 1300, 1500]),
        38: ("Luxury Tax", "SPECIAL", 0, 0, [0]),
        39: ("Boardwalk", "DARK_BLUE", 400, 200, [50, 200, 600, 1400, 1700, 2000]),
        40: ("Boardwalk", "DARK_BLUE", 400, 200, [50, 200, 600, 1400, 1700, 2000])
    }
    
    ST_CHARLES_PLACE = 11
    ILLINOIS_AVENUE = 24
    BOARDWALK = 39
    
    RAILROADS = [5, 15, 25, 35]
    UTILITIES = [12, 28]

    # Defines count required to achieve a full set monopoly color match
    COLOR_COUNTS = {
        "BROWN": 2, "LIGHT_BLUE": 3, "PINK": 3, "ORANGE": 3,
        "RED": 3, "YELLOW": 3, "GREEN": 3, "DARK_BLUE": 2
    }

    @classmethod
    def wrap_position(cls, raw_position: int) -> int:
        new_position = raw_position % cls.SIZE
        return cls.SIZE if new_position == 0 else new_position

    @classmethod
    def get_space_info(cls, space: int) -> tuple:
        """Returns the name, group, and pricing data for a given board space."""
        # Returns a safe placeholder tuple if the space key is not found
        return cls.SPACE_REGISTRY.get(space, ("Unknown Space", "SPECIAL", 0, 0, [0]))

    @classmethod
    def format_colored_name(cls, space: int) -> str:
        info = cls.get_space_info(space)
        name, group = info[0], info[1]
        color_code = cls.COLORS.get(group, cls.COLORS["SPECIAL"])
        return f"{color_code}{name}{cls.COLORS['RESET']}"