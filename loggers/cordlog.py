import logging


# create log file
LOG_FILE = "D:\\Dev\\Python\\Roland\\data\\logs\\cord logs\\cord.log"

# gets or creates a logger
logger = logging.getLogger(__name__)

# set log level
logger.setLevel(logging.INFO)

# define file handler and set formatter
file_handler = logging.FileHandler(LOG_FILE)
formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(name)s : %(message)s')
file_handler.setFormatter(formatter)

# add file to logger
logger.addHandler(file_handler)

# logs
logger.debug('A debug message')
logger.info('An issue has arose in discord..')
