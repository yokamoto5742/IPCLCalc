import subprocess

from scripts.version_manager import update_version


def build_executable():
    new_version = update_version()
    subprocess.run([
        "pyinstaller",
        "--name=IPCLCalc",
        "--windowed",
        "--icon=assets/app.ico",
        "--add-data", "utils/config.ini:.",
        "main.py"
    ])

    print(f"Executable built successfully. Version: {new_version}")
    return new_version


if __name__ == "__main__":
    build_executable()
