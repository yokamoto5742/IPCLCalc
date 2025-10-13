from unittest.mock import Mock, patch, MagicMock

import pytest

from service.save_service import SaveService


class TestSaveService:
    """SaveServiceのテストクラス"""

    @pytest.fixture
    def temp_dirs(self, tmp_path):
        """一時ディレクトリを提供するフィクスチャ"""
        pdf_dir = tmp_path / "pdf"
        calculated_dir = tmp_path / "calculated"
        pdf_dir.mkdir()
        calculated_dir.mkdir()
        return pdf_dir, calculated_dir

    @pytest.fixture
    def save_service(self, temp_dirs):
        """SaveServiceインスタンスを提供するフィクスチャ"""
        pdf_dir, calculated_dir = temp_dirs
        return SaveService(pdf_dir, calculated_dir)

    @pytest.fixture
    def mock_page(self):
        """Playwrightのページモックを提供するフィクスチャ"""
        return Mock()

    def test_init_stores_directories(self, temp_dirs):
        """初期化時にディレクトリが正しく保存されることを確認"""
        pdf_dir, calculated_dir = temp_dirs
        service = SaveService(pdf_dir, calculated_dir)

        assert service.pdf_dir == pdf_dir
        assert service.calculated_dir == calculated_dir

    def test_click_save_pdf_button_downloads_pdf(self, save_service, mock_page, temp_dirs):
        """PDFダウンロードが正しく実行されることを確認"""
        pdf_dir, _ = temp_dirs
        mock_frame = Mock()
        mock_page.frame_locator.return_value = mock_frame

        # ダウンロード情報のモック
        mock_download = Mock()
        mock_download.path.return_value = "/tmp/download.pdf"
        mock_download.suggested_filename = "report.pdf"

        # expect_downloadのモック - MagicMockを使用してコンテキストマネージャーをサポート
        mock_download_context = MagicMock()
        mock_download_context.__enter__.return_value = mock_download_context
        mock_download_context.__exit__.return_value = None
        mock_download_context.value = mock_download
        mock_page.expect_download.return_value = mock_download_context

        result = save_service.click_save_pdf_button(mock_page, "P12345", "山田太郎")

        # PDFボタンがクリックされたことを確認
        mock_frame.locator.assert_called_once_with('a:has(i.far.fa-file-pdf)')
        mock_frame.locator.return_value.click.assert_called_once()

        # ファイルが保存されたことを確認
        mock_download.save_as.assert_called_once()
        assert result.startswith(str(pdf_dir))
        assert "IPCLdata_IDP12345" in result

    def test_click_save_pdf_button_filename_format(self, save_service, mock_page, temp_dirs):
        """PDFファイル名のフォーマットが正しいことを確認"""
        pdf_dir, _ = temp_dirs
        mock_frame = Mock()
        mock_page.frame_locator.return_value = mock_frame

        mock_download = Mock()
        mock_download.path.return_value = "/tmp/download.pdf"
        mock_download.suggested_filename = "report.pdf"

        mock_download_context = MagicMock()
        mock_download_context.__enter__.return_value = mock_download_context
        mock_download_context.__exit__.return_value = None
        mock_download_context.value = mock_download
        mock_page.expect_download.return_value = mock_download_context

        with patch('service.save_service.datetime') as mock_datetime:
            mock_datetime.now.return_value.strftime.return_value = '20240115_120000'
            result = save_service.click_save_pdf_button(mock_page, "TEST001", "テスト患者")

        expected_filename = "IPCLdata_IDTEST001_20240115_120000.pdf"
        assert expected_filename in result

    def test_click_save_pdf_button_raises_exception_on_error(self, save_service, mock_page):
        """PDFダウンロード時のエラーを適切に処理することを確認"""
        mock_frame = Mock()
        mock_page.frame_locator.return_value = mock_frame

        # expect_downloadが例外を発生させる
        mock_download_context = MagicMock()
        mock_download_context.__enter__.side_effect = Exception("Download failed")
        mock_page.expect_download.return_value = mock_download_context

        with pytest.raises(Exception, match="Download failed"):
            save_service.click_save_pdf_button(mock_page, "P001", "患者名")

    def test_save_input_clicks_save_button(self, mock_page):
        """入力保存ボタンがクリックされることを確認"""
        mock_frame = Mock()
        mock_page.frame_locator.return_value = mock_frame

        SaveService.save_input(mock_page)

        mock_frame.locator.assert_called_once_with('button#btn-save-draft-modal')
        mock_frame.locator.return_value.click.assert_called_once()

    def test_save_input_waits_after_click(self, mock_page):
        """入力保存後の動作を確認"""
        mock_frame = Mock()
        mock_page.frame_locator.return_value = mock_frame

        SaveService.save_input(mock_page)

        # ボタンがクリックされることを確認
        mock_frame.locator.return_value.click.assert_called_once()

    def test_save_draft_returns_true_on_success(self, mock_page):
        """下書き保存が成功した場合にTrueを返すことを確認"""
        mock_button = Mock()
        mock_button.is_disabled.return_value = False
        mock_page.locator.return_value = mock_button

        result = SaveService.save_draft(mock_page)

        assert result is True
        mock_button.click.assert_called_once()

    def test_save_draft_returns_false_when_button_disabled(self, mock_page):
        """ボタンが無効な場合にFalseを返すことを確認"""
        mock_button = Mock()
        mock_button.is_disabled.return_value = True
        mock_page.locator.return_value = mock_button

        result = SaveService.save_draft(mock_page)

        assert result is False
        mock_button.click.assert_not_called()

    def test_save_draft_waits_for_button_visibility(self, mock_page):
        """下書き保存ボタンの表示を待機することを確認"""
        mock_button = Mock()
        mock_button.is_disabled.return_value = False
        mock_page.locator.return_value = mock_button

        SaveService.save_draft(mock_page)

        mock_button.wait_for.assert_called_once_with(state='visible', timeout=2000)

    def test_save_draft_waits_before_clicking(self, mock_page):
        """下書き保存ボタンクリック後にネットワークアイドルを待機することを確認"""
        mock_button = Mock()
        mock_button.is_disabled.return_value = False
        mock_page.locator.return_value = mock_button

        SaveService.save_draft(mock_page)

        mock_page.wait_for_load_state.assert_called_with('networkidle')

    def test_save_draft_returns_false_on_exception(self, mock_page):
        """例外発生時にFalseを返すことを確認"""
        mock_page.locator.side_effect = Exception("Button not found")

        result = SaveService.save_draft(mock_page)

        assert result is False

    def test_move_csv_to_calculated_moves_file(self, save_service, temp_dirs, tmp_path):
        """CSVファイルがcalculatedディレクトリに移動されることを確認"""
        pdf_dir, calculated_dir = temp_dirs

        # テストCSVファイルを作成
        csv_path = tmp_path / "test_data.csv"
        csv_path.write_text("test,data\n1,2")

        save_service.move_csv_to_calculated(csv_path)

        # ファイルが移動されたことを確認
        assert not csv_path.exists()
        assert (calculated_dir / "test_data.csv").exists()

    def test_move_csv_to_calculated_creates_directory(self, save_service, temp_dirs, tmp_path):
        """calculatedディレクトリが存在しない場合に作成されることを確認"""
        pdf_dir, calculated_dir = temp_dirs

        # ディレクトリを削除
        calculated_dir.rmdir()

        # テストCSVファイルを作成
        csv_path = tmp_path / "test_data.csv"
        csv_path.write_text("test,data\n1,2")

        save_service.move_csv_to_calculated(csv_path)

        # ディレクトリが作成され、ファイルが移動されたことを確認
        assert calculated_dir.exists()
        assert (calculated_dir / "test_data.csv").exists()

    def test_move_csv_to_calculated_overwrites_existing_file(self, save_service, temp_dirs, tmp_path):
        """同名ファイルが存在する場合に上書きされることを確認"""
        pdf_dir, calculated_dir = temp_dirs

        # 既存ファイルを作成
        existing_file = calculated_dir / "test_data.csv"
        existing_file.write_text("old,data\n3,4")

        # 新しいCSVファイルを作成
        csv_path = tmp_path / "test_data.csv"
        csv_path.write_text("new,data\n5,6")

        save_service.move_csv_to_calculated(csv_path)

        # ファイルが上書きされたことを確認
        assert existing_file.read_text() == "new,data\n5,6"

    def test_click_save_pdf_button_with_special_characters_in_name(self, save_service, mock_page, temp_dirs):
        """特殊文字を含む患者名でPDFが保存できることを確認"""
        pdf_dir, _ = temp_dirs
        mock_frame = Mock()
        mock_page.frame_locator.return_value = mock_frame

        mock_download = Mock()
        mock_download.path.return_value = "/tmp/download.pdf"
        mock_download.suggested_filename = "report.pdf"

        mock_download_context = MagicMock()
        mock_download_context.__enter__.return_value = mock_download_context
        mock_download_context.__exit__.return_value = None
        mock_download_context.value = mock_download
        mock_page.expect_download.return_value = mock_download_context

        result = save_service.click_save_pdf_button(mock_page, "P001", "患者・名前（テスト）")

        assert "IPCLdata_IDP001" in result
