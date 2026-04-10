import logging

def get_logger():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(asctime)s — %(message)s"))
        logger.addHandler(handler)
    return logger