import player_class
import team_class
import utils
import match
import draft
from itertools import combinations
import colorama
from colorama import Fore, Back, Style
import globalvars
import pickle
from globalvars import PROSPECT_POOL
import json
import sys
import time
import trading
import playoff_logic
import random
from utils import pot_conv

sys.stdout.reconfigure(encoding="utf-8")

dashamount = 268  # playerformatting
playerformat = "Name                   | Age  | OVR | Δ  | POT        | Team         | Val |gs | NHL: G/GP/GPG     | AHL: G/GP/GPG     | EU: G/GP/GPG     | CHL: G/GP/GPG     | SPHL: G/GP/GPG     | FHL: G/GP/GPG     | rec1: G/GP/GPG   | rec2: G/GP/GPG   | Draft  | Drafted By    |sys"


# misc funcs


def safe_avg_pos(x):
    if x[0] is None:
        return float("inf")
    return x[0] if x[0] > 0 else float("inf")


def record_team_positions(league):
    teams = all_leagues[league]

    sorted_teams = sorted(teams, key=lambda x: (x.points, x.gdiff, x.gf), reverse=True)

    for i, t in enumerate(sorted_teams, 1):
        if t.name not in team_history:
            team_history[t.name] = {"positions": [], "gdiffs": []}
        team_history[t.name]["positions"].append(i)
        team_history[t.name]["gdiffs"].append(t.gdiff)


def reset_season_team_stats(team):
    team.wins = 0
    team.losses = 0
    team.points = 0
    team.gf = 0
    team.ga = 0
    team.gdiff = 0
    team.last10 = []


def calculate_league_stats(league):
    assign_lineups_pipeline()
    league = league.lower()

    all_players = []

    if league == "nhl":
        for t in nhl_teams:
            all_players.extend(
                [
                    p
                    for p in t.roster
                    if getattr(p, "current_league", "").lower() == "nhl"
                ]
            )
    elif league == "ahl":
        for t in nhl_teams:
            all_players.extend(
                [
                    p
                    for p in t.roster
                    if getattr(p, "current_league", "").lower() == "ahl"
                ]
            )
    elif league == "eu":
        for t in nhl_teams:
            all_players.extend(
                [
                    p
                    for p in t.roster
                    if getattr(p, "current_league", "").lower() == "eu"
                ]
            )
    elif league == "chl":
        for t in nhl_teams:
            all_players.extend(
                [
                    p
                    for p in t.roster
                    if getattr(p, "current_league", "").lower() == "chl"
                ]
            )
    elif league == "sphl":
        for t in nhl_teams:
            all_players.extend(
                [
                    p
                    for p in t.roster
                    if getattr(p, "current_league", "").lower() == "sphl"
                ]
            )
    elif league == "fhl":
        for t in nhl_teams:
            all_players.extend(
                [
                    p
                    for p in t.roster
                    if getattr(p, "current_league", "").lower() == "fhl"
                ]
            )
    elif league == "rec1":
        for t in nhl_teams:
            all_players.extend(
                [
                    p
                    for p in t.roster
                    if getattr(p, "current_league", "").lower() == "rec1"
                ]
            )
    elif league == "rec2":
        for t in nhl_teams:
            all_players.extend(
                [
                    p
                    for p in t.roster
                    if getattr(p, "current_league", "").lower() == "rec2"
                ]
            )
    else:
        print("Invalid league")
        return
    if not all_players:
        print(f"{league.upper()}: No players")
        return
    total_players = len(all_players)

    avg_val = sum(p.value for p in all_players) / total_players
    avg_ovr = sum(p.ovr for p in all_players) / total_players
    avg_age = sum(p.age for p in all_players) / total_players

    drafted_players = [
        p for p in all_players if getattr(p, "drafted_by", "") != "UNDRAFTED"
    ]
    avg_draft = (
        (sum(p.draft_number for p in drafted_players) / len(drafted_players))
        if drafted_players
        else 0
    )

    total_gp = 0
    total_goals = 0

    for p in all_players:
        gp = (
            getattr(p, "gp_nhl", 0)
            + getattr(p, "gp_ahl", 0)
            + getattr(p, "gp_eu", 0)
            + getattr(p, "gp_chl", 0)
            + getattr(p, "gp_sphl", 0)
            + getattr(p, "gp_fhl", 0)
            + getattr(p, "gp_rec1", 0)
            + getattr(p, "gp_rec2", 0)
        )

        goals = (
            getattr(p, "careergoals_nhl", 0)
            + getattr(p, "careergoals_ahl", 0)
            + getattr(p, "careergoals_eu", 0)
            + getattr(p, "careergoals_chl", 0)
            + getattr(p, "careergoals_sphl", 0)
            + getattr(p, "careergoals_fhl", 0)
            + getattr(p, "careergoals_rec1", 0)
            + getattr(p, "careergoals_rec2", 0)
        )

        total_gp += gp
        total_goals += goals
    avg_gp = total_gp / total_players
    avg_goals = total_goals / total_players
    avg_gpg = (total_goals / total_gp) if total_gp > 0 else 0

    best_player = max(all_players, key=lambda p: p.ovr)
    worst_player = min(all_players, key=lambda p: p.ovr)

    rookie_count = sum(1 for p in all_players if p.age <= 20)
    vet_count = sum(1 for p in all_players if p.age >= 30)

    print("\n=== LEAGUE STATS ===\n")
    print(f"League: {league.upper()}")
    print(f"Players: {total_players}")
    print(f"Avg OVR: {avg_ovr:.2f}")
    print(f"Avg Value: {avg_val: .2f}")
    print(f"Avg draft pos: {avg_draft: .2f}")
    print(f"Avg Age: {avg_age:.2f}")
    print(f"Avg GP: {avg_gp:.2f}")
    print(f"Avg Goals: {avg_goals:.2f}")
    print(f"League GPG: {avg_gpg:.3f}")
    print(f"Rookies (<=20): {rookie_count}")
    print(f"Veterans (30+): {vet_count}")
    print(f"Best: {best_player.full_name} ({best_player.ovr})")
    print(f"Worst: {worst_player.full_name} ({worst_player.ovr})")


def gen_vet(amount):
    for t in nhl_teams:
        for _ in range(amount):
            p = player_class.Player()
            p.drafted_by = "UNDRAFTED"
            p.age = random.randint(34, 42)
            p.ovr = random.randint(12, 40)
            p.draft_number = 0
            p.retirement_age = random.randint(43, 62)
            p.team = "none"
            t.roster.append(p)
            p.pot = 0
    assign_lineups_pipeline()


def get_team(name):
    for t in nhl_teams + ahl_teams + eu_teams + chl_teams + sphl_teams:
        if name.lower() in t.name.lower():
            return t
    raise ValueError(f"Team '{name}' not found")


def record_season_stats():
    sorted_teams = sorted(
        nhl_teams, key=lambda t: (t.points, t.gdiff, t.gf), reverse=True
    )

    for pos, t in enumerate(sorted_teams, start=1):

        if t.name not in team_history:
            team_history[t.name] = {"positions": [], "gdiffs": []}
        team_history[t.name]["positions"].append(pos)
        team_history[t.name]["gdiffs"].append(t.gdiff)


def rgb(r, g, b):
    return f"\033[38;2;{r};{g};{b}m"


def ovr_color(v):
    base = f"{v:>3}"

    if v >= 95:
        return f"{rgb(171, 125, 255)}{base}\033[0m"  # purple-white
    elif v >= 80:
        return f"{rgb(255, 215, 0)}{base}\033[0m"  # gold
    elif v >= 74:
        return f"{rgb(150, 123, 0)}{base}\033[0m"  # deeper gold
    elif v >= 70:
        return f"{rgb(117, 117, 117)}{base}\033[0m"  # silver
    else:
        return f"{rgb(139, 69, 19)}{base}\033[0m"  # bronze


def get_eligible_prospects():
    return [p for p in PROSPECT_POOL if p.age >= 18]


def team_color(name, text):
    blue_teams = [
        "Red Wings",
        "Griffins",
        "Frölunda",
        "Titans",
        "Steelhawks",
        "Steelhawks",
        "Crushers",
        "Beers",
        "Beerpong",
    ]

    if any(x.lower() in name.lower() for x in blue_teams):
        return f"{Fore.GREEN}{text}{Style.RESET_ALL}"
    return text


def get_attr(p, attr):
    if attr == "gpg":
        gp = getattr(p, "gp_nhl", 0)
        goals = getattr(p, "careergoals_nhl", 0)
        return goals / gp if gp else 0
    if attr == "gpg_nhl":
        gp = getattr(p, "gp_nhl", 0)
        goals = getattr(p, "careergoals_nhl", 0)
        return goals / gp if gp else 0
    if attr == "gpg_ahl":
        gp = getattr(p, "gp_ahl", 0)
        goals = getattr(p, "careergoals_ahl", 0)
        return goals / gp if gp else 0
    if attr == "gpg_eu":
        gp = getattr(p, "gp_eu", 0)
        goals = getattr(p, "careergoals_eu", 0)
        return goals / gp if gp else 0
    if attr == "gpg_chl":
        gp = getattr(p, "gp_chl", 0)
        goals = getattr(p, "careergoals_chl", 0)
        return goals / gp if gp else 0
    if attr == "gpg_sphl":
        gp = getattr(p, "gp_sphl", 0)
        goals = getattr(p, "careergoals_sphl", 0)
        return goals / gp if gp else 0
    if attr == "gpg_fhl":
        gp = getattr(p, "gp_fhl", 0)
        goals = getattr(p, "careergoals_fhl", 0)
        return goals / gp if gp else 0
    if attr == "gpg_rec1":
        gp = getattr(p, "gp_rec1", 0)
        goals = getattr(p, "careergoals_rec1", 0)
        return goals / gp if gp else 0
    if attr == "gpg_rec2":
        gp = getattr(p, "gp_rec2", 0)
        goals = getattr(p, "careergoals_rec2", 0)
        return goals / gp if gp else 0
    return getattr(p, attr, 0)


def change_sort():
    global sort_attr
    options = [
        "ovr",
        "value",
        "age",
        "pot",
        "draft_number",
        "ovr_delta",
        "gp_nhl",
        "careergoals_nhl",
        "gp_ahl",
        "careergoals_ahl",
        "gp_eu",
        "careergoals_eu",
        "gp_chl",
        "careergoals_chl",
        "gp_sphl",
        "careergoals_sphl",
        "gp_fhl",
        "careergoals_fhl",
        "gp_rec1",
        "careergoals_rec1",
        "gp_rec2",
        "careergoals_rec2",
        "gpg_ahl",
        "gpg_eu",
        "gpg_nhl",
        "gpg_chl",
        "gpg_sphl",
        "gpg_fhl",
        "gpg_rec1",
        "gpg_rec2",
        "season_goals",
    ]
    print("\nChoose attribute to sort players by:\n")
    for i, attr in enumerate(options, 1):
        print(f"{i} - {attr}")
    choice = input("Select option: ").strip()
    if choice.isdigit() and 1 <= int(choice) <= len(options):
        sort_attr = options[int(choice) - 1]


def load_custom_roster_profile(filename="custom_roster_profile.json"):
    try:
        with open(filename, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        print("custom roster file not found")
        return
    for team_name, players in data.items():
        team = get_team(team_name)

        for pdata in players:
            p = player_class.Player()

            p.full_name = pdata["full_name"]
            parts = p.full_name.split(" ", 1)
            p.first_name = parts[0]
            p.last_name = parts[1] if len(parts) > 1 else ""

            p.age = pdata["age"]
            p.ovr = pdata["ovr"]
            p.draft_number = pdata["draft_number"]

            p.pot = utils.calcPOT(p.ovr, p.age)
            p.team = team.name
            p.value = utils.calcvalue(p.ovr, p.age)

            p.careergoals = 0
            p.gp = 0
            p.last_game_goals = 0
            p.ovr_delta = 0

            team.roster.append(p)
    print("Custom roster profile loaded.")


# misc engine
def run_initial_drafts():
    for i in range(7):
        reversed_order = i % 2 == 1
        print("\n==============================")
        print(f"INITIAL DRAFT {i + 1}")
        print("Order:", "REVERSED" if reversed_order else "NORMAL")
        print("==============================\n")
        draft.draft(
            nhl_teams, user_team_name=initvalue, rounds=7, reversed_order=reversed_order
        )


# on start
if __name__ == "__main__":
    colorama.init(autoreset=True)
    print(Fore.GREEN + "-==🧊 Welcome to Arran Murdochs - Be a GM simulator🧊 ==-")
    print("_" * 58)
    print("")
    while True:
        skip_init = str(input("skip inital draft? y/n: "))
        if skip_init == "y":
            initvalue = None
            break
        elif skip_init == "n":
            initvalue = "Red Wings"
            break
        print("invalid")
    while True:
        use_custom = input("load custom roster profile? y/n: ").strip().lower()
        if use_custom in ("y", "n"):
            break
        print("invalid")
    if skip_init == "y":
        print("\nInitial draft will now be auto simulated...")
    else:
        print("\nInitial draft beginning...")
    time.sleep(2)
# vars init
franchises = []
nhl_teams = []
ahl_teams = []
eu_teams = []
chl_teams = []
sphl_teams = []
fhl_teams = []
rec1_teams = []
rec2_teams = []
pair_count = {}
schedule_pairs = {}
schedule_list = []
counter = 0

for i in range(len(nhl_teams)):
    for j in range(i + 1, len(nhl_teams)):
        t1 = nhl_teams[i]
        t2 = nhl_teams[j]
        key = tuple(sorted([t1.name, t2.name]))
        pair_count[key] = 0
for i in range(len(globalvars.teamnames)):
    nhl = team_class.Team(globalvars.teamnames[i])
    ahl = team_class.Team(globalvars.AHLteamnames[i])
    eu = team_class.Team(globalvars.EUteamnames[i])
    chl = team_class.Team(globalvars.CHLteamnames[i])
    sphl = team_class.Team(globalvars.SPHLteamnames[i])
    fhl = team_class.Team(globalvars.FHLteamnames[i])
    rec1 = team_class.Team(globalvars.REC1teamnames[i])
    rec2 = team_class.Team(globalvars.REC2teamnames[i])
    franchises.append(globalvars.Franchise(nhl, ahl, eu, chl, sphl, fhl, rec1, rec2))
    nhl_teams.append(nhl)
    ahl_teams.append(ahl)
    eu_teams.append(eu)
    chl_teams.append(chl)
    sphl_teams.append(sphl)
    fhl_teams.append(fhl)
    rec1_teams.append(rec1)
    rec2_teams.append(rec2)
teams = nhl_teams

if use_custom == "y":
    load_custom_roster_profile()
all_leagues = {
    "NHL": nhl_teams,
    "AHL": ahl_teams,
    "EU": eu_teams,
    "CHL": chl_teams,
    "SPHL": sphl_teams,
    "FHL": fhl_teams,
    "REC1": rec1_teams,
    "REC2": rec2_teams,
}
all_matchups = []
next_game_idx = 0
pair_count = {}
sort_attr = "ovr"
red_wings = None
season_num = 0
draft_done = False
season_complete = False
team_history = {t.name: {"positions": [], "gdiffs": []} for t in nhl_teams}
hof = {
    "highest_gpg": None,
    "highest_career_goals": None,
    "highest_overall": None,
    "highest_value": None,
    "highest_overall_1st_round": None,
    "highest_overall_2nd_round": None,
    "highest_overall_3rd_round": None,
    "highest_overall_4th_round": None,
    "highest_overall_5th_round": None,
    "highest_overall_6th_round": None,
    "highest_overall_7th_round": None,
    "season_records": {
        "most_goals_in_season": (0, 0),
        "highest_team_points": (0, 0),
    },
}


# update funcs
def assign_lineups_pipeline():
    for f in franchises:

        combined_players = (
            f.nhl.roster
            + f.ahl.roster
            + f.eu.roster
            + f.chl.roster
            + f.sphl.roster
            + f.fhl.roster
            + f.rec1.roster
            + f.rec2.roster
        )

        unique_players = list(dict.fromkeys(combined_players))

        all_players = sorted(
            unique_players,
            key=lambda p: p.ovr,
            reverse=True,
        )

        for p in all_players:
            p.current_league = ""
            p.current_team = ""
        f.nhl.lineup = all_players[:18]
        f.ahl.lineup = all_players[18:36]
        f.eu.lineup = all_players[36:54]
        f.chl.lineup = all_players[54:72]
        f.sphl.lineup = all_players[72:90]
        f.fhl.lineup = all_players[90:108]
        f.rec1.lineup = all_players[108:118]
        f.rec2.lineup = all_players[118:128]

        for p in f.nhl.lineup:
            p.current_league = "NHL"
            p.current_team = f.nhl.name
        for p in f.ahl.lineup:
            p.current_league = "AHL"
            p.current_team = f.ahl.name
        for p in f.eu.lineup:
            p.current_league = "EU"
            p.current_team = f.eu.name
        for p in f.chl.lineup:
            p.current_league = "CHL"
            p.current_team = f.chl.name
        for p in f.sphl.lineup:
            p.current_league = "SPHL"
            p.current_team = f.sphl.name
        for p in f.fhl.lineup:
            p.current_league = "FHL"
            p.current_team = f.fhl.name
        for p in f.rec1.lineup:
            p.current_league = "REC1"
            p.current_team = f.rec1.name
        for p in f.rec2.lineup:
            p.current_league = "REC2"
            p.current_team = f.rec2.name


def update_lineup_stats(team, league):
    for p in team.lineup:
        if league == "NHL":
            p.gp_nhl += 1
            p.careergoals_nhl += p.last_game_goals
            p.season_goals += p.last_game_goals
        elif league == "AHL":
            p.season_goals += p.last_game_goals
            p.gp_ahl += 1
            p.careergoals_ahl += p.last_game_goals
        elif league == "EU":
            p.season_goals += p.last_game_goals
            p.gp_eu += 1
            p.careergoals_eu += p.last_game_goals
        elif league == "CHL":
            p.season_goals += p.last_game_goals
            p.gp_chl += 1
            p.careergoals_chl += p.last_game_goals
        elif league == "SPHL":
            p.season_goals += p.last_game_goals
            p.gp_sphl += 1
            p.careergoals_sphl += p.last_game_goals
        elif league == "FHL":
            p.season_goals += p.last_game_goals
            p.gp_fhl += 1
            p.careergoals_fhl += p.last_game_goals
        elif league == "REC1":
            p.season_goals += p.last_game_goals
            p.gp_rec1 += 1
            p.careergoals_rec1 += p.last_game_goals
        elif league == "REC2":
            p.season_goals += p.last_game_goals
            p.gp_rec2 += 1
            p.careergoals_rec2 += p.last_game_goals


def update_team_rating(team):
    if team.lineup:
        team.rating = sum(p.ovr for p in team.lineup) / len(team.lineup)
    elif team.roster:
        team.rating = sum(p.ovr for p in team.roster) / len(team.roster)
    else:
        team.rating = 0


def calculate_player_stats():
    for t in nhl_teams + ahl_teams + eu_teams:
        for p in t.roster:
            if not hasattr(p, "careergoals_nhl"):
                p.careergoals_nhl = 0
            if not hasattr(p, "gp_nhl"):
                p.gp_nhl = 0
            if not hasattr(p, "careergoals_ahl"):
                p.careergoals_ahl = 0
            if not hasattr(p, "gp_ahl"):
                p.gp_ahl = 0
            if not hasattr(p, "careergoals_eu"):
                p.careergoals_eu = 0
            if not hasattr(p, "gp_eu"):
                p.gp_eu = 0
            if not hasattr(p, "last_game_goals"):
                p.last_game_goals = 0
            if not hasattr(p, "ovr_delta"):
                p.ovr_delta = 0
            if not hasattr(p, "current_league"):
                p.current_league = "NONE"
        for attr in [
            "gp_chl",
            "careergoals_chl",
            "gp_sphl",
            "careergoals_sphl",
            "gp_fhl",
            "careergoals_fhl",
            "gp_rec1",
            "careergoals_rec1",
            "gp_rec2",
            "careergoals_rec2",
        ]:
            if not hasattr(p, attr):
                setattr(p, attr, 0)


def update_hof():
    global season_num
    for t in teams:
        for p in t.roster:
            gp = (
                getattr(p, "gp_nhl", 0)
                + getattr(p, "gp_ahl", 0)
                + getattr(p, "gp_eu", 0)
            )
            careergoals = (
                getattr(p, "careergoals_nhl", 0)
                + getattr(p, "careergoals_ahl", 0)
                + getattr(p, "careergoals_eu", 0)
            )
            ovr = getattr(p, "ovr", 0)
            value = getattr(p, "value", 0)
            draft_number = getattr(p, "draft_number", 0)
            if gp > 0:
                gpg = careergoals / gp
                if not hof["highest_gpg"] or gpg > hof["highest_gpg"][0]:
                    hof["highest_gpg"] = (gpg, p, season_num)
            if (
                not hof["highest_career_goals"]
                or careergoals > hof["highest_career_goals"][0]
            ):
                hof["highest_career_goals"] = (careergoals, p, season_num)
            if not hof["highest_overall"] or ovr > hof["highest_overall"][0]:
                hof["highest_overall"] = (ovr, p, season_num)
            if not hof["highest_value"] or value > hof["highest_value"][0]:
                hof["highest_value"] = (value, p, season_num)
            if draft_number:
                if 1 <= draft_number <= 32:
                    if (
                        not hof["highest_overall_1st_round"]
                        or ovr > hof["highest_overall_1st_round"][0]
                    ):
                        hof["highest_overall_1st_round"] = (ovr, p, season_num)
                elif 33 <= draft_number <= 64:
                    if (
                        not hof["highest_overall_2nd_round"]
                        or ovr > hof["highest_overall_2nd_round"][0]
                    ):
                        hof["highest_overall_2nd_round"] = (ovr, p, season_num)
                elif 65 <= draft_number <= 96:
                    if (
                        not hof["highest_overall_3rd_round"]
                        or ovr > hof["highest_overall_3rd_round"][0]
                    ):
                        hof["highest_overall_3rd_round"] = (ovr, p, season_num)
                elif 97 <= draft_number <= 128:
                    if (
                        not hof["highest_overall_4th_round"]
                        or ovr > hof["highest_overall_4th_round"][0]
                    ):
                        hof["highest_overall_4th_round"] = (ovr, p, season_num)
                elif 129 <= draft_number <= 160:
                    if (
                        not hof["highest_overall_5th_round"]
                        or ovr > hof["highest_overall_5th_round"][0]
                    ):
                        hof["highest_overall_5th_round"] = (ovr, p, season_num)
                elif 161 <= draft_number <= 192:
                    if (
                        not hof["highest_overall_6th_round"]
                        or ovr > hof["highest_overall_6th_round"][0]
                    ):
                        hof["highest_overall_6th_round"] = (ovr, p, season_num)
                elif 193 <= draft_number <= 224:
                    if (
                        not hof["highest_overall_7th_round"]
                        or ovr > hof["highest_overall_7th_round"][0]
                    ):
                        hof["highest_overall_7th_round"] = (ovr, p, season_num)


def update_team_type(teams):
    team_ratings = []
    for t in teams:
        if t.lineup:
            rating = sum(p.ovr for p in t.lineup) / len(t.lineup)
        elif t.roster:
            rating = sum(p.ovr for p in t.roster) / len(t.roster)
        else:
            rating = 0
        t.rating = rating
        team_ratings.append(rating)
    sorted_ratings = sorted(team_ratings)
    lower_third = sorted_ratings[len(sorted_ratings) // 3] if sorted_ratings else 0
    upper_third = (
        sorted_ratings[(2 * len(sorted_ratings)) // 3] if sorted_ratings else 0
    )

    for t in teams:
        if t.rating < lower_third:
            t.team_type = "rebuilding"
        elif t.rating < upper_third:
            t.team_type = "balanced"
        else:
            t.team_type = "contender"


# save funcs
def save_game(filename="savegame.pkl"):
    import pickle
    import playoff_logic

    playoff_state = {
        league: playoff_logic.get_state(league)
        for league in ["NHL", "AHL", "EU", "CHL", "SPHL", "FHL", "REC1", "REC2"]
    }

    data = {
        "nhl_teams": nhl_teams,
        "ahl_teams": ahl_teams,
        "eu_teams": eu_teams,
        "chl_teams": chl_teams,
        "sphl_teams": sphl_teams,
        "fhl_teams": fhl_teams,
        "rec1_teams": rec1_teams,
        "rec2_teams": rec2_teams,
        "prospects": PROSPECT_POOL,
        "season_num": season_num,
        "next_game_idx": next_game_idx,
        "all_matchups": all_matchups,
        "draft_done": draft_done,
        "season_complete": season_complete,
        "team_history": team_history,
        "hof": hof,
        "sort_attr": sort_attr,
        "pair_count": pair_count,
        "counter": counter,
        "team_cash": {t.name: int(t.cash) for t in nhl_teams},
        "playoff_state": playoff_state,
    }

    with open(filename, "wb") as f:
        pickle.dump(data, f)
    print("Game saved.")


def load_game(filename="savegame.pkl"):
    global nhl_teams, ahl_teams, eu_teams, chl_teams, sphl_teams, fhl_teams, rec1_teams, rec2_teams
    global teams, PROSPECT_POOL, season_num, next_game_idx
    global all_matchups, draft_done, season_complete
    global team_history, hof, sort_attr, red_wings
    global all_leagues, pair_count, franchises, counter

    import pickle
    import playoff_logic

    with open(filename, "rb") as f:
        data = pickle.load(f)
    nhl_teams = data["nhl_teams"]
    ahl_teams = data["ahl_teams"]
    eu_teams = data["eu_teams"]
    chl_teams = data["chl_teams"]
    sphl_teams = data["sphl_teams"]
    fhl_teams = data["fhl_teams"]
    rec1_teams = data["rec1_teams"]
    rec2_teams = data["rec2_teams"]

    teams = nhl_teams

    PROSPECT_POOL[:] = data["prospects"]
    season_num = data["season_num"]
    next_game_idx = data["next_game_idx"]
    all_matchups = data["all_matchups"]
    draft_done = data["draft_done"]
    season_complete = data["season_complete"]
    team_history = data["team_history"]
    hof = data["hof"]
    sort_attr = data["sort_attr"]
    pair_count = data["pair_count"]
    counter = data["counter"]

    cash_map = data.get("team_cash", {})
    for t in nhl_teams:
        if t.name in cash_map:
            t.cash = cash_map[t.name]
    all_leagues = {
        "NHL": nhl_teams,
        "AHL": ahl_teams,
        "EU": eu_teams,
        "CHL": chl_teams,
        "SPHL": sphl_teams,
        "FHL": fhl_teams,
        "REC1": rec1_teams,
        "REC2": rec2_teams,
    }

    franchises = []
    for i in range(len(nhl_teams)):
        franchises.append(
            globalvars.Franchise(
                nhl_teams[i],
                ahl_teams[i],
                eu_teams[i],
                chl_teams[i],
                sphl_teams[i],
                fhl_teams[i],
                rec1_teams[i],
                rec2_teams[i],
            )
        )
    red_wings = nhl_teams[0]

    assign_lineups_pipeline()

    playoff_state = data.get("playoff_state", {})

    for league, state in playoff_state.items():
        playoff_logic.playoff_data[league] = state
    print("Game loaded.")


# print funcs
def view_all_players_in_choice(choice_league, sort_attr="ovr"):
    all_players = []

    if choice_league.lower() == "nhl":
        for t in nhl_teams:
            all_players.extend(
                [
                    p
                    for p in t.roster
                    if getattr(p, "current_league", "").lower() == "nhl"
                ]
            )
    elif choice_league.lower() == "ahl":
        for t in nhl_teams:
            all_players.extend(
                [
                    p
                    for p in t.roster
                    if getattr(p, "current_league", "").lower() == "ahl"
                ]
            )
    elif choice_league.lower() == "eu":
        for t in nhl_teams:
            all_players.extend(
                [
                    p
                    for p in t.roster
                    if getattr(p, "current_league", "").lower() == "eu"
                ]
            )
    elif choice_league.lower() == "chl":
        for t in nhl_teams:
            all_players.extend(
                [
                    p
                    for p in t.roster
                    if getattr(p, "current_league", "").lower() == "chl"
                ]
            )
    elif choice_league.lower() == "sphl":
        for t in nhl_teams:
            all_players.extend(
                [
                    p
                    for p in t.roster
                    if getattr(p, "current_league", "").lower() == "sphl"
                ]
            )
    elif choice_league.lower() == "fhl":
        for t in nhl_teams:
            all_players.extend(
                [
                    p
                    for p in t.roster
                    if getattr(p, "current_league", "").lower() == "fhl"
                ]
            )
    elif choice_league.lower() == "rec1":
        for t in nhl_teams:
            all_players.extend(
                [
                    p
                    for p in t.roster
                    if getattr(p, "current_league", "").lower() == "rec1"
                ]
            )
    elif choice_league.lower() == "rec2":
        for t in nhl_teams:
            all_players.extend(
                [
                    p
                    for p in t.roster
                    if getattr(p, "current_league", "").lower() == "rec2"
                ]
            )
    else:
        print("Invalid league choice.")
        return
    all_players.sort(key=lambda p: get_attr(p, sort_attr), reverse=True)

    print(
        f"\nAll Players in {choice_league.upper()} (sorted by {sort_attr.upper()}):\n"
    )
    print(playerformat)
    print("-" * dashamount)

    for p in all_players:
        print(format_player(p))


def format_player(p):
    name = p.full_name[:18]
    team = p.team[:10] if hasattr(p, "team") else ""

    def get_stats(prefix):
        gp = getattr(p, f"gp_{prefix}", 0)
        goals = getattr(p, f"careergoals_{prefix}", 0)
        gpg = goals / gp if gp else 0
        return gp, goals, gpg

    leagues = [
        ("NHL", "nhl"),
        ("AHL", "ahl"),
        ("EU", "eu"),
        ("CHL", "chl"),
        ("SPHL", "sphl"),
        ("FHL", "fhl"),
        ("R1", "rec1"),
        ("R2", "rec2"),
    ]

    stat_parts = []
    for tag, key in leagues:
        gp, goals, gpg = get_stats(key)
        stat_parts.append(f"{tag}:{gp:4}/{goals:4}({gpg:4.2f})")
    stats = "|".join(stat_parts)

    draft = getattr(p, "draft_number", 0)
    draft_round = ((draft - 1) // 32 + 1) if draft else 0

    delta = int(getattr(p, "ovr_delta", 0))
    delta_str = f"{delta:+d}"

    if delta > 0:
        delta_str = f"{Fore.GREEN}{delta_str}{Style.RESET_ALL}"
    elif delta < 0:
        delta_str = f"{Fore.RED}{delta_str}{Style.RESET_ALL}"
    else:
        delta_str = f"{Fore.YELLOW}{delta_str}{Style.RESET_ALL}"
    return (
        f"{p.full_name:<23}|age:{p.age:>2}|💪{ovr_color(int(p.ovr))}|Δ:{delta_str}|📈 {pot_conv(p.pot):<9}|"
        f"{getattr(p, 'current_team', 'NONE'):<14}|💰{p.value:>3}|G{p.season_goals:>2}|"
        f"{stats}|"
        f"{draft_round}{utils.suffex(draft_round)} #{draft:<3}|{getattr(p, 'drafted_by', 'UNDRAFTED'):<14} |"
        f"{({'REC1': 'R1', 'REC2': 'R2'}.get(getattr(p, 'current_league', 'N/A'), getattr(p, 'current_league', 'N/A')))}"
    )


def print_hof():
    print("\n=== HALL OF FAME ===\n")

    def show(label, entry):
        if entry:
            value, p, season = entry
            print(
                f"{label}: {p.full_name} | Value: {value} | Draft: {p.draft_number} | Season {season}"
            )
        else:
            print(f"{label}: None")

    show("Highest GPG", hof["highest_gpg"])
    show("Highest Career Goals", hof["highest_career_goals"])
    show("Highest Overall", hof["highest_overall"])
    show("Highest Value", hof["highest_value"])
    show("Highest 1st Round OVR", hof["highest_overall_1st_round"])
    show("Highest 2st Round OVR", hof["highest_overall_2nd_round"])
    show("Highest 3rd Round OVR", hof["highest_overall_3rd_round"])
    show("Highest 4th Round OVR", hof["highest_overall_4th_round"])
    show("Highest 5th Round OVR", hof["highest_overall_5th_round"])
    show("Highest 6th Round OVR", hof["highest_overall_6th_round"])
    show("Highest 7th Round OVR", hof["highest_overall_7th_round"])
    print("\nSeason Records:")
    most_goals = hof["season_records"]["most_goals_in_season"]
    if most_goals:
        print(f"Most Goals in Season: {most_goals[0]} | Season {most_goals[1]}")
    else:
        print("Most Goals in Season: None")
    team_points = hof["season_records"]["highest_team_points"]
    if team_points:
        print(f"Highest Team Points: {team_points[0]} | Season {team_points[1]}")
    else:
        print("Highest Team Points: None")


def print_team_info():
    league = (
        input("Which league for team info? (NHL/AHL/EU/CHL/SPHL/FHL/rec1/rec2): ")
        .strip()
        .upper()
    )
    if league not in all_leagues:
        print("Invalid league.")
        return
    print("\nTEAM LEADERBOARD\n")

    rows = []
    league_teams = all_leagues[league]

    sorted_teams = sorted(
        league_teams,
        key=lambda x: (
            sum(p.ovr for p in x.lineup) / len(x.lineup)
            if x.lineup
            else (sum(p.ovr for p in x.roster) / len(x.roster) if x.roster else 0)
        ),
    )

    for t in sorted_teams:
        h = team_history.get(t.name, {"positions": [], "gdiffs": []})

        avg_pos = (
            (sum(h["positions"]) / len(h["positions"])) if h["positions"] else None
        )
        avg_gd = sum(h["gdiffs"]) / len(h["gdiffs"]) if h["gdiffs"] else 0

        titles = getattr(t, "titles", 0)
        roster_size = len(t.roster)

        cash = getattr(t, "cash", 0)
        pending = getattr(t, "pending_cash", 0)

        playoffs = getattr(t, "playoffs", 0)

        streak = getattr(t, "playoff_streak", getattr(t, "playoff_streak", 0))
        drought = getattr(t, "playoff_drought", getattr(t, "playoff_drought", 0))

        if streak > 0:
            streak_info = f"🔥 {streak}"
        elif drought > 0:
            streak_info = f"🌵 {drought}"
        else:
            streak_info = ""
        if t.lineup:
            avg_ovr = sum(p.ovr for p in t.lineup) / len(t.lineup)
            avg_age = sum(p.age for p in t.lineup) / len(t.lineup)
            best_player = max(t.lineup, key=lambda p: p.ovr)
            best_player_info = f"{best_player.full_name} ({best_player.ovr} OVR, {best_player.age} AGE)"
        else:
            avg_ovr = 0
            avg_age = 0
            best_player_info = "None"
        rows.append(
            (
                avg_pos,
                t.name,
                avg_gd,
                titles,
                playoffs,
                streak_info,
                roster_size,
                avg_ovr,
                avg_age,
                cash,
                pending,
                t.team_type,
                best_player_info,
            )
        )
    rows.sort(
        key=lambda x: (
            x[0] is None,
            x[0] if x[0] is not None and x[0] > 0 else float("inf"),
        )
    )

    print(
        f"{'Team':<15} | Avg Pos | Avg GD  | 🏆 | Playoffs | streak  | Roster |  💪   |  Age  |  💵  | Type        | Best Player"
    )
    print("-" * 175)

    for (
        avg_pos,
        name,
        avg_gd,
        titles,
        playoffs,
        streak_info,
        roster_size,
        avg_ovr,
        avg_age,
        cash,
        pending,
        team_type,
        best_player_info,
    ) in rows:
        avg_pos_str = f"{avg_pos:.2f}" if avg_pos is not None else "N/A"
        print(
            f"{name:<15} | {avg_pos_str:<7} | {avg_gd:<7.2f} | {titles:<2} | {playoffs:<8} | "
            f"{streak_info:<6} | {roster_size:<6} | {avg_ovr:<5.2f} | {avg_age:<5.2f} | "
            f"{cash:<4} | {team_type:<12} | {best_player_info}"
        )


from colorama import Fore, Style

from colorama import Fore, Style

from colorama import Fore, Style

def color_gd(gd):
    if gd > 0:
        return Fore.GREEN + "+" +str(gd) + Style.RESET_ALL
    elif gd < 0:
        return Fore.RED + str(gd) + Style.RESET_ALL
    else:
        return Fore.YELLOW + str(gd) + Style.RESET_ALL


def print_standings():
    league = input("Which league standings? (NHL/AHL/EU/CHL/SPHL/FHL/rec1/rec2): ").strip().upper()

    if league not in all_leagues:
        print("Invalid league.")
        return

    header = (
        "Team                 |  💪  |   📊   | ⭐  | GF   | GA   | GD   | L10   |   🔥   | Avg g     | Type         | 💵"
    )

    print(f"\nStandings ({league}):\n")
    print(header)
    print("-" * 114)

    league_teams = all_leagues[league]

    sorted_teams = sorted(
        league_teams,
        key=lambda x: (x.points, x.gdiff, x.gf),
        reverse=True
    )

    green_teams = {
        "Red Wings",
        "Griffins",
        "Frölunda",
        "Titans",
        "Steelhawks",
        "Crushers",
        "Beers",
        "Beerpong"
    }

    divider_printed = False
    half_point = len(sorted_teams) // 2

    for i, t in enumerate(sorted_teams):

        if not divider_printed and i == half_point:
            print("-" * 114)
            divider_printed = True

        name = t.name.strip()

        w = getattr(t, "wins", 0)
        l = getattr(t, "losses", 0)
        games = w + l if (w + l) else 1

        record = f"{w}-{l}"

        last10 = t.last10[-10:]
        lw = last10.count("W")
        ll = last10.count("L")
        l10 = f"{lw}-{ll}"

        gf_avg = t.gf / games
        ga_avg = t.ga / games

        streak = 0
        streak_type = ""

        for r in reversed(last10):
            if streak == 0:
                streak_type = r
                streak = 1
            elif r == streak_type:
                streak += 1
            else:
                break

        streak_str = f"{streak}{streak_type}" if streak_type else ""

        gd = getattr(t, "gdiff", 0)

        row = (
            f"{name:<20} | "
            f"{getattr(t, 'rating', 0):<4.1f} | "
            f"{record:<6} | "
            f"{t.points:<3} | "
            f"{t.gf:<4} | "
            f"{t.ga:<4} | "
            f"{color_gd(gd):<13} | "
            f"{l10:<5} | "
            f"{streak_str:<6} |"
            f"{gf_avg:4.1f} -{ga_avg:4.1f} | "
            f"{getattr(t, 'team_type', 'N/A'):<12} | "
            f"{getattr(t, 'cash', 0):<4}"
        )

        if name in green_teams:
            row = Fore.GREEN + row + Style.RESET_ALL

        print(row)

def mega_analysis():
    from draft import LAST_DRAFT

    if not LAST_DRAFT:
        print("\nNo draft data available.\n")
        return
    n = len(LAST_DRAFT)

    ovr_list = [p.ovr for p in LAST_DRAFT]
    pot_list = [p.pot for p in LAST_DRAFT]
    age_list = [p.age for p in LAST_DRAFT]

    avg_ovr = sum(ovr_list) / n
    avg_pot = sum(pot_list) / n
    avg_age = sum(age_list) / n

    best = max(LAST_DRAFT, key=lambda p: p.ovr)
    worst = min(LAST_DRAFT, key=lambda p: p.ovr)

    elite = [p for p in LAST_DRAFT if p.ovr >= 85]
    starter = [p for p in LAST_DRAFT if 75 <= p.ovr < 85]
    depth = [p for p in LAST_DRAFT if 65 <= p.ovr < 75]
    low = [p for p in LAST_DRAFT if p.ovr < 65]

    spread = max(ovr_list) - min(ovr_list)

    avg_dev_gap = sum(p.pot - p.ovr for p in LAST_DRAFT) / n
    avg_age_eff = sum(p.ovr / p.age for p in LAST_DRAFT) / n

    sorted_by_pick = sorted(
        LAST_DRAFT, key=lambda p: p.draft_number if p.draft_number else 9999
    )

    mid = n // 2
    early = sorted_by_pick[:mid]
    late = sorted_by_pick[mid:]

    early_avg = sum(p.ovr for p in early) / len(early) if early else 0
    late_avg = sum(p.ovr for p in late) / len(late) if late else 0

    def percentile(val, arr):
        return sum(1 for x in arr if x <= val) / len(arr) * 100

    ovr_percentiles = [percentile(v, ovr_list) for v in ovr_list]
    avg_percentile = sum(ovr_percentiles) / n

    steals = sorted(
        LAST_DRAFT,
        key=lambda p: p.ovr - (p.draft_number * 0.12 if p.draft_number else 0),
        reverse=True,
    )

    reaches = sorted(
        LAST_DRAFT,
        key=lambda p: (p.draft_number * 0.12 if p.draft_number else 0) - p.ovr,
        reverse=True,
    )

    round_data = {i: [] for i in range(1, 8)}
    for p in LAST_DRAFT:
        if p.draft_number:
            r = ((p.draft_number - 1) // 32) + 1
            if 1 <= r <= 7:
                round_data[r].append(p)
    all_players = []
    for t in nhl_teams + ahl_teams + eu_teams:
        all_players.extend(t.roster)
    league_n = len(all_players)

    league_age = sum(p.age for p in all_players) / league_n
    league_ovr = sum(p.ovr for p in all_players) / league_n

    rookies = [p for p in all_players if p.gp_nhl + p.gp_ahl + p.gp_eu == 62]
    vets = [p for p in all_players if p.age >= 30]

    total_career_games = [(p.gp_nhl + p.gp_ahl + p.gp_eu) for p in all_players]

    avg_career_games = sum(total_career_games) / league_n

    most_experienced = sorted(
        all_players,
        key=lambda p: (p.gp_nhl + p.gp_ahl + p.gp_eu),
        reverse=True,
    )[:10]

    youngest = sorted(all_players, key=lambda p: p.age)[:10]

    oldest = sorted(
        [p for p in all_players if p.draft_number != 0],
        key=lambda p: p.age,
        reverse=True
    )[:10]

    agingstars = agingstars = sorted(
        [p for p in all_players if p.ovr >= 75], key=lambda p: p.age, reverse=True
    )[:10]

    team_avgs = []
    for t in nhl_teams:
        if t.roster:
            team_avgs.append(sum(p.ovr for p in t.roster) / len(t.roster))
    parity = (
        sum((x - sum(team_avgs) / len(team_avgs)) ** 2 for x in team_avgs)
        / len(team_avgs)
        if team_avgs
        else 0
    )

    print("\n==============================")
    print("          DRAFT ANALYSIS     ")
    print("==============================\n")

    print(f"Players (Draft): {n}")
    print(f"Avg OVR: {avg_ovr:.2f}")
    print(f"Avg POT: {avg_pot:.2f}")
    print(f"Avg Age: {avg_age:.2f}")
    print(f"OVR Spread: {spread}")
    print("Best:")
    print(format_player(best))
    print("worst:")
    print(format_player(worst))

    print(f"\nElite (85+): {len(elite)}")
    for p in elite:
        print(format_player(p))
    print(f"\nStarter (75-84): {len(starter)}")
    print(f"Depth (65-74): {len(depth)}")
    print(f"Low (<65): {len(low)}")

    print(f"\nDev Gap (POT-OVR): {avg_dev_gap:.2f}")
    print(f"Age Efficiency: {avg_age_eff:.2f}")
    print(f"Percentile Strength: {avg_percentile:.2f}")

    print("\nEarly vs Late Draft Strength:")
    print(f"Early Avg OVR: {early_avg:.2f}")
    print(f"Late Avg OVR: {late_avg:.2f}")

    print("\nRound Strength Report:")
    for r in range(1, 8):
        vals = round_data[r]
        if vals:
            print(
                f"Round {r}: Avg OVR {sum(p.ovr for p in vals) / len(vals):.2f} | Count {len(vals)}"
            )
        else:
            print(f"Round {r}: No data")
    print("\nTop 5 Steals:")
    for p in steals[:5]:
        print(format_player(p))
    print("\nTop 5 Reaches:")
    for p in reaches[:5]:
        print(format_player(p))
    print("\nTop 5 Best Players:")
    for p in sorted(LAST_DRAFT, key=lambda p: p.ovr, reverse=True)[:5]:
        print(format_player(p))
    print("\n==============================")
    print("       LEAGUE ANALYSIS")
    print("==============================\n")

    print(f"League Avg OVR: {league_ovr:.2f}")
    print(f"League Avg Age: {league_age:.2f}")
    print(f"Avg Career Games: {avg_career_games:.2f}")

    print(f"total players: {len(all_players)}")
    print(f"Rookies (=62 GP): {len(rookies)}")
    print(f"Veterans (28+): {len(vets)}")

    print("\nTop 10 Most Experienced Players:")
    for p in most_experienced:
        print(format_player(p))
    print("\nOldest Active Players:")
    for p in oldest:
        print(format_player(p))
    print("\nAging Stars:")
    for p in agingstars:
        print(format_player(p))
    print(f"\nTeam Parity Index: {parity:.2f}")

    print("\n==============================\n")


def print_roster(team):
    print(f"\nRoster for {team.name} (sorted by {sort_attr}):\n")
    print(playerformat)
    print("-" * dashamount)
    for p in sorted(team.roster, key=lambda p: get_attr(p, sort_attr), reverse=True):
        print(format_player(p))


def print_all_players():
    all_players = []
    for t in nhl_teams:
        all_players.extend([p for p in t.roster if getattr(p, "gp_nhl", 0) > 0])
    all_players.sort(key=lambda p: get_attr(p, sort_attr), reverse=True)
    print(f"\nAll Players in League (sorted by {sort_attr}):\n")
    print(playerformat)
    print("-" * dashamount)
    for p in all_players:
        print(format_player(p))


def print_all_prospects():
    all_players = []
    for t in nhl_teams:
        all_players.extend([p for p in t.roster if getattr(p, "gp_nhl", 0) == 0])
    all_players.sort(key=lambda p: get_attr(p, sort_attr), reverse=True)
    print(f"\nAll Prospects (sorted by {sort_attr}):\n")
    print(playerformat)
    print("-" * dashamount)
    for p in all_players:
        print(format_player(p))


def print_lineup_stats(team):
    print(f"\nLineup Stats for {team.name} (sorted by {sort_attr}):\n")
    print(playerformat)
    print("-" * dashamount)
    for p in sorted(team.lineup, key=lambda p: get_attr(p, sort_attr), reverse=True):
        print(format_player(p))


def print_season_status(teams):
    print(f"\nSeason {season_num} Status:")
    print(
        f"All matches completed: {'Yes' if playoff_logic.get_state('NHL')['complete'] else 'No'}"
    )
    print(f"Draft done this season: {'Yes' if draft_done else 'No'}")

    red_wings = None
    for t in teams:
        if t.name.lower() == "red wings":
            red_wings = t
            break
    if red_wings:
        print(f"Red Wings cash 💵: {red_wings.cash}")
    else:
        print("Red Wings not found")


def view_any_team_roster():
    print("\nSelect team:\n")
    all_teams = nhl_teams
    for i, t in enumerate(all_teams, 1):
        print(f"{i} - {t.name}")
    while True:
        try:
            choice = int(input("Choose team: ").strip())
            if 1 <= choice <= len(all_teams):
                break
            print("out of range")
        except ValueError:
            print("invalid input")
    team = all_teams[choice - 1]
    print_roster(team)


def view_any_team_lineup():
    print("\nSelect team:\n")
    all_teams = (
        nhl_teams
        + ahl_teams
        + eu_teams
        + chl_teams
        + sphl_teams
        + fhl_teams
        + rec1_teams
        + rec2_teams
    )
    for i, t in enumerate(all_teams, 1):
        print(f"{i} - {t.name}")
    while True:
        try:
            choice = int(input("Choose team: ").strip())
            if 1 <= choice <= len(all_teams):
                break
            print("out of range")
        except ValueError:
            print("invalid input")
    team = all_teams[choice - 1]
    print_lineup_stats(team)


def print_prospects():
    all_prospects = sorted(
        PROSPECT_POOL, key=lambda p: get_attr(p, sort_attr), reverse=True
    )
    print(f"\nProspects (sorted by {sort_attr}):\n")
    print(playerformat)
    print("-" * dashamount)
    for p in all_prospects:
        print(format_player(p))


def search_players():
    query = input("Enter player name: ").strip().lower()
    matches = []
    for t in nhl_teams + ahl_teams + eu_teams:
        for p in t.roster:
            if query in p.full_name.lower():
                matches.append(p)
    for p in PROSPECT_POOL:
        if query in p.full_name.lower():
            matches.append(p)
    if not matches:
        print("\nNo players found")
        return
    matches.sort(key=lambda p: p.ovr, reverse=True)
    print("\nSearch Results:\n")
    print(playerformat)
    print("-" * dashamount)
    for p in matches:
        print(format_player(p))


# player creation
def create_player():
    fname = input("First name: ").strip()
    sname = input("Last name: ").strip()

    while True:
        try:
            age = int(input("Age: ").strip())
            break
        except ValueError:
            print("invalid age")
    while True:
        try:
            ovr = int(input("OVR: ").strip())
            break
        except ValueError:
            print("invalid ovr")
    while True:
        try:
            draft_num = int(input("Draft number: ").strip())
            break
        except ValueError:
            print("invalid draft number")
    print("\nSelect team:\n")
    for i, t in enumerate(teams, 1):
        print(f"{i} - {t.name}")
    while True:
        try:
            team_choice = int(input("Choose team: ").strip())
            if 1 <= team_choice <= len(teams):
                break
            print("out of range")
        except ValueError:
            print("invalid input")
    team = teams[team_choice - 1]

    print("\nSelect draft team:\n")
    print("0 - UNDRAFTED / NONE")
    for i, t in enumerate(teams, 1):
        print(f"{i} - {t.name}")
    while True:
        try:
            choice = int(input("Choose draft team: ").strip())

            if choice == 0:
                draft_team = "UNDRAFTED"
                break
            if 1 <= choice <= len(teams):
                draft_team = teams[choice - 1].name
                break
            print("out of range")
        except ValueError:
            print("invalid input")
    p = player_class.Player()
    p.first_name = fname
    p.last_name = sname
    p.full_name = f"{fname} {sname}"
    p.age = age
    p.ovr = ovr
    p.pot = utils.calcPOT(p.ovr, p.age)
    p.draft_number = draft_num
    p.drafted_by = draft_team
    p.team = team.name
    p.value = ovr * 1000
    p.careergoals = 0
    p.gp = 0
    p.last_game_goals = 0
    p.ovr_delta = 0

    team.roster.append(p)
    print(f"\nCreated {p.full_name} on {team.name}")
    assign_lineups_pipeline()
    p.value = utils.calcvalue(p.ovr, p.age)


def create_prospect():
    fname = input("First name: ").strip()
    lname = input("Last name: ").strip()
    while True:
        try:
            age = int(input("Age: ").strip())
            break
        except ValueError:
            print("invalid age")
    while True:
        try:
            ovr = int(input("OVR: ").strip())
            break
        except ValueError:
            print("invalid ovr")
    while True:
        try:
            retage = int(input("Retirement age: ").strip())
            break
        except ValueError:
            print("invalid age")
    p = player_class.Player()
    p.first_name = fname
    p.last_name = lname
    p.full_name = f"{fname} {lname}"
    p.age = age
    p.ovr = ovr
    p.pot = 0
    p.team = "PROSPECT"
    p.value = ovr * 1000
    p.careergoals = 0
    p.gp = 0
    p.last_game_goals = 0
    p.ovr_delta = 0
    p.retirement_age = retage
    PROSPECT_POOL.append(p)
    print(f"\nCreated prospect {p.full_name}")


# core funcs
def initialize_matchups(league="NHL"):
    global all_matchups
    teams = all_leagues[league]
    all_matchups = []
    for i in range(len(teams)):
        for j in range(i + 1, len(teams)):
            all_matchups.append((teams[i], teams[j]))
            all_matchups.append((teams[j], teams[i]))


def simulate_league_season(league):
    teams = all_leagues[league]
    initialize_matchups(league)
    idx = 0
    while idx < len(all_matchups):
        t1, t2 = all_matchups[idx]
        idx += 1
        update_team_rating(t1)
        update_team_rating(t2)
        goals1, goals2 = match.domatch(t1, t2)
        update_lineup_stats(t1, league)
        update_lineup_stats(t2, league)
        if league == "NHL":
            print(f"{t1.name} {goals1} - {goals2} {t2.name}")


def advance_league_season():
    global all_matchups, next_game_idx, draft_done, season_complete, season_num, pair_count, teams
    league = "NHL"
    import playoff_logic

    league = "NHL"
    record_team_positions(league)
    gen_vet(7)
    playoff_logic.reset_playoffs_state("NHL")
    pair_count = {}
    assign_lineups_pipeline()

    for i in range(len(nhl_teams)):
        for j in range(i + 1, len(nhl_teams)):
            t1 = nhl_teams[i]
            t2 = nhl_teams[j]
            key = tuple(sorted([t1.name, t2.name]))
            pair_count[key] = 0
    season_complete = False

    update_hof()
    trading.settle_pending_cash(teams)

    to_remove = []
    for p in PROSPECT_POOL:
        if p.retired:
            to_remove.append(p)
    for p in to_remove:
        PROSPECT_POOL.remove(p)
    all_players = set()

    for t in (
        nhl_teams
        + ahl_teams
        + eu_teams
        + chl_teams
        + sphl_teams
        + fhl_teams
        + rec1_teams
        + rec2_teams
    ):
        all_players.update(t.roster)
    for t in teams:
        update_team_type(teams)
        reset_season_team_stats(t)
    for p in PROSPECT_POOL:
        all_players.add(p)
    for p in all_players:
        p.advance_season()
        p.last_game_goals = 0
        p.season_goals = 0
    for t in (
        nhl_teams
        + ahl_teams
        + eu_teams
        + chl_teams
        + sphl_teams
        + fhl_teams
        + rec1_teams
        + rec2_teams
    ):
        to_remove = []
        for p in t.roster:
            if p.retired:
                to_remove.append(p)
        for p in to_remove:
            if hasattr(t, "lineup") and p in t.lineup:
                t.lineup.remove(p)
            t.roster.remove(p)
        t.reset_season_stats()

        if t.roster:
            t.rating = sum(p.ovr for p in t.roster) / len(t.roster)
        else:
            t.rating = 0
    for t in nhl_teams:
        while len(t.roster) < 130:
            gen_vet(10)
    assign_lineups_pipeline()
    simulate_league_season("AHL")
    playoff_logic.start_playoffs("AHL", ahl_teams)
    playoff_logic.sim_full_playoffs("AHL", update_team_rating, update_lineup_stats)
    simulate_league_season("EU")
    playoff_logic.start_playoffs("EU", eu_teams)
    playoff_logic.sim_full_playoffs("EU", update_team_rating, update_lineup_stats)
    simulate_league_season("CHL")
    playoff_logic.start_playoffs("CHL", chl_teams)
    playoff_logic.sim_full_playoffs("CHL", update_team_rating, update_lineup_stats)
    simulate_league_season("SPHL")
    playoff_logic.start_playoffs("SPHL", sphl_teams)
    playoff_logic.sim_full_playoffs("SPHL", update_team_rating, update_lineup_stats)
    simulate_league_season("FHL")
    playoff_logic.start_playoffs("FHL", fhl_teams)
    playoff_logic.sim_full_playoffs("FHL", update_team_rating, update_lineup_stats)
    simulate_league_season("REC1")
    playoff_logic.start_playoffs("REC1", rec1_teams)
    playoff_logic.sim_full_playoffs("REC1", update_team_rating, update_lineup_stats)
    simulate_league_season("REC2")
    playoff_logic.start_playoffs("REC2", rec2_teams)
    playoff_logic.sim_full_playoffs("REC2", update_team_rating, update_lineup_stats)
    initialize_matchups("NHL")
    record_team_positions("AHL")
    record_team_positions("EU")
    record_team_positions("CHL")
    record_team_positions("SPHL")
    record_team_positions("FHL")
    record_team_positions("REC1")
    record_team_positions("REC2")

    next_game_idx = 0
    draft_done = False
    season_complete = False
    season_num += 1
    for p in PROSPECT_POOL:
        if p.age == 18:
            p.pot = utils.calcPOT(p.ovr, p.age)


def main():
    import playoff_logic

    playoff_logic.playoffs_complete = False
    global playoffs_active, playoff_series, playoff_round, playoff_teams, playoff_bracket
    global pair_count
    global red_wings, next_game_idx, draft_done, season_complete, season_num, counter
    red_wings = nhl_teams[0]
    run_initial_drafts()
    assign_lineups_pipeline()
    for t in (
        nhl_teams
        + ahl_teams
        + eu_teams
        + chl_teams
        + sphl_teams
        + fhl_teams
        + rec1_teams
        + rec2_teams
    ):
        t.reset_season_stats()
    gen_vet(90)
    assign_lineups_pipeline()
    simulate_league_season("AHL")
    playoff_logic.start_playoffs("AHL", ahl_teams)
    playoff_logic.sim_full_playoffs("AHL", update_team_rating, update_lineup_stats)
    simulate_league_season("EU")
    playoff_logic.start_playoffs("EU", eu_teams)
    playoff_logic.sim_full_playoffs("EU", update_team_rating, update_lineup_stats)
    simulate_league_season("CHL")
    playoff_logic.start_playoffs("CHL", chl_teams)
    playoff_logic.sim_full_playoffs("CHL", update_team_rating, update_lineup_stats)
    simulate_league_season("SPHL")
    playoff_logic.start_playoffs("SPHL", sphl_teams)
    playoff_logic.sim_full_playoffs("SPHL", update_team_rating, update_lineup_stats)
    simulate_league_season("FHL")
    playoff_logic.start_playoffs("FHL", fhl_teams)
    playoff_logic.sim_full_playoffs("FHL", update_team_rating, update_lineup_stats)
    simulate_league_season("REC1")
    playoff_logic.start_playoffs("REC1", rec1_teams)
    playoff_logic.sim_full_playoffs("REC1", update_team_rating, update_lineup_stats)
    simulate_league_season("REC2")
    playoff_logic.start_playoffs("REC2", rec2_teams)
    playoff_logic.sim_full_playoffs("REC2", update_team_rating, update_lineup_stats)
    initialize_matchups("NHL")
    record_team_positions("AHL")
    record_team_positions("EU")
    record_team_positions("CHL")
    record_team_positions("SPHL")
    record_team_positions("FHL")
    record_team_positions("REC1")
    record_team_positions("REC2")
    while True:
        for t in teams:
            update_team_rating(t)
        assign_lineups_pipeline()
        print_season_status(teams)
        print("=" * 60)
        print("1  - Simulate next match round")
        print("2  - Simulate full remaining season")
        print("3  - View standings")
        print("4  - View Red Wings roster")
        print("5  - View all players with NHL experience")
        print("6  - View Red Wings lineup")
        print("7  - Draft")
        print("8  - Quit")
        print("9  - Advance season")
        print("10 - Change player sort")
        print("11 - Team info")
        print("12 - Auto simulate seasons")
        print("13 - Create player")
        print("14 - View all players without NHL experience")
        print("15 - Simulate seasons with auto draft")
        print("16 - Hall of Fame")
        print("17 - Create prospect")
        print("18 - Print created prospects")
        print("19 - View any team roster")
        print("20 - View any team lineup")
        print("21 - Player search")
        print("22 - Save game")
        print("23 - Load game")
        print("24 - View players by league")
        print("25 - Mega analysis")
        print("26 - Display affiliation")
        print("27 - View playoff bracket")
        print("28 - View league info")
        print("=" * 60)
        option = input("Choose an option: ").strip()
        rounds = 7
        import playoff_logic
        import match

        league = "NHL"
        state = playoff_logic.get_state(league)
        if option == "1":
            if not playoff_logic.get_state("NHL")["complete"]:
                counter = counter + 1

                if state["playoffs_active"]:
                    playoff_logic.sim_playoff_round_step(
                        league, update_team_rating, update_lineup_stats
                    )

                    if playoff_logic.playoffs_finished(league):
                        print("Playoffs complete.")
                        season_complete = True
                    continue
                if "pair_count" not in globals() or season_complete:
                    pair_count = {}
                    for i in range(len(nhl_teams)):
                        for j in range(i + 1, len(nhl_teams)):
                            t1 = nhl_teams[i]
                            t2 = nhl_teams[j]
                            key = tuple(sorted([t1.name, t2.name]))
                            pair_count[key] = 0
                if counter > 62:
                    season_complete = True
                if season_complete and not state["playoffs_active"]:
                    print("Regular season complete. Starting playoffs.")
                    playoff_logic.start_playoffs(league, nhl_teams)
                    continue
                games_this_tick = 0
                MAX_GAMES = 16
                used = set()

                for i in range(len(nhl_teams)):
                    t1 = nhl_teams[i]
                    if t1 in used:
                        continue
                    for j in range(len(nhl_teams)):
                        t2 = nhl_teams[j]
                        if t1 == t2 or t2 in used:
                            continue
                        key = tuple(sorted([t1.name, t2.name]))

                        if pair_count.get(key, 0) >= 2:
                            continue
                        update_team_rating(t1)
                        update_team_rating(t2)

                        goals1, goals2 = match.domatch(t1, t2)

                        update_lineup_stats(t1, "NHL")
                        update_lineup_stats(t2, "NHL")

                        print(f"{t1.name} {goals1} - {goals2} {t2.name}")

                        pair_count[key] = pair_count.get(key, 0) + 1

                        used.add(t1)
                        used.add(t2)

                        games_this_tick += 1
                        break
                    if games_this_tick >= MAX_GAMES:
                        break
                season_complete = all(v >= 32 for v in pair_count.values())

                if season_complete and not state["playoffs_active"]:
                    print("Regular season finished. Starting playoffs.")
                    playoff_logic.start_playoffs(league, nhl_teams)
            if state["complete"]:
                print("all games complete")
        elif option == "2":
            if not playoff_logic.get_state("NHL")["complete"]:

                import playoff_logic
                import match

                league = "NHL"
                state = playoff_logic.get_state(league)

                if "pair_count" not in globals() or not pair_count:
                    pair_count = {}

                    for i in range(len(nhl_teams)):
                        for j in range(i + 1, len(nhl_teams)):
                            t1 = nhl_teams[i]
                            t2 = nhl_teams[j]
                            key = tuple(sorted([t1.name, t2.name]))
                            pair_count[key] = 0

                def total_games_played(team):
                    return sum(
                        pair_count.get(tuple(sorted([team.name, t.name])), 0)
                        for t in nhl_teams
                        if t != team
                    )

                while True:
                    all_done = True

                    for i in range(len(nhl_teams)):
                        for j in range(i + 1, len(nhl_teams)):

                            t1 = nhl_teams[i]
                            t2 = nhl_teams[j]
                            key = tuple(sorted([t1.name, t2.name]))

                            if pair_count.get(key, 0) >= 2:
                                continue
                            if (
                                total_games_played(t1) >= 62
                                and total_games_played(t2) >= 62
                            ):
                                continue
                            update_team_rating(t1)
                            update_team_rating(t2)

                            goals1, goals2 = match.domatch(t1, t2)

                            update_lineup_stats(t1, "NHL")
                            update_lineup_stats(t2, "NHL")

                            print(f"{t1.name} {goals1} - {goals2} {t2.name}")

                            pair_count[key] = pair_count.get(key, 0) + 1

                            all_done = False
                            break
                        if not all_done:
                            break
                    if all_done:
                        break
                season_complete = all(pair_count.get(k, 0) >= 2 for k in pair_count)

                if season_complete and not state["playoffs_active"]:
                    print("Regular season finished. Starting playoffs.")
                    playoff_logic.start_playoffs(league, nhl_teams)
                if state["playoffs_active"]:
                    playoff_logic.sim_full_playoffs(
                        league, update_team_rating, update_lineup_stats
                    )
            if option in ("1", "2"):
                state = playoff_logic.get_state("NHL")

                if state["complete"]:
                    print("all games complete")
        elif option == "3":
            print_standings()
        elif option == "4":
            print_roster(red_wings)
        elif option == "5":
            print_all_players()
        elif option == "6":
            print_lineup_stats(red_wings)
        elif option == "7":
            if not playoff_logic.get_state("NHL")["complete"]:
                print("Season not finished")
            else:
                draft.draft(nhl_teams, user_team_name="Red Wings", rounds=rounds)
                assign_lineups_pipeline()
                draft_done = True
        elif option == "8":
            while True:
                rusure = input("are you sure you want to quit? y/n: ")
                if rusure == "y":
                    exit()
                elif rusure == "n":
                    break
                else:
                    print("invalid")
        elif option == "9":

            import playoff_logic

            league = "NHL"
            state = playoff_logic.get_state(league)

            if not season_complete:
                while next_game_idx < len(all_matchups):
                    t1, t2 = all_matchups[next_game_idx]
                    next_game_idx += 1

                    update_team_rating(t1)
                    update_team_rating(t2)

                    goals1, goals2 = match.domatch(t1, t2)

                    print(f"{t1.name} {goals1} - {goals2} {t2.name}")

                    update_lineup_stats(t1, "NHL")
                    update_lineup_stats(t2, "NHL")
                season_complete = True
            if (
                season_complete
                and not state["playoffs_active"]
                and not state["complete"]
            ):
                print("Regular season complete. Starting playoffs.")
                playoff_logic.start_playoffs(league, nhl_teams)
            if state["playoffs_active"]:
                playoff_logic.sim_full_playoffs(
                    league, update_team_rating, update_lineup_stats
                )

            if not draft_done:
                draft.draft(nhl_teams, user_team_name="none", rounds=rounds)
                draft_done = True
            advance_league_season()

            trading.run_trade_phase(teams, "none")

            next_game_idx = 0
            pair_count = {}
            season_complete = False
            counter = 0
        elif option == "10":
            change_sort()
        elif option == "11":
            print_team_info()
        elif option == "12":

            import playoff_logic

            while True:
                try:
                    cycles = int(input("How many seasons? (0 to cancel) ").strip())

                    if cycles == 0:
                        break
                    if cycles < 0:
                        print("must be >= 0")
                        continue
                    break
                except ValueError:
                    print("invalid number")
            if cycles == 0:
                continue
            league = "NHL"

            for _ in range(cycles):

                state = playoff_logic.get_state(league)

                if not season_complete:

                    while next_game_idx < len(all_matchups):
                        t1, t2 = all_matchups[next_game_idx]
                        next_game_idx += 1

                        update_team_rating(t1)
                        update_team_rating(t2)

                        goals1, goals2 = match.domatch(t1, t2)

                        print(f"{t1.name} {goals1} - {goals2} {t2.name}")

                        update_lineup_stats(t1, "NHL")
                        update_lineup_stats(t2, "NHL")
                    season_complete = True
                if (
                    season_complete
                    and not state["playoffs_active"]
                    and not state["complete"]
                ):
                    playoff_logic.start_playoffs(league, nhl_teams)
                if state["playoffs_active"]:
                    playoff_logic.sim_full_playoffs(
                        league, update_team_rating, update_lineup_stats
                    )

                if not draft_done:
                    draft.draft(nhl_teams, user_team_name="Red Wings", rounds=rounds)
                    draft_done = True

                trading.run_trade_phase(nhl_teams, user_team_name="none")
                counter = 0
                advance_league_season()
                next_game_idx = 0
        elif option == "13":
            create_player()
        elif option == "14":
            print_all_prospects()
        elif option == "15":

            import playoff_logic

            while True:
                try:
                    cycles = int(input("How many seasons? (0 to cancel) ").strip())

                    if cycles == 0:
                        break
                    if cycles < 0:
                        print("must be >= 0")
                        continue
                    break
                except ValueError:
                    print("invalid number")
            if cycles == 0:
                continue
            league = "NHL"

            for _ in range(cycles):

                state = playoff_logic.get_state(league)

                if not season_complete:

                    while next_game_idx < len(all_matchups):
                        t1, t2 = all_matchups[next_game_idx]
                        next_game_idx += 1

                        update_team_rating(t1)
                        update_team_rating(t2)

                        goals1, goals2 = match.domatch(t1, t2)

                        print(f"{t1.name} {goals1} - {goals2} {t2.name}")

                        update_lineup_stats(t1, "NHL")
                        update_lineup_stats(t2, "NHL")
                    season_complete = True
                if (
                    season_complete
                    and not state["playoffs_active"]
                    and not state["complete"]
                ):
                    playoff_logic.start_playoffs(league, nhl_teams)
                if state["playoffs_active"]:
                    playoff_logic.sim_full_playoffs(
                        league, update_team_rating, update_lineup_stats
                    )

                if not draft_done:
                    draft.draft(nhl_teams, user_team_name="none", rounds=rounds)
                    draft_done = True

                trading.run_trade_phase(nhl_teams, user_team_name="none")
                counter = 0
                advance_league_season()
                next_game_idx = 0
        elif option == "16":
            print_hof()
        elif option == "17":
            create_prospect()
        elif option == "18":
            print_prospects()
        elif option == "19":
            view_any_team_roster()
        elif option == "20":
            view_any_team_lineup()
        elif option == "21":
            search_players()
        elif option == "22":
            confirm = (
                input("Are you sure you want to save the game? (y/n): ").strip().lower()
            )
            while confirm not in ("y", "n"):
                confirm = input("Invalid input. Enter y or n: ").strip().lower()
            if confirm == "y":
                save_game()
        elif option == "23":
            confirm = (
                input("Are you sure you want to load the game? (y/n): ").strip().lower()
            )
            while confirm not in ("y", "n"):
                confirm = input("Invalid input. Enter y or n: ").strip().lower()
            if confirm == "y":
                load_game()
        elif option == "24":
            choice_league = (
                input("League (NHL/AHL/EU/CHL/SPHL/FHL/REC1/REC2): ").strip().lower()
            )

            view_all_players_in_choice(choice_league, sort_attr)
        elif option == "25":
            mega_analysis()
        elif option == "26":
            globalvars.print_affiliation()
        elif option == "27":

            import playoff_logic

            leagues = ["NHL", "AHL", "EU", "CHL", "SPHL", "FHL", "REC1", "REC2"]

            league = input(f"eague (NHL/AHL/EU/CHL/SPHL/FHL/REC1/REC2): ").upper()

            state = playoff_logic.get_state(league)

            if not state or not state["playoff_bracket"]:
                print("No playoff data available.")
                continue

            def fmt_team(name, width=18):
                name = name[:width]
                return name.ljust(width)

            def fmt_series(s):
                t1 = fmt_team(f"{s['team1'].name} ({s.get('seed1', '?')})")
                t2 = fmt_team(f"{s['team2'].name} ({s.get('seed2', '?')})")
                return f"{t1} {s['wins1']} - {s['wins2']} {t2}"

            rounds = state["playoff_bracket"]

            print(f"\n=== {league} PLAYOFF BRACKET ===\n")

            max_rows = max(len(r) for r in rounds)
            col_width = 38

            for i in range(max_rows):
                line = []

                for r in range(len(rounds)):
                    if i < len(rounds[r]):
                        cell = fmt_series(rounds[r][i])
                        line.append(cell.ljust(col_width))
                print(" | ".join(line))
        elif option == "28":
            valid_leagues = ["nhl", "ahl", "eu", "chl", "sphl", "fhl", "rec1", "rec2"]

            l_choice = (
                input("League (NHL/AHL/EU/CHL/SPHL/FHL/REC1/REC2): ").strip().lower()
            )

            if l_choice not in valid_leagues:
                print("Invalid league selected.")
            else:
                calculate_league_stats(l_choice)


if __name__ == "__main__":
    main()
