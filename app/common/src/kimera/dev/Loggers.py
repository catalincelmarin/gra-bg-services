import logging
import os
import sys

level = os.getenv("LOGGER_LEVEL", "INFO")


formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
stream_handler = logging.StreamHandler(sys.stderr)
stream_handler.setLevel(getattr(logging, level))
stream_handler.setFormatter(formatter)


class APILogger:
    logger = logging.getLogger('APILogger')
    logger.setLevel(getattr(logging, level))
    file_handler = logging.FileHandler(f'{"/home/jazzms"}/app/logs/api.log')
    file_handler.setLevel(getattr(logging, level))
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)


class KafkaLogger:
    logger = logging.getLogger('KafkaLogger')
    logger.setLevel(getattr(logging, level))
    file_handler = logging.FileHandler(f'{"/home/jazzms"}/app/logs/kafka.log')
    file_handler.setLevel(getattr(logging, level))
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)


class GPTLogger:
    logger = logging.getLogger('GPTLogger')
    logger.setLevel(getattr(logging, level))
    file_handler = logging.FileHandler(f'{"/home/jazzms"}/app/logs/gpt.log')
    file_handler.setLevel(getattr(logging, level))
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    stream_handler = logging.StreamHandler(sys.stderr)
    stream_handler.setLevel(getattr(logging, level))
    stream_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)


class ConsoleLogger:
    logger = logging.getLogger('ConsoleLogger')
    logger.setLevel(getattr(logging, level))
    file_handler = logging.FileHandler(f'{"/home/jazzms"}/app/logs/console.log')
    file_handler.setLevel(getattr(logging, level))
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)


class TaskLogger:
    logger = logging.getLogger('TaskLogger')
    logger.setLevel(getattr(logging, level))
    file_handler = logging.FileHandler(f'{"/home/jazzms"}/app/logs/celery.log')
    file_handler.setLevel(getattr(logging, level))
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)


sys.stdout = sys.__stdout__
