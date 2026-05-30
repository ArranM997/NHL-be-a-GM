import subprocess
import os
import sys
import shutil
import re


def parse_version(name):
    match = re.search(r"v(\d+(?:\.\d+)*)", name)
    if not match:
        return None
    return tuple(map(int, match.group(1).split(".")))


def get_games():
    base = (
        os.path.dirname(sys.executable)
        if getattr(sys, "frozen", False)
        else os.getcwd()
    )

    games = []
    for f in os.listdir(base):
        if f.startswith("NHL be a GM v") and f.endswith(".exe"):
            version = parse_version(f)
            if version:
                games.append((version, f, os.path.join(base, f)))

    games.sort(key=lambda x: x[0], reverse=True)
    return games


def launch(path):
    if shutil.which("wt"):
        subprocess.Popen(["wt", "-w", "maximized", path])
    elif shutil.which("powershell"):
        subprocess.Popen(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                f"Start-Process '{path}' -WindowStyle Maximized",
            ]
        )
    else:
        subprocess.Popen(["cmd", "/c", f'start "" "{path}"'])


def main():
    games = get_games()

    if not games:
        print("No game versions found")
        return

    print("\nAvailable versions:\n")
    for i, (ver, name, _) in enumerate(games, 1):
        print(f"{i}. {name}")

    while True:
        try:
            choice = int(input("\nSelect version to run: ").strip())
            if 1 <= choice <= len(games):
                break
            print("Invalid selection")
        except ValueError:
            print("Enter a number")

    launch(games[choice - 1][2])


if __name__ == "__main__":
    main()
