#!/bin/sh

for index in {1..973}
do
    dir=$(sed -n "${index}p" /home/bloomcap3/listdir.txt)
    cms=$(sed -n "${index}p" /home/bloomcap3/listcms.txt)
    arch=$(sed -n "${index}p" /home/bloomcap3/listarch.txt)

    echo "The variables: ${dir} ${cms} ${arch}"

    condor_submit massWrapper.sub -append "Arguments = ${dir} ${cms} ${arch}" "transfer_input_files = /home/bloomcap3/$dir, /home/bloomcap3/$dir/PSetDump.py, /home/bloom/yanfr0818/IDDS/condor/psetB.py, /home/bloom/yanfr0818/IDDS/condor/psetEditWrapper.py" "Error = massWrapper/err.$index" "Output = massWrapper/out.$index" "Log = massWrapper/log.$index" 

done
