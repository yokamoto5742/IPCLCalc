import csv
from pathlib import Path

import pytest

from service.csv_handler import CSVHandler


class TestCSVHandler:
    """CSVHandlerのテストクラス"""

    @pytest.fixture
    def sample_csv_data(self):
        """サンプルCSVデータを提供するフィクスチャ"""
        return [
            {
                'name': '山田太郎', 'ID': 'P12345', 'sex': '男性',
                'birthday': '05/15/1980', 'surgerydate': '2024/01/15', 'eye': '両眼',
                'R_SPH': '-5.00', 'R_Cyl': '-1.50', 'R_Axis': '90',
                'R_ACD': '3.2', 'R_Pachy(CCT)': '520', 'R_CLR': '12.0',
                'R_K1(Kf)': '43.5', 'R_K1Axis': '180', 'R_K2(Kf)': '44.0',
                'R_SIA': '0.5', 'R_Ins': '11.0',
                'L_SPH': '-4.00', 'L_Cyl': '-1.00', 'L_Axis': '85',
                'L_ACD': '3.1', 'L_Pachy(CCT)': '515', 'L_CLR': '11.8',
                'L_K1(Kf)': '43.2', 'L_K1Axis': '175', 'L_K2(Kf)': '43.8',
                'L_SIA': '0.4', 'L_Ins': '10.8',
                'R_\tATA': '5.0', 'R_CASIA_WTW_M': '11.5', 'R_Caliper_WTW': '11.6',
                'L_\tATA': '5.1', 'L_CASIA_WTW_M': '11.4', 'L_Caliper_WTW': '11.5',
            }
        ]

    @pytest.fixture
    def create_csv_file(self, tmp_path, sample_csv_data):
        """CSVファイルを作成するフィクスチャ"""
        def _create_csv(encoding='cp932', data=None):
            if data is None:
                data = sample_csv_data

            csv_path = tmp_path / "test_data.csv"
            with open(csv_path, 'w', newline='', encoding=encoding) as f:
                if data:
                    writer = csv.DictWriter(f, fieldnames=data[0].keys())
                    writer.writeheader()
                    writer.writerows(data)
            return csv_path
        return _create_csv

    def test_read_csv_file_returns_list(self, create_csv_file):
        """CSVファイルがリストとして読み込まれることを確認"""
        csv_path = create_csv_file()
        result = CSVHandler.read_csv_file(csv_path)

        assert isinstance(result, list)
        assert len(result) > 0

    def test_read_csv_file_contains_patient_data(self, create_csv_file):
        """読み込んだデータに患者情報が含まれることを確認"""
        csv_path = create_csv_file()
        result = CSVHandler.read_csv_file(csv_path)

        patient = result[0]
        assert 'name' in patient
        assert 'id' in patient
        assert 'sex' in patient
        assert 'birthday' in patient
        assert 'surgery_date' in patient
        assert 'eye' in patient

    def test_read_csv_file_contains_measurement_data(self, create_csv_file):
        """読み込んだデータに測定データが含まれることを確認"""
        csv_path = create_csv_file()
        result = CSVHandler.read_csv_file(csv_path)

        patient = result[0]
        # 右眼データ
        assert 'r_sph' in patient
        assert 'r_cyl' in patient
        assert 'r_axis' in patient
        # 左眼データ
        assert 'l_sph' in patient
        assert 'l_cyl' in patient
        assert 'l_axis' in patient

    def test_read_csv_file_contains_ata_wtw_data(self, create_csv_file):
        """読み込んだデータにATA/WTWデータが含まれることを確認"""
        csv_path = create_csv_file()
        result = CSVHandler.read_csv_file(csv_path)

        patient = result[0]
        assert 'r_ata' in patient
        assert 'r_casia_wtw_m' in patient
        assert 'r_caliper_wtw' in patient
        assert 'l_ata' in patient
        assert 'l_casia_wtw_m' in patient
        assert 'l_caliper_wtw' in patient

    def test_read_csv_file_maps_fields_correctly(self, create_csv_file, sample_csv_data):
        """CSVフィールドが正しくマッピングされることを確認"""
        csv_path = create_csv_file()
        result = CSVHandler.read_csv_file(csv_path)

        patient = result[0]
        assert patient['name'] == '山田太郎'
        assert patient['id'] == 'P12345'
        assert patient['sex'] == '男性'
        assert patient['r_sph'] == '-5.00'
        assert patient['l_cyl'] == '-1.00'

    def test_read_csv_file_with_utf8_encoding(self, create_csv_file):
        """UTF-8エンコーディングのCSVファイルを読み込めることを確認"""
        csv_path = create_csv_file(encoding='utf-8')
        result = CSVHandler.read_csv_file(csv_path)

        assert len(result) == 1
        assert result[0]['name'] == '山田太郎'

    def test_read_csv_file_with_cp932_encoding(self, create_csv_file):
        """CP932エンコーディングのCSVファイルを読み込めることを確認"""
        csv_path = create_csv_file(encoding='cp932')
        result = CSVHandler.read_csv_file(csv_path)

        assert len(result) == 1
        assert result[0]['name'] == '山田太郎'

    def test_read_csv_file_with_multiple_rows(self, tmp_path, sample_csv_data):
        """複数行のCSVファイルを読み込めることを確認"""
        # 3行のデータを作成
        multiple_data = [
            sample_csv_data[0].copy(),
            sample_csv_data[0].copy(),
            sample_csv_data[0].copy(),
        ]
        multiple_data[1]['ID'] = 'P12346'
        multiple_data[1]['name'] = '佐藤花子'
        multiple_data[2]['ID'] = 'P12347'
        multiple_data[2]['name'] = '鈴木一郎'

        csv_path = tmp_path / "multiple_rows.csv"
        with open(csv_path, 'w', newline='', encoding='cp932') as f:
            writer = csv.DictWriter(f, fieldnames=multiple_data[0].keys())
            writer.writeheader()
            writer.writerows(multiple_data)

        result = CSVHandler.read_csv_file(csv_path)

        assert len(result) == 3
        assert result[0]['id'] == 'P12345'
        assert result[1]['id'] == 'P12346'
        assert result[2]['id'] == 'P12347'

    def test_read_csv_file_preserves_data_types_as_strings(self, create_csv_file):
        """数値データが文字列として保持されることを確認"""
        csv_path = create_csv_file()
        result = CSVHandler.read_csv_file(csv_path)

        patient = result[0]
        assert isinstance(patient['r_sph'], str)
        assert isinstance(patient['r_acd'], str)
        assert isinstance(patient['r_pachy'], str)

    def test_read_csv_file_handles_empty_fields(self, tmp_path, sample_csv_data):
        """空のフィールドを適切に処理することを確認"""
        data = sample_csv_data[0].copy()
        data['R_SPH'] = ''
        data['L_Cyl'] = ''

        csv_path = tmp_path / "empty_fields.csv"
        with open(csv_path, 'w', newline='', encoding='cp932') as f:
            writer = csv.DictWriter(f, fieldnames=data.keys())
            writer.writeheader()
            writer.writerow(data)

        result = CSVHandler.read_csv_file(csv_path)

        assert result[0]['r_sph'] == ''
        assert result[0]['l_cyl'] == ''

    def test_read_csv_file_with_invalid_binary_data(self, tmp_path):
        """バイナリデータを含むファイルの処理を確認"""
        # バイナリデータでファイルを作成
        csv_path = tmp_path / "binary_data.csv"
        csv_path.write_bytes(b'\x00\x01\x02\x03\x04\x05')  # バイナリデータ

        # バイナリデータの場合、空のリストまたは例外が発生する可能性がある
        try:
            result = CSVHandler.read_csv_file(csv_path)
            # エラーが発生しない場合は空リストが返される
            assert result == []
        except UnicodeDecodeError:
            # UnicodeDecodeErrorが発生することも許容
            pass

    def test_read_csv_file_with_special_characters(self, tmp_path, sample_csv_data):
        """特殊文字を含むデータを読み込めることを確認"""
        data = sample_csv_data[0].copy()
        data['name'] = '患者・名前（テスト）'

        csv_path = tmp_path / "special_chars.csv"
        with open(csv_path, 'w', newline='', encoding='cp932') as f:
            writer = csv.DictWriter(f, fieldnames=data.keys())
            writer.writeheader()
            writer.writerow(data)

        result = CSVHandler.read_csv_file(csv_path)

        assert result[0]['name'] == '患者・名前（テスト）'

    def test_read_csv_file_returns_empty_list_for_empty_csv(self, tmp_path):
        """空のCSVファイルの場合の処理を確認"""
        csv_path = tmp_path / "empty.csv"
        csv_path.write_text('', encoding='cp932')

        # 空のCSVファイルは空リストを返す（ヘッダーがないため）
        result = CSVHandler.read_csv_file(csv_path)
        assert result == []

    def test_read_csv_file_with_only_header(self, tmp_path, sample_csv_data):
        """ヘッダーのみのCSVファイルを読み込めることを確認"""
        csv_path = tmp_path / "header_only.csv"
        with open(csv_path, 'w', newline='', encoding='cp932') as f:
            writer = csv.DictWriter(f, fieldnames=sample_csv_data[0].keys())
            writer.writeheader()

        result = CSVHandler.read_csv_file(csv_path)

        assert result == []

    @pytest.mark.parametrize("eye_value", ['両眼', '右眼', '左眼'])
    def test_read_csv_file_with_different_eye_values(self, tmp_path, sample_csv_data, eye_value):
        """異なる眼の値を読み込めることを確認"""
        data = sample_csv_data[0].copy()
        data['eye'] = eye_value

        csv_path = tmp_path / f"eye_{eye_value}.csv"
        with open(csv_path, 'w', newline='', encoding='cp932') as f:
            writer = csv.DictWriter(f, fieldnames=data.keys())
            writer.writeheader()
            writer.writerow(data)

        result = CSVHandler.read_csv_file(csv_path)

        assert result[0]['eye'] == eye_value
