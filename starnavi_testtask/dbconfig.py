from configparser import ConfigParser
from pathlib import Path


config = ConfigParser()
config.read(Path(__file__).parent.parent / "db.env")

POSTGRES_USER = config.get("POSTGRES", "POSTGRES_USER")
POSTGRES_DB = config.get("POSTGRES", "POSTGRES_DB")
POSTGRES_PASSWORD = config.get("POSTGRES", "POSTGRES_PASSWORD")
POSTGRES_PORT = config.get("POSTGRES", "POSTGRES_PORT")
POSTGRES_HOST = config.get("POSTGRES", "POSTGRES_HOST")


__all__ = [
    "POSTGRES_USER",
    "POSTGRES_PASSWORD",
    "POSTGRES_HOST",
    "POSTGRES_PORT",
    "POSTGRES_DB",
]