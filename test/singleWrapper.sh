#!/bin/sh

if [ $3 == "NULL" ] && [ $4 == "NULL" ]
then
    exit -1
fi

dir=$1
cms=$2
sarch=$3
jno=$4

condor_chirp=/usr/libexec/condor/condor_chirp
executable=SetupPSet.py

source /cvmfs/cms.cern.ch/cmsset_default.sh
export SCRAM_ARCH=$sarch
scramv1 project CMSSW $cms
cd $cms
cd src
cmsenv

cd ../..
cp -r $dir/$cms/. $cms/.
cmsRun PSetDump.py

cp PSetDump.py pset.py
python $executable

method=$($condor_chirp get_job_attr ChirpTransferMethod)
if [ $method == "cms" ]
then
    trap 'exit' ERR
    cmsRun ppsetB.py -j jobreportB$jno.xml
    cmsRun ppsetA.py -j jobreportA$jno.xml
else
    cmsRun ppsetA.py -j jobreport$jno.xml
fi
