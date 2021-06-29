import os
import socket

import loguru

project_root_path = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(project_root_path, "logs")

if not os.path.isdir(data_path):
    os.mkdir(data_path)


class FRSFilter:
    def __init__(self):
        self.system_name = str(socket.gethostname())
        self.project_name = "FastAPI"

    def __call__(self, record):
        record["extra"]["project_name"] = self.project_name
        record["extra"]["system_name"] = self.system_name
        return record


def _init_logger():
    logger = loguru.logger
    logger.remove()

    logfile = os.path.join(data_path, str(socket.gethostname()) + ".log")
    form = "{time:YYYY-MM-DD HH:mm:ss.SSS} — {level} — {extra[system_name]} — {extra[project_name]} — [{extra[end_point]}] — [{extra[request_id]}] — {file}:{line} — {message} "

    logger.add(
        logfile + "{time:YYYY-MM-DD}", format=form, filter=FRSFilter(), level="DEBUG"
    )
    return logger
