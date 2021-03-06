#!/bin/sh

if [ $3 == "NULL" ] && [ $4 == "NULL" ]
then
    exit -1
fi

dir=$1
cms=$2
sarch=$3
jno=$4

source /cvmfs/cms.cern.ch/cmsset_default.sh
export SCRAM_ARCH=$sarch
scramv1 project CMSSW $cms
cd $cms
cd src
cmsenv

cd ../..
cp -r $dir/$cms/. $cms/.
#cmsRun PSetDump.py

cp PSetDump.py pset.py
python psetEditWrapper.py foo

method=$(/usr/libexec/condor/condor_chirp get_job_attr ChirpTransferMethod)
if (method=="cms")
then
    trap 'exit' ERR
    cmsRun psetB.py -j jobreportB$jno.xml
    cmsRun psetA.py -j jobreportA$jno.xml
else
    cmsRun psetA.py -j jobreport$jno.xml
fi
