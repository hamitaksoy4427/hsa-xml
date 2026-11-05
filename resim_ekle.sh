#!/bin/bash
# (5 Kas 2026: resim adi kaynak_kodu (Himpeks orijinal kodu) ile eslenir, resimler git deposundan kontrol edilir)
# himpeks.xml'deki her urune resim/ klasorundeki resim linklerini ekler (stok kodu: harf/rakam disi -> "_")
cd "$(dirname "$0")" || exit 1
perl -0777 -i -pe '
  BEGIN { $url = "https://raw.githubusercontent.com/hamitaksoy4427/hsa-xml/main/resim/"; $var = 0; $top = 0;
          { local $/ = "\n"; %git = map { chomp; ($_ => 1) } `git ls-tree -r --name-only HEAD resim/`; } }
  s{(<urun>.*?</urun>)}{
    my $u = $1; $top++;
    if ($u !~ /<resimler>/ && $u =~ m{<kaynak_kodu>([^<]*)</kaynak_kodu>}) {
      (my $ad = $1) =~ s/&amp;/&/g; $ad =~ s/&gt;/>/g; $ad =~ s/&lt;/</g; $ad =~ s/[^A-Za-z0-9]/_/g;
      my @r = grep { $git{$_} || -f $_ } ("resim/$ad.jpg", map { "resim/${ad}_$_.jpg" } 2..10);
      if (@r) {
        my $x = "<resimler>" . join("", map { my $f = $_; $f =~ s{^resim/}{}; "<resim>$url$f</resim>" } @r) . "</resimler>";
        $u =~ s{</urun>$}{  $x\n  </urun>}; $var++;
      }
    }
    $u
  }gse;
  END { print STDERR "Resim eklenen urun: $var / $top\n"; }
' himpeks.xml
