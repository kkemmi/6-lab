import os
import yaml
import logging
from functools import wraps


class FileNotFound(Exception):
    pass


class FileCorrupted(Exception):
    pass


def logged(exception_types, mode="console"):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = logging.getLogger(func.__name__)
            logger.setLevel(logging.ERROR)

            if not logger.handlers:
                if mode == "console":
                    handler = logging.StreamHandler()
                else:
                    handler = logging.FileHandler(
                        "file_log.txt", mode="a", encoding="utf-8"
                    )

                formatter = logging.Formatter(
                    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                )
                handler.setFormatter(formatter)
                logger.addHandler(handler)

            try:
                return func(*args, **kwargs)
            except exception_types as e:
                logger.error(str(e))
                raise

        return wrapper

    return decorator


class FileManager:
    def __init__(self, filepath: str):
        self.filepath = filepath

        # Create file if it does not exist
        if not os.path.exists(self.filepath):
            with open(self.filepath, "w", encoding="utf-8") as f:
                yaml.safe_dump([], f)

    def _validate_data(self, data):

        if not isinstance(data, list):
            return []

        valid_data = []
        for item in data:
            if (
                    isinstance(item, dict)
                    and "id" in item
                    and "text" in item
                    and isinstance(item["id"], int)
                    and isinstance(item["text"], str)
            ):
                valid_data.append(item)

        return valid_data

    @logged((FileCorrupted, FileNotFound), mode="console")
    def read(self):
        if not os.path.exists(self.filepath):
            raise FileNotFound(f"File '{self.filepath}' not found")

        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                return self._validate_data(data)
        except Exception as e:
            raise FileCorrupted(f"Cannot read file '{self.filepath}': {e}")

    @logged(FileCorrupted, mode="file")
    def write(self, data: list):
        try:
            validated_data = self._validate_data(data)
            with open(self.filepath, "w", encoding="utf-8") as f:
                yaml.safe_dump(validated_data, f, allow_unicode=True)
        except Exception as e:
            raise FileCorrupted(f"Cannot write to file '{self.filepath}': {e}")

    @logged(FileCorrupted, mode="file")
    def append(self, text: str):
        try:
            data = self.read()
            new_id = max((item["id"] for item in data), default=0) + 1

            data.append({"id": new_id, "text": text})

            with open(self.filepath, "w", encoding="utf-8") as f:
                yaml.safe_dump(data, f, allow_unicode=True)

        except Exception as e:
            raise FileCorrupted(f"Cannot append to file '{self.filepath}': {e}")


if __name__ == "__main__":
    manager = FileManager("example.yaml")
    manager.append("Exception")
    manager.append("Error")
    print(manager.read())

   
