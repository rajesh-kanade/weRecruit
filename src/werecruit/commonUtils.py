# get file extension
import os
def getFileExtension(fileName):
    extension = os.path.splitext(fileName)[1][1:]
    return extension
