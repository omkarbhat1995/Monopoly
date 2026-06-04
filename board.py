class Board:
    """Manages the board configurations and spatial positioning logic."""
    SIZE = 40
    JAIL = 10
    GO_TO_JAIL = 30

    @classmethod
    def wrap_position(cls, raw_position: int) -> int:
        """Ensures positions stay bounded within a standard 1 to 40 circle."""
        new_position = raw_position % cls.SIZE
        return cls.SIZE if new_position == 0 else new_position

    @classmethod
    def get_special_label(cls, space: int) -> str:
        """Provides human-readable labels for primary landmark spaces."""
        if space == cls.JAIL: 
            return " (Jail)"
        if space == cls.GO_TO_JAIL: 
            return " (Go To Jail)"
        if space == 1: 
            return " (GO)"
        return ""