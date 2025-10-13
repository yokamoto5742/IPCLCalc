from unittest.mock import Mock, patch, call

import pytest

from service.draft_launch import launch_draft_page


class TestDraftLaunch:
    """draft_launchモジュールのテストクラス"""

    @patch('service.draft_launch.os.path.exists')
    @patch('service.draft_launch.load_config')
    @patch('service.draft_launch.subprocess.Popen')
    def test_launch_draft_page_loads_config(self, mock_popen, mock_load_config, mock_exists):
        """設定ファイルが読み込まれることを確認"""
        mock_exists.return_value = True
        mock_config = Mock()
        mock_config.get.side_effect = [
            'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
            'https://example.com/draft'
        ]
        mock_load_config.return_value = mock_config

        launch_draft_page()

        mock_load_config.assert_called_once()

    @patch('service.draft_launch.os.path.exists')
    @patch('service.draft_launch.load_config')
    @patch('service.draft_launch.subprocess.Popen')
    def test_launch_draft_page_gets_chrome_path(self, mock_popen, mock_load_config, mock_exists):
        """Chrome実行パスが取得されることを確認"""
        mock_exists.return_value = True
        mock_config = Mock()
        mock_config.get.side_effect = [
            'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
            'https://example.com/draft'
        ]
        mock_load_config.return_value = mock_config

        launch_draft_page()

        mock_config.get.assert_any_call('Chrome', 'chrome_path')

    @patch('service.draft_launch.load_config')
    @patch('service.draft_launch.subprocess.Popen')
    def test_launch_draft_page_gets_draft_url(self, mock_popen, mock_load_config):
        """下書きURLが取得されることを確認"""
        mock_config = Mock()
        mock_config.get.side_effect = [
            'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
            'https://example.com/draft'
        ]
        mock_load_config.return_value = mock_config

        launch_draft_page()

        mock_config.get.assert_any_call('URL', 'draft_url')

    @patch('service.draft_launch.load_config')
    @patch('service.draft_launch.subprocess.Popen')
    def test_launch_draft_page_strips_quotes_from_url(self, mock_popen, mock_load_config):
        """URLから引用符が削除されることを確認"""
        mock_config = Mock()
        mock_config.get.side_effect = [
            'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
            '"https://example.com/draft"'  # 引用符付き
        ]
        mock_load_config.return_value = mock_config

        launch_draft_page()

        # 引用符が削除されたURLでPopenが呼ばれることを確認
        expected_call = call([
            'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
            'https://example.com/draft'
        ])
        mock_popen.assert_called_once_with(expected_call.args[0])

    @patch('service.draft_launch.os.path.exists')
    @patch('service.draft_launch.load_config')
    @patch('service.draft_launch.subprocess.Popen')
    def test_launch_draft_page_calls_subprocess_popen(self, mock_popen, mock_load_config, mock_exists):
        """subprocess.Popenが呼ばれることを確認"""
        mock_exists.return_value = True
        mock_config = Mock()
        mock_config.get.side_effect = [
            '/usr/bin/google-chrome',
            'https://example.com/draft'
        ]
        mock_load_config.return_value = mock_config

        launch_draft_page()

        mock_popen.assert_called_once()

    @patch('service.draft_launch.os.path.exists')
    @patch('service.draft_launch.load_config')
    @patch('service.draft_launch.subprocess.Popen')
    def test_launch_draft_page_passes_correct_arguments(self, mock_popen, mock_load_config, mock_exists):
        """正しい引数でsubprocess.Popenが呼ばれることを確認"""
        mock_exists.return_value = True
        chrome_path = 'C:\\Program Files\\Chrome\\chrome.exe'
        draft_url = 'https://example.com/draft'

        mock_config = Mock()
        mock_config.get.side_effect = [chrome_path, draft_url]
        mock_load_config.return_value = mock_config

        launch_draft_page()

        mock_popen.assert_called_once_with([chrome_path, draft_url])

    @patch('service.draft_launch.os.path.exists')
    @patch('service.draft_launch.load_config')
    @patch('service.draft_launch.subprocess.Popen')
    def test_launch_draft_page_with_url_containing_parameters(self, mock_popen, mock_load_config, mock_exists):
        """パラメータ付きURLを処理できることを確認"""
        mock_exists.return_value = True
        chrome_path = '/usr/bin/chrome'
        draft_url = 'https://example.com/draft?id=123&mode=edit'

        mock_config = Mock()
        mock_config.get.side_effect = [chrome_path, draft_url]
        mock_load_config.return_value = mock_config

        launch_draft_page()

        mock_popen.assert_called_once_with([chrome_path, draft_url])

    @patch('service.draft_launch.os.path.exists')
    @patch('service.draft_launch.load_config')
    @patch('service.draft_launch.subprocess.Popen')
    def test_launch_draft_page_handles_popen_exception(self, mock_popen, mock_load_config, mock_exists):
        """subprocess.Popen実行時の例外を適切に処理することを確認"""
        mock_exists.return_value = True
        mock_config = Mock()
        mock_config.get.side_effect = [
            'C:\\Program Files\\Chrome\\chrome.exe',
            'https://example.com/draft'
        ]
        mock_load_config.return_value = mock_config
        mock_popen.side_effect = FileNotFoundError("Chrome not found")

        with pytest.raises(FileNotFoundError, match="Chrome not found"):
            launch_draft_page()

    @patch('service.draft_launch.load_config')
    @patch('service.draft_launch.subprocess.Popen')
    def test_launch_draft_page_handles_config_exception(self, mock_popen, mock_load_config):
        """設定読み込み時の例外を適切に処理することを確認"""
        mock_load_config.side_effect = Exception("Config file not found")

        with pytest.raises(Exception, match="Config file not found"):
            launch_draft_page()

        mock_popen.assert_not_called()

    @patch('service.draft_launch.os.path.exists')
    @patch('service.draft_launch.load_config')
    @patch('service.draft_launch.subprocess.Popen')
    def test_launch_draft_page_with_empty_url(self, mock_popen, mock_load_config, mock_exists):
        """空のURLでも処理が実行されることを確認"""
        mock_exists.return_value = True
        chrome_path = '/usr/bin/chrome'
        draft_url = ''

        mock_config = Mock()
        mock_config.get.side_effect = [chrome_path, draft_url]
        mock_load_config.return_value = mock_config

        launch_draft_page()

        mock_popen.assert_called_once_with([chrome_path, ''])

    @patch('service.draft_launch.os.path.exists')
    @patch('service.draft_launch.load_config')
    @patch('service.draft_launch.subprocess.Popen')
    def test_launch_draft_page_with_quotes_variations(self, mock_popen, mock_load_config, mock_exists):
        """引用符が削除されることを確認"""
        mock_exists.return_value = True
        chrome_path = '/usr/bin/chrome'
        draft_url = '"https://example.com/draft"'

        mock_config = Mock()
        mock_config.get.side_effect = [chrome_path, draft_url]
        mock_load_config.return_value = mock_config

        launch_draft_page()

        # .strip('"')が呼ばれているので、両端の引用符が削除される
        expected_url = 'https://example.com/draft'
        mock_popen.assert_called_once_with([chrome_path, expected_url])

    @patch('service.draft_launch.os.path.exists')
    @patch('service.draft_launch.load_config')
    @patch('service.draft_launch.subprocess.Popen')
    def test_launch_draft_page_returns_none(self, mock_popen, mock_load_config, mock_exists):
        """launch_draft_page関数がNoneを返すことを確認"""
        mock_exists.return_value = True
        mock_config = Mock()
        mock_config.get.side_effect = [
            '/usr/bin/chrome',
            'https://example.com/draft'
        ]
        mock_load_config.return_value = mock_config

        result = launch_draft_page()

        assert result is None

    @patch('service.draft_launch.os.path.exists')
    @patch('service.draft_launch.load_config')
    @patch('service.draft_launch.subprocess.Popen')
    def test_launch_draft_page_popen_creates_new_process(self, mock_popen, mock_load_config, mock_exists):
        """Popenが新しいプロセスを作成することを確認"""
        mock_exists.return_value = True
        mock_config = Mock()
        mock_config.get.side_effect = [
            '/usr/bin/chrome',
            'https://example.com/draft'
        ]
        mock_load_config.return_value = mock_config
        mock_process = Mock()
        mock_popen.return_value = mock_process

        launch_draft_page()

        # Popenが呼ばれ、プロセスオブジェクトが返されることを確認
        assert mock_popen.called
        assert mock_popen.return_value == mock_process
