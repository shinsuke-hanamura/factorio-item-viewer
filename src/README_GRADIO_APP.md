# Factorio アイテムビューアー Gradio アプリ

## 概要

このGradioアプリは、`get_item_recipe.py`と`get_item_volume.py`の実行結果であるJSONファイルを読み込み、Factorioのアイテム情報をWebブラウザ上で表示します。

## 機能

### 1. アイテム詳細表示
- アイテムの基本情報（名前、コード、生産数）
- レシピ情報（必要な材料とその数量）
- 容量情報（ロケット容量、容積）
- 生のJSONデータ表示

### 2. アイテム検索
- アイテム名またはアイテムコードによる検索
- リアルタイム検索結果の表示

### 3. アイテム一覧表示
- すべてのアイテム情報をテーブル形式で表示
- 材料数などの統計情報も含む

## 必要な環境

### Python バージョン
- Python 3.8 以上

### 必要なライブラリ
```bash
pip install -r requirements.txt
```

または個別にインストール：
```bash
pip install gradio>=4.0.0 pandas>=1.5.0 requests>=2.28.0 beautifulsoup4>=4.11.0
```

## 使用方法

### 1. 基本的な起動

```bash
cd /path/to/factorio-item-viewer/src
python factorio_gradio_app.py
```

アプリが起動すると、以下のようなメッセージが表示されます：
```
🏭 Factorio アイテムビューアーを起動中...
📍 URL: http://127.0.0.1:7860
```

ブラウザで表示されたURLにアクセスしてアプリを使用できます。

### 2. コマンドライン オプション

```bash
python factorio_gradio_app.py [オプション]
```

#### 利用可能なオプション

- `--config CONFIG_FILE`: 設定ファイルのパスを指定
- `--port PORT`: ポート番号を指定（デフォルト: 7860）
- `--host HOST`: ホストアドレスを指定（デフォルト: 127.0.0.1）
- `--share`: 公開リンクを生成（インターネット経由でアクセス可能）

#### 使用例

```bash
# カスタムポートで起動
python factorio_gradio_app.py --port 8080

# 外部からアクセス可能にする
python factorio_gradio_app.py --host 0.0.0.0

# 公開リンクを生成
python factorio_gradio_app.py --share

# カスタム設定ファイルを使用
python factorio_gradio_app.py --config my_config.json
```

## アプリの使い方

### アイテム詳細タブ

1. **アイテム検索**: 検索ボックスにアイテム名またはアイテムコードを入力
2. **アイテム選択**: ドロップダウンメニューからアイテムを選択
3. **情報表示**: 選択したアイテムの詳細情報が表示されます
   - 基本情報: アイテム名、コード、生産数
   - レシピ情報: 必要な材料とその数量
   - 容量情報: ロケット容量と容積
   - JSONデータ: 生のデータ

### アイテム一覧タブ

- すべてのアイテム情報がテーブル形式で表示されます
- 「🔄 更新」ボタンでデータを再読み込みできます

## データの準備

アプリを使用する前に、以下のスクリプトを実行してJSONデータを準備してください：

### 1. アイテム情報の取得
```bash
python fetch_items_links.py
```

### 2. レシピ情報の取得
```bash
python get_item_recipe.py -i アイテム名
```

### 3. 容量情報の取得
```bash
python get_item_volume.py -i アイテム名
```

例：
```bash
# グレネードの情報を取得
python get_item_recipe.py -i グレネード
python get_item_volume.py -i グレネード
```

## 設定ファイル

デフォルトでは、`factorio_config.json`の設定が使用されます。設定ファイルが存在しない場合は、デフォルト設定が適用されます。

### 設定例
```json
{
    "data_dir": "data",
    "csv_file": "factorio_items.csv",
    "json_dir": "json",
    "language": "ja",
    "game_mode": "SpaceAge",
    "log_level": "INFO"
}
```

## トラブルシューティング

### よくある問題

#### 1. JSONファイルが見つからない
```
JSONディレクトリが見つかりません: data/json
```

**解決方法**: 
- `get_item_recipe.py`と`get_item_volume.py`を実行してJSONファイルを生成してください
- 設定ファイルでJSONディレクトリのパスが正しく設定されているか確認してください

#### 2. アイテムが表示されない
**解決方法**:
- CSVファイル（`factorio_items.csv`）が存在するか確認してください
- `fetch_items_links.py`を実行してアイテム情報を取得してください

#### 3. ポートが使用中
```
OSError: [Errno 48] Address already in use
```

**解決方法**:
- 別のポート番号を指定してください: `--port 8080`
- または、使用中のプロセスを終了してください

### ログの確認

デバッグ情報を確認したい場合は、設定ファイルで`log_level`を`DEBUG`に設定してください：

```json
{
    "log_level": "DEBUG"
}
```

## 開発者向け情報

### ファイル構造
```
src/
├── factorio_gradio_app.py    # メインアプリケーション
├── factorio_config.py        # 設定管理
├── factorio_item.py          # アイテム管理
├── requirements.txt          # 依存関係
└── data/
    ├── factorio_items.csv    # アイテム一覧
    └── json/
        ├── item_グレネード.json
        ├── item_爆薬.json
        └── ...
```

### クラス構造

#### `FactorioItemViewer`
- `load_all_items()`: すべてのJSONファイルを読み込み
- `get_item_info()`: 指定されたアイテムの詳細情報を取得
- `search_items()`: アイテム検索
- `get_items_table()`: テーブル用データを生成

### カスタマイズ

アプリの外観や機能をカスタマイズしたい場合は、`create_gradio_app()`関数を編集してください。

## ライセンス

このプロジェクトは、既存のFactorioアイテム情報取得ツールと同じライセンスに従います。
