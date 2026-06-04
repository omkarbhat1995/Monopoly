import time
from collections import Counter
from typing import Optional, List
from dice import Dice
from board import Board
from deck import Deck
from player import Player

# ==========================================
# 1. UI / DISPLAY SUBSYSTEM
# ==========================================
class GameRenderer:
    """Isolates all terminal outputs, visual maps, and statistical summaries."""
    def __init__(self, debug_mode: bool):
        self.debug_mode = debug_mode

    def render_live_board(self, bank: 'CentralBank', players: List[Player]) -> None:
        if not self.debug_mode: return
        
        print("\n" + "═"*18 + f" LIVE BOARD MAP (Bank: {bank.houses}H, {bank.hotels} Hotels) " + "═"*18)
        print(f"{'ID':<3} | {'Space Property Name':<35} | {'Ownership/Structure State':<30} | Tokens")
        print("-" * 85)
        
        for space in range(1, Board.SIZE + 1):
            name, group = Board.get_space_info(space)[:2]
            colored_name = Board.format_colored_name(space)
            
            tokens_on_space = [p.name for p in players if p.position == space and not p.is_bankrupt]
            token_str = " ".join(tokens_on_space) if tokens_on_space else ""
            
            struct_str = ""
            if space in bank.property_owners:
                owner = bank.property_owners[space]
                if space in owner.mortgaged_properties:
                    build_label = "Mortgaged"
                else:
                    houses = owner.buildings.get(space, 0)
                    build_label = f"Hotel" if houses == 5 else f"{houses}H" if houses > 0 else "Unimproved"
                struct_str = f"Owned by {owner.name} ({build_label})"
            elif Board.SPACE_REGISTRY[space][2] > 0:
                struct_str = f"For Sale: ${Board.SPACE_REGISTRY[space][2]}"
                
            ansi_padding = 45 if group in ["BROWN", "ORANGE", "RAILROAD", "UTILITY"] else 35
            print(f"{space:02d}  | {colored_name:<{ansi_padding}} | {struct_str:<30} | {token_str}")
        print("═"*86 + "\n")
        time.sleep(0.4)

    def print_summary(self, total_games: int, players: List[Player], average_cash: dict, bankruptcies: int, visited_tracking: Counter, total_logged: int) -> None:
        print(f"\n" + "═"*25 + f" SIMULATION SUMMARY " + "═"*25)
        
        if total_games == 1:
            print("\n--- FINAL GAME STATE & ASSET PORTFOLIO ---")
            for player in players:
                status = "Bankrupt" if player.is_bankrupt else "Active"
                print(f"\n👤 {player.name} | Cash: ${player.cash} | Status: {status}")
                if player.owned_properties:
                    print(f"   Owned Properties ({len(player.owned_properties)}):")
                    for space_id in sorted(player.owned_properties):
                        name, group = Board.get_space_info(space_id)[:2]
                        colored_name = Board.format_colored_name(space_id)
                        
                        if space_id in player.mortgaged_properties:
                            build_status = " [Mortgaged]"
                        else:
                            houses = player.buildings.get(space_id, 0)
                            if houses == 0: build_status = " [Unimproved]"
                            elif houses == 5: build_status = " [🏨 HOTEL]"
                            else: build_status = f" [{houses} 🏠]"
                                
                        ansi_padding = 45 if group in ["BROWN", "ORANGE", "RAILROAD", "UTILITY"] else 35
                        print(f"      - {colored_name:<{ansi_padding}} {build_status}")
                else:
                    print("   Owned Properties: None")
            print("\n" + "-" * 70)
        else:
            print("\n--- FINANCIAL STATUS (AVERAGES) ---")
            print(f"{'Player Name':<15} | {'Avg Ending Cash':<18} | {'Status'}")
            print("-" * 45)
            for name, total_cash in average_cash.items():
                avg_cash = total_cash / total_games
                status = "Bankrupt" if avg_cash <= 0 else "Active"
                print(f"{name:<15} | ${avg_cash:<17.2f} | {status}")
            print(f"\nTotal Bankruptcies Triggered Across Simulation: {bankruptcies:,}")
            
        print("\n--- BOARD HEATMAP (MOST LANDED ON) ---")
        print(f"{'ID':<3} | {'Space Name':<35} | {'Group':<12} | {'Total Visits':<12} | {'Landed %':<10}")
        print("-" * 85)
        sorted_visits = sorted(visited_tracking.items(), key=lambda item: item[1], reverse=True)
        for space, visits in sorted_visits:
            name, group = Board.get_space_info(space)[:2]
            colored_name = Board.format_colored_name(space)
            percentage = (visits / total_logged) * 100 if total_logged > 0 else 0
            ansi_padding = 45 if group in ["BROWN", "ORANGE", "RAILROAD", "UTILITY"] else 35
            print(f"{space:02d}  | {colored_name:<{ansi_padding}} | {group:<12} | {visits:<12,} | {percentage:.2f}%")


# ==========================================
# 2. ECONOMIC SUBSYSTEM
# ==========================================
class CentralBank:
    """Manages global housing supply, property deeds, liquidations, and auctions."""
    def __init__(self, debug_mode: bool):
        self.debug_mode = debug_mode
        self.houses = 32
        self.hotels = 12
        self.property_owners = {}

    def reset_supply(self) -> None:
        self.houses = 32
        self.hotels = 12
        self.property_owners.clear()

    def process_liquidation(self, player: Player) -> None:
        """Sells structures and mortgages land if player is in debt."""
        if player.cash >= 0: return
            
        # 1. Liquidate Houses (Uniformly)
        while sum(player.buildings.values()) > 0 and player.cash < 0:
            sold_this_loop = False
            for space_id in list(player.buildings.keys()):
                group = Board.SPACE_REGISTRY[space_id][1]
                group_props = [p for p in player.owned_properties if Board.SPACE_REGISTRY[p][1] == group]
                current_houses = player.buildings.get(space_id, 0)
                max_houses = max(player.buildings.get(p, 0) for p in group_props)
                
                if current_houses == max_houses and current_houses > 0:
                    house_sell_price = Board.SPACE_REGISTRY[space_id][3] // 2
                    if current_houses == 5: 
                        if self.houses >= 4:
                            self.hotels += 1; self.houses -= 4
                            player.buildings[space_id] = 4
                            player.change_cash(house_sell_price)
                        else:
                            self.hotels += 1
                            player.buildings[space_id] = 0
                            player.change_cash(house_sell_price * 5)
                    else: 
                        self.houses += 1
                        player.buildings[space_id] -= 1
                        player.change_cash(house_sell_price)
                        
                    if self.debug_mode: print(f"    📉 {player.name} sold structures on {Board.format_colored_name(space_id)}.")
                    if player.buildings[space_id] == 0: del player.buildings[space_id]
                    sold_this_loop = True; break 
            if not sold_this_loop: break 

        # 2. Mortgage Land
        if player.cash < 0:
            unmortgaged = player.owned_properties - player.mortgaged_properties
            for space_id in list(unmortgaged):
                if player.cash >= 0: break
                mortgage_value = Board.SPACE_REGISTRY[space_id][2] // 2
                player.mortgaged_properties.add(space_id)
                player.change_cash(mortgage_value)
                if self.debug_mode: print(f"    🏦 {player.name} mortgaged {Board.format_colored_name(space_id)}.")

    def check_bankruptcy(self, player: Player, creditor: Optional[Player], amount_owed: int, chance_deck: Deck) -> int:
        """Determines if a player survives debt, otherwise handles asset transfers."""
        if player.cash >= 0: return amount_owed
        self.process_liquidation(player)
        if player.cash >= 0: return amount_owed 
            
        actual_paid = amount_owed + player.cash 
        player.cash = 0; player.is_bankrupt = True
        
        if creditor: # Transfer to Player
            for space_id in list(player.owned_properties):
                self.property_owners[space_id] = creditor
                creditor.owned_properties.add(space_id)
                if space_id in player.mortgaged_properties: creditor.mortgaged_properties.add(space_id)
            creditor.goojf_cards += player.goojf_cards
            if self.debug_mode: print(f"    💀 {player.name} BANKRUPT! Assets seized by {creditor.name}.")
        else: # Transfer to Bank
            for space_id in list(player.owned_properties): del self.property_owners[space_id]
            for _ in range(player.goojf_cards): chance_deck.return_goojf_card()
            if self.debug_mode: print(f"    💀 {player.name} BANKRUPT to the Bank! Properties released.")
        return actual_paid

    def calculate_rent(self, space_id: int, owner: Player, dice_total: int) -> int:
        if space_id in owner.mortgaged_properties: return 0  
        info = Board.get_space_info(space_id)
        group, rent_table = info[1], info[4]
        houses = owner.buildings.get(space_id, 0)

        if group == "RAILROAD":
            num_owned = owner.count_owned_in_group("RAILROAD", Board.SPACE_REGISTRY)
            return rent_table[min(num_owned - 1, 3)]
        if group == "UTILITY":
            num_owned = owner.count_owned_in_group("UTILITY", Board.SPACE_REGISTRY)
            return dice_total * (10 if num_owned == 2 else 4)
        if houses > 0: return rent_table[houses]

        num_owned = owner.count_owned_in_group(group, Board.SPACE_REGISTRY)
        if num_owned == Board.COLOR_COUNTS.get(group, 0): return rent_table[0] * 2
        return rent_table[0]

    def execute_auction(self, space_id: int, active_players: List[Player]) -> None:
        """Simulates a Vickrey Auction based on AI cash limits and monopolies."""
        bidders = [p for p in active_players if not p.is_bankrupt]
        if not bidders: return

        base_price, group = Board.SPACE_REGISTRY[space_id][2], Board.SPACE_REGISTRY[space_id][1]
        max_bids = {}

        for p in bidders:
            valuation = base_price
            num_owned = p.count_owned_in_group(group, Board.SPACE_REGISTRY)
            if group in Board.COLOR_COUNTS and num_owned == Board.COLOR_COUNTS[group] - 1:
                valuation = base_price * 2 # Bid aggressively to complete a set
            max_bids[p] = max(0, min(valuation, p.cash - 10))

        sorted_bidders = sorted(max_bids.items(), key=lambda x: x[1], reverse=True)
        winner, highest_bid = sorted_bidders[0]

        if highest_bid <= 0:
            if self.debug_mode: print(f"    🚫 Auction passed on {Board.format_colored_name(space_id)}.")
            return

        second_highest_bid = sorted_bidders[1][1] if len(sorted_bidders) > 1 else 0
        winning_price = min(max(10, second_highest_bid + 1), highest_bid)

        winner.change_cash(-winning_price)
        winner.owned_properties.add(space_id)
        self.property_owners[space_id] = winner
        if self.debug_mode: print(f"    🔨 AUCTION WON! {winner.name} sniped {Board.format_colored_name(space_id)} for ${winning_price}.")

    def process_unmortgage(self, player: Player) -> None:
        if player.is_bankrupt or not player.mortgaged_properties: return
        for space_id in list(player.mortgaged_properties):
            unmortgage_cost = int((Board.SPACE_REGISTRY[space_id][2] // 2) * 1.1)
            if player.cash > (unmortgage_cost + 300): # Safe buffer
                player.change_cash(-unmortgage_cost)
                player.mortgaged_properties.remove(space_id)
                if self.debug_mode: print(f"    📈 {player.name} unmortgaged {Board.format_colored_name(space_id)}.")

    def process_building(self, player: Player) -> None:
        """Builds houses symmetrically if player holds an unmortgaged monopoly."""
        if player.is_bankrupt: return
        valid_groups = []
        for space_id in player.owned_properties:
            group = Board.SPACE_REGISTRY[space_id][1]
            if group in Board.COLOR_COUNTS and group not in valid_groups:
                if player.count_owned_in_group(group, Board.SPACE_REGISTRY) == Board.COLOR_COUNTS[group]:
                    if not player.has_mortgaged_in_group(group, Board.SPACE_REGISTRY):
                        valid_groups.append(group)
                        
        for group in valid_groups:
            group_props = [p for p in player.owned_properties if Board.SPACE_REGISTRY[p][1] == group]
            house_cost = Board.SPACE_REGISTRY[group_props[0]][3]
            
            building = True
            while building:
                building = False
                for space_id in group_props:
                    current_houses = player.buildings.get(space_id, 0)
                    min_houses = min(player.buildings.get(p, 0) for p in group_props)
                    
                    if current_houses == min_houses and current_houses < 5 and player.cash > (house_cost + 150):
                        if current_houses < 4 and self.houses > 0:
                            self.houses -= 1
                            player.change_cash(-house_cost)
                            player.buildings[space_id] = current_houses + 1
                            building = True
                            if self.debug_mode: print(f"    🏠 Built house on {Board.format_colored_name(space_id)}.")
                            break 
                        elif current_houses == 4 and self.hotels > 0:
                            self.hotels -= 1; self.houses += 4
                            player.change_cash(-house_cost)
                            player.buildings[space_id] = 5
                            building = True
                            if self.debug_mode: print(f"    🏨 Built HOTEL on {Board.format_colored_name(space_id)}.")
                            break 


# ==========================================
# 3. CORE ENGINE ORCHESTRATOR
# ==========================================
class MonopolySimulation:
    """Manages the game loop, dice, decks, and coordinates between Bank and UI."""
    def __init__(self, total_games: int = 1_000, steps_per_game: int = 100, debug_mode: bool = False):
        self.debug_mode = debug_mode
        self.total_games = 1 if debug_mode else total_games
        self.steps_per_game = steps_per_game
        
        self.renderer = GameRenderer(self.debug_mode)
        self.bank = CentralBank(self.debug_mode)
        self.dice = Dice()
        self.players = [Player("P1"), Player("P2"), Player("P3"), Player("P4")]
        
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

    # --- TURN LOGIC ROUTINES ---
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

    # --- ACTION HELPERS ---
    def _handle_jail_state(self, player: Player) -> int:
        """Returns the dice total if they roll out, or 0 if they use a card/pay out."""
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
            
        # Forced Payout on 3rd Turn
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
            if player.cash >= (cost + 100):
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