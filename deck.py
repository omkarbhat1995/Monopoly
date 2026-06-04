import random
from board import Board

class Deck:
    """Manages card inventories, shuffles, and action resolution logic."""
    def __init__(self, deck_type: str):
        self.deck_type = deck_type.lower()
        self.cards = []
        self._initialize_deck()

    def _initialize_deck(self) -> None:
        """Generates standard movement cards + placeholder filler cards."""
        if self.deck_type == "chance":
            # 16 Total Cards: 9 Movement Commands, 7 General Finance Placeholders
            self.cards = [
                "ADVANCE_TO_GO", "ADVANCE_TO_ILLINOIS", "ADVANCE_TO_ST_CHARLES",
                "ADVANCE_TO_NEAREST_RAILROAD", "ADVANCE_TO_NEAREST_RAILROAD",
                "ADVANCE_TO_NEAREST_UTILITY", "GO_BACK_3_SPACES", "GO_TO_JAIL",
                "CHAIRMAN_OF_THE_BOARD"  # Fixed movement targets
            ] + ["FILLER_CARD"] * 7
        elif self.deck_type == "community_chest":
            # 16 Total Cards: 2 Movement Commands, 14 Financial Placeholders
            self.cards = [
                "ADVANCE_TO_GO", "GO_TO_JAIL"
            ] + ["FILLER_CARD"] * 14
            
        random.shuffle(self.cards)

    def draw_card(self) -> str:
        """Draws top card and recycles it to the bottom of the deck stack."""
        card = self.cards.pop(0)
        self.cards.append(card)
        return card

    def resolve_card_movement(self, card: str, current_pos: int) -> tuple[int, bool]:
        """
        Determines if a card shifts a piece spatially.
        Returns: (new_position, forced_to_jail_flag)
        """
        if card == "ADVANCE_TO_GO":
            return 1, False
        if card == "GO_TO_JAIL":
            return Board.JAIL, True
        if card == "ADVANCE_TO_ILLINOIS":
            return Board.ILLINOIS_AVENUE, False
        if card == "ADVANCE_TO_ST_CHARLES":
            return Board.ST_CHARLES_PLACE, False
        
        if card == "ADVANCE_TO_NEAREST_RAILROAD":
            for rr in Board.RAILROADS:
                if rr > current_pos:
                    return rr, False
            return Board.RAILROADS[0], False # Wrap to first railroad
            
        if card == "ADVANCE_TO_NEAREST_UTILITY":
            for util in Board.UTILITIES:
                if util > current_pos:
                    return util, False
            return Board.UTILITIES[0], False # Wrap to first utility
            
        if card == "GO_BACK_3_SPACES":
            new_pos = current_pos - 3
            if new_pos <= 0:
                new_pos += Board.SIZE
            return new_pos, False
            
        return current_pos, False # Filler card, no movement changes    