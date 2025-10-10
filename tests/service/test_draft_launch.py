from unittest.mock import Mock, patch

import pytest

from service.draft_launch import launch_draft_page


class TestDraftLaunch:
    """draft_launchモジュールのテストクラス"""

    @patch('service.draft_launch.load_config')
    @patch('service.draft_launch.webbrowser.open')
    def test_launch_draft_page_loads_config(self, mock_webbrowser_open, mock_load_config):
        """設定ファイルが読み込まれることを確認"""
        mock_config = Mock()
        mock_config.get.return_value = 'https://example.com/draft'
        mock_load_config.return_value = mock_config

        launch_draft_page()

        mock_load_config.assert_called_once()

    @patch('service.draft_launch.load_config')
    @patch('service.draft_launch.webbrowser.open')
    def test_launch_draft_page_gets_draft_url(self, mock_webbrowser_open, mock_load_config):
        """下書きURLが取得されることを確認"""
        mock_config = Mock()
        mock_config.get.return_value = 'https://example.com/draft'
        mock_load_config.return_value = mock_config

        launch_draft_page()

        mock_config.get.assert_called_once_with('URL', 'draft_url')

    @patch('service.draft_launch.load_config')
    @patch('service.draft_launch.webbrowser.open')
    def test_launch_draft_page_strips_quotes_from_url(self, mock_webbrowser_open, mock_load_config):
        """URLから引用符が削除されることを確認"""
        mock_config = Mock()
        mock_config.get.return_value = '"https://example.com/draft"'
        mock_load_config.return_value = mock_config

        launch_draft_page()

        mock_webbrowser_open.assert_called_once_with('https://example.com/draft')

    @patch('service.draft_launch.load_config')
    @patch('service.draft_launch.webbrowser.open')
    def test_launch_draft_page_calls_webbrowser_open(self, mock_webbrowser_open, mock_load_config):
        """webbrowser.openが呼ばれることを確認"""
        mock_config = Mock()
        mock_config.get.return_value = 'https://example.com/draft'
        mock_load_config.return_value = mock_config

        launch_draft_page()

        mock_webbrowser_open.assert_called_once()

    @patch('service.draft_launch.load_config')
    @patch('service.draft_launch.webbrowser.open')
    def test_launch_draft_page_passes_correct_url(self, mock_webbrowser_open, mock_load_config):
        """正しいURLでwebbrowser.openが呼ばれることを確認"""
        draft_url = 'https://example.com/draft'

        mock_config = Mock()
        mock_config.get.return_value = draft_url
        mock_load_config.return_value = mock_config

        launch_draft_page()

        mock_webbrowser_open.assert_called_once_with(draft_url)

    @patch('service.draft_launch.load_config')
    @patch('service.draft_launch.webbrowser.open')
    def test_launch_draft_page_with_url_containing_parameters(self, mock_webbrowser_open, mock_load_config):
        """パラメータ付きURLを処理できることを確認"""
        draft_url = 'https://example.com/draft?id=123&mode=edit'

        mock_config = Mock()
        mock_config.get.return_value = draft_url
        mock_load_config.return_value = mock_config

        launch_draft_page()

        mock_webbrowser_open.assert_called_once_with(draft_url)

    @patch('service.draft_launch.load_config')
    @patch('service.draft_launch.webbrowser.open')
    def test_launch_draft_page_handles_config_exception(self, mock_webbrowser_open, mock_load_config):
        """設定読み込み時の例外を適切に処理することを確認"""
        mock_load_config.side_effect = Exception("Config file not found")

        with pytest.raises(Exception, match="Config file not found"):
            launch_draft_page()

        mock_webbrowser_open.assert_not_called()

    @patch('service.draft_launch.load_config')
    @patch('service.draft_launch.webbrowser.open')
    def test_launch_draft_page_with_empty_url(self, mock_webbrowser_open, mock_load_config):
        """空のURLでも処理が実行されることを確認"""
        draft_url = ''

        mock_config = Mock()
        mock_config.get.return_value = draft_url
        mock_load_config.return_value = mock_config

        launch_draft_page()

        mock_webbrowser_open.assert_called_once_with('')

    @patch('service.draft_launch.load_config')
    @patch('service.draft_launch.webbrowser.open')
    def test_launch_draft_page_with_quotes_variations(self, mock_webbrowser_open, mock_load_config):
        """引用符が削除されることを確認"""
        draft_url = '"https://example.com/draft"'

        mock_config = Mock()
        mock_config.get.return_value = draft_url
        mock_load_config.return_value = mock_config

        launch_draft_page()

        mock_webbrowser_open.assert_called_once_with('https://example.com/draft')

    @patch('service.draft_launch.load_config')
    @patch('service.draft_launch.webbrowser.open')
    def test_launch_draft_page_returns_none(self, mock_webbrowser_open, mock_load_config):
        """launch_draft_page関数がNoneを返すことを確認"""
        mock_config = Mock()
        mock_config.get.return_value = 'https://example.com/draft'
        mock_load_config.return_value = mock_config

        result = launch_draft_page()

        assert result is None

    @patch('service.draft_launch.load_config')
    @patch('service.draft_launch.webbrowser.open')
    def test_launch_draft_page_with_leading_and_trailing_quotes(self, mock_webbrowser_open, mock_load_config):
        """先頭と末尾の引用符が削除されることを確認"""
        mock_config = Mock()
        mock_config.get.return_value = '""https://example.com/draft""'
        mock_load_config.return_value = mock_config

        launch_draft_page()

        mock_webbrowser_open.assert_called_once_with('https://example.com/draft')

    @patch('service.draft_launch.load_config')
    @patch('service.draft_launch.webbrowser.open')
    def test_launch_draft_page_opens_url_in_default_browser(self, mock_webbrowser_open, mock_load_config):
        """デフォルトブラウザでURLが開かれることを確認"""
        mock_config = Mock()
        mock_config.get.return_value = 'https://example.com/draft'
        mock_load_config.return_value = mock_config
        mock_webbrowser_open.return_value = True

        launch_draft_page()

        assert mock_webbrowser_open.called
        assert mock_webbrowser_open.return_value is True
