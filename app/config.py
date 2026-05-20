import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    app_env: str = "dev"
    app_port: int = 8097

    db_host: str = "localhost"
    db_port: int = 5432
    db_user: str = "integrator"
    db_password: str = "integrator123"
    db_name: str = "sensor_data_dev"

    rabbitmq_url: str = "amqp://integrator:integrator123@localhost:5672/"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }

    @property
    def db_config(self) -> dict:
        return {
            "host": self.db_host,
            "port": self.db_port,
            "dbname": self.db_name,
            "user": self.db_user,
            "password": self.db_password,
        }


def get_settings() -> Settings:
    return Settings()