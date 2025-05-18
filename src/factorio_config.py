"""
Factorio 設定管理モジュール
=========================

このモジュールは、Factorioアイテム情報取得ツールの設定を管理するためのクラスを提供します。
JSONファイルから設定を読み込み、各プログラムで使用できるようにします。
"""

import os
import json
import logging

# ロギング設定
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

class Config:
    """
    Factorioアイテム情報取得ツールの設定を管理するクラス
    
    このクラスは、JSONファイルから設定を読み込み、各プログラムで使用できるようにします。
    デフォルト設定を提供し、設定値へのアクセスを提供します。
    """
    
    # デフォルト設定
    DEFAULT_CONFIG = {
        # データディレクトリの設定
        "data_dir": "data",
        
        # CSVファイルの設定
        "csv_file": "factorio_items.csv",
        
        # JSONファイルの設定
        "json_dir": "json",
        
        # 言語設定
        "language": "ja",
        
        # ゲームモード設定
        "game_mode": "SpaceAge",
        
        # ログレベル設定
        "log_level": "INFO",
        
        # Wikiの設定
        "wiki_base_url": "https://wiki.factorio.com/",
        "wiki_materials_page": "Materials_and_recipes/ja"
    }
    
    def __init__(self, config_file=None):
        """
        設定を初期化
        
        引数:
            config_file (str): 設定ファイルのパス（デフォルト: None）
        """
        self.config = self.DEFAULT_CONFIG.copy()
        self.config_file = config_file
        
        if config_file:
            self.load_config(config_file)
    
    def load_config(self, config_file):
        """
        設定ファイルから設定を読み込む
        
        引数:
            config_file (str): 設定ファイルのパス
        
        戻り値:
            bool: 読み込みが成功したかどうか
        """
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    
                # ユーザー設定をマージ
                self.config.update(user_config)
                logging.info(f"設定ファイル '{config_file}' を読み込みました。")
                return True
            else:
                logging.warning(f"設定ファイル '{config_file}' が見つかりません。デフォルト設定を使用します。")
                return False
        except Exception as e:
            logging.error(f"設定ファイルの読み込みエラー: {e}")
            logging.debug(f"例外の詳細: {str(e)}", exc_info=True)
            return False
    
    def save_config(self, config_file=None):
        """
        設定をファイルに保存
        
        引数:
            config_file (str): 設定ファイルのパス（デフォルト: 初期化時に指定したファイル）
        
        戻り値:
            bool: 保存が成功したかどうか
        """
        if config_file is None:
            config_file = self.config_file
            
        if config_file is None:
            logging.error("設定ファイルが指定されていません。")
            return False
            
        try:
            # ディレクトリが存在しない場合は作成
            os.makedirs(os.path.dirname(os.path.abspath(config_file)), exist_ok=True)
            
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=4)
                
            logging.info(f"設定を '{config_file}' に保存しました。")
            return True
        except Exception as e:
            logging.error(f"設定ファイルの保存エラー: {e}")
            logging.debug(f"例外の詳細: {str(e)}", exc_info=True)
            return False
    
    def get(self, key, default=None):
        """
        設定値を取得
        
        引数:
            key (str): 設定キー
            default: キーが存在しない場合のデフォルト値
        
        戻り値:
            設定値
        """
        return self.config.get(key, default)
    
    def set(self, key, value):
        """
        設定値を設定
        
        引数:
            key (str): 設定キー
            value: 設定値
        """
        self.config[key] = value
    
    def get_csv_path(self):
        """
        CSVファイルのパスを取得
        
        戻り値:
            str: CSVファイルのパス
        """
        data_dir = self.get('data_dir')
        csv_file = self.get('csv_file')
        
        # data_dirが指定されていない場合は、カレントディレクトリを使用
        if not data_dir:
            return csv_file
            
        # ディレクトリが存在しない場合は作成
        os.makedirs(data_dir, exist_ok=True)
        
        return os.path.join(data_dir, csv_file)
    
    def get_json_path(self, filename):
        """
        JSONファイルのパスを取得
        
        引数:
            filename (str): JSONファイル名
        
        戻り値:
            str: JSONファイルのパス
        """
        data_dir = self.get('data_dir')
        json_dir = self.get('json_dir')
        
        # data_dirとjson_dirが指定されていない場合は、カレントディレクトリを使用
        if not data_dir or not json_dir:
            return filename
            
        # ディレクトリが存在しない場合は作成
        full_path = os.path.join(data_dir, json_dir)
        os.makedirs(full_path, exist_ok=True)
        
        return os.path.join(full_path, filename)
    
    def get_language(self):
        """
        言語設定を取得
        
        戻り値:
            str: 言語コード
        """
        return self.get('language', 'ja')
    
    def get_game_mode(self):
        """
        ゲームモード設定を取得
        
        戻り値:
            str: ゲームモード
        """
        return self.get('game_mode', 'SpaceAge')
    
    def get_log_level(self):
        """
        ログレベル設定を取得
        
        戻り値:
            str: ログレベル
        """
        return self.get('log_level', 'INFO')
    
    def set_log_level(self):
        """
        ログレベルを設定する
        
        設定ファイルから読み込んだログレベルに基づいて、
        loggingモジュールのログレベルを設定します。
        """
        log_level = self.get_log_level()
        if log_level == "DEBUG":
            logging.getLogger().setLevel(logging.DEBUG)
        elif log_level == "INFO":
            logging.getLogger().setLevel(logging.INFO)
        elif log_level == "WARNING":
            logging.getLogger().setLevel(logging.WARNING)
        elif log_level == "ERROR":
            logging.getLogger().setLevel(logging.ERROR)
    
    def get_wiki_base_url(self):
        """
        WikiのベースURLを取得
        
        戻り値:
            str: WikiのベースURL
        """
        return self.get('wiki_base_url', 'https://wiki.factorio.com/')
    
    def get_wiki_materials_page(self):
        """
        Wikiの材料ページを取得
        
        戻り値:
            str: Wikiの材料ページ
        """
        return self.get('wiki_materials_page', 'Materials_and_recipes/ja')
    
    def create_default_config(self, config_file):
        """
        デフォルト設定ファイルを作成
        
        引数:
            config_file (str): 設定ファイルのパス
        
        戻り値:
            bool: 作成が成功したかどうか
        """
        try:
            # ディレクトリが存在しない場合は作成
            os.makedirs(os.path.dirname(os.path.abspath(config_file)), exist_ok=True)
            
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(self.DEFAULT_CONFIG, f, ensure_ascii=False, indent=4)
                
            logging.info(f"デフォルト設定を '{config_file}' に保存しました。")
            return True
        except Exception as e:
            logging.error(f"デフォルト設定ファイルの作成エラー: {e}")
            logging.debug(f"例外の詳細: {str(e)}", exc_info=True)
            return False
    
    def __str__(self):
        """
        設定の文字列表現
        
        戻り値:
            str: 設定の文字列表現
        """
        return json.dumps(self.config, ensure_ascii=False, indent=4)


# 設定ファイルのパスを取得する関数
def get_config_path(config_file=None):
    """
    設定ファイルのパスを取得
    
    引数:
        config_file (str): コマンドラインで指定された設定ファイルのパス
    
    戻り値:
        str: 設定ファイルのパス
    """
    # コマンドラインで指定された設定ファイルがある場合はそれを使用
    if config_file:
        return config_file
        
    # 環境変数で指定された設定ファイルがある場合はそれを使用
    env_config = os.environ.get('FACTORIO_CONFIG')
    if env_config:
        return env_config
        
    # デフォルトの設定ファイルを使用
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_dir, 'factorio_config.json')


# 設定を読み込む関数
def load_config(config_file=None):
    """
    設定を読み込む
    
    引数:
        config_file (str): 設定ファイルのパス
    
    戻り値:
        Config: 設定オブジェクト
    """
    config_path = get_config_path(config_file)
    config = Config(config_path)
    config.set_log_level()
    return config


if __name__ == "__main__":
    # コマンドライン引数の解析
    import argparse
    
    parser = argparse.ArgumentParser(description='Factorio 設定管理ツール')
    parser.add_argument('-c', '--create', action='store_true', help='デフォルト設定ファイルを作成')
    parser.add_argument('-f', '--file', type=str, default=None, help='設定ファイルのパス')
    parser.add_argument('-s', '--show', action='store_true', help='現在の設定を表示')
    args = parser.parse_args()
    
    # デフォルト設定ファイルを作成
    if args.create:
        config_path = get_config_path(args.file)
        config = Config()
        if config.create_default_config(config_path):
            print(f"デフォルト設定ファイルを '{config_path}' に作成しました。")
        else:
            print(f"デフォルト設定ファイルの作成に失敗しました。")
    
    # 現在の設定を表示
    if args.show:
        config = load_config(args.file)
        print(f"設定ファイル: {config.config_file}")
        print(config)
