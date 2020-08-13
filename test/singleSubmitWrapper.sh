#!/bin/sh

index=$1
if [ $index == "NULL" ]
then
    exit
fi

for i in {1..100}
do
    dir=$(sed -n "${index}p" /home/bloomcap3/listdir.txt)
    cms=$(sed -n "${index}p" /home/bloomcap3/listcms.txt)
    sarch=$(sed -n "${index}p" /home/bloomcap3/listarch.txt)

    echo "The variables: ${dir} ${cms} ${sarch} ${i}"

    condor_submit singleWrapper.sub -append "Arguments = ${dir} ${cms} ${sarch} ${i}" "transfer_input_files = /home/bloomcap3/$dir, /home/bloomcap3/$dir/PSetDump.py, ../PSets/psetB.py, ../WMCore/SetupPSet.py" "Error = singleWrapper/err.$i" "Output = singleWrapper/out.$i" "Log = singleWrapper/log.$i" 

done
