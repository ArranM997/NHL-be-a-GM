import random
from player_class import Player
from team_class import Team
from utils import suffex
from globalvars import PROSPECT_POOL
from utils import pot_conv

LAST_DRAFT = []


def rgb(r, g, b):
    return f"\033[38;2;{r};{g};{b}m"


def ovr_color(v):
    base = f"{v:>3}"

    if v >= 95:
        return f"{rgb(171, 125, 255)}{base}\033[0m"
    elif v >= 80:
        return f"{rgb(255, 215, 0)}{base}\033[0m"
    elif v >= 74:
        return f"{rgb(150, 123, 0)}{base}\033[0m"
    elif v >= 70:
        return f"{rgb(117, 117, 117)}{base}\033[0m"
    else:
        return f"{rgb(139, 69, 19)}{base}\033[0m"


def format_draft_player(p):
    name = p.full_name[:20]
    return f"{name:<20} | 💪 {ovr_color(p.ovr):<3} | 📈 {pot_conv(p.pot):<9} | Age: {p.age:<3} | 💰 {p.value:<6}"


def get_draft_order(teams):
    return sorted(teams, key=lambda t: (t.points, t.gdiff, t.gf))


def draft(
    teams, user_team_name="Red Wings", rounds=3, auto=False, reversed_order=False
):
    global LAST_DRAFT
    LAST_DRAFT = []

    overall_pick = 1

    player_pool = [Player() for _ in range(len(teams) * rounds)] + [
        p for p in PROSPECT_POOL if p.age >= 18 and p.draft_number == 0
    ]

    for p in player_pool:
        if not hasattr(p, "drafted_by"):
            p.drafted_by = "UNDRAFTED"
    base_order = get_draft_order(teams)
    draft_order = list(reversed(base_order)) if reversed_order else base_order

    if not auto:
        print("Draft order (worst → best):")
        for i, t in enumerate(draft_order):
            print(f"{i+1}. {t.name} - {t.points} pts")
    for rnd in range(rounds):

        if not auto:
            print(f"\n--- Round {rnd + 1} ---")
        for team in draft_order:

            if not player_pool:
                return
            player_pool.sort(key=lambda p: p.pot, reverse=True)

            if team.name == user_team_name and not auto:

                print("\nAvailable players:")
                print("No. | Name                 | OVR    | POT          | Age      | Value")
                print("-" * 76)

                for idx, player in enumerate(player_pool):
                    print(f"{idx+1:<3} | {format_draft_player(player)}")
                while True:
                    choice = input(
                        f"\nRound {rnd + 1} {overall_pick}{suffex(overall_pick)} overall: "
                        f"Select a player for {team.name} [1-{len(player_pool)}]: "
                    )

                    if choice.isdigit():
                        choice = int(choice)
                        if 1 <= choice <= len(player_pool):

                            selected = player_pool.pop(choice - 1)

                            selected.draft_number = overall_pick
                            selected.drafted_by = team.name

                            team.add_player(selected)
                            LAST_DRAFT.append(selected)

                            print(
                                f"You selected: {selected.full_name} "
                                f"({overall_pick}{suffex(overall_pick)})"
                            )

                            overall_pick += 1
                            break
                    print("Invalid choice, try again.")
            else:
                selected = player_pool.pop(0)

                selected.draft_number = overall_pick
                selected.drafted_by = team.name

                team.add_player(selected)
                LAST_DRAFT.append(selected)

                if not auto:
                    print(
                        f"{team.name:<15} drafted {selected.full_name[:20]:<20} | "
                        f"age: {selected.age} | 💪{ovr_color(selected.ovr)} | "
                        f"📈 {pot_conv(selected.pot):<9} "
                        f"({overall_pick}{suffex(overall_pick)})"
                    )
                overall_pick += 1
    if not auto:
        print("\n--- Draft Complete ---")
