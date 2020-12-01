import pandas as pd
import librosa
import matplotlib.pyplot as plt
import numpy as np
import csv
import os

# Load wav paths
wav_scp = pd.read_csv("data/zjch/test/wav.scp", delimiter="\t", names=["utt","path"])
#test_wav = wav_scp[wav_scp.utt==utt_id].path.iloc[0]
#print(test_wav)

col_names = ['语音编号', '总字数', '非重复字数的总个数', '有意义字数', '总时间', '发音时间', '有意义发音时间', '停顿总时间', '停顿总次数', \
                 '语速', '发音语速', '有意义产出语速', 'pruned有意义产出语速', '平均每次停顿时长', '停顿频率', 'Token Type Ratio']

def print(*args):
    args = [str(x) for x in args]
    with open('stat/logs/'+utt_id+'.txt', 'a') as wf:
        wf.write(' '.join(args)+'\n')

for idx, row in wav_scp.iterrows():
    utt_id, test_wav = row['utt'], row['path']
    if os.path.exists('stat/logs/'+utt_id+'.txt'):
        os.remove('stat/logs/'+utt_id+'.txt')

    # Read alignment file
    ali = pd.read_csv("stat/utt_alis/"+utt_id+".txt", delimiter="\t", names=["pinyin_id","utt_id","_","start","dur","pinyin"])
    ali = ali.sort_values('start')
    py = ali["pinyin"].tolist()
    print("预测拼音:", py)
    dur = ali["dur"].tolist()
    print("预测时长:", dur)

    # Read word dict
    id2tran = dict()
    with open("exp/chain/tdnn/graph/words.txt", "r") as rf:
        for line in rf:
            columns = line.split()
            id2tran[columns[1]] = columns[0]

    # Predicted transcript
    utt2tran = dict()
    with open("exp/chain/tdnn/decode_test/scoring/17.tra", "r") as rf:
    	for line in rf:
    		words = line.split()
    		utt2tran[words[0]] = "".join([id2tran[x] for x in words[1:]])
    tran = utt2tran[utt_id]
    print("预测旁白:", tran)

    # Ground-truth transcript
    utt2gtran = dict()
    with open("exp/chain/tdnn/decode_test/scoring/test_filt.txt", "r") as rf:
    	for line in rf:
    		words = line.split()
    		utt2gtran[words[0]] = "".join(words[1:])
    gtran = utt2gtran[utt_id]
    for x in [('0','零'),('1','一'),('2','二'),('3','三'),('4','四'),('5','五'),('6','六'),('7','七'),('8','八'),('9','九')]:
        gtran = gtran.replace(x[0], x[1])
    print("真实旁白:", gtran)

    # Read pinyin dict
    word2py = dict()
    with open("data/lang_chain/phones/align_lexicon.txt", "r") as rf:
        for line in rf:
            tokens = line.split()
            word2py[tokens[0]] = tokens[2:]

    # Ground-truth pinyin
    cons_len = 0
    gpy = []
    while cons_len < len(tran):
    	for i in range(4,-1,-1):
    		try: 
    			gpy += word2py[tran[cons_len:cons_len+i]]
    			cons_len += i
    			break
    		except Exception as e:
    			#print(e)
    			pass
    		if i == 0:
    			print("Error: Cannot find py.")
    			exit()
    print("真实拼音:", gpy)

    # Align sequence
    def levenshteinDistance(s1, s2, dur=None):
        if dur is None:
            dur = [0 for _ in s1]
        distances = range(len(s1) + 1)
        aligns = [["x"]*x for x in distances]
        aligns2 = [[0]*x for x in distances]
        for i2, c2 in enumerate(s2):
            distances_ = [i2+1]
            aligns_ = [[["x"]*(i2+1)]]
            aligns2_ = [[[0]*(i2+1)]]
            for i1, c1 in enumerate(s1):
                if c1 == c2:
                    distances_.append(distances[i1])
                    aligns_.append(aligns[i1] + [c1])
                    aligns2_.append(aligns2[i1] + [dur[i1]])
                elif distances[i1] <= distances[i1 + 1] and distances[i1] <= distances_[-1]:
                    distances_.append(1 + distances[i1])
                    aligns_.append(aligns[i1]+["x"])
                    aligns2_.append(aligns2[i1]+[0])
                elif distances[i1 + 1] <= distances_[-1]:
                    distances_.append(1 + distances[i1 + 1])
                    aligns_.append(aligns[i1 + 1]+["x"])
                    aligns2_.append(aligns2[i1 + 1]+[0])
                else:
                    distances_.append(1 + distances_[-1])
                    aligns_.append(aligns_[-1])
                    aligns2_.append(aligns2_[-1])
            distances = distances_
            aligns = aligns_
            aligns2 = aligns2_
        return distances[-1], aligns[-1], aligns2[-1]

    # Align transcription
    _, alig_tran, _ = levenshteinDistance([x for x in tran], [x for x in gtran])
    print("对齐旁白:", alig_tran)

    # Align pinyin
    _, alig_py, alig_dur = levenshteinDistance(py, gpy, dur)
    print("对齐拼音:", alig_py)
    print("对齐时长:", alig_dur)

    # Calculate pinyin duration
    py_time = 0
    for t in dur:
        py_time += t
    alig_py_time = 0
    for t in alig_dur:
        alig_py_time += t

    # Read wav
    y, sr = librosa.load(test_wav, sr=8000)
    abs_y = np.abs(y)
    plt.plot(y)
    plt.show()
    print("语音形状:", y.shape)

    # Calculate silence time
    sil_time = 0
    sil_thre = np.mean(abs_y)*0.8
    print("沉默音量阈值:", sil_thre)
    for x in range(y.shape[0]-int(sr*0.01)):
        if np.amax(abs_y[x:x+int(sr*0.01)]) < sil_thre:
            sil_time += 1/sr

    # Calculate silence count
    sil_count = 0
    sil_pts = []
    is_silence = True
    for x in range(y.shape[0]-int(sr*0.25)):
        if not is_silence and np.amax(abs_y[x:x+int(sr*0.25)]) < sil_thre:
            sil_count += 1
            is_silence = True
            sil_pts.append(x/sr)
        if y[x] >= sil_thre:
            is_silence = False
    print("沉默时间点：", sil_pts)

    # Print stat
    print('总字数：', len(tran), '字')
    print('非重复字数的总个数：', len(set(tran)), '字')
    print('有意义字数：', len([1 for w in alig_tran if w != 'x']), '字')
    print('总时间：', y.shape[0]/sr, '秒')
    print('发音时间：', py_time,'秒')
    print('有意义发音时间：', alig_py_time, '秒')
    print('停顿总时间：', sil_time, '秒')
    print('停顿总次数：', sil_count, '次')
    print('语速：', len(tran)/(y.shape[0]/sr), '字/秒')
    print('发音语速：', len(tran)/py_time, '字/发音时间')
    print('有意义产出语速：', len([1 for w in alig_tran if w != 'x'])/(y.shape[0]/sr), '(有意义的字数/总时间)')
    print('pruned有意义产出语速：', len([1 for w in alig_tran if w != 'x'])/alig_py_time, '(有意义字数/有意义的发音总时间)')
    print('平均每次停顿时长：', ((y.shape[0]/sr)-py_time)/sil_count, '秒')
    print('停顿频率：', ((y.shape[0]/sr)-py_time)/(y.shape[0]/sr), '[(总时间-发音时间)/总时间]')
    print('Token Type Ratio：', len(set(tran))/len(tran), '(非重复字数的总个数/总字数)')

    if not os.path.isfile("stat/stats.csv") :
        with open("stat/stats.csv", 'w', newline='') as rf:
            writer = csv.writer(rf)
            writer.writerow(col_names)

    with open("stat/stats.csv", 'a', newline='') as rf:
        writer = csv.writer(rf)
        writer.writerow([utt_id, len(tran), len(set(tran)), len([1 for w in alig_tran if w != 'x']), y.shape[0]/sr, py_time, alig_py_time, \
                         sil_time, sil_count, len(tran)/(y.shape[0]/sr), len(tran)/py_time, \
                         len([1 for w in alig_tran if w != 'x'])/(y.shape[0]/sr), len([1 for w in alig_tran if w != 'x'])/alig_py_time, \
                         ((y.shape[0]/sr)-py_time)/sil_count, ((y.shape[0]/sr)-py_time)/(y.shape[0]/sr), len(set(tran))/len(tran)])