import colorama
from colorama import Fore, Style


class Team:
    def __init__(self, name):
        self.name = name
        self.last10 = []
        self.roster = []
        self.lineup = []
        self.playoffs = 0

        self.rating = 0

        self.wins = 0
        self.losses = 0
        self.points = 0

        self.gf = 0
        self.ga = 0
        self.gdiff = 0

        self.cash = 200
        self.pending_cash = 0
        self.team_type = "none"

        self.playoff_streak = 0
        self.playoff_drought = 0
        self.in_playoffs = False

    def can_afford(self, amount):
        return self.cash >= amount

    def spend_cash(self, amount):
        if amount < 0:
            return False
        if self.cash < amount:
            return False
        self.cash -= amount
        return True

    def add_cash(self, amount):
        if amount < 0:
            return False
        self.cash += amount
        return True

    def add_player(self, player):
        player.team = self.name
        self.roster.append(player)
        self.update_lineup()

    def remove_player(self, player):
        if player in self.roster:
            self.roster.remove(player)
            player.team = "null"
            self.update_lineup()

    def update_lineup(self):
        self.lineup = sorted(self.roster, key=lambda p: p.ovr, reverse=True)[:18]

        if self.lineup:
            self.rating = sum(p.ovr for p in self.lineup) / len(self.lineup)
        else:
            self.rating = 0

    def record_game(self, goals_for, goals_against):
        self.gf += goals_for
        self.ga += goals_against
        self.gdiff = self.gf - self.ga

        if goals_for > goals_against:
            self.wins += 1
            self.points += 2
        else:
            self.losses += 1

    def reset_season_stats(self):
        self.wins = 0
        self.losses = 0
        self.points = 0
        self.gf = 0
        self.ga = 0
        self.gdiff = 0

    def advance_season(self):
        for player in self.roster:
            player.advance_season()
        self.update_lineup()
        self.reset_season_stats()

    def __str__(self):
        gd_value = self.gdiff
        gd_raw = f"{gd_value:+4d}"  # ALWAYS 4 chars: "+  6", "- 12", "   0" style

        if gd_value > 0:
            gd_str = f"{Fore.GREEN}{gd_raw}{Style.RESET_ALL}"
        elif gd_value < 0:
            gd_str = f"{Fore.RED}{gd_raw}{Style.RESET_ALL}"
        else:
            gd_str = f"{Fore.YELLOW}{gd_raw}{Style.RESET_ALL}"

        return (
            f"{self.name:<20} |"
            f"{self.rating:>5.1f} | "
            f"{self.wins:>3}-{self.losses:<3} |"
            f"{self.points:>3} | "
            f"{self.gf:>3} | "
            f"{self.ga:>3} | "
            f"{gd_str} | "
            f"{self.team_type:<12} | "
            f"{self.cash:>4}"
        )
