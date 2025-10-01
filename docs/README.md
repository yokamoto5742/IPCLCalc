# IPCL Lens Order Automation System

IPCL注文システムへの自動入力を行うPythonプログラムです。

## 機能

- CSVファイルから患者データを読み込み
- IPCL注文システムへ自動ログイン
- 患者情報・測定データの自動入力
- レンズタイプの自動選択（Cyl値に基づく）
- レンズ計算の実行
- 下書き保存
- 処理済みCSVファイルの自動移動

## 必要な環境

- Python 3.8以上
- Playwright

## セットアップ

1. 依存パッケージのインストール:
```bash
pip install -r requirements.txt
```

2. Playwrightブラウザのインストール:
```bash
playwright install chromium
```

## 使い方

### CSVファイルの準備

`csv/` ディレクトリに以下の形式のCSVファイルを配置します：

ファイル名: `IPCLdata_ID{患者ID}.csv`

必須カラム:
- name, ID, Birthday, surgerydate
- R_SPH, R_Cyl, R_Axis, R_ACD, R_Pachy(CCT), R_CLR, R_K1(Kf), R_K1Axis, R_K2(Kf), R_SIA, R_Ins
- L_SPH, L_Cyl, L_Axis, L_ACD, L_Pachy(CCT), L_CLR, L_K1(Kf), L_K1Axis, L_K2(Kf), L_SIA, L_Ins
- R_ATA, R_CASIA_WTW_M, R_Caliper_WTW
- L_ATA, L_CASIA_WTW_M, L_Caliper_WTW

### プログラムの実行

```bash
python main.py
```

プログラムは以下の処理を自動的に実行します：

1. `csv/` ディレクトリ内のすべての `IPCLdata_*.csv` ファイルを検索
2. 各ファイルについて：
   - データ読み込み
   - IPCL注文システムへログイン
   - 患者情報入力
   - レンズ計算・注文モーダルを開く
   - 両眼タブを選択
   - 測定データ入力
   - レンズタイプ選択（Cyl=0なら Mono、Cyl<0なら Toric）
   - ATA/WTWデータ入力
   - レンズ計算実行
   - 入力保存
   - 下書き保存
3. 処理済みCSVファイルを `csv/calculated/` に移動

### ログイン情報の変更

`main.py` の `IPCLOrderAutomation` クラスの `__init__` メソッド内で変更できます：

```python
self.email = "your-email@example.com"
self.password = "your-password"
```

## ディレクトリ構造

```
IPCLCalc/
├── main.py              # メインプログラム
├── csv/                 # CSVファイル格納ディレクトリ
│   ├── IPCLdata_*.csv  # 処理対象のCSVファイル
│   └── calculated/     # 処理済みCSVファイル
└── requirements.txt    # 依存パッケージリスト
```

## レンズタイプ選択ロジック

- Cyl値が **0** の場合: **IPCL V2.0 Mono** を選択
- Cyl値が **0以外** の場合: **IPCL V2.0 Toric** を選択

## 注意事項

- プログラム実行中はブラウザが自動操作されます
- `headless=False` に設定されているため、ブラウザウィンドウが表示されます
- 非表示モードにする場合は `main.py` の `browser = p.chromium.launch(headless=False)` を `headless=True` に変更してください
- ネットワーク速度によっては待機時間の調整が必要な場合があります

## トラブルシューティング

### Playwrightが見つからない場合

```bash
pip install playwright
playwright install chromium
```

### ブラウザが起動しない場合

Playwrightのブラウザドライバーを再インストール:
```bash
playwright install --force chromium
```

### タイムアウトエラーが発生する場合

`page.wait_for_timeout()` の値を大きくしてください。

## ライセンス

© 2025 All Rights Reserved.
