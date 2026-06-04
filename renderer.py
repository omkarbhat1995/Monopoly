import time
from collections import Counter
from typing import List, TYPE_CHECKING
from board import Board
from player import Player

# Prevents circular imports while allowing type hinting
if TYPE_CHECKING:
    from bank import CentralBank

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