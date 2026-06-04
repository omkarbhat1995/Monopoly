from collections import Counter
from dice import Dice
from board import Board
from deck import Deck
from player import Player

class MonopolySimulation:
    def __init__(self, total_games: int = 1_000, steps_per_game: int = 100):
        self.total_games = total_games
        self.steps_per_game = steps_per_game
        self.dice = Dice()
        
        # Instantiate 4 distinct players
        self.players = [
            Player("Player 1"), Player("Player 2"), 
            Player("Player 3"), Player("Player 4")
        ]
        
        self.chance_deck = Deck("chance")
        self.com_chest_deck = Deck("community_chest")
        
        # Global Registry Map: space_id -> Player object who holds exclusive title deed
        self.property_owners = {}
        
        self.visited_tracking = Counter({space: 0 for space in range(1, Board.SIZE + 1)})
        self.total_positions_logged = 0
        
        # Financial tracking metrics for final reporting
        self.total_bankruptcies = 0
        self.average_ending_cash = {p.name: 0 for p in self.players}

    def calculate_rent(self, space_id: int, owner: Player, dice_total: int) -> int:
        """Computes true rent based on exclusive ownership, monopolies, and houses."""
        info = Board.get_space_info(space_id)
        group, rent_table = info[1], info[4]
        houses = owner.buildings.get(space_id, 0)

        # 1. Railroad Pricing
        if group == "RAILROAD":
            num_owned = owner.count_owned_in_group("RAILROAD", Board.SPACE_REGISTRY)
            return rent_table[min(num_owned - 1, 3)]

        # 2. Utility Pricing
        if group == "UTILITY":
            num_owned = owner.count_owned_in_group("UTILITY", Board.SPACE_REGISTRY)
            multiplier = 10 if num_owned == 2 else 4
            return dice_total * multiplier

        # 3. Developed Property Metrics (Houses / Hotels)
        if houses > 0:
            return rent_table[houses]

        # 4. Monopolized Unimproved Set Multiplier Rule (Double Base Rent)
        num_owned = owner.count_owned_in_group(group, Board.SPACE_REGISTRY)
        if num_owned == Board.COLOR_COUNTS.get(group, 0):
            return rent_table[0] * 2

        return rent_table[0]

    def handle_property_landing(self, player: Player, space_id: int, dice_total: int) -> None:
        """Resolves transactions: buy if unowned, or pay rent to the exclusive owner."""
        info = Board.get_space_info(space_id)
        cost = info[2]
        
        if cost == 0:
            return  # Non-purchasable structural landing frame

        # Case A: Property is Unowned - Attempt exclusive title purchase
        if space_id not in self.property_owners:
            if player.cash >= cost:
                player.change_cash(-cost)
                player.owned_properties.add(space_id)
                self.property_owners[space_id] = player
                
        # Case B: Property is Owned by an Opponent - Process Rent
        elif self.property_owners[space_id] != player:
            owner = self.property_owners[space_id]
            if not owner.is_bankrupt:
                rent = self.calculate_rent(space_id, owner, dice_total)
                player.change_cash(-rent)
                owner.change_cash(rent)

    def handle_house_building(self, player: Player) -> None:
        """Triggers construction checks to add houses/hotels on owned monopolies."""
        for space_id in list(player.owned_properties):
            info = Board.get_space_info(space_id)
            group, house_cost = info[1], info[3]
            
            if group in Board.COLOR_COUNTS:
                num_owned = player.count_owned_in_group(group, Board.SPACE_REGISTRY)
                if num_owned == Board.COLOR_COUNTS[group]:
                    current_houses = player.buildings.get(space_id, 0)
                    # Safe buffer: Build only if player has enough cash leftover
                    if current_houses < 5 and player.cash > (house_cost + 150): 
                        player.change_cash(-house_cost)
                        player.buildings[space_id] = current_houses + 1

    def run(self) -> None:
        """Executes the complete batch simulation loop."""
        for _ in range(self.total_games):
            # Flash game states clean
            self.property_owners.clear()
            for p in self.players:
                p.reset_for_new_game()
            self.dice.reset_doubles()

            # Execute Turn Sequence System
            for step in range(self.steps_per_game):
                active_players = [p for p in self.players if not p.is_bankrupt]
                if len(active_players) <= 1:
                    break # End game early if only one player is left standing

                for player in active_players:
                    if player.is_bankrupt:
                        continue
                    
                    dice_total, is_double = self.dice.roll()

                    if self.dice.consecutive_doubles == 3:
                        player.position = Board.JAIL
                        self.dice.reset_doubles()
                        self.visited_tracking[player.position] += 1
                        self.total_positions_logged += 1
                        continue

                    raw_new_pos = player.position + dice_total
                    
                    # Capital Flow: Collect $200 for passing GO
                    if raw_new_pos > Board.SIZE:
                        player.change_cash(200) 
                        
                    new_position = Board.wrap_position(raw_new_pos)

                    # Capital Flow: Intercept structural tax nodes
                    if new_position == Board.GO_TO_JAIL:
                        new_position = Board.JAIL
                    elif new_position == Board.INCOME_TAX:
                        player.change_cash(-200)
                    elif new_position == Board.LUXURY_TAX:
                        player.change_cash(-100)
                    
                    # Intercept Card Deck anchors
                    elif new_position in Board.CHANCE_SPACES or new_position in Board.COMMUNITY_CHEST_SPACES:
                        self.visited_tracking[new_position] += 1
                        self.total_positions_logged += 1
                        
                        if new_position in Board.CHANCE_SPACES:
                            card = self.chance_deck.draw_card()
                            new_position, forced_jail = self.chance_deck.resolve_card_movement(card, new_position)
                        else:
                            card = self.com_chest_deck.draw_card()
                            new_position, forced_jail = self.com_chest_deck.resolve_card_movement(card, new_position)
                        
                        if card == "GO_BACK_3_SPACES" and new_position == 33:
                            self.visited_tracking[new_position] += 1
                            self.total_positions_logged += 1
                            cc_card = self.com_chest_deck.draw_card()
                            new_position, forced_jail = self.com_chest_deck.resolve_card_movement(cc_card, new_position)

                        if forced_jail:
                            self.dice.reset_doubles()

                    # Process economic spatial properties
                    player.position = new_position
                    self.handle_property_landing(player, player.position, dice_total)
                    
                    # Update tracking metrics
                    self.visited_tracking[player.position] += 1
                    self.total_positions_logged += 1
                    
                    # Dynamic construction check
                    self.handle_house_building(player)

            # Record final game financial state metrics
            for player in self.players:
                if player.is_bankrupt:
                    self.total_bankruptcies += 1
                self.average_ending_cash[player.name] += player.cash

        self._print_summary()

    def _print_summary(self) -> None:
        """Outputs statistical analytics, heatmaps, and financial metrics."""
        print(f"\n" + "="*25 + f" SIMULATION COMPLETE ({self.total_games:,} GAMES) " + "="*25)
        
        # Financial Summary Report Table
        print("\n--- FINANCIAL SUMMARY ---")
        print(f"{'Player Name':<15} | {'Avg Ending Cash':<18} | {'Status'}")
        print("-" * 45)
        for name, total_cash in self.average_ending_cash.items():
            avg_cash = total_cash / self.total_games
            print(f"{name:<15} | ${avg_cash:<17.2f} | Running Smoothly")
        print(f"\nTotal Bankruptcies Triggered Across Simulation: {self.total_bankruptcies:,}")
        
        # Spatial Heatmap Report Table
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