# Factorio Item Viewer テスト

このディレクトリには、Factorio Item Viewerの各モジュールに対するテストが含まれています。テストはpytestフレームワークを使用して実装されています。

## テストの構成

テストは以下のファイルで構成されています：

1. `__init__.py` - テストパッケージの初期化ファイル
2. `test_factorio_item.py` - factorio_item.pyのテスト
3. `test_factorio_config.py` - factorio_config.pyのテスト
4. `test_fetch_items_links.py` - fetch_items_links.pyのテスト
5. `test_get_item_recipe.py` - get_item_recipe.pyのテスト
6. `test_get_item_volume.py` - get_item_volume.pyのテスト

## 前提条件

テストを実行するには、以下のパッケージが必要です：

```
pytest
requests
beautifulsoup4
```

以下のコマンドでインストールできます：

```bash
pip install pytest requests beautifulsoup4
```

## テストの実行方法

### すべてのテストを実行

すべてのテストを実行するには、以下のコマンドを使用します：

```bash
# プロジェクトのルートディレクトリから
pytest -v src/tests/

# または、testsディレクトリ内から
cd src/tests/
pytest -v
```

### 特定のテストファイルを実行

特定のテストファイルのみを実行するには、以下のコマンドを使用します：

```bash
# 例: factorio_item.pyのテストのみを実行
pytest -v src/tests/test_factorio_item.py
```

### 特定のテスト関数を実行

特定のテスト関数のみを実行するには、以下のコマンドを使用します：

```bash
# 例: factorio_item.pyのTestItemクラスのtest_name_property関数のみを実行
pytest -v src/tests/test_factorio_item.py::TestItem::test_name_property
```

### キーワードでテストを実行

特定のキーワードを含むテストのみを実行するには、以下のコマンドを使用します：

```bash
# 例: "language"を含むテストのみを実行
pytest -v -k "language"
```

## テストの詳細

### test_factorio_item.py

このファイルでは、`factorio_item.py`モジュールの以下の機能をテストしています：

- `Item`クラス
  - `name`プロパティ
  - `code`プロパティ
  - `url`プロパティ
  - `set_language`メソッド
  - `__str__`メソッド
  - `to_dict`メソッド

- `ItemManager`クラス
  - `load_items`メソッド
  - `find_item_by_name`メソッド
  - `find_item_by_code`メソッド
  - `get_item_url`メソッド
  - `get_item_code`メソッド
  - `set_language`メソッド
  - `add_item`メソッド

- 後方互換性のための関数
  - `load_item_url`関数

### test_factorio_config.py

このファイルでは、`factorio_config.py`モジュールの以下の機能をテストしています：

- `Config`クラス
  - 初期化（デフォルト設定と設定ファイルを使用した場合）
  - `load_config`メソッド
  - `save_config`メソッド
  - `get`メソッド
  - `set`メソッド
  - `get_csv_path`メソッド
  - `get_json_path`メソッド
  - `get_language`メソッド
  - `get_game_mode`メソッド
  - `get_log_level`メソッド
  - `set_log_level`メソッド
  - `get_wiki_base_url`メソッド
  - `get_wiki_materials_page`メソッド
  - `create_default_config`メソッド
  - `__str__`メソッド

- ヘルパー関数
  - `get_config_path`関数
  - `load_config`関数

### test_fetch_items_links.py

このファイルでは、`fetch_items_links.py`モジュールの以下の機能をテストしています：

- `fetch_items_from_materials_page`関数
  - 正常系
  - リクエストエラー時

- `load_item_url`関数
  - 存在するアイテム
  - 存在しないアイテム
  - 言語指定時

### test_get_item_recipe.py

このファイルでは、`get_item_recipe.py`モジュールの以下の機能をテストしています：

- `get_recipe`関数
  - 正常系
  - レシピがない場合
  - リクエストエラー時

- `get_item_code_from_name`関数
  - 存在するアイテム
  - 存在しないアイテム
  - 言語指定時

- `create_recipe_json`関数
  - 材料と生成物がある場合
  - 材料があり生成物がない場合
  - 数値に変換できない数量の場合

### test_get_item_volume.py

このファイルでは、`get_item_volume.py`モジュールの以下の機能をテストしています：

- `get_item_rocket_capacity`関数
  - 正常系
  - ロケット容量がない場合
  - 行にロケット容量がある場合
  - リクエストエラー時

- `calculate_item_volume`関数
  - 正常なロケット容量
  - ロケット容量がNoneの場合
  - ロケット容量が0の場合

## テスト実装のポイント

### fixtureの活用

pytestのfixtureを活用して、テストデータやモックオブジェクトを提供しています。fixtureを使用することで、テストコードの重複を減らし、テストの可読性を向上させています。

```python
@pytest.fixture
def item_data(self):
    """テスト用のアイテムデータ"""
    return {
        '日本語アイテム名': '鉄板',
        'アイテムコード': 'Iron_plate',
        'URL': 'https://wiki.factorio.com/Iron_plate/ja'
    }
```

### モックの使用

外部依存関係（HTTPリクエストなど）をテストするために、`unittest.mock`モジュールを使用しています。これにより、実際のHTTPリクエストを行わずにテストを実行できます。

```python
@patch('requests.get')
def test_get_recipe(self, mock_get, mock_html_content):
    # モックの設定
    mock_response = MagicMock()
    mock_response.text = mock_html_content
    mock_response.raise_for_status = MagicMock()
    mock_get.return_value = mock_response
    
    # 関数を実行
    materials, product = get_recipe('https://wiki.factorio.com/Iron_plate/ja')
    
    # 結果を検証
    assert len(materials) == 1
    assert materials[0][0] == 'Iron_ore'  # アイテムコード
    assert materials[0][1] == '1'  # 数量
```

### 一時ファイルの使用

ファイル操作をテストするために、`tempfile`モジュールを使用して一時ファイルを作成しています。テスト終了後に自動的に削除されるため、テスト環境を汚さずに済みます。

```python
@pytest.fixture
def temp_csv_file(self):
    """テスト用の一時CSVファイル"""
    temp_file = tempfile.NamedTemporaryFile(delete=False, mode='w', encoding='utf-8', suffix='.csv')
    # ファイルの内容を書き込む
    temp_file.close()
    
    yield temp_file.name
    
    # テスト後にファイルを削除
    os.unlink(temp_file.name)
```

### 正常系と異常系のテスト

各関数の正常系（正常に動作する場合）と異常系（エラーが発生する場合）の両方をテストしています。これにより、関数の堅牢性を確保しています。

```python
# 正常系のテスト
def test_get_item_rocket_capacity(self, mock_get, mock_html_content_with_capacity):
    # ...

# 異常系のテスト
def test_get_item_rocket_capacity_request_error(self, mock_get):
    # ...
```

## トラブルシューティング

### テストが失敗する場合

テストが失敗する場合は、以下の点を確認してください：

1. 必要なパッケージがインストールされているか
2. テスト対象のモジュールが正しく実装されているか
3. テストコードが最新の実装に対応しているか

詳細なエラーメッセージを確認するには、`-v`オプションを使用してください：

```bash
pytest -v src/tests/
```

### カバレッジレポートの生成

テストのカバレッジレポートを生成するには、`pytest-cov`パッケージをインストールし、以下のコマンドを実行します：

```bash
pip install pytest-cov
pytest --cov=src src/tests/
```

HTML形式のレポートを生成するには：

```bash
pytest --cov=src --cov-report=html src/tests/
```

これにより、`htmlcov`ディレクトリにレポートが生成されます。
