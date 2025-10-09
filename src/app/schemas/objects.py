import datetime

from typing import Any

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
# ------Application 課題Lv2 編集ここから------
    hoge: str #この項目は削除して修正すること
# ------Application 課題Lv2 編集ここまで------

class ProductInfo(BaseModel):
# ------Application 課題Lv2 編集ここから------
    hoge: str #この項目は削除して修正すること
# ------Application 課題Lv2 編集ここまで------

class ProductImage(BaseModel):
# ------Application 課題Lv2 編集ここから------
    hoge: str #この項目は削除して修正すること
# ------Application 課題Lv2 編集ここまで------

class Order(BaseModel):
    id: int
    product_id: int
    order_num: int

# ------AI Coding 課題Lv1 編集ここから------

# ------AI Coding 課題Lv1 編集ここまで------
