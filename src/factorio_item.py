"""
Factorio アイテムクラス
======================

このモジュールは、Factorioのアイテム情報を扱うための共通クラスを提供します。
言語設定によってアイテム名を取得できるようにします。
"""

import csv
import os
import logging

# ロギング設定
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

class Item:
    """
    Factorioのアイテム情報を扱うクラス
    
    このクラスは、アイテムの名前、コード、URLなどの情報を管理し、
    言語設定に応じたアイテム名を提供します。
    """
    
    # 言語コードとCSVフィールド名のマッピング
    LANGUAGE_FIELDS = {
        'ja': '日本語アイテム名',
        'en': 'アイテムコード'  # 英語名はアイテムコードと同じと仮定
    }
    
    # デフォルト言語
    DEFAULT_LANGUAGE = 'ja'
    
    def __init__(self, item_data, language=None):
        """
        アイテムオブジェクトを初期化
        
        引数:
            item_data (dict): CSVから読み込んだアイテム情報の辞書
            language (str): 使用する言語コード（デフォルト: クラスのデフォルト言語）
        """
        self.data = item_data
        self.language = language or self.DEFAULT_LANGUAGE
    
    @property
    def name(self):
        """
        現在の言語設定に基づいたアイテム名を取得
        
        戻り値:
            str: アイテム名
        """
        field_name = self.LANGUAGE_FIELDS.get(self.language)
        
        # 言語フィールドが存在し、データがある場合はそれを返す
        if field_name and field_name in self.data and self.data[field_name]:
            return self.data[field_name]
        
        # 言語フィールドがない場合はアイテムコードを返す
        if 'アイテムコード' in self.data:
            return self.data['アイテムコード']
        
        # どちらもない場合は空文字列を返す
        return ""
    
    @property
    def code(self):
        """
        アイテムコードを取得
        
        戻り値:
            str: アイテムコード
        """
        return self.data.get('アイテムコード', "")
    
    @property
    def url(self):
        """
        アイテムのURLを取得
        
        戻り値:
            str: アイテムのURL
        """
        return self.data.get('URL', "")
    
    def set_language(self, language):
        """
        言語設定を変更
        
        引数:
            language (str): 設定する言語コード
        
        戻り値:
            Item: 自身のインスタンス（メソッドチェーン用）
        """
        if language in self.LANGUAGE_FIELDS:
            self.language = language
        else:
            logging.warning(f"サポートされていない言語コード: {language}、デフォルト言語を使用します。")
            self.language = self.DEFAULT_LANGUAGE
        return self
    
    def __str__(self):
        """
        アイテムの文字列表現
        
        戻り値:
            str: アイテム名
        """
        return self.name
    
    def to_dict(self):
        """
        アイテム情報を辞書形式で取得
        
        戻り値:
            dict: アイテム情報の辞書
        """
        return {
            'name': self.name,
            'code': self.code,
            'url': self.url,
            'language': self.language
        }


class ItemManager:
    """
    Factorioのアイテム情報を管理するクラス
    
    このクラスは、CSVファイルからアイテム情報を読み込み、
    アイテム名からアイテム情報を検索する機能を提供します。
    """
    
    def __init__(self, csv_path=None, language=None):
        """
        アイテムマネージャーを初期化
        
        引数:
            csv_path (str): CSVファイルのパス（デフォルト: スクリプトと同じディレクトリの'factorio_items.csv'）
            language (str): デフォルトの言語コード（デフォルト: Itemクラスのデフォルト言語）
        """
        # CSVファイルのパスが指定されていない場合はデフォルトパスを使用
        if csv_path is None:
            csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'factorio_items.csv')
        
        self.csv_path = csv_path
        self.language = language or Item.DEFAULT_LANGUAGE
        self.items = []
        self.load_items()
    
    def load_items(self):
        """
        CSVファイルからアイテム情報を読み込む
        """
        try:
            with open(self.csv_path, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                self.items = [Item(row, self.language) for row in reader]
            logging.info(f"{len(self.items)} 件のアイテム情報を読み込みました。")
        except Exception as e:
            logging.error(f"CSVファイル読み込みエラー: {e}")
            self.items = []
    
    def find_item_by_name(self, item_name):
        """
        アイテム名からアイテムを検索
        
        引数:
            item_name (str): 検索するアイテム名
        
        戻り値:
            Item: 見つかったアイテム、見つからない場合はNone
        """
        for item in self.items:
            if item.name == item_name:
                return item
        
        logging.warning(f"指定されたアイテム「{item_name}」は見つかりません。")
        return None
    
    def find_item_by_code(self, item_code):
        """
        アイテムコードからアイテムを検索
        
        引数:
            item_code (str): 検索するアイテムコード
        
        戻り値:
            Item: 見つかったアイテム、見つからない場合はNone
        """
        for item in self.items:
            if item.code == item_code:
                return item
        
        logging.warning(f"指定されたアイテムコード「{item_code}」は見つかりません。")
        return None
    
    def get_item_url(self, item_name):
        """
        アイテム名からURLを取得
        
        引数:
            item_name (str): アイテムの名前
        
        戻り値:
            str: アイテムのURL、見つからない場合はNone
        """
        item = self.find_item_by_name(item_name)
        return item.url if item else None
    
    def get_item_code(self, item_name):
        """
        アイテム名からアイテムコードを取得
        
        引数:
            item_name (str): アイテムの名前
        
        戻り値:
            str: アイテムコード、見つからない場合はNone
        """
        item = self.find_item_by_name(item_name)
        return item.code if item else None
    
    def set_language(self, language):
        """
        言語設定を変更
        
        引数:
            language (str): 設定する言語コード
        
        戻り値:
            ItemManager: 自身のインスタンス（メソッドチェーン用）
        """
        self.language = language
        # すべてのアイテムの言語設定を変更
        for item in self.items:
            item.set_language(language)
        return self
    
    def add_item(self, item_name_ja, item_code, item_url):
        """
        新しいアイテム情報をCSVに追加
        
        引数:
            item_name_ja (str): アイテムの日本語名
            item_code (str): アイテムの英語コード
            item_url (str): アイテムのWikiページURL
        
        戻り値:
            bool: 追加が成功したかどうか
        """
        try:
            # 既存のデータを読み込み
            items_data = []
            fieldnames = [Item.LANGUAGE_FIELDS['ja'], 'アイテムコード', 'URL']
            
            if os.path.exists(self.csv_path):
                with open(self.csv_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    # CSVのヘッダーを取得
                    if reader.fieldnames:
                        fieldnames = reader.fieldnames
                    items_data = list(reader)
            
            # 既存のアイテムかチェック
            for item_data in items_data:
                if Item.LANGUAGE_FIELDS['ja'] in item_data and item_data[Item.LANGUAGE_FIELDS['ja']] == item_name_ja:
                    logging.info(f"アイテム「{item_name_ja}」は既にCSVに存在します。")
                    return False
            
            # 新しいアイテムデータの準備
            new_item = {Item.LANGUAGE_FIELDS['ja']: item_name_ja}
            # フィールド名に応じてデータを設定
            if 'アイテムコード' in fieldnames:
                new_item['アイテムコード'] = item_code
            if 'URL' in fieldnames:
                new_item['URL'] = item_url
            
            # その他の存在するフィールドに空の値を設定
            for field in fieldnames:
                if field not in new_item:
                    new_item[field] = ""
            
            # 新しいアイテムを追加
            with open(self.csv_path, 'w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for item_data in items_data:
                    writer.writerow(item_data)
                writer.writerow(new_item)
            
            # アイテムリストに追加
            self.items.append(Item(new_item, self.language))
            
            logging.info(f"アイテム「{item_name_ja}」をCSVに追加しました。")
            return True
        
        except Exception as e:
            logging.error(f"CSVファイル書き込みエラー: {e}")
            logging.debug(f"例外の詳細: {str(e)}", exc_info=True)
            return False


# 後方互換性のための関数
def load_item_url(item_name, csv_path=None, language=None):
    """
    アイテム名からURLを取得する関数（後方互換性用）
    
    引数:
        item_name (str): アイテムの名前
        csv_path (str): CSVファイルのパス（デフォルト: スクリプトと同じディレクトリの'factorio_items.csv'）
        language (str): 言語コード（デフォルト: Itemクラスのデフォルト言語）
        
    戻り値:
        str: アイテムのURL、見つからない場合はNone
    """
    manager = ItemManager(csv_path, language)
    return manager.get_item_url(item_name)

# 後方互換性のための変数
item_name_ja_field = Item.LANGUAGE_FIELDS['ja']
