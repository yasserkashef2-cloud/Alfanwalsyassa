import re,json
def norm(s):
    s=re.sub(r'[ً-ٰٟـ]','',s)
    s=re.sub('[إأآٱ]','ا',s).replace('ى','ي').replace('ؤ','و').replace('ئ','ي')
    return s
def stem(w):
    w=norm(w)
    for p in ['وال','بال','لل','كال','فال','ال','و','ب','ل','ك','ف','س']:
        if w.startswith(p) and len(w)-len(p)>=3: w=w[len(p):];break
    for sfx in ['ها','هم','هن','نا','كم','ات','ون','ين','ان','ة','ه','ي','ا','ك']:
        if w.endswith(sfx) and len(w)-len(sfx)>=3: w=w[:-len(sfx)];break
    return w
def src_text(n):
    v=json.load(open('videos.json'));t=json.load(open('texts_raw.json'))
    if n<=7:
        d=v['V%d'%n]
        return ' '.join(d['lines']) if d['kind']=='summary' else ' '.join(s.get('text','') for s in d['segs'])
    return ' '.join(x['text'] for x in t['T%d'%(n-7)])
