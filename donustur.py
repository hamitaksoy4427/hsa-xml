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

# 9 Kas 2026: kaporta panelleri (kapi, camurluk, kaput, bagaj kapagi) = KDV dahil net x 1,40 (Meydan kuraliyla ayni)
import re
KAPORTA_CARPAN = 1.40
def up_inv(s):          # ToUpperInvariant
    return s.upper().replace("İ", "İ")

# --- Kaporta paneli kurali ---
RX_PAREN = re.compile(r'\([^)]*\)?')
RX_KAPISAY = re.compile(r'\b\d+(?:\s*/\s*\d+)?\s*KAPI(LI)?\b|\b(TEK|ÇİFT|CIFT) KAPI(LI)?\b')
RX_KW = re.compile(r'\b(ARKA |ÖN |ON )?(KAPI|ÇAMURLUK|CAMURLUK|KAPUT(?:U)?|BAGAJ KAPA[ĞG]I|BAĞAJ KAPA[ĞG]I)\b')
RX_ONCE = re.compile(r'TAMPON|AYNA|STOP|\bFAR|LAMBA|PANJUR|IZGARA|MARŞPİYEL|MARSPIYEL|DİREK|PANEL|TAVAN|PLASTİ|BRAKET|DAVLUMBAZ|KİLİT|SİNYAL')
RX_PAREN2 = re.compile(r'\([^)]*\)')
RX_HARIC = re.compile(r'DAVLUMBAZ|AÇMA|ACMA|DURDURUCU|MENTEŞE|MENTESE|AYNA|BAND|AĞZI|AGZI|SİNYAL|SINYAL|MUSKA|RAY|KİLİ|KILI|KİLİT|BAĞLANTI|BAGLANTI|DODİK|DODIK|TOZ|KLİPS|KLIPS|LASTİ|LASTI|DİREĞ|KAPLAMA|PLAKA|EMNİYET|NİKELAJ|NIKELAJ|BRAKET|AMORTİSÖR|AMORTISOR|DESTEK|DÜĞME|HAVALANDIRMA|İZOLATÖR|IZOLATOR|ÇEKME|SIYIRICI|MARŞPİYEL|TUTAMA|KIZA|ÇITA|CITA|CAM|AYDINLATMA|LAMBA|KARŞI|TELİ|TELI|KÖPRÜ|PLASTİ|PLASTI|İÇ |IÇ |SUPORT|SAC |SACI|KOLU|FİTİL|FITIL|DÖŞEME|DOSEME|SPOYLER|SPOILER|ARMA|YAZI|LOGO|ETİKET|CONTA|MOTOR|MEKANİZMA|KABLO|ŞALTER|SALTER|ANAHTAR|KİT|TAMİR|TAMIR|PARÇA|KÖŞE|KOSE|ÇERÇEVE|KASA|DIŞ |DIS |UÇ |ALT |ÜST |ORTA RAY|TAKIM|VİDA|VIDA|SOMUN|MANDAL|KANCA|TEL\b|RÖLE|BUTON|MASKE|KAPAĞI KAPAK|DEPO|METEŞE|AMORT|AMÖRT|PANJUR|PODYE|TWEETER|HOPARL|BASAMA|CEB|PANEL|TAMPON|IZGARA|GRİ|GRI|SİYAH ')
RX_AYNA = re.compile(r'\bKAPILI\b|AYNA')


def kaporta_mi(ad):
    n = RX_PAREN.sub(' ', up_inv(ad))
    n = RX_KAPISAY.sub(' ', n)
    m = RX_KW.search(n)
    if not m:
        return False
    if RX_ONCE.search(n[:m.start()]):
        return False
    kuyruk = RX_PAREN2.sub('', n[m.start():]) + ' '
    if RX_AYNA.search(kuyruk):
        return False
    mlen = m.end() - m.start()
    if RX_HARIC.search(kuyruk[min(mlen, len(kuyruk)):] + ' '):
        return False
    return True



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
        _ad = (p.findtext('ProductNames/ProductName') or '').strip()
        _c = KAPORTA_CARPAN if (kaporta_mi(_ad) and not re.search(r'DİREK|DIREK|KORDON|GERGİ|GERGI|KOLU|KİLİT|KILIT|MENTEŞE|FİTİL|CAM', _ad.upper())) else CARPAN
        fiyat = max(YUVARLA, int(math.ceil(round(net * _c, 4) / YUVARLA) * YUVARLA))
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
# 5 Kas 2026: hatali kaynak fiyatlar icin sabit fiyat ve engel listesi (betikle ayni klasorde)
import os
_D = os.path.dirname(os.path.abspath(__file__))
SABIT, ENGEL = {}, set()
try:
    for _l in open(os.path.join(_D, 'himpeks_sabit_fiyat.tsv'), encoding='utf-8'):
        _p = _l.rstrip('\n').split('\t')
        if len(_p) == 2 and _p[1].strip(): SABIT[_p[0].strip()] = int(float(_p[1]))
except FileNotFoundError: pass
try:
    ENGEL = {x.strip() for x in open(os.path.join(_D, 'himpeks_engel.txt'), encoding='utf-8') if x.strip()}
except FileNotFoundError: pass
for _k in [k for k, r in seen.items() if r['stok_kodu'] in ENGEL]: del seen[_k]
for r in seen.values():
    if r['stok_kodu'] in SABIT: r['satis_fiyati'] = SABIT[r['stok_kodu']]
# 6 Kas 2026: urun adi yazim/Turkce karakter duzeltme
import sys as _s; _s.path.insert(0, _D)
from ad_duzelt import ad_duzelt
for r in seen.values(): r['urun_adi'] = ad_duzelt(r['urun_adi'], meydan=False)
# 11 Kas 2026: kalici (duzeltilmis) urun adlari
from ad_kayit import kayitli_ad
for r in seen.values(): r['urun_adi'] = kayitli_ad(r['stok_kodu'], r['urun_adi'])
with open(out, 'w', encoding='utf-8') as fh:
    fh.write('<?xml version="1.0" encoding="UTF-8"?>\n<urunler>\n')
    for r in seen.values():
        fh.write('  <urun>\n' + ''.join(f'    <{k}>{escape(str(v))}</{k}>\n' for k, v in r.items()) + '  </urun>\n')
    fh.write('</urunler>\n')
print(len(seen))
