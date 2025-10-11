import logging
import shutil
from datetime import datetime
from pathlib import Path

from playwright.sync_api import Page

logger = logging.getLogger(__name__)


class SaveService:
    def __init__(self, pdf_dir: Path, calculated_dir: Path):
        self.pdf_dir = pdf_dir
        self.calculated_dir = calculated_dir

    def click_save_pdf_button(self, page: Page, patient_id: str, patient_name: str) -> str:
        frame = page.frame_locator('#calculatorFrame')

        try:
            with page.expect_download() as download_info:
                frame.locator('a:has(i.far.fa-file-pdf)').click()

            download = download_info.value

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            pdf_filename = f"IPCLdata_ID{patient_id}_{timestamp}.pdf"
            pdf_path = self.pdf_dir / pdf_filename

            download.save_as(pdf_path)

            logger.info(f"計算結果のPDFファイルを保存しました: {pdf_path}")
            return str(pdf_path)

        except Exception as e:
            logger.error(f"PDF保存中にエラーが発生しました: {e}")
            raise

    @staticmethod
    def save_input(page: Page):
        frame = page.frame_locator('#calculatorFrame')
        frame.locator('button#btn-save-draft-modal').click()

    @staticmethod
    def save_draft(page: Page) -> bool:
        try:
            save_button = page.locator('button:has-text("下書き保存")')
            save_button.wait_for(state='visible', timeout=2000)

            if not save_button.is_disabled():
                save_button.click()
                page.wait_for_load_state('networkidle')
                return True
            else:
                logger.warning("下書き保存ボタンが無効のため、処理をスキップしました")
                return False
        except Exception as e:
            logger.warning(f"下書き保存をスキップしました: {e}")
            return False

    def move_csv_to_calculated(self, csv_path: Path):
        self.calculated_dir.mkdir(exist_ok=True)

        destination = self.calculated_dir / csv_path.name
        shutil.move(str(csv_path), str(destination))
        logger.info(f"{csv_path.name} を 計算済フォルダに移動しました")

    def move_csv_to_error(self, csv_path: Path, error_dir: Path):
        error_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        base_name = csv_path.stem
        extension = csv_path.suffix
        destination = error_dir / f"{base_name}_error_{timestamp}{extension}"

        shutil.move(str(csv_path), str(destination))
        logger.error(f"{csv_path.name} をエラーフォルダに移動しました: {destination.name}")
