import pytest
from unittest.mock import Mock

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
        page = Mock()

        # locatorメソッドのモック設定
        mock_locator = Mock()
        mock_locator.count.return_value = 1
        page.locator.return_value = mock_locator

        return page

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

    def test_login_fills_login_id_field(self, auth_service, mock_page):
        """ログイン時にログインIDフィールドを入力することを確認"""
        auth_service.login(mock_page)

        # locatorが呼ばれたことを確認
        assert mock_page.locator.call_count >= 2  # login_id + password
        # fillメソッドが呼ばれたことを確認
        mock_page.locator.return_value.fill.assert_any_call("test@example.com")

    def test_login_fills_password_field(self, auth_service, mock_page):
        """ログイン時にパスワードフィールドを入力することを確認"""
        auth_service.login(mock_page)

        # fillメソッドが呼ばれたことを確認
        mock_page.locator.return_value.fill.assert_any_call("password123")

    def test_login_clicks_signin_button(self, auth_service, mock_page):
        """ログイン時にサインインボタンをクリックすることを確認"""
        auth_service.login(mock_page)

        mock_page.click.assert_called_once_with('button:has-text("サインイン")')

    def test_login_with_empty_credentials(self):
        """空の認証情報でログインを試みる"""
        auth_service = AuthService("", "", "")
        mock_page = Mock()

        # locatorメソッドのモック設定
        mock_locator = Mock()
        mock_locator.count.return_value = 1
        mock_page.locator.return_value = mock_locator

        auth_service.login(mock_page)

        # 空文字列で入力されたことを確認
        calls = mock_page.locator.return_value.fill.call_args_list
        assert any(call[0][0] == "" for call in calls)

    def test_login_with_special_characters_in_password(self):
        """特殊文字を含むパスワードでログインできることを確認"""
        auth_service = AuthService(
            "https://example.com",
            "user@domain.com",
            "P@ssw0rd!#$%"
        )
        mock_page = Mock()

        # locatorメソッドのモック設定
        mock_locator = Mock()
        mock_locator.count.return_value = 1
        mock_page.locator.return_value = mock_locator

        auth_service.login(mock_page)

        # 特殊文字を含むパスワードで入力されたことを確認
        mock_page.locator.return_value.fill.assert_any_call("P@ssw0rd!#$%")

    def test_login_handles_page_exception(self, auth_service, mock_page):
        """ページ遷移時の例外を適切に処理することを確認"""
        mock_page.goto.side_effect = Exception("Network error")

        with pytest.raises(Exception, match="Network error"):
            auth_service.login(mock_page)

    def test_fill_login_id_tries_multiple_selectors(self, auth_service):
        """ログインID入力で複数のセレクタを試行することを確認"""
        mock_page = Mock()
        mock_locator = Mock()
        mock_locator.count.return_value = 1
        mock_page.locator.return_value = mock_locator

        auth_service._fill_login_id(mock_page)

        # 最初のセレクタで成功する
        mock_page.locator.assert_called_with('#login-form-login')
        mock_locator.fill.assert_called_once_with("test@example.com")

    def test_fill_login_id_fallback_to_second_selector(self, auth_service):
        """ログインID入力で最初のセレクタが失敗した場合に次のセレクタを試行することを確認"""
        mock_page = Mock()

        # 最初のlocator呼び出しは要素が見つからない
        first_locator = Mock()
        first_locator.count.return_value = 0

        # 2番目のlocator呼び出しは成功
        second_locator = Mock()
        second_locator.count.return_value = 1

        mock_page.locator.side_effect = [first_locator, second_locator]

        auth_service._fill_login_id(mock_page)

        # 2つのセレクタが試行されたことを確認
        assert mock_page.locator.call_count == 2
        second_locator.fill.assert_called_once_with("test@example.com")

    def test_fill_login_id_raises_exception_when_no_selector_works(self, auth_service):
        """すべてのセレクタが失敗した場合に例外を発生させることを確認"""
        mock_page = Mock()
        mock_locator = Mock()
        mock_locator.count.return_value = 0
        mock_page.locator.return_value = mock_locator

        with pytest.raises(Exception, match="ログインID入力フィールドが見つかりませんでした"):
            auth_service._fill_login_id(mock_page)

    def test_fill_password_tries_multiple_selectors(self, auth_service):
        """パスワード入力で複数のセレクタを試行することを確認"""
        mock_page = Mock()
        mock_locator = Mock()
        mock_locator.count.return_value = 1
        mock_page.locator.return_value = mock_locator

        auth_service._fill_password(mock_page)

        # 最初のセレクタで成功する
        mock_page.locator.assert_called_with('#login-form-password')
        mock_locator.fill.assert_called_once_with("password123")

    def test_fill_password_fallback_to_second_selector(self, auth_service):
        """パスワード入力で最初のセレクタが失敗した場合に次のセレクタを試行することを確認"""
        mock_page = Mock()

        # 最初のlocator呼び出しは要素が見つからない
        first_locator = Mock()
        first_locator.count.return_value = 0

        # 2番目のlocator呼び出しは成功
        second_locator = Mock()
        second_locator.count.return_value = 1

        mock_page.locator.side_effect = [first_locator, second_locator]

        auth_service._fill_password(mock_page)

        # 2つのセレクタが試行されたことを確認
        assert mock_page.locator.call_count == 2
        second_locator.fill.assert_called_once_with("password123")

    def test_fill_password_raises_exception_when_no_selector_works(self, auth_service):
        """すべてのセレクタが失敗した場合に例外を発生させることを確認"""
        mock_page = Mock()
        mock_locator = Mock()
        mock_locator.count.return_value = 0
        mock_page.locator.return_value = mock_locator

        with pytest.raises(Exception, match="パスワード入力フィールドが見つかりませんでした"):
            auth_service._fill_password(mock_page)
