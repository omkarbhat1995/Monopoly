from collections import Counter
from typing import List
from dice import Dice
from board import Board
from deck import Deck
from player import Player
from renderer import GameRenderer
from bank import CentralBank
from typing import Optional

class MonopolySimulation:
    """Manages the game loop, dice, decks, and coordinates between Bank and UI."""
    def __init__(self, total_games: int = 1_000, steps_per_game: int = 100, debug_mode: bool = False, strategies: Optional[List] = None):
        self.debug_mode = debug_mode
        self.total_games = 1 if debug_mode else total_games
        self.steps_per_game = steps_per_game
        
        self.renderer = GameRenderer(self.debug_mode)
        self.bank = CentralBank(self.debug_mode)
        self.dice = Dice()
        
        # If no strategies provided, default everyone to Balanced
        from strategy import BALANCED_STRATEGY
        if strategies is None:
            strategies = [BALANCED_STRATEGY] * 4
            
        # Initialize players with their respective strategies
        self.players = [Player(f"P{i+1} ({strategies[i].name})", strategy=strategies[i]) for i in range(4)]
        
        self.chance_deck = Deck("chance")
        self.com_chest_deck = Deck("community_chest")
        
        self.visited_tracking = Counter({space: 0 for space in range(1, Board.SIZE + 1)})
        self.total_positions_logged = 0
        self.total_bankruptcies = 0
        self.average_ending_cash = {p.name: 0 for p in self.players}

    def run(self) -> None:
        if self.debug_mode: print("\n" + "═"*30 + " DEBUG ENGINE RUN " + "═"*30 + "\n")

        for game_idx in range(self.total_games):
            self.bank.reset_supply()
            for p in self.players: p.reset_for_new_game()
            self.dice.reset_doubles()

            for step in range(1, self.steps_per_game + 1):
                active_players = [p for p in self.players if not p.is_bankrupt]
                if len(active_players) <= 1: break 
                if self.debug_mode: print(f"🏁 --- Round Step {step} ---")

                for player in active_players:
                    self._execute_turn(player, active_players)

                self.renderer.render_live_board(self.bank, self.players)

            for player in self.players:
                if player.is_bankrupt: self.total_bankruptcies += 1
                self.average_ending_cash[player.name] += player.cash

        self.renderer.print_summary(
            self.total_games, self.players, self.average_ending_cash, 
            self.total_bankruptcies, self.visited_tracking, self.total_positions_logged
        )

    def _execute_turn(self, player: Player, active_players: List[Player]) -> None:
        if player.is_bankrupt: return
        dice_total = 0
        old_position = player.position
        
        # 1. Handle Jail Block
        if player.is_in_jail:
            dice_total = self._handle_jail_state(player)
            if player.is_in_jail or player.is_bankrupt: return

        # 2. Movement Block
        if dice_total == 0:
            dice_total, is_double = self.dice.roll()
            if self.debug_mode: print(f"🎲 {player.name} rolled {dice_total} {'(DOUBLES!)' if is_double else ''}")
            if self.dice.consecutive_doubles == 3:
                self._send_to_jail(player)
                return

        new_position = Board.wrap_position(player.position + dice_total)

        # 3. Special Spaces & Cards
        new_position = self._resolve_special_actions(player, new_position, active_players)

        # 4. Pass GO Validation
        if new_position < old_position and not player.is_in_jail and not player.is_bankrupt:
            player.change_cash(200)
            if self.debug_mode: print(f"    🏪 Passed GO! Collected $200.")

        # 5. Land on Property
        if not player.is_bankrupt and not player.is_in_jail:
            if self.debug_mode: print(f"    📍 Landed on {Board.format_colored_name(new_position)}")
            self._handle_property_transaction(player, new_position, dice_total, active_players)
            
        # 6. End Turn Updates
        if not player.is_bankrupt:
            player.position = new_position
            self.visited_tracking[player.position] += 1
            self.total_positions_logged += 1
            self.bank.process_unmortgage(player)
            self.bank.process_building(player)

    def _handle_jail_state(self, player: Player) -> int:
        if player.goojf_cards > 0:
            player.goojf_cards -= 1
            player.is_in_jail = False; player.turns_in_jail = 0
            self.chance_deck.return_goojf_card() 
            if self.debug_mode: print(f"    🔓 {player.name} used a GOOJF card.")
            return 0
            
        player.turns_in_jail += 1
        dice_total, is_double = self.dice.roll()
        if self.debug_mode: print(f"🔒 {player.name} in JAIL (Turn {player.turns_in_jail}/3). Rolled {dice_total}")
        
        if is_double:
            player.is_in_jail = False; player.turns_in_jail = 0
            self.dice.reset_doubles()
            return dice_total
            
        if player.turns_in_jail < 3:
            self.visited_tracking[player.position] += 1
            self.total_positions_logged += 1
            return 0
            
        player.is_in_jail = False; player.turns_in_jail = 0
        player.change_cash(-50)
        self.bank.check_bankruptcy(player, None, 50, self.chance_deck)
        if self.debug_mode and not player.is_bankrupt: print(f"    💸 Forced $50 Fee! Left prison.")
        return dice_total

    def _send_to_jail(self, player: Player) -> None:
        player.position = Board.JAIL
        player.is_in_jail = True
        player.turns_in_jail = 0
        self.dice.reset_doubles()
        self.visited_tracking[player.position] += 1
        self.total_positions_logged += 1
        if self.debug_mode: print(f"    ❌ SPEEDING TICKET / ARREST! Sent straight to Jail.")

    def _resolve_special_actions(self, player: Player, position: int, active_players: List[Player]) -> int:
        if position == Board.GO_TO_JAIL:
            self._send_to_jail(player)
            return player.position
            
        elif position == Board.INCOME_TAX:
            player.change_cash(-200)
            self.bank.check_bankruptcy(player, None, 200, self.chance_deck)
            if self.debug_mode and not player.is_bankrupt: print(f"    💸 Paid Income Tax.")
                
        elif position == Board.LUXURY_TAX:
            player.change_cash(-100)
            self.bank.check_bankruptcy(player, None, 100, self.chance_deck)
            if self.debug_mode and not player.is_bankrupt: print(f"    💸 Paid Luxury Tax.")
        
        elif position in Board.CHANCE_SPACES or position in Board.COMMUNITY_CHEST_SPACES:
            self.visited_tracking[position] += 1
            self.total_positions_logged += 1
            
            is_chance = position in Board.CHANCE_SPACES
            deck = self.chance_deck if is_chance else self.com_chest_deck
            card = deck.draw_card()
            if self.debug_mode: print(f"    {'❓ Chance' if is_chance else '📦 Chest'}: {card}")
            
            position, forced_jail, holds_card = deck.resolve_card_movement(card, position)
            
            if holds_card:
                player.goojf_cards += 1
            elif "PAY" in card or "COLLECT" in card or "REPAIRS" in card:
                self._apply_card_finances(player, card, active_players)

            if forced_jail: self._send_to_jail(player)
                
        return position

    def _apply_card_finances(self, player: Player, card: str, active_players: List[Player]) -> None:
        if card.startswith("PAY_") and not card.endswith("_EACH"):
            amt = int(card.split("_")[1])
            player.change_cash(-amt)
            self.bank.check_bankruptcy(player, None, amt, self.chance_deck)
            if self.debug_mode and not player.is_bankrupt: print(f"    💳 Paid Card Fine: ${amt}")
            
        elif card.startswith("COLLECT_") and not card.endswith("_EACH"):
            amt = int(card.split("_")[1])
            player.change_cash(amt)
            if self.debug_mode: print(f"    🤑 Collected Card Reward: ${amt}")
            
        elif card == "PAY_50_EACH":
            for p in active_players:
                if p != player and not p.is_bankrupt:
                    p.change_cash(50); player.change_cash(-50)
            self.bank.check_bankruptcy(player, None, 50, self.chance_deck)
            
        elif card == "COLLECT_50_EACH":
            for p in active_players:
                if p != player and not p.is_bankrupt:
                    p.change_cash(-50)
                    actual_paid = self.bank.check_bankruptcy(p, player, 50, self.chance_deck)
                    player.change_cash(actual_paid)
                    
        elif card.startswith("REPAIRS_"):
            h_cost, H_cost = int(card.split("_")[1]), int(card.split("_")[2])
            total = sum(H_cost if h == 5 else h * h_cost for h in player.buildings.values())
            if total > 0:
                player.change_cash(-total)
                self.bank.check_bankruptcy(player, None, total, self.chance_deck)
                if self.debug_mode and not player.is_bankrupt: print(f"    🛠️ Paid ${total} in repairs.")

    def _handle_property_transaction(self, player: Player, space_id: int, dice_total: int, active_players: List[Player]) -> None:
        cost = Board.SPACE_REGISTRY[space_id][2]
        if cost == 0: return  

        if space_id not in self.bank.property_owners:
            # AI Check: Buy using the specific strategy buffer
            if player.cash >= (cost + player.strategy.buy_buffer):
                player.change_cash(-cost)
                player.owned_properties.add(space_id)
                self.bank.property_owners[space_id] = player
                if self.debug_mode: print(f"    💰 {player.name} bought {Board.format_colored_name(space_id)}.")
            else:
                if self.debug_mode: print(f"    ⚖️ {player.name} declined {Board.format_colored_name(space_id)}. AUCTION!")
                self.bank.execute_auction(space_id, active_players)
                
        elif self.bank.property_owners[space_id] != player:
            owner = self.bank.property_owners[space_id]
            if not owner.is_bankrupt:
                rent = self.bank.calculate_rent(space_id, owner, dice_total)
                if rent > 0:
                    player.change_cash(-rent)
                    actual_paid = self.bank.check_bankruptcy(player, owner, rent, self.chance_deck)
                    owner.change_cash(actual_paid)
                    if self.debug_mode and not player.is_bankrupt:
                        print(f"    💸 Rent! {player.name} paid ${actual_paid} to {owner.name} for {Board.format_colored_name(space_id)}.")
