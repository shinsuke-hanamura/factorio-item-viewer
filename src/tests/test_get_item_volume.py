"""
get_item_volume.py のテスト
========================

このモジュールは、get_item_volume.py モジュールの機能をテストします。
"""

import os
import sys
import tempfile
import pytest
from unittest.mock import patch, MagicMock

# テスト対象のモジュールのパスを追加
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from get_item_volume import get_item_rocket_capacity, calculate_item_volume
from factorio_config import Config


class TestGetItemVolume:
    """get_item_volume.pyのテスト"""

    @pytest.fixture
    def mock_html_content_with_capacity(self):
        """ロケット容量があるHTML内容"""
        return """
        <html>
            <body>
                <table>
                    <tr>
                        <td>ロケット容量</td>
                        <td>100</td>
                    </tr>
                </table>
            </body>
        </html>
        """

    @pytest.fixture
    def mock_html_content_no_capacity(self):
        """ロケット容量がないHTML内容"""
        return """
        <html>
            <body>
                <table>
                    <tr>
                        <td>情報</td>
                        <td>値</td>
                    </tr>
                </table>
            </body>
        </html>
        """

    @pytest.fixture
    def mock_html_content_with_capacity_in_row(self):
        """行にロケット容量があるHTML内容"""
        return """
        <html>
            <body>
                <table>
                    <tr>
                        ロケット容量 100
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
        temp_file.close()
        
        yield temp_file.name
        
        # テスト後にファイルを削除
        os.unlink(temp_file.name)

    @pytest.fixture
    def config(self):
        """テスト用の設定"""
        config = Config()
        return config

    @patch('requests.get')
    def test_get_item_rocket_capacity(self, mock_get, mock_html_content_with_capacity):
        """get_item_rocket_capacity関数のテスト"""
        # モックの設定
        mock_response = MagicMock()
        mock_response.text = mock_html_content_with_capacity
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        # 関数を実行
        capacity = get_item_rocket_capacity('https://wiki.factorio.com/Iron_plate/ja')
        
        # 結果を検証
        assert capacity == 100

    @patch('requests.get')
    def test_get_item_rocket_capacity_no_capacity(self, mock_get, mock_html_content_no_capacity):
        """ロケット容量がない場合のget_item_rocket_capacity関数のテスト"""
        # モックの設定
        mock_response = MagicMock()
        mock_response.text = mock_html_content_no_capacity
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        # 関数を実行
        capacity = get_item_rocket_capacity('https://wiki.factorio.com/Iron_plate/ja')
        
        # 結果を検証
        assert capacity is None

    @patch('requests.get')
    def test_get_item_rocket_capacity_in_row(self, mock_get, mock_html_content_with_capacity_in_row):
        """行にロケット容量がある場合のget_item_rocket_capacity関数のテスト"""
        # モックの設定
        mock_response = MagicMock()
        mock_response.text = mock_html_content_with_capacity_in_row
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        # 関数を実行
        capacity = get_item_rocket_capacity('https://wiki.factorio.com/Iron_plate/ja')
        
        # 結果を検証
        assert capacity == 100

    @patch('requests.get')
    def test_get_item_rocket_capacity_request_error(self, mock_get):
        """リクエストエラー時のget_item_rocket_capacity関数のテスト"""
        # モックの設定
        mock_get.side_effect = Exception("Test exception")
        
        # 関数を実行
        capacity = get_item_rocket_capacity('https://wiki.factorio.com/Iron_plate/ja')
        
        # 結果を検証
        assert capacity is None

    def test_calculate_item_volume(self):
        """calculate_item_volume関数のテスト"""
        # 正常なロケット容量
        volume = calculate_item_volume(100)
        assert volume == 10.0  # 1000 / 100
        
        # ロケット容量がNoneの場合
        volume = calculate_item_volume(None)
        assert volume is None
        
        # ロケット容量が0の場合
        volume = calculate_item_volume(0)
        assert volume is None
