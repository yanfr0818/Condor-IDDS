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
            raise ex

    def swap(self, pset, process='input'):
        
        if process == 'input':
            self.process.source = pset.process.source
            
        if process == 'output':
            self.process.outputModules = pset.process.outputModules
            
        if process == 'outputToInput':
            for outMod in pset.process.outputModules.keys():
                fName = (getattr(pset.process,outMod).fileName)
            fName = cms.untracked.vstring('file:'+str(fName)[len("cms.untracked.string('"):-len("')")])
            self.process.source.fileNames = fName
            
        if process == 'nEvent':
            self.process.maxEvents = pset.process.maxEvents
            
        return

    def persist(self):
        print('input: ',self.process.source.fileNames)
        for outMod in self.process.outputModules.keys():
            print('output: ',getattr(self.process,outMod).fileName)
        return

def chirpSetAttr(attr, val):
    condor_chirp = '/usr/libexec/condor/condor_chirp'
    process = subprocess.Popen([condor_chirp, 'set_job_attr', attr,'\''+val+'\''], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = process.communicate()


if __name__ == "__main__":
        
    shutil.copyfile( 'pset.py', 'psetA.py')
        
    pset_job = CMSSWPset('PSetDump')
    psetA    = CMSSWPset('psetA')
    psetB    = CMSSWPset('psetB')

    # Check process.source exists
    if getattr(pset_job.process, "source", None) is None:
        msg = "Error in CMSSW PSet: process is missing attribute 'source'"
        msg += " or process.source is defined with None value."
        raise RuntimeError(msg)
        
    inputFiles = pset_job.process.source.fileNames
    for outMod in psetB.process.outputModules.keys():
        outputFiles = getattr(psetB.process,outMod).fileName
        break
            
    method = random.randint(0,1)
    if (method == 0):
        transfer = 'cms'
        psetB.swap(pset_job, 'input')
        psetA.swap(psetB, 'outputToInput')
        psetA.swap(pset_job, 'nEvent')
        psetB.swap(pset_job, 'nEvent')  
    else:
        transfer = 'default'
    chirpSetAttr('ChirpTransferMethod', transfer)
    
    workingDir   = os.getcwd()
    configPickle = ['ppsetA.pkl', 'ppsetB.pkl']
    configFile   = [x.replace('.pkl','.py') for x in configPickle]
        
    for i in range(2):
      try:
         with open("%s/%s" % (workingDir, configPickle[i]), 'wb') as pHandle:
            if configPickle[i] == 'ppsetA.pkl': pickle.dump(psetA.process, pHandle)
            if configPickle[i] == 'ppsetB.pkl': pickle.dump(psetB.process, pHandle)
         with open("%s/%s" % (workingDir, configFile[i]), 'w') as handle:
            handle.write("import FWCore.ParameterSet.Config as cms\n")
            handle.write("import pickle\n")
            handle.write("with open('%s', 'rb') as handle:\n" % configPickle[i])
            handle.write("    process = pickle.load(handle)\n")
      except Exception as ex:
        raise ex
