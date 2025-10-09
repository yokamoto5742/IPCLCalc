from playwright.sync_api import Page


class LensCalculatorService:
    @staticmethod
    def open_lens_calculator(page: Page):
        """レンズ計算・注文モーダルを開く"""
        page.click('button:has-text("レンズ計算・注文")')
        page.frame_locator('#calculatorFrame').locator('body').wait_for(state='visible')

    @staticmethod
    def select_eye_tab(page: Page, eye: str):
        """眼別タブを選択"""
        frame = page.frame_locator('#calculatorFrame')

        if eye == '両眼':
            frame.locator('a:has-text("両眼")').click()
            backup_checkbox = frame.locator('input[type="checkbox"][name="OrderDetail[include_backup]"]')
            if not backup_checkbox.is_checked():
                backup_checkbox.check()
        elif eye == '右眼':
            frame.locator('a:has-text("右眼")').click()
        elif eye == '左眼':
            frame.locator('a:has-text("左眼")').click()

    @staticmethod
    def fill_measurement_data(page: Page, data: dict, eye: str):
        """測定データを入力"""
        frame = page.frame_locator('#calculatorFrame')

        if eye in ['両眼', '右眼']:
            # 右眼データ
            frame.locator('input[name="OrderDetail[r_spherical]"]').fill(data['r_sph'])
            frame.locator('input[name="OrderDetail[r_cylinder]"]').fill(data['r_cyl'])
            frame.locator('input[name="OrderDetail[r_axis]"]').fill(data['r_axis'])
            frame.locator('input[name="OrderDetail[r_acd]"]').fill(data['r_acd'])
            frame.locator('input[name="OrderDetail[r_pachy]"]').fill(data['r_pachy'])
            frame.locator('input[name="OrderDetail[r_clr]"]').fill(data['r_clr'])
            frame.locator('input[name="OrderDetail[r_k1]"]').fill(data['r_k1'])
            frame.locator('input[name="OrderDetail[r_k1_axis]"]').fill(data['r_k1_axis'])
            frame.locator('input[name="OrderDetail[r_k2]"]').fill(data['r_k2'])
            frame.locator('input[name="OrderDetail[r_sia]"]').fill(data['r_sia'])
            frame.locator('input[name="OrderDetail[r_ins]"]').fill(data['r_ins'])

        if eye in ['両眼', '左眼']:
            # 左眼データ
            frame.locator('input[name="OrderDetail[l_spherical]"]').fill(data['l_sph'])
            frame.locator('input[name="OrderDetail[l_cylinder]"]').fill(data['l_cyl'])
            frame.locator('input[name="OrderDetail[l_axis]"]').fill(data['l_axis'])
            frame.locator('input[name="OrderDetail[l_acd]"]').fill(data['l_acd'])
            frame.locator('input[name="OrderDetail[l_pachy]"]').fill(data['l_pachy'])
            frame.locator('input[name="OrderDetail[l_clr]"]').fill(data['l_clr'])
            frame.locator('input[name="OrderDetail[l_k1]"]').fill(data['l_k1'])
            frame.locator('input[name="OrderDetail[l_k1_axis]"]').fill(data['l_k1_axis'])
            frame.locator('input[name="OrderDetail[l_k2]"]').fill(data['l_k2'])
            frame.locator('input[name="OrderDetail[l_sia]"]').fill(data['l_sia'])
            frame.locator('input[name="OrderDetail[l_ins]"]').fill(data['l_ins'])

    @staticmethod
    def select_lens_type(page: Page, data: dict, eye: str):
        """レンズタイプを選択"""
        frame = page.frame_locator('#calculatorFrame')

        if eye in ['両眼', '右眼']:
            r_cyl = float(data['r_cyl'])
            if r_cyl == 0:
                frame.locator('input[name="OrderDetail[ipcl_r]"][value="IPCL V2.0 Mono"]').check()
            else:
                frame.locator('input[name="OrderDetail[ipcl_r]"][value="IPCL V2.0 Toric"]').check()

        if eye in ['両眼', '左眼']:
            l_cyl = float(data['l_cyl'])
            if l_cyl == 0:
                frame.locator('input[name="OrderDetail[ipcl_l]"][value="IPCL V2.0 Mono"]').check()
            else:
                frame.locator('input[name="OrderDetail[ipcl_l]"][value="IPCL V2.0 Toric"]').check()

    @staticmethod
    def fill_ata_wtw_data(page: Page, data: dict, eye: str):
        """ATA/WTWデータを入力"""
        frame = page.frame_locator('#calculatorFrame')

        if eye in ['両眼', '右眼']:
            # 右眼のATA/WTWデータ
            frame.locator('input[name="OrderDetail[r_ata]"]').fill(data['r_ata'])
            frame.locator('input[name="OrderDetail[r_casia_manual]"]').fill(data['r_casia_wtw_m'])
            frame.locator('input[name="OrderDetail[r_caliper_manual]"]').fill(data['r_caliper_wtw'])

        if eye in ['両眼', '左眼']:
            # 左眼のATA/WTWデータ
            frame.locator('input[name="OrderDetail[l_ata]"]').fill(data['l_ata'])
            frame.locator('input[name="OrderDetail[l_casia_manual]"]').fill(data['l_casia_wtw_m'])
            frame.locator('input[name="OrderDetail[l_caliper_manual]"]').fill(data['l_caliper_wtw'])

    @staticmethod
    def click_calculate_button(page: Page):
        """計算ボタンをクリック"""
        frame = page.frame_locator('#calculatorFrame')
        frame.locator('button#btn-calculate').click()
