#!/bin/bash
# Duzeltilmis himpeks.xml (HMPX- kodlari, x1,85 + yukari 100 TL, resim linkleri) ve betikleri GitHub'a gonderir.
cd "$HOME/hsa-xml" || exit 1
git add parca himpeks.xml donustur.py resim_ekle.sh kontrol_cek.sh himpeks_gonder.command
git commit -q -m "Himpeks: HMPX- stok kodlari, x1.85 + yukari 100 TL, resim linkleri ($(date '+%Y-%m-%d %H:%M'))" || echo "Degisiklik yok"
git push -q origin main && echo "TAMAM: GitHub'a yuklendi" || echo "HATA: push basarisiz"
git log --oneline -1
