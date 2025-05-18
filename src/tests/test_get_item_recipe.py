"""
get_item_recipe.py のテスト
========================

このモジュールは、get_item_recipe.py モジュールの機能をテストします。
"""

import os
import sys
import json
import tempfile
import pytest
from unittest.mock import patch, MagicMock

# テスト対象のモジュールのパスを追加
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from get_item_recipe import get_recipe, get_item_code_from_name, create_recipe_json
from factorio_config import Config


class TestGetItemRecipe:
    """get_item_recipe.pyのテスト"""

    @pytest.fixture
    def mock_html_content(self):
        """モック用のHTML内容"""
        return """
        <html>
            <body>
                <table>
                    <tr>
                        <p>レシピ</p>
                    </tr>
                    <tr>
                        <div class="factorio-icon">
                            <a href="/Iron_ore/ja" title="鉄鉱石">鉄鉱石</a>
                            <div class="factorio-icon-text">1</div>
                        </div>
                        &#8594;
                        <div class="factorio-icon">
                            <a href="/Iron_plate/ja" title="鉄板">鉄板</a>
                            <div class="factorio-icon-text">1</div>
                        </div>
                    </tr>
                    <tr>
                        <p>トータルコスト</p>
                    </tr>
                </table>
            </body>
        </html>
        """

    @pytest.fixture
    def mock_html_content_no_recipe(self):
        """レシピがないHTML内容"""
        return """
        <html>
            <body>
                <table>
                    <tr>
                        <p>情報</p>
                    </tr>
                </table>
            </body>
        </html>
        """

    @pytest.fixture
    def temp_csv_file(self):
        """テスト用の一時CSVファイル"""
        temp_file = tempfile.NamedTemporaryFile(delete=False, mode='w', encoding='utf-8', suffix='.csv')
        fieldnames = ['日本語アイテム名', 'アイテムコード', 'URL']
        import csv
        writer = csv.DictWriter(temp_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow({
            '日本語アイテム名': '鉄板',
            'アイテムコード': 'Iron_plate',
            'URL': 'https://wiki.factorio.com/Iron_plate/ja'
        })
        writer.writerow({
            '日本語アイテム名': '鉄鉱石',
            'アイテムコード': 'Iron_ore',
            'URL': 'https://wiki.factorio.com/Iron_ore/ja'
        })
        temp_file.close()
        
        yield temp_file.name
        
        # テスト後にファイルを削除
        os.unlink(temp_file.name)

    @pytest.fixture
    def config(self):
        """テスト用の設定"""
        config = Config()
        config.set('game_mode', 'SpaceAge')
        return config

    @patch('requests.get')
    def test_get_recipe(self, mock_get, mock_html_content):
        """get_recipe関数のテスト"""
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
        
        assert product is not None
        assert product[0] == 'Iron_plate'  # アイテムコード
        assert product[1] == '1'  # 数量

    @patch('requests.get')
    def test_get_recipe_no_recipe(self, mock_get, mock_html_content_no_recipe):
        """レシピがない場合のget_recipe関数のテスト"""
        # モックの設定
        mock_response = MagicMock()
        mock_response.text = mock_html_content_no_recipe
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        # 関数を実行
        materials, product = get_recipe('https://wiki.factorio.com/Iron_plate/ja')
        
        # 結果を検証
        assert len(materials) == 0
        assert product is None

    @patch('requests.get')
    def test_get_recipe_request_error(self, mock_get):
        """リクエストエラー時のget_recipe関数のテスト"""
        # モックの設定
        mock_get.side_effect = Exception("Test exception")
        
        # 関数を実行
        materials, product = get_recipe('https://wiki.factorio.com/Iron_plate/ja')
        
        # 結果を検証
        assert len(materials) == 0
        assert product is None

    def test_get_item_code_from_name(self, temp_csv_file):
        """get_item_code_from_name関数のテスト"""
        # 存在するアイテム
        code = get_item_code_from_name('鉄板', temp_csv_file)
        assert code == 'Iron_plate'
        
        # 存在しないアイテム
        code = get_item_code_from_name('存在しないアイテム', temp_csv_file)
        assert code is None
        
        # 言語を指定した場合
        code = get_item_code_from_name('鉄板', temp_csv_file, 'en')
        assert code == 'Iron_plate'

    def test_create_recipe_json(self, temp_csv_file):
        """create_recipe_json関数のテスト"""
        # 材料と生成物がある場合
        materials = [('Iron_ore', '1')]
        product = ('Iron_plate', '1')
        
        recipe_json = create_recipe_json('鉄板', materials, product, temp_csv_file)
        
        # 結果を検証
        assert recipe_json['item_code'] == 'Iron_plate'
        assert len(recipe_json['recipe']) == 1
        assert recipe_json['recipe'][0]['item_code'] == 'Iron_ore'
        assert recipe_json['recipe'][0]['consumption_number'] == 1
        assert recipe_json['production_number'] == 1
        
        # 材料があり、生成物がない場合
        recipe_json = create_recipe_json('鉄板', materials, None, temp_csv_file)
        
        # 結果を検証
        assert recipe_json['item_code'] == 'Iron_plate'
        assert len(recipe_json['recipe']) == 1
        assert recipe_json['recipe'][0]['item_code'] == 'Iron_ore'
        assert recipe_json['recipe'][0]['consumption_number'] == 1
        assert recipe_json['production_number'] == 0
        
        # 数値に変換できない数量の場合
        materials = [('Iron_ore', 'invalid')]
        product = ('Iron_plate', 'invalid')
        
        recipe_json = create_recipe_json('鉄板', materials, product, temp_csv_file)
        
        # 結果を検証
        assert recipe_json['recipe'][0]['consumption_number'] == 1  # デフォルト値
        assert recipe_json['production_number'] == 1  # デフォルト値
