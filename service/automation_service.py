import logging
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
from widgets.progress_window import ProgressWindow

logger = logging.getLogger(__name__)


class IPCLOrderAutomation:
    def __init__(self):
        self.progress_window = ProgressWindow()

        if getattr(sys, 'frozen', False):
            base_path = Path(sys._MEIPASS)
            playwright_browsers = base_path / 'playwright' / 'driver' / 'package' / '.local-browsers'
            if playwright_browsers.exists():
                os.environ['PLAYWRIGHT_BROWSERS_PATH'] = str(playwright_browsers)
                logger.info(f"Playwrightブラウザパス設定: {playwright_browsers}")
            else:
                logger.warning(f"Playwrightブラウザパスが見つかりません: {playwright_browsers}")

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

        self.pdf_dir = self.csv_dir / 'pdf'
        self.pdf_dir.mkdir(exist_ok=True)
        logger.info(f"PDFダウンロード先: {self.pdf_dir}")

        self.auth_service = AuthService(self.base_url, self.email, self.password)
        self.csv_handler = CSVHandler()
        self.patient_service = PatientService()
        self.lens_calculator_service = LensCalculatorService()
        self.save_service = SaveService(self.pdf_dir, self.calculated_dir)

    def _read_csv_data(self, csv_path: Path) -> list[dict]:
        """CSVファイルを読み込む"""
        self.progress_window.update(f"CSVファイルを読み込み中...\n{csv_path.name}")
        all_data = self.csv_handler.read_csv_file(csv_path)
        self.progress_window.update(f"{len(all_data)}件のデータを読み込みました")
        return all_data

    def _execute_patient_workflow(self, page, idx: int, total: int, data: dict) -> tuple[bool, Path | None]:
        """患者データ処理のワークフローを実行"""
        pdf_path = None

        # ログイン
        self.progress_window.update(f"[{idx}/{total}] Webサイトにログイン中...")
        self.auth_service.login(page)

        # 患者情報を入力
        self.progress_window.update(f"[{idx}/{total}] 患者情報を入力中...")
        self.patient_service.fill_patient_info(page, data)

        # レンズ計算・注文モーダルを開く
        self.progress_window.update(f"[{idx}/{total}] レンズ計算・注文を開いています...")
        self.lens_calculator_service.open_lens_calculator(page)

        # 眼のタブを選択
        self.progress_window.update(f"[{idx}/{total}] {data['eye']}タブを選択中...")
        self.lens_calculator_service.select_eye_tab(page, data['eye'])

        # 誕生日を入力
        self.progress_window.update(f"[{idx}/{total}] 誕生日を入力中...")
        self.patient_service.fill_birthday(page, data['birthday'])

        # 測定データを入力
        self.progress_window.update(f"[{idx}/{total}] 測定データを入力中...")
        self.lens_calculator_service.fill_measurement_data(page, data, data['eye'])

        # レンズタイプを選択
        self.progress_window.update(f"[{idx}/{total}] レンズタイプを選択中...")
        self.lens_calculator_service.select_lens_type(page, data, data['eye'])

        # ATA/WTWデータを入力
        self.progress_window.update(f"[{idx}/{total}] ATA/WTWデータを入力中...")
        self.lens_calculator_service.fill_ata_wtw_data(page, data, data['eye'])

        # レンズ計算
        self.progress_window.update(f"[{idx}/{total}] レンズ計算を実行中...")
        self.lens_calculator_service.click_calculate_button(page)

        # PDF保存
        self.progress_window.update(f"[{idx}/{total}] PDFを保存中...")
        pdf_path = self.save_service.click_save_pdf_button(page, data['id'], data['name'])

        # 入力を保存
        self.progress_window.update(f"[{idx}/{total}] 入力を保存中...")
        self.save_service.save_input(page)

        # 下書き保存
        self.progress_window.update(f"[{idx}/{total}] 下書き保存中...")
        save_success = self.save_service.save_draft(page)

        if save_success:
            self.progress_window.update(f"[{idx}/{total}] 注文の下書きが保存されました")
            if pdf_path:
                logger.info(f"PDF保存先: {pdf_path}")
        else:
            logger.warning("ブラウザを開いたままにします。手動で確認してください。")

        return save_success, pdf_path

    def _process_single_record(self, idx: int, total: int, data: dict) -> bool:
        """単一レコードを処理"""
        logger.info(f"[{idx}/{total}件目を処理中…]")
        logger.info(f"  患者ID: {data['id']}, 名前: {data['name']}, 眼: {data['eye']}")
        self.progress_window.update(
            f"[{idx}/{total}件目を処理中…]\n患者ID: {data['id']}\n名前: {data['name']}\n眼: {data['eye']}"
        )

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            context = browser.new_context(accept_downloads=True)
            page = context.new_page()

            try:
                save_success, _ = self._execute_patient_workflow(page, idx, total, data)
                return save_success

            except Exception as e:
                error_msg = f"エラーが発生しました: {e}"
                logger.exception(error_msg)
                self.progress_window.update(f"[ERROR] {error_msg}")
                return False

            finally:
                page.wait_for_timeout(2000)
                browser.close()

    def process_csv_file(self, csv_path: Path):
        """CSVファイルを処理"""
        logger.info(f"処理開始: {csv_path.name}")

        all_data = self._read_csv_data(csv_path)
        all_success = True

        for idx, data in enumerate(all_data, 1):
            success = self._process_single_record(idx, len(all_data), data)
            if not success:
                all_success = False

        if all_success:
            self.save_service.move_csv_to_calculated(csv_path)

        logger.info(f"{'=' * 60}")
        logger.info(f"処理完了: {csv_path.name}")
        logger.info(f"{'=' * 60}")

    def process_all_csv_files(self):
        csv_files = list(self.csv_dir.glob('IPCLdata_*.csv'))

        if not csv_files:
            logger.warning("処理するCSVファイルが見つかりませんでした")
            return

        self.progress_window.create()

        try:
            logger.info(f"{len(csv_files)}件のCSVファイルを処理します")
            self.progress_window.update(f"{len(csv_files)}件のCSVファイルを処理します")

            for idx, csv_file in enumerate(csv_files, 1):
                logger.info(f"[{idx}/{len(csv_files)}件目を処理中…]")
                self.progress_window.update(f"[{idx}/{len(csv_files)}件目のファイルを処理中…]\n{csv_file.name}")
                self.process_csv_file(csv_file)

            logger.info("すべてのファイルの処理が完了しました")
            logger.info(f"PDFの保存先: {self.pdf_dir}")
            self.progress_window.update(f"すべてのファイルの処理が完了しました\n\nPDFの保存先:\n{self.pdf_dir}")

        finally:
            if self.progress_window.progress_window:
                self.progress_window.progress_window.after(1000, self.progress_window.close)
