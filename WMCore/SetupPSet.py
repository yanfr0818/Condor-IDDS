"""
_SetupCMSSWPset_

Create a CMSSW PSet suitable for running a WMAgent job.

"""
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

import FWCore.ParameterSet.Config as cms

from PSetTweak import PSetTweak

class SetupCMSSWPset():
    """
    _SetupCMSSWPset_

    """

    def __init__(self, psetModule = 'pset'):
        """
        _loadPSet_

        Load a PSet that was shipped with the job sandbox.

        """
        try:
            processMod = __import__(psetModule, globals(), locals(), ["process"], -1)
            self.process = processMod.process
        except ImportError as ex:
            msg = "Unable to import process from %s:\n" % psetModule
            msg += str(ex)
            print(msg)
            raise ex

    def applyTweak(self, psetTweak):
        """
        _applyTweak_

        Apply a tweak to the process.
        """
        tweak = PSetTweak()
        tweak.persist('test.py')
        tweak.unpersist(psetTweak)
        applyTweak(self.process, tweak, self.fixupDict)
        return

    def persist(self):
        """
        _persist_
        Save this object as either python, json or pickle
        """
        i=0	        
        for key in self.process.__dict__:
            if key.startswith('_'): continue
            i+=1	
            #print(i,': ',key,' -> ',self.process.__dict__[key])
        
        print(self.process.source)
        print(self.process._Process__outputmodules)
        
        print(self.process.source.fileNames)
        print(self.process.outputModules.fileName)
        for outMod in self.process.outputModules.keys():
            outModRef = getattr(self.process, outMod)
            print(outModRef.fileName)
        return

        
def main():
        
        pset_job = SetupCMSSWPset('pset')
        psetA    = SetupCMSSWPset('psetA')
        psetB    = SetupCMSSWPset('psetB')

        # Check process.source exists
        if getattr(pset_job.process, "source", None) is None:
            msg = "Error in CMSSW PSet: process is missing attribute 'source'"
            msg += " or process.source is defined with None value."
            raise RuntimeError(msg)
            
        psetB.persist()
        #if psetTweak is not None:
        #    mySetup.applyTweak(psetTweak)
        
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
