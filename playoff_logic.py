import match

playoff_data = {}


def reset_playoffs_state(league):
    playoff_data[league] = {
        "playoff_mode": False,
        "playoffs_active": False,
        "playoff_round": 0,
        "playoff_series": [],
        "playoff_teams": [],
        "playoff_bracket": [],
        "champion": None,
        "complete": False,
    }


def get_state(league):
    if league not in playoff_data:
        reset_playoffs_state(league)
    return playoff_data[league]


def start_playoffs(league, teams):
    state = get_state(league)

    state["playoff_mode"] = True
    state["champion"] = None
    state["complete"] = False

    standings = sorted(
        teams,
        key=lambda x: (x.points, x.gdiff, x.gf),
        reverse=True
    )

    playoff_teams = []

    for i, t in enumerate(standings[:16]):
        t.playoffs = getattr(t, "playoffs", 0) + 1

        t.playoff_streak = getattr(t, "playoff_streak", 0) + 1
        t.playoff_drought = 0

        playoff_teams.append({"team": t, "seed": i + 1})

    playoff_set = {p["team"] for p in playoff_teams}
    non_playoff = [t for t in teams if t not in playoff_set]

    for t in non_playoff:
        t.playoff_drought = getattr(t, "playoff_drought", 0) + 1
        t.playoff_streak = 0

    pairs = []
    for i in range(8):
        pairs.append((playoff_teams[i], playoff_teams[15 - i]))

    playoff_series = []

    for a, b in pairs:
        playoff_series.append(
            {
                "team1": a["team"],
                "team2": b["team"],
                "seed1": a["seed"],
                "seed2": b["seed"],
                "wins1": 0,
                "wins2": 0,
                "games": [],
            }
        )

    state["playoff_series"] = playoff_series
    state["playoff_bracket"] = [playoff_series]
    state["playoff_round"] = 1
    state["playoffs_active"] = True
    state["playoff_teams"] = playoff_teams


def sim_playoff_round_step(league, update_team_rating, update_lineup_stats, verbose=False):
    state = get_state(league)

    if not state["playoffs_active"]:
        return False

    active_series = 0

    for series in state["playoff_series"]:
        if series["wins1"] >= 4 or series["wins2"] >= 4:
            continue

        active_series += 1

        t1 = series["team1"]
        t2 = series["team2"]

        g1, g2 = match.domatch(t1, t2, update_standings=False)

        update_lineup_stats(t1, league)
        update_lineup_stats(t2, league)

        if g1 > g2:
            series["wins1"] += 1
        else:
            series["wins2"] += 1

        series["games"].append((g1, g2))

        if league == "NHL" or verbose:
            print(
                f"{t1.name} ({series['seed1']}) "
                f"{series['wins1']} - {series['wins2']} "
                f"({series['seed2']}) {t2.name} | {g1}-{g2}"
            )

    if active_series == 0:
        advance_round(league)

    return True


def sim_full_playoffs(league, update_team_rating, update_lineup_stats):
    state = get_state(league)

    while state["playoffs_active"]:
        sim_playoff_round_step(league, update_team_rating, update_lineup_stats)


def advance_round(league):
    state = get_state(league)

    winners = []

    for series in state["playoff_series"]:
        if series["wins1"] >= 4:
            winners.append({"team": series["team1"], "seed": series["seed1"]})
        else:
            winners.append({"team": series["team2"], "seed": series["seed2"]})

    if len(winners) == 1:
        champion = winners[0]["team"]
        champion.titles = getattr(champion, "titles", 0) + 1

        state["champion"] = champion
        state["playoffs_active"] = False
        state["playoff_mode"] = False
        state["complete"] = True
        return

    winners_sorted = sorted(
        winners,
        key=lambda x: (x["team"].points, x["team"].gdiff, x["team"].gf),
        reverse=True
    )

    new_series = []

    for i in range(len(winners_sorted) // 2):
        new_series.append(
            {
                "team1": winners_sorted[i]["team"],
                "team2": winners_sorted[-(i + 1)]["team"],
                "seed1": winners_sorted[i]["seed"],
                "seed2": winners_sorted[-(i + 1)]["seed"],
                "wins1": 0,
                "wins2": 0,
                "games": [],
            }
        )

    state["playoff_series"] = new_series
    state["playoff_bracket"].append(new_series)
    state["playoff_round"] += 1


def playoffs_finished(league):
    return get_state(league)["complete"]


def get_champion(league):
    return get_state(league)["champion"]
