# ---------------編集ここから---------------
# 必要なimportがあれば追加してよい
import shutil
import datetime
from typing import List, Optional
from pathlib import Path
import time
import csv
import requests
import json
import base64
import os        
import boto3     

from fastapi import (
    APIRouter,
    Depends,
    Query,
    Path,
    UploadFile,
    File,
    HTTPException,
    Response,
    BackgroundTasks,
)
from sqlalchemy.orm import Session
from src.app.schemas.base import ResponseModel
from src.app.schemas.objects import (
    DeliveryHistoryDisplayed,
    TotalCO2AmountSummary,
    TownCoordinate,
    ConversationDisplayed,
    Product,
    ProductInfo,
    ProductImage,
    Order,
    ReviewCreate,
    ReviewDisplayed,
)
from src.app.exceptions.db_error import SqlExecutionException
from src.configurations import LambdaConfigurations
from src.db import cruds
from src.db.database import get_db
from src.utils.chat import (
    call_chat_ai,
    inquiry_info,
)
from src.db import initialize
from src.db.database import engine

import logging
logger = logging.getLogger(__name__)
# ---------------編集ここまで---------------

router = APIRouter()


@router.get(
    "/delivery-history",
    response_model=ResponseModel[List[DeliveryHistoryDisplayed]],
)
def search_delivery_history(db: Session = Depends(get_db), limit: int = None):
    """delivery historyテーブル内のデータを直近からlimitで指定された件数だけjson形式で出力。"""
    # 配達履歴データ取得
    data = cruds.select_delivery_history(db=db, limit=limit)
    if data is None:
        raise SqlExecutionException()

    # レスポンスデータ作成
    response = ResponseModel[List[DeliveryHistoryDisplayed]](
        result_code="N001", result_msg="正常終了", result_content=data)

    return response


@router.get(
    "/total-co2-amount/summary",
    response_model=ResponseModel[TotalCO2AmountSummary],
)
def get_CO2_amount_summary(db: Session = Depends(get_db)):
    """CO2排出量の現在時刻を基準にした日次、週次(月曜～日曜)、月次のsummaryをjson形式で出力。"""
    # 各期間のCO2排出量格納用
    today_total = 0
    yesterday_total = 0
    this_week_total = 0
    last_week_total = 0
    this_month_total = 0
    last_month_total = 0

    # 各期間の区切りの時刻を取得
    # 現在時刻(JST)を取得(今日、今週、今月の終了)
    tz_jst = datetime.timezone(datetime.timedelta(hours=9))
    current = datetime.datetime.now(tz_jst)

    # 今日の開始(兼前日の終了)
    today_start = datetime.datetime(current.year,
                                    current.month,
                                    current.day,
                                    tzinfo=tz_jst)

    # 前日の開始
    yesterday_start = today_start - datetime.timedelta(days=1)

    # 今週の開始(兼前週の終了)
    today_weekday = today_start.date().weekday()
    this_week_start = today_start - datetime.timedelta(days=today_weekday)

    # 前週の開始
    last_week_start = this_week_start - datetime.timedelta(days=7)

    # 今月の開始(兼前月の終了)
    this_month_start = datetime.datetime(current.year,
                                         current.month,
                                         1,
                                         tzinfo=tz_jst)

    # 前月の開始
    last_month_year = current.year - 1 if current.month == 1 else current.year
    last_month = 12 if current.month == 1 else current.month - 1
    last_month_start = datetime.datetime(last_month_year,
                                         last_month,
                                         1,
                                         tzinfo=tz_jst)

    # store_site_id に 0～99 をセットし100回取得する
    for store_site_id in range(100):

        # 先月頭から現在までの配達履歴リスト取得
        target_delivery_history_list = cruds.select_delivery_history_by_period(
            db, last_month_start, current, store_site_id)
        if target_delivery_history_list is None:
            raise SqlExecutionException()

        # 各期間のCO2排出量を算出
        for delivery_history in target_delivery_history_list:
            order_date_with_tz = delivery_history.order_date.replace(tzinfo=tz_jst)
            # 日次累計の更新
            if order_date_with_tz >= today_start:
                today_total += delivery_history.CO2_amount
            elif order_date_with_tz >= yesterday_start:
                yesterday_total += delivery_history.CO2_amount

            # 週次累計の更新
            if order_date_with_tz >= this_week_start:
                this_week_total += delivery_history.CO2_amount
            elif order_date_with_tz >= last_week_start:
                last_week_total += delivery_history.CO2_amount

            # 月次累計の更新
            if order_date_with_tz >= this_month_start:
                this_month_total += delivery_history.CO2_amount
            elif order_date_with_tz >= last_month_start:
                last_month_total += delivery_history.CO2_amount

    # CO2排出量サマリデータ作成
    result = TotalCO2AmountSummary(
        today_total=today_total,
        yesterday_total=yesterday_total,
        this_week_total=this_week_total,
        last_week_total=last_week_total,
        this_month_total=this_month_total,
        last_month_total=last_month_total,
    )

    # レスポンスデータ作成
    response = ResponseModel[TotalCO2AmountSummary](
        result_code="N001",
        result_msg="正常終了",
        result_content=result,
    )

    return response


@router.get("/get-path-coordinate",
            response_model=ResponseModel[List[TownCoordinate]])
def get_path_coordinate_by_order_id(db: Session = Depends(get_db), order_id: str = None):

    # 経由点の緯度経度情報のリスト
    path_coordinate = []

    # 対象データの経路ID取得
    records = cruds.select_path_id_by_order_id(db=db, order_id=order_id)
    if records is None:
        raise SqlExecutionException()
    town_ids_in_route = records[0]["items"]

    # 各地点の緯度経度情報のcsv取得
    with open("data/towns.csv", encoding="utf-8-sig") as towns:
        reader = csv.DictReader(towns)
        towns = [row for row in reader]

    # 経路IDから経由点の緯度経度情報へ変換
    for town_id in town_ids_in_route:
        town = list(filter(lambda row: int(row["town_id"]) == town_id,
                           towns))[0]
        path_coordinate.append(
            TownCoordinate(
                town_id=town_id,
                latitude=float(town["lat"]),
                longitude=float(town["lon"]),
            ))

    # レスポンスデータ作成
    response = ResponseModel[List[TownCoordinate]](
        result_code="N001",
        result_msg="正常終了",
        result_content=path_coordinate,
    )

    return response


@router.get(
    "/conversation",
    response_model=ResponseModel[ConversationDisplayed],
)
def conversation(user_input: str, db: Session = Depends(get_db)):

    # 分類API エンドポイント
    category_api_url = "https://w50b7i5tre.execute-api.us-west-2.amazonaws.com/default/intent-classification-api"

    # パラメータ
    category_api_params = {
        "conversation": user_input,
    }

    # GETリクエスト
    category_api_response = requests.get(category_api_url,
                                         params=category_api_params,
                                         verify=False).json()

    classification = category_api_response.get("classification", "Unknown")

    if classification == "inquiry":
        # 配達履歴紹介(delivery_history)、配達時間照会(delivery_time)
        conversation_result = inquiry_info(db, category_api_response["search_type"], category_api_response["order_id"])
    # 質疑応答FAQ(question)
    elif classification == "question":
        conversation_result = call_chat_ai(user_input)
    # クレーム(complaint)
    elif classification == "complaint":
        conversation_result = category_api_response["draft_response"]
    # その他(other)
    elif classification == "other":
        conversation_result = category_api_response["draft_response"]
    # それ以外
    else:
        conversation_result = "もう一度質問の入力をお願いします。"

    # ~~~~~~~~~~~~~~~~~~~~~

    # 応答用データ作成
    response_data = ConversationDisplayed(input_msg=user_input,
                                          response=conversation_result)

    # レスポンスデータ作成
    response = ResponseModel[ConversationDisplayed](
        result_code="N001", result_msg="正常終了", result_content=response_data)

    return response


@router.get(
    "/get-product-list/init",
    response_model=ResponseModel[str],
)
def get_product_list_init(db: Session = Depends(get_db)):
    #for sqlite initialization
    initialize.create_tables(engine=engine, checkfirst=True)
    initialize.initialize_table(engine, checkfirst=True)
    result = cruds.initialize_table(db=db)
    result_loacal = cruds.create_product_item_initialize(db=db)
    response_message = result
    
    if result is None:
        raise SqlExecutionException()

    # レスポンスデータ作成
    response = ResponseModel[str](
        result_code="N001",
        result_msg="正常終了",
        result_content=response_message,
    )

    return response


@router.get(
    "/get-product-list/all",
    response_model=ResponseModel[List[Product]],
)
def get_product_list_all(db: Session = Depends(get_db)):
    # DBから商品データを取得
    product_list_result = cruds.select_product_all(db=db)
    if product_list_result is None:
        raise SqlExecutionException()
    
    # 画像データをbase64にエンコード
    product_base64_image_result = []
    for product in product_list_result:
        product_base64_image_result.append(Product(
            product_id = product["product_id"],
            product_name = product["product_name"],
            store_name = product["store_name"],
            product_price = product["product_price"],
            product_image = base64.b64encode(product["product_image"])
        ))
    
    # レスポンスデータ作成
    response = ResponseModel[List[Product]](
        result_code="N001",
        result_msg="正常終了",
        result_content=product_base64_image_result,
    )
    
    return response


@router.get(
    "/get-product-list/info",
    response_model=ResponseModel[List[ProductInfo]],
)
def get_product_list_info(db: Session = Depends(get_db), offset: int = 0, limit: int = 100):
    # DBから商品データを取得
    product_info_list_result = cruds.select_product_info(db=db, offset=offset, limit=limit)
    if product_info_list_result is None:
        raise SqlExecutionException()
    
    # レスポンスデータ作成
    response = ResponseModel[List[ProductInfo]](
        result_code="N001",
        result_msg="正常終了",
        result_content=product_info_list_result,
    )
    
    return response


@router.get(
    "/get-product-list/image",
    response_model=ResponseModel[List[ProductImage]],
)
def get_product_list_image(product_ids: List[int]= Query(...), db: Session = Depends(get_db)):
    # DBから画像データを取得
    product_image_result = cruds.select_product_image_by_id(product_ids=product_ids, db=db)
    if product_image_result is None:
        raise SqlExecutionException()
    
    # 画像データをbase64にエンコード
    product_base64_image_result = []
    for product in product_image_result:
        product_base64_image_result.append(ProductImage(
            product_id = product["product_id"],
            product_image = base64.b64encode(product["product_image"])
        ))
    
    # レスポンスデータ作成
    response = ResponseModel[List[ProductImage]](
        result_code="N001",
        result_msg="正常終了",
        result_content=product_base64_image_result,
    )
    
    return response


@router.get(
    "/order",
    response_model=ResponseModel[str],
)
def order(background_tasks: BackgroundTasks, db: Session = Depends(get_db), product_id: int = 0, order_num: int = 0):
    # 業務処理を実行 
    background_tasks.add_task(create_order_item_in_background, db, product_id, order_num)

    # レスポンスデータ作成
    response = ResponseModel[str](
        result_code="N001",
        result_msg="正常終了",
        result_content="注文を受け付けました。"
    )

    return response

# 関数は適宜追加可能
def create_order_item_in_background(db: Session, product_id: int, order_num: int):
    cruds.create_order_item(db=db, product_id=product_id, order_num=order_num)


@router.get(
    "/get-order-all",
    response_model=ResponseModel[List[Order]],
)
def get_order_all(db: Session = Depends(get_db)):
    #DBからデータを取得
    product_list_result = cruds.select_order_all(db=db)
    if product_list_result is None:
        raise SqlExecutionException()
    
    # レスポンスデータ作成
    response = ResponseModel[List[Order]](
        result_code="N001",
        result_msg="正常終了",
        result_content=product_list_result,
    )

    return response


# =============== Application 課題Lv2: レビュー関連のAPI ===============

@router.post(
    "/review/add",
    response_model=ResponseModel[int],
)
def post_review_add(review: ReviewCreate, db: Session = Depends(get_db)):
    """
    レビューを追加する。成功時は result_content に review_id を返却する。
    """
    logger.info(f"POST /review/add called. product_id={review.product_id}, user_name={review.user_name}")
    
    # ============ Application 課題Lv2 編集ここから ============
    # TODO: cruds.create_review を呼び出してレビューを登録してください
    review_id = cruds.create_review(
        
    )
    
    if review_id is None:
        raise SqlExecutionException()
    
    # TODO: レスポンスデータを作成してください
    response = ResponseModel[int](
        
    )
    # ============ Application 課題Lv2 編集ここまで ============
    
    logger.info(f"POST /review/add success. review_id={review_id}")
    return response


@router.get(
    "/review/list",
    response_model=ResponseModel[List[ReviewDisplayed]],
)
def get_review_list(
    product_id: int = Query(..., description="商品ID"),
    limit: Optional[int] = Query(None, description="取得件数上限"),
    offset: Optional[int] = Query(None, description="取得開始位置"),
    db: Session = Depends(get_db)
):
    """
    指定商品IDのレビュー一覧を取得する。
    """
    logger.info(f"GET /review/list called. product_id={product_id}, limit={limit}, offset={offset}")
    
    # ============ Application 課題Lv2 編集ここから ============
    # TODO: cruds.select_reviews_by_product を呼び出してレビュー一覧を取得してください
    reviews = cruds.select_reviews_by_product(
        
    )

    if reviews is None:
        raise SqlExecutionException()

    # TODO: レスポンスデータを作成してください
    response = ResponseModel[List[ReviewDisplayed]](
        
    )
    # ============ Application 課題Lv2 編集ここまで ============
    
    logger.info(f"GET /review/list success. count={len(reviews)}")
    return response

# =============== レビュー関連のAPIここまで ===============


# =============== Application 課題Lv3: AI要約API ===============

@router.post(
    "/ai/review-summary",
    response_model=ResponseModel[dict],
)
async def get_ai_review_summary(
    product_id: int = Query(..., description="商品ID"),
    db: Session = Depends(get_db)
):
    """
    指定商品のレビューをAI要約する。
    
    処理フロー:
    1. DBから対象商品のレビューを取得
    2. レビューデータをプロンプト形式に整形
    3. 準備済みのLambda関数（Bedrock連携）を呼び出す
    4. AI要約結果を返却
    """
    logger.info(f"POST /ai/review-summary called. product_id={product_id}")
    
    try:
        # ============ Application 課題Lv3 編集ここから ============
        # Step1: レビューデータをDBから取得
        # TODO: cruds.select_reviews_by_product でレビューを取得してください（最大50件）
        reviews = cruds.select_reviews_by_product(
            )
        # ============ Application 課題Lv3 編集ここまで ============
        if reviews is None:
            raise SqlExecutionException()
        
        if len(reviews) == 0:
            logger.info("No reviews found for this product")
        # ============ Application 課題Lv3 編集ここから ============
            # TODO: レビューが0件の場合のレスポンスを作成してください
            response = ResponseModel[dict](
                
            )
        # ============ Application 課題Lv3 編集ここまで ============
            logger.info("No reviews found for this product")
            return response
        
        # Step2: プロンプトを生成
        # TODO: create_review_summary_prompt を実装してください
        prompt = create_review_summary_prompt(reviews, product_id)

        # Step3: Lambda関数を呼び出す
        lambda_arn = LambdaConfigurations.lambda_function_arn

        if not lambda_arn:
            raise HTTPException(
                status_code=500,
                detail="Lambda関数のARNが設定されていません"
            )
        
        lambda_client = boto3.client('lambda', region_name='us-west-2')
        
        payload = {
            "body": json.dumps({
                "prompt": prompt
            })
        }
        
        lambda_response = lambda_client.invoke(
            FunctionName=lambda_arn,
            InvocationType='RequestResponse',
            Payload=json.dumps(payload)
        )
        
        # レスポンス解析
        response_payload = json.loads(lambda_response['Payload'].read())
        logger.info(f"Lambda response: {response_payload}")
        
        if 'body' in response_payload:
            body = json.loads(response_payload['body'])
            if body.get('result_code') == 'N001':
                summary = body['result_content']['summary']
        # ============ Application 課題Lv3 編集ここから ============                
                # TODO: 成功時のレスポンスを作成してください
                response = ResponseModel[dict](
                    
                )
        # ============ Application 課題Lv3 編集ここまで ============ 
                logger.info(f"AI summary generated successfully. review_count={len(reviews)}")
                return response
            else:
                raise HTTPException(
                    status_code=500,
                    detail=f"Lambda関数がエラーを返しました: {body.get('error_message')}"
                )
        else:
            raise HTTPException(
                status_code=500,
                detail="Lambda関数のレスポンス形式が不正です"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"AI review summary error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"AI要約の生成に失敗しました: {str(e)}"
        )


def create_review_summary_prompt(reviews, product_id: int) -> str:
    """
    レビューデータからAI要約用のプロンプトを生成する。
    
    Args:
        reviews: レビューデータのリスト
        product_id: 商品ID
        
    Returns:
        str: プロンプト文字列
    """
    # ============ Application 課題Lv3 編集ここから ============
    # TODO: レビュー情報を整形してください（AI向けプロンプト用に）
    
    # TODO: 生成AIに送る適切なプロンプトを作成してください
    prompt = ""
    
    # ============ Application 課題Lv3 編集ここまで ============
    
    return prompt

# =============== AI要約APIここまで ===============
