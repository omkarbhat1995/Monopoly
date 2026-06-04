import random
from board import Board

class Deck:
    """Manages card inventories, shuffles, and action resolution logic."""
    def __init__(self, deck_type: str):
        self.deck_type = deck_type.lower()
        self.cards = []
        self._initialize_deck()

    def _initialize_deck(self) -> None:
        if self.deck_type == "chance":
            self.cards = [
                "ADVANCE_TO_GO", "ADVANCE_TO_ILLINOIS", "ADVANCE_TO_ST_CHARLES",
                "ADVANCE_TO_NEAREST_RAILROAD", "ADVANCE_TO_NEAREST_RAILROAD",
                "ADVANCE_TO_NEAREST_UTILITY", "GO_BACK_3_SPACES", "GO_TO_JAIL",
                "GET_OUT_OF_JAIL_FREE"  # Chance contains 1 escape card
            ] + ["FILLER_CARD"] * 7
        elif self.deck_type == "community_chest":
            self.cards = [
                "ADVANCE_TO_GO", "GO_TO_JAIL", "GET_OUT_OF_JAIL_FREE"  # Chest contains 1 escape card
            ] + ["FILLER_CARD"] * 13
            
        random.shuffle(self.cards)

    def draw_card(self) -> str:
        """Draws top card. If it's a GOOJF card, it's held out of rotation."""
        if not self.cards:
            self._initialize_deck()
        return self.cards.pop(0)

    def return_goojf_card(self) -> None:
        """Recycles a used GOOJF card back into the bottom of the deck pile."""
        self.cards.append("GET_OUT_OF_JAIL_FREE")

    def resolve_card_movement(self, card: str, current_pos: int) -> tuple[int, bool, bool]:
        """
        Returns: (new_position, forced_to_jail_flag, keeps_card_flag)
        """
        if card == "ADVANCE_TO_GO":
            return 1, False, False
        if card == "GO_TO_JAIL":
            return Board.JAIL, True, False
        if card == "ADVANCE_TO_ILLINOIS":
            return Board.ILLINOIS_AVENUE, False, False
        if card == "ADVANCE_TO_ST_CHARLES":
            return Board.ST_CHARLES_PLACE, False, False
        if card == "GET_OUT_OF_JAIL_FREE":
            return current_pos, False, True  # Player keeps card, no movement
        
        if card == "ADVANCE_TO_NEAREST_RAILROAD":
            for rr in Board.RAILROADS:
                if rr > current_pos: return rr, False, False
            return Board.RAILROADS[0], False, False
            
        if card == "ADVANCE_TO_NEAREST_UTILITY":
            for util in Board.UTILITIES:
                if util > current_pos: return util, False, False
            return Board.UTILITIES[0], False, False
            
        if card == "GO_BACK_3_SPACES":
            new_pos = current_pos - 3
            if new_pos <= 0: new_pos += Board.SIZE
            return new_pos, False, False
            
        return current_pos, False, False