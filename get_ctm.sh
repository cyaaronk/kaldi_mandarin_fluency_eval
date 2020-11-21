#!/usr/bin/env bash

for i in exp/tri4b_ali/test/ali.*.gz; do
	src/bin/ali-to-phones --ctm-output exp/tri4b/final.mdl ark:"gunzip -c $i|" - > ${i%.gz}.ctm;
done