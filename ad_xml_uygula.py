# 11 Kas 2026: Yayindaki XML'lerde (universal/himpeks/meydan) urun adlarini urun_adlari.tsv'ye gore duzeltir. Fiyat/stok vb. dokunmaz.
import re, sys, os
from xml.sax.saxutils import escape
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ad_kayit import ADLAR
def yap(dosya, blok, kod_rx, ad_rx, ad_yaz):
    t = open(dosya, encoding='utf-8').read(); n = [0]
    def f(m):
        b = m.group(0); k = re.search(kod_rx, b)
        if not k or k.group(1) not in ADLAR: return b
        y = ADLAR[k.group(1)]; b2 = re.sub(ad_rx, lambda _: ad_yaz(y), b, count=1, flags=re.S)
        if b2 != b: n[0] += 1
        return b2
    t2 = re.sub(blok, f, t, flags=re.S)
    open(dosya, 'w', encoding='utf-8').write(t2); print(dosya, 'degisen ad:', n[0])
D = sys.argv[1:] or ['universal.xml','himpeks.xml','meydan.xml']
if 'universal.xml' in D: yap('universal.xml', r'<Product>.*?</Product>', r'<Product_code><!\[CDATA\[([^\]]*)\]\]>', r'<Name><!\[CDATA\[.*?\]\]></Name>', lambda y: '<Name><![CDATA[%s]]></Name>' % y)
if 'himpeks.xml' in D: yap('himpeks.xml', r'<urun>.*?</urun>', r'<stok_kodu>([^<]*)</stok_kodu>', r'<urun_adi>.*?</urun_adi>', lambda y: '<urun_adi>%s</urun_adi>' % escape(y))
if 'meydan.xml' in D: yap('meydan.xml', r'<Urun>.*?</Urun>', r'<StokKodu>([^<]*)</StokKodu>', r'<UrunAdi>.*?</UrunAdi>', lambda y: '<UrunAdi>%s</UrunAdi>' % escape(y))
