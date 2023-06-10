import bpy
import datetime

class TLM_Logman:

    _log = []

    def __init__(self):
        print("Logger started Init")
        self.append("Logger started.")

    def append(self, appended):
        self._log.append(str(datetime.datetime.now()) + ": " + str(appended))

    #TODO!
    def stats():
        pass

    def dumpLog(self):
        for line in self._log:
            print(line)