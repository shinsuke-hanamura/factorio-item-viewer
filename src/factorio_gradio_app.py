"""
Factorio アイテムビューアー Gradio アプリ
==========================================

このアプリは、get_item_recipe.pyとget_item_volume.pyの実行結果であるJSONファイルを読み込み、
Factorioのアイテム情報を画面に表示するGradioアプリです。
"""

import gradio as gr
import json
import os
import glob
import pandas as pd
from typing import Dict, List, Optional, Tuple
import logging

# 既存のモジュールをインポート
from factorio_config import load_config
from factorio_item import ItemManager

# ロギング設定
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

class FactorioItemViewer:
    """
    Factorioアイテム情報を表示するクラス
    """
    
    def __init__(self, config_file=None):
        """
        初期化
        
        引数:
            config_file (str): 設定ファイルのパス
        """
        self.config = load_config(config_file)
        self.item_manager = ItemManager(self.config.get_csv_path(), self.config.get_language())
        self.json_dir = os.path.join(self.config.get('data_dir', 'data'), self.config.get('json_dir', 'json'))
        
    def load_all_items(self) -> List[Dict]:
        """
        すべてのJSONファイルからアイテム情報を読み込む
        
        戻り値:
            List[Dict]: アイテム情報のリスト
        """
        items = []
        
        if not os.path.exists(self.json_dir):
            logging.warning(f"JSONディレクトリが見つかりません: {self.json_dir}")
            return items
            
        json_files = glob.glob(os.path.join(self.json_dir, "item_*.json"))
        
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    item_data = json.load(f)
                    items.append(item_data)
            except Exception as e:
                logging.error(f"JSONファイル読み込みエラー ({json_file}): {e}")
                
        return items
    
    def get_item_list(self) -> List[str]:
        """
        利用可能なアイテムのリストを取得
        
        戻り値:
            List[str]: アイテム名のリスト
        """
        items = self.load_all_items()
        return [item.get('item_name', 'Unknown') for item in items]
    
    def get_item_info(self, item_name: str) -> Tuple[str, str, str, str]:
        """
        指定されたアイテムの詳細情報を取得
        
        引数:
            item_name (str): アイテム名
            
        戻り値:
            Tuple[str, str, str, str]: (基本情報, レシピ情報, 容量情報, JSON表示)
        """
        if not item_name:
            return "アイテムを選択してください。", "", "", ""
            
        items = self.load_all_items()
        target_item = None
        
        for item in items:
            if item.get('item_name') == item_name:
                target_item = item
                break
                
        if not target_item:
            return f"アイテム「{item_name}」の情報が見つかりません。", "", "", ""
            
        # 基本情報
        basic_info = self._format_basic_info(target_item)
        
        # レシピ情報
        recipe_info = self._format_recipe_info(target_item)
        
        # 容量情報
        volume_info = self._format_volume_info(target_item)
        
        # JSON表示
        json_display = json.dumps(target_item, ensure_ascii=False, indent=2)
        
        return basic_info, recipe_info, volume_info, json_display
    
    def _format_basic_info(self, item: Dict) -> str:
        """
        基本情報をフォーマット
        
        引数:
            item (Dict): アイテム情報
            
        戻り値:
            str: フォーマットされた基本情報
        """
        info = []
        info.append(f"**アイテム名**: {item.get('item_name', 'Unknown')}")
        info.append(f"**アイテムコード**: {item.get('item_code', 'Unknown')}")
        
        if 'production_number' in item:
            info.append(f"**生産数**: {item['production_number']}")
            
        return "\n".join(info)
    
    def _format_recipe_info(self, item: Dict) -> str:
        """
        レシピ情報をフォーマット
        
        引数:
            item (Dict): アイテム情報
            
        戻り値:
            str: フォーマットされたレシピ情報
        """
        if 'recipe' not in item or not item['recipe']:
            return "レシピ情報がありません。"
            
        info = ["**レシピ (材料)**:"]
        
        for material in item['recipe']:
            item_code = material.get('item_code', 'Unknown')
            consumption = material.get('consumption_number', 0)
            
            # アイテムコードから日本語名を取得を試みる
            japanese_name = self._get_japanese_name(item_code)
            if japanese_name and japanese_name != item_code:
                info.append(f"- {japanese_name} ({item_code}): {consumption}")
            else:
                info.append(f"- {item_code}: {consumption}")
                
        return "\n".join(info)
    
    def _format_volume_info(self, item: Dict) -> str:
        """
        容量情報をフォーマット
        
        引数:
            item (Dict): アイテム情報
            
        戻り値:
            str: フォーマットされた容量情報
        """
        info = []
        
        if 'rocket_capacity' in item:
            info.append(f"**ロケット容量**: {item['rocket_capacity']}")
            
        if 'volume' in item:
            info.append(f"**容積**: {item['volume']}")
            
        if not info:
            return "容量情報がありません。"
            
        return "\n".join(info)
    
    def _get_japanese_name(self, item_code: str) -> Optional[str]:
        """
        アイテムコードから日本語名を取得
        
        引数:
            item_code (str): アイテムコード
            
        戻り値:
            Optional[str]: 日本語名、見つからない場合はNone
        """
        item = self.item_manager.find_item_by_code(item_code)
        return item.name if item else None
    
    def get_items_table(self) -> pd.DataFrame:
        """
        すべてのアイテム情報をテーブル形式で取得
        
        戻り値:
            pd.DataFrame: アイテム情報のデータフレーム
        """
        items = self.load_all_items()
        
        if not items:
            return pd.DataFrame(columns=['アイテム名', 'アイテムコード', '生産数', 'ロケット容量', '容積', '材料数'])
            
        table_data = []
        
        for item in items:
            row = {
                'アイテム名': item.get('item_name', 'Unknown'),
                'アイテムコード': item.get('item_code', 'Unknown'),
                '生産数': item.get('production_number', ''),
                'ロケット容量': item.get('rocket_capacity', ''),
                '容積': item.get('volume', ''),
                '材料数': len(item.get('recipe', []))
            }
            table_data.append(row)
            
        return pd.DataFrame(table_data)
    
    def search_items(self, search_term: str) -> List[str]:
        """
        アイテムを検索
        
        引数:
            search_term (str): 検索語
            
        戻り値:
            List[str]: マッチしたアイテム名のリスト
        """
        if not search_term:
            return self.get_item_list()
            
        items = self.load_all_items()
        matched_items = []
        
        search_term_lower = search_term.lower()
        
        for item in items:
            item_name = item.get('item_name', '')
            item_code = item.get('item_code', '')
            
            if (search_term_lower in item_name.lower() or 
                search_term_lower in item_code.lower()):
                matched_items.append(item_name)
                
        return matched_items


def create_gradio_app(config_file=None):
    """
    Gradioアプリを作成
    
    引数:
        config_file (str): 設定ファイルのパス
        
    戻り値:
        gr.Blocks: Gradioアプリ
    """
    viewer = FactorioItemViewer(config_file)
    
    with gr.Blocks(title="Factorio アイテムビューアー", theme=gr.themes.Soft()) as app:
        gr.Markdown("# 🏭 Factorio アイテムビューアー")
        gr.Markdown("Factorio Wikiから取得したアイテム情報を表示します。")
        
        with gr.Tabs():
            # アイテム詳細タブ
            with gr.TabItem("アイテム詳細"):
                with gr.Row():
                    with gr.Column(scale=1):
                        search_box = gr.Textbox(
                            label="アイテム検索",
                            placeholder="アイテム名またはコードを入力...",
                            value=""
                        )
                        
                        item_dropdown = gr.Dropdown(
                            label="アイテム選択",
                            choices=viewer.get_item_list(),
                            value=None,
                            interactive=True
                        )
                        
                    with gr.Column(scale=2):
                        basic_info = gr.Markdown(label="基本情報")
                        
                with gr.Row():
                    with gr.Column():
                        recipe_info = gr.Markdown(label="レシピ情報")
                        
                    with gr.Column():
                        volume_info = gr.Markdown(label="容量情報")
                        
                with gr.Row():
                    json_display = gr.Code(
                        label="JSON データ",
                        language="json",
                        interactive=False
                    )
            
            # アイテム一覧タブ
            with gr.TabItem("アイテム一覧"):
                items_table = gr.Dataframe(
                    value=viewer.get_items_table(),
                    label="アイテム一覧",
                    interactive=False,
                    wrap=True
                )
                
                refresh_btn = gr.Button("🔄 更新", variant="secondary")
        
        # イベントハンドラー
        def update_item_info(item_name):
            return viewer.get_item_info(item_name)
        
        def search_and_update_dropdown(search_term):
            matched_items = viewer.search_items(search_term)
            return gr.Dropdown(choices=matched_items, value=None)
        
        def refresh_table():
            return viewer.get_items_table()
        
        # イベント設定
        item_dropdown.change(
            fn=update_item_info,
            inputs=[item_dropdown],
            outputs=[basic_info, recipe_info, volume_info, json_display]
        )
        
        search_box.change(
            fn=search_and_update_dropdown,
            inputs=[search_box],
            outputs=[item_dropdown]
        )
        
        refresh_btn.click(
            fn=refresh_table,
            outputs=[items_table]
        )
    
    return app


def main():
    """
    メイン関数
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='Factorio アイテムビューアー Gradio アプリ')
    parser.add_argument('--config', type=str, default=None, help='設定ファイルのパス')
    parser.add_argument('--port', type=int, default=7860, help='ポート番号')
    parser.add_argument('--host', type=str, default="127.0.0.1", help='ホストアドレス')
    parser.add_argument('--share', action='store_true', help='公開リンクを生成')
    args = parser.parse_args()
    
    try:
        app = create_gradio_app(args.config)
        
        print(f"🏭 Factorio アイテムビューアーを起動中...")
        print(f"📍 URL: http://{args.host}:{args.port}")
        
        app.launch(
            server_name=args.host,
            server_port=args.port,
            share=args.share,
            show_error=True
        )
        
    except Exception as e:
        logging.error(f"アプリケーション起動エラー: {e}")
        logging.debug(f"例外の詳細: {str(e)}", exc_info=True)


if __name__ == "__main__":
    main()
