import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

formatter = logging.Formatter('[%(asctime)s, File<%(filename)s> line %(lineno)s] [%(levelname)s] %(message)s', '%Y-%m-%d %H:%M:%S')

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

file_debug_handler = logging.FileHandler('testinglog.log')
file_debug_handler.setFormatter(formatter)
logger.addHandler(file_debug_handler)


def troublefunc():
    logging.info("I am here")

troublefunc()