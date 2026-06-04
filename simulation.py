import time
from collections import Counter
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
        self.players = [
            Player("P1"), Player("P2"), Player("P3"), Player("P4")
        ]
        
        self.chance_deck = Deck("chance")
        self.com_chest_deck = Deck("community_chest")
        self.property_owners = {}
        
        self.visited_tracking = Counter({space: 0 for space in range(1, Board.SIZE + 1)})
        self.total_positions_logged = 0
        self.total_bankruptcies = 0
        self.average_ending_cash = {p.name: 0 for p in self.players}

    def render_visual_board(self) -> None:
        print("\n" + "═"*35 + " LIVE BOARD MAP " + "═"*35)
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
        """Sells houses and mortgages properties to avoid bankruptcy when cash < $0."""
        if player.cash >= 0:
            return
            
        # Step 1: Sell houses back to the bank for half price
        for space_id in list(player.buildings.keys()):
            if player.cash >= 0: break
            info = Board.get_space_info(space_id)
            house_sell_price = info[3] // 2
            
            while player.buildings[space_id] > 0 and player.cash < 0:
                player.buildings[space_id] -= 1
                player.change_cash(house_sell_price)
                if self.debug_mode:
                    print(f"    📉 {player.name} sold a house on {Board.format_colored_name(space_id)} for ${house_sell_price}.")
            
            if player.buildings[space_id] == 0:
                del player.buildings[space_id]

        # Step 2: Mortgage unimproved properties for half their buy price
        if player.cash < 0:
            unmortgaged = player.owned_properties - player.mortgaged_properties
            for space_id in list(unmortgaged):
                if player.cash >= 0: break
                info = Board.get_space_info(space_id)
                mortgage_value = info[2] // 2
                
                player.mortgaged_properties.add(space_id)
                player.change_cash(mortgage_value)
                if self.debug_mode:
                    print(f"    🏦 {player.name} mortgaged {Board.format_colored_name(space_id)} for ${mortgage_value}.")

        # Step 3: Final Bankruptcy Verdict
        if player.cash < 0:
            player.is_bankrupt = True
            if self.debug_mode:
                print(f"    💀 {player.name} could not raise funds and went BANKRUPT!")
                
    def handle_unmortgage(self, player: Player) -> None:
        """Uses excess cash to pay off mortgages + 10% interest."""
        if player.is_bankrupt or not player.mortgaged_properties:
            return
            
        for space_id in list(player.mortgaged_properties):
            info = Board.get_space_info(space_id)
            unmortgage_cost = int((info[2] // 2) * 1.1)
            
            # Unmortgage only if they retain a safe $300 cash buffer
            if player.cash > (unmortgage_cost + 300):
                player.change_cash(-unmortgage_cost)
                player.mortgaged_properties.remove(space_id)
                if self.debug_mode:
                    print(f"    📈 {player.name} paid ${unmortgage_cost} to unmortgage {Board.format_colored_name(space_id)}.")

    def calculate_rent(self, space_id: int, owner: Player, dice_total: int) -> int:
        if space_id in owner.mortgaged_properties:
            return 0  # 🚨 RULE: No rent can be collected on mortgaged land

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
        if houses > 0:
            return rent_table[houses]

        num_owned = owner.count_owned_in_group(group, Board.SPACE_REGISTRY)
        if num_owned == Board.COLOR_COUNTS.get(group, 0):
            return rent_table[0] * 2
        return rent_table[0]

    def handle_property_landing(self, player: Player, space_id: int, dice_total: int) -> None:
        info = Board.get_space_info(space_id)
        cost = info[2]
        if cost == 0 or player.is_bankrupt: return  

        if space_id not in self.property_owners:
            if player.cash >= cost:
                player.change_cash(-cost)
                player.owned_properties.add(space_id)
                self.property_owners[space_id] = player
                if self.debug_mode:
                    print(f"    💰 {player.name} bought {Board.format_colored_name(space_id)} for ${cost}. Balance: ${player.cash}")
                
        elif self.property_owners[space_id] != player:
            owner = self.property_owners[space_id]
            if not owner.is_bankrupt:
                rent = self.calculate_rent(space_id, owner, dice_total)
                if rent > 0:
                    player.change_cash(-rent)
                    owner.change_cash(rent)
                    if self.debug_mode:
                        houses = owner.buildings.get(space_id, 0)
                        house_text = f" ({houses} houses)" if houses > 0 else ""
                        print(f"    💸 Rent! {player.name} paid ${rent} to {owner.name} for {Board.format_colored_name(space_id)}{house_text}.")
                    
                    if player.cash < 0:
                        self.handle_liquidation(player) # Liquidate if rent puts them in debt

    def handle_house_building(self, player: Player) -> None:
        if player.is_bankrupt: return
        for space_id in list(player.owned_properties):
            info = Board.get_space_info(space_id)
            group, house_cost = info[1], info[3]
            if group in Board.COLOR_COUNTS:
                num_owned = player.count_owned_in_group(group, Board.SPACE_REGISTRY)
                # 🚨 RULE: You cannot build if any property in this color group is mortgaged
                if num_owned == Board.COLOR_COUNTS[group] and not player.has_mortgaged_in_group(group, Board.SPACE_REGISTRY):
                    current_houses = player.buildings.get(space_id, 0)
                    if current_houses < 5 and player.cash > (house_cost + 150): 
                        player.change_cash(-house_cost)
                        player.buildings[space_id] = current_houses + 1
                        if self.debug_mode:
                            type_built = "a HOTEL" if current_houses + 1 == 5 else f"house #{current_houses + 1}"
                            print(f"    🏠 {player.name} built {type_built} on {Board.format_colored_name(space_id)} for ${house_cost}.")

    def run(self) -> None:
        if self.debug_mode:
            print("\n" + "═"*30 + " DEBUG ENGINE RUN " + "═"*30 + "\n")

        for game_idx in range(self.total_games):
            self.property_owners.clear()
            for p in self.players: p.reset_for_new_game()
            self.dice.reset_doubles()

            for step in range(1, self.steps_per_game + 1):
                active_players = [p for p in self.players if not p.is_bankrupt]
                if len(active_players) <= 1: break 

                if self.debug_mode:
                    print(f"🏁 --- Round Step {step} ---")

                for player in active_players:
                    if player.is_bankrupt: continue
                    
                    dice_total = 0
                    old_position = player.position
                    
                    if player.is_in_jail:
                        if player.goojf_cards > 0:
                            player.goojf_cards -= 1
                            player.is_in_jail = False
                            player.turns_in_jail = 0
                            self.chance_deck.return_goojf_card() 
                            if self.debug_mode:
                                print(f"    🔓 Card Freedom! {player.name} used a 'Get Out of Jail Free' card to walk out.")
                        else:
                            player.turns_in_jail += 1
                            dice_total, is_double = self.dice.roll()
                            if self.debug_mode:
                                print(f"🔒 {player.name} is in JAIL (Turn {player.turns_in_jail}/3). Rolled {dice_total} {'(DOUBLES!)' if is_double else ''}")
                            
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
                                    if self.debug_mode:
                                        print(f"    💸 Forced $50 Fee! Left prison. Balance: ${player.cash}")
                                    if player.cash < 0:
                                        self.handle_liquidation(player) # Check liquidation on jail fine
                                    if player.is_bankrupt:
                                        self.visited_tracking[player.position] += 1
                                        self.total_positions_logged += 1
                                        continue
                                        
                        new_position = Board.wrap_position(player.position + dice_total)
                    else:
                        dice_total, is_double = self.dice.roll()
                        db_text = f" (DOUBLE #{self.dice.consecutive_doubles}!)" if is_double else ""
                        if self.debug_mode: print(f"🎲 {player.name} rolled {dice_total}{db_text}")

                        if self.dice.consecutive_doubles == 3:
                            player.position = Board.JAIL
                            player.is_in_jail = True
                            player.turns_in_jail = 0
                            self.dice.reset_doubles()
                            self.visited_tracking[player.position] += 1
                            self.total_positions_logged += 1
                            if self.debug_mode: print(f"    ❌ SPEEDING TICKET! Sent straight to Jail.")
                            continue

                        new_position = Board.wrap_position(player.position + dice_total)

                    # --- SPACE PENALTIES & CARDS ---
                    if new_position == Board.GO_TO_JAIL:
                        new_position = Board.JAIL
                        player.is_in_jail = True
                        player.turns_in_jail = 0
                        self.dice.reset_doubles()
                        if self.debug_mode: print(f"    👮 Landed on Go To Jail! Sent to Jail cell.")
                            
                    elif new_position == Board.INCOME_TAX:
                        player.change_cash(-200)
                        if self.debug_mode: print(f"    💸 Paid Income Tax (-$200).")
                        if player.cash < 0: self.handle_liquidation(player)
                            
                    elif new_position == Board.LUXURY_TAX:
                        player.change_cash(-100)
                        if self.debug_mode: print(f"    💸 Paid Luxury Tax (-$100).")
                        if player.cash < 0: self.handle_liquidation(player)
                    
                    elif new_position in Board.CHANCE_SPACES or new_position in Board.COMMUNITY_CHEST_SPACES:
                        self.visited_tracking[new_position] += 1
                        self.total_positions_logged += 1
                        
                        if new_position in Board.CHANCE_SPACES:
                            card = self.chance_deck.draw_card()
                            if self.debug_mode: print(f"    ❓ drew Chance: {card}")
                            new_position, forced_jail, holds_card = self.chance_deck.resolve_card_movement(card, new_position)
                        else:
                            card = self.com_chest_deck.draw_card()
                            if self.debug_mode: print(f"    📦 drew Chest: {card}")
                            new_position, forced_jail, holds_card = self.com_chest_deck.resolve_card_movement(card, new_position)
                        
                        if holds_card:
                            player.goojf_cards += 1
                            if self.debug_mode: print(f"    🎫 Secured Card Asset! {player.name} is holding a backup escape card.")
                        if forced_jail:
                            player.is_in_jail = True
                            player.turns_in_jail = 0
                            self.dice.reset_doubles()

                        if card == "GO_BACK_3_SPACES" and new_position == 33:
                            self.visited_tracking[new_position] += 1
                            self.total_positions_logged += 1
                            cc_card = self.com_chest_deck.draw_card()
                            if self.debug_mode: print(f"    💥 Chain Reaction! Moved back into Chest space and drew: {cc_card}")
                            new_position, forced_jail, holds_card = self.com_chest_deck.resolve_card_movement(cc_card, new_position)
                            if holds_card: player.goojf_cards += 1
                            if forced_jail:
                                player.is_in_jail = True
                                player.turns_in_jail = 0
                                self.dice.reset_doubles()

                    # --- RESOLUTIONS ---
                    if new_position < old_position and not player.is_in_jail:
                        player.change_cash(200)
                        if self.debug_mode: print(f"    🏪 Passed GO! Collected $200.")

                    if self.debug_mode and not player.is_bankrupt:
                        print(f"    📍 Landed on space {new_position}: {Board.format_colored_name(new_position)}")
                    
                    self.handle_property_landing(player, new_position, dice_total)
                    player.position = new_position
                    self.visited_tracking[player.position] += 1
                    self.total_positions_logged += 1
                    
                    # Process End of Turn Capital Improvements
                    self.handle_unmortgage(player)
                    self.handle_house_building(player)

                if self.debug_mode:
                    self.render_visual_board()

            for player in self.players:
                if player.is_bankrupt: self.total_bankruptcies += 1
                self.average_ending_cash[player.name] += player.cash

        self._print_summary()

    def _print_summary(self) -> None:
        print(f"\n" + "═"*25 + f" SIMULATION SUMMARY " + "═"*25)
        print("\n--- FINANCIAL STATUS ---")
        print(f"{'Player Name':<15} | {'Ending/Avg Cash':<18} | {'Status'}")
        print("-" * 45)
        for name, total_cash in self.average_ending_cash.items():
            avg_cash = total_cash / self.total_games
            status = "Bankrupt" if avg_cash <= 0 else "Active"
            print(f"{name:<15} | ${avg_cash:<17.2f} | {status}")
            
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