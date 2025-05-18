"""
factorio_config.py のテスト
========================

このモジュールは、factorio_config.py モジュールの機能をテストします。
"""

import os
import sys
import json
import tempfile
import pytest
from unittest.mock import patch, mock_open

# テスト対象のモジュールのパスを追加
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from factorio_config import Config, load_config, get_config_path


class TestConfig:
    """Configクラスのテスト"""

    @pytest.fixture
    def config_data(self):
        """テスト用の設定データ"""
        return {
            "data_dir": "test_data",
            "csv_file": "test_items.csv",
            "json_dir": "test_json",
            "language": "en",
            "game_mode": "Base",
            "log_level": "DEBUG",
            "wiki_base_url": "https://test.factorio.com/",
            "wiki_materials_page": "Test_materials"
        }

    @pytest.fixture
    def temp_config_file(self, config_data):
        """テスト用の一時設定ファイル"""
        temp_file = tempfile.NamedTemporaryFile(delete=False, mode='w', encoding='utf-8', suffix='.json')
        json.dump(config_data, temp_file)
        temp_file.close()
        
        yield temp_file.name
        
        # テスト後にファイルを削除
        os.unlink(temp_file.name)

    @pytest.fixture
    def config(self):
        """テスト用のConfigインスタンス"""
        return Config()

    @pytest.fixture
    def config_with_file(self, temp_config_file):
        """設定ファイルを使用したConfigインスタンス"""
        return Config(temp_config_file)

    def test_init_default(self, config):
        """デフォルト設定でのinitのテスト"""
        # デフォルト設定が正しく設定されているか確認
        assert config.config == Config.DEFAULT_CONFIG
        assert config.config_file is None

    def test_init_with_file(self, config_with_file, config_data):
        """設定ファイルを使用したinitのテスト"""
        # 設定ファイルの内容が正しく読み込まれているか確認
        for key, value in config_data.items():
            assert config_with_file.config[key] == value

    def test_load_config(self, config, temp_config_file, config_data):
        """load_configメソッドのテスト"""
        # 存在する設定ファイルを読み込む
        result = config.load_config(temp_config_file)
        assert result is True
        
        # 設定が正しく読み込まれているか確認
        for key, value in config_data.items():
            assert config.config[key] == value
        
        # 存在しない設定ファイルを読み込む
        result = config.load_config("non_existent_file.json")
        assert result is False
        
        # 設定ファイルの読み込みに失敗した場合
        with patch('builtins.open', side_effect=Exception("Test exception")):
            result = config.load_config(temp_config_file)
            assert result is False

    def test_save_config(self, config, temp_config_file):
        """save_configメソッドのテスト"""
        # 設定ファイルを指定してsave_configを呼び出す
        result = config.save_config(temp_config_file)
        assert result is True
        
        # 設定ファイルが正しく保存されているか確認
        with open(temp_config_file, 'r', encoding='utf-8') as f:
            saved_config = json.load(f)
            assert saved_config == config.config
        
        # 設定ファイルを指定せずにsave_configを呼び出す（config_fileがNoneの場合）
        config.config_file = None
        result = config.save_config()
        assert result is False
        
        # 設定ファイルの保存に失敗した場合
        with patch('builtins.open', side_effect=Exception("Test exception")):
            result = config.save_config(temp_config_file)
            assert result is False

    def test_get(self, config):
        """getメソッドのテスト"""
        # 存在するキー
        assert config.get('data_dir') == Config.DEFAULT_CONFIG['data_dir']
        
        # 存在しないキー（デフォルト値なし）
        assert config.get('non_existent_key') is None
        
        # 存在しないキー（デフォルト値あり）
        assert config.get('non_existent_key', 'default_value') == 'default_value'

    def test_set(self, config):
        """setメソッドのテスト"""
        # 既存のキーを更新
        config.set('data_dir', 'new_data_dir')
        assert config.config['data_dir'] == 'new_data_dir'
        
        # 新しいキーを追加
        config.set('new_key', 'new_value')
        assert config.config['new_key'] == 'new_value'

    def test_get_csv_path(self, config):
        """get_csv_pathメソッドのテスト"""
        # デフォルト設定
        expected_path = os.path.join(config.get('data_dir'), config.get('csv_file'))
        assert config.get_csv_path() == expected_path
        
        # data_dirが空の場合
        config.set('data_dir', '')
        assert config.get_csv_path() == config.get('csv_file')

    def test_get_json_path(self, config):
        """get_json_pathメソッドのテスト"""
        # デフォルト設定
        filename = 'test.json'
        expected_path = os.path.join(config.get('data_dir'), config.get('json_dir'), filename)
        assert config.get_json_path(filename) == expected_path
        
        # data_dirとjson_dirが空の場合
        config.set('data_dir', '')
        config.set('json_dir', '')
        assert config.get_json_path(filename) == filename

    def test_get_language(self, config):
        """get_languageメソッドのテスト"""
        # デフォルト設定
        assert config.get_language() == config.get('language')
        
        # 設定を変更した場合
        config.set('language', 'en')
        assert config.get_language() == 'en'

    def test_get_game_mode(self, config):
        """get_game_modeメソッドのテスト"""
        # デフォルト設定
        assert config.get_game_mode() == config.get('game_mode')
        
        # 設定を変更した場合
        config.set('game_mode', 'Base')
        assert config.get_game_mode() == 'Base'

    def test_get_log_level(self, config):
        """get_log_levelメソッドのテスト"""
        # デフォルト設定
        assert config.get_log_level() == config.get('log_level')
        
        # 設定を変更した場合
        config.set('log_level', 'DEBUG')
        assert config.get_log_level() == 'DEBUG'

    @patch('logging.getLogger')
    def test_set_log_level(self, mock_get_logger, config):
        """set_log_levelメソッドのテスト"""
        mock_logger = mock_get_logger.return_value
        
        # DEBUGレベル
        config.set('log_level', 'DEBUG')
        config.set_log_level()
        mock_logger.setLevel.assert_called_once()
        
        # INFOレベル
        mock_logger.reset_mock()
        config.set('log_level', 'INFO')
        config.set_log_level()
        mock_logger.setLevel.assert_called_once()
        
        # WARNINGレベル
        mock_logger.reset_mock()
        config.set('log_level', 'WARNING')
        config.set_log_level()
        mock_logger.setLevel.assert_called_once()
        
        # ERRORレベル
        mock_logger.reset_mock()
        config.set('log_level', 'ERROR')
        config.set_log_level()
        mock_logger.setLevel.assert_called_once()

    def test_get_wiki_base_url(self, config):
        """get_wiki_base_urlメソッドのテスト"""
        # デフォルト設定
        assert config.get_wiki_base_url() == config.get('wiki_base_url')
        
        # 設定を変更した場合
        config.set('wiki_base_url', 'https://test.factorio.com/')
        assert config.get_wiki_base_url() == 'https://test.factorio.com/'

    def test_get_wiki_materials_page(self, config):
        """get_wiki_materials_pageメソッドのテスト"""
        # デフォルト設定
        assert config.get_wiki_materials_page() == config.get('wiki_materials_page')
        
        # 設定を変更した場合
        config.set('wiki_materials_page', 'Test_materials')
        assert config.get_wiki_materials_page() == 'Test_materials'

    def test_create_default_config(self, config):
        """create_default_configメソッドのテスト"""
        # 一時ファイルを作成
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file_path = temp_file.name
        
        try:
            # デフォルト設定ファイルを作成
            result = config.create_default_config(temp_file_path)
            assert result is True
            
            # ファイルが正しく作成されているか確認
            with open(temp_file_path, 'r', encoding='utf-8') as f:
                saved_config = json.load(f)
                assert saved_config == Config.DEFAULT_CONFIG
            
            # ファイルの作成に失敗した場合
            with patch('builtins.open', side_effect=Exception("Test exception")):
                result = config.create_default_config(temp_file_path)
                assert result is False
        finally:
            # テスト後にファイルを削除
            os.unlink(temp_file_path)

    def test_str_representation(self, config):
        """__str__メソッドのテスト"""
        # 設定の文字列表現
        expected = json.dumps(config.config, ensure_ascii=False, indent=4)
        assert str(config) == expected


class TestHelperFunctions:
    """ヘルパー関数のテスト"""

    @patch('os.environ.get')
    def test_get_config_path(self, mock_environ_get):
        """get_config_path関数のテスト"""
        # コマンドラインで指定された設定ファイル
        config_file = 'command_line_config.json'
        assert get_config_path(config_file) == config_file
        
        # 環境変数で指定された設定ファイル
        mock_environ_get.return_value = 'env_config.json'
        assert get_config_path() == 'env_config.json'
        
        # デフォルトの設定ファイル
        mock_environ_get.return_value = None
        with patch('os.path.dirname', return_value='/path/to/script'):
            assert get_config_path() == '/path/to/script/factorio_config.json'

    @patch('factorio_config.get_config_path')
    def test_load_config_function(self, mock_get_config_path, temp_config_file, config_data):
        """load_config関数のテスト"""
        # 設定ファイルを指定した場合
        config = load_config(temp_config_file)
        assert isinstance(config, Config)
        
        # 設定ファイルを指定しない場合
        mock_get_config_path.return_value = temp_config_file
        config = load_config()
        assert isinstance(config, Config)
        
        # 設定が正しく読み込まれているか確認
        for key, value in config_data.items():
            assert config.config[key] == value
