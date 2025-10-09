# IPCLCalc

**現在のバージョン**: 1.0.1
**最終更新日**: 2025年10月7日

IPCLCalcは、IPCL注文システムへの患者データ入力を自動化するPythonアプリケーションです。CSVファイルから患者データを読み込み、Webブラウザを自動操作してIPCL注文システムに入力、レンズ計算を実行し、PDF形式で計算結果を保存します。

## 目次

- [主要な機能](#主要な機能)
- [対象ユーザー](#対象ユーザー)
- [前提条件と要件](#前提条件と要件)
- [インストール手順](#インストール手順)
- [使用方法](#使用方法)
- [プロジェクト構造](#プロジェクト構造)
- [機能説明](#機能説明)
- [設定ファイル](#設定ファイル)
- [開発者向け情報](#開発者向け情報)
- [トラブルシューティング](#トラブルシューティング)
- [ライセンス](#ライセンス)

## 主要な機能

### 自動化機能
- **CSVファイルからのデータ読み込み**: 患者ID、測定データ、手術日などを一括読み込み
- **Webブラウザ自動操作**: Playwrightを使用したIPCL注文システムへの自動ログインと入力
- **患者情報の自動入力**: 基本情報（ID、性別、手術日）の自動入力
- **測定データの自動入力**: 両眼の屈折測定値、角膜データ、前房深度などの自動入力
- **レンズタイプの自動選択**: Cyl値に基づいてMono/Toricレンズを自動判定・選択
- **レンズ計算の自動実行**: 入力データに基づくレンズ計算の実行
- **PDF自動保存**: 計算結果をPDF形式で自動保存（タイムスタンプ付き）
- **下書き自動保存**: 注文データの下書き保存

### ユーザーインターフェース
- **進捗表示ウィンドウ**: リアルタイムで処理状況を表示するTkinterベースのGUI
- **バッチ処理対応**: 複数のCSVファイルを連続して自動処理

### その他の機能
- **自動ブラウザ起動**: 処理完了後、下書きページと保存先フォルダを自動で開く
- **エンコーディング自動判定**: CP932とUTF-8のCSVファイルに対応
- **エラーハンドリング**: 処理エラー時のログ出力と安全な終了処理

## 対象ユーザー
- **眼科医療従事者**: IPCL（眼内コンタクトレンズ）の注文業務を行う眼科医療従事者

## プロダクト開発の背景と解決する問題

### 課題
IPCL注文システムへの患者データ入力は、多数の測定値を手動で入力する必要があり、以下の問題がありました：

- 測定データの入力に時間がかかる（1件あたり5～10分）
- 手動入力によるミスのリスク
- 複数患者のデータ入力時の作業負担

### 解決方法
IPCLCalcは、CSVファイルから患者データを読み込み、Webブラウザを自動操作することで：

- **作業時間を大幅に短縮**（1件あたり1～2分程度）
- **入力ミスを削減**（自動入力による正確性向上）
- **複数患者の一括処理**（バッチ処理による効率化）

## 前提条件と要件

### 必要な開発環境
- **OS**: Windows 11（Windows 10でも動作可能）
- **Python**: 3.11以降を推奨
- **Webブラウザ**: Google Chrome（最新版推奨）

### ハードウェア要件
- **メモリ**: 4GB以上推奨（ブラウザ自動操作のため）
- **ストレージ**: 500MB以上の空き容量
- **ネットワーク**: インターネット接続必須（IPCL注文システムへのアクセスに必要）

## インストール手順

### 1. リポジトリのクローン

```bash
git clone https://github.com/yourusername/IPCLCalc.git
cd IPCLCalc
```

### 2. Python仮想環境の作成（推奨）

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. 依存パッケージのインストール

```bash
pip install -r requirements.txt
```

### 4. Playwrightブラウザのインストール

```bash
playwright install chromium
```

### 5. 環境変数の設定

プロジェクトルートに`.env`ファイルを作成し、ログイン情報を設定します：

```env
# IPCL注文システムのログイン情報
EMAIL=your-email@example.com
PASSWORD=your-password
```

**重要**: `.env`ファイルには機密情報が含まれるため、Gitにコミットしないでください。

### 6. 設定ファイルの編集

`utils/config.ini`を環境に合わせて編集します：

```ini
[Paths]
csv_dir = C:\Shinseikai\IPCLCalc\csv
calculated_dir = C:\Shinseikai\IPCLCalc\csv\calculated
error_dir = C:\Shinseikai\IPCLCalc\csv\error
log_dir = C:\Shinseikai\IPCLCalc\logs
pdf_dir = C:\Shinseikai\IPCLCalc\csv\pdf

[Chrome]
chrome_path = C:\Program Files\Google\Chrome\Application\chrome.exe

[Settings]
headless = True
```

**パスの設定**: 実際の環境に合わせてディレクトリパスを変更してください。

### 7. ディレクトリ構造の作成

必要なディレクトリを手動で作成するか、初回実行時に自動作成されます：

```
C:\Shinseikai\IPCLCalc\
├── csv\
│   ├── calculated\
│   ├── error\
│   └── pdf\
└── logs\
```

## 使用方法

### CSVファイルの準備

#### ファイル名の規則
```
IPCLdata_ID{患者ID}_yymmddHHmm.csv
```

例：`IPCLdata_ID12345_2510031122.csv`

#### CSVファイルの形式

必須カラム（列名は正確に一致する必要があります）：

**基本情報**
- `name`: 患者名
- `ID`: 患者ID
- `sex`: 性別（"男性" または "女性"）
- `birthday`: 誕生日（MM/DD/YYYY形式）
- `surgerydate`: 手術日（MM/DD/YYYY形式）
- `eye`: 対象眼（"右眼", "左眼", または "両眼"）

**右眼の測定データ**
- `R_SPH`: 球面度数
- `R_Cyl`: 乱視度数
- `R_Axis`: 乱視軸
- `R_ACD`: 前房深度
- `R_Pachy(CCT)`: 角膜中心厚
- `R_CLR`: 角膜水晶体距離
- `R_K1(Kf)`: 最大角膜屈折力
- `R_K1Axis`: K1の軸
- `R_K2(Kf)`: 最小角膜屈折力
- `R_SIA`: 手術惹起乱視
- `R_Ins`: 切開位置

**左眼の測定データ**
- `L_SPH`, `L_Cyl`, `L_Axis`, `L_ACD`, `L_Pachy(CCT)`, `L_CLR`
- `L_K1(Kf)`, `L_K1Axis`, `L_K2(Kf)`, `L_SIA`, `L_Ins`

**ATA/WTW測定データ**
- `R_ATA`: 右眼ATA値
- `R_CASIA_WTW_M`: 右眼CASIA WTW（手動測定）
- `R_Caliper_WTW`: 右眼キャリパーWTW
- `L_ATA`: 左眼ATA値
- `L_CASIA_WTW_M`: 左眼CASIA WTW（手動測定）
- `L_Caliper_WTW`: 左眼キャリパーWTW

#### CSVファイルの配置

準備したCSVファイルを`csv/`ディレクトリに配置します：

```
C:\Shinseikai\IPCLCalc\csv\IPCLdata_ID12345.csv
C:\Shinseikai\IPCLCalc\csv\IPCLdata_ID12346.csv
```

### プログラムの実行

#### 基本的な実行方法

```bash
python main.py
```

#### 実行フロー

1. **CSV読み込み**: `csv/`ディレクトリ内の全`IPCLdata_*.csv`ファイルを検索
2. **進捗ウィンドウ表示**: 処理状況をリアルタイム表示
3. **各ファイルの処理**:
   - ブラウザ起動（Chromium）
   - IPCL注文システムへログイン
   - 患者情報入力
   - レンズ計算・注文モーダルを開く
   - 対象眼のタブを選択
   - 測定データ入力
   - レンズタイプ自動選択
   - ATA/WTWデータ入力
   - レンズ計算実行
   - PDF保存
   - 入力保存
   - 下書き保存
4. **ファイル移動**: 処理済みCSVを`csv/calculated/`に移動
5. **自動起動**:
   - 下書きページをChromeで開く
   - PDFフォルダをエクスプローラーで開く

### 処理結果の確認

#### PDF保存先

```
C:\Shinseikai\IPCLCalc\csv\pdf\
```

PDFファイル名の形式：
```
IPCLdata_ID{患者ID}_{タイムスタンプ}.pdf
```

例：`IPCLdata_ID12345_20251007_143025.pdf`

#### 処理済みCSVファイル

```
C:\Shinseikai\IPCLCalc\csv\calculated\
```

処理が正常に完了したCSVファイルは自動的にこのフォルダに移動されます。

### レンズタイプ選択ロジック

プログラムは乱視度数（Cyl値）に基づいて自動的にレンズタイプを選択します：

- **Cyl = 0**: `IPCL V2.0 Mono`（単焦点レンズ）
- **Cyl ≠ 0**: `IPCL V2.0 Toric`（乱視矯正レンズ）

両眼処理の場合、右眼と左眼で異なるレンズタイプが選択される可能性があります。

## プロジェクト構造

```
IPCLCalc/
├── main.py                      # メインエントリーポイント
├── requirements.txt             # 依存パッケージリスト
├── .env                         # 環境変数（ログイン情報）※Gitにコミットしない
│
├── app/
│   └── __init__.py             # バージョン情報
│
├── service/                     # ビジネスロジック層
│   ├── __init__.py
│   ├── auth_service.py         # 認証サービス（ログイン処理）
│   ├── automation_service.py   # 自動化メインサービス
│   ├── browser_manager.py      # ブラウザ処理管理
│   ├── csv_handler.py          # CSVファイル読み込み
│   ├── draft_launch.py         # 下書きページ起動
│   ├── lens_calculator_service.py  # レンズ計算処理
│   ├── patient_service.py      # 患者情報入力処理
│   ├── patient_workflow_executor.py  # 患者ワークフロー実行
│   └── save_service.py         # 保存処理（PDF、下書き、CSV移動）
│
├── utils/                       # ユーティリティ
│   ├── config.ini              # 設定ファイル
│   ├── config_manager.py       # 設定管理
│   ├── constants.py            # 定数定義
│   ├── env_loader.py           # 環境変数ローダー
│   └── log_rotation.py         # ログローテーション
│
├── widgets/                     # GUI コンポーネント
│   ├── __init__.py
│   └── progress_window.py      # 進捗表示ウィンドウ
│
├── scripts/                     # 開発用スクリプト
│   ├── __init__.py
│   ├── project_structure.py    # プロジェクト構造出力
│   └── version_manager.py      # バージョン管理
│
└── docs/
    ├── LICENSE                  # Apache License 2.0
    └── README.md               # このファイル
```

### 主要ファイルの役割

#### main.py
アプリケーションのエントリーポイント。以下の処理を実行：
- `IPCLOrderAutomation`クラスのインスタンス化
- CSVファイルの一括処理
- 処理完了後の下書きページ起動とPDFフォルダ表示

#### service/automation_service.py
自動化処理の中核。以下の機能を提供：
- 設定ファイルと環境変数の読み込み
- CSVファイルごとの処理フロー制御
- 進捗表示ウィンドウの管理
- エラーハンドリング

#### service/browser_manager.py
Playwrightブラウザのライフサイクル管理：
- ブラウザインスタンスの作成
- ブラウザコンテキストの作成
- 実行環境に応じたブラウザパス設定（PyInstaller対応）

#### service/patient_workflow_executor.py
患者データ処理ワークフロー全体を統合：
- 各サービスを組み合わせて患者データ処理を実行
- ログイン→患者情報入力→測定データ入力→計算→保存の一連の流れを管理
- 進捗表示の更新

#### service/csv_handler.py
CSVファイルの読み込みと解析：
- 複数エンコーディング対応（CP932、UTF-8）
- CSVデータの構造化

#### service/lens_calculator_service.py
レンズ計算関連の処理：
- レンズ計算モーダルの操作
- 眼別タブの選択
- 測定データの入力
- レンズタイプの自動選択
- ATA/WTWデータの入力
- 計算ボタンのクリック

#### service/save_service.py
保存処理全般：
- PDF自動ダウンロードと保存
- 下書き保存
- 処理済みCSVファイルの移動

#### widgets/progress_window.py
Tkinterベースの進捗表示ウィンドウ：
- 処理状況のリアルタイム表示
- カスタマイズ可能なウィンドウサイズとフォント

## 機能説明

### ブラウザ管理（BrowserManager）

#### __init__(headless: bool = True)
ブラウザマネージャーを初期化します。

**パラメータ**:
- `headless`: ヘッドレスモード（True: ブラウザ非表示、False: ブラウザ表示）

**処理内容**:
- PyInstaller実行環境の検出と対応
- Playwrightブラウザパスの自動設定

#### create_browser(playwright: Playwright) -> Browser
ブラウザインスタンスを作成します。

#### create_context(browser: Browser) -> BrowserContext
ダウンロードを許可するブラウザコンテキストを作成します。

#### create_page(context: BrowserContext) -> Page
新しいページを作成します。

### ワークフロー実行（PatientWorkflowExecutor）

#### execute(page: Page, idx: int, total: int, data: dict) -> tuple[bool, Path | None]
患者データ処理の完全なワークフローを実行します。

**パラメータ**:
- `page`: Playwrightのページオブジェクト
- `idx`: 現在の処理インデックス
- `total`: 総処理件数
- `data`: 患者データの辞書

**戻り値**:
- `(save_success, pdf_path)`: 保存成功フラグとPDFファイルパス

**実行フロー**:
1. ログイン
2. 患者情報入力
3. レンズ計算・注文モーダルを開く
4. 眼のタブ選択(両眼、右眼、左眼)
5. 誕生日入力
6. 測定データ入力
7. レンズタイプ選択
8. ATA/WTWデータ入力
9. レンズ計算実行
10. 計算結果をPDFに保存
11. 入力したデータを保存
12. 下書き保存

### 認証機能（AuthService）

#### login(page: Page)
IPCL注文システムへのログイン処理を実行します。

**パラメータ**:
- `page`: Playwrightのページオブジェクト

**処理内容**:
1. ログインページへ遷移
2. メールアドレスとパスワードを入力
3. サインインボタンをクリック
4. ページ読み込み完了を待機

### 患者情報処理（PatientService）

#### fill_patient_info(page: Page, data: dict)
患者の基本情報を入力します。

**パラメータ**:
- `page`: Playwrightのページオブジェクト
- `data`: 患者データの辞書

**入力項目**:
- 患者ID
- 性別（ドロップダウン選択）
- 手術日

#### fill_birthday(page: Page, birthday: str)
誕生日を入力します。フレーム内の入力フィールドに対応。

**パラメータ**:
- `page`: Playwrightのページオブジェクト
- `birthday`: 誕生日（MM/DD/YYYY形式）

**処理内容**:
- MM/DD/YYYY形式をDD/MM/YYYY形式に変換
- フレーム内の誕生日入力フィールドに入力

### レンズ計算処理（LensCalculatorService）

#### open_lens_calculator(page: Page)
レンズ計算・注文モーダルを開きます。

#### select_eye_tab(page: Page, eye: str)
対象眼のタブを選択します。

**パラメータ**:
- `eye`: "両眼", "右眼", または "左眼"

**処理内容**:
- 両眼の場合: バックアップレンズのチェックボックスを有効化

#### fill_measurement_data(page: Page, data: dict, eye: str)
測定データを入力します。

**入力項目**（眼ごと）:
- 球面度数（SPH）
- 乱視度数（Cyl）
- 乱視軸（Axis）
- 前房深度（ACD）
- 角膜中心厚（Pachy）
- 角膜水晶体距離（CLR）
- 角膜屈折力（K1、K2）
- K1の軸（K1 Axis）
- 手術惹起乱視（SIA）
- 切開位置（Ins）

#### select_lens_type(page: Page, data: dict, eye: str)
レンズタイプを自動選択します。

**選択ロジック**:
```python
if Cyl == 0:
    レンズタイプ = "IPCL V2.0 Mono"
else:
    レンズタイプ = "IPCL V2.0 Toric"
```

#### fill_ata_wtw_data(page: Page, data: dict, eye: str)
ATA/WTW測定データを入力します。

**入力項目**（眼ごと）:
- ATA値
- CASIA WTW（手動測定）
- Caliper WTW

#### click_calculate_button(page: Page)
レンズ計算ボタンをクリックし、計算を実行します。

### 保存処理（SaveService）

#### click_save_pdf_button(page: Page, patient_id: str, patient_name: str) -> str
PDFをダウンロードして保存します。

**パラメータ**:
- `patient_id`: 患者ID
- `patient_name`: 患者名

**戻り値**:
- 保存されたPDFファイルのパス

**ファイル名形式**:
```
IPCLdata_ID{patient_id}_{timestamp}.pdf
```

#### save_input(page: Page)
入力内容を保存します（モーダル内の保存ボタン）。

#### save_draft(page: Page) -> bool
下書きとして保存します。

**戻り値**:
- `True`: 保存成功
- `False`: 保存失敗またはスキップ

#### move_csv_to_calculated(csv_path: Path)
処理済みCSVファイルをcalculatedディレクトリに移動します。

### CSV処理（CSVHandler）

#### read_csv_file(csv_path: Path) -> list[dict]
CSVファイルを読み込み、患者データのリストを返します。

**機能**:
- CP932とUTF-8のエンコーディング自動判定
- カラム名を辞書キーにマッピング

**戻り値**:
- 患者データの辞書のリスト

### 進捗表示（ProgressWindow）

#### create()
進捗表示ウィンドウを作成します。

**機能**:
- 画面中央に配置
- カスタマイズ可能なサイズとフォント

#### update(message: str)
進捗メッセージを更新します。

#### close()
ウィンドウを閉じます。

## 設定ファイル

### config.ini

#### [Appearance]
```ini
font_size = 11              # 進捗ウィンドウのフォントサイズ
window_width = 450          # ウィンドウ幅（ピクセル）
window_height = 150         # ウィンドウ高さ（ピクセル）
```

#### [Chrome]
```ini
chrome_path = C:\Program Files\Google\Chrome\Application\chrome.exe
```
Chromeの実行ファイルパス。下書きページ起動に使用。

#### [Paths]
```ini
csv_dir = C:\Shinseikai\IPCLCalc\csv                    # CSV入力ディレクトリ
calculated_dir = C:\Shinseikai\IPCLCalc\csv\calculated  # 処理済みCSV移動先
error_dir = C:\Shinseikai\IPCLCalc\csv\error           # エラーファイル移動先
log_dir = C:\Shinseikai\IPCLCalc\logs                  # ログ出力先
pdf_dir = C:\Shinseikai\IPCLCalc\csv\pdf               # PDF保存先
```

#### [Settings]
```ini
headless = True             # ヘッドレスモード（True: ブラウザ非表示、False: ブラウザ表示）
```

**開発・デバッグ時**: `headless = False`に設定して動作を確認することを推奨

#### [URL]
```ini
base_url = https://www.ipcl-jp.com/awsystem/order/create    # 注文作成ページ
draft_url = https://www.ipcl-jp.com/awsystem/order/drafts   # 注文下書き一覧ページ
```

### .env

```env
# IPCL注文システムのログイン情報
EMAIL=your-email@example.com
PASSWORD=your-password
```

**セキュリティ注意事項**:
- `.env`ファイルは`.gitignore`に追加してください
- パスワードは平文で保存されるため、ファイルのアクセス権限に注意
- 定期的なパスワード変更を推奨

## 開発者向け情報

### 開発環境のセットアップ

#### 1. 仮想環境の作成

```bash
python -m venv venv
venv\Scripts\activate
```

#### 2. 開発用パッケージのインストール

```bash
pip install -r requirements.txt
pip install pytest pytest-cov
```

#### 3. テストの実行

```bash
# 全テスト実行
pytest

# 特定のテストファイル実行
pytest tests/test_main.py

# カバレッジ付きテスト実行
pytest --cov
```

### ビルド方法

PyInstallerを使用して実行ファイルを作成できます：

```bash
python build.py
```

**ビルド処理**:
1. バージョン番号を自動インクリメント（`app/__init__.py`と`docs/README.md`を更新）
2. PyInstallerでWindows実行ファイルを作成
3. `dist/`ディレクトリに出力

### バージョン管理

#### バージョン情報の場所
- `app/__init__.py`: `__version__`と`__date__`変数
- `docs/README.md`: 先頭のバージョン表記

#### バージョンの更新

```python
from scripts.version_manager import update_version

# パッチバージョンをインクリメント（例: 1.0.0 → 1.0.1）
new_version = update_version()
```

### コーディング規約

#### Pythonコード
- ファイル名: スネークケース（例: `automation_service.py`）
- クラス名: パスカルケース（例: `IPCLOrderAutomation`）
- 関数名: スネークケース（例: `process_csv_file`）

### プロジェクト構造の出力

```bash
python scripts/project_structure.py
```

`project_structure.txt`にディレクトリツリーが出力されます。

## トラブルシューティング

### よくある問題と解決方法

#### 1. Playwrightが見つからない

**症状**: `playwright: command not found`

**解決方法**:
```bash
pip install playwright
playwright install chromium
```

#### 2. ブラウザが起動しない

**症状**: ブラウザドライバーのエラー

**解決方法**:
```bash
# ブラウザドライバーを強制再インストール
playwright install --force chromium
```

#### 3. ログインに失敗する

**症状**: 認証エラーまたはタイムアウト

**解決方法**:
- `.env`ファイルのEMAILとPASSWORDを確認
- ネットワーク接続を確認
- IPCL注文システムのログイン情報が正しいか確認
- `config.ini`で`headless = False`に設定し、ブラウザを表示して動作を確認

#### 4. CSVファイルが読み込めない

**症状**: `UnicodeDecodeError`または`FileNotFoundError`

**解決方法**:
- ファイル名が`IPCLdata_ID*.csv`形式か確認
- CSVファイルのエンコーディングがCP932またはUTF-8か確認
- `config.ini`の`csv_dir`パスが正しいか確認
- CSVファイルの必須カラムが全て存在するか確認

#### 5. タイムアウトエラーが発生する

**症状**: ページ読み込み中に処理が停止

**解決方法**:
- ネットワーク速度が遅い場合、待機時間を延長：
  ```python
  page.wait_for_timeout(3000)  # 3秒に延長
  ```
- `service/`内の各サービスファイルで`wait_for_timeout`の値を調整

#### 6. PDFが保存されない

**症状**: PDF保存エラーまたは保存先が見つからない

**解決方法**:
- `config.ini`の`pdf_dir`パスが存在するか確認
- ディレクトリを手動で作成：
  ```bash
  mkdir C:\Shinseikai\IPCLCalc\csv\pdf
  ```
- ディスクの空き容量を確認

#### 7. 下書き保存ボタンが無効

**症状**: "下書き保存ボタンが無効のため、処理をスキップしました"

**原因**:
- 入力データが不完全
- レンズ計算が完了していない
- システム側のバリデーションエラー

**解決方法**:
- CSVファイルのデータが全て正しいか確認
- `headless = False`に設定して、ブラウザで実際の入力内容を確認
- エラーメッセージを確認し、該当する入力項目を修正

#### 8. 進捗ウィンドウが表示されない

**症状**: GUIウィンドウが表示されない

**解決方法**:
- Tkinterがインストールされているか確認：
  ```bash
  python -m tkinter
  ```
- Windows環境でTkinterが標準でインストールされていない場合、Python再インストール時に「tcl/tk」を選択

#### 9. 処理が途中で停止する

**症状**: エラーなく処理が停止

**解決方法**:
- ログファイルを確認：`logs/`ディレクトリ
- `headless = False`に設定してブラウザ動作を確認
- ネットワーク接続を確認
- IPCL注文システムのメンテナンス時間を確認

#### 10. 複数ファイル処理時にエラー

**症状**: 最初のファイルは成功するが、2件目以降でエラー

**解決方法**:
- 各ファイルの処理後にブラウザが正しく閉じられているか確認
- CSVファイルのフォーマットが統一されているか確認

### デバッグモード

開発・デバッグ時は以下の設定を推奨：

```ini
[Settings]
headless = False
```

これにより、ブラウザの動作を目視で確認できます。

### ログの確認

ログファイルは`logs/`ディレクトリに保存されます：

```
logs/
└── IPCLCalc.log
└── IPCLCalc.log.2025-10-06
└── IPCLCalc.log.2025-10-05
```

ログは毎日ローテーションされ、設定された日数（デフォルト7日）保持されます。

## ライセンス

このプロジェクトは**Apache License 2.0**の下でライセンスされています。

詳細については、[LICENSE](LICENSE)ファイルを参照してください。

---

## サポート

### お問い合わせ

問題が発生した場合や機能追加の要望がある場合は、GitHubのIssuesページをご利用ください。

---

**IPCLCalc** - IPCL注文業務を効率化し、眼科医療従事者の負担を軽減します。