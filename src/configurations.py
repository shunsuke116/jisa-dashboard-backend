import os
import boto3
from logging import getLogger
from dotenv import load_dotenv

load_dotenv()

logger = getLogger(__name__)


class APIConfigurations:
    title = "JISA Dashboard Backend"
    description = "JISA Dashboard Backend API Server"
    version = 1.0


logger.info(f"{APIConfigurations.__name__}: {APIConfigurations.__dict__}")


class DBConfigurations:
    mysql_username = None
    mysql_password = None
    mysql_host = None
    mysql_dbname = "jisa"
    sql_alchemy_database_url = "sqlite:///test_db.sqlite3"
    connect_args = {"check_same_thread": False}
    
    is_dev = os.getenv("ENV_TYPE") == "dev"
    logger.info(f"ENV_TYPE: {os.getenv('ENV_TYPE')}")
    
    # 本番環境ではAWS System Manager Parameter StoreよりDB情報を取得
    if not is_dev:
        
        ssm = boto3.client("ssm", region_name="us-west-2")
        mysql_username = ssm.get_parameter(
            Name="delivery-order-db-user", WithDecryption=False
        )["Parameter"]["Value"]
        mysql_password = ssm.get_parameter(
            Name="delivery-order-db-password", WithDecryption=False
        )["Parameter"]["Value"]
        mysql_host = ssm.get_parameter(Name="delivery-order-db", WithDecryption=False)[
            "Parameter"
        ]["Value"]
        # mysql_port =
        sql_alchemy_database_url = (
            f"mysql://{mysql_username}:{mysql_password}@{mysql_host}/{mysql_dbname}"
        )
        connect_args = {}