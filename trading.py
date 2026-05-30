import sys
from utils import suffex

sys.stdout.reconfigure(encoding="utf-8")

trading_list = []
trades_log = []

MAX_SALES = 5
REBUILD_BIAS = 1.35


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


class Trade:
    def __init__(self, seller, buyer, player):
        self.new_t = buyer.name
        self.new_t_type = getattr(buyer, "team_type", "unknown")
        self.og_t_type = getattr(seller, "team_type", "unknown")
        self.original_t = seller.name
        self.player_name = player.full_name
        self.player_age = player.age
        self.player_ovr = player.ovr
        self.player_value = player.value
        self.draft_pos = player.draft_number
        self.draft_round = ((player.draft_number - 1) // 32 + 1) if player.draft_number else 0

    def __str__(self):
        return (
            f"{self.player_name[:24]:<24} | age: {self.player_age:>2} | "
            f"💪{ovr_color(self.player_ovr)} | "
            f"{self.draft_round}{suffex(self.draft_round)} #{self.draft_pos:<3} | "
            f"💰{self.player_value:<3} | "
            f"{self.original_t[:12]:<12} -> {self.new_t[:12]:<12} | "
            f"{self.og_t_type} -> {self.new_t_type}"
        )


def team_type(team, teams):
    avg = sum(p.ovr for p in team.roster) / len(team.roster) if team.roster else 0

    all_avg = sorted(
        sum(p.ovr for p in t.roster) / len(t.roster) if t.roster else 0
        for t in teams
    )

    low = all_avg[len(all_avg) // 3]
    high = all_avg[(2 * len(all_avg)) // 3]

    if avg < low:
        return "rebuilding"
    if avg < high:
        return "balanced"
    return "contender"


def rebuild_score(p):
    return (100 - p.age) * 10 * REBUILD_BIAS + p.ovr * 0.5 + (100 - p.value)


def contender_score(p):
    return p.ovr * 5


def score(ttype, p):
    return rebuild_score(p) if ttype == "rebuilding" else contender_score(p)


def allowed_sell(ttype, age):
    if ttype == "rebuilding":
        return age >= 27
    if ttype == "contender":
        return age < 26
    return 26 <= age <= 28


def allowed_buy(ttype, age):
    if ttype == "rebuilding":
        return age < 26
    if ttype == "contender":
        return age > 28
    return 26 <= age <= 28


def generate_market(teams):
    global trading_list
    trading_list = [
        (p, t)
        for t in teams
        for p in t.roster
        if p.value > 70 and not getattr(p, "retired", False)
    ]


def execute(buyer, seller, player):
    value = int(player.value)

    if buyer.cash < value:
        return False

    buyer.add_player(player)
    seller.remove_player(player)

    buyer.cash -= value
    buyer.cash = int(buyer.cash)

    if not hasattr(seller, "pending_cash"):
        seller.pending_cash = 0

    seller.pending_cash += value

    seller.season_sales = getattr(seller, "season_sales", 0) + 1
    buyer.season_buys = getattr(buyer, "season_buys", 0) + 1

    trades_log.append(Trade(seller, buyer, player))

    if (player, seller) in trading_list:
        trading_list.remove((player, seller))

    return True


def settle_pending_cash(teams):
    for t in teams:
        pending_cash = getattr(t, "pending_cash", 0)
        t.cash = int(t.cash + pending_cash)
        t.pending_cash = 0


def buy(team, teams, user_team=None):
    best = None
    ttype = team_type(team, teams)

    for p, seller in trading_list:
        if seller == team:
            continue

        if getattr(seller, "season_sales", 0) >= MAX_SALES:
            continue

        if not allowed_sell(getattr(seller, "team_type", "balanced"), p.age):
            continue

        if not allowed_buy(ttype, p.age):
            continue

        value = int(p.value)

        if ttype == "rebuilding" and value > team.cash:
            continue

        s = score(ttype, p)

        if not best or s > best[0]:
            best = (s, p, seller)

    if not best:
        return False

    _, p, seller = best

    if user_team and (team == user_team or seller == user_team):
        print("\n=== TRADE OFFER ===")
        print(f"{team.name} -> {seller.name}")
        print(f"{p.full_name} | OVR {p.ovr} | AGE {p.age} | Value {p.value}")

        if input("Accept? (y/n): ").lower() != "y":
            return False

    return execute(team, seller, p)


def run_trade_phase(teams, user_team_name="Red Wings"):
    global trading_list, trades_log

    trading_list = []
    trades_log = []

    team_stats = {}

    for t in teams:
        t.season_buys = 0
        t.season_sales = 0
        t._start_cash = int(t.cash)
        t.pending_cash = getattr(t, "pending_cash", 0)
        team_stats[t.name] = {"buys": 0, "sales": 0}

    generate_market(teams)

    user_team = next(
        (t for t in teams if t.name.lower() == user_team_name.lower()), None
    )

    order = sorted(teams, key=lambda t: (t.points, t.gdiff, t.gf), reverse=True)

    changed = True
    it = 0

    while changed and it < 10:
        changed = False
        it += 1

        for t in order:
            if buy(t, teams, user_team):
                changed = True

    for tr in trades_log:
        team_stats[tr.new_t]["buys"] += 1
        team_stats[tr.original_t]["sales"] += 1

    settle_pending_cash(teams)

    print("\n=== TEAM TRADE SUMMARY ===\n")

    for t in teams:
        stats = team_stats[t.name]
        net_cash = int(t.cash - t._start_cash)

        print(
            f"{t.name:<20} | Buys: {stats['buys']:<3} "
            f"| Sales: {stats['sales']:<3} "
            f"| Net Cash: {net_cash:+}"
        )

    print("\n=== TRADES COMPLETED ===")

    for tr in sorted(trades_log, key=lambda x: x.player_value, reverse=True):
        print(tr)
