from re import I
import uuid
import time
import datetime
from typing import Dict, List, Optional
from fastapi import Query

from sqlalchemy import and_
from sqlalchemy.orm import Session
from sqlalchemy.sql import func, desc
from src.app.schemas.objects import DeliveryHistoryDisplayed
from src.db.models import DeliveryHistory, Product, Orders, Review

from src.db import initialize
from src.db.database import engine

import logging
logger = logging.getLogger(__name__)
fh = logging.FileHandler(filename='log/uvicorn_error.log', encoding='utf-8', mode='a')
fmt = logging.Formatter(fmt='[%(asctime)s] [%(levelname)s] [%(process)d] [%(name)s] [%(funcName)s] [%(lineno)d] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
fh.setLevel(logging.DEBUG)
fh.setFormatter(fmt)
logger.addHandler(fh)


def select_delivery_history(
    db: Session, limit: int = None
) -> List[DeliveryHistoryDisplayed]:
    logger.debug("select_delivery_history start.[limit=" + str(limit) +"]")
    result=None
    for i in range(5): #最大5回繰り返す
        try:
            search_query = (
                db.query(
                    DeliveryHistory.order_date,
                    DeliveryHistory.order_id,
                    DeliveryHistory.store_site_id,
                    DeliveryHistory.delivery_target_id,
                    DeliveryHistory.CO2_amount,
                    DeliveryHistory.delivery_time,
                )
                .filter(DeliveryHistory.order_date >= '2022-01-01')
                .order_by(desc(DeliveryHistory.order_date))
            )

            if limit is not None:
                search_query = search_query.limit(limit)

            result = search_query.all()
        except RuntimeError as e:
            logger.error("select_delivery_historyにて" + str(i+1) + "回目のRuntimeErrorが発生中です: %s", e)
            time.sleep(1) # 1秒待機してリトライ
        except Exception as e:
            logger.error("select_delivery_historyにて" + str(i+1) + "回目のExceptionが発生中です: %s", e)
            time.sleep(1) # 1秒待機してリトライ
        else:
            break
    logger.debug("select_delivery_history end.[limit=" + str(limit) +"]")
    return result


def select_delivery_history_by_period(
    db: Session, start: datetime.datetime, end: datetime.datetime, store_site_id: int = None
) -> List[DeliveryHistory]:
    logger.debug("select_delivery_history_by_period start.")
    result=None
    for i in range(5): #最大5回繰り返す
        try:
            search_query = (
                db.query(
                    DeliveryHistory.order_date,
                    DeliveryHistory.CO2_amount,
                )
                .filter(DeliveryHistory.order_date >= start)
                .filter(DeliveryHistory.order_date < end)
            )

            if store_site_id is not None:
                search_query = search_query.filter(DeliveryHistory.store_site_id == store_site_id)

            result = search_query.all()
        except RuntimeError as e:
            logger.error("select_delivery_history_by_periodにて" + str(i+1) + "回目のRuntimeErrorが発生中です: %s", e)
            time.sleep(1) # 1秒待機してリトライ
        except Exception as e:
            logger.error("select_delivery_history_by_periodにて" + str(i+1) + "回目のExceptionが発生中です: %s", e)
            time.sleep(1) # 1秒待機してリトライ
        else:
            break
    logger.debug("select_delivery_history_by_period end.")
    return result   


def select_path_id_by_order_id(db: Session, order_id: str):
    logger.debug("select_path_id_by_order_id start.[order_id=" + order_id +"]")
    result=None
    for i in range(5): #最大5回繰り返す
        try:
            result = (
                db.query(DeliveryHistory.path_id)
                .filter(DeliveryHistory.order_id == order_id)
                .first()
            )
        except RuntimeError as e:
            logger.error("select_path_id_by_order_idにて" + str(i+1) + "回目のRuntimeErrorが発生中です: %s", e)
            time.sleep(1) # 1秒待機してリトライ
        except Exception as e:
            logger.error("select_path_id_by_order_idにて" + str(i+1) + "回目のExceptionが発生中です: %s", e)
            time.sleep(1) # 1秒待機してリトライ
        else:
            break
    logger.debug("select_path_id_by_order_id end.[order_id=" + order_id +"]")
    return result


def select_delivery_history_by_order_id(db: Session, order_id: str):
    try:
        result = (
            db.query(
                DeliveryHistory.order_date,
                DeliveryHistory.order_id,
                DeliveryHistory.store_site_id,
                DeliveryHistory.delivery_target_id,
                DeliveryHistory.CO2_amount,
                DeliveryHistory.delivery_time,
            )
            .filter(DeliveryHistory.order_id == order_id)
            .first()
        )

    except Exception as e:
        print(e)
        return None

    return result


def select_product_all(db: Session):
    try:
        result = (
            db.query(
                Product.product_id,
                Product.product_name,
                Product.store_name,
                Product.product_price,
                Product.product_image,
            )
            .all()
        )
    except Exception as e:
        logger.error("select_product_all error: %s", e)
        return None
    
    return result


def select_product_info(db: Session, offset: int, limit: int):
    try:
        query = db.query(
            Product.product_id,
            Product.product_name,
            Product.store_name,
            Product.product_price,
        )
        
        if offset is not None:
            query = query.offset(offset)
        if limit is not None:
            query = query.limit(limit)
            
        result = query.all()
        
    except Exception as e:
        logger.error("select_product_info error: %s", e)
        return None
    
    return result


def select_product_image_by_id(db: Session, product_ids: List[int]):
    try:
        result = (
            db.query(
                Product.product_id,
                Product.product_image,
            )
            .filter(Product.product_id.in_(product_ids))
            .all()
        )
    except Exception as e:
        logger.error("select_product_image_by_id error: %s", e)
        return None
    
    return result


def create_order_item(db: Session, product_id: int, order_num: int):
    try:
        db.begin()
        db.query(Orders).delete()
        time.sleep(10)
        db.query(Orders).delete()
        db.add(Orders(product_id=product_id, order_num=order_num))
        db.commit()

    except Exception as e:
        print(e)
        return None
    
def select_order_all(db: Session):
    try:
        result = (
            db.query(
                Orders.id,
                Orders.product_id,
                Orders.order_num,
            ).order_by(Orders.id)
            .all()
        )

    except Exception as e:
        print(e)
        return None
    
    return result


# ============ Application 課題Lv2: レビュー関連のCRUD処理 ============

def create_review(db: Session, product_id: int, user_name: str, rating: int, comment: Optional[str] = None):
    """
    レビューをDBに登録し、作成された review_id を返却する。
    
    Args:
        db: データベースセッション
        product_id: 商品ID
        user_name: ユーザー名
        rating: 評価（1-5）
        comment: コメント（任意）
        
    Returns:
        int: 作成されたレビューID（成功時） / None（失敗時）
    """
    logger.debug(f"create_review start. [product_id={product_id}, user_name={user_name}, rating={rating}]")
    
    try:
        # ============ Application 課題Lv2 編集ここから ============
        # TODO: Reviewインスタンスを作成してください
        review = Review(
        )
        pass
        # ============ Application 課題Lv2 編集ここまで ============
        
        db.add(review)
        db.commit()
        db.refresh(review)
        
        logger.debug(f"create_review end. [review_id={review.review_id}]")
        return review.review_id
        
    except Exception as e:
        logger.error(f"create_review error: {e}")
        db.rollback()
        return None


def select_reviews_by_product(db: Session, product_id: int, limit: Optional[int] = None, offset: Optional[int] = None):
    """
    指定商品IDのレビュー一覧を取得する。
    
    Args:
        db: データベースセッション
        product_id: 商品ID
        limit: 取得件数上限（任意）
        offset: 取得開始位置（任意）
        
    Returns:
        List: レビューのリスト（成功時） / None（失敗時）
    """
    logger.debug(f"select_reviews_by_product start. [product_id={product_id}, limit={limit}, offset={offset}]")
    
    try:
        # ============ Application 課題Lv2 編集ここから ============
        # TODO: 指定商品IDのレビュー一覧を取得するクエリを作成してください
        query = db.query(
        )
        pass
        # ============ Application 課題Lv2 編集ここまで ============
        
        query = query.filter(Review.product_id == product_id)
        query = query.order_by(desc(Review.created_at))
        
        if offset is not None:
            query = query.offset(offset)
        if limit is not None:
            query = query.limit(limit)
        
        result = query.all()
        
        logger.debug(f"select_reviews_by_product end. [count={len(result)}]")
        return result
        
    except Exception as e:
        logger.error(f"select_reviews_by_product error: {e}")
        return None

# ============ レビュー関連のCRUD処理ここまで ============