from os import getenv

from dotenv import load_dotenv


load_dotenv(override=True)


def getenv_or_raise(var_name: str) -> str:
    value = getenv(var_name)
    if value is None:
        raise EnvironmentError(f'Environment variable "{var_name}" is not set.')
    return value


TOKEN = getenv_or_raise("BOT_TOKEN")
SCRAPER_URL = getenv_or_raise("SCRAPER_URL")

MASTER_ID: int = int(getenv_or_raise("MASTER_ID"))
ADMINS: set[int] = set(
    [
        int(i)
        for i in (getenv("ADMINS") or "").strip().replace(" ", "").split(",")
        if i != ""
    ]
    + [MASTER_ID]
)

WEBHOOK_URL: str = getenv("WEBHOOK_URL")
