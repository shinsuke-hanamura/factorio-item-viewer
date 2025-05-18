"""
factorio_item.py のテスト
=======================

このモジュールは、factorio_item.py モジュールの機能をテストします。
"""

import os
import sys
import csv
import tempfile
import pytest
from unittest.mock import patch, mock_open

# テスト対象のモジュールのパスを追加
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from factorio_item import Item, ItemManager


class TestItem:
    """Itemクラスのテスト"""

    @pytest.fixture
    def item_data(self):
        """テスト用のアイテムデータ"""
        return {
            '日本語アイテム名': '鉄板',
            'アイテムコード': 'Iron_plate',
            'URL': 'https://wiki.factorio.com/Iron_plate/ja'
        }

    @pytest.fixture
    def item(self, item_data):
        """テスト用のItemインスタンス"""
        return Item(item_data)

    def test_name_property(self, item):
        """nameプロパティのテスト"""
        # デフォルト言語（日本語）での名前
        assert item.name == '鉄板'
        
        # 英語に設定した場合
        item.set_language('en')
        assert item.name == 'Iron_plate'
        
        # サポートされていない言語の場合はアイテムコードを返す
        item.set_language('fr')
        assert item.name == 'Iron_plate'

    def test_code_property(self, item):
        """codeプロパティのテスト"""
        assert item.code == 'Iron_plate'

    def test_url_property(self, item):
        """urlプロパティのテスト"""
        assert item.url == 'https://wiki.factorio.com/Iron_plate/ja'

    def test_set_language(self, item):
        """set_languageメソッドのテスト"""
        # 有効な言語設定
        result = item.set_language('en')
        assert item.language == 'en'
        assert result == item  # メソッドチェーン用に自身を返す
        
        # 無効な言語設定
        result = item.set_language('invalid')
        assert item.language == Item.DEFAULT_LANGUAGE  # デフォルト言語に戻る
        assert result == item  # メソッドチェーン用に自身を返す

    def test_str_representation(self, item):
        """__str__メソッドのテスト"""
        assert str(item) == '鉄板'
        
        # 言語を変更した場合
        item.set_language('en')
        assert str(item) == 'Iron_plate'

    def test_to_dict(self, item):
        """to_dictメソッドのテスト"""
        expected = {
            'name': '鉄板',
            'code': 'Iron_plate',
            'url': 'https://wiki.factorio.com/Iron_plate/ja',
            'language': 'ja'
        }
        assert item.to_dict() == expected
        
        # 言語を変更した場合
        item.set_language('en')
        expected['name'] = 'Iron_plate'
        expected['language'] = 'en'
        assert item.to_dict() == expected


class TestItemManager:
    """ItemManagerクラスのテスト"""

    @pytest.fixture
    def csv_data(self):
        """テスト用のCSVデータ"""
        return [
            {'日本語アイテム名': '鉄板', 'アイテムコード': 'Iron_plate', 'URL': 'https://wiki.factorio.com/Iron_plate/ja'},
            {'日本語アイテム名': '銅板', 'アイテムコード': 'Copper_plate', 'URL': 'https://wiki.factorio.com/Copper_plate/ja'},
            {'日本語アイテム名': '電子回路', 'アイテムコード': 'Electronic_circuit', 'URL': 'https://wiki.factorio.com/Electronic_circuit/ja'}
        ]

    @pytest.fixture
    def temp_csv_file(self, csv_data):
        """テスト用の一時CSVファイル"""
        temp_file = tempfile.NamedTemporaryFile(delete=False, mode='w', encoding='utf-8', suffix='.csv')
        fieldnames = ['日本語アイテム名', 'アイテムコード', 'URL']
        writer = csv.DictWriter(temp_file, fieldnames=fieldnames)
        writer.writeheader()
        for row in csv_data:
            writer.writerow(row)
        temp_file.close()
        
        yield temp_file.name
        
        # テスト後にファイルを削除
        os.unlink(temp_file.name)

    @pytest.fixture
    def manager(self, temp_csv_file):
        """テスト用のItemManagerインスタンス"""
        return ItemManager(temp_csv_file)

    def test_load_items(self, manager):
        """load_itemsメソッドのテスト"""
        # 初期化時に既にload_itemsが呼ばれているので、アイテム数をチェック
        assert len(manager.items) == 3
        
        # 各アイテムが正しく読み込まれているか確認
        assert manager.items[0].name == '鉄板'
        assert manager.items[1].name == '銅板'
        assert manager.items[2].name == '電子回路'

    def test_find_item_by_name(self, manager):
        """find_item_by_nameメソッドのテスト"""
        # 存在するアイテム
        item = manager.find_item_by_name('鉄板')
        assert item is not None
        assert item.code == 'Iron_plate'
        
        # 存在しないアイテム
        item = manager.find_item_by_name('存在しないアイテム')
        assert item is None

    def test_find_item_by_code(self, manager):
        """find_item_by_codeメソッドのテスト"""
        # 存在するアイテム
        item = manager.find_item_by_code('Iron_plate')
        assert item is not None
        assert item.name == '鉄板'
        
        # 存在しないアイテム
        item = manager.find_item_by_code('Non_existent')
        assert item is None

    def test_get_item_url(self, manager):
        """get_item_urlメソッドのテスト"""
        # 存在するアイテム
        url = manager.get_item_url('鉄板')
        assert url == 'https://wiki.factorio.com/Iron_plate/ja'
        
        # 存在しないアイテム
        url = manager.get_item_url('存在しないアイテム')
        assert url is None

    def test_get_item_code(self, manager):
        """get_item_codeメソッドのテスト"""
        # 存在するアイテム
        code = manager.get_item_code('鉄板')
        assert code == 'Iron_plate'
        
        # 存在しないアイテム
        code = manager.get_item_code('存在しないアイテム')
        assert code is None

    def test_set_language(self, manager):
        """set_languageメソッドのテスト"""
        # 言語を英語に設定
        result = manager.set_language('en')
        assert manager.language == 'en'
        assert result == manager  # メソッドチェーン用に自身を返す
        
        # すべてのアイテムの言語が変更されているか確認
        for item in manager.items:
            assert item.language == 'en'

    @patch('builtins.open', new_callable=mock_open)
    @patch('csv.DictReader')
    @patch('csv.DictWriter')
    def test_add_item(self, mock_writer, mock_reader, mock_open):
        """add_itemメソッドのテスト"""
        # モックの設定
        mock_reader.return_value = [
            {'日本語アイテム名': '鉄板', 'アイテムコード': 'Iron_plate', 'URL': 'https://wiki.factorio.com/Iron_plate/ja'}
        ]
        
        manager = ItemManager()
        
        # 新しいアイテムを追加
        result = manager.add_item('崖用発破', 'Cliff_explosives', 'https://wiki.factorio.com/Cliff_explosives/ja')
        assert result is True
        
        # 既存のアイテムを追加しようとした場合
        mock_reader.return_value = [
            {'日本語アイテム名': '鉄板', 'アイテムコード': 'Iron_plate', 'URL': 'https://wiki.factorio.com/Iron_plate/ja'},
            {'日本語アイテム名': '崖用発破', 'アイテムコード': 'Cliff_explosives', 'URL': 'https://wiki.factorio.com/Cliff_explosives/ja'}
        ]
        result = manager.add_item('鉄板', 'Iron_plate', 'https://wiki.factorio.com/Iron_plate/ja')
        assert result is False


class TestLegacyFunctions:
    """後方互換性のための関数のテスト"""

    @pytest.fixture
    def csv_data(self):
        """テスト用のCSVデータ"""
        return [
            {'日本語アイテム名': '鉄板', 'アイテムコード': 'Iron_plate', 'URL': 'https://wiki.factorio.com/Iron_plate/ja'},
            {'日本語アイテム名': '銅板', 'アイテムコード': 'Copper_plate', 'URL': 'https://wiki.factorio.com/Copper_plate/ja'}
        ]

    @pytest.fixture
    def temp_csv_file(self, csv_data):
        """テスト用の一時CSVファイル"""
        temp_file = tempfile.NamedTemporaryFile(delete=False, mode='w', encoding='utf-8', suffix='.csv')
        fieldnames = ['日本語アイテム名', 'アイテムコード', 'URL']
        writer = csv.DictWriter(temp_file, fieldnames=fieldnames)
        writer.writeheader()
        for row in csv_data:
            writer.writerow(row)
        temp_file.close()
        
        yield temp_file.name
        
        # テスト後にファイルを削除
        os.unlink(temp_file.name)

    def test_load_item_url(self, temp_csv_file):
        """load_item_url関数のテスト"""
        from factorio_item import load_item_url
        
        # 存在するアイテム
        url = load_item_url('鉄板', temp_csv_file)
        assert url == 'https://wiki.factorio.com/Iron_plate/ja'
        
        # 存在しないアイテム
        url = load_item_url('存在しないアイテム', temp_csv_file)
        assert url is None
        
        # 言語を指定した場合
        url = load_item_url('鉄板', temp_csv_file, 'en')
        assert url == 'https://wiki.factorio.com/Iron_plate/ja'
