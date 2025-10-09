from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Float,
    String,
    Text,
    Time,
    JSON,
)
from sqlalchemy.orm import relation, relationship
from sqlalchemy.sql.functions import current_timestamp
from sqlalchemy.sql.sqltypes import Boolean
from sqlalchemy.types import JSON, LargeBinary
from src.db.database import Base


class DeliveryHistory(Base):
    __tablename__ = "delivery_history"

    order_date = Column(
        DateTime,
        nullable=False,
        comment="注文時刻",
    )
    order_id = Column(
        String(13),
        primary_key=True,
        comment="注文ID",
    )
    store_site_id = Column(
        Integer,
        nullable=False,
        comment="店舗地点ID",
    )
    delivery_target_id = Column(
        Integer,
        nullable=False,
        comment="配達先地点ID",
    )
    path_id = Column(
        JSON,
        nullable=True,
        comment="経路ID",
    )
    CO2_amount = Column(
        Float,
        nullable=False,
        comment="CO2排出量",
    )
    delivery_time = Column(
        Time,
        nullable=False,
        comment="配達時間",
    )

class Product(Base):
# ------Application 課題Lv2 編集ここから------
    # 下記は削除して修正すること
    __tablename__ = "hoge"
    
    hoge = Column(
        String(10),
        primary_key=True,
        comment="hoge",
    )
# ------Application 課題Lv2 編集ここまで------

class Orders(Base):
    __tablename__ = "orders"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        nullable=False,
        comment="注文ID",
    )
    product_id = Column(
        Integer,
        comment="商品ID",
    )
    order_num = Column(
        Integer,
        comment="個数",
    )

# ------AI Coding 課題Lv1 編集ここから------

# ------AI Coding 課題Lv1 編集ここまで------
