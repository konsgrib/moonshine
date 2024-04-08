import os
import json
from logger import logger


def set_environment_variables_from_json(json_file_path):
    """reading config file and setting environment variables"""

    def set_env_vars(data, prefix=""):
        logger.info(f"Parsing config: {json_file_path}")
        for key, value in data.items():
            if isinstance(value, dict):
                set_env_vars(value, prefix + key + "_")
            else:
                print(f"setting env var: {prefix + key}: {str(value)}")
                logger.info(f"setting env var: {prefix + key}: {str(value)}")
                os.environ[prefix + key] = str(value)

    with open(json_file_path, "r") as f:
        config_data = json.load(f)

    set_env_vars(config_data)
