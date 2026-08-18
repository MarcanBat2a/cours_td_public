# Travaux dirigés - Marcu-Andria Battesti

Dépôt public des TD. **Une branche par chapitre** : le matériel d'un chapitre
(énoncé, travail personnel, fichiers de manipulation) vit sur sa propre branche,
et `master` ne contient que cette page.

Les corrigés ne sont sur aucune branche de ce dépôt.

## Récupérer un TD

```bash
git clone https://github.com/MarcanBat2a/cours_td_public.git
cd cours_td_public
git switch tp/ue1-01-systemes-distribues-cap   # la branche du chapitre voulu
```

Pour passer d'un chapitre à l'autre : `git fetch origin` puis
`git switch <branche>`. `git branch -r` en donne la liste complète.

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

Une branche dont le chapitre n'a pas encore eu lieu ne porte que son README :
le matériel y est poussé avant la séance.
