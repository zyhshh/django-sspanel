import os

from configs.default import *  # noqa
from configs.default import DATABASES

DEBUG = False

DATABASES["default"].update(
    {
        "PASSWORD": os.getenv("MYSQL_PASSWORD", "yourpass"),
        "HOST": os.getenv("MYSQL_HOST", "127.0.0.1"),
        "USER": os.getenv("MYSQL_USER", "root"),
    }
)
