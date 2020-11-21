import pandas as pd
import librosa
import matplotlib.pyplot as plt
import numpy as np

utt_id = "D32_999"

wav_scp = pd.read_csv("data/test/wav.scp", delimiter=" ", names=["utt","path"])
test_wav = wav_scp[wav_scp.utt==utt_id].path.iloc[0]
print(test_wav)

ali = pd.read_csv("wav_ali/"+utt_id+".txt", delimiter="\t", names=["pyid","utt","b","start","dur","spk","py"])
ali = ali.sort_values('start')
py = ali["py"].tolist()
print(py)
dur = ali["dur"].tolist()
print(dur)

utt2_tran = dict()
with open("exp/tri4b/decode_test_word/scoring_kaldi/penalty_0.0/7.txt", "r") as rf:
	for line in rf:
		words = line.split()
		utt2_tran[words[0]] = "".join(words[1:])
tran = utt2_tran[utt_id]
print(tran)

utt2_true_tran = dict()
with open("exp/tri4b/decode_test_word/scoring_kaldi/test_filt.txt", "r") as rf:
	for line in rf:
		words = line.split()
		utt2_true_tran[words[0]] = "".join(words[1:])
true_tran = utt2_true_tran[utt_id]
print(true_tran)

word2py = dict()
with open("data/dict/lexicon.txt", "r") as rf:
	for line in rf:
		tokens = line.split()
		word2py[tokens[0]] = tokens[1:]
cons_len = 0
true_py = []
while cons_len < len(tran):
	for i in range(4,-1,-1):
		try: 
			true_py += word2py[tran[cons_len:cons_len+i]]
			cons_len += i
			break
		except Exception as e:
			#print(e)
			pass
		if i == 0:
			print("Error: Cannot find py.")
			exit()
print(true_py)


def align(py, dur, true_py):
    align_py = []
    align_dur = []
    py_cons = 0
    for k,true_py_ in enumerate(true_py):
        for i,py_ in enumerate(py[py_cons:py_cons+4]):
            if py_ == true_py_:
                align_py.append(py_)
                align_dur.append(dur[i+py_cons])
                py_cons += i+1
                break
        if len(align_py) <= k:
            align_py.append('x')
            align_dur.append(0)
    return align_py, align_dur
align_py, align_dur = align(py, dur, true_py)
print(align_py)
print(align_dur)

print('总字数：',len(tran))
print('非重复字数的总个数：',len(set(tran)))
#print('有意义字数：',len([1 for w in align_words if w != 'x']))

y, sr = librosa.load(test_wav, sr=8000)
plt.plot(y)
plt.show()
print(y.shape)
total_time = 0
for time in dur:
    total_time += time
total_align_time = 0
for time in align_dur:
    total_align_time += time
total_silence_time = 0
for x in range(y.shape[0]-10):
    if np.mean(np.abs(y[x:x+100])) < 0.001:
        total_silence_time += 1/sr
silence_count = 0
is_silence = False
for x in range(y.shape[0]-int(sr*0.25)):
    if not is_silence and np.amax(y[x:x+int(sr*0.25)]) < 0.01:
        silence_count += 1
        is_silence = True
    if y[x] >= 0.01:
        is_silence = False
print('总时间：',y.shape[0]/sr,'秒')
print('发音时间：',total_time,'秒')
print('有意义发音时间：',total_align_time,'秒')
print('停顿总时间：',total_silence_time,'秒')
print('停顿总次数：',silence_count,'次')

print('语速：',len(tran)/(y.shape[0]/sr),'字数/总时间')
print('发音语速：',len(tran)/total_time,'字数/发音总时间')
#print('有意义产出语速：',len([1 for w in align_words if w != 'x'])/(y.shape[0]/sr),'有意义的字数/总时间')
#print('pruned有意义产出语速：',len([1 for w in align_words if w != 'x'])/total_align_time,'有意义字数/有意义的发音总时间')
print('平均每次停顿时长：',((y.shape[0]/sr)-total_time)/silence_count,'（总时间-发音时间）/停顿次数')
print('停顿频率：',((y.shape[0]/sr)-total_time)/(y.shape[0]/sr),'（总时间-发音时间）/总时间')
print('Token Type Ratio：',len(set(tran))/len(tran),'非重复字数的总个数/总字数')