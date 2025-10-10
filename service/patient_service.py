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
        """
        誕生日を入力します。
        typeメソッドを使用して1文字ずつ入力することで、
        Webサイトの日付ピッカーが正しく動作するようにします。
        """
        frame = page.frame_locator('#calculatorFrame')

        try:
            birthday_input = frame.locator('input[placeholder="dd/mm/yyyy"]').first

            # フィールドをクリックしてフォーカス
            birthday_input.click()

            # 既存の値をクリア（念のため）
            birthday_input.press('Control+A')
            birthday_input.press('Delete')

            # typeメソッドで1文字ずつ入力（delay=100msで人間らしい入力速度）
            birthday_input.type(birthday, delay=100)
            logger.info(f"誕生日を入力しました: {birthday}")

            # 少し待機してからEnterキーを押す
            birthday_input.press('Enter')

            # 入力後の値を確認（オプション）
            try:
                final_value = birthday_input.input_value()
                if final_value != birthday:
                    logger.warning(f"⚠️ 入力後の値が異なります: 期待値='{birthday}', 実際値='{final_value}'")
                else:
                    logger.info(f"✅ 誕生日が正しく入力されました: {final_value}")
            except:
                pass

        except Exception as e:
            logger.error(f"誕生日入力中にエラーが発生: {e}", exc_info=True)