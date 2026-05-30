import random

def domatch(team1, team2, update_standings=True):
    min_rating = 1e-3

    r1 = team1.rating if team1.rating > 0 else min_rating
    r2 = team2.rating if team2.rating > 0 else min_rating

    r = random.random()

    if r < 0.15:
        base_goals = random.gauss(8, 2.5)
    elif r < 0.30:
        base_goals = random.gauss(3.5, 1.2)
    else:
        base_goals = random.gauss(6, 1.5)

    rating_factor = (r1 / r2) ** 10

    expected_goals1 = base_goals * (rating_factor / (1 + rating_factor))
    expected_goals2 = base_goals - expected_goals1

    goals_team1 = max(0, int(random.gauss(expected_goals1, 1.4)))
    goals_team2 = max(0, int(random.gauss(expected_goals2, 1.4)))

    if random.random() < 0.1:
        goals_team1 += random.randint(2, 5)

    if random.random() < 0.1:
        goals_team2 += random.randint(2, 5)

    if goals_team1 == goals_team2:
        if goals_team1 == 0:
            goals_team1 = 1
        else:
            if random.random() < 0.6:
                goals_team1 += 1
            else:
                goals_team2 += 1

    def assign_goals(team, goals, exponent=4):
        if not team.lineup:
            return

        for p in team.lineup:
            p.last_game_goals = 0

        if goals <= 0:
            return

        weights = [p.ovr ** exponent for p in team.lineup]
        total_weight = sum(weights)

        if total_weight <= 0:
            return

        probs = [w / total_weight for w in weights]

        for _ in range(goals):
            r = random.random()
            cumulative = 0
            for i, prob in enumerate(probs):
                cumulative += prob
                if r <= cumulative:
                    team.lineup[i].last_game_goals += 1
                    break

    assign_goals(team1, goals_team1)
    assign_goals(team2, goals_team2)

    if update_standings:
        for t in (team1, team2):
            t.last10 = getattr(t, "last10", [])

        team1.gf += goals_team1
        team2.gf += goals_team2

        team1.ga += goals_team2
        team2.ga += goals_team1

        team1.gdiff = team1.gf - team1.ga
        team2.gdiff = team2.gf - team2.ga

        if goals_team1 > goals_team2:
            team1.wins += 1
            team2.losses += 1
            team1.points += 2

            team1.last10.append("W")
            team2.last10.append("L")

        else:
            team2.wins += 1
            team1.losses += 1
            team2.points += 2

            team2.last10.append("W")
            team1.last10.append("L")

        team1.last10 = team1.last10[-10:]
        team2.last10 = team2.last10[-10:]

    return goals_team1, goals_team2
