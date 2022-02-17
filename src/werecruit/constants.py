import os

DATE_FORMAT = '%d/%m/%Y %H:%M:%S'
NEW_ENTITY_ID = -1
LOG_FORMAT = '%(asctime)s | %(levelname)s | %(funcName)s:%(lineno)d | %(message)s'
LOG_FILENAME_WEB = 'wr_web.log'
LOG_FILENAME_SCHED ='wr_job.log'

def getUploadFolderPath():
     return os.environ.get("FILE_UPLOAD_FOLDER")


