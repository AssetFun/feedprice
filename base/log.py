#coding=utf-8
import logging
import logging.handlers
import os

def LogInit(log_file="./log/all.log", when="M", log_name=""):
    dir=os.path.dirname(log_file)
    if not dir:
        dir="."
    elif not os.path.exists(dir):
        os.makedirs(dir)
    logger = logging.getLogger(log_name)
    if not logger.handlers:
        hdlr = logging.handlers.TimedRotatingFileHandler(log_file,when,interval=1,backupCount=40)
        formatter = logging.Formatter("[%(asctime)s] [%(filename)s][line:%(lineno)d] [%(levelname)s] %(message)s")
        hdlr.setFormatter(formatter)
        logger.addHandler(hdlr)
    logger.setLevel(logging.DEBUG)
    return logger

#################################################################################################################
def main():
    import time
    logger1 = LogInit(log_file="logtest1.log", when="D", log_name="log1")
    logger2 = LogInit(log_file="logtest2.log", when="D", log_name="log2")

    if logger1 == logger2:
        print("the same")
    else:
        print("different.")
    logger1.info("date split info")
    logger1.debug("date split debug")
    logger1.error("date split error")
    logger2.info("date split info")
    logger2.debug("date split debug")
    logger2.error("date split error")
    return


    print("Test gennerate log file by minute...")
    logger = LogInit(log_file="logtest.log")
    i=1
    while True:
        logger.info("date split info")
        logger.debug("date split debug")
        logger.error("date split error")
        print("generate %d log files..." %i)
        time.sleep(60)
        i=i+1
    

if __name__ == '__main__':
    main()