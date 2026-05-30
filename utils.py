import random
import math


def pot_conv(POT):
    POT = POT + 4
    if POT >= 91:
        return "Franchise"
    elif 84 <= POT <= 90:
        return "Elite"
    elif 79 <= POT <= 83:
        return "NHL"
    elif 73 <= POT <= 78:
        return "NHL dpth"
    elif 68 <= POT <= 72:
        return "AHL"
    elif 65 <= POT <= 67:
        return "AHL dpth"
    elif 61 <= POT <= 64:
        return "EU"
    elif 58 <= POT <= 60:
        return "EU dpth"
    elif 55 <= POT <= 57:
        return "CHL"
    elif POT == 54:
        return "CHL dpth"
    elif POT == 53:
        return "SPHL"
    elif POT == 52:
        return "SPHL dpth"
    elif POT == 51:
        return "Rec1"
    else:
        return "Rec2"



def genovr():
    r = random.random()

    if r < 0.0009:
        return random.randint(74, 88)
    elif r < 0.01:
        return random.randint(69, 73)
    elif r < 0.04:
        return random.randint(65, 68)
    elif r < 0.12:
        return random.randint(62, 64)
    elif r < 0.28:
        return random.randint(59, 61)
    elif r < 0.52:
        return random.randint(57, 58)
    elif r < 0.78:
        return random.randint(55, 56)
    else:
        return random.randint(53, 54)


def _clean_num(x):
    if isinstance(x, complex):
        x = x.real
    return float(x)


def calcvalue(ovr, age):
    ovr = _clean_num(ovr)
    age = _clean_num(age)

    youth_bonus = max(0.6, 1 + (26 - age) * 0.028)

    ovr_factor = (ovr / 100) ** 2.3

    value = ovr_factor * youth_bonus * 200

    if isinstance(value, complex):
        value = value.real

    return max(1, int(value))


def calcPOT(ovr, age):
    ovr = _clean_num(ovr)
    age = _clean_num(age)

    remaining = 0.0

    if age < 20:
        remaining += (20 - age) * 3.5
    if age < 23:
        remaining += (min(23, 23) - max(age, 20)) * 2
    if age < 27:
        remaining += (min(27, 27) - max(age, 23)) * 1
    if age < 31:
        remaining += (min(31, 31) - max(age, 27)) * -0.5
    if age < 33:
        remaining += (min(33, 33) - max(age, 31)) * -1.5

    pot = round(ovr + remaining)
    return min(99, max(0, int(pot)))


def suffex(n):
    n = int(n)
    if 11 <= n % 100 <= 13:
        return "th"
    return {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")


def format_ordinal(n):
    return f"{n}{suffex(n)}"


if __name__ == "__main__":
    print(calcvalue(65, 18))
    print(calcvalue(80, 35))
    print(calcvalue(76, 29))
    print(calcvalue(88, 18))
    print("="*30)
    print(calcPOT(54, 18))
    print(pot_conv(87))
    print(pot_conv(calcPOT(68, 19)))
