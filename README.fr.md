# Quinhão

[English](README.md) · [Português](README.pt.md) · **Français**

> *Quinhão* (portugais) : la part qui revient de droit à quelqu'un.

La loi mozambicaine affecte **2,75 %** de l'impôt sur la production minière et pétrolière
aux communautés qui accueillent ces exploitations. L'argent est transféré. Ce que
personne ne peut vous dire, c'est **pourquoi votre communauté a reçu ce montant-là**, ni
**ce qui en a été fait**.

Ce n'est pas une accusation — c'est le constat de l'organisme de transparence lui-même.
Extrait du rapport ITIE Mozambique :

> « o REOE não permite aferir qual foi o critério utilizado para repartir o valor a alocar
> para cada comunidade e para quais actividades os fundos foram alocados »
>
> *(« le rapport d'exécution budgétaire ne permet pas de déterminer le critère utilisé
> pour répartir le montant alloué à chaque communauté, ni les activités financées »)*

Quinhão transforme six années de ces transferts en quelque chose qu'une personne à
Nyamanhumbir ou à Benga peut lire, comparer et contester.

## Ce que contient ce dépôt aujourd'hui

Un pipeline de données vérifié. L'application n'est pas encore construite.

| Fichier | Contenu |
|---|---|
| `src/extract.py` | Télécharge les PDF sources depuis eiti.org et les analyse |
| `data/transfers.csv` | 129 lignes — dotation vs. réalisation par localité, 2019/2021/2023/2024 |
| `data/projects.csv` | 41 lignes — projets financés et montants, 2022 (**brouillon**, voir réserves) |

### La série de six ans

| Année | Source | Granularité | Total (millions MZN) |
|---|---|---|---|
| 2019 | Rapport ITIE 2020, tableau 42 | localité | 88,0 dotés / 87,8 réalisés |
| 2021 | Rapport ITIE 2021, tableau 46 | localité | 73,4 |
| 2022 | Rapport ITIE 2022, tableau 45 | **projet individuel** | 44,6 |
| 2023 | Rapport ITIE 2023–2024, annexe 6.1 | localité + minerai | 77,1 |
| 2024 | Rapport ITIE 2023–2024, annexe 6.1 | localité + minerai | 318,7 |

Chaque chiffre remonte à un PDF public publié par [eiti.org](https://eiti.org/countries/mozambique).
Aucun nombre de ce dépôt n'a été saisi à la main.

## Exécution

Nécessite Python 3.9+ et `pdftotext` (poppler). Aucun paquet Python à installer.

```bash
brew install poppler           # macOS
sudo apt install poppler-utils # Debian/Ubuntu
```

```bash
python3 src/extract.py
```

Au premier lancement, le script télécharge ~25 Mo de PDF dans `data/raw/`, les met en
cache et régénère les deux CSV. Il se termine par une auto-vérification qui contrôle que
le total calculé de chaque année correspond au total publié — **si un analyseur dérive,
l'exécution échoue bruyamment** au lieu d'écrire de mauvais chiffres.

## Réserves sur les données

À lire avant d'utiliser les données. C'est l'essentiel, pas les petits caractères.

- **`projects.csv` (2022) est un brouillon.** Les montants sont fiables — leur somme
  correspond exactement au total publié de 44 608 666,89 MZN. Les libellés
  province/district/communauté et les descriptions de projets **ne le sont pas** : le PDF
  source fusionne ces cellules verticalement et coupe les descriptions au-dessus et
  au-dessous de leur propre montant. Chaque ligne porte `needs_review=yes` tant que les
  41 lignes n'ont pas été vérifiées à la main contre le PDF.
- **Dotation n'est pas livraison.** Les annexes comme les rapports indiquent une
  réalisation à ~100 % de la dotation. Cela signifie que l'argent est sorti du trésor,
  pas que quelque chose a été construit. La vérification de terrain est la couche
  manquante.
- **Décalage de deux ans.** Les fonds débloqués une année donnée reposent sur les
  recettes perçues deux ans plus tôt (n−2). La dotation 2021 reflète les recettes 2019.
- **Les 2,75 % ne portent pas sur toute l'assiette.** Le rapport 2020 montre que 2,75 %
  de l'impôt sur la production 2018 auraient dû donner 100,59 millions MZN ; 87,8
  millions ont été alloués — un écart de 12,79 millions. L'explication du ministère :
  seul l'impôt sur la production *minière* compte, pas celui sur le pétrole.
- **Les noms de localités varient d'une année à l'autre.** Topuito est classé sous Moma
  en 2019 et sous Larde à partir de 2021. Les graphies fluctuent (`Micaune`/`Micaúne`,
  `Ilmenite`/`Iimenite`). Les noms sont reproduits tels que publiés, sans normalisation.
- **Les valeurs sont en millions de MZN** dans `transfers.csv` et en meticais entiers
  dans `projects.csv`, conformément à leurs sources respectives.

## Sources

- [Page Mozambique de l'ITIE](https://eiti.org/countries/mozambique) — rapports et annexes
- Annexe 6.1, Transferts aux communautés (rapport 2023–2024)
- Tableaux 42, 45 et 46 des rapports 2020, 2022 et 2021
- [Centro de Integridade Pública](https://www.cipmoz.org/) — analyse indépendante des 2,75 %

## Langues

Le code et les identifiants sont en anglais. Le contenu destiné aux utilisateurs est en
anglais, portugais et français. Le portugais est la langue des documents sources et de
l'État mozambicain ; une édition en langue locale (l'emakhuwa est parlé à Montepuez,
Balama, Ancuabe, Topuito et Moma — les localités les mieux dotées) exige un locuteur
natif et n'est pas traduite automatiquement ici.

## Licence

Code : MIT. Les données sous-jacentes sont publiées par l'ITIE Mozambique et sont publiques.
