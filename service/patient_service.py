import logging

from playwright.sync_api import Page

logger = logging.getLogger(__name__)


class PatientService:
    @staticmethod
    def fill_patient_info(page: Page, data: dict):
        page.wait_for_load_state('networkidle')

        page.get_by_label("患者ID").fill(data['id'])

        try:
            page.locator('#select2-order-sex-container').click()
            page.locator('li.select2-results__option').first.wait_for(state='visible')
            sex_index = 0 if data['sex'] == '男性' else 1
            page.locator('li.select2-results__option').nth(sex_index).click()
        except Exception as e:
            try:
                page.get_by_label("性別*").click()
                page.click(f'li:has-text("{data["sex"]}")')
            except Exception as retry_error:
                logger.warning("性別選択をスキップしました")

        try:
            surgery_date_input = page.get_by_label("手術日")
            surgery_date_input.click()
            surgery_date_input.type(data['surgery_date'], delay=100)
            logger.info(f"手術日を入力しました: {data['surgery_date']}")
            surgery_date_input.press('Enter')

        except Exception as e:
            try:
                surgery_date_input = page.locator('input[name*="surgery"]').first
                surgery_date_input.click()
                surgery_date_input.type(data['surgery_date'], delay=100)
                surgery_date_input.press('Enter')
                logger.info(f"手術日を入力しました: {data['surgery_date']}")

            except Exception as retry_error:
                logger.warning(f"手術日入力をスキップしました: {retry_error}")

    @staticmethod
    def fill_birthday(page: Page, birthday: str):
        frame = page.frame_locator('#calculatorFrame')

        try:
            birthday_input = frame.locator('input[placeholder="dd/mm/yyyy"]').first
            birthday_input.click()
            birthday_input.type(birthday, delay=100)
            birthday_input.press('Enter')
            logger.info(f"誕生日を入力しました: {birthday}")

        except Exception as e:
            logger.error(f"誕生日入力中にエラーが発生: {e}", exc_info=True)
