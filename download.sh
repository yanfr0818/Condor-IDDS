#Import CMS python class definitions such as Process, Source, and EDProducer
import FWCore.ParameterSet.Config as cms

# Set up a process, named RECO in this case
process = cms.Process("Download")

process.load("FWCore.MessageService.MessageLogger_cfi")

process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(-1) )

# Configure the object that reads the input file
process.source = cms.Source("PoolSource",
    fileNames = cms.untracked.vstring("root://cms-xrd-global.cern.ch//store/data/Run2018B/EGamma/RAW/v1/000/317/182/00000/962DC3A0-4364-E811-B353-02163E017F41.root")
)

# Configure the object that writes an output file
process.out = cms.OutputModule("PoolOutputModule",
    fileName = cms.untracked.string("test.root")
)

process.end = cms.EndPath(process.out)
