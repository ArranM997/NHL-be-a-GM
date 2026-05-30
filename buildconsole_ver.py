import sys
import subprocess
import shutil
import os

version = input("Enter version: ").strip()

exe_name = f"NHL be a GM v{version}"

subprocess.run([
    sys.executable, "-m", "PyInstaller",
    "--onefile",
    "--icon=logo.ico",
    "--name", exe_name,
    "console_ver.py"
])

print("Build complete")
