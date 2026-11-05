import sys, glob, math
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape
src, out = sys.argv[1], sys.argv[2]
CARPAN = 1.85   # KDV dahil net x 1,85 (5 Kas 2026)
YUVARLA = 100   # yukari 100 TL'ye yuvarla
ONEK = 'HMPX-' # sitedeki stok kodu oneki (entegrasyon eslesmesi icin sart)
TEDARIK_STOK = 10
SURE_STOKTA = '1-2 iş günü'
SURE_TEDARIK = '3-5 iş günü'
seen = {}
for f in sorted(glob.glob(src + '/*.xml')):
    try: res = ET.parse(f).getroot().find('Result')
    except Exception: continue
    if res is None: continue
    brands = {b.get('ID'): b.get('BrandName') for b in res.findall('Brands/Brand')}
    for p in res.findall('Products/Product'):
        pr = p.find('Pricing')
        try: net = float(pr.findtext('LocalNetPriceWVat') or 0)
        except Exception: net = 0
        if net <= 0: continue
        fiyat = max(YUVARLA, int(math.ceil(round(net * CARPAN, 4) / YUVARLA) * YUVARLA))
        stok = int(sum(float(s.text or 0) for s in p.findall('Stocks/Stock')))
        seen[p.get('ID')] = dict(
            stok_kodu=p.get('ProductCode').strip(), kaynak_kodu=p.get('ProductCode').strip(), urun_adi=(p.findtext('ProductNames/ProductName') or '').strip(),
            uretici_kodu=(p.get('ProducerCode') or '').strip(), tedarikci_marka=brands.get(p.get('BrandID'), ''),
            satis_fiyati=fiyat, kdv=pr.findtext('VatRate') or '20', para_birimi='TL',
            stok=(stok if stok > 0 else TEDARIK_STOK),
            tedarik_durumu=('Stokta' if stok > 0 else 'Tedarik ile getirtilir'),
            teslim_suresi=(SURE_STOKTA if stok > 0 else SURE_TEDARIK), himpeks_stok=stok,
            birim=p.get('Unit') or '', himpeks_id=p.get('ID'))
# Sitedeki stok kodu kurali (API yuklemesiyle ayni; entegrasyon eslesmesi icin birebir olmali):
#   'HMPX X' -> 'HMPX-X'  (ama 'X' de ayri urun olarak varsa -> 'HMPX-HMPX X');  diger her kod -> 'HMPX-' + kod
kodlar = {r['stok_kodu'] for r in seen.values()}
for r in seen.values():
    k = r['stok_kodu']
    if k.startswith('HMPX ') and k[5:] not in kodlar: r['stok_kodu'] = ONEK + k[5:]
    else: r['stok_kodu'] = ONEK + k
with open(out, 'w', encoding='utf-8') as fh:
    fh.write('<?xml version="1.0" encoding="UTF-8"?>\n<urunler>\n')
    for r in seen.values():
        fh.write('  <urun>\n' + ''.join(f'    <{k}>{escape(str(v))}</{k}>\n' for k, v in r.items()) + '  </urun>\n')
    fh.write('</urunler>\n')
print(len(seen))
