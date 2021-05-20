import config as cfg


def get_telegram_token():
    return cfg.TELEGRAM_TOKEN


def get_telegram_group_id():
    return cfg.TELEGRAM_GROUP_ID


def get_connection_string() -> str:
    """Return Postgre connection string."""
    return "postgresql://{0}:{1}@{2}:{3}/{4}".format(
        cfg.POSTGRE_USER,
        cfg.POSTGRE_PASS,
        cfg.POSTGRE_HOST,
        cfg.POSTGRE_PORT,
        cfg.POSTGRE_DATABASE
    )


def get_twitter_data():
    """Return twitter api data."""
    return cfg.CONSUMER_KEY, cfg.CONSUMER_SECRET, cfg.ACCESS_KEY, cfg.ACCESS_SECRET


def get_twitter_user():
    """Return Twitter user."""
    return cfg.TWITTER_USER
