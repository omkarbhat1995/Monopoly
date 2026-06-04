import random

class Dice:
    """Handles dice rolling mechanics and consecutive doubles tracking."""
    
    def __init__(self, sides: int = 6):
        self.sides = sides
        self.consecutive_doubles = 0

    def roll(self) -> tuple[int, int, int, bool]:
        """
        Rolls two dice.
        Returns: (die1, die2, total, is_double)
        """
        die1 = random.randint(1, self.sides)
        die2 = random.randint(1, self.sides)
        total = die1 + die2
        is_double = (die1 == die2)

        if is_double:
            self.consecutive_doubles += 1
        else:
            self.reset_doubles()

        return die1, die2, total, is_double

    def reset_doubles(self) -> None:
        """Resets the consecutive doubles tracker back to zero."""
        self.consecutive_doubles = 0

    @property
    def has_speeded(self) -> bool:
        """Returns True if the player rolled doubles three times in a row."""
        return self.consecutive_doubles == 3