import shutil
from datetime import datetime
from pathlib import Path

from playwright.sync_api import Page


class SaveService:
    def __init__(self, pdf_dir: Path, calculated_dir: Path):
        self.pdf_dir = pdf_dir
        self.calculated_dir = calculated_dir

    def click_save_pdf_button(self, page: Page, patient_id: str, patient_name: str) -> str:
        """PDFを保存し、保存先パスを返す"""
        frame = page.frame_locator('#calculatorFrame')

        try:
            # ダウンロードを待機
            with page.expect_download() as download_info:
                frame.locator('a:has(i.far.fa-file-pdf)').click()

            download = download_info.value

            # デバッグ情報を表示
            print(f"[DEBUG] 一時ファイル: {download.path()}")
            print(f"[DEBUG] 推奨ファイル名: {download.suggested_filename}")

            # ファイル名を生成（患者IDと患者名を含む）
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            pdf_filename = f"IPCL_{patient_id}_{patient_name}_{timestamp}.pdf"
            pdf_path = self.pdf_dir / pdf_filename

            # ダウンロードしたファイルを指定先に保存
            download.save_as(pdf_path)

            print(f"[OK] PDFを保存しました: {pdf_path}")
            return str(pdf_path)

        except Exception as e:
            print(f"[ERROR] PDF保存中にエラーが発生しました: {e}")
            raise

    @staticmethod
    def save_input(page: Page):
        """入力を保存"""
        frame = page.frame_locator('#calculatorFrame')
        frame.locator('button#btn-save-draft-modal').click()
        page.wait_for_timeout(1000)

    @staticmethod
    def save_draft(page: Page) -> bool:
        """下書きを保存"""
        try:
            save_button = page.locator('button:has-text("下書き保存")')
            save_button.wait_for(state='visible', timeout=5000)
            page.wait_for_timeout(2000)

            if not save_button.is_disabled():
                save_button.click()
                page.wait_for_load_state('networkidle')
                return True
            else:
                print("[WARNING] 下書き保存ボタンが無効のため、処理をスキップしました")
                return False
        except Exception as e:
            print(f"[WARNING] 下書き保存をスキップしました: {e}")
            return False

    def move_csv_to_calculated(self, csv_path: Path):
        """CSVファイルをcalculatedディレクトリに移動"""
        self.calculated_dir.mkdir(exist_ok=True)

        destination = self.calculated_dir / csv_path.name
        shutil.move(str(csv_path), str(destination))
        print(f"[OK] {csv_path.name} を calculated ディレクトリに移動しました")
