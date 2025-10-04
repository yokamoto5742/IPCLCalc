import csv
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

from playwright.sync_api import Page, sync_playwright

from service.draft_launch import launch_draft_page
from utils.config_manager import load_config, load_environment_variables


class IPCLOrderAutomation:
    def __init__(self):

        if getattr(sys, 'frozen', False):
            base_path = Path(sys._MEIPASS)
            playwright_browsers = base_path / 'playwright' / 'driver' / 'package' / '.local-browsers'
            if playwright_browsers.exists():
                os.environ['PLAYWRIGHT_BROWSERS_PATH'] = str(playwright_browsers)
                print(f"[OK] Playwrightブラウザパス設定: {playwright_browsers}")
            else:
                print(f"[WARNING] Playwrightブラウザパスが見つかりません: {playwright_browsers}")

        load_environment_variables()

        config = load_config()

        self.base_url = config.get('URL', 'base_url')
        self.email = os.getenv('EMAIL')
        self.password = os.getenv('PASSWORD')
        self.csv_dir = Path(config.get('Paths', 'csv_dir'))
        self.calculated_dir = Path(config.get('Paths', 'calculated_dir'))
        self.error_dir = Path(config.get('Paths', 'error_dir'))
        self.log_dir = Path(config.get('Paths', 'log_dir'))
        self.headless = config.getboolean('Settings', 'headless')

        # PDFダウンロード先ディレクトリを設定
        self.pdf_dir = self.csv_dir / 'pdf'
        self.pdf_dir.mkdir(exist_ok=True)
        print(f"[OK] PDFダウンロード先: {self.pdf_dir}")

    def read_csv_file(self, csv_path: Path) -> dict:
        # cp932, utf-8の順で試行
        for encoding in ['cp932', 'utf-8']:
            try:
                with open(csv_path, encoding=encoding) as f:
                    reader = csv.DictReader(f)
                    data = next(reader)
                break
            except UnicodeDecodeError:
                if encoding == 'utf-8':
                    raise
                continue

        patient_data = {
            'name': data['name'],
            'id': data['ID'],
            'birthday': data['birthday'],
            'sex': data['sex'],
            'surgery_date': data['surgerydate'],
            # 右眼データ
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
            # 左眼データ
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
            # ATA/WTW データ
            'r_ata': data['R_\tATA'],
            'r_casia_wtw_m': data['R_CASIA_WTW_M'],
            'r_caliper_wtw': data['R_Caliper_WTW'],
            'l_ata': data['L_\tATA'],
            'l_casia_wtw_m': data['L_CASIA_WTW_M'],
            'l_caliper_wtw': data['L_Caliper_WTW'],
        }

        return patient_data

    def login(self, page: Page):
        page.goto(self.base_url)
        page.wait_for_load_state('networkidle')

        page.get_by_placeholder("ログインID").fill(self.email)
        page.get_by_label("パスワード").fill(self.password)
        page.click('button:has-text("サインイン")')
        page.wait_for_load_state('networkidle')

    def fill_patient_info(self, page: Page, data: dict):
        page.wait_for_load_state('domcontentloaded')
        page.wait_for_timeout(2000)

        page.get_by_label("患者ID").fill(data['id'])

        try:
            page.locator('#select2-order-sex-container').click()
            page.wait_for_timeout(500)
            sex_index = 0 if data['sex'] == '男性' else 1
            page.locator('li.select2-results__option').nth(sex_index).click()
        except:
            try:
                page.get_by_label("性別*").click()
                page.click(f'li:has-text("{data["sex"]}")')
            except Exception:
                print(f"[WARNING] 性別選択をスキップしました")

        try:
            page.get_by_label("手術日").fill(data['surgery_date'])
            page.get_by_label("手術日").press('Enter')
        except:
            try:
                page.locator('input[name*="surgery"]').first.fill(data['surgery_date'])
                page.locator('input[name*="surgery"]').first.press('Enter')
            except:
                pass

    def open_lens_calculator(self, page: Page):
        page.click('button:has-text("レンズ計算・注文")')
        page.wait_for_timeout(1000)

    def select_both_eyes_tab(self, page: Page):
        frame = page.frame_locator('#calculatorFrame')
        frame.locator('a:has-text("両眼")').click()

        backup_checkbox = frame.locator('input[type="checkbox"][name="OrderDetail[include_backup]"]')
        if not backup_checkbox.is_checked():
            backup_checkbox.check()

    def fill_measurement_data(self, page: Page, data: dict):
        frame = page.frame_locator('#calculatorFrame')

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

    def select_lens_type(self, page: Page, data: dict):
        frame = page.frame_locator('#calculatorFrame')

        r_cyl = float(data['r_cyl'])
        if r_cyl == 0:
            frame.locator('input[name="OrderDetail[ipcl_r]"][value="IPCL V2.0 Mono"]').check()
        else:
            frame.locator('input[name="OrderDetail[ipcl_r]"][value="IPCL V2.0 Toric"]').check()

        l_cyl = float(data['l_cyl'])
        if l_cyl == 0:
            frame.locator('input[name="OrderDetail[ipcl_l]"][value="IPCL V2.0 Mono"]').check()
        else:
            frame.locator('input[name="OrderDetail[ipcl_l]"][value="IPCL V2.0 Toric"]').check()

    def fill_birthday(self, page: Page, birthday: str):
        frame = page.frame_locator('#calculatorFrame')

        try:
            month, day, year = birthday.split('/')
            formatted_birthday = f"{day}/{month}/{year}"

            # 誕生日入力フィールドに直接入力（プレースホルダーで識別）
            birthday_input = frame.locator('input[placeholder="dd/mm/yyyy"]').first
            birthday_input.fill(formatted_birthday)
            birthday_input.press('Enter')  # Enterキーを押さないと登録されない
            page.wait_for_timeout(500)

        except Exception as e:
            print(f"[WARNING] 誕生日入力をスキップしました: {e}")

    def fill_ata_wtw_data(self, page: Page, data: dict):
        frame = page.frame_locator('#calculatorFrame')

        # 右眼のATA/WTWデータ
        frame.locator('input[name="OrderDetail[r_ata]"]').fill(data['r_ata'])
        frame.locator('input[name="OrderDetail[r_casia_manual]"]').fill(data['r_casia_wtw_m'])
        frame.locator('input[name="OrderDetail[r_caliper_manual]"]').fill(data['r_caliper_wtw'])

        # 左眼のATA/WTWデータ
        frame.locator('input[name="OrderDetail[l_ata]"]').fill(data['l_ata'])
        frame.locator('input[name="OrderDetail[l_casia_manual]"]').fill(data['l_casia_wtw_m'])
        frame.locator('input[name="OrderDetail[l_caliper_manual]"]').fill(data['l_caliper_wtw'])

    def click_calculate_button(self, page: Page):
        frame = page.frame_locator('#calculatorFrame')
        frame.locator('button#btn-calculate').click()
        page.wait_for_timeout(1000)

    def click_save_pdf_button(self, page: Page, patient_id: str, patient_name: str) -> str:
        """PDFを保存し、保存先パスを返す"""
        frame = page.frame_locator('#calculatorFrame')

        try:
            # ダウンロードを待機
            with page.expect_download() as download_info:
                frame.locator('a:has(i.far.fa-file-pdf)').click()

            download = download_info.value

            # デバッグ情報を表示
            print(f"[DEBUG] 一時ファイル: {download.path()}")
            print(f"[DEBUG] 推奨ファイル名: {download.suggested_filename}")

            # ファイル名を生成（患者IDと患者名を含む）
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            pdf_filename = f"IPCL_{patient_id}_{patient_name}_{timestamp}.pdf"
            pdf_path = self.pdf_dir / pdf_filename

            # ダウンロードしたファイルを指定先に保存
            download.save_as(pdf_path)

            print(f"[OK] PDFを保存しました: {pdf_path}")
            return str(pdf_path)

        except Exception as e:
            print(f"[ERROR] PDF保存中にエラーが発生しました: {e}")
            raise

    def save_input(self, page: Page):
        frame = page.frame_locator('#calculatorFrame')
        frame.locator('button#btn-save-draft-modal').click()
        page.wait_for_timeout(1000)

    def save_draft(self, page: Page) -> bool:
        try:
            save_button = page.locator('button:has-text("下書き保存")')
            save_button.wait_for(state='visible', timeout=5000)
            page.wait_for_timeout(2000)

            if not save_button.is_disabled():
                save_button.click()
                page.wait_for_load_state('networkidle')
                return True
            else:
                print("[WARNING] 下書き保存ボタンが無効のため、処理をスキップしました")
                return False
        except Exception as e:
            print(f"[WARNING] 下書き保存をスキップしました: {e}")
            return False

    def move_csv_to_calculated(self, csv_path: Path):
        self.calculated_dir.mkdir(exist_ok=True)

        destination = self.calculated_dir / csv_path.name
        shutil.move(str(csv_path), str(destination))
        print(f"[OK] {csv_path.name} を calculated ディレクトリに移動しました")

    def process_csv_file(self, csv_path: Path):
        print(f"\n{'=' * 60}")
        print(f"処理開始: {csv_path.name}")
        print(f"{'=' * 60}")

        print("[OK] CSVファイルを読み込みました")
        data = self.read_csv_file(csv_path)
        print(f"  患者ID: {data['id']}, 名前: {data['name']}")

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)

            # ダウンロード先を指定してコンテキストを作成
            context = browser.new_context(
                accept_downloads=True
            )
            page = context.new_page()

            save_success = False
            pdf_path = None

            try:
                # ログイン
                print("[OK] Webサイトにログインしています...")
                self.login(page)

                # 患者情報を入力
                print("[OK] 患者情報を入力しています...")
                self.fill_patient_info(page, data)

                # レンズ計算・注文モーダルを開く
                print("[OK] レンズ計算・注文を開いています...")
                self.open_lens_calculator(page)

                # 両眼タブを選択
                print("[OK] 両眼タブを選択しています...")
                self.select_both_eyes_tab(page)

                # 誕生日を入力
                print("[OK] 誕生日を入力しています...")
                self.fill_birthday(page, data['birthday'])

                # 測定データを入力
                print("[OK] 測定データを入力しています...")
                self.fill_measurement_data(page, data)

                # レンズタイプを選択
                print("[OK] レンズタイプを選択しています...")
                self.select_lens_type(page, data)

                # ATA/WTWデータを入力
                print("[OK] ATA/WTWデータを入力しています...")
                self.fill_ata_wtw_data(page, data)

                # レンズ計算
                print("[OK] レンズ計算を実行しています...")
                self.click_calculate_button(page)

                # PDF保存
                print("[OK] PDFを保存しています...")
                pdf_path = self.click_save_pdf_button(page, data['id'], data['name'])

                # 入力を保存
                print("[OK] 入力を保存しています...")
                self.save_input(page)

                # 下書き保存
                print("[OK] 下書き保存しています...")
                save_success = self.save_draft(page)

                if save_success:
                    print("[OK] 注文の下書きが正常に保存されました")
                    if pdf_path:
                        print(f"[OK] PDF保存先: {pdf_path}")
                else:
                    print("[WARNING] ブラウザを開いたままにします。手動で確認してください。")

            except Exception as e:
                print(f"[ERROR] エラーが発生しました: {e}")
                raise

            finally:
                if save_success:
                    page.wait_for_timeout(2000)
                    browser.close()

        if save_success:
            self.move_csv_to_calculated(csv_path)

        print(f"{'=' * 60}")
        print(f"処理完了: {csv_path.name}")
        print(f"{'=' * 60}\n")

    def process_all_csv_files(self):
        csv_files = list(self.csv_dir.glob('IPCLdata_*.csv'))

        if not csv_files:
            print("処理するCSVファイルが見つかりませんでした")
            return

        print(f"\n{len(csv_files)}件のCSVファイルを処理します")

        for csv_file in csv_files:
            self.process_csv_file(csv_file)

        print("\nすべてのファイルの処理が完了しました")
        print(f"PDFの保存先: {self.pdf_dir}")


def main():
    automation = IPCLOrderAutomation()
    automation.process_all_csv_files()
    launch_draft_page()


if __name__ == "__main__":
    main()
