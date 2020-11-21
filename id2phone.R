#!/usr/bin/Rscript

#  id2phone.R
#  
#
#  Created by Eleanor Chodroff on 3/24/15.
#
phones <- read.table("data/lang/phones.txt", quote="\"")
ctm <- read.table("exp/tri4b_ali/test/merged_alignment.txt", quote="\"")

names(ctm) <- c("file_utt","utt","start","dur","id")
ctm$file <- gsub("_[0-9]*$","",ctm$file_utt)
names(phones) <- c("phone","id")

ctm2 <- merge(ctm, phones, by="id")

write.table(ctm2, "exp/tri4b_ali/test/final_ali.txt", row.names=F, quote=F, sep="\t")

