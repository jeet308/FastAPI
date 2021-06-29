import logging
import os
import socket
import uuid
from logging.handlers import TimedRotatingFileHandler

project_root_path = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(project_root_path, "Logs")

if not os.path.isdir(data_path):
    os.mkdir(data_path)


class GetLogger:

    request_id = uuid.uuid4()
    system_name = socket.gethostname()
    project_name = "FastAPI"
    end_point = "[test]"
    form = f"%(asctime)s.%(msecs)03d — %(levelname)-8s — {system_name} — {project_name} — {end_point} — {request_id} — %(filename)s:%(lineno)-3d — %(message)s"

    def get_logger(self):
        logger = logging.getLogger("frs_labs")
        logger.propagate = False
        logger.setLevel(logging.DEBUG)
        # logger.addHandler(self.get_stream_handler())
        logger.addHandler(self.get_file_handler())
        return logger

    def get_file_handler(self):
        logfile = f"Logs/{self.system_name }.log"
        # logfile = self.system_name + ".log"
        file_handler = TimedRotatingFileHandler(logfile, when="midnight", interval=1)
        file_handler.setLevel(logging.DEBUG)
        formatter = self.form
        logFormatter = logging.Formatter(formatter)
        file_handler.setFormatter(logFormatter)
        file_handler.suffix = "%d-%m-%Y-%H-%M-%S"
        file_handler.addFilter(SystemLogFilter())
        return file_handler

    def get_stream_handler(self):
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.DEBUG)
        formatter = self.form
        logFormatter = logging.Formatter(formatter)
        stream_handler.setFormatter(logFormatter)
        stream_handler.addFilter(SystemLogFilter())
        return stream_handler


class SystemLogFilter(logging.Filter):
    def __init__(self):
        self.project_name = "FastAPI"
        if "CONTAINER_NAME" in os.environ:
            self.system_name = os.environ["CONTAINER_NAME"]
        else:
            self.system_name = socket.gethostname()

    def filter(self, record):
        if not hasattr(record, "project_name"):
            record.project_name = self.project_name
        if not hasattr(record, "system_name"):
            record.system_name = self.system_name
        if not hasattr(record, "request_id"):
            record.request_id = ""
        if not hasattr(record, "file_name"):
            record.file_name = ""
        if not hasattr(record, "endpoint"):
            record.endpoint = "common"
        return True
