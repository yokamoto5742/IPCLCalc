import os
import subprocess
import sys

from scripts.version_manager import update_version


def get_playwright_browsers_path():
    """Playwrightのブラウザインストールパスを取得"""
    import os
    from pathlib import Path

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

    # Playwrightブラウザのパスを取得
    playwright_browsers_path = get_playwright_browsers_path()

    # PyInstallerのコマンドを構築
    command = [
        "pyinstaller",
        "--name=IPCLCalc",
        "--windowed",
        "--icon=assets/app.ico",
        "--add-data", "utils/config.ini;utils",
        "--hidden-import", "playwright",
        "--hidden-import", "playwright.sync_api",
        "--collect-all", "playwright",
        "--noconfirm",  # 既存のビルドを上書き
    ]

    # Playwrightブラウザを含める
    # この部分を変更
    if playwright_browsers_path and os.path.exists(playwright_browsers_path):
        print(f"[OK] Playwrightブラウザを含めます: {playwright_browsers_path}")

        # chromium-* ディレクトリを探す
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

    # PyInstallerを実行
    print("\nPyInstallerを実行中...")
    subprocess.run(command, check=True)

    print(f"\n[OK] 実行ファイルのビルドが完了しました。バージョン: {new_version}")
    print("\n配布前の確認事項:")
    print("1. dist/IPCLCalc/IPCLCalc.exe を実行して動作確認")
    print("2. 実行ファイルと同じディレクトリに以下を配置:")
    print("   - csv/ ディレクトリ（処理対象のCSVを格納）")
    print("   - csv/calculated/ ディレクトリ（処理済みCSVを格納）")

    return new_version


if __name__ == "__main__":
    print("=" * 60)
    print("IPCLCalc 実行ファイルビルドスクリプト")
    print("=" * 60)
    print()

    # Playwrightブラウザがインストールされているか確認
    try:
        subprocess.run(
            [sys.executable, "-c", "from playwright.sync_api import sync_playwright"],
            check=True,
            capture_output=True
        )
        print("[OK] Playwrightがインストールされています")
    except subprocess.CalledProcessError:
        print("[ERROR] エラー: Playwrightがインストールされていません。")
        print("以下のコマンドを実行してください:")
        print("  pip install playwright")
        print("  playwright install chromium")
        sys.exit(1)

    result = build_executable()
    if result is None:
        sys.exit(1)
