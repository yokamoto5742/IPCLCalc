from unittest.mock import Mock

import pytest

from service.auth_service import AuthService


class TestAuthService:
    """AuthServiceのテストクラス"""

    @pytest.fixture
    def auth_service(self):
        """AuthServiceインスタンスを提供するフィクスチャ"""
        return AuthService(
            base_url="https://example.com",
            email="test@example.com",
            password="password123"
        )

    @pytest.fixture
    def mock_page(self):
        """Playwrightのページモックを提供するフィクスチャ"""
        return Mock()

    def test_init_stores_credentials(self, auth_service):
        """初期化時に認証情報が正しく保存されることを確認"""
        assert auth_service.base_url == "https://example.com"
        assert auth_service.email == "test@example.com"
        assert auth_service.password == "password123"

    def test_login_navigates_to_base_url(self, auth_service, mock_page):
        """ログイン時にベースURLに遷移することを確認"""
        auth_service.login(mock_page)

        mock_page.goto.assert_called_once_with("https://example.com")

    def test_login_waits_for_network_idle(self, auth_service, mock_page):
        """ログイン時にネットワークアイドルを待機することを確認"""
        auth_service.login(mock_page)

        assert mock_page.wait_for_load_state.call_count == 2
        mock_page.wait_for_load_state.assert_any_call('networkidle')

    def test_login_fills_email_field(self, auth_service, mock_page):
        """ログイン時にメールフィールドを入力することを確認"""
        auth_service.login(mock_page)

        mock_page.get_by_placeholder.assert_called_once_with("ログインID")
        mock_page.get_by_placeholder.return_value.fill.assert_called_once_with("test@example.com")

    def test_login_fills_password_field(self, auth_service, mock_page):
        """ログイン時にパスワードフィールドを入力することを確認"""
        auth_service.login(mock_page)

        mock_page.get_by_label.assert_called_once_with("パスワード")
        mock_page.get_by_label.return_value.fill.assert_called_once_with("password123")

    def test_login_clicks_signin_button(self, auth_service, mock_page):
        """ログイン時にサインインボタンをクリックすることを確認"""
        auth_service.login(mock_page)

        mock_page.click.assert_called_once_with('button:has-text("サインイン")')

    def test_login_with_empty_credentials(self):
        """空の認証情報でログインを試みる"""
        auth_service = AuthService("", "", "")
        mock_page = Mock()

        auth_service.login(mock_page)

        mock_page.get_by_placeholder.return_value.fill.assert_called_once_with("")
        mock_page.get_by_label.return_value.fill.assert_called_once_with("")

    def test_login_with_special_characters_in_password(self):
        """特殊文字を含むパスワードでログインできることを確認"""
        auth_service = AuthService(
            "https://example.com",
            "user@domain.com",
            "P@ssw0rd!#$%"
        )
        mock_page = Mock()

        auth_service.login(mock_page)

        mock_page.get_by_label.return_value.fill.assert_called_once_with("P@ssw0rd!#$%")

    def test_login_handles_page_exception(self, auth_service, mock_page):
        """ページ遷移時の例外を適切に処理することを確認"""
        mock_page.goto.side_effect = Exception("Network error")

        with pytest.raises(Exception, match="Network error"):
            auth_service.login(mock_page)
