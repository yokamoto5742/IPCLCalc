import os
import subprocess
import sys

from pathlib import Path
from scripts.version_manager import update_version


def get_playwright_browsers_path():
    """Playwrightのブラウザインストールパスを取得"""
    # 環境変数をチェック
    env_path = os.environ.get('PLAYWRIGHT_BROWSERS_PATH')
    if env_path and os.path.exists(env_path):
        return env_path

    # Windowsのデフォルトパス
    default_path = Path.home() / 'AppData' / 'Local' / 'ms-playwright'
    if default_path.exists():
        return str(default_path)

    print("[ERROR] Playwrightブラウザが見つかりません")
    return None


def build_executable():
    """実行ファイルをビルド"""
    new_version = update_version()

    playwright_browsers_path = get_playwright_browsers_path()

    command = [
        "pyinstaller",
        "--name=IPCLCalc",
        "--windowed",
        "--icon=assets/app.ico",
        "--add-data", "utils/config.ini;",
        "--hidden-import", "playwright",
        "--hidden-import", "playwright.sync_api",
        "--collect-all", "playwright",
    ]

    if playwright_browsers_path and os.path.exists(playwright_browsers_path):
        print(f"[OK] Playwrightブラウザを含めます: {playwright_browsers_path}")

        chromium_dirs = [d for d in os.listdir(playwright_browsers_path)
                         if d.startswith('chromium-')]

        if chromium_dirs:
            chromium_dir = os.path.join(playwright_browsers_path, chromium_dirs[0])
            command.extend([
                "--add-data",
                f"{chromium_dir};playwright/driver/package/.local-browsers/{chromium_dirs[0]}"
            ])
            print(f"[OK] {chromium_dirs[0]} を含めました")
        else:
            print("[ERROR] chromiumディレクトリが見つかりません")
            return None

    command.append("main.py")

    print("\nPyInstallerを実行中...")
    subprocess.run(command, check=True)

    print(f"\n[OK] 実行ファイルのビルドが完了しました。バージョン: {new_version}")

    return new_version


if __name__ == "__main__":
    print("=" * 60)
    print("IPCLCalc 実行ファイルビルドスクリプト")
    print("=" * 60)
    print()

    try:
        subprocess.run(
            [sys.executable, "-c", "from playwright.sync_api import sync_playwright"],
            check=True,
            capture_output=True
        )
        print("[OK] Playwrightがインストールされています")
    except subprocess.CalledProcessError:
        print("[ERROR] エラー: Playwrightがインストールされていません。")
        sys.exit(1)

    result = build_executable()
    if result is None:
        sys.exit(1)
