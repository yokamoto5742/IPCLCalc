import logging
from pathlib import Path

from playwright.sync_api import Page

from service.auth_service import AuthService
from service.lens_calculator_service import LensCalculatorService
from service.patient_service import PatientService
from service.save_service import SaveService
from widgets.progress_window import ProgressWindow

logger = logging.getLogger(__name__)


class PatientWorkflowExecutor:
    def __init__(
        self,
        auth_service: AuthService,
        patient_service: PatientService,
        lens_calculator_service: LensCalculatorService,
        save_service: SaveService,
        progress_window: ProgressWindow,
    ):
        self.auth_service = auth_service
        self.patient_service = patient_service
        self.lens_calculator_service = lens_calculator_service
        self.save_service = save_service
        self.progress_window = progress_window

    def execute(self, page: Page, idx: int, total: int, data: dict) -> tuple[bool, Path | None]:
        pdf_path = None

        self.progress_window.update(f"[{idx}/{total}] Webサイトにログイン中...")
        self.auth_service.login(page)

        self.progress_window.update(f"[{idx}/{total}] 患者情報を入力中...")
        self.patient_service.fill_patient_info(page, data)

        self.progress_window.update(f"[{idx}/{total}] レンズ計算・注文を開いています...")
        self.lens_calculator_service.open_lens_calculator(page)

        self.progress_window.update(f"[{idx}/{total}] {data['eye']}タブを選択中...")
        self.lens_calculator_service.select_eye_tab(page, data['eye'])

        self.progress_window.update(f"[{idx}/{total}] 誕生日を入力中...")
        self.patient_service.fill_birthday(page, data['birthday'])

        self.progress_window.update(f"[{idx}/{total}] 測定データを入力中...")
        self.lens_calculator_service.fill_measurement_data(page, data, data['eye'])

        self.progress_window.update(f"[{idx}/{total}] レンズタイプを選択中...")
        self.lens_calculator_service.select_lens_type(page, data, data['eye'])

        self.progress_window.update(f"[{idx}/{total}] ATA/WTWデータを入力中...")
        self.lens_calculator_service.fill_ata_wtw_data(page, data, data['eye'])

        self.progress_window.update(f"[{idx}/{total}] レンズ計算を実行中...")
        self.lens_calculator_service.click_calculate_button(page)

        self.progress_window.update(f"[{idx}/{total}] 計算結果のPDFファイルを保存中...")
        pdf_path = self.save_service.click_save_pdf_button(page, data['id'], data['name'])

        self.progress_window.update(f"[{idx}/{total}] 入力したデータを保存中...")
        self.save_service.save_input(page)

        self.progress_window.update(f"[{idx}/{total}] 下書き保存中...")
        save_success = self.save_service.save_draft(page)

        if save_success:
            self.progress_window.update(f"[{idx}/{total}] 注文の下書きが保存されました")
            if pdf_path:
                logger.info(f"PDF保存先: {pdf_path}")
        else:
            logger.warning("ブラウザを開いたままにします。手動で確認してください。")

        return save_success, pdf_path
