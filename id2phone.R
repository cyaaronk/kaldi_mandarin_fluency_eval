#!/usr/bin/Rscript

#  id2phone.R
#  
#
#  Created by Eleanor Chodroff on 3/24/15.
#
phones <- read.table("exp/chain/tdnn/graph/phones.txt", quote="\"")
ctm <- read.table("stat/ali.ctm", quote="\"")

names(ctm) <- c("file_utt","utt","start","dur","id")
names(phones) <- c("phone","id")

ctm2 <- merge(ctm, phones, by="id")

write.table(ctm2, "stat/ali.txt", row.names=F, quote=F, sep="\t")

