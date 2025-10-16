import datetime

from typing import Any, Optional

from pydantic import BaseModel


class DeliveryHistoryDisplayed(BaseModel):
    order_date: datetime.datetime
    order_id: str
    store_site_id: int
    delivery_target_id: int
    # path_id: Any  # Level1時点であり、Level2で削除
    CO2_amount: float
    delivery_time: datetime.time

    class Config:
        orm_mode = True


class TotalCO2AmountSummary(BaseModel):
    today_total: float
    yesterday_total: float
    this_week_total: float
    last_week_total: float
    this_month_total: float
    last_month_total: float


class TownCoordinate(BaseModel):
    town_id: int
    latitude: float
    longitude: float

class ConversationDisplayed(BaseModel):
    input_msg: str
    response: str

class Product(BaseModel):
    product_id: int
    product_name: str
    store_name: str
    product_price: int
    product_image: str

class ProductInfo(BaseModel):
    product_id: int
    product_name: str
    store_name: str
    product_price: int

class ProductImage(BaseModel):
    product_id: int
    product_image: str

class Order(BaseModel):
    id: int
    product_id: int
    order_num: int


# ============ Application 課題Lv2: レビュー関連スキーマ ============

class ReviewCreate(BaseModel):
    """レビュー投稿用スキーマ"""
    # ============ Application 課題Lv2 編集ここから ============
    # TODO: API仕様書を参考にして ReviewCreate スキーマを定義してください
    pass
    # ============ Application 課題Lv2 編集ここまで ============


class ReviewDisplayed(BaseModel):
    """レビュー表示用スキーマ"""
    # ============ Application 課題Lv2 編集ここから ============
    # TODO: API仕様書を参考にして ReviewDisplayed スキーマを定義してください
    pass
    # ============ Application 課題Lv2 編集ここまで ============

# ============ レビュー関連スキーマここまで ============
