# Import CMS python class definitions such as Process, Source, and EDProducer
import FWCore.ParameterSet.Config as cms

# Set up a process, named RECO in this case
process = cms.Process("ReadIn")

process.load("FWCore.MessageService.MessageLogger_cfi")

process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(100) )

# Configure the object that reads the input file
process.source = cms.Source("PoolSource", 
    fileNames = cms.untracked.vstring('file://local.root'),
)

# Configure the object that writes an output file
process.out = cms.OutputModule("PoolOutputModule",
    fileName = cms.untracked.string("local.root")
)

process.end = cms.EndPath(process.out)
