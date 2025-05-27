"""
Factorio アイテム容積取得ツール
==============================

このスクリプトは、Factorioのアイテム情報ページからロケット容量を取得し、
アイテムの容積を計算するツールです。
アイテム情報ファイルに容量情報を付記してJSON形式で保存します。

アイテム情報ファイルは「item_アイテム名.json」の形式で保存され、
既存のファイルがある場合はそれに追記・上書きします。

使用方法:
  python get_item_volume.py -i <アイテム名> [-c <CSVファイルパス>] [-d] [-l <言語コード>] [--config <設定ファイルパス>]

オプション:
  -i, --item    アイテム名 (必須)
  -c, --csv     CSVファイルのパス（デフォルト=factorio_items.csv）
  -d, --debug   デバッグモードを有効化（詳細なログを出力）
  -l, --lang    言語コード (ja または en, デフォルト=ja)
  --config      設定ファイルのパス

例:
  python get_item_volume.py -i 鉄板
  python get_item_volume.py -i 電子回路 -c my_items.csv
  python get_item_volume.py -i 崖用発破 -d
  python get_item_volume.py -i Iron_plate -l en
  python get_item_volume.py -i 鉄板 --config my_config.json
"""

import argparse
import logging
import requests
import sys
import re
import os
import json
from bs4 import BeautifulSoup
from factorio_item import ItemManager, Item
from factorio_config import load_config

# ログ設定 - INFO レベルで基本的なログを出力
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

def get_item_rocket_capacity(page_url):
    """
    指定されたページURLからアイテムのロケット容量を取得する関数
    
    引数:
        page_url (str): アイテム情報を取得するページのURL
    
    戻り値:
        int: ロケット容量、見つからない場合はNone
    """
    # URLにスキームがない場合にチェック
    if not page_url.startswith('http'):
        logging.warning(f"完全なURLではありません: {page_url}")
        # 相対パスの場合はベースURLを追加
        if not page_url.startswith('https://') and not page_url.startswith('http://'):
            base_url = 'https://wiki.factorio.com/'
            page_url = base_url + page_url
            logging.debug(f"URLを修正: {page_url}")
    
    try:
        # URLからページを取得
        logging.debug(f"リクエスト送信: {page_url}")
        res = requests.get(page_url)
        res.raise_for_status()  # HTTPエラーがあれば例外を発生
        logging.info(f"ページ取得成功: {page_url} (ステータスコード: {res.status_code})")
    except requests.exceptions.RequestException as e:
        # リクエスト失敗時のエラーハンドリング
        logging.error(f"ページ取得失敗: {e}")
        return None

    # BeautifulSoupでHTMLを解析
    soup = BeautifulSoup(res.text, 'html.parser')
    
    # ページ内のすべてのテキストを検索（デバッグ用）
    page_text = soup.get_text()
    logging.debug(f"ページテキスト（一部）: {page_text[:500]}...")
    
    # テーブルセルから「ロケット容量」を含むセルを探す
    for td in soup.find_all('td'):
        td_text = td.get_text().strip()
        logging.debug(f"テーブルセル内容: {td_text}")
        
        if 'ロケット容量' in td_text:
            logging.debug(f"「ロケット容量」を含むセルを検出: {td_text}")
            
            # 次のtdタグを取得
            next_td = td.find_next_sibling('td')
            if next_td:
                next_td_text = next_td.get_text().strip()
                logging.debug(f"次のセルの内容: {next_td_text}")
                
                # 数値を抽出
                capacity_match = re.search(r'(\d+)', next_td_text)
                if capacity_match:
                    capacity = int(capacity_match.group(1))
                    logging.debug(f"ロケット容量を検出: {capacity}")
                    return capacity
    
    # 見つからなかった場合、テーブル行から探す
    for tr in soup.find_all('tr'):
        tr_text = tr.get_text().strip()
        if 'ロケット容量' in tr_text:
            logging.debug(f"「ロケット容量」を含む行を検出: {tr_text}")
            
            # 数値を抽出
            capacity_match = re.search(r'(\d+)', tr_text)
            if capacity_match:
                capacity = int(capacity_match.group(1))
                logging.debug(f"行からロケット容量を検出: {capacity}")
                return capacity
    
    logging.debug("ロケット容量が見つかりませんでした")
    return None

def calculate_item_volume(rocket_capacity):
    """
    ロケット容量からアイテムの容積を計算する関数
    
    引数:
        rocket_capacity (int): アイテムのロケット容量
    
    戻り値:
        float: アイテムの容積、ロケット容量がNoneまたは0の場合はNone
    """
    if rocket_capacity is None or rocket_capacity == 0:
        return None
    
    # 容積の計算: ロケット容積 / アイテムのロケット容量
    rocket_volume = 1000
    volume = rocket_volume / rocket_capacity
    logging.debug(f"アイテム容積を計算: {volume}")
    return volume

def create_item_json(item_name, rocket_capacity, item_volume, csv_path=None, language=None):
    """
    容量情報をJSON形式のデータとして作成し、アイテム情報ファイルに付記する関数
    
    引数:
        item_name (str): アイテムの名前
        rocket_capacity (int): ロケット容量
        item_volume (float): アイテム容積
        csv_path (str): CSVファイルのパス
        language (str): 言語コード
        
    戻り値:
        dict: JSON形式のアイテムデータ（容量情報を含む）
    """
    # ItemManagerの初期化
    manager = ItemManager(csv_path, language)
    
    # アイテムコードを取得
    item_code = manager.get_item_code(item_name)
    
    # JSONデータの基本構造
    item_data = {
        "item_name": item_name,
        "item_code": item_code,
        "rocket_capacity": rocket_capacity,
        "volume": item_volume
    }
    
    return item_data

def get_item_volume(item_name, csv_path, language, json_dir=None, max_depth=0, current_depth=0, processed_items=None):
    """
    アイテムの容積情報を取得し、JSONファイルに保存する関数
    
    引数:
        item_name (str): アイテムの名前
        csv_path (str): CSVファイルのパス
        language (str): 言語コード
        json_dir (str): JSONファイルの保存ディレクトリ（デフォルト: None、保存しない）
        max_depth (int): 再帰的に材料のレシピを取得する最大深さ（デフォルト: 0、再帰なし）
        current_depth (int): 現在の再帰深さ（内部使用）
        processed_items (set): 既に処理済みのアイテム名のセット（内部使用、循環参照防止）
        
    戻り値:
        dict: アイテム情報を含む辞書
    """
    # 処理済みアイテムの初期化（循環参照防止）
    if processed_items is None:
        processed_items = set()
    
    # 既に処理済みのアイテムの場合はスキップ
    if item_name in processed_items:
        logging.debug(f"アイテム「{item_name}」は既に処理済みのため、スキップします。")
        return None
    
    # 処理済みアイテムに追加
    processed_items.add(item_name)
    
    # ItemManagerの初期化
    manager = ItemManager(csv_path, language)

    # アイテム名からURLを取得
    logging.debug(f"アイテム名: {item_name}")
    
    page_url = manager.get_item_url(item_name)
    if not page_url:
        logging.error(f"指定されたアイテム「{item_name}」はCSVに見つかりません。")
        return None
    
    logging.info(f"アイテム「{item_name}」のURLを取得: {page_url}")

    # ロケット容量の取得
    rocket_capacity = get_item_rocket_capacity(page_url)
    
    # 容積の計算
    item_volume = calculate_item_volume(rocket_capacity)
    
    # アイテム情報に容積情報を付記してJSON形式で出力
    volume_data = create_item_json(item_name, rocket_capacity, item_volume, csv_path, language)
    
    # JSONファイルに保存
    if json_dir:
        # JSONファイルのパスを取得
        json_filename = f"item_{item_name}.json"
        json_path = os.path.join(json_dir, json_filename)
        
        # 既存のJSONファイルがあれば読み込む
        existing_data = {}
        if os.path.exists(json_path):
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
                logging.info(f"既存のアイテム情報を {json_path} から読み込みました。")
            except Exception as e:
                logging.error(f"既存のJSONファイルの読み込みエラー: {e}")
                logging.debug(f"例外の詳細: {str(e)}", exc_info=True)
        
        # 既存のデータを更新
        existing_data.update(volume_data)
        
        # JSONファイルに保存
        try:
            # ディレクトリが存在しない場合は作成
            os.makedirs(os.path.dirname(os.path.abspath(json_path)), exist_ok=True)
            
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, ensure_ascii=False, indent=4)
            
            logging.info(f"アイテム情報を {json_path} に保存しました。")
            
            # 最上位の呼び出しの場合のみ標準出力に表示
            if current_depth == 0:
                print(f"🚀 アイテム: {item_name} の容積情報:")
                
                if rocket_capacity:
                    print(f"ロケット容量: {rocket_capacity}")
                    
                    if item_volume:
                        print(f"アイテム容積: {item_volume:.2f}")
                    else:
                        print("アイテム容積を計算できませんでした。")
                else:
                    print("ロケット容量情報は取得できませんでした。")
                
                print(f"容量情報をアイテム情報ファイル {json_path} に保存しました。")
        except Exception as e:
            logging.error(f"JSONファイルの保存エラー: {e}")
            logging.debug(f"例外の詳細: {str(e)}", exc_info=True)
    
    # 最大深さに達していない場合、材料のレシピも再帰的に取得
    if max_depth > 0 and current_depth < max_depth:
        # 材料情報を取得するために、レシピ情報が必要
        # レシピ情報を取得するために、get_item_recipeモジュールをインポート
        try:
            from get_item_recipe import get_recipe
            
            # レシピ情報を取得
            materials, _ = get_recipe(page_url)
            
            for material_code, _ in materials:
                # 材料のアイテム名を取得
                material_item = manager.find_item_by_code(material_code)
                if material_item:
                    material_name = material_item.name
                    # 材料の容積情報を再帰的に取得
                    get_item_volume(
                        material_name, 
                        csv_path,
                        language,
                        json_dir,  # 材料のJSONも同じディレクトリに保存
                        max_depth, 
                        current_depth + 1, 
                        processed_items
                    )
        except ImportError:
            logging.warning("get_item_recipeモジュールをインポートできないため、材料の再帰的な処理をスキップします。")
    
    return volume_data

def main():
    """
    メイン関数: コマンドライン引数を解析し、アイテムの容積情報を取得して表示
    """
    # コマンドライン引数の設定
    parser = argparse.ArgumentParser(description='Factorio アイテム容積取得ツール')
    parser.add_argument('-i', '--item', type=str, required=True, help='アイテム名')
    parser.add_argument('-c', '--csv', type=str, default=None,
                        help='CSVファイルのパス')
    parser.add_argument('-d', '--debug', action='store_true', help='デバッグモードを有効化')
    parser.add_argument('-l', '--lang', type=str, choices=['ja', 'en'], default=None,
                        help='言語コード (ja または en)')
    parser.add_argument('--config', type=str, default=None, help='設定ファイルのパス')
    parser.add_argument('--depth', type=int, default=0, 
                        help='材料の容積情報を再帰的に取得する深さ（デフォルト: 0、再帰なし）')
    args = parser.parse_args()

    # デバッグモードを有効化
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logging.debug("デバッグモードが有効化されました")

    # 設定を読み込む
    config = load_config(args.config)

    # コマンドライン引数で指定された値を設定に反映
    if args.csv:
        config.set('csv_file', args.csv)
    if args.lang:
        config.set('language', args.lang)

    # CSVパスを取得
    csv_path = config.get_csv_path()
    logging.debug(f"CSVパス: {csv_path}")

    # 言語設定を取得
    language = config.get_language()
    logging.debug(f"言語設定: {language}")

    # JSONディレクトリを取得
    json_dir = os.path.join(config.get('data_dir', ''), config.get('json_dir', ''))
    logging.debug(f"JSONディレクトリ: {json_dir}")

    # アイテム名
    item_name = args.item
    
    # 容積情報の取得と保存
    volume_data = get_item_volume(
        item_name, 
        csv_path, 
        language, 
        json_dir,
        args.depth
    )
    
    if not volume_data:
        print(f"エラー: アイテム「{item_name}」の情報が見つかりません。")


if __name__ == '__main__':
    main()
