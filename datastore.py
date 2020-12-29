import json
import os
import sys
import time
import threading
class datastore:

    def __init__(self, filepath=os.getcwd()):

        self.file_path = filepath + '/key_value.json'
        self.file_lock = threading.Lock()
        self.data_lock = threading.Lock()

        try:
            file = open(self.file_path, 'r')
            filedata = json.load(file)
            self.data = filedata
            file.close()

            if not self.file_size_check():
                raise Exception('Size of the data store exceeds 1 GB. Unable to add more data.')

            print('The file is created in this location' + self.file_path)
        except:

            file = open(self.file_path, 'w')
            self.data = {}
            self.ttldict = {}
            file.close()
            print('file is created in this location ' + self.file_path)
    
    #This func is used to check the size of file.Returns wheather the file is greater than 1GB or not.
    def file_size_check(self):
        self.file_lock.acquire()
        if os.path.getsize(self.file_path) <= 1e+9:
            self.file_lock.release()
            return True
        else:
            self.file_lock.release()
            return False
    #This func is used to check the wheather given constrain are matched for the key.
    def key_check(self, key):                                                  
        if type(key) == type(""):
            if len(key) > 32:
                raise Exception('Key size is capped at 32char. The given key length is ' + str(len(key)))
            else:
                return True
        else:
            raise Exception('Key value is not a string. The give type is: ' + str(type(key)))
    
    #This func is used to create key-value pair.
    def create(self, key='', value='', ttl=None):
        self.key_check(key)
        
        if key == '':
            raise Exception('No key was provided.')
        
        if value == '':
            value = None
        
        if sys.getsizeof(value) > 16384:                                          
            raise Exception("value exceeds 16KB size limit.")
        
        if not self.file_size_check():
            raise Exception('Size of the data store exceeds 1 GB. Unable to add more data.')
        self.data_lock.acquire()
        
        if key in self.data.keys():
            self.data_lock.release()
            raise Exception('Key is already present.')
                                            
        if ttl is not None:
            ttl = int(time.time()) + abs(int(ttl))

        tempdict = {'value': value, 'ttl': ttl}
        self.data[key] = tempdict
        self.file_lock.acquire()
        json.dump(self.data, fp=open(self.file_path, 'w'), indent=2)
        self.file_lock.release()
        self.data_lock.release()
        print('added to the file')
    
    #This func is used to read the key-value pair. 
    def read(self, key=''):

        self.key_check(key)
        if key == '':
            raise Exception('Expecting a key to be read.')
        
        self.data_lock.acquire()

        if key in self.data.keys():
            pass
        else:
            self.data_lock.release()
            raise Exception('Key not found in database')

        ttl = self.data[key]['ttl']

        if not ttl:
            ttl = 0

        if (time.time() < ttl) or (ttl == 0):
            self.data_lock.release()
            return json.dumps(self.data[key]['value'])
        else:
            self.data_lock.release()
            raise Exception("Key's TTL has expired. Unable to read.")
    
    #This func is used to delete the key-value pair.
    def delete(self, key=''):
        self.key_check(key)

        if key == '':
            raise Exception('Expecting a key to be read.')

        self.data_lock.acquire()

        if key in self.data.keys():
            pass
        else:
            self.data_lock.release()
            raise Exception('Key not found in database')

        ttl = self.data[key]['ttl']
        
        if not ttl:
            ttl = 0
        #This snippet check for does the entity ttl is expired or not.
        if time.time() < ttl or (ttl == 0):
            self.data.pop(key)
            self.file_lock.acquire()
            file = open(self.file_path, 'w')
            json.dump(self.data, file)
            self.file_lock.release()
            self.data_lock.release()
            print("pair deleted")
            return
        else:
            self.data_lock.release()
            raise Exception("Key's TTL has expired. Unable to delete!!")
