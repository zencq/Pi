import logging


# decorator to wrap an entire method. useful as exceptions raised in mod methods will not be visible otherwise
def try_except(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.error(e)

    return wrapper
