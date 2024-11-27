import os

from dotenv import load_dotenv


def load_env():
    ENV = os.getenv("ENV", "development")

    if ENV == "development":
        load_dotenv()
