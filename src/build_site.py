"""Build the public page from the extracted CSVs.

One self-contained HTML file: no external requests, no fonts, no frameworks, so it
loads on a slow connection and keeps working offline once opened. Data is inlined.

Run: python3 src/build_site.py   ->   docs/index.html
"""

import csv
import json
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
        "mineral": "Actividade mineira", "total": "Total em 6 anos",
        "mzn_m": "milhões de MZN", "no_data": "Sem transferência registada neste ano.",
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
        "mineral": "Mining activity", "total": "Total over 6 years",
        "mzn_m": "million MZN", "no_data": "No transfer recorded this year.",
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
        "mineral": "Activité minière", "total": "Total sur 6 ans",
        "mzn_m": "millions MZN", "no_data": "Aucun transfert enregistré cette année.",
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


HTML = """<!DOCTYPE html>
<html lang="pt">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Quinhão — %(tagline_pt)s</title>
<meta name="description" content="%(tagline_pt)s">
<style>
:root{--bg:#fffdf8;--fg:#1a1a1a;--mut:#5c5651;--line:#ded7cc;--acc:#8a5a00;--card:#fff}
@media(prefers-color-scheme:dark){:root{--bg:#16150f;--fg:#f2efe8;--mut:#a9a299;--line:#332f28;--acc:#e0a53a;--card:#1f1d16}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);font:17px/1.55 system-ui,-apple-system,Segoe UI,Roboto,sans-serif}
.wrap{max-width:46rem;margin:0 auto;padding:1.5rem 1rem 4rem}
h1{font-size:2.1rem;margin:.2rem 0 .3rem;letter-spacing:-.02em}
.tag{color:var(--acc);font-weight:600;margin:0 0 1rem}
.intro{color:var(--mut);margin:0 0 1.5rem}
nav{display:flex;gap:.4rem;margin-bottom:1.2rem;flex-wrap:wrap}
nav button{font:inherit;font-size:.9rem;padding:.4rem .8rem;border:1px solid var(--line);background:var(--card);color:var(--fg);border-radius:999px;cursor:pointer}
nav button[aria-pressed=true]{background:var(--acc);color:var(--bg);border-color:var(--acc);font-weight:600}
label{display:block;font-weight:600;margin:0 0 .4rem}
input,select{font:inherit;width:100%%;padding:.7rem .8rem;border:2px solid var(--line);border-radius:.5rem;background:var(--card);color:var(--fg)}
input:focus,select:focus{outline:3px solid var(--acc);outline-offset:1px}
ul.hits{list-style:none;margin:.5rem 0 0;padding:0;max-height:15rem;overflow:auto;border:1px solid var(--line);border-radius:.5rem}
ul.hits:empty{display:none}
ul.hits button{display:block;width:100%%;text-align:left;font:inherit;padding:.65rem .8rem;background:var(--card);color:var(--fg);border:0;border-bottom:1px solid var(--line);cursor:pointer}
ul.hits button:hover,ul.hits button:focus{background:var(--acc);color:var(--bg)}
ul.hits small{display:block;opacity:.75}
section{margin-top:2rem;border-top:1px solid var(--line);padding-top:1.3rem}
h2{font-size:1.15rem;margin:0 0 .6rem}
table{width:100%%;border-collapse:collapse;margin:.5rem 0}
th,td{text-align:left;padding:.5rem .3rem;border-bottom:1px solid var(--line)}
td.n{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
tr.tot td{font-weight:700;border-bottom:0;border-top:2px solid var(--fg)}
.big{font-size:1.9rem;font-weight:700;color:var(--acc);font-variant-numeric:tabular-nums}
.mut{color:var(--mut)}
ol,ul.plain{padding-left:1.2rem;margin:.5rem 0}
li{margin:.3rem 0}
footer{margin-top:2.5rem;font-size:.85rem;color:var(--mut)}
a{color:var(--acc)}
[hidden]{display:none!important}
</style>
</head>
<body>
<div class="wrap">
<nav id="langs"></nav>
<h1>Quinhão</h1>
<p class="tag" id="tagline"></p>
<p class="intro" id="intro"></p>

<label for="q" id="picklbl"></label>
<input id="q" type="search" autocomplete="off" enterkeyhint="search">
<ul class="hits" id="hits"></ul>
<p id="nomatch" class="mut" hidden></p>

<div id="result" hidden>
  <section>
    <h2 id="r-title"></h2>
    <p class="mut" id="r-where"></p>
    <table>
      <thead><tr><th id="h-year"></th><th class="n" id="h-amt"></th></tr></thead>
      <tbody id="r-rows"></tbody>
    </table>
    <p class="mut" id="r-note2022" style="font-size:.9rem"></p>
    <p><span class="big" id="r-total"></span> <span class="mut" id="r-unit"></span><br>
    <span class="mut" id="r-totlbl"></span></p>
  </section>
  <section>
    <h2 id="n-title"></h2>
    <p id="n-body"></p>
    <ul class="plain" id="n-uses"></ul>
  </section>
  <section>
    <h2 id="a-title"></h2>
    <ol id="a-list"></ol>
  </section>
</div>

<section>
  <h2 id="s-title"></h2>
  <p class="mut" id="s-body"></p>
  <h2 id="c-title" style="margin-top:1.2rem"></h2>
  <p class="mut" id="c-body"></p>
</section>

<footer><span id="f-upd"></span> %(built)s ·
<a href="https://github.com/eltonlaice/quinhao">github.com/eltonlaice/quinhao</a> ·
<a href="https://eiti.org/countries/mozambique">eiti.org</a></footer>
</div>
<script>
const DATA=%(data)s, T=%(t)s, USES=%(uses)s, YEARS=%(years)s;
let lang=(navigator.language||"pt").slice(0,2); if(!T[lang]) lang="pt";
let picked=null;
const $=id=>document.getElementById(id);
const fmt=n=>n.toLocaleString(lang==="en"?"en-GB":lang==="fr"?"fr-FR":"pt-PT",{minimumFractionDigits:1,maximumFractionDigits:1});

$("langs").innerHTML=Object.keys(T).map(k=>
  `<button data-l="${k}">${T[k].lang_name}</button>`).join("");
$("langs").onclick=e=>{const l=e.target.dataset.l; if(l){lang=l; render();}};

function render(){
  const t=T[lang];
  document.documentElement.lang=lang;
  for(const [id,v] of Object.entries({tagline:t.tagline,intro:t.intro,picklbl:t.pick,
    nomatch:t.nomatch,"h-year":t.year,"h-amt":t.amount,"r-totlbl":t.total,"r-unit":t.mzn_m,
    "n-title":t.next_title,"a-title":t.ask_title,"s-title":t.source_title,"s-body":t.source_body,
    "c-title":t.caveat_title,"c-body":t.caveat_body,"f-upd":t.updated,
    "r-note2022":t.note2022})) $(id).textContent=v;
  $("n-body").innerHTML=t.next_body;
  $("q").placeholder=t.search;
  $("n-uses").innerHTML=USES[lang].map(u=>`<li>${u}</li>`).join("");
  $("a-list").innerHTML=t.asks.map(a=>`<li>${a}</li>`).join("");
  [...$("langs").children].forEach(b=>b.setAttribute("aria-pressed",b.dataset.l===lang));
  search(); if(picked) show(picked);
}

function search(){
  const t=T[lang], q=$("q").value.trim().toLowerCase();
  if(!q){$("hits").innerHTML="";$("nomatch").hidden=true;return;}
  const hits=DATA.filter(e=>(e.l+" "+e.d+" "+e.p).toLowerCase().includes(q)).slice(0,30);
  $("nomatch").hidden=hits.length>0;
  $("hits").innerHTML=hits.map(e=>
    `<li><button data-k="${e.l}|${e.d}">${e.l}<small>${e.d}, ${e.p}</small></button></li>`).join("");
}
$("q").oninput=search;
$("hits").onclick=e=>{
  const b=e.target.closest("button"); if(!b) return;
  const [l,d]=b.dataset.k.split("|");
  picked=DATA.find(x=>x.l===l&&x.d===d);
  $("q").value=""; search(); show(picked); $("result").scrollIntoView({behavior:"smooth"});
};

function show(e){
  const t=T[lang];
  $("result").hidden=false;
  $("r-title").textContent=`${t.received}: ${e.l}`;
  $("r-where").textContent=[e.d,e.p,e.m].filter(Boolean).join(" · ");
  let tot=0;
  $("r-rows").innerHTML=YEARS.map(y=>{
    const v=e.y[String(y)];
    if(v!=null) tot+=v;
    return `<tr><td>${y}</td><td class="n">${v!=null?fmt(v)+" "+t.mzn_m:'<span class="mut">'+t.no_data+'</span>'}</td></tr>`;
  }).join("");
  $("r-total").textContent=fmt(tot);
}
render();
</script>
</body>
</html>
"""


def main():
    import datetime
    data = load()
    out = ROOT / "docs" / "index.html"
    out.parent.mkdir(exist_ok=True)
    out.write_text(HTML % {
        "data": json.dumps(data, ensure_ascii=False, separators=(",", ":")),
        "t": json.dumps(T, ensure_ascii=False, separators=(",", ":")),
        "uses": json.dumps(USES, ensure_ascii=False, separators=(",", ":")),
        "years": json.dumps(YEARS),
        "tagline_pt": T["pt"]["tagline"],
        "built": datetime.date.today().isoformat(),
    }, encoding="utf-8")
    kb = out.stat().st_size / 1024
    assert kb < 150, f"page grew to {kb:.0f} KB - it must stay small for slow connections"
    print(f"wrote {out.relative_to(ROOT)} ({kb:.0f} KB, {len(data)} localities)")


if __name__ == "__main__":
    main()
