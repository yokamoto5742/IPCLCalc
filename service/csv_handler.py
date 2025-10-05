import csv
from pathlib import Path


class CSVHandler:
    @staticmethod
    def read_csv_file(csv_path: Path) -> list[dict]:
        """CSVファイルからすべての行のデータを読み込む"""
        # cp932, utf-8の順で試行
        all_data = []
        for encoding in ['cp932', 'utf-8']:
            try:
                with open(csv_path, encoding=encoding) as f:
                    reader = csv.DictReader(f)
                    for data in reader:
                        patient_data = {
                            'name': data['name'],
                            'id': data['ID'],
                            'sex': data['sex'],
                            'birthday': data['birthday'],
                            'surgery_date': data['surgerydate'],
                            'eye': data['eye'],
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
                        all_data.append(patient_data)
                break
            except UnicodeDecodeError:
                if encoding == 'utf-8':
                    raise
                continue

        return all_data
