import random
import utils
import globalvars


class Player:
    def __init__(self):
        self.current_league = "NONE"
        self.full_name = self._gen_name()
        self.team = None
        self.age = random.randint(18, 20)
        self.ovr = utils.genovr()
        self.pot = utils.calcPOT(self.ovr, self.age)
        self.value = utils.calcvalue(self.ovr, self.age)
        self.drafted_by = "UNDRAFTED"

        self.draft_number = 0
        self.draft_round = 0

        self.top6seasons = 0

        self.contract = 2

        self.retired = False
        r = random.random()

        if r < 0.001:
            self.retirement_age = 46
        elif r < 0.011:
            self.retirement_age = 45
        elif r < 0.061:
            self.retirement_age = 44
        elif r < 0.261:
            self.retirement_age = 43
        else:
            self.retirement_age = random.randint(34, 41)

        self.gf = 0
        self.season_goals = 0
        self.last_game_goals = 0

        self.ovr_delta = 0

        self.gp_nhl = 0
        self.careergoals_nhl = 0
        self.gp_ahl = 0
        self.careergoals_ahl = 0
        self.gp_eu = 0
        self.careergoals_eu = 0
        self.gp_chl = 0
        self.careergoals_chl = 0
        self.gp_sphl = 0
        self.careergoals_sphl = 0
        self.gp_fhl = 0
        self.careergoals_fhl = 0
        self.gp_rec1 = 0
        self.careergoals_rec1 = 0
        self.gp_rec2 = 0
        self.careergoals_rec2 = 0

    def update_value(self):
        self.value = utils.calcvalue(self.ovr, self.age)

    def advance_season(self):
        self.develop_player()
        self.update_value()

    def _gen_name(self):
        Fname = random.choice(globalvars.FNAME)
        Lname = random.choice(globalvars.LNAME)
        return f"{Fname} {Lname}"

    def __str__(self):
        return (
            f"{self.full_name} | Age: {self.age} | OVR: {self.ovr} | POT: {self.pot} | Value: {self.value} | OVR Δ: {self.ovr_delta} | "
            f"NHL GP: {self.gp_nhl} CG: {self.careergoals_nhl} | "
            f"AHL GP: {self.gp_ahl} CG: {self.careergoals_ahl} | "
            f"EU GP: {self.gp_eu} CG: {self.careergoals_eu}"
        )

    def develop_player(self):
        if self.retired:
            self.ovr_delta = 0
            return

        prev_ovr = self.ovr

        if self.age < 20:
            self.ovr += random.randint(-1, 8)
        elif self.age < 23:
            self.ovr += random.randint(-2, 6)
        elif self.age < 27:
            self.ovr += random.randint(-3, 5)
        elif self.age < 31:
            self.ovr += random.randint(-4, 3)
        elif self.age < 33:
            self.ovr += random.randint(-5, 2)
        else:
            self.ovr += random.randint(-6, 1)

        self.ovr_delta = self.ovr - prev_ovr
        self.value = utils.calcvalue(self.ovr, self.age)
        self.age += 1

        if self.age > (self.retirement_age - 1):
            self.retired = True
