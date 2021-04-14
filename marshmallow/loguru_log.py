import loguru
import socket
import os

project_root_path = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(project_root_path, 'Logs')

if not os.path.isdir(data_path):
    os.mkdir(data_path)

class GetLogger():

    def logg():
        logger = loguru.logger
        logger.remove()
        system_name = socket.gethostname()
        logfile = f'Logs/{socket.gethostname()}.log'
        form = "{time:YYYY-MM-DD HH:mm:ss.SSS} — {level} — {extra[system_name]} — {extra[project_name]} — [{extra[end_point]}] — [{extra[request_id]}] — {file}:{line} — {message} "
        logger = logger.bind(project_name = "FastAPI",system_name=system_name)
        logger.add(logfile+'{time:YYYY-MM-DD}', format=form ,level="DEBUG")
        return logger