import os
import hdbcli.dbapi as dbapi
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), ".env")

load_dotenv(dotenv_path, override=True)


def con():
    try:
        conn = dbapi.connect(
            address=os.getenv("DB_ADDRESS"),
            port=int(os.getenv("DB_PORT")),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            databaseName=os.getenv("DB_NAME"),
        )
        return conn

    except Exception as e:
        raise Exception(f"Erro HANA: {e}")
