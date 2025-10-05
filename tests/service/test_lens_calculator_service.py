import pytest
from unittest.mock import Mock

from service.lens_calculator_service import LensCalculatorService


class TestLensCalculatorService:
    """LensCalculatorServiceのテストクラス"""

    @pytest.fixture
    def mock_page(self):
        """Playwrightのページモックを提供するフィクスチャ"""
        return Mock()

    @pytest.fixture
    def mock_frame(self, mock_page):
        """フレームモックを提供するフィクスチャ"""
        frame = Mock()
        mock_page.frame_locator.return_value = frame
        return frame

    @pytest.fixture
    def measurement_data(self):
        """測定データのフィクスチャ"""
        return {
            'r_sph': '-5.00', 'r_cyl': '-1.50', 'r_axis': '90',
            'r_acd': '3.2', 'r_pachy': '520', 'r_clr': '12.0',
            'r_k1': '43.5', 'r_k1_axis': '180', 'r_k2': '44.0',
            'r_sia': '0.5', 'r_ins': '11.0',
            'l_sph': '-4.00', 'l_cyl': '-1.00', 'l_axis': '85',
            'l_acd': '3.1', 'l_pachy': '515', 'l_clr': '11.8',
            'l_k1': '43.2', 'l_k1_axis': '175', 'l_k2': '43.8',
            'l_sia': '0.4', 'l_ins': '10.8',
        }

    @pytest.fixture
    def ata_wtw_data(self):
        """ATA/WTWデータのフィクスチャ"""
        return {
            'r_ata': '5.0', 'r_casia_wtw_m': '11.5', 'r_caliper_wtw': '11.6',
            'l_ata': '5.1', 'l_casia_wtw_m': '11.4', 'l_caliper_wtw': '11.5',
        }

    def test_open_lens_calculator_clicks_button(self, mock_page):
        """レンズ計算・注文ボタンがクリックされることを確認"""
        LensCalculatorService.open_lens_calculator(mock_page)

        mock_page.click.assert_called_once_with('button:has-text("レンズ計算・注文")')

    def test_open_lens_calculator_waits_after_click(self, mock_page):
        """レンズ計算・注文ボタンクリック後に待機することを確認"""
        LensCalculatorService.open_lens_calculator(mock_page)

        mock_page.wait_for_timeout.assert_called_once_with(1000)

    def test_select_eye_tab_both_eyes(self, mock_page, mock_frame):
        """両眼タブを選択することを確認"""
        mock_checkbox = Mock()
        mock_checkbox.is_checked.return_value = False
        mock_frame.locator.return_value = mock_checkbox

        LensCalculatorService.select_eye_tab(mock_page, '両眼')

        mock_frame.locator.assert_any_call('a:has-text("両眼")')
        mock_frame.locator.return_value.click.assert_called()

    def test_select_eye_tab_both_eyes_checks_backup(self, mock_page, mock_frame):
        """両眼選択時にバックアップチェックボックスがチェックされることを確認"""
        mock_checkbox = Mock()
        mock_checkbox.is_checked.return_value = False
        mock_frame.locator.return_value = mock_checkbox

        LensCalculatorService.select_eye_tab(mock_page, '両眼')

        mock_checkbox.check.assert_called_once()

    def test_select_eye_tab_both_eyes_skips_if_already_checked(self, mock_page, mock_frame):
        """バックアップチェックボックスが既にチェック済みの場合はスキップすることを確認"""
        mock_checkbox = Mock()
        mock_checkbox.is_checked.return_value = True
        mock_frame.locator.return_value = mock_checkbox

        LensCalculatorService.select_eye_tab(mock_page, '両眼')

        mock_checkbox.check.assert_not_called()

    def test_select_eye_tab_right_eye(self, mock_page, mock_frame):
        """右眼タブを選択することを確認"""
        LensCalculatorService.select_eye_tab(mock_page, '右眼')

        mock_frame.locator.assert_called_with('a:has-text("右眼")')
        mock_frame.locator.return_value.click.assert_called()

    def test_select_eye_tab_left_eye(self, mock_page, mock_frame):
        """左眼タブを選択することを確認"""
        LensCalculatorService.select_eye_tab(mock_page, '左眼')

        mock_frame.locator.assert_called_with('a:has-text("左眼")')
        mock_frame.locator.return_value.click.assert_called()

    def test_select_eye_tab_waits_after_selection(self, mock_page, mock_frame):
        """タブ選択後に待機することを確認"""
        LensCalculatorService.select_eye_tab(mock_page, '右眼')

        mock_page.wait_for_timeout.assert_called_once_with(500)

    def test_fill_measurement_data_both_eyes(self, mock_page, mock_frame, measurement_data):
        """両眼の測定データが入力されることを確認"""
        LensCalculatorService.fill_measurement_data(mock_page, measurement_data, '両眼')

        # 右眼データ
        mock_frame.locator.assert_any_call('input[name="OrderDetail[r_spherical]"]')
        mock_frame.locator.assert_any_call('input[name="OrderDetail[r_cylinder]"]')

        # 左眼データ
        mock_frame.locator.assert_any_call('input[name="OrderDetail[l_spherical]"]')
        mock_frame.locator.assert_any_call('input[name="OrderDetail[l_cylinder]"]')

    def test_fill_measurement_data_right_eye_only(self, mock_page, mock_frame, measurement_data):
        """右眼のみの測定データが入力されることを確認"""
        LensCalculatorService.fill_measurement_data(mock_page, measurement_data, '右眼')

        # 右眼データのみ入力されることを確認
        mock_frame.locator.assert_any_call('input[name="OrderDetail[r_spherical]"]')

        # 左眼データは入力されないことを確認（呼び出し回数で判定）
        left_eye_calls = [call for call in mock_frame.locator.call_args_list
                         if 'l_spherical' in str(call)]
        assert len(left_eye_calls) == 0

    def test_fill_measurement_data_left_eye_only(self, mock_page, mock_frame, measurement_data):
        """左眼のみの測定データが入力されることを確認"""
        LensCalculatorService.fill_measurement_data(mock_page, measurement_data, '左眼')

        # 左眼データのみ入力されることを確認
        mock_frame.locator.assert_any_call('input[name="OrderDetail[l_spherical]"]')

        # 右眼データは入力されないことを確認
        right_eye_calls = [call for call in mock_frame.locator.call_args_list
                          if 'r_spherical' in str(call)]
        assert len(right_eye_calls) == 0

    def test_select_lens_type_mono_for_zero_cylinder(self, mock_page, mock_frame):
        """乱視度数が0の場合にMonoレンズが選択されることを確認"""
        data = {'r_cyl': '0', 'l_cyl': '0'}

        LensCalculatorService.select_lens_type(mock_page, data, '両眼')

        mock_frame.locator.assert_any_call('input[name="OrderDetail[ipcl_r]"][value="IPCL V2.0 Mono"]')
        mock_frame.locator.assert_any_call('input[name="OrderDetail[ipcl_l]"][value="IPCL V2.0 Mono"]')

    def test_select_lens_type_toric_for_nonzero_cylinder(self, mock_page, mock_frame):
        """乱視度数が0以外の場合にToricレンズが選択されることを確認"""
        data = {'r_cyl': '-1.5', 'l_cyl': '-1.0'}

        LensCalculatorService.select_lens_type(mock_page, data, '両眼')

        mock_frame.locator.assert_any_call('input[name="OrderDetail[ipcl_r]"][value="IPCL V2.0 Toric"]')
        mock_frame.locator.assert_any_call('input[name="OrderDetail[ipcl_l]"][value="IPCL V2.0 Toric"]')

    def test_select_lens_type_mixed_mono_toric(self, mock_page, mock_frame):
        """片眼がMono、もう片眼がToricの場合の選択を確認"""
        data = {'r_cyl': '0', 'l_cyl': '-1.5'}

        LensCalculatorService.select_lens_type(mock_page, data, '両眼')

        mock_frame.locator.assert_any_call('input[name="OrderDetail[ipcl_r]"][value="IPCL V2.0 Mono"]')
        mock_frame.locator.assert_any_call('input[name="OrderDetail[ipcl_l]"][value="IPCL V2.0 Toric"]')

    def test_select_lens_type_right_eye_only(self, mock_page, mock_frame):
        """右眼のみのレンズタイプ選択を確認"""
        data = {'r_cyl': '-1.0', 'l_cyl': '0'}

        LensCalculatorService.select_lens_type(mock_page, data, '右眼')

        # 右眼のみ選択されることを確認
        right_eye_calls = [call for call in mock_frame.locator.call_args_list
                          if 'ipcl_r' in str(call)]
        assert len(right_eye_calls) > 0

        # 左眼は選択されないことを確認
        left_eye_calls = [call for call in mock_frame.locator.call_args_list
                         if 'ipcl_l' in str(call)]
        assert len(left_eye_calls) == 0

    def test_fill_ata_wtw_data_both_eyes(self, mock_page, mock_frame, ata_wtw_data):
        """両眼のATA/WTWデータが入力されることを確認"""
        LensCalculatorService.fill_ata_wtw_data(mock_page, ata_wtw_data, '両眼')

        # 右眼データ
        mock_frame.locator.assert_any_call('input[name="OrderDetail[r_ata]"]')
        mock_frame.locator.assert_any_call('input[name="OrderDetail[r_casia_manual]"]')
        mock_frame.locator.assert_any_call('input[name="OrderDetail[r_caliper_manual]"]')

        # 左眼データ
        mock_frame.locator.assert_any_call('input[name="OrderDetail[l_ata]"]')
        mock_frame.locator.assert_any_call('input[name="OrderDetail[l_casia_manual]"]')
        mock_frame.locator.assert_any_call('input[name="OrderDetail[l_caliper_manual]"]')

    def test_fill_ata_wtw_data_right_eye_only(self, mock_page, mock_frame, ata_wtw_data):
        """右眼のみのATA/WTWデータが入力されることを確認"""
        LensCalculatorService.fill_ata_wtw_data(mock_page, ata_wtw_data, '右眼')

        # 右眼データのみ入力
        mock_frame.locator.assert_any_call('input[name="OrderDetail[r_ata]"]')

        # 左眼データは入力されない
        left_eye_calls = [call for call in mock_frame.locator.call_args_list
                         if 'l_ata' in str(call)]
        assert len(left_eye_calls) == 0

    def test_fill_ata_wtw_data_left_eye_only(self, mock_page, mock_frame, ata_wtw_data):
        """左眼のみのATA/WTWデータが入力されることを確認"""
        LensCalculatorService.fill_ata_wtw_data(mock_page, ata_wtw_data, '左眼')

        # 左眼データのみ入力
        mock_frame.locator.assert_any_call('input[name="OrderDetail[l_ata]"]')

        # 右眼データは入力されない
        right_eye_calls = [call for call in mock_frame.locator.call_args_list
                          if 'r_ata' in str(call)]
        assert len(right_eye_calls) == 0

    def test_click_calculate_button_clicks_and_waits(self, mock_page, mock_frame):
        """計算ボタンがクリックされ、待機することを確認"""
        LensCalculatorService.click_calculate_button(mock_page)

        mock_frame.locator.assert_called_once_with('button#btn-calculate')
        mock_frame.locator.return_value.click.assert_called_once()
        mock_page.wait_for_timeout.assert_called_once_with(1000)

    @pytest.mark.parametrize("eye,expected_tab", [
        ('両眼', '両眼'),
        ('右眼', '右眼'),
        ('左眼', '左眼'),
    ])
    def test_select_eye_tab_parametrized(self, mock_page, mock_frame, eye, expected_tab):
        """パラメータ化テスト: 各眼タブの選択を確認"""
        LensCalculatorService.select_eye_tab(mock_page, eye)

        mock_frame.locator.assert_any_call(f'a:has-text("{expected_tab}")')

    @pytest.mark.parametrize("cyl_value,expected_lens", [
        ('0', 'IPCL V2.0 Mono'),
        ('0.0', 'IPCL V2.0 Mono'),
        ('-1.0', 'IPCL V2.0 Toric'),
        ('-2.5', 'IPCL V2.0 Toric'),
        ('1.5', 'IPCL V2.0 Toric'),
    ])
    def test_select_lens_type_based_on_cylinder(self, mock_page, mock_frame, cyl_value, expected_lens):
        """パラメータ化テスト: 乱視度数に応じたレンズタイプ選択を確認"""
        data = {'r_cyl': cyl_value, 'l_cyl': '0'}

        LensCalculatorService.select_lens_type(mock_page, data, '右眼')

        mock_frame.locator.assert_called_with(f'input[name="OrderDetail[ipcl_r]"][value="{expected_lens}"]')
