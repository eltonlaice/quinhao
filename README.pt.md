# Quinhão

[English](README.md) · **Português** · [Français](README.fr.md)

> *Quinhão*: a parte que cabe a alguém por direito.

A lei moçambicana destina **2,75%** do imposto sobre a produção mineira e petrolífera às
comunidades onde se localizam esses empreendimentos. O dinheiro é transferido. O que
ninguém consegue dizer é **porque é que a tua comunidade recebeu aquele valor**, nem
**o que foi feito com ele**.

Não é acusação — é a constatação do próprio organismo de transparência. Do relatório do
ITIE Moçambique:

> "o REOE não permite aferir qual foi o critério utilizado para repartir o valor a alocar
> para cada comunidade e para quais actividades os fundos foram alocados"

O Quinhão transforma seis anos dessas transferências em algo que uma pessoa em
Nyamanhumbir ou em Benga consegue ler, comparar e questionar.

## O que este repositório contém hoje

Uma pipeline de dados verificada. A aplicação ainda não está construída.

| Ficheiro | Conteúdo |
|---|---|
| `src/extract.py` | Descarrega os PDF de origem do eiti.org e analisa-os |
| `data/transfers.csv` | 129 linhas — dotação vs. realização por localidade, 2019/2021/2023/2024 |
| `data/projects.csv` | 41 linhas — projectos financiados com valores, 2022 (**rascunho**, ver ressalvas) |

### A série de seis anos

| Ano | Fonte | Granularidade | Total (milhões MZN) |
|---|---|---|---|
| 2019 | Relatório ITIE 2020, Tabela 42 | localidade | 88,0 dotado / 87,8 realizado |
| 2021 | Relatório ITIE 2021, Tabela 46 | localidade | 73,4 |
| 2022 | Relatório ITIE 2022, Tabela 45 | **projecto individual** | 44,6 |
| 2023 | Relatório ITIE 2023–2024, Anexo 6.1 | localidade + mineral | 77,1 |
| 2024 | Relatório ITIE 2023–2024, Anexo 6.1 | localidade + mineral | 318,7 |

Todos os valores remontam a um PDF público do [eiti.org](https://eiti.org/countries/mozambique).
Nenhum número deste repositório foi escrito à mão.

## Como executar

Requer Python 3.9+ e `pdftotext` (poppler). Não há pacotes Python a instalar.

```bash
brew install poppler           # macOS
sudo apt install poppler-utils # Debian/Ubuntu
```

```bash
python3 src/extract.py
```

Na primeira execução o script descarrega ~25 MB de PDF para `data/raw/`, guarda-os em
cache e regenera os dois CSV. Termina com uma auto-verificação que confirma que o total
calculado de cada ano é igual ao total publicado — **se um parser se desviar, a execução
falha em voz alta** em vez de escrever números errados.

## Ressalvas sobre os dados

Lê isto antes de usar os dados. É o essencial, não o rodapé.

- **O `projects.csv` (2022) é um rascunho.** Os valores são fiáveis — somam exactamente
  o total publicado de 44.608.666,89 MZN. Os rótulos de província/distrito/comunidade e
  as descrições dos projectos **não são**: o PDF de origem funde essas células
  verticalmente e parte as descrições acima e abaixo do próprio valor. Todas as linhas
  levam `needs_review=yes` até alguém conferir as 41 linhas à mão contra o PDF.
- **Dotação não é entrega.** Tanto os anexos como os relatórios indicam realização a
  ~100% da dotação. Isso significa que o dinheiro saiu do tesouro, não que algo foi
  construído. A verificação no terreno é a camada em falta.
- **Desfasamento de dois anos.** Os fundos libertados num ano baseiam-se em receitas
  cobradas dois anos antes (n−2). A dotação de 2021 reflecte receitas de 2019.
- **Os 2,75% não incidem sobre toda a base tributária.** O relatório de 2020 mostra que
  2,75% do imposto de produção de 2018 dariam 100,59 milhões de MZN; foram alocados 87,8
  milhões — uma diferença de 12,79 milhões. A explicação do Ministério é que só conta o
  imposto sobre a produção *mineira*, não o petrolífero.
- **Os nomes das localidades variam entre anos.** Topuito aparece em Moma em 2019 e em
  Larde a partir de 2021. As grafias oscilam (`Micaune`/`Micaúne`, `Ilmenite`/`Iimenite`).
  Os nomes são reproduzidos como publicados, sem normalização.
- **Os valores estão em milhões de MZN** no `transfers.csv` e em meticais inteiros no
  `projects.csv`, conforme as respectivas fontes.

## Fontes

- [Página de Moçambique no ITIE](https://eiti.org/countries/mozambique) — relatórios e anexos
- Anexo 6.1, Transferências às Comunidades (relatório 2023–2024)
- Tabelas 42, 45 e 46 dos relatórios de 2020, 2022 e 2021
- [Centro de Integridade Pública](https://www.cipmoz.org/) — análise independente dos 2,75%

## Contexto

Construído para o hackathon Open Society Foundations × Andela, *Information You Can
Trust*, track de **Transparência e Responsabilização**.

O código e os identificadores estão em inglês. O conteúdo para o utilizador está em
inglês, português e francês. O português é a língua dos documentos de origem e do Estado
moçambicano; uma edição em língua local (o emakhuwa é falado em Montepuez, Balama,
Ancuabe, Topuito e Moma — as localidades que mais recebem) exige um falante nativo e não
é aqui traduzida por máquina.

## Licença

Código: MIT. Os dados subjacentes são publicados pelo ITIE Moçambique e são públicos.
