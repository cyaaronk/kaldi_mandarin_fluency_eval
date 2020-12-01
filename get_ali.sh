#!/usr/bin/env bash

#for i in exp/chain/tdnn/decode_test/ali_tmp.*.gz; do
#	src/bin/ali-to-phones --ctm-output exp/chain/tdnn/final.mdl ark:"gunzip -c $i|" - > ${i%.gz}.ctm;
#done

src/bin/ali-to-phones --ctm-output exp/chain/tdnn/final.mdl "ark:gunzip -c exp/chain/tdnn/decode_test/ali_tmp.*.gz|" - > stat/ali.ctm
Rscript stat/id2phone.R
tail -n +2 stat/ali.txt | awk -F, 'BEGIN {FS="\t"}; { print > "stat/utt_alis/" $2 ".txt" }'