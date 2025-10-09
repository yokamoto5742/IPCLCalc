import logging

from playwright.sync_api import Page

logger = logging.getLogger(__name__)


class AuthService:
    def __init__(self, base_url: str, email: str, password: str):
        self.base_url = base_url
        self.email = email
        self.password = password

    def _fill_login_id(self, page: Page):
        selectors = [
            '#login-form-login',  # id属性
            'input[name="login-form[login]"]',  # name属性
        ]

        for selector in selectors:
            try:
                element = page.locator(selector)
                if element.count() > 0:
                    element.fill(self.email)
                    logger.info(f"ログインIDを入力しました（セレクタ: {selector}）")
                    return
            except Exception as e:
                logger.debug(f"セレクタ {selector} での入力に失敗: {e}")
                continue

        raise Exception("ログインID入力フィールドが見つかりませんでした")

    def _fill_password(self, page: Page):
        selectors = [
            '#login-form-password',
            'input[name="login-form[password]"]',
        ]

        for selector in selectors:
            try:
                element = page.locator(selector)
                if element.count() > 0:
                    element.fill(self.password)
                    logger.info(f"パスワードを入力しました（セレクタ: {selector}）")
                    return
            except Exception as e:
                logger.debug(f"セレクタ {selector} での入力に失敗: {e}")
                continue

        raise Exception("パスワード入力フィールドが見つかりませんでした")

    def login(self, page: Page):
        page.goto(self.base_url)
        page.wait_for_load_state('networkidle')

        self._fill_login_id(page)
        self._fill_password(page)

        page.click('button:has-text("サインイン")')
        page.wait_for_load_state('networkidle')
        logger.info("ログイン処理が完了しました")
