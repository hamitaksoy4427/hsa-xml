# 12 Kas 2026: yayindaki himpeks.xml'e v4 adlari ve kopya urunleri ekler (fiyat/stok ananinki)
import re, os, sys
from xml.sax.saxutils import escape
_D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, _D)
from ad_kayit import kayitli_ad
X = os.path.join(_D, 'himpeks.xml') if len(sys.argv) < 2 else sys.argv[1]
t = open(X, encoding='utf-8').read()
bl = re.findall(r'  <urun>\n.*?</urun>\n', t, flags=re.S)
kod = lambda b: re.search(r'<stok_kodu>([^<]*)</stok_kodu>', b).group(1)
def ad(b, y): return re.sub(r'<urun_adi>.*?</urun_adi>', lambda _: '<urun_adi>%s</urun_adi>' % escape(y), b, count=1, flags=re.S)
from xml.sax.saxutils import unescape
yeni = []; mevcut = set()
for b in bl:
    k = unescape(kod(b)); mevcut.add(k)
    a = re.search(r'<urun_adi>(.*?)</urun_adi>', b, flags=re.S).group(1)
    yeni.append(ad(b, kayitli_ad(k, unescape(a))))
ana = {unescape(kod(b)): b for b in yeni}; n = 0
for l in open(os.path.join(_D, 'himpeks_kopya_adlar.tsv'), encoding='utf-8'):
    if l.startswith('#'): continue
    p = l.rstrip('\n').split('\t')
    if len(p) == 3 and p[0] in ana and p[1] not in mevcut:
        b = re.sub(r'<stok_kodu>[^<]*</stok_kodu>', '<stok_kodu>%s</stok_kodu>' % escape(p[1]), ana[p[0]], count=1)
        yeni.append(ad(b, kayitli_ad(p[1], p[2]))); mevcut.add(p[1]); n += 1
open(X, 'w', encoding='utf-8').write('<?xml version="1.0" encoding="UTF-8"?>\n<urunler>\n' + ''.join(yeni) + '</urunler>\n')
print('urun', len(yeni), 'eklenen kopya', n)
