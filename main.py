import os
import yaml
import logging
from functools import wraps


class FileNotFound(Exception):
    pass


class FileCorrupted(Exception):
    pass


def logged(exception_type, mode="console"):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = logging.getLogger(func.__name__)
            logger.setLevel(logging.ERROR)

            if mode == "console":
                handler = logging.StreamHandler()
            else:
                handler = logging.FileHandler("file_log.txt", mode="a", encoding="utf-8")

            formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            handler.setFormatter(formatter)
            logger.handlers = [handler]

            try:
                return func(*args, **kwargs)
            except exception_type as e:
                logger.error(f"{e}")
                raise
        return wrapper
    return decorator


class FileManager:
    def __init__(self, filepath: str):
        self.filepath = filepath

        if not os.path.exists(self.filepath):
            with open(self.filepath, "w", encoding="utf-8") as f:
                yaml.safe_dump([], f)

    @logged(FileCorrupted, mode="console")
    def read(self):
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                return data if isinstance(data, list) else []
        except Exception as e:
            raise FileCorrupted(f"Cannot read file '{self.filepath}': {e}")

    @logged(FileCorrupted, mode="file")
    def write(self, data: list):
        try:
            with open(self.filepath, "w", encoding="utf-8") as f:
                yaml.safe_dump(data, f, allow_unicode=True)
        except Exception as e:
            raise FileCorrupted(f"Cannot write to file '{self.filepath}': {e}")

    @logged(FileCorrupted, mode="file")
    def append(self, text: str):
        try:
            data = self.read()
            new_id = 1 if not data else data[-1]["id"] + 1

            new_record = {"id": new_id, "text": text}
            data.append(new_record)

            with open(self.filepath, "w", encoding="utf-8") as f:
                yaml.safe_dump(data, f, allow_unicode=True)

        except Exception as e:
            raise FileCorrupted(f"Cannot append to file '{self.filepath}': {e}")


if __name__ == "__main__":
    manager = FileManager("example.yaml")
    manager.append("Exception")
    manager.append("Error")
    print(manager.read())
