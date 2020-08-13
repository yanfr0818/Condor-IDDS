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

    def loadPSet(self, psetModule = 'pset'):
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
        return

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
              
    def pythonise(self):
        """
        _pythonise_
        return this object as python format
        """
        result = ''
        
        print(self.process.source)
        print(self.process.outputModules)
                
        return result

    def persist(self, filename, formatting="python"):
        """
        _persist_
        Save this object as either python, json or pickle
        """
        if formatting == "python":
            with open(filename, 'w') as handle:
                handle.write(self.pythonise())
        return

        
def main():
        
        mySetup = SetupCMSSWPset()
        try:
            mySetup.loadPSet('pset')
        except Exception as ex:
            print("Error loading PSet:")
            raise ex
        mySetup.persist('test.py')
        # Check process.source exists
        if getattr(mySetup.process, "source", None) is None:
            msg = "Error in CMSSW PSet: process is missing attribute 'source'"
            msg += " or process.source is defined with None value."
            print(msg)
            raise RuntimeError(msg)
            
        #mySetup.fixupProcess()

        #if psetTweak is not None:
        #    mySetup.applyTweak(psetTweak)
        
        workingDir   = os.getcwd
        configPickle = 'psettest.pkl'
        configFile   = configPickle.replace('.pkl','.py')
        
        try:
            with open("%s/%s" % (workingDir, configPickle), 'wb') as pHandle:
                pickle.dump(mySetup.process, pHandle)

            with open("%s/%s" % (workingDir, configFile), 'w') as handle:
                handle.write("import FWCore.ParameterSet.Config as cms\n")
                handle.write("import pickle\n")
                handle.write("with open('%s', 'rb') as handle:\n" % configPickle)
                handle.write("    process = pickle.load(handle)\n")
        except Exception as ex:
            raise ex
   
if __name__ == "__main__":
    main()
