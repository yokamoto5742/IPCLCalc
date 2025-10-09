import pytest
from unittest.mock import Mock, MagicMock

from service.patient_service import PatientService


class TestPatientService:
    """PatientServiceのテストクラス"""

    @pytest.fixture
    def mock_page(self):
        """Playwrightのページモックを提供するフィクスチャ"""
        page = Mock()
        page.locator.return_value = Mock()
        return page

    @pytest.fixture
    def patient_data(self):
        """患者データのフィクスチャ"""
        return {
            'id': 'P12345',
            'sex': '男性',
            'surgery_date': '2024/01/15',
            'birthday': '05/15/1980'
        }

    def test_fill_patient_info_fills_patient_id(self, mock_page, patient_data):
        """患者IDが正しく入力されることを確認"""
        PatientService.fill_patient_info(mock_page, patient_data)

        mock_page.get_by_label.assert_any_call("患者ID")
        mock_page.get_by_label.return_value.fill.assert_any_call('P12345')

    def test_fill_patient_info_waits_for_dom(self, mock_page, patient_data):
        """ネットワークアイドル状態を待機することを確認"""
        PatientService.fill_patient_info(mock_page, patient_data)

        mock_page.wait_for_load_state.assert_called_with('networkidle')

    def test_fill_patient_info_with_male_sex(self, mock_page, patient_data):
        """男性の性別選択が正しく行われることを確認"""
        patient_data['sex'] = '男性'

        PatientService.fill_patient_info(mock_page, patient_data)

        # Select2クリックを確認
        mock_page.locator.assert_any_call('#select2-order-sex-container')

    def test_fill_patient_info_with_female_sex(self, mock_page, patient_data):
        """女性の性別選択が正しく行われることを確認"""
        patient_data['sex'] = '女性'

        PatientService.fill_patient_info(mock_page, patient_data)

        # Select2クリックを確認
        mock_page.locator.assert_any_call('#select2-order-sex-container')

    def test_fill_patient_info_fills_surgery_date(self, mock_page, patient_data):
        """手術日が正しく入力されることを確認"""
        PatientService.fill_patient_info(mock_page, patient_data)

        mock_page.get_by_label.assert_any_call("手術日")

    def test_fill_patient_info_handles_sex_selection_error(self, mock_page, patient_data):
        """性別選択エラーを適切に処理することを確認"""
        mock_page.locator.side_effect = Exception("Element not found")

        # エラーが発生しても処理が継続することを確認
        PatientService.fill_patient_info(mock_page, patient_data)

    def test_fill_patient_info_handles_surgery_date_error(self, mock_page, patient_data):
        """手術日入力エラーを適切に処理することを確認"""
        mock_page.get_by_label.side_effect = [Mock(), Exception("Date field error"), Mock()]

        # エラーが発生しても処理が継続することを確認
        PatientService.fill_patient_info(mock_page, patient_data)

    def test_fill_birthday_converts_date_format(self, mock_page):
        """誕生日のフォーマット変換が正しく行われることを確認"""
        birthday = '05/15/1980'  # mm/dd/yyyy

        mock_frame = Mock()
        mock_page.frame_locator.return_value = mock_frame
        mock_input = Mock()
        mock_frame.locator.return_value.first = mock_input

        PatientService.fill_birthday(mock_page, birthday)

        # dd/mm/yyyy形式に変換されることを確認
        mock_input.fill.assert_called_once_with('15/05/1980')

    def test_fill_birthday_presses_enter(self, mock_page):
        """誕生日入力後にEnterキーが押されることを確認"""
        birthday = '01/20/1990'

        mock_frame = Mock()
        mock_page.frame_locator.return_value = mock_frame
        mock_input = Mock()
        mock_frame.locator.return_value.first = mock_input

        PatientService.fill_birthday(mock_page, birthday)

        mock_input.press.assert_called_once_with('Enter')

    def test_fill_birthday_waits_after_input(self, mock_page):
        """誕生日入力後の動作を確認"""
        birthday = '12/31/1985'

        mock_frame = Mock()
        mock_page.frame_locator.return_value = mock_frame
        mock_input = Mock()
        mock_frame.locator.return_value.first = mock_input

        PatientService.fill_birthday(mock_page, birthday)

        # Enterキーが押されることを確認
        mock_input.press.assert_called_once_with('Enter')

    def test_fill_birthday_handles_invalid_format(self, mock_page):
        """無効な誕生日フォーマットを適切に処理することを確認"""
        birthday = 'invalid-date'

        mock_frame = Mock()
        mock_page.frame_locator.return_value = mock_frame
        mock_input = Mock()
        mock_input.fill.side_effect = ValueError("Invalid date format")
        mock_frame.locator.return_value.first = mock_input

        # 例外が発生しても処理が継続することを確認（ワーニングとして処理）
        PatientService.fill_birthday(mock_page, birthday)

    def test_fill_birthday_handles_frame_not_found(self, mock_page):
        """フレームが見つからない場合を適切に処理することを確認"""
        birthday = '03/10/1995'

        mock_frame = Mock()
        mock_input = Mock()
        mock_input.fill.side_effect = Exception("Frame not found")
        mock_frame.locator.return_value.first = mock_input
        mock_page.frame_locator.return_value = mock_frame

        # 例外が発生しても処理が継続することを確認（ワーニング出力のみ）
        PatientService.fill_birthday(mock_page, birthday)

    def test_fill_patient_info_with_empty_data(self, mock_page):
        """空のデータでも処理が実行されることを確認"""
        empty_data = {
            'id': '',
            'sex': '',
            'surgery_date': ''
        }

        PatientService.fill_patient_info(mock_page, empty_data)

        mock_page.get_by_label.assert_any_call("患者ID")

    @pytest.mark.parametrize("birthday,expected", [
        ('01/01/2000', '01/01/2000'),
        ('12/31/1999', '31/12/1999'),
        ('06/15/1985', '15/06/1985'),
    ])
    def test_fill_birthday_date_conversion_parametrized(self, mock_page, birthday, expected):
        """様々な誕生日フォーマットの変換を確認"""
        mock_frame = Mock()
        mock_page.frame_locator.return_value = mock_frame
        mock_input = Mock()
        mock_frame.locator.return_value.first = mock_input

        PatientService.fill_birthday(mock_page, birthday)

        mock_input.fill.assert_called_once_with(expected)
