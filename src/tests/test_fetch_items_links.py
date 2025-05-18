"""
fetch_items_links.py のテスト
==========================

このモジュールは、fetch_items_links.py モジュールの機能をテストします。
"""

import os
import sys
import csv
import tempfile
import pytest
from unittest.mock import patch, MagicMock

# テスト対象のモジュールのパスを追加
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fetch_items_links import fetch_items_from_materials_page, load_item_url
from factorio_config import Config


class TestFetchItemsLinks:
    """fetch_items_links.pyのテスト"""

    @pytest.fixture
    def mock_html_content(self):
        """モック用のHTML内容"""
        return """
        <html>
            <body>
                <div class="factorio-icon">
                    <a href="/Iron_plate/ja" title="鉄板">鉄板</a>
                </div>
                <div class="factorio-icon">
                    <a href="/Copper_plate/ja" title="銅板">銅板</a>
                </div>
                <div class="factorio-icon">
                    <a href="/Electronic_circuit/ja" title="電子回路">電子回路</a>
                </div>
                <div class="factorio-icon">
                    <a href="/invalid_url" title="無効なURL">無効なURL</a>
                </div>
                <div class="factorio-icon">
                    <span>リンクなし</span>
                </div>
            </body>
        </html>
        """

    @pytest.fixture
    def config(self):
        """テスト用の設定"""
        config = Config()
        config.set('wiki_base_url', 'https://wiki.factorio.com/')
        config.set('wiki_materials_page', 'Materials_and_recipes/ja')
        return config

    @pytest.fixture
    def temp_csv_file(self):
        """テスト用の一時CSVファイル"""
        temp_file = tempfile.NamedTemporaryFile(delete=False, mode='w', encoding='utf-8', suffix='.csv')
        fieldnames = ['日本語アイテム名', 'アイテムコード', 'URL']
        writer = csv.DictWriter(temp_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow({
            '日本語アイテム名': '鉄板',
            'アイテムコード': 'Iron_plate',
            'URL': 'https://wiki.factorio.com/Iron_plate/ja'
        })
        writer.writerow({
            '日本語アイテム名': '銅板',
            'アイテムコード': 'Copper_plate',
            'URL': 'https://wiki.factorio.com/Copper_plate/ja'
        })
        temp_file.close()
        
        yield temp_file.name
        
        # テスト後にファイルを削除
        os.unlink(temp_file.name)

    @patch('requests.get')
    def test_fetch_items_from_materials_page(self, mock_get, mock_html_content, config):
        """fetch_items_from_materials_pageのテスト"""
        # モックの設定
        mock_response = MagicMock()
        mock_response.text = mock_html_content
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        # 一時ファイルを作成
        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as temp_file:
            temp_csv_path = temp_file.name
        
        try:
            # 設定にCSVパスを設定
            config.set('csv_file', os.path.basename(temp_csv_path))
            config.set('data_dir', os.path.dirname(temp_csv_path))
            
            # 関数を実行
            result = fetch_items_from_materials_page(config)
            
            # 結果を検証
            assert result is True
            
            # CSVファイルが作成されたか確認
            assert os.path.exists(temp_csv_path)
            
            # CSVファイルの内容を確認
            with open(temp_csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                
                # 有効なアイテムが3つ抽出されているか確認
                assert len(rows) == 3
                
                # 各アイテムの内容を確認
                assert rows[0]['日本語アイテム名'] == '鉄板'
                assert rows[0]['アイテムコード'] == 'Iron_plate'
                assert rows[0]['URL'] == 'https://wiki.factorio.com/Iron_plate/ja'
                
                assert rows[1]['日本語アイテム名'] == '銅板'
                assert rows[1]['アイテムコード'] == 'Copper_plate'
                assert rows[1]['URL'] == 'https://wiki.factorio.com/Copper_plate/ja'
                
                assert rows[2]['日本語アイテム名'] == '電子回路'
                assert rows[2]['アイテムコード'] == 'Electronic_circuit'
                assert rows[2]['URL'] == 'https://wiki.factorio.com/Electronic_circuit/ja'
        finally:
            # テスト後にファイルを削除
            if os.path.exists(temp_csv_path):
                os.unlink(temp_csv_path)

    @patch('requests.get')
    def test_fetch_items_from_materials_page_request_error(self, mock_get, config):
        """fetch_items_from_materials_page のリクエストエラーのテスト"""
        # モックの設定
        mock_get.side_effect = Exception("Test exception")
        
        # 関数を実行
        result = fetch_items_from_materials_page(config)
        
        # 結果を検証
        assert result is False

    def test_load_item_url(self, temp_csv_file):
        """load_item_url関数のテスト"""
        # 存在するアイテム
        url = load_item_url('鉄板', temp_csv_file)
        assert url == 'https://wiki.factorio.com/Iron_plate/ja'
        
        # 存在しないアイテム
        url = load_item_url('存在しないアイテム', temp_csv_file)
        assert url is None
        
        # 言語を指定した場合
        url = load_item_url('鉄板', temp_csv_file, 'en')
        assert url == 'https://wiki.factorio.com/Iron_plate/ja'
