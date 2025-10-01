"""
IPCL Lens Order Automation System
CSVա��K��������IPCL臷���k��e�Y�����
"""

import csv
import os
import shutil
from pathlib import Path
from datetime import datetime
from playwright.sync_api import sync_playwright, Page, expect


class IPCLOrderAutomation:
    """IPCL臷���n����"""

    def __init__(self):
        self.base_url = "https://www.ipcl-jp.com/awsystem/order/create"
        self.email = "m-hosokawa@shinseikai.or.jp"
        self.password = "Shinseikai123!"
        self.csv_dir = Path(__file__).parent / "csv"
        self.calculated_dir = self.csv_dir / "calculated"

    def read_csv_file(self, csv_path: Path) -> dict:
        """
        CSVա��K��������

        Args:
            csv_path: CSVա��nѹ

        Returns:
            ����n��
        """
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            data = next(reader)

        # ����tb
        patient_data = {
            'name': data['name'],
            'id': data['ID'],
            'birthday': data['Birthday'],
            'surgery_date': data['surgerydate'],
            # �<���
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
            # �<���
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
            # ATA/WTW ���
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
        Web���k��Y�

        Args:
            page: Playwrightn����ָ���
        """
        page.goto(self.base_url)
        page.wait_for_load_state('networkidle')

        # ��թ��ke�
        page.fill('input[name="LoginForm[email]"]', self.email)
        page.fill('input[name="LoginForm[password]"]', self.password)
        page.click('button:has-text("����")')
        page.wait_for_load_state('networkidle')

    def fill_patient_info(self, page: Page, data: dict):
        """
        ��1�e�Y�

        Args:
            page: Playwrightn����ָ���
            data: ����
        """
        # �ID�e�
        page.fill('input[name="OrderDetail[patient_id]"]', data['id'])

        # '%�x�7'	
        page.click('div:has(> input[name="OrderDetail[gender]"])')
        page.click('li:has-text("7'")')

        # KS�e�
        page.fill('input[name="OrderDetail[surgery_date]"]', data['surgery_date'])

    def open_lens_calculator(self, page: Page):
        """
        ��������뒋O

        Args:
            page: Playwrightn����ָ���
        """
        page.click('button:has-text("�����")')
        page.wait_for_timeout(1000)

    def select_both_eyes_tab(self, page: Page):
        """
        !<�֒x�W�ï��������ï

        Args:
            page: Playwrightn����ָ���
        """
        frame = page.frame_locator('#calculatorFrame')
        frame.locator('a:has-text("!<")').click()

        # �ï��������ï
        backup_checkbox = frame.locator('input[name="OrderDetail[include_backup]"]')
        if not backup_checkbox.is_checked():
            backup_checkbox.check()

    def fill_measurement_data(self, page: Page, data: dict):
        """
        �<��<n,�����e�Y�

        Args:
            page: Playwrightn����ָ���
            data: ����
        """
        frame = page.frame_locator('#calculatorFrame')

        # �<���
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

        # �<���
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
        Cyl$k�eDf�󺿤גx�Y�

        Args:
            page: Playwrightn����ָ���
            data: ����
        """
        frame = page.frame_locator('#calculatorFrame')

        # �<n�󺿤גx�
        r_cyl = float(data['r_cyl'])
        if r_cyl == 0:
            frame.locator('input[name="OrderDetail[ipcl_r]"][value="IPCL V2.0 Mono"]').check()
        else:
            frame.locator('input[name="OrderDetail[ipcl_r]"][value="IPCL V2.0 Toric"]').check()

        # �<n�󺿤גx�
        l_cyl = float(data['l_cyl'])
        if l_cyl == 0:
            frame.locator('input[name="OrderDetail[ipcl_l]"][value="IPCL V2.0 Mono"]').check()
        else:
            frame.locator('input[name="OrderDetail[ipcl_l]"][value="IPCL V2.0 Toric"]').check()

    def fill_birthday(self, page: Page, birthday: str):
        """
        �咫�����ë�ge�Y�

        Args:
            page: Playwrightn����ָ���
            birthday: ��MM/DD/YYYYb	
        """
        frame = page.frame_locator('#calculatorFrame')

        # ���ë���O
        frame.locator('span.input-group-addon:has(i.glyphicon-calendar)').first.click()
        page.wait_for_timeout(500)

        # ���MM/DD/YYYY � DD, MM, YYYY	
        month, day, year = birthday.split('/')
        target_year = int(year)

        # t�x�2007K��t~ga�	
        current_year = 2007
        while current_year > target_year:
            frame.locator('td.prev').first.click()
            page.wait_for_timeout(200)
            current_year -= 1

        # �x�
        month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        month_name = month_names[int(month) - 1]
        frame.locator(f'span:has-text("{month_name}")').click()
        page.wait_for_timeout(500)

        # �x�3j��Mn��K�rSY�咢Y	
        day_cells = frame.locator(f'td:has-text("{int(day)}")').all()
        for cell in day_cells:
            if cell.inner_text() == str(int(day)):
                cell.click()
                break

        page.wait_for_timeout(500)

    def fill_ata_wtw_data(self, page: Page, data: dict):
        """
        ATA/WTW����e�Y�

        Args:
            page: Playwrightn����ָ���
            data: ����
        """
        frame = page.frame_locator('#calculatorFrame')

        # �<nATA/WTW���
        frame.locator('input[name="OrderDetail[r_ata]"]').fill(data['r_ata'])
        frame.locator('input[name="OrderDetail[r_casia_manual]"]').fill(data['r_casia_wtw_m'])
        frame.locator('input[name="OrderDetail[r_caliper_manual]"]').fill(data['r_caliper_wtw'])

        # �<nATA/WTW���
        frame.locator('input[name="OrderDetail[l_ata]"]').fill(data['l_ata'])
        frame.locator('input[name="OrderDetail[l_casia_manual]"]').fill(data['l_casia_wtw_m'])
        frame.locator('input[name="OrderDetail[l_caliper_manual]"]').fill(data['l_caliper_wtw'])

    def calculate_lens(self, page: Page):
        """
        �����LY�

        Args:
            page: Playwrightn����ָ���
        """
        frame = page.frame_locator('#calculatorFrame')
        frame.locator('button:has-text("���")').click()
        page.wait_for_timeout(2000)  # �P�Lh:U��~g�_

    def save_input(self, page: Page):
        """
        e���XY�

        Args:
            page: Playwrightn����ָ���
        """
        frame = page.frame_locator('#calculatorFrame')
        frame.locator('button:has-text("e��X")').click()
        page.wait_for_timeout(1000)

    def save_draft(self, page: Page):
        """
        �M�XY�

        Args:
            page: Playwrightn����ָ���
        """
        page.locator('button:has-text("�M�X")').click()
        page.wait_for_load_state('networkidle')

    def move_csv_to_calculated(self, csv_path: Path):
        """
        �CSVա��calculatedǣ���k��Y�

        Args:
            csv_path: CSVա��nѹ
        """
        # calculatedǣ���LX(WjD4o\
        self.calculated_dir.mkdir(exist_ok=True)

        # ա����
        destination = self.calculated_dir / csv_path.name
        shutil.move(str(csv_path), str(destination))
        print(f" {csv_path.name} � calculated ǣ���k��W~W_")

    def process_csv_file(self, csv_path: Path):
        """
        CSVա���WfIPCL臒\Y�

        Args:
            csv_path: CSVա��nѹ
        """
        print(f"\n{'='*60}")
        print(f"���: {csv_path.name}")
        print(f"{'='*60}")

        # CSV������
        print(" CSVա�뒭�~W_")
        data = self.read_csv_file(csv_path)
        print(f"  �ID: {data['id']}, M: {data['name']}")

        # Playwrightg�馶�w�
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)  # headless=Trueg^h:���
            context = browser.new_context()
            page = context.new_page()

            try:
                # ��
                print(" Web���k��WfD~Y...")
                self.login(page)

                # ��1�e�
                print(" ��1�e�WfD~Y...")
                self.fill_patient_info(page, data)

                # ��������뒋O
                print(" ����臒�DfD~Y...")
                self.open_lens_calculator(page)

                # !<�֒x�
                print(" !<�֒x�WfD~Y...")
                self.select_both_eyes_tab(page)

                # �ID�e�����	
                print(" �ID�e�WfD~Y...")
                frame = page.frame_locator('#calculatorFrame')
                frame.locator('input[name="OrderDetail[patient_id]"]').fill(data['id'])

                # ��e�
                print(" ��e�WfD~Y...")
                self.fill_birthday(page, data['birthday'])

                # ,�����e�
                print(" ,�����e�WfD~Y...")
                self.fill_measurement_data(page, data)

                # �󺿤גx�
                print(" �󺿤גx�WfD~Y...")
                self.select_lens_type(page, data)

                # ATA/WTW����e�
                print(" ATA/WTW����e�WfD~Y...")
                self.fill_ata_wtw_data(page, data)

                # �����L
                print(" �����LWfD~Y...")
                self.calculate_lens(page)

                # e���X
                print(" e���XWfD~Y...")
                self.save_input(page)

                # �M�X
                print(" �M�XWfD~Y...")
                self.save_draft(page)

                print(" �n�MLc8k�XU�~W_")

            except Exception as e:
                print(f" ���LzW~W_: {e}")
                raise

            finally:
                # �馶��X�MkW�_
                page.wait_for_timeout(2000)
                browser.close()

        # CSVա����
        self.move_csv_to_calculated(csv_path)

        print(f"{'='*60}")
        print(f"���: {csv_path.name}")
        print(f"{'='*60}\n")

    def process_all_csv_files(self):
        """
        csvǣ���nYyfnCSVա���Y�
        """
        csv_files = list(self.csv_dir.glob('IPCLdata_*.csv'))

        if not csv_files:
            print("�Y�CSVա��L�dK�~[�gW_")
            return

        print(f"\n{len(csv_files)}�nCSVա���W~Y")

        for csv_file in csv_files:
            self.process_csv_file(csv_file)

        print("\nYyfnա��n�L��W~W_")


def main():
    """���"""
    automation = IPCLOrderAutomation()
    automation.process_all_csv_files()


if __name__ == "__main__":
    main()
