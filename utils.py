import os

from dotenv import load_dotenv
from loguru import logger


def parse_env(key):
    """Parse .env file."""
    load_dotenv()

    if key == 'admin_id':
        logger.success(f'Config file was parsed for {key}.')
        admins = os.getenv(key).split(',')
        return [int(item) for item in admins]

    logger.success(f'Config file was parsed for {key}.')
    return os.getenv(key)
