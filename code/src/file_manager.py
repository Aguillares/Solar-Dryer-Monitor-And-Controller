from pathlib import Path

class FileManager(object):
    
    _mode = ''
    def __init__(self,file_path:str|Path):
        self._file_path = file_path

    def __enter__(self):
         # The relative path to the database is in 'file'
        self._file = open(self._file_path,self._mode)
        return self._file
    
    def __exit__(self, exc_type,exc_value, exc_tb):
        if self._file:
            self._file.close()

        if isinstance(exc_type,Exception): 
            print(f" {exc_type = }")
            print(f" {exc_value = }")
            print(f" {exc_tb = }")


class ReadFile(FileManager):
    """It opens the file in reading and editing mode"""
    _mode = 'r+'

class DetectFile(FileManager):
    """It helps to detect whether the file exists or not"""
    _mode = 'x'
    def __exit__(self, exc_type,exc_value, exc_tb):
        if self._file:
            self._file.close()

        if isinstance(exc_type,Exception) and not isinstance(exc_type,FileExistsError): 
            print(f" {exc_type = }")
            print(f" {exc_value = }")
            print(f" {exc_tb = }")
    
class OverWriteFile(FileManager):
    _mode = 'w+'

class AddInfo(FileManager):
    _mode = 'a'
