#!/usr/bin/env python
from __future__ import print_function
import json
import imp
import inspect
import logging
import os
import pickle
import random
import socket
import re
import posixpath
import shutil
import random
import subprocess

import FWCore.ParameterSet.Config as cms

class CMSSWPset():

    def __init__(self, psetModule = 'pset'):
        try:
            processMod = __import__(psetModule, globals(), locals(), ["process"], -1)
            self.process = processMod.process
        except ImportError as ex:
            msg = "Unable to import process from %s:\n" % psetModule
            msg += str(ex)
            print(msg)
            raise ex

    def swap(self, process='input', fName=''):
        
        if process == 'input':
            fName = str(fName)
            try:    fName = fName.replace('.string' ,'.vstring')    
            except: pass
            print("file name: ",fName)
            if fName.find('/') == -1:    fName = fName.replace("string(\'", "string(\'file:")
            #setattr(self, self.process.source.fileNames, fName)
            for inMod in self.process.source.keys():
                setattr(self.process,getattr(self.process,inMod).fileName,fName)
            
        if process == 'output':
            try:    fName = fName.replace('vstring','string' )    
            except: pass
            for outMod in self.process.outputModules.keys():
                setattr(self,getattr(self.process,outMod).fileName, fName)
                break
                
        return

    def persist(self):
        print(self.process.source.fileNames)
        for outMod in self.process.outputModules.keys():
            print(getattr(self.process,outMod).fileName)
        return

        
def main():
        
        shutil.copyfile( 'pset.py', 'psetA.py')
        
        pset_job = CMSSWPset('pset')
        psetA    = CMSSWPset('psetA')
        psetB    = CMSSWPset('psetB')

        # Check process.source exists
        if getattr(pset_job.process, "source", None) is None:
            msg = "Error in CMSSW PSet: process is missing attribute 'source'"
            msg += " or process.source is defined with None value."
            raise RuntimeError(msg)
 
        psetA.persist()           
        psetB.persist()
        
        inputFiles = pset_job.process.source.fileNames
        for outMod in psetB.process.outputModules.keys():
            outputFiles = getattr(psetB.process,outMod).fileName
            break
            
        psetB.swap('input', inputFiles )
        psetA.swap('input', outputFiles)
        
        psetA.persist()
        psetB.persist()
        
        workingDir   = os.getcwd()
        configPickle = 'psettest.pkl'
        configFile   = configPickle.replace('.pkl','.py')
        
        try:
            with open("%s/%s" % (workingDir, configPickle), 'wb') as pHandle:
                pickle.dump(psetB.process, pHandle)

            with open("%s/%s" % (workingDir, configFile), 'w') as handle:
                handle.write("import FWCore.ParameterSet.Config as cms\n")
                handle.write("import pickle\n")
                handle.write("with open('%s', 'rb') as handle:\n" % configPickle)
                handle.write("    process = pickle.load(handle)\n")
        except Exception as ex:
            raise ex
   
if __name__ == "__main__":
    main()
