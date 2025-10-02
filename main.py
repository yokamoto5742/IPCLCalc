import shutil
from pathlib import Path

from playwright.sync_api import sync_playwright, Page

import csv


class IPCLOrderAutomation:
    """IPCL注文システムの自動化クラス"""

    def __init__(self):
        self.base_url = "https://www.ipcl-jp.com/awsystem/order/create"
        self.email = "m-hosokawa@shinseikai.or.jp"
        self.password = "Shinseikai123!"
        self.csv_dir = Path(__file__).parent / "csv"
        self.calculated_dir = self.csv_dir / "calculated"

    def read_csv_file(self, csv_path: Path) -> dict:
        """
        CSVファイルからデータを読み込む

        Args:
            csv_path: CSVファイルのパス

        Returns:
            患者データの辞書
        """
        with open(csv_path, encoding='utf-8') as f:
            reader = csv.DictReader(f)
            data = next(reader)

        # データを整形
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
        """
        Webサイトにログインする

        Args:
            page: Playwrightのページオブジェクト
        """
        page.goto(self.base_url)
        page.wait_for_load_state('networkidle')

        # ログインフォームに入力（プレースホルダーとラベルで要素を特定）
        page.get_by_placeholder("ログインID").fill(self.email)
        page.get_by_label("パスワード").fill(self.password)
        page.click('button:has-text("サインイン")')
        page.wait_for_load_state('networkidle')

    def fill_patient_info(self, page: Page, data: dict):
        """
        患者情報を入力する

        Args:
            page: Playwrightのページオブジェクト
            data: 患者データ
        """
        # ページが完全にロードされるまで待機
        page.wait_for_load_state('domcontentloaded')
        page.wait_for_timeout(2000)

        # 患者IDを入力（代替セレクタを試す）
        page.get_by_label("患者ID").fill(data['id'])

        # 性別を選択（男性）
        try:
            page.get_by_label("性別*").click()
            page.click('li:has-text("男性")')
        except:
            try:
                page.get_by_label("性別").click()
                page.click('li:has-text("男性")')
            except:
                pass

        # 手術日を入力
        try:
            page.get_by_label("手術日").fill(data['surgery_date'])
        except:
            try:
                page.locator('input[name*="surgery"]').first.fill(data['surgery_date'])
            except:
                pass

    def open_lens_calculator(self, page: Page):
        """
        レンズ計算・注文モーダルを開く

        Args:
            page: Playwrightのページオブジェクト
        """
        page.click('button:has-text("レンズ計算・注文")')
        page.wait_for_timeout(1000)

    def select_both_eyes_tab(self, page: Page):
        """
        両眼タブを選択し、バックアップレンズ込みをチェック

        Args:
            page: Playwrightのページオブジェクト
        """
        frame = page.frame_locator('#calculatorFrame')
        frame.locator('a:has-text("両眼")').click()

        # バックアップレンズ込みをチェック（type="checkbox"を明示的に指定）
        backup_checkbox = frame.locator('input[type="checkbox"][name="OrderDetail[include_backup]"]')
        if not backup_checkbox.is_checked():
            backup_checkbox.check()

    def fill_measurement_data(self, page: Page, data: dict):
        """
        右眼・左眼の測定データを入力する

        Args:
            page: Playwrightのページオブジェクト
            data: 患者データ
        """
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
        """
        Cyl値に基づいてレンズタイプを選択する

        Args:
            page: Playwrightのページオブジェクト
            data: 患者データ
        """
        frame = page.frame_locator('#calculatorFrame')

        # 右眼のレンズタイプを選択
        r_cyl = float(data['r_cyl'])
        if r_cyl == 0:
            frame.locator('input[name="OrderDetail[ipcl_r]"][value="IPCL V2.0 Mono"]').check()
        else:
            frame.locator('input[name="OrderDetail[ipcl_r]"][value="IPCL V2.0 Toric"]').check()

        # 左眼のレンズタイプを選択
        l_cyl = float(data['l_cyl'])
        if l_cyl == 0:
            frame.locator('input[name="OrderDetail[ipcl_l]"][value="IPCL V2.0 Mono"]').check()
        else:
            frame.locator('input[name="OrderDetail[ipcl_l]"][value="IPCL V2.0 Toric"]').check()

    def fill_birthday(self, page: Page, birthday: str):
        """
        誕生日をカレンダーピッカーで入力する

        Args:
            page: Playwrightのページオブジェクト
            birthday: 誕生日（MM/DD/YYYY形式）
        """
        frame = page.frame_locator('#calculatorFrame')

        try:
            frame.get_by_label("誕生日").fill(birthday)
        except:
            # カレンダーピッカーが見つからない場合は直接入力を試す
            try:
                frame.locator('input[name*="birthday"]').first.fill(birthday)
            except:
                try:
                    # 日付ピッカーを開く
                    frame.locator('span.input-group-addon:has(i.glyphicon-calendar)').first.click(timeout=5000)
                    page.wait_for_timeout(500)

                    # 誕生日を解析（MM/DD/YYYY → DD, MM, YYYY）
                    month, day, year = birthday.split('/')
                    target_year = int(year)

                    # 年を選択（2007から目標年まで遡る）
                    current_year = 2007
                    while current_year > target_year:
                        frame.locator('td.prev').first.click()
                        page.wait_for_timeout(200)
                        current_year -= 1

                    # 月を選択
                    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                                   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
                    month_name = month_names[int(month) - 1]
                    frame.locator(f'span:has-text("{month_name}")').click()
                    page.wait_for_timeout(500)

                    # 日を選択（3番目以降のセルから該当する日を探す）
                    day_cells = frame.locator(f'td:has-text("{int(day)}")').all()
                    for cell in day_cells:
                        if cell.inner_text() == str(int(day)):
                            cell.click()
                            break

                    page.wait_for_timeout(500)
                except:
                    print("[WARNING] 誕生日入力をスキップしました")

    def fill_ata_wtw_data(self, page: Page, data: dict):
        """
        ATA/WTWデータを入力する

        Args:
            page: Playwrightのページオブジェクト
            data: 患者データ
        """
        frame = page.frame_locator('#calculatorFrame')

        # 右眼のATA/WTWデータ
        frame.locator('input[name="OrderDetail[r_ata]"]').fill(data['r_ata'])
        frame.locator('input[name="OrderDetail[r_casia_manual]"]').fill(data['r_casia_wtw_m'])
        frame.locator('input[name="OrderDetail[r_caliper_manual]"]').fill(data['r_caliper_wtw'])

        # 左眼のATA/WTWデータ
        frame.locator('input[name="OrderDetail[l_ata]"]').fill(data['l_ata'])
        frame.locator('input[name="OrderDetail[l_casia_manual]"]').fill(data['l_casia_wtw_m'])
        frame.locator('input[name="OrderDetail[l_caliper_manual]"]').fill(data['l_caliper_wtw'])

    def calculate_lens(self, page: Page):
        """
        レンズ計算を実行する

        Args:
            page: Playwrightのページオブジェクト
        """
        frame = page.frame_locator('#calculatorFrame')
        frame.locator('button:has-text("レンズ計算")').click()
        page.wait_for_timeout(2000)  # 計算結果が表示されるまで待機

    def save_input(self, page: Page):
        """
        入力を保存する

        Args:
            page: Playwrightのページオブジェクト
        """
        frame = page.frame_locator('#calculatorFrame')
        frame.locator('button:has-text("入力保存")').click()
        page.wait_for_timeout(1000)

    def save_draft(self, page: Page) -> bool:
        """
        下書き保存する

        Args:
            page: Playwrightのページオブジェクト

        Returns:
            bool: 保存に成功した場合True、スキップした場合False
        """
        try:
            # ボタンが有効になるまで待つ（最大10秒）
            save_button = page.locator('button:has-text("下書き保存")')
            save_button.wait_for(state='visible', timeout=10000)
            page.wait_for_timeout(2000)  # 少し待機してからクリック

            # ボタンが有効であることを確認してクリック
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
        """
        処理済みCSVファイルをcalculatedディレクトリに移動する

        Args:
            csv_path: CSVファイルのパス
        """
        # calculatedディレクトリが存在しない場合は作成
        self.calculated_dir.mkdir(exist_ok=True)

        # ファイルを移動
        destination = self.calculated_dir / csv_path.name
        shutil.move(str(csv_path), str(destination))
        print(f"[OK] {csv_path.name} を calculated ディレクトリに移動しました")

    def process_csv_file(self, csv_path: Path):
        """
        CSVファイルを処理してIPCL注文を作成する

        Args:
            csv_path: CSVファイルのパス
        """
        print(f"\n{'='*60}")
        print(f"処理開始: {csv_path.name}")
        print(f"{'='*60}")

        # CSVデータを読み込み
        print("[OK] CSVファイルを読み込みました")
        data = self.read_csv_file(csv_path)
        print(f"  患者ID: {data['id']}, 名前: {data['name']}")

        # Playwrightでブラウザを起動
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)  # headless=Trueで非表示モード
            context = browser.new_context()
            page = context.new_page()

            save_success = False
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

                # レンズ計算を実行
                print("[OK] レンズ計算を実行しています...")
                self.calculate_lens(page)

                # 入力を保存
                print("[OK] 入力を保存しています...")
                self.save_input(page)

                # 下書き保存
                print("[OK] 下書き保存しています...")
                save_success = self.save_draft(page)

                if save_success:
                    print("[OK] 注文の下書きが正常に保存されました")
                else:
                    print("[WARNING] ブラウザを開いたままにします。手動で確認してください。")

            except Exception as e:
                print(f"[ERROR] エラーが発生しました: {e}")
                raise

            finally:
                if save_success:
                    pass
                    # ブラウザを閉じる前に少し待機
                    # page.wait_for_timeout(2000)
                    # # browser.close()

        # CSVファイルを移動（保存成功時のみ）
        if save_success:
            self.move_csv_to_calculated(csv_path)

        print(f"{'='*60}")
        print(f"処理完了: {csv_path.name}")
        print(f"{'='*60}\n")

    def process_all_csv_files(self):
        """
        csvディレクトリ内のすべてのCSVファイルを処理する
        """
        csv_files = list(self.csv_dir.glob('IPCLdata_*.csv'))

        if not csv_files:
            print("処理するCSVファイルが見つかりませんでした")
            return

        print(f"\n{len(csv_files)}件のCSVファイルを処理します")

        for csv_file in csv_files:
            self.process_csv_file(csv_file)

        print("\nすべてのファイルの処理が完了しました")


def main():
    """メイン処理"""
    automation = IPCLOrderAutomation()
    automation.process_all_csv_files()


if __name__ == "__main__":
    main()
