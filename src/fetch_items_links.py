import requests
from bs4 import BeautifulSoup
import csv
import urllib.parse
import logging
import os
import argparse
from factorio_item import ItemManager, Item
from factorio_config import load_config

# ロギング設定
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

# アイテム名とURLのマッピングを読み込む関数
def load_item_url(item_name, csv_path=None, language=None):
    """
    アイテム名からURLを取得する関数
    
    引数:
        item_name (str): アイテムの名前
        csv_path (str): CSVファイルのパス（デフォルトはスクリプトと同じディレクトリの'factorio_items.csv'）
        language (str): 言語コード（デフォルト: Itemクラスのデフォルト言語）
        
    戻り値:
        str: アイテムのWikiページURL、見つからない場合はNone
    """
    manager = ItemManager(csv_path, language)
    return manager.get_item_url(item_name)

def fetch_items_from_materials_page(config):
    """
    Factorio Wikiの材料とレシピページからアイテム情報を取得し、CSVファイルに保存します。
    
    引数:
        config (Config): 設定オブジェクト
    
    戻り値:
        bool: 取得が成功したかどうか
    """
    # 設定から値を取得
    wiki_base_url = config.get_wiki_base_url()
    wiki_materials_page = config.get_wiki_materials_page()
    csv_path = config.get_csv_path()
    
    # URLを構築
    url = urllib.parse.urljoin(wiki_base_url, wiki_materials_page)
    
    try:
        res = requests.get(url)
        res.raise_for_status()
        logging.info(f"ページ取得成功: {url}")
    except requests.exceptions.RequestException as e:
        logging.error(f"ページ取得失敗: {e}")
        return False

    soup = BeautifulSoup(res.text, 'html.parser')

    items = []

    for icon_div in soup.select('div.factorio-icon'):
        a_tag = icon_div.find('a')
        if not a_tag:
            continue

        href = a_tag.get('href')
        title = a_tag.get('title')

        # /xxx/ja 形式のみ対象
        if not href or not href.endswith('/ja') or not title:
            continue

        item_code = href.strip('/').replace('/ja', '')  # 例: /Cliff_explosives/ja → Cliff_explosives
        full_url = urllib.parse.urljoin(wiki_base_url, href)

        items.append((title, item_code, full_url))
        logging.debug(f"抽出: {title} ({item_code}) → {full_url}")

    # 重複排除
    items = list(set(items))
    items.sort()

    # ディレクトリが存在しない場合は作成
    os.makedirs(os.path.dirname(os.path.abspath(csv_path)), exist_ok=True)

    # CSV書き出し
    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([Item.LANGUAGE_FIELDS['ja'], 'アイテムコード', 'URL'])
        writer.writerows(items)

    logging.info(f"{len(items)} 件のアイテムを {csv_path} に書き出しました。")
    
    # ItemManagerを使用してアイテム情報を読み込み
    manager = ItemManager(csv_path, config.get_language())
    logging.info(f"ItemManagerに {len(manager.items)} 件のアイテム情報を読み込みました。")
    
    return True

def main():
    """
    メイン関数: コマンドライン引数を解析し、アイテム情報を取得して保存
    """
    # コマンドライン引数の解析
    parser = argparse.ArgumentParser(description='Factorio アイテム情報取得ツール')
    parser.add_argument('-c', '--config', type=str, default=None, help='設定ファイルのパス')
    parser.add_argument('-d', '--debug', action='store_true', help='デバッグモードを有効化')
    args = parser.parse_args()
    
    # デバッグモードを有効化
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logging.debug("デバッグモードが有効化されました")
    
    # 設定を読み込む
    config = load_config(args.config)
    
    # アイテム情報を取得
    if fetch_items_from_materials_page(config):
        print(f"アイテム情報を {config.get_csv_path()} に保存しました。")
    else:
        print("アイテム情報の取得に失敗しました。")


if __name__ == "__main__":
    main()
