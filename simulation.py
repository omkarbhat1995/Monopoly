import time
from collections import Counter
from typing import Optional
from dice import Dice
from board import Board
from deck import Deck
from player import Player

class MonopolySimulation:
    def __init__(self, total_games: int = 1_000, steps_per_game: int = 100, debug_mode: bool = False):
        self.debug_mode = debug_mode
        self.total_games = 1 if debug_mode else total_games
        self.steps_per_game = steps_per_game
        
        self.dice = Dice()
        self.players = [Player("P1"), Player("P2"), Player("P3"), Player("P4")]
        
        self.chance_deck = Deck("chance")
        self.com_chest_deck = Deck("community_chest")
        self.property_owners = {}
        
        self.bank_houses = 32
        self.bank_hotels = 12
        
        self.visited_tracking = Counter({space: 0 for space in range(1, Board.SIZE + 1)})
        self.total_positions_logged = 0
        self.total_bankruptcies = 0
        self.average_ending_cash = {p.name: 0 for p in self.players}

    def render_visual_board(self) -> None:
        print("\n" + "═"*18 + f" LIVE BOARD MAP (Bank: {self.bank_houses}H, {self.bank_hotels} Hotels) " + "═"*18)
        print(f"{'ID':<3} | {'Space Property Name':<35} | {'Ownership/Structure State':<30} | Tokens")
        print("-" * 85)
        for space in range(1, Board.SIZE + 1):
            name, group = Board.get_space_info(space)[:2]
            colored_name = Board.format_colored_name(space)
            
            tokens_on_space = [p.name for p in self.players if p.position == space and not p.is_bankrupt]
            token_str = " ".join(tokens_on_space) if tokens_on_space else ""
            
            struct_str = ""
            if space in self.property_owners:
                owner = self.property_owners[space]
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

    def handle_liquidation(self, player: Player) -> None:
        if player.cash >= 0: return
            
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
                        if self.bank_houses >= 4:
                            self.bank_hotels += 1
                            self.bank_houses -= 4
                            player.buildings[space_id] = 4
                            player.change_cash(house_sell_price)
                        else:
                            self.bank_hotels += 1
                            player.buildings[space_id] = 0
                            player.change_cash(house_sell_price * 5)
                    else: 
                        self.bank_houses += 1
                        player.buildings[space_id] -= 1
                        player.change_cash(house_sell_price)
                        
                    if self.debug_mode: print(f"    📉 {player.name} sold structures on {Board.format_colored_name(space_id)}.")
                    if player.buildings[space_id] == 0: del player.buildings[space_id]
                    sold_this_loop = True
                    break 
            if not sold_this_loop: break 

        if player.cash < 0:
            unmortgaged = player.owned_properties - player.mortgaged_properties
            for space_id in list(unmortgaged):
                if player.cash >= 0: break
                info = Board.get_space_info(space_id)
                mortgage_value = info[2] // 2
                player.mortgaged_properties.add(space_id)
                player.change_cash(mortgage_value)
                if self.debug_mode: print(f"    🏦 {player.name} mortgaged {Board.format_colored_name(space_id)}.")

    def check_bankruptcy(self, player: Player, creditor: Optional[Player] = None, amount_owed: int = 0) -> int:
        if player.cash >= 0: return amount_owed
        self.handle_liquidation(player)
        if player.cash >= 0: return amount_owed 
            
        actual_paid = amount_owed + player.cash 
        player.cash = 0
        player.is_bankrupt = True
        
        if creditor:
            for space_id in list(player.owned_properties):
                self.property_owners[space_id] = creditor
                creditor.owned_properties.add(space_id)
                if space_id in player.mortgaged_properties:
                    creditor.mortgaged_properties.add(space_id)
            creditor.goojf_cards += player.goojf_cards
            if self.debug_mode: print(f"    💀 {player.name} BANKRUPT! Assets seized by {creditor.name}.")
        else:
            for space_id in list(player.owned_properties): del self.property_owners[space_id]
            for _ in range(player.goojf_cards): self.chance_deck.return_goojf_card()
            if self.debug_mode: print(f"    💀 {player.name} BANKRUPT to the Bank! Properties released.")
        return actual_paid

    def handle_unmortgage(self, player: Player) -> None:
        if player.is_bankrupt or not player.mortgaged_properties: return
        for space_id in list(player.mortgaged_properties):
            info = Board.get_space_info(space_id)
            unmortgage_cost = int((info[2] // 2) * 1.1)
            if player.cash > (unmortgage_cost + 300):
                player.change_cash(-unmortgage_cost)
                player.mortgaged_properties.remove(space_id)
                if self.debug_mode: print(f"    📈 {player.name} unmortgaged {Board.format_colored_name(space_id)}.")

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
            multiplier = 10 if num_owned == 2 else 4
            return dice_total * multiplier
        if houses > 0: return rent_table[houses]

        num_owned = owner.count_owned_in_group(group, Board.SPACE_REGISTRY)
        if num_owned == Board.COLOR_COUNTS.get(group, 0): return rent_table[0] * 2
        return rent_table[0]

    def execute_auction(self, space_id: int) -> None:
        bidders = [p for p in self.players if not p.is_bankrupt]
        if not bidders: return

        info = Board.get_space_info(space_id)
        base_price, group = info[2], info[1]
        max_bids = {}

        for p in bidders:
            valuation = base_price
            num_owned = p.count_owned_in_group(group, Board.SPACE_REGISTRY)
            if group in Board.COLOR_COUNTS and num_owned == Board.COLOR_COUNTS[group] - 1:
                valuation = base_price * 2
            max_bid = min(valuation, p.cash - 10)
            max_bids[p] = max(0, max_bid)

        sorted_bidders = sorted(max_bids.items(), key=lambda x: x[1], reverse=True)
        winner, highest_bid = sorted_bidders[0]

        if highest_bid <= 0:
            if self.debug_mode: print(f"    🚫 Auction passed on {Board.format_colored_name(space_id)}.")
            return

        second_highest_bid = sorted_bidders[1][1] if len(sorted_bidders) > 1 else 0
        winning_price = max(10, second_highest_bid + 1)
        winning_price = min(winning_price, highest_bid)

        winner.change_cash(-winning_price)
        winner.owned_properties.add(space_id)
        self.property_owners[space_id] = winner
        if self.debug_mode:
            print(f"    🔨 AUCTION WON! {winner.name} sniped {Board.format_colored_name(space_id)} for ${winning_price}.")

    def handle_property_landing(self, player: Player, space_id: int, dice_total: int) -> None:
        info = Board.get_space_info(space_id)
        cost = info[2]
        if cost == 0 or player.is_bankrupt: return  

        if space_id not in self.property_owners:
            if player.cash >= (cost + 100):
                player.change_cash(-cost)
                player.owned_properties.add(space_id)
                self.property_owners[space_id] = player
                if self.debug_mode: print(f"    💰 {player.name} bought {Board.format_colored_name(space_id)}.")
            else:
                if self.debug_mode: print(f"    ⚖️ {player.name} declined {Board.format_colored_name(space_id)}. AUCTION!")
                self.execute_auction(space_id)
                
        elif self.property_owners[space_id] != player:
            owner = self.property_owners[space_id]
            if not owner.is_bankrupt:
                rent = self.calculate_rent(space_id, owner, dice_total)
                if rent > 0:
                    player.change_cash(-rent)
                    actual_paid = self.check_bankruptcy(player, creditor=owner, amount_owed=rent)
                    owner.change_cash(actual_paid)
                    if self.debug_mode and not player.is_bankrupt:
                        print(f"    💸 Rent! {player.name} paid ${actual_paid} to {owner.name} for {Board.format_colored_name(space_id)}.")

    def handle_house_building(self, player: Player) -> None:
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
                    
                    if current_houses == min_houses and current_houses < 5:
                        if player.cash > (house_cost + 150): 
                            if current_houses < 4 and self.bank_houses > 0:
                                self.bank_houses -= 1
                                player.change_cash(-house_cost)
                                player.buildings[space_id] = current_houses + 1
                                building = True
                                if self.debug_mode: print(f"    🏠 Built house on {Board.format_colored_name(space_id)}.")
                                break 
                            elif current_houses == 4 and self.bank_hotels > 0:
                                self.bank_hotels -= 1
                                self.bank_houses += 4
                                player.change_cash(-house_cost)
                                player.buildings[space_id] = 5
                                building = True
                                if self.debug_mode: print(f"    🏨 Built HOTEL on {Board.format_colored_name(space_id)}.")
                                break 

    def handle_card_finance(self, player: Player, card: str, active_players: list) -> None:
        if card.startswith("PAY_") and not card.endswith("_EACH"):
            amt = int(card.split("_")[1])
            player.change_cash(-amt)
            self.check_bankruptcy(player)
            if self.debug_mode and not player.is_bankrupt: print(f"    💳 Paid Card Fine: ${amt}")
        elif card.startswith("COLLECT_") and not card.endswith("_EACH"):
            amt = int(card.split("_")[1])
            player.change_cash(amt)
            if self.debug_mode: print(f"    🤑 Collected Card Reward: ${amt}")
        elif card == "PAY_50_EACH":
            for p in active_players:
                if p != player and not p.is_bankrupt:
                    p.change_cash(50)
                    player.change_cash(-50)
            self.check_bankruptcy(player)
        elif card == "COLLECT_50_EACH":
            for p in active_players:
                if p != player and not p.is_bankrupt:
                    p.change_cash(-50)
                    actual_paid = self.check_bankruptcy(p, creditor=player, amount_owed=50)
                    player.change_cash(actual_paid)
        elif card.startswith("REPAIRS_"):
            h_cost, H_cost = int(card.split("_")[1]), int(card.split("_")[2])
            total = sum(H_cost if h == 5 else h * h_cost for h in player.buildings.values())
            if total > 0:
                player.change_cash(-total)
                self.check_bankruptcy(player)
                if self.debug_mode and not player.is_bankrupt: print(f"    🛠️ Paid ${total} in property repairs.")

    def run(self) -> None:
        if self.debug_mode: print("\n" + "═"*30 + " DEBUG ENGINE RUN " + "═"*30 + "\n")

        for game_idx in range(self.total_games):
            self.property_owners.clear()
            self.bank_houses, self.bank_hotels = 32, 12
            for p in self.players: p.reset_for_new_game()
            self.dice.reset_doubles()

            for step in range(1, self.steps_per_game + 1):
                active_players = [p for p in self.players if not p.is_bankrupt]
                if len(active_players) <= 1: break 
                if self.debug_mode: print(f"🏁 --- Round Step {step} ---")

                for player in active_players:
                    if player.is_bankrupt: continue
                    dice_total, old_position = 0, player.position
                    
                    if player.is_in_jail:
                        if player.goojf_cards > 0:
                            player.goojf_cards -= 1
                            player.is_in_jail = False
                            player.turns_in_jail = 0
                            self.chance_deck.return_goojf_card() 
                            if self.debug_mode: print(f"    🔓 {player.name} used a GOOJF card.")
                        else:
                            player.turns_in_jail += 1
                            dice_total, is_double = self.dice.roll()
                            if self.debug_mode: print(f"🔒 {player.name} in JAIL (Turn {player.turns_in_jail}/3). Rolled {dice_total}")
                            if is_double:
                                player.is_in_jail = False
                                player.turns_in_jail = 0
                                self.dice.reset_doubles()
                            else:
                                if player.turns_in_jail < 3:
                                    self.visited_tracking[player.position] += 1
                                    self.total_positions_logged += 1
                                    continue
                                else:
                                    player.is_in_jail = False
                                    player.turns_in_jail = 0
                                    player.change_cash(-50)
                                    self.check_bankruptcy(player)
                                    if self.debug_mode and not player.is_bankrupt: print(f"    💸 Forced $50 Fee! Left prison.")
                                    if player.is_bankrupt: continue
                        new_position = Board.wrap_position(player.position + dice_total)
                    else:
                        dice_total, is_double = self.dice.roll()
                        if self.debug_mode: print(f"🎲 {player.name} rolled {dice_total} {'(DOUBLES!)' if is_double else ''}")

                        if self.dice.consecutive_doubles == 3:
                            player.position = Board.JAIL
                            player.is_in_jail = True
                            player.turns_in_jail = 0
                            self.dice.reset_doubles()
                            if self.debug_mode: print(f"    ❌ SPEEDING TICKET! Sent straight to Jail.")
                            continue
                        new_position = Board.wrap_position(player.position + dice_total)

                    if new_position == Board.GO_TO_JAIL:
                        new_position = Board.JAIL
                        player.is_in_jail = True
                        player.turns_in_jail = 0
                        self.dice.reset_doubles()
                        if self.debug_mode: print(f"    👮 Arrested!")
                            
                    elif new_position == Board.INCOME_TAX:
                        player.change_cash(-200)
                        self.check_bankruptcy(player)
                        if self.debug_mode and not player.is_bankrupt: print(f"    💸 Paid Income Tax.")
                            
                    elif new_position == Board.LUXURY_TAX:
                        player.change_cash(-100)
                        self.check_bankruptcy(player)
                        if self.debug_mode and not player.is_bankrupt: print(f"    💸 Paid Luxury Tax.")
                    
                    elif new_position in Board.CHANCE_SPACES or new_position in Board.COMMUNITY_CHEST_SPACES:
                        self.visited_tracking[new_position] += 1
                        self.total_positions_logged += 1
                        
                        if new_position in Board.CHANCE_SPACES:
                            card = self.chance_deck.draw_card()
                            if self.debug_mode: print(f"    ❓ Chance: {card}")
                            new_position, forced_jail, holds_card = self.chance_deck.resolve_card_movement(card, new_position)
                        else:
                            card = self.com_chest_deck.draw_card()
                            if self.debug_mode: print(f"    📦 Chest: {card}")
                            new_position, forced_jail, holds_card = self.com_chest_deck.resolve_card_movement(card, new_position)
                        
                        if holds_card:
                            player.goojf_cards += 1
                        elif "PAY" in card or "COLLECT" in card or "REPAIRS" in card:
                            self.handle_card_finance(player, card, active_players)

                        if forced_jail:
                            player.is_in_jail = True
                            player.turns_in_jail = 0
                            self.dice.reset_doubles()

                    if new_position < old_position and not player.is_in_jail and not player.is_bankrupt:
                        player.change_cash(200)
                        if self.debug_mode: print(f"    🏪 Passed GO! Collected $200.")

                    if self.debug_mode and not player.is_bankrupt:
                        print(f"    📍 Landed on {Board.format_colored_name(new_position)}")
                    
                    if not player.is_bankrupt:
                        self.handle_property_landing(player, new_position, dice_total)
                        
                    if not player.is_bankrupt:
                        player.position = new_position
                        self.visited_tracking[player.position] += 1
                        self.total_positions_logged += 1
                        self.handle_unmortgage(player)
                        self.handle_house_building(player)

                if self.debug_mode: self.render_visual_board()

            for player in self.players:
                if player.is_bankrupt: self.total_bankruptcies += 1
                self.average_ending_cash[player.name] += player.cash

        self._print_summary()

    def _print_summary(self) -> None:
        print(f"\n" + "═"*25 + f" SIMULATION SUMMARY " + "═"*25)
        
        # 🚨 NEW: Branch output based on the type of run (Single vs Mass Simulation)
        if self.total_games == 1:
            print("\n--- FINAL GAME STATE & ASSET PORTFOLIO ---")
            for player in self.players:
                status = "Bankrupt" if player.is_bankrupt else "Active"
                print(f"\n👤 {player.name} | Cash: ${player.cash} | Status: {status}")
                
                if player.owned_properties:
                    print(f"   Owned Properties ({len(player.owned_properties)}):")
                    # Sort properties physically by Board ID for a clean list
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
                                
                        # Pad the colored name so the house labels align perfectly
                        ansi_padding = 45 if group in ["BROWN", "ORANGE", "RAILROAD", "UTILITY"] else 35
                        print(f"      - {colored_name:<{ansi_padding}} {build_status}")
                else:
                    print("   Owned Properties: None")
            print("\n" + "-" * 70)
        else:
            # Multi-game average logic
            print("\n--- FINANCIAL STATUS (AVERAGES) ---")
            print(f"{'Player Name':<15} | {'Avg Ending Cash':<18} | {'Status'}")
            print("-" * 45)
            for name, total_cash in self.average_ending_cash.items():
                avg_cash = total_cash / self.total_games
                status = "Bankrupt" if avg_cash <= 0 else "Active"
                print(f"{name:<15} | ${avg_cash:<17.2f} | {status}")
            print(f"\nTotal Bankruptcies Triggered Across Simulation: {self.total_bankruptcies:,}")
            
        print("\n--- BOARD HEATMAP (MOST LANDED ON) ---")
        print(f"{'ID':<3} | {'Space Name':<35} | {'Group':<12} | {'Total Visits':<12} | {'Landed %':<10}")
        print("-" * 85)
        
        sorted_visits = sorted(self.visited_tracking.items(), key=lambda item: item[1], reverse=True)
        for space, visits in sorted_visits:
            name, group = Board.get_space_info(space)[:2]
            colored_name = Board.format_colored_name(space)
            percentage = (visits / self.total_positions_logged) * 100
            
            ansi_padding = 45 if group in ["BROWN", "ORANGE", "RAILROAD", "UTILITY"] else 35
            print(f"{space:02d}  | {colored_name:<{ansi_padding}} | {group:<12} | {visits:<12,} | {percentage:.2f}%")