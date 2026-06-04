from typing import Optional, List
from board import Board
from deck import Deck
from player import Player

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
        
        if creditor: 
            for space_id in list(player.owned_properties):
                self.property_owners[space_id] = creditor
                creditor.owned_properties.add(space_id)
                if space_id in player.mortgaged_properties: creditor.mortgaged_properties.add(space_id)
            creditor.goojf_cards += player.goojf_cards
            if self.debug_mode: print(f"    💀 {player.name} BANKRUPT! Assets seized by {creditor.name}.")
        else: 
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
        """Simulates a Vickrey Auction based on dynamic AI strategy profiles."""
        bidders = [p for p in active_players if not p.is_bankrupt]
        if not bidders: return

        base_price, group = Board.SPACE_REGISTRY[space_id][2], Board.SPACE_REGISTRY[space_id][1]
        max_bids = {}

        for p in bidders:
            # 1. Base valuation using the player's unique strategy multiplier
            valuation = int(base_price * p.strategy.auction_base_mult)
            num_owned = p.count_owned_in_group(group, Board.SPACE_REGISTRY)
            
            # 2. Aggressive valuation if it completes a set
            if group in Board.COLOR_COUNTS and num_owned == Board.COLOR_COUNTS[group] - 1:
                valuation = int(base_price * p.strategy.auction_set_mult) 
            
            # 3. Cap bid by available cash minus their unique safety buffer
            max_bids[p] = max(0, min(valuation, p.cash - p.strategy.auction_buffer))

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

    def process_building(self, player: Player) -> None:
        """Builds houses symmetrically referencing the player's risk strategy buffer."""
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
                    
                    # AI Check: Does the player have enough cash past their strategy's buffer?
                    if current_houses == min_houses and current_houses < 5 and player.cash >= (house_cost + player.strategy.build_buffer):
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

    def process_unmortgage(self, player: Player) -> None:
        if player.is_bankrupt or not player.mortgaged_properties: return
        for space_id in list(player.mortgaged_properties):
            unmortgage_cost = int((Board.SPACE_REGISTRY[space_id][2] // 2) * 1.1)
            if player.cash > (unmortgage_cost + 300):
                player.change_cash(-unmortgage_cost)
                player.mortgaged_properties.remove(space_id)
                if self.debug_mode: print(f"    📈 {player.name} unmortgaged {Board.format_colored_name(space_id)}.")