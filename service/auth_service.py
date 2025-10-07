from playwright.sync_api import Page


class AuthService:
    def __init__(self, base_url: str, email: str, password: str):
        self.base_url = base_url
        self.email = email
        self.password = password

    def login(self, page: Page):
        page.goto(self.base_url)
        page.wait_for_load_state('networkidle')

        page.get_by_placeholder("ログインID").fill(self.email)
        page.get_by_label("パスワード").fill(self.password)
        page.click('button:has-text("サインイン")')
        page.wait_for_load_state('networkidle')
