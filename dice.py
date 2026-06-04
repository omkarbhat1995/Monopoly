import random

class Dice:
    """Handles dice rolling mechanics and consecutive doubles tracking."""
    def __init__(self, sides: int = 6):
        self.sides = sides
        self.consecutive_doubles = 0

    def roll(self) -> tuple[int, bool]:
        """
        Rolls two dice.
        Returns: (dice_total, is_double)
        """
        die1 = random.randint(1, self.sides)
        die2 = random.randint(1, self.sides)
        is_double = (die1 == die2)

        if is_double:
            self.consecutive_doubles += 1
        else:
            self.consecutive_doubles = 0

        return (die1 + die2), is_double
        
    def reset_doubles(self) -> None:
        """Explicitly resets the consecutive doubles tracker."""
        self.consecutive_doubles = 0