# Travaux dirigés - Marcu-Andria Battesti

Dépôt des TD des deux modules. Vous y prenez les énoncés et les fichiers dont vous
avez besoin en séance ; le cours lui-même (slides, PDF) est sur
<https://cours.battesti.app>.

## Comment ce dépôt est organisé

**Une branche par chapitre.** Il n'y a pas de dossier `chapitre-1/`, `chapitre-2/` :
le matériel d'un chapitre vit sur sa propre branche, nommée `tp/<ue>-<chapitre>`, par
exemple `tp/ue1-01-systemes-distribues-cap`. Vous n'avez donc jamais sous les yeux que
le chapitre en cours, aux mêmes chemins d'une séance à l'autre.

```
master                              cette page, rien d'autre
├── tp/ue0-01-environnement-python  ┐
├── tp/ue0-02-…                     │ une branche par chapitre,
├── tp/ue1-01-…                     │ indépendantes les unes des autres
└── …                               ┘
```

À la racine d'une branche de chapitre :

| Fichier | Ce que c'est |
| --- | --- |
| `README.md` | le chapitre, et ce que contient la branche |
| `td-enonces.md` | l'énoncé des TD de la séance |
| `travail-perso.md` | le travail personnel à rendre |
| `manip/` | les fichiers de la séance sur machine (`docker-compose.yml`, scripts…) |

Tout n'est pas présent partout : un chapitre sans machine n'a pas de `manip/`, et une
branche dont la séance n'a pas encore eu lieu ne porte que son README - le matériel y
est poussé avant le cours.

**Les corrigés ne sont sur aucune branche de ce dépôt.** Ils sont publiés, quand ils le
sont, sur le site du cours.

## Prendre un TD

```bash
git clone https://github.com/MarcanBat2a/cours_td_public.git
cd cours_td_public
git switch tp/ue1-01-systemes-distribues-cap   # la branche du chapitre voulu
```

Pour la séance suivante, ou pour récupérer un énoncé qui vient d'être publié :

```bash
git fetch origin
git switch tp/ue1-02-orientees-documents
```

`git branch -r` donne la liste complète des branches disponibles.

## Travailler sans rien perdre

Ces branches sont des branches de **distribution** : elles sont réécrites et republiées
telles quelles à chaque mise à jour du matériel. Un commit que vous feriez dessus serait
écrasé à la mise à jour suivante.

Vos réponses et votre code vont donc sur une branche à vous, dérivée de celle du
chapitre :

```bash
git switch tp/ue1-01-systemes-distribues-cap
git switch -c moi/ue1-01        # votre branche de travail, locale
```

Et vous ne poussez rien ici : le dépôt est en lecture seule pour vous, les rendus se
font par le canal indiqué en séance.

## Les branches

### UE 0 - Algo 3 avec Python

| Chapitre | Branche |
| --- | --- |
| 1. Introduction à l'environnement Python | [`tp/ue0-01-environnement-python`](https://github.com/MarcanBat2a/cours_td_public/tree/tp/ue0-01-environnement-python) |
| 2. Rappel des structures algorithmiques | [`tp/ue0-02-structures-algorithmiques`](https://github.com/MarcanBat2a/cours_td_public/tree/tp/ue0-02-structures-algorithmiques) |
| 3. Complexité | [`tp/ue0-03-complexite`](https://github.com/MarcanBat2a/cours_td_public/tree/tp/ue0-03-complexite) |
| 4. Graphes | [`tp/ue0-04-graphes`](https://github.com/MarcanBat2a/cours_td_public/tree/tp/ue0-04-graphes) |

### UE 1 - Persistance & Systèmes Distribués (NoSQL)

| Chapitre | Branche |
| --- | --- |
| 1. Introduction aux systèmes distribués et théorème CAP | [`tp/ue1-01-systemes-distribues-cap`](https://github.com/MarcanBat2a/cours_td_public/tree/tp/ue1-01-systemes-distribues-cap) |
| 2. Bases de données orientées documents | [`tp/ue1-02-orientees-documents`](https://github.com/MarcanBat2a/cours_td_public/tree/tp/ue1-02-orientees-documents) |
| 3. Magasins Clé-Valeur et cache distribué | [`tp/ue1-03-cle-valeur-cache`](https://github.com/MarcanBat2a/cours_td_public/tree/tp/ue1-03-cle-valeur-cache) |
| 4. Bases orientées Graphes ou Colonnes | [`tp/ue1-04-graphes-colonnes`](https://github.com/MarcanBat2a/cours_td_public/tree/tp/ue1-04-graphes-colonnes) |
| 5. Stratégies de distribution | [`tp/ue1-05-distribution`](https://github.com/MarcanBat2a/cours_td_public/tree/tp/ue1-05-distribution) |

Une question sur un énoncé se pose en séance ou par le canal habituel du module.
