import logging
import os
import sys
from pathlib import Path

from playwright.sync_api import Browser, BrowserContext, Page, Playwright

logger = logging.getLogger(__name__)


class BrowserManager:
    """Playwrightブラウザのセットアップとライフサイクル管理"""

    def __init__(self, headless: bool = True):
        self.headless = headless
        self._setup_playwright_path()

    def _setup_playwright_path(self):
        """実行環境に応じてPlaywrightブラウザパスを設定"""
        if getattr(sys, 'frozen', False):
            base_path = Path(sys._MEIPASS)
            playwright_browsers = base_path / 'playwright' / 'driver' / 'package' / '.local-browsers'
            if playwright_browsers.exists():
                os.environ['PLAYWRIGHT_BROWSERS_PATH'] = str(playwright_browsers)
                logger.info(f"Playwrightブラウザパス設定: {playwright_browsers}")
            else:
                logger.warning(f"Playwrightブラウザパスが見つかりません: {playwright_browsers}")

    def create_browser(self, playwright: Playwright) -> Browser:
        """ブラウザインスタンスを作成"""
        return playwright.chromium.launch(headless=self.headless)

    def create_context(self, browser: Browser) -> BrowserContext:
        """ブラウザコンテキストを作成"""
        return browser.new_context(accept_downloads=True)

    def create_page(self, context: BrowserContext) -> Page:
        """新しいページを作成"""
        return context.new_page()
