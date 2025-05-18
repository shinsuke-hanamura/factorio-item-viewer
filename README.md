# factorio-item-viewer

## 概要

このドキュメントでは、Factorioゲームのアイテム情報をウェブサイトから取得するための3つのPythonスクリプトの仕様と使用方法について説明します。これらのスクリプトは、Factorio Wikiからアイテム情報、レシピ情報、容量情報などを抽出し、プログラムで利用可能な形式で提供します。

## スクリプト一覧

1. **fetch_items_links.py** - アイテム名からURLを取得するツール
2. **get_item_recipe.py** - レシピページから材料と生成物の情報を抽出するツール
3. **get_item_volume.py** - アイテムの容量情報を抽出するツール
4. **factorio_item.py** - アイテム情報を管理するための共通クラスを提供するモジュール
5. **factorio_config.py** - 設定を管理するためのクラスを提供するモジュール

## 共通仕様

### データ保存形式

アイテム情報は共通のCSVファイル（デフォルト: `factorio_items.csv`）に保存されます。このCSVファイルは以下のフィールドを含みます：

- `日本語アイテム名` - アイテムの日本語名
- `アイテムコード` - アイテムの英語コード（URLの一部として使用）
- `URL` - アイテムのFactorio Wiki URL

### 設定ファイル

プログラムの動作は設定ファイル（デフォルト: `factorio_config.json`）で制御できます。主な設定項目は以下の通りです：

- `data_dir` - データディレクトリのパス
- `csv_file` - CSVファイルの名前
- `json_dir` - JSONファイルを保存するディレクトリ
- `language` - 使用する言語（`ja`または`en`）
- `game_mode` - ゲームモード（`Base`または`SpaceAge`）
- `log_level` - ログレベル（`DEBUG`、`INFO`、`WARNING`、`ERROR`）
- `wiki_base_url` - WikiのベースURL
- `wiki_materials_page` - Wikiの材料ページ

### 依存関係

すべてのスクリプトは以下のPythonライブラリに依存しています：

- `requests` - HTTPリクエスト用
- `BeautifulSoup` (bs4) - HTMLパース用
- `csv` - CSVファイル操作用
- `logging` - ログ出力用
- `json` - JSON操作用

## 4. factorio_item.py

### 機能概要

Factorioのアイテム情報を扱うための共通クラスを提供します。言語設定によってアイテム名を取得できるようにします。

### 主要クラス

#### `Item`

Factorioのアイテム情報を扱うクラスです。

- **主要メソッド**:
  - `name` - 現在の言語設定に基づいたアイテム名を取得
  - `code` - アイテムコードを取得
  - `url` - アイテムのURLを取得
  - `set_language(language)` - 言語設定を変更

#### `ItemManager`

Factorioのアイテム情報を管理するクラスです。

- **主要メソッド**:
  - `load_items()` - CSVファイルからアイテム情報を読み込む
  - `find_item_by_name(item_name)` - アイテム名からアイテムを検索
  - `find_item_by_code(item_code)` - アイテムコードからアイテムを検索
  - `get_item_url(item_name)` - アイテム名からURLを取得
  - `get_item_code(item_name)` - アイテム名からアイテムコードを取得
  - `set_language(language)` - 言語設定を変更
  - `add_item(item_name_ja, item_code, item_url)` - 新しいアイテム情報をCSVに追加

### 使用例

```python
# ItemManagerの初期化
manager = ItemManager('factorio_items.csv', 'ja')

# アイテム名からURLを取得
url = manager.get_item_url("鉄板")
print(url)  # https://wiki.factorio.com/Iron_plate/ja

# アイテム名からアイテムコードを取得
code = manager.get_item_code("鉄板")
print(code)  # Iron_plate

# 言語設定を変更
manager.set_language('en')
```

## 5. factorio_config.py

### 機能概要

Factorioアイテム情報取得ツールの設定を管理するためのクラスを提供します。JSONファイルから設定を読み込み、各プログラムで使用できるようにします。

### 主要クラス

#### `Config`

設定を管理するクラスです。

- **主要メソッド**:
  - `load_config(config_file)` - 設定ファイルから設定を読み込む
  - `save_config(config_file=None)` - 設定をファイルに保存
  - `get(key, default=None)` - 設定値を取得
  - `set(key, value)` - 設定値を設定
  - `get_csv_path()` - CSVファイルのパスを取得
  - `get_json_path(filename)` - JSONファイルのパスを取得
  - `get_language()` - 言語設定を取得
  - `get_game_mode()` - ゲームモード設定を取得
  - `get_log_level()` - ログレベル設定を取得
  - `set_log_level()` - ログレベルを設定する
  - `get_wiki_base_url()` - WikiのベースURLを取得
  - `get_wiki_materials_page()` - Wikiの材料ページを取得

### 使用例

```python
# 設定を読み込む
config = load_config('my_config.json')

# CSVパスを取得
csv_path = config.get_csv_path()

# 言語設定を取得
language = config.get_language()

# 設定値を変更
config.set('language', 'en')

# 設定を保存
config.save_config()
```

## 1. fetch_items_links.py

### 機能概要

Factorio Wikiの「Materials and recipes」ページからアイテム情報を取得し、CSVファイルに保存します。また、CSVファイルからアイテム名に対応するURLを検索する機能も提供します。

### コマンドライン引数

```
python fetch_items_links.py [-c <設定ファイルパス>] [-d]
```

- `-c, --config`: 設定ファイルのパス
- `-d, --debug`: デバッグモードを有効化（詳細なログを出力）

### 主要関数

#### `fetch_items_from_materials_page(config)`

Factorio Wikiの材料とレシピページからアイテム情報を取得し、CSVファイルに保存します。

- **引数**:
  - `config` (Config): 設定オブジェクト
- **処理内容**:
  1. 設定からWikiのURLを取得
  2. ページ内のアイテムアイコン要素を検索
  3. 各アイテムの日本語名、アイテムコード、URLを抽出
  4. 重複を排除してCSVファイルに書き出し

#### `load_item_url(item_name, csv_path=None, language=None)`

アイテム名からURLを取得する関数です。

- **引数**:
  - `item_name` (str): アイテムの名前
  - `csv_path` (str): CSVファイルのパス（デフォルト: スクリプトと同じディレクトリの'factorio_items.csv'）
  - `language` (str): 言語コード（デフォルト: Itemクラスのデフォルト言語）
- **戻り値**:
  - アイテムのWikiページURL、見つからない場合はNone
- **処理内容**:
  1. ItemManagerを初期化
  2. アイテム名からURLを取得

### 使用例

```bash
# デフォルト設定でアイテム情報を取得
python fetch_items_links.py

# カスタム設定ファイルを使用
python fetch_items_links.py -c my_config.json

# デバッグモードを有効化
python fetch_items_links.py -d
```

## 2. get_item_recipe.py

### 機能概要

Factorio Wikiのアイテムページからレシピ情報（材料と生成物）を抽出し、アイテム情報ファイルにレシピ情報を付記してJSON形式で保存します。アイテム情報ファイルは「item_アイテム名.json」の形式で保存され、既存のファイルがある場合はそれに追記・上書きします。また、新しいアイテム情報をCSVに追加する機能も提供します。

### コマンドライン引数

```
python get_item_recipe.py -i <アイテム名> [-m <ゲームモード>] [-c <CSVファイルパス>] [-d] [-l <言語コード>] [--config <設定ファイルパス>]
python get_item_recipe.py -i <アイテム名> -a <アイテムコード> <URL>
```

- `-i, --item`: アイテム名 (必須)
- `-m, --mode`: ゲームモード (Base または SpaceAge, デフォルト=SpaceAge)
- `-c, --csv`: CSVファイルのパス（デフォルト=factorio_items.csv）
- `-d, --debug`: デバッグモードを有効化（詳細なログを出力）
- `-a, --add`: 新しいアイテムをCSVに追加（アイテムコードとURLを指定）
- `-l, --lang`: 言語コード (ja または en, デフォルト=ja)
- `--config`: 設定ファイルのパス

### 主要関数

#### `get_recipe(page_url, game_mode='SpaceAge')`

指定されたページURLからFactorioのレシピ情報を取得します。

- **引数**:
  - `page_url` (str): レシピ情報を取得するページのURL
  - `game_mode` (str): ゲームモード ('Base' または 'SpaceAge')
- **戻り値**:
  - `tuple`: (材料リスト, 生成物情報)
    - 材料リスト: [(アイテムコード, 数量), ...] の形式
    - 生成物情報: (アイテムコード, 数量) または None
- **処理内容**:
  1. 指定されたURLからページを取得
  2. レシピテーブルを検索
  3. 材料と生成物の情報を抽出

#### `get_item_code_from_name(item_name, csv_path=None, language=None)`

アイテム名からアイテムコードを取得する関数です。

- **引数**:
  - `item_name` (str): アイテムの名前
  - `csv_path` (str): CSVファイルのパス
  - `language` (str): 言語コード
- **戻り値**:
  - アイテムコード、見つからない場合はNone
- **処理内容**:
  1. ItemManagerを初期化
  2. アイテム名からアイテムコードを取得

#### `create_item_json(item_name, materials, product, csv_path=None, language=None)`

レシピ情報をJSON形式のデータとして作成し、アイテム情報ファイルに付記します。

- **引数**:
  - `item_name` (str): アイテムの名前
  - `materials` (list): 材料リスト [(アイテムコード, 数量), ...]
  - `product` (tuple): 生成物情報 (アイテムコード, 数量) または None
  - `csv_path` (str): CSVファイルのパス
  - `language` (str): 言語コード
- **戻り値**:
  - `dict`: JSON形式のレシピデータ
- **処理内容**:
  1. アイテムコードを取得
  2. 材料情報をJSONに変換
  3. 生成物情報をJSONに追加

### 出力JSON形式

```json
{
    "item_name": "鉄板",
    "item_code": "Iron_plate",
    "recipe": [
        {
            "item_code": "Iron_ore",
            "consumption_number": 1
        }
    ],
    "production_number": 1
}
```

### 使用例

```bash
# 鉄板のレシピ情報を取得（Baseモード）
python get_item_recipe.py -i 鉄板 -m Base

# 電子回路のレシピ情報を取得（カスタムCSVファイル使用）
python get_item_recipe.py -i 電子回路 -c my_items.csv

# 崖用発破のレシピ情報を取得（デバッグモード）
python get_item_recipe.py -i 崖用発破 -d

# 英語名でアイテムを指定
python get_item_recipe.py -i Iron_plate -l en

# カスタム設定ファイルを使用
python get_item_recipe.py -i 鉄板 --config my_config.json

# 新しいアイテムをCSVに追加
python get_item_recipe.py -i 崖用発破 -a Cliff_explosives https://wiki.factorio.com/Cliff_explosives/ja
```

## 3. get_item_volume.py

### 機能概要

Factorio Wikiのアイテム情報ページからロケット容量を取得し、アイテムの容積を計算します。

### コマンドライン引数

```
python get_item_volume.py -i <アイテム名> [-c <CSVファイルパス>] [-d] [-l <言語コード>] [--config <設定ファイルパス>]
```

- `-i, --item`: アイテム名 (必須)
- `-c, --csv`: CSVファイルのパス（デフォルト=factorio_items.csv）
- `-d, --debug`: デバッグモードを有効化（詳細なログを出力）
- `-l, --lang`: 言語コード (ja または en, デフォルト=ja)
- `--config`: 設定ファイルのパス

### 主要関数

#### `get_item_rocket_capacity(page_url)`

指定されたページURLからアイテムのロケット容量を取得します。

- **引数**:
  - `page_url` (str): アイテム情報を取得するページのURL
- **戻り値**:
  - `int`: ロケット容量、見つからない場合はNone
- **処理内容**:
  1. 指定されたURLからページを取得
  2. 「ロケット容量」を含むテーブルセルを検索
  3. 数値を抽出して返す

#### `calculate_item_volume(rocket_capacity)`

ロケット容量からアイテムの容積を計算します。

- **引数**:
  - `rocket_capacity` (int): アイテムのロケット容量
- **戻り値**:
  - `float`: アイテムの容積、ロケット容量がNoneまたは0の場合はNone
- **処理内容**:
  1. ロケット容積（1000）をロケット容量で割って容積を計算

### 出力JSON形式

```json
{
    "item_name": "鉄板",
    "item_code": "Iron_plate",
    "rocket_capacity": 100,
    "volume": 10.0
}
```

### 使用例

```bash
# 鉄板の容積情報を取得
python get_item_volume.py -i 鉄板

# 電子回路の容積情報を取得（カスタムCSVファイル使用）
python get_item_volume.py -i 電子回路 -c my_items.csv

# 崖用発破の容積情報を取得（デバッグモード）
python get_item_volume.py -i 崖用発破 -d

# 英語名でアイテムを指定
python get_item_volume.py -i Iron_plate -l en

# カスタム設定ファイルを使用
python get_item_volume.py -i 鉄板 --config my_config.json
```

## ワークフロー例

以下は、これらのスクリプトを使用した一般的なワークフローの例です：

1. まず、`fetch_items_links.py`を実行してアイテム情報を取得し、CSVファイルに保存します：
   ```bash
   python fetch_items_links.py
   ```

2. 次に、特定のアイテムのレシピ情報を取得します：
   ```bash
   python get_item_recipe.py -i 鉄板
   ```

3. 同じアイテムの容積情報を取得します：
   ```bash
   python get_item_volume.py -i 鉄板
   ```

4. 新しいアイテムをCSVに追加する場合：
   ```bash
   python get_item_recipe.py -i 新アイテム -a New_item https://wiki.factorio.com/New_item/ja
   ```

5. 設定ファイルを作成して使用する場合：
   ```bash
   python factorio_config.py -c
   python fetch_items_links.py --config factorio_config.json
   ```

## 注意事項

- これらのスクリプトは、Factorio Wikiの構造に依存しています。Wikiの構造が変更された場合、スクリプトが正常に動作しない可能性があります。
- デバッグモード（`-d`オプション）を使用すると、詳細なログが出力され、問題の診断に役立ちます。
- CSVファイルは、設定で指定されたディレクトリに保存されます（別のパスを指定しない限り）。
- JSONファイルは、設定で指定されたディレクトリに保存されます。
- ゲームモードは「Base」または「SpaceAge」から選択できます（`get_item_recipe.py`のみ）。
- 言語設定は「ja」（日本語）または「en」（英語）から選択できます。
