#import time

def safestring(thestring):
    '''safely convert anything into string'''
    if thestring is None:
        return None
    if isinstance(thestring, str): return thestring
    return str(thestring, "utf-8")

def formattime(the_time):
    '''standard format for time'''
    return the_time.strftime('%Y-%m-%d %H:%M:%S')
