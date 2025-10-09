import logging

from playwright.sync_api import Page

logger = logging.getLogger(__name__)


class PatientService:
    @staticmethod
    def fill_patient_info(page: Page, data: dict):
        """患者情報を入力"""
        page.wait_for_load_state('domcontentloaded')
        page.wait_for_timeout(1000)

        page.get_by_label("患者ID").fill(data['id'])

        try:
            page.locator('#select2-order-sex-container').click()
            page.wait_for_timeout(500)
            sex_index = 0 if data['sex'] == '男性' else 1
            page.locator('li.select2-results__option').nth(sex_index).click()
        except Exception as e:
            try:
                page.get_by_label("性別*").click()
                page.click(f'li:has-text("{data["sex"]}")')
            except Exception as retry_error:
                logger.warning("性別選択をスキップしました")

        try:
            page.get_by_label("手術日").fill(data['surgery_date'])
            page.get_by_label("手術日").press('Enter')
        except Exception as e:
            try:
                page.locator('input[name*="surgery"]').first.fill(data['surgery_date'])
                page.locator('input[name*="surgery"]').first.press('Enter')
            except Exception as retry_error:
                logger.warning(f"手術日入力をスキップしました: {retry_error}")

    @staticmethod
    def fill_birthday(page: Page, birthday: str):
        """誕生日を入力"""
        frame = page.frame_locator('#calculatorFrame')

        try:
            month, day, year = birthday.split('/')
            formatted_birthday = f"{day}/{month}/{year}"

            birthday_input = frame.locator('input[placeholder="dd/mm/yyyy"]').first
            birthday_input.fill(formatted_birthday)
            birthday_input.press('Enter')
            page.wait_for_timeout(500)

        except Exception as e:
            logger.warning(f"誕生日入力をスキップしました: {e}")
