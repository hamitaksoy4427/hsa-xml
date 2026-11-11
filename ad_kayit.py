# 11 Kas 2026: Kalici urun adlari. urun_adlari.tsv (stok_kodu<TAB>ad) varsa feed'deki ad yerine bu kullanilir.
import os
_Y = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'urun_adlari.tsv')
ADLAR = {}
if os.path.exists(_Y):
    for _l in open(_Y, encoding='utf-8'):
        if _l.startswith('#'): continue
        _p = _l.rstrip('\n').split('\t')
        if len(_p) == 2 and _p[0] and _p[1]: ADLAR[_p[0]] = _p[1]
def kayitli_ad(stok_kodu, ad):
    return ADLAR.get(stok_kodu, ad)
