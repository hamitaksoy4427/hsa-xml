#!/bin/bash
# SADECE KONTROL: Himpeks'ten tum urunleri ceker, sayar. himpeks.xml'e, GitHub'a ve Ideasoft'a DOKUNMAZ.
cd "$HOME/hsa-xml" || exit 1
K="$HOME/hsa-xml/kontrol"; rm -rf "$K"; mkdir -p "$K/ham"
SIFRE=$(security find-generic-password -s himpeks-xml -a hsaparts -w) || { echo "Sifre okunamadi"; exit 1; }
skip=0; bitti=0
for i in $(seq 1 60); do
  f="$K/ham/$(printf '%08d' $skip).xml"
  kod=$(/usr/bin/curl -s -m 1800 -u "hsaparts:$SIFRE" -o "$f" -w '%{http_code}' "http://himpeks.sistemyazilim.com:3777/XmlService/GetAllProductsByParts/$skip/50000")
  adet=$(grep -o '<Product ID=' "$f" | wc -l | tr -d ' ')
  echo "skip=$skip HTTP=$kod urun=$adet"
  [ "$kod" = "200" ] || { echo "HATA: $(head -c 300 "$f")"; break; }
  grep -q 'EndOfProducts="true"' "$f" && { bitti=1; break; }
  skip=$((skip + 50000))
done
[ $bitti = 1 ] && echo "Liste tamamlandi." || echo "UYARI: liste bitmedi"
python3 - "$K/ham" "$HOME/hsa-xml/himpeks.xml" <<'PY'
import sys, glob, collections, xml.etree.ElementTree as ET
ham, eski = sys.argv[1], sys.argv[2]
tum, fiyatli, marka = {}, 0, collections.Counter()
for f in sorted(glob.glob(ham + '/*.xml')):
    try: res = ET.parse(f).getroot().find('Result')
    except Exception as e: print('Bozuk dosya:', f, e); continue
    b = {x.get('ID'): x.get('BrandName') for x in res.findall('Brands/Brand')}
    for p in res.findall('Products/Product'):
        tum[p.get('ProductCode')] = p
        try: net = float(p.findtext('Pricing/LocalNetPriceWVat') or 0)
        except: net = 0
        if net > 0: fiyatli += 1; marka[b.get(p.get('BrandID'), '?')] += 1
eskiler = {u.findtext('stok_kodu').removeprefix('HMPX-') for u in ET.parse(eski).getroot().findall('urun')}
yeni_fiyatli = {k for k, p in tum.items() if float(p.findtext('Pricing/LocalNetPriceWVat') or 0) > 0}
print('BUGUN: toplam urun', len(tum), '| fiyatli', fiyatli)
print('DUNKU DOSYA: fiyatli urun', len(eskiler))
print('Dunku dosyada olup bugun fiyati olmayan/eksik:', len(eskiler - yeni_fiyatli))
print('Bugun yeni gelen fiyatli:', len(yeni_fiyatli - eskiler))
print('En cok urunu olan markalar:', marka.most_common(8))
PY
echo "KONTROL BITTI (hicbir yere yukleme yapilmadi)"
