#!/bin/bash
RESULT_FOLDER="$RESULT_DIR/result_by_timeout/timeout_0-20"
for sca in $(ls $RESULT_FOLDER/*sca) 
do
    out=${sca/sca/csv}
    ./opp_sca2csv.pl -F packetsReceived -F packetReceivedAt -F hopCount $sca > $out
done

