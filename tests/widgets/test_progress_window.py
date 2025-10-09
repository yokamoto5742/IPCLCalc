from unittest.mock import Mock, patch

import pytest

from widgets.progress_window import ProgressWindow


class TestProgressWindow:
    """ProgressWindowのテストクラス"""

    def test_init_sets_attributes_to_none(self):
        """初期化時にすべての属性がNoneであることを確認"""
        progress = ProgressWindow()

        assert progress.root is None
        assert progress.progress_window is None
        assert progress.progress_label is None

    @patch('widgets.progress_window.tk.Tk')
    @patch('widgets.progress_window.tk.Toplevel')
    @patch('widgets.progress_window.tk.Label')
    def test_create_initializes_root(self, mock_label, mock_toplevel, mock_tk):
        """createメソッドがrootを初期化することを確認"""
        mock_root = Mock()
        mock_tk.return_value = mock_root
        mock_window = Mock()
        mock_window.winfo_screenwidth.return_value = 1920
        mock_window.winfo_screenheight.return_value = 1080
        mock_window.winfo_width.return_value = 500
        mock_window.winfo_height.return_value = 150
        mock_toplevel.return_value = mock_window
        mock_label_instance = Mock()
        mock_label.return_value = mock_label_instance

        progress = ProgressWindow()
        progress.create()

        mock_tk.assert_called_once()
        assert progress.root is not None
        mock_root.withdraw.assert_called_once()

    @patch('widgets.progress_window.tk.Tk')
    @patch('widgets.progress_window.tk.Toplevel')
    @patch('widgets.progress_window.tk.Label')
    def test_create_initializes_progress_window(self, mock_label, mock_toplevel, mock_tk):
        """createメソッドがprogress_windowを初期化することを確認"""
        mock_root = Mock()
        mock_tk.return_value = mock_root
        mock_window = Mock()
        mock_window.winfo_screenwidth.return_value = 1920
        mock_window.winfo_screenheight.return_value = 1080
        mock_window.winfo_width.return_value = 500
        mock_window.winfo_height.return_value = 150
        mock_toplevel.return_value = mock_window
        mock_label_instance = Mock()
        mock_label.return_value = mock_label_instance

        progress = ProgressWindow()
        progress.create()

        mock_toplevel.assert_called_once_with(mock_root)
        assert progress.progress_window is not None
        mock_window.title.assert_called_once_with("進行状況")
        mock_window.geometry.assert_called()

    @patch('widgets.progress_window.load_config')
    @patch('widgets.progress_window.tk.Tk')
    @patch('widgets.progress_window.tk.Toplevel')
    @patch('widgets.progress_window.tk.Label')
    def test_create_sets_window_geometry(self, mock_label, mock_toplevel, mock_tk, mock_load_config):
        """createメソッドがウィンドウのジオメトリを設定することを確認"""
        # 設定のモック
        mock_config = Mock()
        mock_config.getint.side_effect = lambda section, key, fallback=None: {
            ('Appearance', 'font_size'): 11,
            ('Appearance', 'window_width'): 500,
            ('Appearance', 'window_height'): 150
        }.get((section, key), fallback)
        mock_load_config.return_value = mock_config

        mock_root = Mock()
        mock_tk.return_value = mock_root
        mock_window = Mock()
        mock_window.winfo_screenwidth.return_value = 1920
        mock_window.winfo_screenheight.return_value = 1080
        mock_window.winfo_width.return_value = 500
        mock_window.winfo_height.return_value = 150
        mock_toplevel.return_value = mock_window
        mock_label_instance = Mock()
        mock_label.return_value = mock_label_instance

        progress = ProgressWindow()
        progress.create()

        # geometry が少なくとも2回呼ばれることを確認（初期設定と中央配置）
        assert mock_window.geometry.call_count >= 2
        # 最初の呼び出しで window_width x window_height が設定される
        mock_window.geometry.assert_any_call("500x150")

    @patch('widgets.progress_window.tk.Tk')
    @patch('widgets.progress_window.tk.Toplevel')
    @patch('widgets.progress_window.tk.Label')
    def test_create_makes_window_not_resizable(self, mock_label, mock_toplevel, mock_tk):
        """createメソッドがウィンドウをリサイズ不可に設定することを確認"""
        mock_root = Mock()
        mock_tk.return_value = mock_root
        mock_window = Mock()
        mock_window.winfo_screenwidth.return_value = 1920
        mock_window.winfo_screenheight.return_value = 1080
        mock_window.winfo_width.return_value = 500
        mock_window.winfo_height.return_value = 150
        mock_toplevel.return_value = mock_window
        mock_label_instance = Mock()
        mock_label.return_value = mock_label_instance

        progress = ProgressWindow()
        progress.create()

        mock_window.resizable.assert_called_once_with(False, False)

    @patch('widgets.progress_window.tk.Tk')
    @patch('widgets.progress_window.tk.Toplevel')
    @patch('widgets.progress_window.tk.Label')
    def test_create_centers_window_on_screen(self, mock_label, mock_toplevel, mock_tk):
        """createメソッドがウィンドウを画面中央に配置することを確認"""
        mock_root = Mock()
        mock_tk.return_value = mock_root
        mock_window = Mock()
        mock_window.winfo_screenwidth.return_value = 1920
        mock_window.winfo_screenheight.return_value = 1080
        mock_window.winfo_width.return_value = 500
        mock_window.winfo_height.return_value = 150
        mock_toplevel.return_value = mock_window
        mock_label_instance = Mock()
        mock_label.return_value = mock_label_instance

        progress = ProgressWindow()
        progress.create()

        # 中央配置のため、x = (1920 // 2) - (500 // 2) = 960 - 250 = 710
        # y = (1080 // 2) - (150 // 2) = 540 - 75 = 465
        expected_geometry = "500x150+710+465"
        mock_window.geometry.assert_any_call(expected_geometry)

    @patch('widgets.progress_window.tk.Tk')
    @patch('widgets.progress_window.tk.Toplevel')
    @patch('widgets.progress_window.tk.Label')
    def test_create_initializes_progress_label(self, mock_label, mock_toplevel, mock_tk):
        """createメソッドがprogress_labelを初期化することを確認"""
        mock_root = Mock()
        mock_tk.return_value = mock_root
        mock_window = Mock()
        mock_window.winfo_screenwidth.return_value = 1920
        mock_window.winfo_screenheight.return_value = 1080
        mock_window.winfo_width.return_value = 500
        mock_window.winfo_height.return_value = 150
        mock_toplevel.return_value = mock_window
        mock_label_instance = Mock()
        mock_label.return_value = mock_label_instance

        progress = ProgressWindow()
        progress.create()

        mock_label.assert_called_once()
        assert progress.progress_label is not None
        mock_label_instance.pack.assert_called_once_with(expand=True, fill='both')

    @patch('widgets.progress_window.tk.Tk')
    @patch('widgets.progress_window.tk.Toplevel')
    @patch('widgets.progress_window.tk.Label')
    def test_create_sets_default_label_text(self, mock_label, mock_toplevel, mock_tk):
        """createメソッドがデフォルトのラベルテキストを設定することを確認"""
        mock_root = Mock()
        mock_tk.return_value = mock_root
        mock_window = Mock()
        mock_window.winfo_screenwidth.return_value = 1920
        mock_window.winfo_screenheight.return_value = 1080
        mock_window.winfo_width.return_value = 500
        mock_window.winfo_height.return_value = 150
        mock_toplevel.return_value = mock_window
        mock_label_instance = Mock()
        mock_label.return_value = mock_label_instance

        progress = ProgressWindow()
        progress.create()

        # Labelが正しいテキストで呼ばれているか確認
        call_kwargs = mock_label.call_args[1]
        assert call_kwargs['text'] == "計算処理を開始します..."

    @patch('widgets.progress_window.tk.Tk')
    @patch('widgets.progress_window.tk.Toplevel')
    @patch('widgets.progress_window.tk.Label')
    def test_create_calls_update_on_window(self, mock_label, mock_toplevel, mock_tk):
        """createメソッドがウィンドウのupdateを呼び出すことを確認"""
        mock_root = Mock()
        mock_tk.return_value = mock_root
        mock_window = Mock()
        mock_window.winfo_screenwidth.return_value = 1920
        mock_window.winfo_screenheight.return_value = 1080
        mock_window.winfo_width.return_value = 500
        mock_window.winfo_height.return_value = 150
        mock_toplevel.return_value = mock_window
        mock_label_instance = Mock()
        mock_label.return_value = mock_label_instance

        progress = ProgressWindow()
        progress.create()

        mock_window.update.assert_called()
        mock_window.update_idletasks.assert_called_once()

    def test_update_changes_label_text(self):
        """updateメソッドがラベルのテキストを変更することを確認"""
        progress = ProgressWindow()
        progress.progress_label = Mock()
        progress.progress_window = Mock()

        progress.update("新しいメッセージ")

        progress.progress_label.config.assert_called_once_with(text="新しいメッセージ")

    def test_update_calls_window_update(self):
        """updateメソッドがウィンドウのupdateを呼び出すことを確認"""
        progress = ProgressWindow()
        progress.progress_label = Mock()
        progress.progress_window = Mock()

        progress.update("テストメッセージ")

        progress.progress_window.update.assert_called_once()

    def test_update_does_nothing_when_label_is_none(self):
        """progress_labelがNoneの場合、updateメソッドが何もしないことを確認"""
        progress = ProgressWindow()
        progress.progress_label = None
        progress.progress_window = Mock()

        # エラーが発生しないことを確認
        progress.update("テストメッセージ")

        # progress_windowのupdateが呼ばれないことを確認
        progress.progress_window.update.assert_not_called()

    def test_close_destroys_progress_window(self):
        """closeメソッドがprogress_windowを破棄することを確認"""
        progress = ProgressWindow()
        progress.progress_window = Mock()
        progress.root = Mock()

        progress.close()

        progress.progress_window.destroy.assert_called_once()

    def test_close_destroys_root(self):
        """closeメソッドがrootを破棄することを確認"""
        progress = ProgressWindow()
        progress.progress_window = Mock()
        progress.root = Mock()

        progress.close()

        progress.root.destroy.assert_called_once()

    def test_close_handles_none_progress_window(self):
        """progress_windowがNoneの場合、closeメソッドがエラーを起こさないことを確認"""
        progress = ProgressWindow()
        progress.progress_window = None
        progress.root = Mock()

        # エラーが発生しないことを確認
        progress.close()

        progress.root.destroy.assert_called_once()

    def test_close_handles_none_root(self):
        """rootがNoneの場合、closeメソッドがエラーを起こさないことを確認"""
        progress = ProgressWindow()
        progress.progress_window = Mock()
        progress.root = None

        # エラーが発生しないことを確認
        progress.close()

        progress.progress_window.destroy.assert_called_once()

    def test_close_handles_all_none_values(self):
        """すべての属性がNoneの場合、closeメソッドがエラーを起こさないことを確認"""
        progress = ProgressWindow()
        progress.progress_window = None
        progress.root = None

        # エラーが発生しないことを確認
        progress.close()
