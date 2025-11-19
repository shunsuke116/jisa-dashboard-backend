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
from sqlalchemy.sql.functions import current_timestamp, func
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
    __tablename__ = "product"

    product_id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        nullable=False,
        comment="商品ID",
    )
    product_name = Column(
        String(50),
        comment="商品名",
    )
    store_name = Column(
        String(50),
        nullable=False,
        comment="店名",
    )
    product_price = Column(
        Integer,
        nullable=False,
        comment="金額",
    )
    product_image = Column(
        LargeBinary,
        nullable=True,
        comment="商品画像",
    )

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


class Review(Base):
    """レビューテーブル - Application課題Lv2で追加"""
    __tablename__ = "review"

    # ============ Application 課題Lv2 編集ここから ============
    # TODO: DB仕様書を参考にして Review クラスのカラムを定義してください
    # 最小限の実装として review_id カラムのみ定義済
    review_id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        nullable=False,
        comment="レビューID",
    )
    product_id = Column(
        Integer,
        nullable=False,
        comment="商品ID",
    )
    user_name = Column(
        String(255),
        nullable=False,
        comment="ユーザ名",
    )
    rating = Column(
        Integer,
        nullable=False,
        comment="評価（1～5）",
    )
    comment = Column(
        Text,
        nullable=True,
        comment="コメント",
    )
    created_at = Column(
        DateTime,
        nullable=False,
        server_default=current_timestamp(),
        comment="投稿日時",
    )
    #LLM使用
    # ============ Application 課題Lv2 編集ここまで ============
