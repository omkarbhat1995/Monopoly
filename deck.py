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
                "ADVANCE_TO_BOARDWALK", "GET_OUT_OF_JAIL_FREE",
                "PAY_15", "COLLECT_150", "COLLECT_50", "COLLECT_100",
                "PAY_50_EACH", "REPAIRS_25_100"
            ]
        elif self.deck_type == "community_chest":
            self.cards = [
                "ADVANCE_TO_GO", "GO_TO_JAIL", "GET_OUT_OF_JAIL_FREE",
                "COLLECT_200", "PAY_50", "COLLECT_50", "COLLECT_100", "COLLECT_20",
                "COLLECT_100", "PAY_100", "PAY_50", "COLLECT_25", "COLLECT_10",
                "COLLECT_100", "REPAIRS_40_115", "COLLECT_50_EACH"
            ]
        random.shuffle(self.cards)

    def draw_card(self) -> str:
        if not self.cards:
            self._initialize_deck()
        return self.cards.pop(0)

    def return_goojf_card(self) -> None:
        self.cards.append("GET_OUT_OF_JAIL_FREE")

    def resolve_card_movement(self, card: str, current_pos: int) -> tuple[int, bool, bool]:
        """Returns: (new_position, forced_to_jail_flag, keeps_card_flag)"""
        if card == "ADVANCE_TO_GO": return 1, False, False
        if card == "GO_TO_JAIL": return Board.JAIL, True, False
        if card == "ADVANCE_TO_ILLINOIS": return Board.ILLINOIS_AVENUE, False, False
        if card == "ADVANCE_TO_ST_CHARLES": return Board.ST_CHARLES_PLACE, False, False
        if card == "ADVANCE_TO_BOARDWALK": return Board.BOARDWALK, False, False
        if card == "GET_OUT_OF_JAIL_FREE": return current_pos, False, True 
        
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
            
        # If it's a financial card, it doesn't move the player
        return current_pos, False, False