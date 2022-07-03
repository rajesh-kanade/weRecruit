# get file extension
import os
from datetime import datetime
from datetime import timezone

def getFileExtension(fileName):
    extension = os.path.splitext(fileName)[1][1:]
    return extension

def getTimeDelta():
    t1 = datetime.now()
    f1 = t1.timestamp()
    #print(f1)

    #t2 = datetime(t1.year,t1.month,t1.day,hour=0,minute=0,second=0,tzinfo=timezone.utc)
    t2 = datetime(t1.year,t1.month,t1.day,hour=0,minute=0,second=0)

    f2= t2.timestamp()
    #print(f2)

    delta = f1-f2
    #print(delta)

    print ( '*****')
    print (t1)
    print (t2)
    print ( t1-t2)
    return (t1-t2)

#mytime = datetime(2022,7,1,hour=0,minute=0,second=0,tzinfo=timezone.utc)
#print(mytime)
#mytime =mytime+getTimeDelta()
#print(mytime)
