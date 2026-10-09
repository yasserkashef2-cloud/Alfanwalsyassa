# -*- coding: utf-8 -*-
"""Generator for «الفن والسياسة» virtual book. Run: python3 build.py"""
import json, re, html, shutil, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from norm import norm, stem
from content_u1 import U, I
import content_u3  # noqa  (adds units 3-5 to U and I)
from verb_gloss import VG
from connectors_data import GROUPS, SUPP, CLOZE
from flags import FLAGS_G, FLAGS_C, FLAGS_V

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, 'book')
esc = html.escape

VOC = json.load(open(f'{ROOT}/vocab.json'))
TXT = json.load(open(f'{ROOT}/texts_raw.json'))
VID = json.load(open(f'{ROOT}/videos.json'))
CD = json.load(open(f'{ROOT}/cando_all.json'))
THEM = json.load(open(f'{ROOT}/thematic.json'))

U[2]['gap'] = ('تضم هذه الوحدة قراءتين واستماعًا واحدًا فقط، لأن المواد المرفقة لا تتضمن استماعًا ثانيًا عن الجرافيتي. '
               'وقد تُرك مكانه فارغًا ولم يُملأ بمواد من خارج المقرر (انظر تقرير المصادر).')

# ------------------------------------------------------------------ items
ITEMS = [
    ('u1', 'r1', 'T1'), ('u1', 'l1', 'V1'), ('u1', 'r2', 'T2'), ('u1', 'l2', 'V2'),
    ('u2', 'r1', 'T3'), ('u2', 'l1', 'V3'), ('u2', 'r2', 'T4'),
    ('u3', 'r1', 'T7'), ('u3', 'l1', 'V4'),
    ('u4', 'r1', 'T5'), ('u4', 'l1', 'V6'), ('u4', 'r2', 'T6'), ('u4', 'l2', 'V7'),
    ('u5', 'r1', 'T8'), ('u5', 'l1', 'V5'), ('u5', 'r2', 'T9'), ('u5', 'r3', 'T10'),
]
ARNUM = {'1': '١', '2': '٢', '3': '٣'}
YT = {'V1': ('bOxwRc0iQLQ', 'الوتر الحساس | الشيخ إمام وأحمد فؤاد نجم، الثنائي الذي قصف جبهة الأنظمة المصرية بالأغاني', 'AJ+ كبريت'),
      'V2': ('l167nYLAbb8', 'فرقة كايروكي : من ميدان التحرير إلى الكيف', 'فرانس 24'),
      'V3': ('pPfKgLNlUXs', 'الغرافيتي فى مصر .. معركة المسح والرسم / Graffiti in Egypt', 'BBC عربي (BBCcairo)'),
      'V4': ('TC3NjH3PT_M', 'المشربية - الحلي عند الفراعنة', 'القناة الثانية المصرية'),
      'V5': ('fMM-96kxdws', 'مفهوم السينما المستقلة.. وكيف نشأت الأفلام المستقلة المصرية؟ وما هو أول فيلم مستقل مصري؟', 'قربة | Qurbah'),
      'V6': ('ixECceSBLAQ', 'History of Comics in Egypt - تاريخ القصص المصورة في مصر', 'Sutur Misria | سطور مصرية'),
      'V7': ('go2C083EUe4', 'الرسام بهجت عثمان .. بهجاتوس رئيس بهجاتيا العظمى', 'الجزيرة — «خارج النص»')}
REG = {'V1': 'فصحى مبسّطة ولهجة شامية في التعليق، وعامية مصرية في الأغاني',
       'V2': 'مقابلة تلفزيونية بالفصحى والعامية المصرية (يُتحقق منها عند الاستماع)', 'V3': 'فصحى وعامية مصرية بحسب المتحدثين (يُتحقق منها عند الاستماع)',
       'V4': 'فصحى', 'V5': 'فصحى إعلامية', 'V6': 'عامية مصرية مع فصحى', 'V7': 'فصحى (الراوي) وعامية مصرية (الضيوف والتسجيل الأرشيفي)'}


def vocab_n(code):
    return int(code[1:]) if code[0] == 'V' else 7 + int(code[1:])


def item_id(u, s):
    return f'{u}-{s}'


def item_label(s):
    k = 'قراءة' if s[0] == 'r' else 'استماع'
    return f'{k} {ARNUM[s[1]]}'


def item_title(code):
    if code[0] == 'V':
        return YT[code][1]
    return next(x['text'] for x in TXT[code] if x['role'] == 'title')


ITEMMETA = {}
for u, s, code in ITEMS:
    ITEMMETA[item_id(u, s)] = dict(u=u, s=s, code=code, kind='read' if code[0] == 'T' else 'listen',
                                   title=item_title(code), label=item_label(s))
ORDER = ['cover', 'contents', 'guide', 'album']
for n in range(1, 6):
    ORDER.append(f'u{n}')
    ORDER += [item_id(u, s) for u, s, c in ITEMS if u == f'u{n}']
ORDER += ['connectors', 'cando', 'vocab', 'thematic', 'sources', 'tech']
TITLES = {'cover': 'الغلاف', 'contents': 'فهرس المحتويات', 'guide': 'دليل الاستخدام', 'album': 'مدخل المقرر: ألبوم مصر',
          'connectors': 'أدوات الربط والروابط الخطابية', 'cando': 'مرجع عبارات «أستطيع أن» (ACTFL)',
          'vocab': 'فهرس المفردات', 'thematic': 'ملحق: المعجم الموضوعي (B2)', 'sources': 'المصادر والتقرير',
          'tech': 'ملاحظة تقنية'}
for n in range(1, 6):
    TITLES[f'u{n}'] = f"الوحدة {ARNUM.get(str(n), n)}: {U[n]['title']}" if n < 4 else f"الوحدة {n}: {U[n]['title']}"
for k, m in ITEMMETA.items():
    TITLES[k] = f"{m['label']}: {m['title']}"
# neater unit numerals
AR_D = '٠١٢٣٤٥٦٧٨٩'
def ar_num(n):
    return ''.join(AR_D[int(c)] for c in str(n))
for n in range(1, 6):
    TITLES[f'u{n}'] = f"الوحدة {ar_num(n)}: {U[n]['title']}"

# ------------------------------------------------------------------ highlight machinery
TOK = re.compile(r'[ء-يً-ْٰـ]+')
STOP = {'من', 'على', 'في', 'عن', 'الي', 'الى', 'ما', 'لا', 'او', 'ان', 'انه', 'هذا', 'هذه', 'ذلك', 'مع', 'بين', 'كل'}


def full_text(code):
    if code[0] == 'T':
        return ' '.join(x['text'] for x in TXT[code])
    d = VID[code]
    return ' '.join(d['lines']) if d['kind'] == 'summary' else ' '.join(s.get('text', '') for s in d['segs'])


def build_keymap(n, code):
    toks = {stem(w) for w in TOK.findall(full_text(code))}
    keymap, cov = {}, {}
    for i, r in enumerate(VOC['G'][str(n)]):
        ws = [w for w in TOK.findall(r['ar']) if norm(w) not in STOP and len(norm(w)) > 2]
        cands = sorted({stem(w) for w in ws}, key=len, reverse=True)
        key = next((c for c in cands if c in toks), None)
        if key is None:
            for c in cands:
                if len(c) >= 4 and any(len(t) >= 4 and abs(len(t) - len(c)) <= 2 and (t.startswith(c) or c.startswith(t)) for t in toks):
                    key = next(t for t in toks if len(t) >= 4 and abs(len(t) - len(c)) <= 2 and (t.startswith(c) or c.startswith(t)))
                    break
        if key and key not in keymap:
            keymap[key] = i
    return keymap


def hl(text, n, keymap, used):
    out, pos = [], 0
    G = VOC['G'][str(n)]
    for m in TOK.finditer(text):
        w = m.group()
        out.append(esc(text[pos:m.start()]))
        pos = m.end()
        i = keymap.get(stem(w))
        if i is not None and i not in used:
            used.add(i)
            r = G[i]
            out.append(f'<mark class="gl" tabindex="0" role="button" data-en="{esc(r["en"], True)}" '
                       f'data-ar="{esc(r["ar"], True)}" data-ctx="{esc(r["ctx"], True)}">{esc(w)}</mark>')
        else:
            out.append(esc(w))
    out.append(esc(text[pos:]))
    return ''.join(out)


COVERAGE = {}

# ------------------------------------------------------------------ small html helpers
ICONS = {
 'menu': 'M4 6h16M4 12h16M4 18h16', 'home': 'M3 11l9-8 9 8M5 10v10h5v-6h4v6h5V10',
 'plus': 'M12 5v14M5 12h14', 'minus': 'M5 12h14', 'print': 'M7 9V3h10v6M6 17H4v-6h16v6h-2M7 14h10v7H7z',
 'eye': 'M2 12s4-7 10-7 10 7 10 7-4 7-10 7S2 12 2 12zM12 15a3 3 0 100-6 3 3 0 000 6z',
 'book': 'M4 4h7a3 3 0 013 3v13a2 2 0 00-2-2H4zM20 4h-6M20 4v14h-6',
 'headphones': 'M4 14v-2a8 8 0 0116 0v2M4 14h3v6H4zM17 14h3v6h-3z',
 'play': 'M7 4l13 8-13 8z', 'check': 'M4 12l5 5L20 6', 'link': 'M10 14a4 4 0 005.7 0l3-3a4 4 0 00-5.7-5.7l-1 1M14 10a4 4 0 00-5.7 0l-3 3a4 4 0 005.7 5.7l1-1',
 'music': 'M9 18V5l11-2v13M9 18a3 3 0 11-6 0 3 3 0 016 0zM20 16a3 3 0 11-6 0 3 3 0 016 0z',
 'spray': 'M8 10h8v11H8zM10 10V6h4v4M10 3h1M13 3h1M16 5h1M16 2h1',
 'ring': 'M12 9l3-5H9zM12 9a6 6 0 100 12 6 6 0 000-12z', 'comic': 'M4 5h16v11H11l-5 4v-4H4z',
 'film': 'M4 4h16v16H4zM8 4v16M16 4v16M4 9h4M4 15h4M16 9h4M16 15h4', 'star': 'M12 3l2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1L3.2 9.5l6.1-.9z',
 'download': 'M12 3v12M7 11l5 5 5-5M4 20h16', 'arrow-l': 'M15 5l-7 7 7 7', 'arrow-r': 'M9 5l7 7-7 7', 'list': 'M8 6h12M8 12h12M8 18h12M4 6h.01M4 12h.01M4 18h.01',
 'clock': 'M12 7v5l3 2M12 21a9 9 0 100-18 9 9 0 000 18z', 'search': 'M11 19a8 8 0 100-16 8 8 0 000 16zM21 21l-4.3-4.3',
 'info': 'M12 8h.01M11 12h1v5h1M12 21a9 9 0 100-18 9 9 0 000 18z', 'warn': 'M12 4l9 16H3zM12 10v4M12 17h.01',
 'globe': 'M12 21a9 9 0 100-18 9 9 0 000 18zM3 12h18M12 3a14 14 0 010 18M12 3a14 14 0 000 18', 'top': 'M12 19V5M6 11l6-6 6 6',
}


ICONS['graffiti'] = ICONS['spray']


def ic(name, cls=''):
    return f'<svg class="ic {cls}" viewBox="0 0 24 24" aria-hidden="true"><path d="{ICONS[name]}"/></svg>'


def sprite():
    return ''


def chip(txt, cls=''):
    return f'<span class="chip {cls}">{txt}</span>'


def ar_seconds(t):
    p = [int(x) for x in t.split(':')]
    return p[0] * 3600 + p[1] * 60 + p[2] if len(p) == 3 else p[0] * 60 + p[1]


def back_links(u=None):
    s = '<nav class="backnav" aria-label="تنقّل سريع"><a class="btn ghost" href="#/contents">' + ic('list') + ' فهرس المحتويات</a>'
    if u:
        s += f'<a class="btn ghost" href="#/{u}">' + ic('home') + ' مقدمة الوحدة</a>'
    return s + '</nav>'


SUPP_TAG = '<span class="tag supp" title="مادة تعليمية أضافها معدّ الكتاب، وليست من مواد المقرر المرفقة">إضافة تعليمية</span>'
SRC_TAG = '<span class="tag src" title="من مواد المقرر المرفقة كما وردت">من مواد المقرر</span>'

# ------------------------------------------------------------------ Can-Do quoting
LV_AR = {'Advanced Low': 'متقدّم — أدنى', 'Advanced Mid': 'متقدّم — أوسط', 'Advanced High': 'متقدّم — أعلى', 'Advanced': 'متقدّم',
         'Intermediate Low': 'متوسط — أدنى', 'Intermediate Mid': 'متوسط — أوسط', 'Intermediate High': 'متوسط — أعلى',
         'Intermediate': 'متوسط', 'Superior': 'ممتاز'}
MODE_AR = {'Interpretive': 'تفسيري', 'Interpersonal': 'تفاعلي', 'Presentational': 'عرضي', 'Intercultural': 'تواصل بين الثقافات'}


def cando_block(ids, compact=False):
    s = '<div class="cando-list">'
    for cid in ids:
        c = CD[cid]
        s += (f'<details class="cd"><summary><b class="cdid">{cid}</b> <span class="en" dir="ltr">{esc(c["q"])}</span></summary>'
              f'<blockquote class="en quote" dir="ltr"><p class="bench">{esc(c["bench"])}</p>')
        for l in c['levels']:
            s += f'<p><b>{esc(l["level"])}:</b> {esc(l["text"])}</p>'
        s += '</blockquote></details>'
    return s + '<p class="srcnote">النصوص الإنجليزية مقتبسة حرفيًا من <i>ACTFL/NCSSFL Can-Do Statements (2024)</i> — ملفا المستوى المتقدم والمتوسط المرفقان بالمقرر.</p></div>'


def chips_cd(ids):
    return ' '.join(f'<a class="chip cdchip" href="#/cando" title="{esc(CD[i]["q"], True)}">{i}</a>' for i in ids)


# ------------------------------------------------------------------ vocabulary section
def vocab_section(n, code, u, iid):
    G, V, C = VOC['G'][str(n)], VOC['V'][str(n)], VOC['C'][str(n)]
    flagsG = FLAGS_G.get(n, {})
    reg = REG.get(code, 'فصحى (نص مكتوب)')
    s = [f'<section class="vocab" aria-labelledby="vh-{iid}"><h2 id="vh-{iid}" class="sec-h">{ic("book")} مفردات قبل {"القراءة" if code[0]=="T" else "الاستماع"}</h2>'
         f'<p class="note">{SRC_TAG} القوائم أدناه كما وردت في مواد المقرر. <b>مستوى اللغة:</b> المفردات والتراكيب مكتوبة بالفصحى (MSA)؛ '
         f'ومستوى المادة نفسها: {esc(reg)}. المعاني الإنجليزية للأفعال إضافة تعليمية وسِمتها {SUPP_TAG}.</p>']
    # 1 basic
    s.append(f'<details class="vsec" open><summary><span>١. المفردات الأساسية</span><em>{len(G)}</em></summary><div class="vtools">'
             f'<button class="btn small" data-flipall="open">إظهار المعاني</button><button class="btn small" data-flipall="close">إخفاء المعاني</button></div>'
             f'<div class="cards">')
    for i, r in enumerate(G):
        k = f'{iid}:g{i}'
        fl = flagsG.get(norm(r['ar']))
        flhtml = ''
        if fl:
            flhtml = f'<p class="flag">{ic("warn")} <b>تنبيه:</b> {esc(fl[0])}' + (f' — الصيغة المقترحة: <span class="ar-s">{esc(fl[1])}</span>' if fl[1] else '') + '</p>'
        s.append(f'<div class="vcard{" flagged" if fl else ""}" data-key="{k}"><button class="vc-flip" aria-expanded="false">'
                 f'<span class="vc-ar">{esc(r["ar"])}</span><span class="vc-hint">اضغط لإظهار المعنى</span>'
                 f'<span class="vc-back"><span class="vc-en en" dir="ltr">{esc(r["en"])}</span>'
                 f'<span class="vc-ctx"><small>في السياق:</small> {esc(r["ctx"])}</span></span></button>{flhtml}'
                 f'<button class="vc-learn" aria-pressed="false" title="علّم هذه الكلمة بأنني تعلمتها">{ic("star")}<span class="sr">تعلمتها</span></button></div>')
    s.append('</div></details>')
    # 2 verbs
    s.append(f'<details class="vsec"><summary><span>٢. الأفعال والتراكيب الفعلية</span><em>{len(V)}</em></summary>'
             f'<div class="tablewrap"><table class="vt"><thead><tr><th>المصدر</th><th>المضارع</th><th>الماضي</th><th class="en" dir="ltr">English {SUPP_TAG}</th></tr></thead><tbody>')
    for j, r in enumerate(V):
        fl = FLAGS_V.get((n, norm(r['past'])))
        gl = VG.get(norm(r['past']), '')
        s.append(f'<tr><td class="ar">{esc(r["masdar"])}</td><td class="ar">{esc(r["pres"])}</td><td class="ar">{esc(r["past"])}</td>'
                 f'<td class="en" dir="ltr">{esc(gl)}{(" <span class=flagtxt>⚠ " + esc(fl) + "</span>") if fl else ""}</td></tr>')
    s.append('</tbody></table></div><p class="note small">المصدر والمضارع والماضي كما وردت في المقرر؛ ولم تُراجع كل التشكيلات مراجعة لغوية كاملة.</p></details>')
    # 3 collocations
    colls = [(i, r) for i, r in enumerate(C) if 'ربط' not in norm(r['type'])]
    conns = [(i, r) for i, r in enumerate(C) if 'ربط' in norm(r['type'])]
    s.append(f'<details class="vsec"><summary><span>٣. التعبيرات الاصطلاحية والتعبيرات الشائعة (التراكيب اللفظية)</span><em>{len(colls)}</em></summary>'
             f'<p class="note small">تسميها مواد المقرر «تراكيب لفظية»؛ وهي تضم تعبيرات شائعة ومتلازمات لفظية، ولا يُعدّ كلها تعبيرًا اصطلاحيًا بالمعنى الضيق.</p><div class="cards wide">')
    for i, r in colls:
        fl = FLAGS_C.get((n, i))
        s.append(f'<div class="vcard{" flagged" if fl else ""}" data-key="{iid}:c{i}"><button class="vc-flip" aria-expanded="false"><span class="vc-ar">{esc(r["ar"])}</span>'
                 f'<span class="vc-hint">اضغط لإظهار المعنى</span><span class="vc-back"><span class="vc-en en" dir="ltr">{esc(r["en"])}</span></span></button>'
                 + (f'<p class="flag">{ic("warn")} <b>تنبيه:</b> {esc(fl[0])}' + (f' — المقترح: <span class="ar-s">{esc(fl[1])}</span>' if fl[1] else '') + '</p>' if fl else '')
                 + f'<button class="vc-learn" aria-pressed="false">{ic("star")}<span class="sr">تعلمتها</span></button></div>')
    s.append('</div></details>')
    # 4 connectors
    s.append(f'<details class="vsec"><summary><span>٤. أدوات الربط والروابط الخطابية</span><em>{len(conns)}</em></summary><div class="cards wide">')
    for i, r in conns:
        fl = FLAGS_C.get((n, i))
        s.append(f'<div class="vcard conn{" flagged" if fl else ""}" data-key="{iid}:c{i}"><button class="vc-flip" aria-expanded="false"><span class="vc-ar">{esc(r["ar"])}</span>'
                 f'<span class="vc-hint">اضغط لإظهار المعنى</span><span class="vc-back"><span class="vc-en en" dir="ltr">{esc(r["en"])}</span></span></button>'
                 + (f'<p class="flag">{ic("warn")} <b>تنبيه:</b> {esc(fl[0])}' + (f' — المقترح: <span class="ar-s">{esc(fl[1])}</span>' if fl[1] else '') + '</p>' if fl else '')
                 + f'<button class="vc-learn" aria-pressed="false">{ic("star")}<span class="sr">تعلمتها</span></button></div>')
    s.append(f'</div><p class="note small"><a href="#/connectors">{ic("link")} صفحة أدوات الربط الكاملة والتمارين</a></p></details>')
    # 5 opinion
    ex = U[int(u[1])]['expr']
    s.append(f'<details class="vsec"><summary><span>٥. تعبيرات الرأي والتحليل والمقارنة</span><em>{len(ex["items"])}</em></summary>'
             f'<p class="note small">{SUPP_TAG} {esc(ex["title"])}</p><div class="tablewrap"><table class="vt"><thead><tr><th>التعبير</th><th class="en" dir="ltr">English</th><th>مثال (إضافة تعليمية)</th></tr></thead><tbody>')
    for a, e, x in ex['items']:
        s.append(f'<tr><td class="ar">{esc(a)}</td><td class="en" dir="ltr">{esc(e)}</td><td class="ar">{esc(x)}</td></tr>')
    s.append('</tbody></table></div></details></section>')
    return ''.join(s)


# ------------------------------------------------------------------ reading / listening bodies
def reading_body(code, n, iid):
    keymap = build_keymap(n, code)
    used = set()
    parts = []
    pn = 0
    nav = []
    for x in TXT[code]:
        r, t = x['role'], x['text']
        if r == 'title':
            continue
        if r == 'byline':
            parts.append(f'<p class="byline">{esc(t)}</p>')
        elif r == 'source':
            parts.append(f'<p class="srcline">{esc(t)}</p>')
        elif r == 'h':
            parts.append(f'<h3 class="sub-h">{hl(t, n, keymap, used)}</h3>')
        elif r == 'pq':
            parts.append(f'<aside class="pq" aria-label="اقتباس بارز كما ورد في المصدر"><span class="pqlab">اقتباس بارز من المصدر</span>{hl(t, n, keymap, used)}</aside>')
        elif r == 'q':
            parts.append(f'<p class="iq"><span class="iqlab">سؤال المحاور</span> {hl(t, n, keymap, used)}</p>')
        else:
            pn += 1
            nav.append(pn)
            parts.append(f'<p class="para" id="{iid}-p{pn}" data-p="{pn}"><a class="pnum" href="#/{iid}" data-scroll="#{iid}-p{pn}" aria-label="فقرة {pn}">{pn}</a>{hl(t, n, keymap, used)}</p>')
    G = VOC['G'][str(n)]
    COVERAGE[iid] = (len(used), len(G))
    paranav = ''.join(f'<button class="pn" data-scroll="#{iid}-p{i}">{i}</button>' for i in nav)
    return ''.join(parts), paranav, pn


def listening_body(code, n, iid):
    vid, vt, ch = YT[code]
    return (f'<div class="video" data-yt="{vid}"><div class="vposter"><button class="vplay" aria-label="شغّل الفيديو داخل الصفحة">{ic("play")}<span>شغّل الفيديو هنا</span></button>'
            f'<p class="vmeta">{esc(ch)} — {esc(vt)}</p></div><div class="vframe"></div></div>'
            f'<p class="vlinks"><a class="btn primary" href="https://www.youtube.com/watch?v={vid}" target="_blank" rel="noopener">{ic("link")} افتح الفيديو على يوتيوب (صفحة جديدة)</a></p>'
            f'<p class="note small vlinks">استمع أكثر من مرة: أولًا للفكرة العامة، ثم لتفاصيل محددة؛ ودوّن ما تفهمه قبل الإجابة عن الأسئلة.</p>')


def ref_chip(iid, ref, kind):
    if ':' in ref:
        sec = ar_seconds(ref)
        return f'<button class="ref time" data-seek="{sec}" title="انتقل إلى {ref} في الفيديو">{ic("clock")}{ref}</button>'
    m = re.fullmatch(r'p(\d+)(?:-(\d+))?', ref)
    a, b = m.group(1), m.group(2)
    lab = f'ف {a}' + (f'–{b}' if b else '')
    return f'<button class="ref" data-scroll="#{iid}-p{a}" title="انتقل إلى الفقرة {a}">{lab}</button>'


def questions_block(code, iid, kind):
    c = I[code]
    s = [f'<section class="qs" aria-labelledby="qh-{iid}"><h2 id="qh-{iid}" class="sec-h">{ic("info")} بعد {"القراءة" if kind=="read" else "الاستماع"}: أسئلة مفتوحة</h2>'
         f'<p class="note">{SUPP_TAG} أسئلة بالعربية يمكن الإجابة عنها من المادة نفسها؛ أجب بجمل كاملة وبأسلوبك، واستعن بأزرار «ابحث في» للعودة إلى موضع الدليل. تُحفظ إجاباتك في متصفحك فقط، ويمكنك تنزيلها.</p><ol class="qlist">']
    for j, (typ, txt, refs) in enumerate(c['q']):
        rs = ''.join(ref_chip(iid, r, kind) for r in refs)
        s.append(f'<li><div class="qh"><span class="qtype">{esc(typ)}</span></div><p class="qt">{esc(txt)}</p>'
                 + (f'<p class="refs"><span>ابحث في:</span> {rs}</p>' if rs else '')
                 + f'<label class="sr" for="a-{iid}-{j}">إجابتك</label><textarea id="a-{iid}-{j}" class="ans" rows="3" data-ans="{iid}:{j}" placeholder="اكتب إجابتك هنا…"></textarea></li>')
    s.append('</ol>')
    s.append(f'<h3 class="sub-h">نقاش مقارن ثقافي</h3><p class="note small">لا تطلب الأسئلة مقابلة «الشرق» بـ«الغرب»؛ ابحث عن التنوع داخل كل مجتمع، وادعم رأيك بمثال محدد.</p><ol class="qlist disc-l">')
    for j, d in enumerate(c['disc']):
        s.append(f'<li><p class="qt">{esc(d["q"])}</p><p class="cmp">{"".join(chip(esc(x)) for x in d["compare"])}</p>'
                 f'<textarea class="ans" rows="4" data-ans="{iid}:d{j}" aria-label="إجابة النقاش {j+1}" placeholder="اكتب أفكارك هنا…"></textarea></li>')
    s.append(f'</ol><div class="ansbar"><button class="btn" data-download="{iid}">{ic("download")} نزّل إجاباتي (نص)</button><span class="note small saved" aria-live="polite"></span></div></section>')
    return ''.join(s)


def notes_block(code):
    c = I[code]
    s = [f'<section class="lnotes"><h2 class="sec-h">{ic("info")} ملاحظات لغوية وثقافية {SUPP_TAG}</h2><ul>']
    for lab, t in c['notes']:
        if lab.startswith('تنبيه حول النص المقروء'):
            continue
        s.append(f'<li><b>{esc(lab)}:</b> {esc(t)}</li>')
    s.append('</ul></section>')
    return ''.join(s)


def prev_next(iid):
    i = ORDER.index(iid)
    pv = ORDER[i - 1] if i > 0 else None
    nx = ORDER[i + 1] if i < len(ORDER) - 1 else None
    s = '<nav class="pager" aria-label="السابق والتالي">'
    s += (f'<a class="btn" href="#/{nx}" rel="next">{esc(TITLES[nx])[:46]} {ic("arrow-l")}</a>' if nx else '<span></span>')
    s += (f'<a class="btn" href="#/{pv}" rel="prev">{ic("arrow-r")} {esc(TITLES[pv])[:46]}</a>' if pv else '<span></span>')
    return s + '</nav>'


def item_view(iid):
    m = ITEMMETA[iid]
    u, code, kind = m['u'], m['code'], m['kind']
    n = vocab_n(code)
    c = I[code]
    un = int(u[1])
    color = 'read' if kind == 'read' else 'listen'
    head = (f'<header class="ihead {color}"><p class="kicker">{ic("book" if kind=="read" else "headphones")} {esc(U[un]["title"])} · {esc(m["label"])}</p>'
            f'<h1 class="ititle {color}" tabindex="-1">{esc(m["title"])}</h1>')
    if kind == 'read':
        meta = [x['text'] for x in TXT[code] if x['role'] in ('byline', 'source')]
        head += '<p class="meta">' + (' — '.join(esc(x) for x in meta) if meta else 'المصدر: كما ورد في مواد المقرر (لم يُذكر اسم الكاتب أو الجهة في الملف المرفق)') + '</p>'
    else:
        head += f'<p class="meta">{esc(YT[code][2])} · فيديو يوتيوب</p>'
    head += f'<p class="lead">{esc(c["lead"])} {SUPP_TAG}</p><p class="cdline"><span>أهداف «أستطيع أن»:</span> {chips_cd(c["cando"])}</p></header>'
    pre = (f'<section class="pre"><h2 class="sec-h">{ic("info")} قبل أن {"تقرأ" if kind=="read" else "تستمع"}: تفكير وتوقع {SUPP_TAG}</h2><ul>'
           + ''.join(f'<li>{esc(x)}</li>' for x in c['pre']) + '</ul></section>')
    voc = vocab_section(n, code, u, iid)
    if kind == 'read':
        body, paranav, npar = reading_body(code, n, iid)
        tools = (f'<div class="rtools" role="group" aria-label="أدوات القراءة"><span class="grp"><button class="btn small" data-fs="-1" aria-label="تصغير الخط">{ic("minus")}A</button>'
                 f'<button class="btn small" data-fs="1" aria-label="تكبير الخط">{ic("plus")}A</button><button class="btn small" data-fs="0">الحجم الافتراضي</button></span>'
                 f'<label class="chk"><input type="checkbox" data-glt checked> تظليل مفردات الكتاب في النص</label>'
                 f'<button class="btn small" data-readmode>{ic("eye")} وضع القراءة</button></div>'
                 f'<div class="paranav" role="navigation" aria-label="الفقرات"><span>الفقرات:</span>{paranav}</div>')
        art = (f'<section class="article" aria-labelledby="th-{iid}"><h2 id="th-{iid}" class="sec-h read">{ic("book")} النص الأصلي</h2>'
               f'<p class="note small">{SRC_TAG} النص كما ورد في المقرر، مقسّمًا إلى فقرات مرقّمة. التظليل الأصفر آلي (أول ورود لمفردة من قائمة هذه المادة)؛ اضغط على الكلمة لرؤية معناها. '
               f'<span class="cov" data-cov="{COVERAGE[iid][0]}/{COVERAGE[iid][1]}">ظُلّلت {COVERAGE[iid][0]} من {COVERAGE[iid][1]} مفردة</span></p>{tools}'
               f'<div class="rtext ar" lang="ar" dir="rtl">{body}</div></section>')
    else:
        art = (f'<section class="article" aria-labelledby="th-{iid}"><h2 id="th-{iid}" class="sec-h listen">{ic("headphones")} الفيديو</h2>'
               f'{listening_body(code, n, iid)}</section>')
    done = (f'<div class="donebar"><label class="chk big"><input type="checkbox" data-done="{iid}"> أنهيتُ هذه المادة (قراءة/استماع، مفردات، أسئلة)</label></div>')
    prog = '<div class="rprog" aria-hidden="true"><i></i></div>'
    return (f'<section class="view item {color}" id="v-{iid}" data-title="{esc(TITLES[iid], True)}" hidden>{prog}{back_links(u)}{head}{pre}{voc}{art}'
            f'{questions_block(code, iid, kind)}{notes_block(code)}{done}{prev_next(iid)}</section>')


# ------------------------------------------------------------------ unit view
def unit_view(n):
    u = U[n]
    uid = f'u{n}'
    items = [(iid, m) for iid, m in ITEMMETA.items() if m['u'] == uid]
    s = [f'<section class="view unit" id="v-{uid}" data-title="{esc(TITLES[uid], True)}" hidden>{back_links()}']
    s.append(f'<header class="uhero"><picture><source srcset="assets/img/{u["img"]}.webp" type="image/webp"><img src="assets/img/{u["img"]}.jpg" alt="ملصق الوحدة: {esc(u["title"], True)}" loading="lazy"></picture>'
             f'<div><p class="kicker">{ic(u["icon"])} الوحدة {ar_num(n)} من ٥</p><h1 tabindex="-1">{esc(u["title"])}</h1><p class="en etitle" dir="ltr">{esc(u["en"])}</p>'
             f'<p class="tagline">{esc(u["tagline"])}</p><div class="uprog"><div class="bar"><i data-uprog="{uid}"></i></div><span data-uprogt="{uid}"></span></div></div></header>')
    s.append(f'<section><h2 class="sec-h">{ic("globe")} الأهمية الثقافية والسياسية {SUPP_TAG}</h2>' + ''.join(f'<p>{esc(p)}</p>' for p in u['significance']) + '</section>')
    if u.get('gap'):
        s.append(f'<aside class="gapnote">{ic("info")} <b>ملاحظة عن بنية الوحدة:</b> {esc(u["gap"])}</aside>')
    s.append(f'<section><h2 class="sec-h">{ic("check")} أهداف الوحدة {SUPP_TAG}</h2><ul class="obj">' + ''.join(f'<li>{esc(o)}</li>' for o in u['objectives']) + '</ul></section>')
    s.append(f'<section><h2 class="sec-h">{ic("star")} عبارات «أستطيع أن» (ACTFL) المرتبطة بالوحدة</h2>{cando_block(u["cando"])}</section>')
    s.append(f'<section><h2 class="sec-h">{ic("arrow-l")} كيف تسهم الوحدة في تنمية الكفاءة؟ {SUPP_TAG}</h2><p>{esc(u["contribution"])}</p>'
             f'<p class="note">لا يعني إنجازُ نشاطٍ هنا أنك «بلغتَ» مستوى معينًا؛ فالتقييم الرسمي للكفاءة يتطلب أداءً موثقًا ومقارنة بمعايير ACTFL. استعمل الجدول أداةَ تأمل ذاتي فقط.</p></section>')
    s.append(f'<section><h2 class="sec-h">{ic("list")} المواد</h2><ol class="uitems">')
    for iid, m in items:
        s.append(f'<li class="{"read" if m["kind"]=="read" else "listen"}"><a href="#/{iid}"><span class="lab">{ic("book" if m["kind"]=="read" else "headphones")} {esc(m["label"])}</span>'
                 f'<span class="tt">{esc(m["title"])}</span><span class="dn" data-dn="{iid}" aria-label="مكتمل">{ic("check")}</span></a></li>')
    s.append('</ol></section>')
    # proficiency map
    s.append(f'<section class="pmap"><h2 class="sec-h">{ic("star")} خريطة الكفاءة والتأمل الذاتي</h2>'
             f'<p class="note">{SUPP_TAG} لكل نشاط عبارة «أستطيع أن» ذات صلة ومصدرها وما يمكنك فعله والمهارة ومهمة تأمل. اختر تقديرك الذاتي؛ يُحفظ في متصفحك فقط. هذا تأمل ذاتي وليس اختبارًا ولا شهادة بمستوى.</p>'
             f'<div class="tablewrap"><table class="vt map"><thead><tr><th>النشاط (المصدر)</th><th>«أستطيع أن» ذات الصلة</th><th>المهارة</th><th>ما يمكنني فعله</th><th>سؤال التأمل</th><th>تقديري الذاتي</th></tr></thead><tbody>')
    for k, mp in enumerate(u['map']):
        cid = mp['cd']
        s.append(f'<tr><td>{esc(mp["act"])}</td><td><a class="chip cdchip" href="#/cando">{cid}</a><div class="en small" dir="ltr">{esc(CD[cid]["levels"][0]["text"])}</div></td>'
                 f'<td>{esc(mp["skill"])}</td><td>{esc(mp["can"])}</td><td>{esc(mp["reflect"])}</td>'
                 f'<td><select data-cds="{uid}:{k}" aria-label="تقديري الذاتي: {esc(mp["act"], True)}"><option value="">—</option><option value="1">لم أجرّب بعد</option>'
                 f'<option value="2">أحتاج إلى مزيد من التدريب</option><option value="3">أستطيع بمساعدة</option><option value="4">أستطيع باستقلال</option></select></td></tr>')
    s.append('</tbody></table></div></section>')
    f = u['final']
    s.append(f'<section class="final"><h2 class="sec-h">{ic("download")} {esc(f["title"])} {SUPP_TAG}</h2><p>{esc(f["prompt"])}</p><ul class="checklist">'
             + ''.join(f'<li><label class="chk"><input type="checkbox" data-chk="{uid}:f{j}"> {esc(x)}</label></li>' for j, x in enumerate(f['checklist']))
             + '</ul></section>')
    ex = u['expr']
    s.append(f'<section><h2 class="sec-h">{ic("list")} {esc(ex["title"])} {SUPP_TAG}</h2><div class="tablewrap"><table class="vt"><thead><tr><th>التعبير</th><th class="en" dir="ltr">English</th><th>مثال</th></tr></thead><tbody>'
             + ''.join(f'<tr><td class="ar">{esc(a)}</td><td class="en" dir="ltr">{esc(e)}</td><td class="ar">{esc(x)}</td></tr>' for a, e, x in ex['items']) + '</tbody></table></div></section>')
    s.append(f'<nav class="pager"><a class="btn" href="#/{items[0][0]}">{ic("arrow-l")} ابدأ بـ{esc(items[0][1]["label"])}</a><a class="btn" href="#/contents">{ic("list")} العودة إلى الفهرس</a></nav></section>')
    return ''.join(s)


# ------------------------------------------------------------------ other views
def cover_view():
    return (f'<section class="view cover" id="v-cover" data-title="الغلاف"><div class="cover-in"><picture><source srcset="assets/img/cover.webp" type="image/webp">'
            f'<img src="assets/img/cover.jpg" alt="غلاف الكتاب: لوحة كروشيه زرقاء عليها عنوان «الفن والسياسة» وشمس ذهبية خلف الأهرامات ومسجد ومركبين شراعيين على النيل، وفي أسفلها خمس أيقونات: الموسيقا والسينما والحلي والقصص المصورة والجرافيتي" fetchpriority="high"></picture>'
            f'<div class="cover-txt"><p class="kicker">كتاب تفاعلي لمتعلمي العربية لغةً أجنبية — المستوى المتقدم</p><h1 tabindex="-1">الفن والسياسة</h1>'
            f'<p class="en sub" dir="ltr">Art and Politics — an interactive reader for advanced learners of Arabic</p>'
            f'<p class="subt">من الأغنية إلى الجدار، ومن الحلي إلى الشاشة: خمس وحدات عن مصر وفنونها وعلاقتها بالسلطة والمجتمع</p>'
            f'<p class="by">إعداد وانتقاء: <b>ياسر كاشف</b><br><span class="en" dir="ltr">Prepared and curated by Yasser Kashef</span></p>'
            f'<p class="by sm">مواد المقرر المجمّعة — ربيع 2026 · Collected Spring 2026</p>'
            f'<p class="cta"><a class="btn primary" href="#/contents">{ic("book")} ابدأ التصفح</a> <a class="btn" href="#/guide">{ic("info")} دليل الاستخدام</a> <a class="btn" href="#/album">{ic("globe")} مدخل المقرر: ألبوم مصر</a></p>'
            f'<p class="copy en" dir="ltr">© 2026 Yasser Kashef. All rights reserved. Design carried out by AI.</p></div></div></section>')


def contents_view():
    s = [f'<section class="view" id="v-contents" data-title="فهرس المحتويات" hidden><header class="phead"><h1 tabindex="-1">فهرس المحتويات</h1>'
         f'<p class="lead">اضغط على أي عنوان للانتقال إليه. العلامة ✓ تظهر بعد أن تضع علامة «أنهيتُ» في المادة.</p>'
         f'<div class="uprog"><div class="bar"><i data-bprog></i></div><span data-bprogt></span></div></header>'
         f'<ol class="toc-top"><li><a href="#/guide">{ic("info")} دليل الاستخدام</a></li><li><a href="#/album">{ic("globe")} مدخل المقرر: ألبوم مصر</a></li></ol><div class="ugrid">']
    for n in range(1, 6):
        u = U[n]
        s.append(f'<article class="ucard"><a class="uimg" href="#/u{n}" tabindex="-1" aria-hidden="true"><picture><source srcset="assets/img/{u["img"]}.webp" type="image/webp"><img src="assets/img/{u["img"]}.jpg" alt="" loading="lazy"></picture></a>'
                 f'<div class="ubody"><h2><a href="#/u{n}">{ic(u["icon"])} الوحدة {ar_num(n)}: {esc(u["title"])}</a></h2><p class="en etitle" dir="ltr">{esc(u["en"])}</p><p class="tagline">{esc(u["tagline"])}</p><ol class="mini">')
        for iid, m in ITEMMETA.items():
            if m['u'] == f'u{n}':
                s.append(f'<li class="{m["kind"]}"><a href="#/{iid}"><span class="dn" data-dn="{iid}">{ic("check")}</span> <b>{esc(m["label"])}</b> — {esc(m["title"])}</a></li>')
        s.append('</ol></div></article>')
    s.append(f'</div><h2 class="sec-h">صفحات مساندة</h2><ul class="toc-top two"><li><a href="#/connectors">{ic("link")} أدوات الربط والروابط الخطابية</a></li>'
             f'<li><a href="#/cando">{ic("star")} مرجع «أستطيع أن» (ACTFL)</a></li><li><a href="#/vocab">{ic("search")} فهرس المفردات (بحث)</a></li>'
             f'<li><a href="#/thematic">{ic("list")} المعجم الموضوعي (B2)</a></li><li><a href="#/sources">{ic("info")} المصادر والتقرير</a></li><li><a href="#/tech">{ic("info")} ملاحظة تقنية</a></li></ul></section>')
    return ''.join(s)


def guide_view():
    return (f'''<section class="view" id="v-guide" data-title="دليل الاستخدام" hidden>{back_links()}<header class="phead"><h1 tabindex="-1">دليل الاستخدام</h1><p class="lead">كيف يعمل هذا الكتاب، وما الذي جاء من مواد المقرر وما الذي أُضيف إليه.</p></header>
<section><h2 class="sec-h">{ic("list")} بنية الكتاب</h2><p>خمس وحدات بهذا الترتيب: الموسيقا والغناء، الجرافيتي، الحُلي، القصص المصورة والكوميكس، السينما. تتبع كل وحدة، حيثما توافرت المواد، ترتيب: قراءة ١، استماع ١، قراءة ٢، استماع ٢. وفي بعض الوحدات مواد أقل أو أكثر من هذا النمط لأن المواد المرفقة لا تتبعه (انظر مقدمة كل وحدة وصفحة المصادر).</p>
<p>قبل كل مادة تجد: تفكيرًا وتوقعًا، ثم مفردات في خمس فئات، ثم المادة، ثم أسئلة مفتوحة ونقاشًا مقارنًا وملاحظات لغوية.</p></section>
<section><h2 class="sec-h">{ic("info")} ما المنقول وما المضاف؟</h2><p>{SRC_TAG} يعني أن المحتوى جاء من مواد المقرر المرفقة كما هو: نصوص القراءة، والنصوص المكتوبة للفيديوهات، وقوائم المفردات والأفعال والتراكيب، والمعجم الموضوعي، وصفحتا «ألبوم مصر» و«أدوات الربط».</p>
<p>{SUPP_TAG} يعني أن معدّ الكتاب كتبه لأغراض تعليمية: مقدمات الوحدات والأهداف والأسئلة والنقاشات والملاحظات وخرائط الكفاءة والمهام الختامية، والمعاني الإنجليزية للأفعال، والروابط الإضافية وتمارينها. لا تُقدَّم هذه الإضافات بوصفها جزءًا من المصادر.</p></section>
<section><h2 class="sec-h">{ic("star")} أدوات التفاعل</h2><ul>
<li><b>بطاقات المفردات:</b> اضغط البطاقة لإظهار المعنى والسياق، وعلّم الكلمة بنجمة إذا تعلمتها.</li>
<li><b>حجم الخط:</b> الزران A− وA+ في الشريط العلوي يغيّران حجم النص في الكتاب كله.</li>
<li><b>وضع القراءة:</b> يخفف التصميم ويضيّق عرض النص.</li>
<li><b>التظليل الآلي:</b> أول ورود لكل مفردة من قائمة المادة يُظلَّل في النص؛ والمطابقة آلية وقد تخطئ أو تفوّت مواضع.</li>
<li><b>الفيديو:</b> يُحمَّل المشغّل داخل الصفحة عند الضغط، وتحته رابط مباشر يفتح يوتيوب في صفحة جديدة. لا تُعرض نصوص مكتوبة للفيديوهات عمدًا ليتدرّب الطالب على استراتيجيات الاستماع.</li>
<li><b>الإجابات والتقدم:</b> تُحفظ في متصفحك فقط (localStorage) ولا تُرسل إلى أي خادم؛ يمكنك تنزيل إجاباتك نصًّا.</li>
<li><b>الطباعة:</b> زر الطباعة يطبع الصفحة الحالية بتنسيق مناسب.</li></ul></section>
<section><h2 class="sec-h">{ic("warn")} تنبيهات مهمة</h2><ul>
<li>عبارات «أستطيع أن» مقتبسة من ACTFL، وخرائط الكفاءة أداة تأمل لا تعني بلوغ مستوى.</li></ul></section></section>''')


def album_view():
    return (f'''<section class="view" id="v-album" data-title="مدخل المقرر: ألبوم مصر" hidden>{back_links()}<header class="phead"><h1 tabindex="-1">مدخل المقرر: ألبوم مصر</h1>
<p class="lead">قبل الدخول في الوحدات، تعرّف إلى ثماني عشرة شخصية وفكرة مصرية في بطاقات ثنائية اللغة. {SRC_TAG}</p></header>
<div class="legacy"><iframe title="ألبوم مصر" src="assets/legacy/album-misr.html" loading="lazy"></iframe></div>
<p class="note"><a class="btn" href="assets/legacy/album-misr.html" target="_blank" rel="noopener">{ic("link")} افتح الألبوم في صفحة مستقلة</a> الصفحة منقولة من الملف المرفق دون تعديل.</p>
<section class="qs"><h2 class="sec-h">{ic("info")} نشاط مدخل المقرر {SUPP_TAG}</h2><ol class="qlist">
<li><p class="qt">اختر ثلاث بطاقات من الألبوم تمثّل مجالات فنية أو ثقافية مختلفة. ما الذي تعرّفه كل بطاقة عن صاحبها أو موضوعها؟</p><textarea class="ans" rows="3" data-ans="album:0" aria-label="إجابة 1"></textarea></li>
<li><p class="qt">أي بطاقة تتوقع أن ترتبط بموضوع «الفن والسياسة»؟ ولماذا؟ دوّن توقعك ثم عد إليه في نهاية المقرر.</p><textarea class="ans" rows="3" data-ans="album:1" aria-label="إجابة 2"></textarea></li>
<li><p class="qt">ما الصورة التي كانت لديك عن مصر قبل هذا المقرر؟ وما الذي في الألبوم يؤكدها أو يعدّلها؟ تذكّر أن أي مجتمع متنوع من الداخل.</p><textarea class="ans" rows="3" data-ans="album:2" aria-label="إجابة 3"></textarea></li></ol></section>
<nav class="pager"><a class="btn" href="#/u1">{ic("arrow-l")} الوحدة الأولى</a><a class="btn" href="#/contents">{ic("list")} الفهرس</a></nav></section>''')


def connectors_view():
    s = [f'<section class="view" id="v-connectors" data-title="أدوات الربط والروابط الخطابية" hidden>{back_links()}<header class="phead"><h1 tabindex="-1">أدوات الربط والروابط الخطابية</h1>'
         f'<p class="lead">ما الذي يجعل الكتابة والحديث المتقدمين مترابطين؟ هنا أدوات الربط التي وردت في قوائم المقرر مصنفة بحسب وظيفتها.</p></header>'
         f'<p class="note">{SRC_TAG} الأدوات في الجداول الأولى هي ٥١ أداة وردت في قوائم المقرر (٣ في كل مادة من المواد السبع عشرة)، وقد أُعيد تصنيفها بحسب الوظيفة. {SUPP_TAG} الأدوات الإضافية والتمارين وصفها معدّ الكتاب.</p>']
    C = VOC['C']
    for gi, (gname, gdesc, idx) in enumerate(GROUPS):
        s.append(f'<section class="cgrp"><h2 class="sec-h">{esc(gname)} <small>{len(idx)}</small></h2><p class="note small">{esc(gdesc)}</p><div class="cards wide">')
        for (n, i) in idx:
            r = C[str(n)][i]
            fl = FLAGS_C.get((n, i))
            iid = next(k for k, m in ITEMMETA.items() if vocab_n(m['code']) == n)
            s.append(f'<div class="vcard conn{" flagged" if fl else ""}" data-key="cx:{n}:{i}"><button class="vc-flip" aria-expanded="false"><span class="vc-ar">{esc(r["ar"])}</span><span class="vc-hint">اضغط لإظهار المعنى</span>'
                     f'<span class="vc-back"><span class="vc-en en" dir="ltr">{esc(r["en"])}</span><span class="vc-ctx"><small>وردت في:</small> <a href="#/{iid}">{esc(ITEMMETA[iid]["label"])} — {esc(ITEMMETA[iid]["title"])[:40]}</a></span></span></button>'
                     + (f'<p class="flag">{ic("warn")} {esc(fl[0])}' + (f' — المقترح: <span class="ar-s">{esc(fl[1])}</span>' if fl[1] else '') + '</p>' if fl else '')
                     + f'<button class="vc-learn" aria-pressed="false">{ic("star")}<span class="sr">تعلمتها</span></button></div>')
        s.append('</div></section>')
    s.append(f'<section class="cgrp supp"><h2 class="sec-h">أدوات إضافية شائعة {SUPP_TAG}</h2><p class="note small">هذه أدوات لم ترد في قوائم المقرر، أضافها معدّ الكتاب لتوسيع الحصيلة؛ وكلها من الفصحى المعيارية.</p><div class="tablewrap"><table class="vt"><thead><tr><th>الأداة</th><th>الوظيفة</th><th class="en" dir="ltr">English</th><th>مثال (إضافة تعليمية)</th></tr></thead><tbody>')
    for a, f, e, x in SUPP:
        s.append(f'<tr><td class="ar">{esc(a)}</td><td>{esc(f)}</td><td class="en" dir="ltr">{esc(e)}</td><td class="ar">{esc(x)}</td></tr>')
    s.append('</tbody></table></div></section>')
    s.append(f'<section class="cloze-sec"><h2 class="sec-h">{ic("check")} تمرين: اختر أداة الربط المناسبة {SUPP_TAG}</h2><p class="note small">الجمل من تأليف معدّ الكتاب وتدور حول موضوعات المقرر. اختر الأداة ثم اقرأ التعليق.</p><ol class="cloze-l">')
    for j, (pre, post, opts, ans, why) in enumerate(CLOZE):
        s.append(f'<li class="cloze" data-ans="{ans}"><p class="ar">{esc(pre)} <span class="blank">＿＿＿</span> {esc(post)}</p><div class="opts">'
                 + ''.join(f'<button class="opt" data-o="{k}">{esc(o)}</button>' for k, o in enumerate(opts))
                 + f'</div><p class="fb" hidden data-why="{esc(why, True)}"></p></li>')
    s.append(f'</ol></section><section class="bigcard"><h2 class="sec-h">{ic("search")} الأداة التفاعلية: ٤٠٨ أدوات ربط {SRC_TAG}</h2>'
             f'<p>مدونة واسعة من أدوات الربط والروابط الخطابية للدراسة الذاتية. تُفتح في صفحة جديدة.</p>'
             f'<p><a class="btn primary big" href="assets/legacy/arabic-connectors.html" target="_blank" rel="noopener">{ic("link")} افتح أداة أدوات الربط (٤٠٨) في صفحة جديدة</a></p></section></section>')
    return ''.join(s)


def cando_view():
    s = [f'<section class="view" id="v-cando" data-title="مرجع عبارات «أستطيع أن»" hidden>{back_links()}<header class="phead"><h1 tabindex="-1">مرجع عبارات «أستطيع أن» (ACTFL)</h1>'
         f'<p class="lead">كل عبارات الملفين المرفقين (المستوى المتقدم والمستوى المتوسط) كما وردت بالإنجليزية.</p></header>'
         f'<p class="note">المصدر: <i>2024 Advanced Can-Do Statements</i> و<i>2024 Intermediate Can-Do Statements</i> (ACTFL/NCSSFL). حُلّلت الجداول آليًا من ملفي PDF وصُحّحت فيها الأخطاء الناتجة عن التحويل؛ فإن وجدت فرقًا عن الأصل فالأصل هو المعتمد.</p>']
    for pref, nm in (('A-', 'المستوى المتقدم'), ('S-', 'مقتطفات تواصل بين الثقافات (S-)'), ('I-', 'المستوى المتوسط (للمقارنة)')):
        s.append(f'<h2 class="sec-h">{nm}</h2>')
        for cid, c in CD.items():
            if cid.startswith(pref):
                s.append(f'<details class="cd"><summary><b class="cdid">{cid}</b> <span class="chip">{MODE_AR[c["mode"]]}</span> <span class="en" dir="ltr">{esc(c["q"])}</span></summary>'
                         f'<blockquote class="en quote" dir="ltr"><p class="bench">{esc(c["bench"])}</p>' + ''.join(f'<p><b>{esc(l["level"])}:</b> {esc(l["text"])}</p>' for l in c['levels']) + '</blockquote></details>')
    return ''.join(s) + '</section>'


def vocab_index_view():
    s = [f'<section class="view" id="v-vocab" data-title="فهرس المفردات" hidden>{back_links()}<header class="phead"><h1 tabindex="-1">فهرس المفردات</h1>'
         f'<p class="lead">ابحث في كل المفردات والأفعال والتراكيب (بالعربية أو بالإنجليزية). {SRC_TAG}</p></header>'
         f'<div class="searchbar"><label class="sr" for="vq">ابحث</label>{ic("search")}<input id="vq" type="search" placeholder="اكتب كلمة بالعربية أو بالإنجليزية…" autocomplete="off"><span class="count" aria-live="polite"></span></div><div class="vindex">']
    for iid, m in ITEMMETA.items():
        n = vocab_n(m['code'])
        rows = [(r['ar'], r['en'], 'مفردة') for r in VOC['G'][str(n)]] + \
               [(f"{r['past']} / {r['pres']} / {r['masdar']}", VG.get(norm(r['past']), ''), 'فعل') for r in VOC['V'][str(n)]] + \
               [(r['ar'], r['en'], 'ربط' if 'ربط' in norm(r['type']) else 'تركيب') for r in VOC['C'][str(n)]]
        s.append(f'<details class="vi" data-item="{iid}"><summary>{esc(TITLES[iid])} <em>{len(rows)}</em></summary><table class="vt"><tbody>')
        for a, e, t in rows:
            s.append(f'<tr data-s="{esc(norm(a) + " " + e.lower(), True)}"><td class="ar">{esc(a)}</td><td class="en" dir="ltr">{esc(e)}</td><td><span class="chip">{t}</span></td></tr>')
        s.append('</tbody></table></details>')
    return ''.join(s) + '</div></section>'


def thematic_view():
    s = [f'<section class="view" id="v-thematic" data-title="المعجم الموضوعي (B2)" hidden>{back_links()}<header class="phead"><h1 tabindex="-1">ملحق: المعجم الموضوعي (B2)</h1>'
         f'<p class="lead">معجم موضوعي من خمسة أقسام كما ورد في مواد المقرر، بلا تعديل. {SRC_TAG}</p></header>']
    for sec in THEM:
        s.append(f'<section><h2 class="sec-h en" dir="ltr">{esc(sec["title"])}</h2><div class="tablewrap"><table class="vt"><thead><tr><th>العربية</th><th class="en" dir="ltr">Transliteration</th><th class="en" dir="ltr">English</th><th class="en" dir="ltr">Usage context</th></tr></thead><tbody>')
        for r in sec['rows']:
            s.append(f'<tr><td class="ar">{esc(r["a"])}</td><td class="en" dir="ltr">{esc(r["t"])}</td><td class="en" dir="ltr">{esc(r["e"])}</td><td>{esc(r["u"])}</td></tr>')
        s.append('</tbody></table></div></section>')
    return ''.join(s) + '</section>'


def sources_view():
    rep = open(f'{ROOT}/report_ar.html', encoding='utf8').read()
    cov_rows = ''.join(f'<tr><td>{esc(TITLES[k][:60])}</td><td>{a} / {b}</td></tr>' for k, (a, b) in COVERAGE.items())
    return (f'<section class="view" id="v-sources" data-title="المصادر والتقرير" hidden>{back_links()}<header class="phead"><h1 tabindex="-1">المصادر والتقرير</h1>'
            f'<p class="lead">ما استُعمل، وما لم يتوافر، وما استُبدل، وما وُجد فيه خلل.</p></header>{rep}'
            f'<section><h2 class="sec-h">تغطية التظليل الآلي في النصوص</h2><p class="note small">عدد المفردات المظللة في النص من مجموع مفردات القائمة (مطابقة آلية؛ تظلل أول ورود فقط).</p>'
            f'<div class="tablewrap"><table class="vt"><thead><tr><th>المادة</th><th>المظلّل / القائمة</th></tr></thead><tbody>{cov_rows}</tbody></table></div></section></section>')


def tech_view():
    rep = open(f'{ROOT}/tech_ar.html', encoding='utf8').read()
    return (f'<section class="view" id="v-tech" data-title="ملاحظة تقنية" hidden>{back_links()}<header class="phead"><h1 tabindex="-1">ملاحظة تقنية</h1></header>{rep}</section>')


# ------------------------------------------------------------------ shell
def shell(views):
    toc = ['<nav id="toc" class="toc" aria-label="فهرس سريع" hidden><button class="btn small close" data-toc="close">إغلاق ✕</button><ul>']
    toc.append('<li><a href="#/cover">الغلاف</a></li><li><a href="#/contents">فهرس المحتويات</a></li><li><a href="#/guide">دليل الاستخدام</a></li><li><a href="#/album">مدخل المقرر: ألبوم مصر</a></li>')
    for n in range(1, 6):
        toc.append(f'<li class="tu"><a href="#/u{n}">{ic(U[n]["icon"])} الوحدة {ar_num(n)}: {esc(U[n]["title"])}</a><ul>')
        for iid, m in ITEMMETA.items():
            if m['u'] == f'u{n}':
                toc.append(f'<li class="{m["kind"]}"><a href="#/{iid}"><span class="dn" data-dn="{iid}">{ic("check")}</span>{esc(m["label"])}: {esc(m["title"])[:48]}</a></li>')
        toc.append('</ul></li>')
    toc.append('<li><a href="#/connectors">أدوات الربط والروابط الخطابية</a></li><li><a href="#/cando">مرجع «أستطيع أن»</a></li><li><a href="#/vocab">فهرس المفردات</a></li>'
               '<li><a href="#/thematic">المعجم الموضوعي (B2)</a></li><li><a href="#/sources">المصادر والتقرير</a></li><li><a href="#/tech">ملاحظة تقنية</a></li></ul></nav>')
    top = (f'<header class="topbar"><button class="btn icon" data-toc="toggle" aria-controls="toc" aria-expanded="false" aria-label="فتح فهرس المحتويات">{ic("menu")}</button>'
           f'<a class="brand" href="#/cover">الفن والسياسة</a><div class="tools"><button class="btn icon" data-fs="-1" aria-label="تصغير الخط">{ic("minus")}<b>A</b></button>'
           f'<button class="btn icon" data-fs="1" aria-label="تكبير الخط">{ic("plus")}<b>A</b></button><button class="btn icon" data-readmode aria-label="وضع القراءة" aria-pressed="false">{ic("eye")}</button>'
           f'<button class="btn icon" data-print aria-label="طباعة الصفحة">{ic("print")}</button></div><div class="gprog" aria-hidden="true"><i data-bprog></i></div></header>')
    return f'''<!doctype html>
<html lang="ar" dir="rtl">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>الفن والسياسة — كتاب تفاعلي لمتعلمي العربية</title>
<meta name="description" content="كتاب تفاعلي لمتعلمي العربية لغةً أجنبية (المستوى المتقدم): الفن والسياسة في مصر — الموسيقا والجرافيتي والحلي والكوميكس والسينما. إعداد وانتقاء ياسر كاشف.">
<meta name="author" content="Yasser Kashef"><meta name="copyright" content="© 2026 Yasser Kashef. All rights reserved. Design carried out by AI.">
<link rel="stylesheet" href="assets/css/style.css">
</head>
<body>
<a class="skip" href="#main">انتقل إلى المحتوى</a>
{top}
{''.join(toc)}
<div id="scrim" hidden></div>
<main id="main" tabindex="-1">
{''.join(views)}
<noscript><p style="padding:2rem">يحتاج هذا الكتاب إلى تفعيل JavaScript.</p></noscript>
</main>
<footer class="foot"><p>© 2026 Yasser Kashef. All rights reserved. Design carried out by AI. · إعداد وانتقاء: ياسر كاشف · <a href="#/sources">المصادر والتقرير</a></p></footer>
<div id="pop" role="dialog" aria-label="معنى الكلمة" hidden></div>
<button id="totop" class="btn icon" aria-label="إلى أعلى الصفحة" hidden>{ic("top")}</button>
<script src="assets/js/app.js"></script>
</body></html>'''


def main():
    os.makedirs(f'{OUT}/assets/css', exist_ok=True)
    os.makedirs(f'{OUT}/assets/js', exist_ok=True)
    shutil.copy(f'{ROOT}/src/style.css', f'{OUT}/assets/css/style.css')
    shutil.copy(f'{ROOT}/src/app.js', f'{OUT}/assets/js/app.js')
    views = [cover_view(), contents_view(), guide_view(), album_view()]
    for n in range(1, 6):
        views.append(unit_view(n))
        for iid, m in ITEMMETA.items():
            if m['u'] == f'u{n}':
                views.append(item_view(iid))
    views += [connectors_view(), cando_view(), vocab_index_view(), thematic_view()]
    views.append(sources_view())
    views.append(tech_view())
    open(f'{OUT}/index.html', 'w', encoding='utf8').write(shell(views))
    json.dump(COVERAGE, open(f'{ROOT}/coverage.json', 'w'), ensure_ascii=False, indent=1)
    print('built', os.path.getsize(f'{OUT}/index.html') // 1024, 'KB; coverage', sum(a for a, b in COVERAGE.values()), '/', sum(b for a, b in COVERAGE.values()))


if __name__ == '__main__':
    main()
