import shutil
import os
import pickle
import hashlib

class RequestCache:
    '''
    caching is used to prevent the need to download the same responses from the remote server multiple times during testing
    '''

    def __init__(self,mode="off",direc="cache"):
        '''
        mode:
            "off" to disable caching (does not wipe any existing cache data)
            "store" to wipe and store fresh results in the cache
            "reuse" to reuse an existing cache
        direc: the directory used to store the cache
        '''
        self.mode = mode
        self.direc = direc

        if mode == "store": self.wipe()


    def wipe(self):
        'wipe any existing cache directory and setup a new empty one'

        shutil.rmtree(self.direc,ignore_errors=True)
        os.makedirs(self.direc,exist_ok=True)


    def get_path(self,request):
        '''
        return path to cached request response
        '''

        return f"{self.direc}/{hashlib.sha256(request.encode('UTF-8')).hexdigest()}"


    def get_entry(self,request):
        '''
        load cached response
        note this should only be used in a context where you trust the integrity of the cache files
        due to using pickle
        note also: no explicit handling of cache misses yet implemented
        '''

        with open(self.get_path(request),"rb") as f:
            return pickle.load(f)
        

    def set_entry(self,request,response):
        '''
        save a response to the cache
        '''

        with open(self.get_path(request),"wb") as fout:
            pickle.dump(response,fout)

