import os
from unittest.mock import Mock, patch

import pytest

from service.automation_service import IPCLOrderAutomation


class TestIPCLOrderAutomation:
    """IPCLOrderAutomationのテストクラス"""

    @pytest.fixture
    def mock_config(self):
        """設定モックを提供するフィクスチャ"""
        config = Mock()
        config.get.side_effect = lambda section, key: {
            ('URL', 'base_url'): 'https://example.com',
            ('Paths', 'csv_dir'): 'C:\\test\\csv',
            ('Paths', 'calculated_dir'): 'C:\\test\\calculated',
            ('Paths', 'error_dir'): 'C:\\test\\error',
            ('Paths', 'log_dir'): 'C:\\test\\log',
        }.get((section, key), '')
        config.getboolean.return_value = True
        return config

    @pytest.fixture
    def mock_env(self):
        """環境変数モックを提供するフィクスチャ"""
        return {
            'EMAIL': 'test@example.com',
            'PASSWORD': 'password123'
        }

    @patch('service.automation_service.Path.mkdir')
    @patch('service.automation_service.load_environment_variables')
    @patch('service.automation_service.load_config')
    @patch.dict(os.environ, {'EMAIL': 'test@example.com', 'PASSWORD': 'password123'})
    def test_init_loads_config(self, mock_load_config, mock_load_env, mock_mkdir, mock_config):
        """初期化時に設定が読み込まれることを確認"""
        mock_load_config.return_value = mock_config

        automation = IPCLOrderAutomation()

        mock_load_config.assert_called_once()
        mock_load_env.assert_called_once()

    @patch('service.automation_service.Path.mkdir')
    @patch('service.automation_service.load_environment_variables')
    @patch('service.automation_service.load_config')
    @patch.dict(os.environ, {'EMAIL': 'test@example.com', 'PASSWORD': 'password123'})
    def test_init_stores_configuration(self, mock_load_config, mock_load_env, mock_mkdir, mock_config):
        """初期化時に設定が保存されることを確認"""
        mock_load_config.return_value = mock_config

        automation = IPCLOrderAutomation()

        # 認証情報やbase_urlはauth_serviceやbrowser_managerに渡されるため、
        # IPCLOrderAutomationのインスタンス属性としては保持されない
        assert automation.csv_handler is not None
        assert automation.browser_manager is not None
        assert automation.workflow_executor is not None

    @patch('service.automation_service.load_environment_variables')
    @patch('service.automation_service.load_config')
    @patch.dict(os.environ, {'EMAIL': 'test@example.com', 'PASSWORD': 'password123'})
    def test_init_creates_pdf_directory(self, mock_load_config, mock_load_env, mock_config, tmp_path):
        """初期化時にPDFディレクトリパスが設定されることを確認"""
        # 実際のディレクトリを作成
        csv_dir = tmp_path / 'csv'
        csv_dir.mkdir(parents=True, exist_ok=True)

        mock_config.get.side_effect = lambda section, key: {
            ('URL', 'base_url'): 'https://example.com',
            ('Paths', 'csv_dir'): str(csv_dir),
            ('Paths', 'calculated_dir'): str(tmp_path / 'calculated'),
            ('Paths', 'error_dir'): str(tmp_path / 'error'),
            ('Paths', 'log_dir'): str(tmp_path / 'log'),
        }.get((section, key), '')
        mock_config.getboolean.return_value = True
        mock_load_config.return_value = mock_config

        automation = IPCLOrderAutomation()

        # PDFディレクトリのパスが正しく設定されることを確認
        assert automation.pdf_dir == csv_dir / 'pdf'
        # 実際のディレクトリが作成されたことを確認
        assert automation.pdf_dir.exists()

    @patch('service.automation_service.Path.mkdir')
    @patch('service.automation_service.load_environment_variables')
    @patch('service.automation_service.load_config')
    @patch.dict(os.environ, {'EMAIL': 'test@example.com', 'PASSWORD': 'password123'})
    def test_init_initializes_services(self, mock_load_config, mock_load_env, mock_mkdir, mock_config):
        """初期化時にサービスが初期化されることを確認"""
        mock_load_config.return_value = mock_config

        automation = IPCLOrderAutomation()

        # リファクタリング後はworkflow_executorにサービスが統合されている
        assert automation.csv_handler is not None
        assert automation.browser_manager is not None
        assert automation.workflow_executor is not None
        assert automation.save_service is not None
        assert automation.progress_window is not None

    @patch('service.automation_service.Path.mkdir')
    @patch('service.automation_service.load_environment_variables')
    @patch('service.automation_service.load_config')
    @patch.dict(os.environ, {'EMAIL': 'test@example.com', 'PASSWORD': 'password123'})
    def test_create_progress_window_creates_widgets(self, mock_load_config, mock_load_env, mock_mkdir, mock_config):
        """進捗ウィンドウが作成されることを確認"""
        mock_load_config.return_value = mock_config

        with patch('widgets.progress_window.tk.Tk') as mock_tk:
            with patch('widgets.progress_window.tk.Toplevel') as mock_toplevel:
                with patch('widgets.progress_window.tk.Label') as mock_label:
                    mock_root = Mock()
                    mock_tk.return_value = mock_root
                    mock_window = Mock()
                    # winfo_screenwidthなどのメソッドをモック
                    mock_window.winfo_screenwidth.return_value = 1920
                    mock_window.winfo_screenheight.return_value = 1080
                    mock_window.winfo_width.return_value = 500
                    mock_window.winfo_height.return_value = 150
                    mock_toplevel.return_value = mock_window
                    mock_label_instance = Mock()
                    mock_label.return_value = mock_label_instance

                    automation = IPCLOrderAutomation()
                    automation.progress_window.create()

                    mock_tk.assert_called_once()
                    mock_root.withdraw.assert_called_once()
                    assert automation.progress_window.root is not None
                    assert automation.progress_window.progress_window is not None

    @patch('service.automation_service.Path.mkdir')
    @patch('service.automation_service.load_environment_variables')
    @patch('service.automation_service.load_config')
    @patch.dict(os.environ, {'EMAIL': 'test@example.com', 'PASSWORD': 'password123'})
    def test_update_progress_updates_label(self, mock_load_config, mock_load_env, mock_mkdir, mock_config):
        """進捗メッセージが更新されることを確認"""
        mock_load_config.return_value = mock_config

        automation = IPCLOrderAutomation()
        automation.progress_window.progress_label = Mock()
        automation.progress_window.progress_window = Mock()

        automation.progress_window.update("テストメッセージ")

        automation.progress_window.progress_label.config.assert_called_once_with(text="テストメッセージ")
        automation.progress_window.progress_window.update.assert_called_once()

    @patch('service.automation_service.Path.mkdir')
    @patch('service.automation_service.load_environment_variables')
    @patch('service.automation_service.load_config')
    @patch.dict(os.environ, {'EMAIL': 'test@example.com', 'PASSWORD': 'password123'})
    def test_close_progress_window_destroys_widgets(self, mock_load_config, mock_load_env, mock_mkdir, mock_config):
        """進捗ウィンドウが閉じられることを確認"""
        mock_load_config.return_value = mock_config

        automation = IPCLOrderAutomation()
        automation.progress_window.progress_window = Mock()
        automation.progress_window.root = Mock()

        automation.progress_window.close()

        automation.progress_window.progress_window.destroy.assert_called_once()
        automation.progress_window.root.destroy.assert_called_once()

    @patch('service.automation_service.Path.mkdir')
    @patch('service.automation_service.load_environment_variables')
    @patch('service.automation_service.load_config')
    @patch.dict(os.environ, {'EMAIL': 'test@example.com', 'PASSWORD': 'password123'})
    def test_close_progress_window_handles_none_values(self, mock_load_config, mock_load_env, mock_mkdir, mock_config):
        """進捗ウィンドウがNoneの場合でもエラーが発生しないことを確認"""
        mock_load_config.return_value = mock_config

        automation = IPCLOrderAutomation()
        automation.progress_window.progress_window = None
        automation.progress_window.root = None

        # エラーが発生しないことを確認
        automation.progress_window.close()

    @patch('service.automation_service.Path.mkdir')
    @patch('service.automation_service.load_environment_variables')
    @patch('service.automation_service.load_config')
    @patch.dict(os.environ, {'EMAIL': 'test@example.com', 'PASSWORD': 'password123'})
    def test_process_csv_file_reads_csv(self, mock_load_config, mock_load_env, mock_mkdir, mock_config, tmp_path):
        """CSVファイルが読み込まれることを確認"""
        # calculatedディレクトリを作成
        calculated_dir = tmp_path / 'calculated'
        calculated_dir.mkdir(parents=True, exist_ok=True)

        mock_config.get.side_effect = lambda section, key: {
            ('URL', 'base_url'): 'https://example.com',
            ('Paths', 'csv_dir'): str(tmp_path),
            ('Paths', 'calculated_dir'): str(calculated_dir),
            ('Paths', 'error_dir'): str(tmp_path / 'error'),
            ('Paths', 'log_dir'): str(tmp_path / 'log'),
        }.get((section, key), '')
        mock_config.getboolean.return_value = True
        mock_load_config.return_value = mock_config

        automation = IPCLOrderAutomation()
        automation.csv_handler = Mock()
        # 空のリストを返すとprocess_csv_fileはファイルを移動する
        automation.csv_handler.read_csv_file.return_value = []
        automation.update_progress = Mock()
        # ファイル移動をモック
        automation.save_service.move_csv_to_calculated = Mock()

        csv_path = tmp_path / "test.csv"
        csv_path.write_text("test,data\n1,2")

        automation.process_csv_file(csv_path)

        automation.csv_handler.read_csv_file.assert_called_once_with(csv_path)
        # データが空なのでファイルは移動される
        automation.save_service.move_csv_to_calculated.assert_called_once_with(csv_path)

    @patch('service.automation_service.load_environment_variables')
    @patch('service.automation_service.load_config')
    @patch.dict(os.environ, {'EMAIL': 'test@example.com', 'PASSWORD': 'password123'})
    def test_process_all_csv_files_finds_csv_files(self, mock_load_config, mock_load_env, mock_config, tmp_path):
        """CSVファイルが見つかることを確認"""
        mock_config.get.side_effect = lambda section, key: {
            ('URL', 'base_url'): 'https://example.com',
            ('Paths', 'csv_dir'): str(tmp_path),
            ('Paths', 'calculated_dir'): str(tmp_path / 'calculated'),
            ('Paths', 'error_dir'): str(tmp_path / 'error'),
            ('Paths', 'log_dir'): str(tmp_path / 'log'),
        }.get((section, key), '')
        mock_config.getboolean.return_value = True
        mock_load_config.return_value = mock_config

        # テストCSVファイルを作成
        csv_file1 = tmp_path / "IPCLdata_001.csv"
        csv_file2 = tmp_path / "IPCLdata_002.csv"
        csv_file1.write_text("test")
        csv_file2.write_text("test")

        automation = IPCLOrderAutomation()
        automation.create_progress_window = Mock()
        automation.update_progress = Mock()
        automation.process_csv_file = Mock()
        automation.close_progress_window = Mock()
        automation.progress_window = Mock()

        automation.process_all_csv_files()

        # 2つのCSVファイルが処理されることを確認
        assert automation.process_csv_file.call_count == 2

    @patch('service.automation_service.load_environment_variables')
    @patch('service.automation_service.load_config')
    @patch.dict(os.environ, {'EMAIL': 'test@example.com', 'PASSWORD': 'password123'})
    def test_process_all_csv_files_handles_no_files(self, mock_load_config, mock_load_env, mock_config, tmp_path, caplog):
        """CSVファイルが見つからない場合の処理を確認"""
        mock_config.get.side_effect = lambda section, key: {
            ('URL', 'base_url'): 'https://example.com',
            ('Paths', 'csv_dir'): str(tmp_path),
            ('Paths', 'calculated_dir'): str(tmp_path / 'calculated'),
            ('Paths', 'error_dir'): str(tmp_path / 'error'),
            ('Paths', 'log_dir'): str(tmp_path / 'log'),
        }.get((section, key), '')
        mock_config.getboolean.return_value = True
        mock_load_config.return_value = mock_config

        automation = IPCLOrderAutomation()

        automation.process_all_csv_files()

        # logger.warningを使用しているため、caplogで確認
        assert "処理するCSVファイルが見つかりませんでした" in caplog.text

    @patch('service.automation_service.Path.mkdir')
    @patch('service.automation_service.load_environment_variables')
    @patch('service.automation_service.load_config')
    @patch.dict(os.environ, {'EMAIL': 'test@example.com', 'PASSWORD': 'password123'})
    def test_process_csv_file_handles_exception(self, mock_load_config, mock_load_env, mock_mkdir, mock_config, tmp_path):
        """CSVファイル処理時の例外を適切に処理することを確認"""
        # error_dirを作成
        error_dir = tmp_path / 'error'
        error_dir.mkdir(parents=True, exist_ok=True)

        mock_config.get.side_effect = lambda section, key: {
            ('URL', 'base_url'): 'https://example.com',
            ('Paths', 'csv_dir'): str(tmp_path),
            ('Paths', 'calculated_dir'): str(tmp_path / 'calculated'),
            ('Paths', 'error_dir'): str(error_dir),
            ('Paths', 'log_dir'): str(tmp_path / 'log'),
        }.get((section, key), '')
        mock_config.getboolean.return_value = True
        mock_load_config.return_value = mock_config

        automation = IPCLOrderAutomation()
        automation.csv_handler = Mock()
        automation.csv_handler.read_csv_file.side_effect = Exception("CSV read error")
        automation.save_service.move_csv_to_error = Mock()

        csv_path = tmp_path / "test.csv"
        csv_path.write_text("test,data\n1,2")

        # 例外が発生しても、関数は正常に終了し、ファイルをエラーフォルダに移動する
        automation.process_csv_file(csv_path)

        # CSVファイルがエラーフォルダに移動されることを確認
        automation.save_service.move_csv_to_error.assert_called_once_with(csv_path, error_dir)

    @patch('service.automation_service.Path.mkdir')
    @patch('service.automation_service.load_environment_variables')
    @patch('service.automation_service.load_config')
    @patch.dict(os.environ, {}, clear=True)
    def test_init_handles_missing_env_vars(self, mock_load_config, mock_load_env, mock_mkdir, mock_config):
        """環境変数が設定されていない場合の処理を確認"""
        mock_load_config.return_value = mock_config

        automation = IPCLOrderAutomation()

        # 環境変数が設定されていない場合でも初期化は成功する
        # 認証情報はauth_serviceに渡されており、IPCLOrderAutomationには保持されない
        assert automation.csv_handler is not None
        assert automation.browser_manager is not None
        assert automation.workflow_executor is not None

    @patch('service.automation_service.load_environment_variables')
    @patch('service.automation_service.load_config')
    @patch.dict(os.environ, {'EMAIL': 'test@example.com', 'PASSWORD': 'password123'})
    def test_init_with_frozen_sys(self, mock_load_config, mock_load_env, mock_config, tmp_path):
        """PyInstallerでフリーズされた状態での初期化を確認"""
        # CSVディレクトリを作成
        csv_dir = tmp_path / 'csv'
        csv_dir.mkdir(parents=True, exist_ok=True)

        mock_config.get.side_effect = lambda section, key: {
            ('URL', 'base_url'): 'https://example.com',
            ('Paths', 'csv_dir'): str(csv_dir),
            ('Paths', 'calculated_dir'): str(tmp_path / 'calculated'),
            ('Paths', 'error_dir'): str(tmp_path / 'error'),
            ('Paths', 'log_dir'): str(tmp_path / 'log'),
        }.get((section, key), '')
        mock_config.getboolean.return_value = True
        mock_load_config.return_value = mock_config

        # Playwrightブラウザディレクトリを作成
        playwright_dir = tmp_path / 'playwright' / 'driver' / 'package' / '.local-browsers'
        playwright_dir.mkdir(parents=True)

        with patch('sys.frozen', True, create=True):
            with patch('sys._MEIPASS', str(tmp_path), create=True):
                # 環境変数をクリア
                if 'PLAYWRIGHT_BROWSERS_PATH' in os.environ:
                    del os.environ['PLAYWRIGHT_BROWSERS_PATH']

                automation = IPCLOrderAutomation()

                # PLAYWRIGHT_BROWSERS_PATH環境変数が設定されることを確認
                assert 'PLAYWRIGHT_BROWSERS_PATH' in os.environ
                assert str(playwright_dir) in os.environ['PLAYWRIGHT_BROWSERS_PATH']
