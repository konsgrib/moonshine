import os
import logging
from logging.handlers import RotatingFileHandler

dir_path = os.path.dirname(os.path.realpath(__file__))
log_path = os.path.join(dir_path, "moonshine.log")


logger = logging.getLogger('') 
logger.setLevel(logging.INFO) 
handler = RotatingFileHandler(log_path, maxBytes=2000, backupCount=10)
formatter = logging.Formatter("%(asctime)s - %(filename)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)



