"""
Factorio レシピ取得ツール
=========================

このスクリプトは、Factorioのレシピ情報をウェブサイトから取得するツールです。
Factorioのレシピページから材料と生成物の情報を抽出し、アイテム情報ファイルに
レシピ情報を付記してJSON形式で保存します。

アイテム情報ファイルは「item_アイテム名.json」の形式で保存され、
既存のファイルがある場合はそれに追記・上書きします。

使用方法:
  python factorio_recipe.py -i <アイテム名> [-m <ゲームモード>] [-c <CSVファイルパス>] [-d] [-l <言語コード>] [--config <設定ファイルパス>]
  python factorio_recipe.py -i <アイテム名> -a <アイテムコード> <URL>

オプション:
  -i, --item    アイテム名 (必須)
  -m, --mode    ゲームモード (Base または SpaceAge, デフォルト=SpaceAge)
  -c, --csv     CSVファイルのパス（デフォルト=factorio_items.csv）
  -d, --debug   デバッグモードを有効化（詳細なログを出力）
  -a, --add     新しいアイテムをCSVに追加（アイテムコードとURLを指定）
  -l, --lang    言語コード (ja または en, デフォルト=ja)
  --config      設定ファイルのパス

例:
  python factorio_recipe.py -i 鉄板 -m Base
  python factorio_recipe.py -i 電子回路 -c my_items.csv
  python factorio_recipe.py -i 崖用発破 -d
  python factorio_recipe.py -i 崖用発破 -a Cliff_explosives https://wiki.factorio.com/Cliff_explosives/ja
  python factorio_recipe.py -i Iron_plate -l en
  python factorio_recipe.py -i 鉄板 --config my_config.json
"""

import argparse
import logging
import requests
import sys
import os
import json
from bs4 import BeautifulSoup
from factorio_item import ItemManager, Item
from factorio_config import load_config

# ログ設定
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')


def get_recipe(page_url, game_mode='SpaceAge'):
    """
    指定されたページURLからFactorioのレシピ情報を取得する関数
    
    引数:
        page_url (str): レシピ情報を取得するページのURL
        game_mode (str): ゲームモード ('Base' または 'SpaceAge')
    
    戻り値:
        tuple: (材料リスト, 生成物情報)
            - 材料リスト: [(アイテム名, 数量), ...] の形式
            - 生成物情報: (アイテム名, 数量) または None
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
        return [], None

    # BeautifulSoupでHTMLを解析
    soup = BeautifulSoup(res.text, 'html.parser')
    materials = []  # 材料を格納するリスト
    product = None  # 生成物情報

    # ゲームモードに応じたテーブルクラスを選択
    tab_class = 'tab-2' if game_mode == 'SpaceAge' else 'tab-1'
    logging.debug(f"検索するタブクラス: tab {tab_class}")
    
    # クラス名に部分一致するテーブルを検索
    recipe_tables = []
    for table in soup.find_all('table'):
        if table.has_attr('class'):
            class_str = ' '.join(table['class'])
            logging.debug(f"テーブルクラス: {class_str}")
            if 'tab' in class_str and tab_class in class_str:
                recipe_tables.append(table)
    
    logging.debug(f"{len(recipe_tables)} 個のレシピテーブル (class含む={tab_class}) を検出")
    
    # テーブルが見つからない場合は別の方法で検索
    if not recipe_tables:
        logging.debug(f"通常のクラス検索ではテーブルが見つかりませんでした。別の方法で検索します。")
        for table in soup.find_all('table'):
            # テーブルの内容を確認
            if 'レシピ' in table.get_text():
                recipe_tables.append(table)
                logging.debug("'レシピ'を含むテーブルを追加")
    
    logging.debug(f"最終的に {len(recipe_tables)} 個のテーブルを処理します")

    # レシピテーブルの検索と解析
    recipe_found = False
    for table in recipe_tables:
        # 「レシピ」という文字列を含むテーブルを探す
        if 'レシピ' not in table.get_text():
            continue
        logging.debug("レシピテーブル候補を発見")

        # テーブルの内容を出力（デバッグ用）
        logging.debug(f"テーブル内容の一部: {table.get_text()[:200]}...")
        
        # レシピセクションを検出するフラグ
        in_recipe_section = False
        for tr in table.find_all('tr'):
            # tr内の内容を確認（デバッグ用）
            tr_text = tr.get_text().strip()
            logging.debug(f"TR内容: {tr_text[:100]}...")
            
            # レシピセクションの開始を検出
            if tr.find('p') and 'レシピ' in tr.text:
                in_recipe_section = True
                logging.debug("レシピセクション開始")
                continue
            # トータルコストに達したらレシピセクション終了
            if tr.find('p') and 'トータルコスト' in tr.text:
                logging.debug("トータルコストに到達、レシピセクション終了")
                break
            # レシピセクション内のみ処理
            if not in_recipe_section:
                continue

            # tr要素の内容全体を取得
            tr_html = str(tr)
            logging.debug(f"TR HTML: {tr_html[:200]}...")
            
            # 矢印(&#8594;)の位置を特定
            arrow_pos = tr_html.find('&#8594;')
            if arrow_pos == -1:
                arrow_pos = tr_html.find('→')
            
            logging.debug(f"矢印位置: {arrow_pos}")
            
            # アイコン要素を取得
            icons = []
            for div in tr.find_all('div', class_=lambda c: c and 'factorio-icon' in c):
                icons.append(div)
                logging.debug(f"アイコン要素を検出: {div.get('class')}")
            
            if not icons:
                logging.debug("アイコン要素が見つかりません")
                continue
            
            logging.debug(f"{len(icons)} 個のアイコン要素を検出")
            
            # 材料と生成物を分類
            materials = []
            product = None
            
            # 各アイコンの位置を特定し、矢印の前後で分類
            for icon in icons:
                icon_pos = tr_html.find(str(icon))
                
                a_tag = icon.find('a')
                qty_tag = icon.find('div', class_=lambda c: c and 'factorio-icon-text' in c)
                
                if not a_tag or not qty_tag:
                    logging.debug(f"アイコン: aタグまたは数量タグが見つかりません")
                    continue
                
                # アイテムコードと数量を取得
                href = a_tag.get('href', '')
                item_code = href.strip('/').replace('/ja', '')  # 例: /Cliff_explosives/ja → Cliff_explosives
                quantity = qty_tag.text.strip()
                
                logging.debug(f"アイコン位置: {icon_pos}, 矢印位置: {arrow_pos}, アイテムコード: {item_code}, 数量: {quantity}")
                
                # 矢印の前後で材料と生成物に分類
                if arrow_pos > 0 and icon_pos > arrow_pos:
                    product = (item_code, quantity)
                    logging.debug(f"生成物: {item_code} x {quantity}")
                    recipe_found = True
                else:
                    materials.append((item_code, quantity))
                    logging.debug(f"材料: {item_code} x {quantity}")
                    recipe_found = True
        
        # レシピが見つかった場合は最初のテーブルのみ処理
        if recipe_found:
            logging.debug("レシピが見つかったため、最初のテーブルのみ処理")
            break

    # レシピが見つからなかった場合の警告
    if not materials and not product:
        logging.warning("レシピが見つかりませんでした。")

    return materials, product


def get_item_code_from_name(item_name, csv_path=None, language=None):
    """
    アイテム名からアイテムコードを取得する関数
    
    引数:
        item_name (str): アイテムの名前
        csv_path (str): CSVファイルのパス（デフォルトはスクリプトと同じディレクトリの'factorio_items.csv'）
        language (str): 言語コード（デフォルト: Itemクラスのデフォルト言語）
        
    戻り値:
        str: アイテムコード、見つからない場合はNone
    """
    manager = ItemManager(csv_path, language)
    return manager.get_item_code(item_name)

def create_item_json(item_name, materials, product, csv_path=None, language=None):
    """
    レシピ情報をJSON形式のデータとして作成する関数
    
    引数:
        item_name (str): アイテムの名前
        materials (list): 材料リスト [(アイテムコード, 数量), ...]
        product (tuple): 生成物情報 (アイテムコード, 数量) または None
        csv_path (str): CSVファイルのパス
        language (str): 言語コード（デフォルト: Itemクラスのデフォルト言語）
        
    戻り値:
        dict: JSON形式のレシピデータ
    """
    # アイテムコードを取得
    item_code = get_item_code_from_name(item_name, csv_path, language)
    
    # JSONデータの基本構造
    item_data = {
        "item_name": item_name,
        "item_code": item_code,
        "recipe": [],
        "production_number": 0
    }
    
    # 材料情報を追加
    for material_code, quantity in materials:
        try:
            consumption_number = int(quantity)
        except ValueError:
            # 数値に変換できない場合はデフォルト値として1を使用
            logging.warning(f"材料「{material_code}」の数量「{quantity}」を数値に変換できません。デフォルト値1を使用します。")
            consumption_number = 1
            
        item_data["recipe"].append({
            "item_code": material_code,
            "consumption_number": consumption_number
        })
    
    # 生成物情報を追加
    if product:
        try:
            production_number = int(product[1])
        except (ValueError, IndexError):
            # 数値に変換できない場合はデフォルト値として1を使用
            logging.warning(f"生成物の数量「{product[1] if len(product) > 1 else 'unknown'}」を数値に変換できません。デフォルト値1を使用します。")
            production_number = 1
            
        item_data["production_number"] = production_number
    
    return item_data

def get_item_recipe(item_name, csv_path, language, game_mode, json_dir=None, max_depth=0, current_depth=0, processed_items=None):
    """
    アイテムのレシピ情報を取得し、JSONファイルに保存する関数
    
    引数:
        item_name (str): アイテムの名前
        csv_path (str): CSVファイルのパス
        language (str): 言語コード
        game_mode (str): ゲームモード ('Base' または 'SpaceAge')
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

    # レシピ情報の取得
    materials, product = get_recipe(page_url, game_mode=game_mode)
    
    # アイテム情報にレシピ情報を付記してJSON形式で出力
    item_json = create_item_json(item_name, materials, product, csv_path, language)
    
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
        existing_data.update(item_json)
        
        # JSONファイルに保存
        try:
            # ディレクトリが存在しない場合は作成
            os.makedirs(os.path.dirname(os.path.abspath(json_path)), exist_ok=True)
            
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, ensure_ascii=False, indent=4)
            
            logging.info(f"アイテム情報を {json_path} に保存しました。")
            
            # 最上位の呼び出しの場合のみ標準出力に表示
            if current_depth == 0:
                print(json.dumps(item_json, ensure_ascii=False, indent=4))
                print(f"レシピ情報をアイテム情報ファイル {json_path} に保存しました。")
        except Exception as e:
            logging.error(f"JSONファイルの保存エラー: {e}")
            logging.debug(f"例外の詳細: {str(e)}", exc_info=True)
    
    # 最大深さに達していない場合、材料のレシピも再帰的に取得
    if max_depth > 0 and current_depth < max_depth:
        for material_code, _ in materials:
            # 材料のアイテム名を取得
            material_item = manager.find_item_by_code(material_code)
            if material_item:
                material_name = material_item.name
                # 材料のレシピを再帰的に取得
                get_item_recipe(
                    material_name, 
                    csv_path,
                    language,
                    game_mode,
                    json_dir,  # 材料のJSONも同じディレクトリに保存
                    max_depth, 
                    current_depth + 1, 
                    processed_items
                )
    
    return item_json

def main():
    """
    メイン関数: コマンドライン引数を解析し、レシピ情報を取得してJSON形式で出力
    """
    # コマンドライン引数の設定
    parser = argparse.ArgumentParser(description='Factorio Space Age レシピ取得ツール')
    parser.add_argument('-i', '--item', type=str, required=True, help='アイテム名')
    parser.add_argument('-m', '--mode', type=str, choices=['Base', 'SpaceAge'], default=None, 
                        help='ゲームモード (Base or SpaceAge)')
    parser.add_argument('-c', '--csv', type=str, default=None,
                        help='CSVファイルのパス')
    parser.add_argument('-d', '--debug', action='store_true', help='デバッグモードを有効化')
    parser.add_argument('-a', '--add', nargs=2, metavar=('ITEM_CODE', 'URL'), 
                        help='新しいアイテムをCSVに追加（アイテムコードとURLを指定）')
    parser.add_argument('-l', '--lang', type=str, choices=['ja', 'en'], default=None,
                        help='言語コード (ja または en)')
    parser.add_argument('--config', type=str, default=None, help='設定ファイルのパス')
    parser.add_argument('--depth', type=int, default=0, 
                        help='材料のレシピを再帰的に取得する深さ（デフォルト: 0、再帰なし）')
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
    if args.mode:
        config.set('game_mode', args.mode)

    # CSVパスを取得
    csv_path = config.get_csv_path()
    logging.debug(f"CSVパス: {csv_path}")

    # 言語設定を取得
    language = config.get_language()
    logging.debug(f"言語設定: {language}")

    # ゲームモード設定を取得
    game_mode = config.get_game_mode()
    logging.debug(f"ゲームモード設定: {game_mode}")

    # JSONディレクトリを取得
    json_dir = os.path.join(config.get('data_dir', ''), config.get('json_dir', ''))
    logging.debug(f"JSONディレクトリ: {json_dir}")

    # ItemManagerの初期化
    manager = ItemManager(csv_path, language)

    # アイテム追加モード
    if args.add:
        item_code, item_url = args.add
        add_result = manager.add_item(args.item, item_code, item_url)
        if add_result:
            print(f"アイテム「{args.item}」をCSVに追加しました。")
        else:
            print(f"アイテム「{args.item}」の追加に失敗しました。")
        return

    # アイテム名
    item_name = args.item
    
    # レシピ情報の取得と保存
    item_json = get_item_recipe(
        item_name, 
        csv_path, 
        language, 
        game_mode, 
        json_dir,
        args.depth
    )
    
    if not item_json:
        print(f"エラー: アイテム「{item_name}」の情報が見つかりません。")
        print(f"次のコマンドで追加できます: python {sys.argv[0]} -i {item_name} -a アイテムコード URL")


if __name__ == '__main__':
    main()
