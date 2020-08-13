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
from WMTweak import applyTweak, makeJobTweak, makeOutputTweak, makeTaskTweak, resizeResources


def fixupGlobalTag(process):
    """
    _fixupGlobalTag_

    Make sure that the process has a GlobalTag.globaltag string.

    Requires that the configuration already has a properly configured GlobalTag object.

    """
    if hasattr(process, "GlobalTag"):
        if not hasattr(process.GlobalTag, "globaltag"):
            process.GlobalTag.globaltag = cms.string("")
    return


def fixupGlobalTagTransaction(process):
    """
    _fixupGlobalTagTransaction_

    Make sure that the process has a GlobalTag.DBParameters.transactionId string.

    Requires that the configuration already has a properly configured GlobalTag object

    (used to customize conditions access for Tier0 express processing)

    """
    if hasattr(process, "GlobalTag"):
        if not hasattr(process.GlobalTag.DBParameters, "transactionId"):
            process.GlobalTag.DBParameters.transactionId = cms.untracked.string("")
    return


def fixupFirstRun(process):
    """
    _fixupFirstRun_

    Make sure that the process has a firstRun parameter.

    """
    if not hasattr(process.source, "firstRun"):
        process.source.firstRun = cms.untracked.uint32(0)
    return


def fixupLastRun(process):
    """
    _fixupLastRun_

    Make sure that the process has a lastRun parameter.

    """
    if not hasattr(process.source, "lastRun"):
        process.source.lastRun = cms.untracked.uint32(0)
    return


def fixupLumisToProcess(process):
    """
    _fixupLumisToProcess_

    Make sure that the process has a lumisToProcess parameter.

    """
    if not hasattr(process.source, "lumisToProcess"):
        process.source.lumisToProcess = cms.untracked.VLuminosityBlockRange()
    return


def fixupSkipEvents(process):
    """
    _fixupSkipEvents_

    Make sure that the process has a skip events parameter.

    """
    if not hasattr(process.source, "skipEvents"):
        process.source.skipEvents = cms.untracked.uint32(0)
    return


def fixupFirstEvent(process):
    """
    _fixupFirstEvent_

    Make sure that the process has a first event parameter.

    """
    if not hasattr(process.source, "firstEvent"):
        process.source.firstEvent = cms.untracked.uint32(0)
    return


def fixupMaxEvents(process):
    """
    _fixupMaxEvents_

    Make sure that the process has a max events parameter.

    """
    if not hasattr(process, "maxEvents"):
        process.maxEvents = cms.untracked.PSet(input=cms.untracked.int32(-1))
    if not hasattr(process.maxEvents, "input"):
        process.maxEvents.input = cms.untracked.int32(-1)
    return


def fixupFileNames(process):
    """
    _fixupFileNames_

    Make sure that the process has a fileNames parameter.

    """
    if not hasattr(process.source, "fileNames"):
        process.source.fileNames = cms.untracked.vstring()
    return


def fixupSecondaryFileNames(process):
    """
    _fixupSecondaryFileNames_

    Make sure that the process has a secondaryFileNames parameter.

    """
    if not hasattr(process.source, "secondaryFileNames"):
        process.source.secondaryFileNames = cms.untracked.vstring()
    return


def fixupFirstLumi(process):
    """
    _fixupFirstLumi

    Make sure that the process has firstLuminosityBlock parameter.
    """
    if not hasattr(process.source, "firstLuminosityBlock"):
        process.source.firstLuminosityBlock = cms.untracked.uint32(1)
    return


class SetupCMSSWPset():
    """
    _SetupCMSSWPset_

    """
    fixupDict = {"process.GlobalTag.globaltag": fixupGlobalTag,
                 "process.GlobalTag.DBParameters.transactionId": fixupGlobalTagTransaction,
                 "process.source.fileNames": fixupFileNames,
                 "process.source.secondaryFileNames": fixupSecondaryFileNames,
                 "process.maxEvents.input": fixupMaxEvents,
                 "process.source.skipEvents": fixupSkipEvents,
                 "process.source.firstEvent": fixupFirstEvent,
                 "process.source.firstRun": fixupFirstRun,
                 "process.source.lastRun": fixupLastRun,
                 "process.source.lumisToProcess": fixupLumisToProcess,
                 "process.source.firstLuminosityBlock": fixupFirstLumi}

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
        print(self.process)
        print(self.process.__dict__)
        return

    def fixupProcess(self):
        """
        _fixupProcess_

        Look over the process object and make sure that all of the attributes
        that we expect to exist actually exist.

        """
        if hasattr(self.process, "outputModules"):
            outputModuleNames = self.process.outputModules.keys()
        else:
            outputModuleNames = self.process.outputModules_()
        for outMod in outputModuleNames:
            outModRef = getattr(self.process, outMod)
            if not hasattr(outModRef, "dataset"):
                outModRef.dataset = cms.untracked.PSet()
            if not hasattr(outModRef.dataset, "dataTier"):
                outModRef.dataset.dataTier = cms.untracked.string("")
            if not hasattr(outModRef.dataset, "filterName"):
                outModRef.dataset.filterName = cms.untracked.string("")
            if not hasattr(outModRef, "fileName"):
                outModRef.fileName = cms.untracked.string("")
            if not hasattr(outModRef, "logicalFileName"):
                outModRef.logicalFileName = cms.untracked.string("")
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
        
    def setattrCalls(self, psetPath):
        """
        _setattrCalls_
        Generate setattr call for each parameter in the pset structure
        Used for generating python format
        """
        result = {}
        current = None
        last = None
        psets = 'pset.py'
        for _ in range(0, len(psets)):
            pset = psets.pop(0)
            last = current
            if current == None:
                current = pset
            else:
                current += ".%s" % pset
            if last != None:
                result[current] = "setattr(%s, \"%s\", PSetHolder(\"%s\"))" % (
                    last, pset, pset)
        return result
        
    def pythonise(self):
        """
        _pythonise_
        return this object as python format
        """
        result = ""
        result += "\n\n"
        result += "# define PSet Structure\n"
        result += "process = PSetHolder(\"process\")\n"
        setattrCalls = {}
        setattrCalls.update(self.setattrCalls(self.process))
        order = sorted(setattrCalls.keys())
        for call in order:
            if call == "process": continue
            result += "%s\n" % setattrCalls[call]

        result += "# set parameters\n"
        for param, value in self.process:
            psetName = param.rsplit(".", 1)[0]
            paramName = param.rsplit(".", 1)[1]
            if isinstance(value, basestring):
                value = "\"%s\"" % value
            result += "setattr(%s, \"%s\", %s)\n" % (
                psetName, paramName, value)
            result += "%s.parameters_.append(\"%s\")\n" % (psetName, paramName)

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
        
        print("Executing SetupCMSSWPSet...")
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

        psetTweak = "pset.py"

        if psetTweak is not None:
            mySetup.applyTweak(psetTweak)
        
        try:
            with open("pset_new.py", 'wb+') as pHandle:
                pHandle.write(mySetup.process)
        except Exception as ex:
            print("Error writing out PSet:")
            raise ex
        print("CMSSW PSet setup completed!")
   
if __name__ == "__main__":
    main()
