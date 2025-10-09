import logging
import os
from pathlib import Path

from playwright.sync_api import sync_playwright

from service.auth_service import AuthService
from service.browser_manager import BrowserManager
from service.csv_handler import CSVHandler
from service.lens_calculator_service import LensCalculatorService
from service.patient_service import PatientService
from service.patient_workflow_executor import PatientWorkflowExecutor
from service.save_service import SaveService
from utils.config_manager import load_config, load_environment_variables
from widgets.progress_window import ProgressWindow

logger = logging.getLogger(__name__)


class IPCLOrderAutomation:
    def __init__(self):
        load_environment_variables()
        config = load_config()

        # ディレクトリ設定
        self.csv_dir = Path(config.get('Paths', 'csv_dir'))
        self.calculated_dir = Path(config.get('Paths', 'calculated_dir'))
        self.pdf_dir = self.csv_dir / 'pdf'
        self.pdf_dir.mkdir(exist_ok=True)
        logger.info(f"PDFダウンロード先: {self.pdf_dir}")

        base_url = config.get('URL', 'base_url')
        email = os.getenv('EMAIL')
        password = os.getenv('PASSWORD')
        headless = config.getboolean('Settings', 'headless')

        self.progress_window = ProgressWindow()
        self.csv_handler = CSVHandler()
        self.browser_manager = BrowserManager(headless)

        auth_service = AuthService(base_url, email, password)
        patient_service = PatientService()
        lens_calculator_service = LensCalculatorService()
        save_service = SaveService(self.pdf_dir, self.calculated_dir)

        self.workflow_executor = PatientWorkflowExecutor(
            auth_service,
            patient_service,
            lens_calculator_service,
            save_service,
            self.progress_window,
        )
        self.save_service = save_service

    def _read_csv_data(self, csv_path: Path) -> list[dict]:
        self.progress_window.update(f"CSVファイルを読み込み中...\n{csv_path.name}")
        all_data = self.csv_handler.read_csv_file(csv_path)
        self.progress_window.update(f"{len(all_data)}件のデータを読み込みました")
        return all_data

    def _process_single_record(self, idx: int, total: int, data: dict) -> bool:
        logger.info(f"[{idx}/{total}件目を処理中…]")
        logger.info(f"  患者ID: {data['id']}, 名前: {data['name']}, 眼: {data['eye']}")
        self.progress_window.update(
            f"[{idx}/{total}件目を処理中…]\n患者ID: {data['id']}\n名前: {data['name']}\n眼: {data['eye']}"
        )

        with sync_playwright() as p:
            browser = self.browser_manager.create_browser(p)
            context = self.browser_manager.create_context(browser)
            page = self.browser_manager.create_page(context)

            try:
                save_success, _ = self.workflow_executor.execute(page, idx, total, data)
                return save_success

            except Exception as e:
                error_msg = f"エラーが発生しました: {e}"
                logger.exception(error_msg)
                self.progress_window.update(f"[ERROR] {error_msg}")
                return False

            finally:
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

        logger.info(f"処理完了: {csv_path.name}")

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
