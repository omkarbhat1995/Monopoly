from collections import Counter
from dice import Dice
from board import Board
from deck import Deck
from player import Player

class MonopolySimulation:
    """Runs a batch simulation of independent games and aggregates telemetry data."""
    
    def __init__(self, total_games: int = 1_000, steps_per_game: int = 100, debug_mode: bool = False):
        self.debug_mode = debug_mode
        # Force a single game if debugging to prevent terminal flooding
        self.total_games = 1 if debug_mode else total_games
        self.steps_per_game = steps_per_game
        
        self.dice = Dice()
        self.players = [
            Player("Player 1"), Player("Player 2"), 
            Player("Player 3"), Player("Player 4")
        ]
        
        self.chance_deck = Deck("chance")
        self.com_chest_deck = Deck("community_chest")
        
        # Global exclusive title registry: space_id -> Player object
        self.property_owners = {}
        
        self.visited_tracking = Counter({space: 0 for space in range(1, Board.SIZE + 1)})
        self.total_positions_logged = 0
        self.total_bankruptcies = 0
        self.average_ending_cash = {p.name: 0 for p in self.players}

    def calculate_rent(self, space_id: int, owner: Player, dice_total: int) -> int:
        """Computes true rent based on exclusive ownership, monopolies, and houses."""
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
        """Resolves exclusive purchases or processes rental transfer to landlord."""
        info = Board.get_space_info(space_id)
        cost = info[2]
        
        if cost == 0 or player.is_bankrupt:
            return  

        # Case A: Property is Unowned
        if space_id not in self.property_owners:
            if player.cash >= cost:
                player.change_cash(-cost)
                player.owned_properties.add(space_id)
                self.property_owners[space_id] = player
                if self.debug_mode:
                    print(f"    💰 {player.name} bought {Board.format_colored_name(space_id)} for ${cost}. Balance: ${player.cash}")
            elif self.debug_mode:
                print(f"    X {player.name} cannot afford {Board.format_colored_name(space_id)} (Costs ${cost}, has ${player.cash})")
                
        # Case B: Property is Owned by an Opponent
        elif self.property_owners[space_id] != player:
            owner = self.property_owners[space_id]
            if not owner.is_bankrupt:
                rent = self.calculate_rent(space_id, owner, dice_total)
                player.change_cash(-rent)
                owner.change_cash(rent)
                if self.debug_mode:
                    houses = owner.buildings.get(space_id, 0)
                    house_text = f" ({houses} houses)" if houses > 0 else ""
                    print(f"    💸 Rent! {player.name} paid ${rent} to {owner.name} for {Board.format_colored_name(space_id)}{house_text}.")
                
                if player.is_bankrupt and self.debug_mode:
                    print(f"    💀 {player.name} went BANKRUPT paying rent to {owner.name}!")

    def handle_house_building(self, player: Player) -> None:
        """Adds real-estate developments if player holds an exclusive monopoly."""
        if player.is_bankrupt:
            return

        for space_id in list(player.owned_properties):
            info = Board.get_space_info(space_id)
            group, house_cost = info[1], info[3]
            
            if group in Board.COLOR_COUNTS:
                num_owned = player.count_owned_in_group(group, Board.SPACE_REGISTRY)
                if num_owned == Board.COLOR_COUNTS[group]:
                    current_houses = player.buildings.get(space_id, 0)
                    if current_houses < 5 and player.cash > (house_cost + 150): 
                        player.change_cash(-house_cost)
                        player.buildings[space_id] = current_houses + 1
                        if self.debug_mode:
                            type_built = "a HOTEL" if current_houses + 1 == 5 else f"house #{current_houses + 1}"
                            print(f"    🏠 {player.name} built {type_built} on {Board.format_colored_name(space_id)} for ${house_cost}.")

    def run(self) -> None:
        """Executes the complete turn-based batch game environment loop sequentially."""
        if self.debug_mode:
            print("\n" + "═"*30 + " DEBUG MODE ACTIVATED (1 GAME) " + "═"*30 + "\n")

        for game_idx in range(self.total_games):
            self.property_owners.clear()
            for p in self.players:
                p.reset_for_new_game()
            self.dice.reset_doubles()

            for step in range(1, self.steps_per_game + 1):
                active_players = [p for p in self.players if not p.is_bankrupt]
                if len(active_players) <= 1:
                    if self.debug_mode:
                        winner = active_players[0].name if active_players else "Nobody"
                        print(f"\n🏆 Game ended on Step {step}! Winner: {winner}")
                    break 

                if self.debug_mode:
                    print(f"🏁 --- Round Step {step} ---")

                for player in active_players:
                    if player.is_bankrupt:
                        continue
                    
                    # Track where the player started their turn for accurate Pass-GO calculation
                    old_position = player.position
                    
                    # --- CORE JAIL TURN BRANCH ENGINE ---
                    if player.is_in_jail:
                        player.turns_in_jail += 1
                        dice_total, is_double = self.dice.roll()
                        
                        if self.debug_mode:
                            print(f"🔒 {player.name} is in JAIL (Turn {player.turns_in_jail}/3). Rolled {dice_total} {'(DOUBLES!)' if is_double else ''}")
                        
                        if is_double:
                            player.is_in_jail = False
                            player.turns_in_jail = 0
                            self.dice.reset_doubles()  # Doubles out of jail does not grant an extra turn
                            if self.debug_mode:
                                print(f"    🔓 Freedom! Rolled doubles to escape jail for free.")
                        else:
                            if player.turns_in_jail < 3:
                                if self.debug_mode:
                                    print(f"    ❌ Failed to roll doubles. Must remain in Jail.")
                                self.visited_tracking[player.position] += 1
                                self.total_positions_logged += 1
                                continue  # Turn ends stuck in cell
                            else:
                                player.is_in_jail = False
                                player.turns_in_jail = 0
                                player.change_cash(-50)
                                if self.debug_mode:
                                    print(f"    💸 3rd Turn Failure! Forced to pay $50 fine to leave Jail. Balance: ${player.cash}")
                                
                                if player.is_bankrupt:
                                    if self.debug_mode:
                                        print(f"    💀 {player.name} went BANKRUPT paying the Jail posting fee!")
                                    self.visited_tracking[player.position] += 1
                                    self.total_positions_logged += 1
                                    continue
                                    
                        new_position = Board.wrap_position(player.position + dice_total)
                    else:
                        # Standard Roll Dice Action for free players
                        dice_total, is_double = self.dice.roll()
                        db_text = f" (DOUBLE #{self.dice.consecutive_doubles}!)" if is_double else ""
                        
                        if self.debug_mode:
                            print(f"🎲 {player.name} rolled {dice_total}{db_text}")

                        if self.dice.consecutive_doubles == 3:
                            player.position = Board.JAIL
                            player.is_in_jail = True
                            player.turns_in_jail = 0
                            self.dice.reset_doubles()
                            self.visited_tracking[player.position] += 1
                            self.total_positions_logged += 1
                            if self.debug_mode:
                                print(f"    ❌ SPEEDING TICKET! 3 doubles in a row. Sent straight to Jail.")
                            continue

                        new_position = Board.wrap_position(player.position + dice_total)

                    # --- INTERCEPT SPECIAL SPACES, TAXES, & CARDS ---
                    if new_position == Board.GO_TO_JAIL:
                        new_position = Board.JAIL
                        player.is_in_jail = True
                        player.turns_in_jail = 0
                        self.dice.reset_doubles()
                        if self.debug_mode:
                            print(f"    👮 Landed on Go To Jail! Arrested and moved to Jail cell.")
                            
                    elif new_position == Board.INCOME_TAX:
                        player.change_cash(-200)
                        if self.debug_mode:
                            print(f"    💸 Paid Income Tax (-$200). Balance: ${player.cash}")
                        if player.is_bankrupt and self.debug_mode:
                            print(f"    💀 {player.name} went BANKRUPT from Income Tax!")
                            
                    elif new_position == Board.LUXURY_TAX:
                        player.change_cash(-100)
                        if self.debug_mode:
                            print(f"    💸 Paid Luxury Tax (-$100). Balance: ${player.cash}")
                        if player.is_bankrupt and self.debug_mode:
                            print(f"    💀 {player.name} went BANKRUPT from Luxury Tax!")
                    
                    elif new_position in Board.CHANCE_SPACES or new_position in Board.COMMUNITY_CHEST_SPACES:
                        self.visited_tracking[new_position] += 1
                        self.total_positions_logged += 1
                        
                        if new_position in Board.CHANCE_SPACES:
                            card = self.chance_deck.draw_card()
                            if self.debug_mode:
                                print(f"    ❓ Drew Chance Card: {card}")
                            new_position, forced_jail = self.chance_deck.resolve_card_movement(card, new_position)
                        else:
                            card = self.com_chest_deck.draw_card()
                            if self.debug_mode:
                                print(f"    📦 Drew Community Chest Card: {card}")
                            new_position, forced_jail = self.com_chest_deck.resolve_card_movement(card, new_position)
                        
                        if forced_jail:
                            player.is_in_jail = True
                            player.turns_in_jail = 0
                            self.dice.reset_doubles()

                        if card == "GO_BACK_3_SPACES" and new_position == 33:
                            self.visited_tracking[new_position] += 1
                            self.total_positions_logged += 1
                            cc_card = self.com_chest_deck.draw_card()
                            if self.debug_mode:
                                print(f"    💥 Chain Reaction! Moved back into Community Chest space and drew: {cc_card}")
                            new_position, forced_jail = self.com_chest_deck.resolve_card_movement(cc_card, new_position)
                            if forced_jail:
                                player.is_in_jail = True
                                player.turns_in_jail = 0
                                self.dice.reset_doubles()

                    # --- FINAL RESOLUTION & TRANSACTION STAGE ---
                    # Check if the player passed GO either physically or via a card jump
                    if new_position < old_position and not player.is_in_jail:
                        player.change_cash(200)
                        if self.debug_mode:
                            print(f"    🏪 Passed GO! Collected $200. Balance: ${player.cash}")

                    # FIX: Process transactions using the newly calculated position before logging it
                    if self.debug_mode:
                        print(f"    📍 Landed on space {new_position}: {Board.format_colored_name(new_position)}")
                    
                    self.handle_property_landing(player, new_position, dice_total)
                    
                    player.position = new_position
                    self.visited_tracking[player.position] += 1
                    self.total_positions_logged += 1
                    
                    self.handle_house_building(player)

            for player in self.players:
                if player.is_bankrupt:
                    self.total_bankruptcies += 1
                self.average_ending_cash[player.name] += player.cash

        self._print_summary()

    def _print_summary(self) -> None:
        """Outputs statistical tracking tables."""
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