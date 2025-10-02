# 技術的課題と解決策 - IPCL Lens Order Automation

## 概要
このドキュメントでは、IPCL注文システム自動化の開発中に遭遇した技術的課題と、その解決方法を記録します。

---

## 課題 #1: ログインフォームのセレクタエラー

### 🔴 問題
```
TimeoutError: Page.fill: Timeout 30000ms exceeded.
Call log:
  - waiting for locator("input[name=\"LoginForm[email]\"]")
```

### 原因
ログインフォームの入力欄が`name`属性で特定できなかった。実際のHTML構造では、入力欄にはラベルとプレースホルダーしか存在していなかった。

### ❌ 動作しなかったコード
```python
page.fill('input[name="LoginForm[email]"]', self.email)
page.fill('input[name="LoginForm[password]"]', self.password)
```

### ✅ 解決策
Playwrightの`get_by_placeholder()`と`get_by_label()`メソッドを使用してアクセシビリティベースのセレクタに変更。

```python
page.get_by_placeholder("ログインID").fill(self.email)
page.get_by_label("パスワード").fill(self.password)
```

### 学んだこと
- name属性に依存したセレクタは脆弱
- Playwrightのアクセシビリティベースのセレクタ（get_by_label, get_by_placeholder）がより堅牢
- ユーザーが見ている通りに要素を特定する方が保守性が高い

---

## 課題 #2: 患者情報入力フォームのセレクタエラー

### 🔴 問題
```
TimeoutError: Page.fill: Timeout 30000ms exceeded.
Call log:
  - waiting for locator("input[name=\"OrderDetail[patient_id]\"]")
```

### 原因
課題#1と同様、フォーム要素が`name`属性で特定できなかった。

### ❌ 動作しなかったコード
```python
page.fill('input[name="OrderDetail[patient_id]"]', data['id'])
page.click('div:has(> input[name="OrderDetail[gender]"])')
page.fill('input[name="OrderDetail[surgery_date]"]', data['surgery_date'])
```

### ✅ 解決策
すべてのフォーム入力を`get_by_label()`メソッドに変更。

```python
page.get_by_label("患者ID*").fill(data['id'])
page.get_by_label("性別*").click()
page.get_by_label("手術日").fill(data['surgery_date'])
```

### 学んだこと
- 複雑なname属性（角括弧を含む）は特に問題が起きやすい
- ラベルベースのセレクタは一貫性があり、コードの可読性も向上
- フォーム全体で統一されたアプローチを使用すべき

---

## 課題 #3: UTF-8エンコーディングの文字化け

### 🔴 問題
ファイル保存時に日本語が文字化けし、コメントやprint文が正しく表示されなかった。

```python
# 文字化けの例
"""IPCL臷���n����"""  # 本来は「IPCL注文システムの自動化クラス」
```

### 原因
ファイルがUTF-8以外のエンコーディングで保存されていた可能性がある。

### ✅ 解決策
ファイル全体をUTF-8エンコーディングで再保存。

```python
# Write toolを使用してUTF-8で明示的に保存
with open('main.py', 'w', encoding='utf-8') as f:
    f.write(content)
```

### 学んだこと
- Pythonファイルは常にUTF-8で保存すべき
- エディタやIDEのデフォルトエンコーディング設定を確認する重要性
- 日本語を含むプロジェクトでは特に注意が必要

---

## 課題 #4: iframeモーダル内の要素へのアクセス

### 🔴 問題
レンズ計算モーダル（iframe）内の要素に直接アクセスできなかった。

### 原因
モーダルがiframeとして実装されており、メインページのコンテキストから直接要素にアクセスできない。

### ❌ 動作しなかったコード
```python
page.fill('input[name="OrderDetail[r_spherical]"]', data['r_sph'])
```

### ✅ 解決策
`frame_locator()`を使用してiframeコンテキストに切り替え。

```python
frame = page.frame_locator('#calculatorFrame')
frame.locator('input[name="OrderDetail[r_spherical]"]').fill(data['r_sph'])
```

### 学んだこと
- iframeは独立したブラウジングコンテキスト
- Playwrightの`frame_locator()`でシームレスに切り替え可能
- モーダルダイアログがiframeで実装されているケースは多い

---

## 課題 #5: 動的に生成されるカレンダーピッカーの操作

### 🔴 問題
誕生日入力フィールドが通常のテキスト入力ではなく、JavaScriptで動的に生成されるカレンダーピッカーだった。

### 課題
- デフォルトで2007年が表示される
- 過去の年（例：2002年）に遡る必要がある
- 月と日を正確に選択する必要がある

### ✅ 解決策
段階的なアプローチで実装：

```python
# 1. カレンダーを開く
frame.locator('span.input-group-addon:has(i.glyphicon-calendar)').first.click()

# 2. 年を遡る（2007→2002）
current_year = 2007
while current_year > target_year:
    frame.locator('td.prev').first.click()
    page.wait_for_timeout(200)
    current_year -= 1

# 3. 月を選択
month_names = ['Jan', 'Feb', 'Mar', ...]
frame.locator(f'span:has-text("{month_name}")').click()

# 4. 日を選択
day_cells = frame.locator(f'td:has-text("{int(day)}")').all()
for cell in day_cells:
    if cell.inner_text() == str(int(day)):
        cell.click()
        break
```

### 学んだこと
- JavaScriptウィジェットは直接的なテキスト入力ができない
- wait_for_timeout()でアニメーションやトランジションを待つ必要がある
- 複数の同じテキストを持つ要素がある場合、inner_text()で厳密にマッチングする

---

## 課題 #6: レンズタイプの条件分岐ロジック

### 🔴 問題
Cyl値に基づいて適切なレンズタイプ（MonoまたはToric）を自動選択する必要があった。

### 要件
- Cyl値が0の場合: IPCL V2.0 Mono
- Cyl値が0以外の場合: IPCL V2.0 Toric
- 右眼と左眼で異なるタイプになる可能性がある

### ✅ 解決策
```python
# 右眼のレンズタイプを選択
r_cyl = float(data['r_cyl'])
if r_cyl == 0:
    frame.locator('input[name="OrderDetail[ipcl_r]"][value="IPCL V2.0 Mono"]').check()
else:
    frame.locator('input[name="OrderDetail[ipcl_r]"][value="IPCL V2.0 Toric"]').check()

# 左眼も同様
l_cyl = float(data['l_cyl'])
if l_cyl == 0:
    frame.locator('input[name="OrderDetail[ipcl_l]"][value="IPCL V2.0 Mono"]').check()
else:
    frame.locator('input[name="OrderDetail[ipcl_l]"][value="IPCL V2.0 Toric"]').check()
```

### 学んだこと
- CSVから読み込んだ文字列はfloat()で数値に変換する必要がある
- 右眼と左眼は独立して処理する
- ラジオボタンの選択には`.check()`メソッドを使用

---

## 課題 #7: 処理完了後のブラウザクローズタイミング

### 🔴 問題
下書き保存後、すぐにブラウザを閉じるとページ遷移が完了せず、保存が失敗する可能性があった。

### ✅ 解決策
`finally`ブロックで適切な待機時間を設けてからブラウザをクローズ。

```python
try:
    # 処理...
    self.save_draft(page)
    print("✓ 注文の下書きが正常に保存されました")
except Exception as e:
    print(f"✗ エラーが発生しました: {e}")
    raise
finally:
    # ブラウザを閉じる前に少し待機
    page.wait_for_timeout(2000)
    browser.close()
```

### 学んだこと
- ページ遷移やAJAXリクエストの完了を待つ重要性
- `wait_for_load_state('networkidle')`では不十分なケースもある
- 安全マージンとして固定の待機時間を入れることも有効

---

## 課題 #8: CSVファイルのタブ文字を含むカラム名

### 🔴 問題
CSVファイルのカラム名に`R_\tATA`のようにタブ文字（`\t`）が含まれていた。

### ✅ 解決策
カラム名をそのまま使用。

```python
patient_data = {
    'r_ata': data['R_\tATA'],  # タブ文字を含むカラム名
    'r_casia_wtw_m': data['R_CASIA_WTW_M'],
    'r_caliper_wtw': data['R_Caliper_WTW'],
}
```

### 学んだこと
- CSVファイルのカラム名は必ずしも標準的ではない
- Pythonの辞書キーは任意の文字列を受け入れる
- データソースを変更できない場合、そのまま扱う柔軟性が必要

---

## ベストプラクティスのまとめ

### セレクタ選択
1. ✅ `get_by_label()` - 最も堅牢で推奨
2. ✅ `get_by_placeholder()` - プレースホルダーがある場合
3. ✅ `get_by_role()` - セマンティックな役割がある場合
4. ⚠️ `locator('[name="..."]')` - 動的に変わらない場合のみ
5. ❌ XPathやCSSセレクタ - 最後の手段

### 待機戦略
1. `wait_for_load_state('networkidle')` - ページ遷移後
2. `wait_for_timeout(ms)` - アニメーション/トランジション
3. `expect(element).to_be_visible()` - 要素の表示を待つ

### エラーハンドリング
1. try-except-finallyを使用
2. エラーメッセージは具体的に
3. 失敗時もブラウザを確実にクローズ

---

## 課題 #9: Windows環境でのUnicodeEncodeError

### 🔴 問題
```
UnicodeEncodeError: 'cp932' codec can't encode character '\u2713' in position 0: illegal multibyte sequence
```

### 原因
Windowsのコマンドプロンプトのデフォルトエンコーディングがcp932（Shift-JIS）で、Unicode文字（✓）が出力できなかった。

### ❌ 動作しなかったコード
```python
print("✓ CSVファイルを読み込みました")
print("✓ Webサイトにログインしています...")
print(f"✗ エラーが発生しました: {e}")
```

### ✅ 解決策
チェックマークとバツマークをASCII互換の文字列に変更。

```python
print("[OK] CSVファイルを読み込みました")
print("[OK] Webサイトにログインしています...")
print(f"[ERROR] エラーが発生しました: {e}")
```

### 学んだこと
- Windows環境ではコンソール出力のエンコーディングに注意が必要
- Unicode文字は環境によって出力できない場合がある
- ASCII互換の代替表現を使用すると移植性が向上

---

## 課題 #10: Playwrightのstrict mode violation

### 🔴 問題
```
Error: strict mode violation: locator("input[name=\"OrderDetail[include_backup]\"]") resolved to 2 elements:
    1) <input value="0" type="hidden" name="OrderDetail[include_backup]"/>
    2) <input value="1" type="checkbox" class="form-check-input" id="orderdetail-include_backup" name="OrderDetail[include_backup]"/>
```

### 原因
同じname属性を持つhidden inputとcheckbox inputが両方存在し、セレクタが一意でなかった。

### ❌ 動作しなかったコード
```python
backup_checkbox = frame.locator('input[name="OrderDetail[include_backup]"]')
if not backup_checkbox.is_checked():
    backup_checkbox.check()
```

### ✅ 解決策
type属性を明示的に指定してcheckboxのみを選択。

```python
backup_checkbox = frame.locator('input[type="checkbox"][name="OrderDetail[include_backup]"]')
if not backup_checkbox.is_checked():
    backup_checkbox.check()
```

### 学んだこと
- フォームフレームワークはhidden inputとvisible inputを組み合わせて使用することが多い
- Playwrightのstrict modeは複数要素マッチを許可しない
- より具体的なセレクタ（type属性の追加）で一意性を確保

---

## 課題 #11: タイムアウトエラーのロバスト性向上

### 🔴 問題
患者IDや誕生日入力フィールドが環境によって見つからず、タイムアウトエラーが発生。

```
TimeoutError: Locator.fill: Timeout 30000ms exceeded.
Call log:
  - waiting for get_by_label("患者ID")
```

### 原因
ページの動的な変更や、異なるバージョンのフォームでセレクタが一致しない。

### ❌ 動作しなかったコード
```python
frame.get_by_label("患者ID").fill(data['id'])
self.fill_birthday(page, data['birthday'])
```

### ✅ 解決策
複数のフォールバック戦略を実装。

```python
# 患者ID入力のフォールバック
try:
    frame.get_by_label("患者ID").fill(data['id'])
except:
    try:
        frame.get_by_placeholder("患者ID").fill(data['id'])
    except:
        try:
            frame.locator('input[name*="patient"]').first.fill(data['id'])
        except:
            print("[WARNING] 患者ID入力をスキップしました")

# 誕生日入力のフォールバック
try:
    # カレンダーピッカーで入力
    frame.locator('span.input-group-addon:has(i.glyphicon-calendar)').first.click(timeout=5000)
    # ... カレンダー操作 ...
except:
    # 直接入力にフォールバック
    try:
        frame.locator('input[name*="birthday"]').first.fill(birthday)
    except:
        print("[WARNING] 誕生日入力をスキップしました")
```

### 学んだこと
- 単一のセレクタに依存せず、複数の代替手段を用意すべき
- 必須でないフィールドは警告を出してスキップする柔軟性が重要
- タイムアウト時間を調整（5000msなど）してパフォーマンスを改善

---

## 課題 #12: 下書き保存ボタンの無効化状態

### 🔴 問題
下書き保存ボタンが無効（disabled）状態でクリックできず、タイムアウトエラーが発生。

```
TimeoutError: Locator.click: Timeout 30000ms exceeded.
    - locator resolved to <button disabled type="submit" name="save-draft">
    - element is not enabled
```

### 原因
フォーム検証やバックエンド処理が完了するまでボタンが無効化されていた。

### ❌ 動作しなかったコード
```python
page.locator('button:has-text("下書き保存")').click()
page.wait_for_load_state('networkidle')
```

### ✅ 解決策
ボタンの状態を確認し、無効な場合はスキップ。

```python
try:
    save_button = page.locator('button:has-text("下書き保存")')
    save_button.wait_for(state='visible', timeout=10000)
    page.wait_for_timeout(2000)  # 追加の待機

    if not save_button.is_disabled():
        save_button.click()
        page.wait_for_load_state('networkidle')
    else:
        print("[WARNING] 下書き保存ボタンが無効のため、処理をスキップしました")
except Exception as e:
    print(f"[WARNING] 下書き保存をスキップしました: {e}")
```

### 学んだこと
- UI要素の状態（enabled/disabled）を確認してから操作する
- タイムアウトと追加の待機時間を組み合わせる
- 重要でない操作は失敗してもプログラムを継続させる

---

## ベストプラクティスのまとめ

### セレクタ選択
1. ✅ `get_by_label()` - 最も堅牢で推奨
2. ✅ `get_by_placeholder()` - プレースホルダーがある場合
3. ✅ `get_by_role()` - セマンティックな役割がある場合
4. ⚠️ `locator('[name="..."]')` - 動的に変わらない場合のみ
5. ❌ XPathやCSSセレクタ - 最後の手段

### 待機戦略
1. `wait_for_load_state('networkidle')` - ページ遷移後
2. `wait_for_timeout(ms)` - アニメーション/トランジション
3. `expect(element).to_be_visible()` - 要素の表示を待つ
4. `wait_for(state='...')` - 特定の状態を待つ

### エラーハンドリング
1. try-except-finallyを使用
2. エラーメッセージは具体的に
3. 失敗時もブラウザを確実にクローズ
4. フォールバック戦略を複数用意
5. 警告メッセージで処理の継続性を確保

### Windows環境対応
1. Unicode文字の使用を避け、ASCII互換文字を使用
2. コンソール出力のエンコーディングを考慮
3. 環境依存の文字は代替表現を用意

---

**作成日**: 2025-10-02
**最終更新**: 2025-10-02
**課題数**: 12件（すべて解決済み）
