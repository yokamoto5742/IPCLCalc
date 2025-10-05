import os
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

from service.auth_service import AuthService
from service.csv_handler import CSVHandler
from service.lens_calculator_service import LensCalculatorService
from service.patient_service import PatientService
from service.save_service import SaveService
from utils.config_manager import load_config, load_environment_variables


class IPCLOrderAutomation:
    def __init__(self):

        if getattr(sys, 'frozen', False):
            base_path = Path(sys._MEIPASS)
            playwright_browsers = base_path / 'playwright' / 'driver' / 'package' / '.local-browsers'
            if playwright_browsers.exists():
                os.environ['PLAYWRIGHT_BROWSERS_PATH'] = str(playwright_browsers)
                print(f"[OK] Playwrightブラウザパス設定: {playwright_browsers}")
            else:
                print(f"[WARNING] Playwrightブラウザパスが見つかりません: {playwright_browsers}")

        load_environment_variables()

        config = load_config()

        self.base_url = config.get('URL', 'base_url')
        self.email = os.getenv('EMAIL')
        self.password = os.getenv('PASSWORD')
        self.csv_dir = Path(config.get('Paths', 'csv_dir'))
        self.calculated_dir = Path(config.get('Paths', 'calculated_dir'))
        self.error_dir = Path(config.get('Paths', 'error_dir'))
        self.log_dir = Path(config.get('Paths', 'log_dir'))
        self.headless = config.getboolean('Settings', 'headless')

        # PDFダウンロード先ディレクトリを設定
        self.pdf_dir = self.csv_dir / 'pdf'
        self.pdf_dir.mkdir(exist_ok=True)
        print(f"[OK] PDFダウンロード先: {self.pdf_dir}")

        # サービスの初期化
        self.auth_service = AuthService(self.base_url, self.email, self.password)
        self.csv_handler = CSVHandler()
        self.patient_service = PatientService()
        self.lens_calculator_service = LensCalculatorService()
        self.save_service = SaveService(self.pdf_dir, self.calculated_dir)

    def process_csv_file(self, csv_path: Path):
        """CSVファイルを処理"""
        print(f"\n{'=' * 60}")
        print(f"処理開始: {csv_path.name}")
        print(f"{'=' * 60}")

        print("[OK] CSVファイルを読み込みました")
        data = self.csv_handler.read_csv_file(csv_path)
        print(f"  患者ID: {data['id']}, 名前: {data['name']}")

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)

            # ダウンロード先を指定してコンテキストを作成
            context = browser.new_context(
                accept_downloads=True
            )
            page = context.new_page()

            save_success = False
            pdf_path = None

            try:
                # ログイン
                print("[OK] Webサイトにログインしています...")
                self.auth_service.login(page)

                # 患者情報を入力
                print("[OK] 患者情報を入力しています...")
                self.patient_service.fill_patient_info(page, data)

                # レンズ計算・注文モーダルを開く
                print("[OK] レンズ計算・注文を開いています...")
                self.lens_calculator_service.open_lens_calculator(page)

                # 眼別タブを選択
                print(f"[OK] {data['eye']}タブを選択しています...")
                self.lens_calculator_service.select_eye_tab(page, data['eye'])

                # 誕生日を入力
                print("[OK] 誕生日を入力しています...")
                self.patient_service.fill_birthday(page, data['birthday'])

                # 測定データを入力
                print("[OK] 測定データを入力しています...")
                self.lens_calculator_service.fill_measurement_data(page, data, data['eye'])

                # レンズタイプを選択
                print("[OK] レンズタイプを選択しています...")
                self.lens_calculator_service.select_lens_type(page, data, data['eye'])

                # ATA/WTWデータを入力
                print("[OK] ATA/WTWデータを入力しています...")
                self.lens_calculator_service.fill_ata_wtw_data(page, data, data['eye'])

                # レンズ計算
                print("[OK] レンズ計算を実行しています...")
                self.lens_calculator_service.click_calculate_button(page)

                # PDF保存
                print("[OK] PDFを保存しています...")
                pdf_path = self.save_service.click_save_pdf_button(page, data['id'], data['name'])

                # 入力を保存
                print("[OK] 入力を保存しています...")
                self.save_service.save_input(page)

                # 下書き保存
                print("[OK] 下書き保存しています...")
                save_success = self.save_service.save_draft(page)

                if save_success:
                    print("[OK] 注文の下書きが正常に保存されました")
                    if pdf_path:
                        print(f"[OK] PDF保存先: {pdf_path}")
                else:
                    print("[WARNING] ブラウザを開いたままにします。手動で確認してください。")

            except Exception as e:
                print(f"[ERROR] エラーが発生しました: {e}")
                raise

            finally:
                if save_success:
                    page.wait_for_timeout(2000)
                    browser.close()

        if save_success:
            self.save_service.move_csv_to_calculated(csv_path)

        print(f"{'=' * 60}")
        print(f"処理完了: {csv_path.name}")
        print(f"{'=' * 60}\n")

    def process_all_csv_files(self):
        """すべてのCSVファイルを処理"""
        csv_files = list(self.csv_dir.glob('IPCLdata_*.csv'))

        if not csv_files:
            print("処理するCSVファイルが見つかりませんでした")
            return

        print(f"\n{len(csv_files)}件のCSVファイルを処理します")

        for csv_file in csv_files:
            self.process_csv_file(csv_file)

        print("\nすべてのファイルの処理が完了しました")
        print(f"PDFの保存先: {self.pdf_dir}")
