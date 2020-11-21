#  splitAlignments.py
#  
#
#  Created by Eleanor Chodroff on 3/25/15.
#
#
#
import sys,csv
results=[]

#name = name of first text file in final_ali.txt
#name_fin = name of final text file in final_ali.txt

name = "D04_750"
name_fin = "D08_881"
try:
    with open("exp/tri4b_ali/test/final_ali.txt") as f:
        next(f) #skip header
        for line in f:
            columns=line.split("\t")
            name_prev = name
            name = columns[1]
            if (name_prev != name):
                try:
                    with open("wav_ali/"+(name_prev)+".txt",'a') as fwrite:
                        fwrite.write("\n".join(results)+"\n")
                #print name
                except Exception as e:
                    print("Failed to write file",e)
                    sys.exit(2)
                del results[:]
                results.append(line[0:-1])
            else:
                results.append(line[0:-1])
except Exception as e:
    print("Failed to read file",e)
    sys.exit(1)
# this prints out the last textfile (nothing following it to compare with)
try:
    with open("wav_ali/"+(name_prev)+".txt",'a') as fwrite:
        fwrite.write("\n".join(results)+"\n")
except Exception as e:
    print("Failed to write file",e)
    sys.exit(2)