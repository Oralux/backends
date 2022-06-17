# -*- coding: utf-8 -*-
from . import base
import subprocess
import os
import platform
import shutil
from lib import util


class VoxinTTSBackend(base.SimpleTTSBackendBase):
    provider = 'Voxin'
    displayName = 'Voxin'
    speedConstraints = (0,60,100,True)
    settings = {    'voice':'',
                    'speed':0,
                    #'pitch':0,
                    #'output_via_espeak':False,
                    'player':None,
                    #'volume':0,
                    'pipe':False
    }
    exe = 'voxin-say'
    commandLine = [exe]

    def init(self):
        self.process = None
        self.update()

    def addCommonArgs(self,args,text):
        if self.voice: args.extend(('-l',self.voice))
        if self.speed: args.extend(('-S',str(self.speed)))
        # if self.pitch: args.extend(('-p',str(self.pitch)))
        # if self.volume != 100: args.extend(('-a',str(self.volume)))
        args.append(text.encode('utf-8'))

    def runCommand(self,text,outFile):
        args = list(self.commandLine)
        args.extend(('-w', outFile))
        self.addCommonArgs(args,text)
        subprocess.call(args)
        return True

    def runCommandAndSpeak(self,text):
        args = ['voxin-say']
        self.addCommonArgs(args,text)
        self.process = subprocess.Popen(args)
        while self.process.poll() == None and self.active: util.sleep(10)

    def runCommandAndPipe(self,text):
        args = list(self.commandLine)
        self.addCommonArgs(args,text)
        self.process = subprocess.Popen(args,stdout=subprocess.PIPE)
        return self.process.stdout

    def update(self):
        self.setPlayer(self.setting('player'))
        self.setMode(self.getMode())
        self.voice = self.setting('voice')
        self.speed = self.setting('speed')
        # self.pitch = self.setting('pitch')
        # volume = self.setting('volume')
        # self.volume = int(round(100 * (10**(volume/20.0)))) #convert from dB to percent

    def getMode(self):
        if self.setting('pipe'):
            return base.SimpleTTSBackendBase.PIPE
        else:
            return base.SimpleTTSBackendBase.WAVOUT

    def stop(self):
        if not self.process: return
        try:
            self.process.terminate()
        except:
            pass

    @classmethod
    def settingList(cls,setting,*args):
        if setting == 'voice':
            import re
            ret = []
            args = list(cls.commandLine)
            args.append('-L')
            out = subprocess.check_output(args, stdin=subprocess.DEVNULL).splitlines()
            if len(out) == 0:
                return None
            out.pop(0)
            for l in out:
                if len(l) == 0:
                    break
                voice = re.split(',',l.decode('utf-8').strip(),1)[0]
                ret.append((voice,voice))
            return ret
        return None

    @staticmethod
    def available():
        try:
            args = list(VoxinTTSBackend.commandLine)
            args.append('-h')
            subprocess.call(args, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except:
            return False
        return True
