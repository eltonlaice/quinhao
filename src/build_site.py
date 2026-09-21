"""Build the public page from the extracted CSVs.

One self-contained HTML file: no external requests, no fonts, no frameworks, so it
loads on a slow connection and keeps working offline once opened. Data is inlined.

Run: python3 src/build_site.py   ->   docs/index.html
"""

import csv
import json

import build_map
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Legal destinations for the money, per Circular 1/MPD-MF/2013, quoted in the EITI reports.
USES = {
    "pt": ["Educação — salas de aula e apetrechamento", "Saúde — postos e centros de saúde",
           "Agricultura — regadios comunitários e represas", "Silvicultura — florestas comunitárias"],
    "en": ["Education — classrooms and equipment", "Health — health posts and centres",
           "Agriculture — community irrigation and dams", "Forestry — community forests"],
    "fr": ["Éducation — salles de classe et équipement", "Santé — postes et centres de santé",
           "Agriculture — irrigation communautaire et barrages", "Sylviculture — forêts communautaires"],
}

T = {
    "pt": {
        "title": "Quinhão", "lang_name": "Português",
        "tagline": "O que cabe à tua comunidade dos 2,75% da mineração.",
        "intro": "A lei manda 2,75% do imposto sobre a produção mineira e petrolífera para as "
                 "comunidades onde se explora. Escolhe a tua localidade e vê quanto foi transferido.",
        "pick": "Escolhe a tua localidade", "search": "Procurar localidade ou distrito…",
        "nomatch": "Nenhuma localidade encontrada.",
        "received": "Transferido para esta localidade", "year": "Ano", "amount": "Valor",
        "mineral": "Actividade mineira", "total": "Total em 6 anos", "no_data": "Sem transferência registada neste ano.",
        "next_title": "O que podes fazer com isto",
        "next_body": "Quem responde por este dinheiro é a <strong>Secretaria Distrital</strong>, "
                     "em coordenação com o <strong>Conselho Consultivo de Localidade</strong>. "
                     "A lei limita o uso a quatro áreas:",
        "ask_title": "Perguntas que tens o direito de fazer",
        "asks": ["Em que projectos foi aplicado o valor deste ano?",
                 "Onde está a acta do Conselho Consultivo que aprovou esses projectos?",
                 "As obras foram concluídas? Posso ver o auto de recepção?"],
        "source_title": "De onde vêm estes números",
        "source_body": "Relatórios do ITIE Moçambique, publicados em eiti.org. Nenhum número foi "
                       "escrito à mão — são extraídos dos PDF oficiais por um programa que falha "
                       "se os totais não baterem com os publicados.",
        "caveat_title": "O que estes números não dizem",
        "caveat_body": "O Estado declara 100% de execução — o dinheiro saiu. Isso não quer dizer "
                       "que algo foi construído. E o próprio ITIE escreve que não é possível saber "
                       "que critério repartiu o valor por cada comunidade.",
        "note2022": "2022 não aparece acima: nesse ano o relatório oficial publica os gastos por projecto a nível nacional, sem repartição por localidade.",
        "hero_kicker": "O que a lei promete às comunidades mineiras",
        "hero_h": "{com} para as comunidades.<br>{prov} para as direcções provinciais.",
        "hero_p": "Em 2024, as comunidades que vivem em cima do rubi, do carvão e do gás receberam menos de um terço do que foi para as capitais provinciais. Ninguém explica porquê.",
        "cmp_title": "Para onde foi o dinheiro da indústria extractiva em 2024",
        "cmp_com": "Comunidades afectadas",
        "cmp_prov": "Direcções provinciais",
        "quote": "o REOE não permite aferir qual foi o critério utilizado para repartir o valor a alocar para cada comunidade e para quais actividades os fundos foram alocados",
        "quote_src": "ITIE Moçambique, o organismo oficial de transparência, nos relatórios de 2020 e 2021",
        "trend_title": "Total transferido às comunidades, por ano",
        "trend_note": "Em 2022 o valor cai 39% e em 2024 quadruplica. Os relatórios não explicam nenhuma das duas variações.",
        "find_title": "Encontra a tua localidade",
        "map_title": "Onde caem os 2,75%",
        "map_sub": "Total por província no ano seleccionado. Toca numa província para filtrar a lista.",
        "map_low": "menos",
        "map_high": "mais",
        "map_none": "Sem transferência registada",
        "map_all": "Todas as províncias",
        "map_year": "Ano",
        "cap_lng": "Palma, Cabo Delgado — gás natural. A província recebeu {cd} em 2024.",
        "cap_coal": "Moatize, Tete — carvão mineral. Tete recebeu {te} em 2024, mais do que qualquer outra província.",
        "credits": "Imagens: ver CREDITS.md no repositório.",
        "cur_mzn": "Meticais",
        "cur_usd": "Dólares",
        "mzn_m": "milhões de MZN",
        "usd_m": "milhões de USD",
        "fx_note": "Convertido à taxa média oficial de cada ano (Banco Mundial, PA.NUS.FCRF), não à taxa de hoje.",
        "lvl_prov": "Províncias",
        "lvl_dist": "Distritos",
        "map_sub_d": "Total por distrito no ano seleccionado. Toca num distrito para filtrar a lista.",
        "updated": "Dados de 2019 a 2024. Actualizado em",
    },
    "en": {
        "title": "Quinhão", "lang_name": "English",
        "tagline": "Your community's share of the 2.75% from mining.",
        "intro": "The law sends 2.75% of the mining and petroleum production tax to the communities "
                 "where extraction happens. Pick your locality and see what was transferred.",
        "pick": "Pick your locality", "search": "Search locality or district…",
        "nomatch": "No locality found.",
        "received": "Transferred to this locality", "year": "Year", "amount": "Amount",
        "mineral": "Mining activity", "total": "Total over 6 years", "no_data": "No transfer recorded this year.",
        "next_title": "What you can do with this",
        "next_body": "The body answerable for this money is the <strong>District Secretariat</strong>, "
                     "working with the <strong>Locality Consultative Council</strong>. "
                     "The law limits spending to four areas:",
        "ask_title": "Questions you have the right to ask",
        "asks": ["Which projects was this year's amount spent on?",
                 "Where are the Consultative Council minutes approving those projects?",
                 "Was the work completed? May I see the handover certificate?"],
        "source_title": "Where these numbers come from",
        "source_body": "EITI Mozambique reports, published at eiti.org. No number was typed by hand — "
                       "they are extracted from the official PDFs by a program that fails if the "
                       "totals do not match the published ones.",
        "caveat_title": "What these numbers do not tell you",
        "caveat_body": "The State reports 100% execution — the money left. That does not mean "
                       "anything was built. And EITI itself writes that the criterion used to split "
                       "the amount between communities cannot be determined.",
        "note2022": "2022 is missing above: that year the official report publishes spending by project at national level, with no split by locality.",
        "hero_kicker": "What the law promises mining communities",
        "hero_h": "{com} to the communities.<br>{prov} to the provincial directorates.",
        "hero_p": "In 2024 the communities living on top of the ruby, the coal and the gas received less than a third of what went to the provincial capitals. Nobody explains why.",
        "cmp_title": "Where the extractive money went in 2024",
        "cmp_com": "Affected communities",
        "cmp_prov": "Provincial directorates",
        "quote": "the budget execution report does not allow us to determine what criterion was used to split the amount allocated to each community, nor what activities the funds went to",
        "quote_src": "EITI Mozambique, the official transparency body, in its 2020 and 2021 reports",
        "trend_title": "Total transferred to communities, by year",
        "trend_note": "In 2022 the figure falls 39%; in 2024 it quadruples. The reports explain neither move.",
        "find_title": "Find your locality",
        "map_title": "Where the 2.75% lands",
        "map_sub": "Total per province in the selected year. Tap a province to filter the list.",
        "map_low": "less",
        "map_high": "more",
        "map_none": "No transfer recorded",
        "map_all": "All provinces",
        "map_year": "Year",
        "cap_lng": "Palma, Cabo Delgado — natural gas. The province received {cd} in 2024.",
        "cap_coal": "Moatize, Tete — coal. Tete received {te} in 2024, more than any other province.",
        "credits": "Images: see CREDITS.md in the repository.",
        "cur_mzn": "Meticais",
        "cur_usd": "Dollars",
        "mzn_m": "million MZN",
        "usd_m": "million USD",
        "fx_note": "Converted at each year's official average rate (World Bank, PA.NUS.FCRF), not at today's rate.",
        "lvl_prov": "Provinces",
        "lvl_dist": "Districts",
        "map_sub_d": "Total per district in the selected year. Tap a district to filter the list.",
        "updated": "Data from 2019 to 2024. Updated",
    },
    "fr": {
        "title": "Quinhão", "lang_name": "Français",
        "tagline": "La part de votre communauté sur les 2,75 % miniers.",
        "intro": "La loi verse 2,75 % de l'impôt sur la production minière et pétrolière aux "
                 "communautés où se fait l'extraction. Choisissez votre localité et voyez le montant.",
        "pick": "Choisissez votre localité", "search": "Chercher une localité ou un district…",
        "nomatch": "Aucune localité trouvée.",
        "received": "Transféré à cette localité", "year": "Année", "amount": "Montant",
        "mineral": "Activité minière", "total": "Total sur 6 ans", "no_data": "Aucun transfert enregistré cette année.",
        "next_title": "Ce que vous pouvez en faire",
        "next_body": "L'organe responsable de cet argent est le <strong>Secrétariat de district</strong>, "
                     "avec le <strong>Conseil consultatif de localité</strong>. "
                     "La loi limite les dépenses à quatre domaines :",
        "ask_title": "Questions que vous avez le droit de poser",
        "asks": ["À quels projets le montant de cette année a-t-il servi ?",
                 "Où sont les procès-verbaux du Conseil consultatif approuvant ces projets ?",
                 "Les travaux sont-ils terminés ? Puis-je voir le procès-verbal de réception ?"],
        "source_title": "D'où viennent ces chiffres",
        "source_body": "Rapports ITIE Mozambique, publiés sur eiti.org. Aucun chiffre n'a été saisi à "
                       "la main — ils sont extraits des PDF officiels par un programme qui échoue si "
                       "les totaux ne correspondent pas à ceux publiés.",
        "caveat_title": "Ce que ces chiffres ne disent pas",
        "caveat_body": "L'État déclare 100 % d'exécution — l'argent est sorti. Cela ne veut pas dire "
                       "que quelque chose a été construit. Et l'ITIE écrit elle-même que le critère "
                       "de répartition entre communautés ne peut être déterminé.",
        "note2022": "2022 est absent ci-dessus : cette année-là, le rapport officiel publie les dépenses par projet au niveau national, sans répartition par localité.",
        "hero_kicker": "Ce que la loi promet aux communautés minières",
        "hero_h": "{com} aux communautés.<br>{prov} aux directions provinciales.",
        "hero_p": "En 2024, les communautés qui vivent sur le rubis, le charbon et le gaz ont reçu moins d'un tiers de ce qui est allé aux capitales provinciales. Personne n'explique pourquoi.",
        "cmp_title": "Où est allé l'argent extractif en 2024",
        "cmp_com": "Communautés affectées",
        "cmp_prov": "Directions provinciales",
        "quote": "le rapport d'exécution budgétaire ne permet pas de déterminer le critère utilisé pour répartir le montant alloué à chaque communauté, ni les activités financées",
        "quote_src": "ITIE Mozambique, l'organisme officiel de transparence, rapports 2020 et 2021",
        "trend_title": "Total transféré aux communautés, par année",
        "trend_note": "En 2022 le montant chute de 39 % ; en 2024 il quadruple. Les rapports n'expliquent ni l'un ni l'autre.",
        "find_title": "Trouvez votre localité",
        "map_title": "Où atterrissent les 2,75 %",
        "map_sub": "Total par province pour l'année choisie. Touchez une province pour filtrer la liste.",
        "map_low": "moins",
        "map_high": "plus",
        "map_none": "Aucun transfert enregistré",
        "map_all": "Toutes les provinces",
        "map_year": "Année",
        "cap_lng": "Palma, Cabo Delgado — gaz naturel. La province a reçu {cd} en 2024.",
        "cap_coal": "Moatize, Tete — charbon. Tete a reçu {te} en 2024, plus que toute autre province.",
        "credits": "Images : voir CREDITS.md dans le dépôt.",
        "cur_mzn": "Meticais",
        "cur_usd": "Dollars",
        "mzn_m": "millions MZN",
        "usd_m": "millions USD",
        "fx_note": "Converti au taux moyen officiel de chaque année (Banque mondiale, PA.NUS.FCRF), non au taux actuel.",
        "lvl_prov": "Provinces",
        "lvl_dist": "Districts",
        "map_sub_d": "Total par district pour l'année choisie. Touchez un district pour filtrer la liste.",
        "updated": "Données de 2019 à 2024. Mis à jour le",
    },
}

YEARS = [2019, 2021, 2023, 2024]


def load():
    """One record per locality: totals by year, plus the mineral where it is published."""
    by_loc = {}
    with (ROOT / "data" / "transfers.csv").open(encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            key = f"{r['locality']}|{r['district']}|{r['province']}"
            e = by_loc.setdefault(key, {
                "l": r["locality"], "d": r["district"], "p": r["province"], "m": "", "y": {}})
            if r["mining_activity"]:
                e["m"] = r["mining_activity"]
            if r["allocated_mzn_m"]:
                e["y"][r["year"]] = round(float(r["allocated_mzn_m"]), 2)
    return sorted(by_loc.values(), key=lambda e: (e["p"], e["d"], e["l"]))


HTML = r"""<!DOCTYPE html>
<html lang="pt">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Quinhão — __TAGLINE__</title>
<meta name="description" content="__TAGLINE__">
<style>
:root{
  color-scheme:light;
  --bg:#fcfcfb; --surface:#fff; --fg:#0b0b0b; --fg2:#52514e; --mut:#77746d;
  --line:#e3e0d9; --acc:#1c5cab; --s1:#2a78d6; --s2:#eb6834; --quote:#f4f1ea;
  --m1:#9ec5f4; --m2:#6da7ec; --m3:#3987e5; --m4:#256abf; --m5:#104281; --m0:#e8e5de;
}
@media(prefers-color-scheme:dark){:root:where(:not([data-theme=light])){
  color-scheme:dark;
  --bg:#141413; --surface:#1a1a19; --fg:#fff; --fg2:#c3c2b7; --mut:#8e8b82;
  --line:#2f2e2b; --acc:#86b6ef; --s1:#3987e5; --s2:#d95926; --quote:#201f1d;
  --m1:#184f95; --m2:#256abf; --m3:#3987e5; --m4:#6da7ec; --m5:#b7d3f6; --m0:#2a2926;
}}
:root[data-theme=dark]{
  color-scheme:dark;
  --bg:#141413; --surface:#1a1a19; --fg:#fff; --fg2:#c3c2b7; --mut:#8e8b82;
  --line:#2f2e2b; --acc:#86b6ef; --s1:#3987e5; --s2:#d95926; --quote:#201f1d;
  --m1:#184f95; --m2:#256abf; --m3:#3987e5; --m4:#6da7ec; --m5:#b7d3f6; --m0:#2a2926;
}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--fg);
 font:17px/1.6 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;
 font-variant-numeric:tabular-nums}
.wrap{max-width:52rem;margin:0 auto;padding:0 1rem 5rem}
header{display:flex;justify-content:space-between;align-items:center;gap:1rem;
 padding:1rem 0;flex-wrap:wrap}
.brand{font-weight:700;font-size:1.05rem;letter-spacing:-.01em}
.brand span{color:var(--s2)}
nav{display:flex;gap:.35rem}
nav button{font:inherit;font-size:.82rem;padding:.3rem .7rem;border:1px solid var(--line);
 background:var(--surface);color:var(--fg2);border-radius:999px;cursor:pointer}
nav button[aria-pressed=true]{background:var(--fg);color:var(--bg);border-color:var(--fg);font-weight:600}
.kicker{color:var(--s2);font-weight:700;font-size:.8rem;letter-spacing:.09em;
 text-transform:uppercase;margin:2rem 0 .75rem}
h1{font-size:clamp(1.9rem,6vw,3.1rem);line-height:1.12;letter-spacing:-.03em;
 margin:0 0 1rem;font-weight:800;text-wrap:balance}
.lede{font-size:clamp(1rem,2.6vw,1.2rem);color:var(--fg2);margin:0 0 2rem;max-width:40rem}
section{margin:3rem 0 0;padding-top:2rem;border-top:1px solid var(--line)}
section:first-of-type{border-top:0;padding-top:0}
h2{font-size:1.25rem;letter-spacing:-.01em;margin:0 0 .3rem;font-weight:700}
.sub{color:var(--mut);font-size:.9rem;margin:0 0 1.2rem}
figure{margin:1.2rem 0}
svg{display:block;width:100%;height:auto;overflow:visible}
.lbl{fill:var(--fg2);font-size:17px}
.val{fill:var(--fg);font-size:19px;font-weight:700}
.axis{stroke:var(--line);stroke-width:1}
blockquote{margin:1.5rem 0 0;padding:1.3rem 1.4rem;background:var(--quote);
 border-left:4px solid var(--s2);border-radius:0 .5rem .5rem 0}
blockquote p{margin:0;font-size:1.06rem;line-height:1.5;font-style:italic}
blockquote cite{display:block;margin-top:.8rem;font-size:.85rem;color:var(--mut);font-style:normal}
label{position:absolute;width:1px;height:1px;overflow:hidden;clip-path:inset(50%);white-space:nowrap}
input{font:inherit;width:100%;padding:.8rem .9rem;border:2px solid var(--line);
 border-radius:.6rem;background:var(--surface);color:var(--fg)}
input:focus{outline:3px solid var(--acc);outline-offset:1px;border-color:transparent}
ul.hits{list-style:none;margin:.5rem 0 0;padding:0;max-height:17rem;overflow:auto;
 border:1px solid var(--line);border-radius:.6rem}
ul.hits:empty{display:none}
ul.hits button{display:block;width:100%;text-align:left;font:inherit;padding:.7rem .9rem;
 background:var(--surface);color:var(--fg);border:0;border-bottom:1px solid var(--line);cursor:pointer}
ul.hits button:hover,ul.hits button:focus{background:var(--acc);color:var(--bg)}
ul.hits small{display:block;opacity:.75;font-size:.82rem}
.card{background:var(--surface);border:1px solid var(--line);border-radius:.8rem;
 padding:1.3rem;margin-top:1.3rem}
.hero-n{font-size:clamp(2.2rem,8vw,3rem);font-weight:800;color:var(--s2);line-height:1;letter-spacing:-.03em}
.unit{font-size:.95rem;color:var(--mut);font-weight:500}
table{width:100%;border-collapse:collapse;margin:.6rem 0}
th,td{text-align:left;padding:.5rem .3rem;border-bottom:1px solid var(--line);font-size:.95rem}
td.n{text-align:right;white-space:nowrap}
ol,ul.plain{padding-left:1.25rem;margin:.6rem 0}
li{margin:.35rem 0}
.note{color:var(--mut);font-size:.88rem}
footer{margin-top:3rem;padding-top:1.5rem;border-top:1px solid var(--line);
 font-size:.85rem;color:var(--mut)}
.hero{position:relative;padding-top:1rem}
.strata{position:absolute;inset:auto 0 -1rem 0;height:120px;z-index:-1;opacity:.5;
 -webkit-mask-image:linear-gradient(#000,transparent);mask-image:linear-gradient(#000,transparent)}
.ico{width:1.05em;height:1.05em;vertical-align:-.16em;margin-right:.3em;flex:none}
.shots{display:grid;grid-template-columns:1fr 1fr;gap:1rem;margin:2rem 0 0}
@media(max-width:33rem){.shots{grid-template-columns:1fr}}
.shots figure{margin:0}
.shots img{width:100%;height:auto;aspect-ratio:15/9;object-fit:cover;border-radius:.6rem;
 background:var(--quote);display:block}
.shots figcaption{font-size:.85rem;color:var(--mut);margin-top:.5rem;line-height:1.45}
.chips{display:flex;gap:.4rem;flex-wrap:wrap;margin:0 0 1rem}
.chips button{font:inherit;font-size:.85rem;padding:.35rem .8rem;border:1px solid var(--line);
 background:var(--surface);color:var(--fg2);border-radius:999px;cursor:pointer}
.chips button[aria-pressed=true]{background:var(--acc);color:var(--bg);border-color:var(--acc);font-weight:600}
.maprow{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.1fr);gap:1.5rem;align-items:start}
@media(max-width:33rem){.maprow{grid-template-columns:1fr}}
#map path{stroke:var(--bg);stroke-width:1.2;cursor:pointer}
#map path:hover{stroke:var(--fg);stroke-width:2}
#map path[aria-current=true]{stroke:var(--fg);stroke-width:2.5}
.legend{display:flex;align-items:center;gap:.4rem;font-size:.8rem;color:var(--mut);margin-top:.7rem}
.legend i{width:1.4rem;height:.7rem;border-radius:2px;display:inline-block}
.plist{list-style:none;margin:0;padding:0}
.plist li{display:flex;justify-content:space-between;gap:1rem;padding:.4rem 0;
 border-bottom:1px solid var(--line);font-size:.93rem}
.plist b{font-weight:700}
a{color:var(--acc)}
[hidden]{display:none!important}
@media print{nav{display:none}}
</style>
</head>
<body>
<div class="wrap">
<header>
  <div class="brand">Quinh<span>ã</span>o</div>
  <div style="display:flex;gap:.35rem;flex-wrap:wrap"><nav class="chips" id="cur" style="margin:0" role="group"></nav><nav id="langs" aria-label="Language"></nav></div>
</header>

<div class="hero">
<svg class="strata" viewBox="0 0 600 120" preserveAspectRatio="none" aria-hidden="true">
  <path d="M0 96 Q150 74 300 88 T600 78 V120 H0Z" fill="var(--s1)" opacity=".16"/>
  <path d="M0 108 Q150 90 300 102 T600 94 V120 H0Z" fill="var(--s2)" opacity=".2"/>
  <path d="M0 118 Q150 106 300 114 T600 108 V120 H0Z" fill="var(--s1)" opacity=".3"/>
</svg>
<p class="kicker" id="kicker"></p>
<h1 id="heroh"></h1>
<p class="lede" id="herop"></p>
</div>

<div class="shots">
  <figure><img src="img/lng-afungi.webp" width="900" height="540" loading="lazy" decoding="async" alt="" id="im1">
    <figcaption id="cap1"></figcaption></figure>
  <figure><img src="img/moatize-coal.webp" width="900" height="540" loading="lazy" decoding="async" alt="" id="im2">
    <figcaption id="cap2"></figcaption></figure>
</div>

<section>
  <h2 id="cmp-t"></h2>
  <p class="sub" id="cmp-s"></p>
  <figure><svg id="cmp" viewBox="0 0 640 150" role="img" aria-labelledby="cmp-t"></svg></figure>
  <blockquote>
    <p id="quote"></p>
    <cite id="quote-src"></cite>
  </blockquote>
</section>

<section>
  <h2 id="trend-t"></h2>
  <p class="sub" id="trend-s"></p>
  <figure><svg id="trend" viewBox="0 0 640 220" role="img" aria-labelledby="trend-t"></svg></figure>
  <p class="note" id="trend-note"></p>
  <p class="note" id="fx-note"></p>
</section>

<section>
  <h2 id="map-t"></h2>
  <p class="sub" id="map-s"></p>
  <div class="chips" id="lvl" role="group"></div>
  <div class="chips" id="years" role="group"></div>
  <div class="maprow">
    <div>
      <svg id="map" viewBox="__MAPVB__" role="img" aria-labelledby="map-t"></svg>
      <div class="legend"><span id="lg-low"></span>
        <i style="background:var(--m1)"></i><i style="background:var(--m2)"></i>
        <i style="background:var(--m3)"></i><i style="background:var(--m4)"></i>
        <i style="background:var(--m5)"></i><span id="lg-high"></span></div>
    </div>
    <ul class="plist" id="plist"></ul>
  </div>
</section>

<section>
  <h2 id="find-t"></h2>
  <label for="q" id="picklbl"></label>
  <input id="q" type="search" autocomplete="off" enterkeyhint="search">
  <ul class="hits" id="hits"></ul>
  <p id="nomatch" class="note" hidden></p>

  <div id="result" hidden>
    <div class="card">
      <h2 id="r-title"></h2>
      <p class="sub" id="r-where"></p>
      <figure><svg id="r-chart" viewBox="0 0 640 170" role="img"></svg></figure>
      <p><span class="hero-n" id="r-total"></span> <span class="unit" id="r-unit"></span><br>
      <span class="note" id="r-totlbl"></span></p>
      <p class="note" id="r-note2022"></p>
      <table>
        <thead><tr><th id="h-year"></th><th class="n" id="h-amt"></th></tr></thead>
        <tbody id="r-rows"></tbody>
      </table>
    </div>
    <div class="card">
      <h2 id="n-title"></h2>
      <p id="n-body"></p>
      <ul class="plain" id="n-uses"></ul>
      <h2 id="a-title" style="margin-top:1.2rem"></h2>
      <ol id="a-list"></ol>
    </div>
  </div>
</section>

<section>
  <h2 id="s-title"></h2>
  <p class="note" id="s-body"></p>
  <h2 id="c-title" style="margin-top:1.3rem"></h2>
  <p class="note" id="c-body"></p>
</section>

<footer><span id="credits"></span><br><span id="f-upd"></span> __BUILT__ ·
<a href="https://github.com/eltonlaice/quinhao">github.com/eltonlaice/quinhao</a> ·
<a href="https://eiti.org/countries/mozambique">eiti.org</a></footer>
</div>

<script>
const DATA=__DATA__, T=__T__, USES=__USES__, YEARS=__YEARS__,
      NATIONAL=__NATIONAL__, PROVINCES=__PROVINCES__, MAP=__MAP__, FX=__FX__, DIST=__DIST__, DKEY=__DKEY__;
let year=2024, prov=null, cur="MZN", level="prov";

/* Each year converts at its own average rate; a 2019 figure at a 2024 rate would
   misstate it by about a tenth. */
function conv(v,y){return cur==="MZN"?v:v/(FX[String(y)]||FX["2024"]);}
function unit(){return cur==="MZN"?T[lang].mzn_m:T[lang].usd_m;}
let lang=(navigator.language||"pt").slice(0,2); if(!T[lang]) lang="pt";
let picked=null;
const $=id=>document.getElementById(id);
const loc=()=>lang==="en"?"en-GB":lang==="fr"?"fr-FR":"pt-PT";
function fmt(n){
  const d=cur==="MZN"?1:(n>=1?2:n>=0.01?3:0);
  if(cur==="USD"&&n>0&&n<0.005) return "< 0,01".replace(",",lang==="en"?".":",");
  return n.toLocaleString(loc(),{minimumFractionDigits:d,maximumFractionDigits:d});
}
/* One glyph per commodity: identity at a glance, zero bytes over the wire. */
const ICONS={
 rubi:'<path d="M5 3h14l3 6-10 12L2 9z"/><path d="M2 9h20M9 3 7 9l5 12M15 3l2 6-5 12" fill="none" stroke="var(--bg)" stroke-width="1.1"/>',
 carvao:'<path d="M7 5 3 13l5 6 7-1 6-6-4-7z"/><path d="m7 5 4 7-3 7M15 18l-4-6 9-2" fill="none" stroke="var(--bg)" stroke-width="1.1"/>',
 gas:'<path d="M12 2c3 4 5 6 5 9a5 5 0 1 1-10 0c0-2 1-3 2-5 1 2 2 2 2 4 0-3 .5-5 1-8z"/>',
 areia:'<circle cx="7" cy="16" r="3"/><circle cx="14" cy="17" r="2.2"/><circle cx="11" cy="10" r="2.6"/><circle cx="18" cy="12" r="1.8"/><circle cx="5" cy="9" r="1.6"/>',
 agua:'<path d="M12 2c4 6 6 8 6 11a6 6 0 0 1-12 0c0-3 2-5 6-11z"/>',
 ouro:'<path d="M3 8h18l-2 10H5z"/><path d="M3 8 6 4h12l3 4" fill="none" stroke="var(--bg)" stroke-width="1.1"/>',
 pedra:'<path d="M4 9 9 4l7 1 4 6-3 9H7z"/>'};
function icon(activity){
  const a=(activity||"").toLowerCase();
  const k=/rubi/.test(a)?"rubi":/carv/.test(a)?"carvao":/g[aá]s|lng|condes/.test(a)?"gas":
    /areia|ilmen|iimen|zirc|titan|turmal|tantal|grafite/.test(a)?"areia":
    /[aá]gua/.test(a)?"agua":/ouro|bauxit/.test(a)?"ouro":
    /granito|calc|saibro|brita|riolito|pedra|guano/.test(a)?"pedra":null;
  return k?`<svg class="ico" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">${ICONS[k]}</svg>`:"";
}
const esc=t=>String(t).replace(/[&<>]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;"}[c]));

/* Horizontal bars: two categories, direct-labelled, 4px rounded data-end. */
function hbars(svg,items){
  const W=640,rowH=64,max=Math.max(...items.map(i=>i.v));
  svg.setAttribute("viewBox",`0 0 ${W} ${items.length*rowH}`);
  svg.innerHTML=items.map((it,i)=>{
    const y=i*rowH, w=Math.max(4,(W-95)*it.v/max);
    return `<g><title>${esc(it.k)}: ${fmt(it.v)}</title>`+
      `<text class="lbl" x="0" y="${y+16}">${esc(it.k)}</text>`+
      `<rect x="0" y="${y+24}" width="${w}" height="26" rx="4" fill="${it.c}"/>`+
      `<text class="val" x="${w+12}" y="${y+44}">${fmt(it.v)}</text></g>`;
  }).join("");
}

/* Vertical bars over time: one series, one hue, every bar labelled. */
function vbars(svg,items,color){
  const W=640,H=220,base=H-34,top=26,max=Math.max(...items.map(i=>i.v)),
        n=items.length,gap=10,bw=(W-(n-1)*gap)/n;
  svg.setAttribute("viewBox",`0 0 ${W} ${H}`);
  svg.innerHTML=`<line class="axis" x1="0" y1="${base}" x2="${W}" y2="${base}"/>`+
    items.map((it,i)=>{
      const h=Math.max(3,(base-top)*it.v/max), x=i*(bw+gap), y=base-h;
      return `<g><title>${esc(it.k)}: ${fmt(it.v)}</title>`+
        `<rect x="${x}" y="${y}" width="${bw}" height="${h}" rx="4" fill="${color}"/>`+
        `<text class="val" x="${x+bw/2}" y="${y-8}" text-anchor="middle">${fmt(it.v)}</text>`+
        `<text class="lbl" x="${x+bw/2}" y="${base+20}" text-anchor="middle">${esc(it.k)}</text></g>`;
    }).join("");
}

/* Province totals for a year, straight from the same locality rows the list uses. */
function provTotals(y){
  const t={};
  for(const e of DATA){const v=e.y[String(y)]; if(v!=null) t[e.p]=(t[e.p]||0)+conv(v,y);}
  return t;
}

/* District totals, keyed by the polygon name so the map can look them up directly. */
function distTotals(y){
  const t={};
  for(const e of DATA){
    const v=e.y[String(y)], k=DKEY[e.d];
    if(v!=null&&k) t[k]=(t[k]||0)+conv(v,y);
  }
  return t;
}

function drawMap(){
  const dist=level==="dist";
  const tot=dist?distTotals(year):provTotals(year);
  const shapes=dist?DIST:MAP;
  const sel=dist?(prov?DKEY[prov]:null):prov;
  const vals=Object.values(tot).filter(v=>v>0).sort((a,b)=>a-b);
  const step=v=>{
    if(!(v>0)) return "var(--m0)";
    const i=Math.min(4,Math.floor(vals.indexOf(v)/vals.length*5));
    return `var(--m${i+1})`;
  };
  $("map").innerHTML=Object.entries(shapes).map(([name,d])=>{
    const v=tot[name]||0;
    return `<path d="${d}" fill="${step(v)}" data-p="${esc(name)}" tabindex="0" role="button"`+
      (sel===name?' aria-current="true"':"")+
      `><title>${esc(name)}: ${v>0?fmt(v)+" "+unit():T[lang].map_none}</title></path>`;
  }).join("")
  + (dist?Object.values(MAP).map(d=>
      `<path d="${d}" fill="none" stroke="var(--fg)" stroke-width="1.6" opacity=".35" pointer-events="none"/>`).join(""):"");
  const rows=Object.entries(tot).filter(([,v])=>v>0).sort((a,b)=>b[1]-a[1])
    .slice(0,dist?12:20);
  $("plist").innerHTML=(dist?rows:Object.entries(shapes).map(([n])=>[n,tot[n]||0])
      .sort((a,b)=>b[1]-a[1]))
    .map(([n,v])=>`<li><span>${esc(n)}</span><b>${v>0?fmt(v):"—"}</b></li>`).join("");
}
$("map").addEventListener("click",e=>{
  const pth=e.target.closest("path"); if(!pth) return;
  const hit=pth.dataset.p;
  const mine=level==="dist"
    ? Object.keys(DKEY).find(k=>DKEY[k]===hit)
    : hit;
  prov = (mine&&prov===mine) ? null : (mine||null);
  drawMap(); search();
});
$("map").addEventListener("keydown",e=>{
  if(e.key==="Enter"||e.key===" "){e.preventDefault();e.target.click();}
});
$("lvl").addEventListener("click",e=>{
  const v=e.target.dataset.v; if(!v||v===level) return;
  level=v; prov=null; render(); search();
});
$("years").addEventListener("click",e=>{
  const y=e.target.dataset.y; if(!y) return;
  year=+y; drawMap();
  [...$("years").children].forEach(b=>b.setAttribute("aria-pressed",+b.dataset.y===year));
});

$("cur").addEventListener("click",e=>{
  const c=e.target.dataset.c; if(!c) return;
  cur=c; render();
});

$("langs").innerHTML=Object.keys(T).map(k=>
  `<button data-l="${k}" type="button">${T[k].lang_name}</button>`).join("");
$("langs").onclick=e=>{const l=e.target.dataset.l; if(l){lang=l; render();}};

function css(v){return getComputedStyle(document.documentElement).getPropertyValue(v).trim()}

function render(){
  const t=T[lang];
  document.documentElement.lang=lang;
  const text={kicker:t.hero_kicker,herop:t.hero_p,"cmp-t":t.cmp_title,
    quote:"“"+t.quote+"”","quote-src":t.quote_src,"trend-t":t.trend_title,
    "trend-note":t.trend_note,"find-t":t.find_title,picklbl:t.pick,nomatch:t.nomatch,
    "h-year":t.year,"h-amt":t.amount,"r-totlbl":t.total,"r-unit":unit(),
    "n-title":t.next_title,"a-title":t.ask_title,"s-title":t.source_title,
    "s-body":t.source_body,"c-title":t.caveat_title,"c-body":t.caveat_body,
    "r-note2022":t.note2022,"f-upd":t.updated,credits:t.credits,"cmp-s":unit(),"trend-s":unit(),"fx-note":cur==="USD"?t.fx_note:""};
  for(const [id,v] of Object.entries(text)) $(id).textContent=v;
  const p24=provTotals(2024), money=v=>fmt(v)+" "+unit();
  const fill=str=>str.replace("{com}",money(conv(NATIONAL["2024"],2024)))
    .replace("{prov}",money(conv(PROVINCES,2024)))
    .replace("{cd}",money(p24["Cabo Delgado"]||0)).replace("{te}",money(p24["Tete"]||0));
  $("heroh").innerHTML=fill(t.hero_h);
  $("cap1").textContent=fill(t.cap_lng); $("cap2").textContent=fill(t.cap_coal);
  $("im1").alt=fill(t.cap_lng); $("im2").alt=fill(t.cap_coal);
  $("n-body").innerHTML=t.next_body;
  $("q").placeholder=t.search;
  $("n-uses").innerHTML=USES[lang].map(u=>`<li>${esc(u)}</li>`).join("");
  $("a-list").innerHTML=t.asks.map(a=>`<li>${esc(a)}</li>`).join("");
  [...$("langs").children].forEach(b=>b.setAttribute("aria-pressed",b.dataset.l===lang));

  $("cur").innerHTML=[["MZN",t.cur_mzn],["USD",t.cur_usd]].map(([c,n])=>
    `<button type="button" data-c="${c}" aria-pressed="${c===cur}">${n}</button>`).join("");
  $("map-t").textContent=t.map_title;
  $("map-s").textContent=level==="dist"?t.map_sub_d:t.map_sub;
  $("lvl").innerHTML=[["prov",t.lvl_prov],["dist",t.lvl_dist]].map(([k,n])=>
    `<button type="button" data-v="${k}" aria-pressed="${k===level}">${n}</button>`).join("");
  $("lg-low").textContent=t.map_low; $("lg-high").textContent=t.map_high;
  $("years").innerHTML=YEARS.map(y=>
    `<button type="button" data-y="${y}" aria-pressed="${y===year}">${y}</button>`).join("");
  drawMap();
  hbars($("cmp"),[{k:t.cmp_com,v:conv(NATIONAL["2024"],2024),c:css("--s1")},
                  {k:t.cmp_prov,v:conv(PROVINCES,2024),c:css("--s2")}]);
  vbars($("trend"),Object.entries(NATIONAL).map(([k,v])=>({k,v:conv(v,k)})),css("--s1"));
  search(); if(picked) show(picked);
}

function search(){
  const q=$("q").value.trim().toLowerCase();
  if(!q&&!prov){$("hits").innerHTML="";$("nomatch").hidden=true;return;}
  const hits=DATA.filter(e=>(!prov||(level==="dist"?e.d===prov:e.p===prov))&&
    (!q||(e.l+" "+e.d+" "+e.p).toLowerCase().includes(q))).slice(0,60);
  $("nomatch").hidden=hits.length>0;
  $("hits").innerHTML=hits.map(e=>
    `<li><button type="button" data-k="${esc(e.l)}|${esc(e.d)}">${icon(e.m)}${esc(e.l)}`+
    `<small>${esc(e.d)}, ${esc(e.p)}</small></button></li>`).join("");
}
$("q").oninput=search;
$("hits").onclick=e=>{
  const b=e.target.closest("button"); if(!b) return;
  const [l,d]=b.dataset.k.split("|");
  picked=DATA.find(x=>x.l===l&&x.d===d);
  $("q").value=""; search(); show(picked);
  $("result").scrollIntoView({behavior:"smooth",block:"start"});
};

function show(e){
  const t=T[lang];
  $("result").hidden=false;
  $("r-title").textContent=`${t.received}: ${e.l}`;
  $("r-where").innerHTML=icon(e.m)+esc([e.d,e.p,e.m].filter(Boolean).join(" · "));
  const got=YEARS.filter(y=>e.y[String(y)]!=null).map(y=>({k:String(y),v:conv(e.y[String(y)],y)}));
  vbars($("r-chart"),got.length?got:[{k:"—",v:0}],css("--s1"));
  $("r-total").textContent=fmt(got.reduce((a,b)=>a+b.v,0));
  $("r-rows").innerHTML=YEARS.map(y=>{
    const v=e.y[String(y)];
    return `<tr><td>${y}</td><td class="n">${v!=null?fmt(conv(v,y))+" "+unit():
      '<span class="note">'+t.no_data+'</span>'}</td></tr>`;
  }).join("");
}
render();
</script>
</body>
</html>
"""

# geoBoundaries spells districts without accents, and Pemba is filed as a city.
DISTRICT_ALIASES = {"Pemba": "Cidade De Pemba", "Alto Moloucue": "Alto Molocue"}


def match_districts(mine, adm2):
    """Map each district name in the EITI data to its geoBoundaries polygon."""
    import unicodedata

    def norm(x):
        return "".join(c for c in unicodedata.normalize("NFD", x.lower()) if c.isalnum())

    lookup = {norm(k): k for k in adm2}
    out, missing = {}, []
    for d in sorted(mine):
        target = DISTRICT_ALIASES.get(d, d)
        hit = lookup.get(norm(target))
        if hit:
            out[d] = hit
        else:
            missing.append(d)
    assert not missing, f"districts with no polygon: {missing}"
    return out


NATIONAL = {2019: 88.0, 2021: 73.4, 2022: 44.6, 2023: 77.1, 2024: 318.7}


def main():
    import datetime
    data = load()
    with (ROOT / "data" / "provinces.csv").open(encoding="utf-8") as fh:
        provinces = round(sum(float(r["allocated_mzn_m"]) for r in csv.DictReader(fh)), 1)
    with (ROOT / "data" / "fx.csv").open(encoding="utf-8") as fh:
        fx = {r["year"]: float(r["mzn_per_usd"]) for r in csv.DictReader(fh)}
    map_paths, mw, mh, bounds = build_map.build()
    dist_paths, _, _, _ = build_map.build(tol=0.04, lvl="ADM2", bounds=bounds)
    dkey = match_districts({e["d"] for e in data if e["d"]}, dist_paths)
    out = ROOT / "docs" / "index.html"
    out.parent.mkdir(exist_ok=True)
    html = HTML
    for k, v in {
        "__DATA__": json.dumps(data, ensure_ascii=False, separators=(",", ":")),
        "__T__": json.dumps(T, ensure_ascii=False, separators=(",", ":")),
        "__USES__": json.dumps(USES, ensure_ascii=False, separators=(",", ":")),
        "__YEARS__": json.dumps(YEARS),
        "__NATIONAL__": json.dumps({str(y): v for y, v in NATIONAL.items()}),
        "__PROVINCES__": json.dumps(provinces),
        "__FX__": json.dumps(fx),
        "__MAP__": json.dumps(map_paths, ensure_ascii=False, separators=(",", ":")),
        "__DIST__": json.dumps(dist_paths, ensure_ascii=False, separators=(",", ":")),
        "__DKEY__": json.dumps(dkey, ensure_ascii=False, separators=(",", ":")),
        "__MAPVB__": f"0 0 {mw} {mh}",
        "__TAGLINE__": T["pt"]["tagline"],
        "__BUILT__": datetime.date.today().isoformat(),
    }.items():
        html = html.replace(k, v)
    out.write_text(html, encoding="utf-8")
    kb = out.stat().st_size / 1024
    assert kb < 130, f"page grew to {kb:.0f} KB - it must stay small for slow connections"
    print(f"wrote {out.relative_to(ROOT)} ({kb:.0f} KB, {len(data)} localities)")


if __name__ == "__main__":
    main()
