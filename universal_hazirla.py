# HSA Parts - Universal XML hazirlama (9 Kas 2026)
# Universal kaynak XML'indeki fiyatlari site fiyatina cevirir:
#   Price  (KDV dahil) -> Price x 1,85 (FAR/STOP alt kategorisi x 1,40), 100 TL'ye YUKARI yuvarlanir
#   Price2 (KDV haric) -> yeni Price / (1 + KDV)   (KDV haric kullanan urunlerde de son fiyat yuvarlak cikar)
# Diger tum alanlar (isim, kategori, resim, stok...) aynen kalir.
# Ideasoft'ta universaloto fiyat orani 1 olmali (carpan burada uygulandi).
import re, sys, math
CARPAN = 1.85
FAR_STOP_CARPAN = 1.40   # 9 Kas 2026: alt kategorisi FAR veya STOP olan urunler
YUVARLA = 100
src, out = sys.argv[1], sys.argv[2]
t = open(src, encoding='utf-8').read()
n = 0
fs = []
def urun(m):
    global n
    b = m.group(0)
    pm = re.search(r'<Price>([^<]*)</Price>', b)
    if not pm: return b
    try: p = float(pm.group(1).replace(',', '.'))
    except ValueError: return b
    if p <= 0: return b
    tm = re.search(r'<Tax>([^<]*)</Tax>', b)
    try: kdv = float(tm.group(1)) if tm else 20.0
    except ValueError: kdv = 20.0
    sm = re.search(r'<subCategory><!\[CDATA\[([^\]]*)\]\]></subCategory>', b)
    alt = (sm.group(1).strip().upper() if sm else '')
    c = FAR_STOP_CARPAN if alt in ('FAR', 'STOP') else CARPAN
    if c == FAR_STOP_CARPAN: fs.append(1)
    yeni = int(math.ceil(round(p * c, 4) / YUVARLA) * YUVARLA)
    b = b.replace(pm.group(0), '<Price>%d.00</Price>' % yeni, 1)
    b = re.sub(r'<Price2>[^<]*</Price2>', '<Price2>%.4f</Price2>' % (yeni / (1 + kdv / 100)), b, count=1)
    n += 1
    return b
t2 = re.sub(r'<Product>.*?</Product>', urun, t, flags=re.S)
# 9 Kas 2026: ayni stok kodlu/OEM'li kopya urunler (STOKKODU/1, /2 ...) asil urunle ayni fiyat ve stoku alsin.
# Liste: universal_kopyalar.tsv (ana_stok_kodu <TAB> kopya_sayisi). Yeni kopya acilinca bu listeye eklenir.
import os
KOP = {}
kp = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'universal_kopyalar.tsv')
if os.path.exists(kp):
    for l in open(kp, encoding='utf-8'):
        a = l.rstrip('\n').split('\t')
        if len(a) == 2 and a[1].isdigit(): KOP[a[0]] = int(a[1])
eklenen = []
def kopya(m):
    b = m.group(0)
    km = re.search(r'<Product_code><!\[CDATA\[([^\]]*)\]\]></Product_code>', b)
    if not km or km.group(1) not in KOP: return b
    kod = km.group(1)
    ek = [b]
    for i in range(1, KOP[kod] + 1):
        ek.append(b.replace(km.group(0), '<Product_code><![CDATA[%s/%d]]></Product_code>' % (kod, i), 1))
        eklenen.append(1)
    return '\n  '.join(ek)
t2 = re.sub(r'<Product>.*?</Product>', kopya, t2, flags=re.S)
# 11 Kas 2026: kalici (duzeltilmis) urun adlari
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ad_kayit import ADLAR
def ad_koy(m):
    b = m.group(0)
    km = re.search(r'<Product_code><!\[CDATA\[([^\]]*)\]\]></Product_code>', b)
    if not km or km.group(1) not in ADLAR: return b
    return re.sub(r'<Name><!\[CDATA\[.*?\]\]></Name>', lambda _: '<Name><![CDATA[%s]]></Name>' % ADLAR[km.group(1)], b, count=1, flags=re.S)
t2 = re.sub(r'<Product>.*?</Product>', ad_koy, t2, flags=re.S)
if n < 10000:
    print('HATA: cok az urun (%d), dosya yazilmadi' % n); sys.exit(1)
open(out, 'w', encoding='utf-8').write(t2)
print('Universal hazir: %d urun + %d kopya (%d far/stop x1,40, digerleri x1,85, hepsi 100 TL yukari)' % (n, len(eklenen), len(fs)))
