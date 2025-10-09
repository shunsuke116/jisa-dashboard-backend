import requests
import json
from datetime import datetime
from fastapi import Depends
from src.db.database import get_db
from src.db import cruds


def call_chat_ai(user_input: str, prompt: str = "ヘルプに対する答えをお願いします"):
    """Azure OpenAI Service の API を呼び出す関数

    Args:
        user_input (str): ユーザーからの入力
        prompt (str, optional): LLM への指示内容. Defaults to "ヘルプに対する答えをお願いします".

    Returns:
        str: LLM からの応答
    """

    # API エンドポイント
    chat_api_url = "https://r7m9wx090b.execute-api.us-west-2.amazonaws.com/default/chatgpt"

    # パラメータ
    chat_api_params = {
        "conversation": user_input,
        "instruction": prompt,
    }

    # データをJSON形式に変換
    json_data = json.dumps(chat_api_params)

    # POSTリクエスト
    chat_api_response = requests.post(
        chat_api_url,
        data=json_data,
        headers={"content-Type": "application/json"},
        verify=False)

    # JSONレスポンスを取得
    chat_api_result = chat_api_response.json()

    print(chat_api_result)

    # 戻り値をセット
    return chat_api_result.get("response", "Unknown")


def inquiry_info(db, search_type, order_id):
    """照会情報を取得する関数

    Args:
        db : データベース接続情報
        search_type (str): 照会種別
        order_id : 注文ID

    Returns:
       str: 照会結果
    """

    # 結果格納用変数
    inquiry_result = ""

    #引数(search_type)に応じて分岐処理を実施
    # 質問内容が配達履歴に関するものだった場合(delivery_time)
    if search_type == "delivery_history":
        records = cruds.select_delivery_history(db, limit=5)
        if records is None:
            inquiry_result = "配達履歴はありません"
        else:
            inquiry_result = "直近の配達履歴は下記になります"
            for record in records:
                inquiry_result = inquiry_result + "\n・注文日: " + record.order_date.strftime("%Y-%m-%d %H:%M:%S")
                inquiry_result = inquiry_result + ", 注文ID: " + record.order_id
                inquiry_result = inquiry_result + ", 配達時間: " + record.delivery_time.strftime("%H:%M-%S")

    # 配達時間に関するものだった場合(delivery_history)
    elif search_type == "delivery_time":
        record = cruds.select_delivery_history_by_order_id(db, order_id)
        if record is None:
            inquiry_result = "該当する注文は存在しません"
        else:
            inquiry_result = inquiry_result + "注文ID: " + record.order_id
            inquiry_result = inquiry_result + ", 配達時間: " + record.delivery_time.strftime("%H:%M:%S")
    # それ以外
    else:
        inquiry_result = "Unknown"
    
    # 戻り値をセット
    return inquiry_result
