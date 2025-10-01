"""
IPCL Lens Order Automation System
CSVÕ¡¤ëK‰£Çü¿’­¼IPCLè‡·¹ÆàkêÕe›Y‹×í°éà
"""

import csv
import os
import shutil
from pathlib import Path
from datetime import datetime
from playwright.sync_api import sync_playwright, Page, expect


class IPCLOrderAutomation:
    """IPCLè‡·¹ÆànêÕ¯é¹"""

    def __init__(self):
        self.base_url = "https://www.ipcl-jp.com/awsystem/order/create"
        self.email = "m-hosokawa@shinseikai.or.jp"
        self.password = "Shinseikai123!"
        self.csv_dir = Path(__file__).parent / "csv"
        self.calculated_dir = self.csv_dir / "calculated"

    def read_csv_file(self, csv_path: Path) -> dict:
        """
        CSVÕ¡¤ëK‰Çü¿’­¼€

        Args:
            csv_path: CSVÕ¡¤ënÑ¹

        Returns:
            £Çü¿nžø
        """
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            data = next(reader)

        # Çü¿’tb
        patient_data = {
            'name': data['name'],
            'id': data['ID'],
            'birthday': data['Birthday'],
            'surgery_date': data['surgerydate'],
            # ó<Çü¿
            'r_sph': data['R_SPH'],
            'r_cyl': data['R_Cyl'],
            'r_axis': data['R_Axis'],
            'r_acd': data['R_ACD'],
            'r_pachy': data['R_Pachy(CCT)'],
            'r_clr': data['R_CLR'],
            'r_k1': data['R_K1(Kf)'],
            'r_k1_axis': data['R_K1Axis'],
            'r_k2': data['R_K2(Kf)'],
            'r_sia': data['R_SIA'],
            'r_ins': data['R_Ins'],
            # æ<Çü¿
            'l_sph': data['L_SPH'],
            'l_cyl': data['L_Cyl'],
            'l_axis': data['L_Axis'],
            'l_acd': data['L_ACD'],
            'l_pachy': data['L_Pachy(CCT)'],
            'l_clr': data['L_CLR'],
            'l_k1': data['L_K1(Kf)'],
            'l_k1_axis': data['L_K1Axis'],
            'l_k2': data['L_K2(Kf)'],
            'l_sia': data['L_SIA'],
            'l_ins': data['L_Ins'],
            # ATA/WTW Çü¿
            'r_ata': data['R_\tATA'],
            'r_casia_wtw_m': data['R_CASIA_WTW_M'],
            'r_caliper_wtw': data['R_Caliper_WTW'],
            'l_ata': data['L_\tATA'],
            'l_casia_wtw_m': data['L_CASIA_WTW_M'],
            'l_caliper_wtw': data['L_Caliper_WTW'],
        }

        return patient_data

    def login(self, page: Page):
        """
        Webµ¤Èkí°¤óY‹

        Args:
            page: PlaywrightnÚü¸ªÖ¸§¯È
        """
        page.goto(self.base_url)
        page.wait_for_load_state('networkidle')

        # í°¤óÕ©üàke›
        page.fill('input[name="LoginForm[email]"]', self.email)
        page.fill('input[name="LoginForm[password]"]', self.password)
        page.click('button:has-text("µ¤ó¤ó")')
        page.wait_for_load_state('networkidle')

    def fill_patient_info(self, page: Page, data: dict):
        """
        £Å1’e›Y‹

        Args:
            page: PlaywrightnÚü¸ªÖ¸§¯È
            data: £Çü¿
        """
        # £ID’e›
        page.fill('input[name="OrderDetail[patient_id]"]', data['id'])

        # '%’xž7'	
        page.click('div:has(> input[name="OrderDetail[gender]"])')
        page.click('li:has-text("7'")')

        # KSå’e›
        page.fill('input[name="OrderDetail[surgery_date]"]', data['surgery_date'])

    def open_lens_calculator(self, page: Page):
        """
        ìóº—ûè‡âüÀë’‹O

        Args:
            page: PlaywrightnÚü¸ªÖ¸§¯È
        """
        page.click('button:has-text("ìóº—ûè‡")')
        page.wait_for_timeout(1000)

    def select_both_eyes_tab(self, page: Page):
        """
        !<¿Ö’xžWÐÃ¯¢Ã×ìóº¼’Á§Ã¯

        Args:
            page: PlaywrightnÚü¸ªÖ¸§¯È
        """
        frame = page.frame_locator('#calculatorFrame')
        frame.locator('a:has-text("!<")').click()

        # ÐÃ¯¢Ã×ìóº¼’Á§Ã¯
        backup_checkbox = frame.locator('input[name="OrderDetail[include_backup]"]')
        if not backup_checkbox.is_checked():
            backup_checkbox.check()

    def fill_measurement_data(self, page: Page, data: dict):
        """
        ó<ûæ<n,šÇü¿’e›Y‹

        Args:
            page: PlaywrightnÚü¸ªÖ¸§¯È
            data: £Çü¿
        """
        frame = page.frame_locator('#calculatorFrame')

        # ó<Çü¿
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

        # æ<Çü¿
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

    def select_lens_type(self, page: Page, data: dict):
        """
        Cyl$kúeDfìóº¿¤×’xžY‹

        Args:
            page: PlaywrightnÚü¸ªÖ¸§¯È
            data: £Çü¿
        """
        frame = page.frame_locator('#calculatorFrame')

        # ó<nìóº¿¤×’xž
        r_cyl = float(data['r_cyl'])
        if r_cyl == 0:
            frame.locator('input[name="OrderDetail[ipcl_r]"][value="IPCL V2.0 Mono"]').check()
        else:
            frame.locator('input[name="OrderDetail[ipcl_r]"][value="IPCL V2.0 Toric"]').check()

        # æ<nìóº¿¤×’xž
        l_cyl = float(data['l_cyl'])
        if l_cyl == 0:
            frame.locator('input[name="OrderDetail[ipcl_l]"][value="IPCL V2.0 Mono"]').check()
        else:
            frame.locator('input[name="OrderDetail[ipcl_l]"][value="IPCL V2.0 Toric"]').check()

    def fill_birthday(self, page: Page, birthday: str):
        """
        •å’«ìóÀüÔÃ«üge›Y‹

        Args:
            page: PlaywrightnÚü¸ªÖ¸§¯È
            birthday: •åMM/DD/YYYYb	
        """
        frame = page.frame_locator('#calculatorFrame')

        # åØÔÃ«ü’‹O
        frame.locator('span.input-group-addon:has(i.glyphicon-calendar)').first.click()
        page.wait_for_timeout(500)

        # •å’ãMM/DD/YYYY ’ DD, MM, YYYY	
        month, day, year = birthday.split('/')
        target_year = int(year)

        # t’xž2007K‰ît~ga‹	
        current_year = 2007
        while current_year > target_year:
            frame.locator('td.prev').first.click()
            page.wait_for_timeout(200)
            current_year -= 1

        # ’xž
        month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        month_name = month_names[int(month) - 1]
        frame.locator(f'span:has-text("{month_name}")').click()
        page.wait_for_timeout(500)

        # å’xž3jîåMn»ëK‰rSY‹å’¢Y	
        day_cells = frame.locator(f'td:has-text("{int(day)}")').all()
        for cell in day_cells:
            if cell.inner_text() == str(int(day)):
                cell.click()
                break

        page.wait_for_timeout(500)

    def fill_ata_wtw_data(self, page: Page, data: dict):
        """
        ATA/WTWÇü¿’e›Y‹

        Args:
            page: PlaywrightnÚü¸ªÖ¸§¯È
            data: £Çü¿
        """
        frame = page.frame_locator('#calculatorFrame')

        # ó<nATA/WTWÇü¿
        frame.locator('input[name="OrderDetail[r_ata]"]').fill(data['r_ata'])
        frame.locator('input[name="OrderDetail[r_casia_manual]"]').fill(data['r_casia_wtw_m'])
        frame.locator('input[name="OrderDetail[r_caliper_manual]"]').fill(data['r_caliper_wtw'])

        # æ<nATA/WTWÇü¿
        frame.locator('input[name="OrderDetail[l_ata]"]').fill(data['l_ata'])
        frame.locator('input[name="OrderDetail[l_casia_manual]"]').fill(data['l_casia_wtw_m'])
        frame.locator('input[name="OrderDetail[l_caliper_manual]"]').fill(data['l_caliper_wtw'])

    def calculate_lens(self, page: Page):
        """
        ìóº—’ŸLY‹

        Args:
            page: PlaywrightnÚü¸ªÖ¸§¯È
        """
        frame = page.frame_locator('#calculatorFrame')
        frame.locator('button:has-text("ìóº—")').click()
        page.wait_for_timeout(2000)  # —PœLh:UŒ‹~g…_

    def save_input(self, page: Page):
        """
        e›’ÝXY‹

        Args:
            page: PlaywrightnÚü¸ªÖ¸§¯È
        """
        frame = page.frame_locator('#calculatorFrame')
        frame.locator('button:has-text("e›ÝX")').click()
        page.wait_for_timeout(1000)

    def save_draft(self, page: Page):
        """
        øMÝXY‹

        Args:
            page: PlaywrightnÚü¸ªÖ¸§¯È
        """
        page.locator('button:has-text("øMÝX")').click()
        page.wait_for_load_state('networkidle')

    def move_csv_to_calculated(self, csv_path: Path):
        """
        æCSVÕ¡¤ë’calculatedÇ£ì¯ÈêkûÕY‹

        Args:
            csv_path: CSVÕ¡¤ënÑ¹
        """
        # calculatedÇ£ì¯ÈêLX(WjD4o\
        self.calculated_dir.mkdir(exist_ok=True)

        # Õ¡¤ë’ûÕ
        destination = self.calculated_dir / csv_path.name
        shutil.move(str(csv_path), str(destination))
        print(f" {csv_path.name} ’ calculated Ç£ì¯ÈêkûÕW~W_")

    def process_csv_file(self, csv_path: Path):
        """
        CSVÕ¡¤ë’æWfIPCLè‡’\Y‹

        Args:
            csv_path: CSVÕ¡¤ënÑ¹
        """
        print(f"\n{'='*60}")
        print(f"æ‹Ë: {csv_path.name}")
        print(f"{'='*60}")

        # CSVÇü¿’­¼
        print(" CSVÕ¡¤ë’­¼~W_")
        data = self.read_csv_file(csv_path)
        print(f"  £ID: {data['id']}, M: {data['name']}")

        # PlaywrightgÖé¦¶’wÕ
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)  # headless=Trueg^h:âüÉ
            context = browser.new_context()
            page = context.new_page()

            try:
                # í°¤ó
                print(" Webµ¤Èkí°¤óWfD~Y...")
                self.login(page)

                # £Å1’e›
                print(" £Å1’e›WfD~Y...")
                self.fill_patient_info(page, data)

                # ìóº—ûè‡âüÀë’‹O
                print(" ìóº—ûè‡’‹DfD~Y...")
                self.open_lens_calculator(page)

                # !<¿Ö’xž
                print(" !<¿Ö’xžWfD~Y...")
                self.select_both_eyes_tab(page)

                # £ID’e›âüÀë…	
                print(" £ID’e›WfD~Y...")
                frame = page.frame_locator('#calculatorFrame')
                frame.locator('input[name="OrderDetail[patient_id]"]').fill(data['id'])

                # •å’e›
                print(" •å’e›WfD~Y...")
                self.fill_birthday(page, data['birthday'])

                # ,šÇü¿’e›
                print(" ,šÇü¿’e›WfD~Y...")
                self.fill_measurement_data(page, data)

                # ìóº¿¤×’xž
                print(" ìóº¿¤×’xžWfD~Y...")
                self.select_lens_type(page, data)

                # ATA/WTWÇü¿’e›
                print(" ATA/WTWÇü¿’e›WfD~Y...")
                self.fill_ata_wtw_data(page, data)

                # ìóº—’ŸL
                print(" ìóº—’ŸLWfD~Y...")
                self.calculate_lens(page)

                # e›’ÝX
                print(" e›’ÝXWfD~Y...")
                self.save_input(page)

                # øMÝX
                print(" øMÝXWfD~Y...")
                self.save_draft(page)

                print(" è‡nøMLc8kÝXUŒ~W_")

            except Exception as e:
                print(f" ¨éüLzW~W_: {e}")
                raise

            finally:
                # Öé¦¶’‰X‹MkW…_
                page.wait_for_timeout(2000)
                browser.close()

        # CSVÕ¡¤ë’ûÕ
        self.move_csv_to_calculated(csv_path)

        print(f"{'='*60}")
        print(f"æŒ†: {csv_path.name}")
        print(f"{'='*60}\n")

    def process_all_csv_files(self):
        """
        csvÇ£ì¯Èê…nYyfnCSVÕ¡¤ë’æY‹
        """
        csv_files = list(self.csv_dir.glob('IPCLdata_*.csv'))

        if not csv_files:
            print("æY‹CSVÕ¡¤ëL‹dKŠ~[“gW_")
            return

        print(f"\n{len(csv_files)}önCSVÕ¡¤ë’æW~Y")

        for csv_file in csv_files:
            self.process_csv_file(csv_file)

        print("\nYyfnÕ¡¤ënæLŒ†W~W_")


def main():
    """á¤óæ"""
    automation = IPCLOrderAutomation()
    automation.process_all_csv_files()


if __name__ == "__main__":
    main()
