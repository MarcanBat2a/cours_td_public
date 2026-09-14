# TD - Le donjon

**UE 0 - Algo 3 avec Python · Chapitre 2 · variante facultative « jeu »**
Marcu-Andria Battesti · Bachelor CLIC · 2026-2027

> Une autre mise en situation des TD : une compagnie de 24 aventuriers,
> des cartes et un gardien. À choisir **à la place** du parcours communes,
> sans ajouter neuf TD à la séance. Les objectifs et les traces de
> [la fiche principale](td-enonces.md) restent la référence.
>
> Copier le **contenu** de `manip/donjon/` dans `algo3/chapitre2/donjon/`.
> Le jeu `python donjon.py` appelle les fonctions écrites par l'étudiant.
> Une fonction absente laisse une porte fermée. Le labyrinthe final est
> facultatif et prépare le chapitre 4 ; finir les treize portes n'est pas
> un objectif obligatoire de séance.
>
> Les compteurs préparent le chapitre 3. Les formules, les grandes tailles,
> la puissance rapide et la mémoïsation seront étudiées dans ce chapitre.

Les définitions et les exemples guidés du [cours](cours.md) servent aussi
à cette variante. Pour la démonstration de la factorielle, copiez également
`manip/trace_factorielle.py` à côté de vos fichiers.

---

# Séance 1 - Boucles et conditions

# TD 1 - L'entrée du donjon

**Sur machine** · dans `entree.py`

Les scores de la dernière partie : `scores = [12, 47, 3, 91, 25]`.

## Étape 0 - Le REPL

```python
scores = [12, 47, 3, 91, 25]
scores[-2]
scores[2:]
scores[:2]
scores.append(7)
91 in scores
```

1. Notez les cinq réponses. La règle de `t[a:b]`, en une phrase.

## Étape 1 - Le sort du magicien

Le magicien lance un sort sur un nombre : s'il est pair, il le divise par
deux ; s'il est impair, il le triple et ajoute un. Le sort s'arrête
quand le nombre vaut 1.

1. `etapes(n)` : le nombre de coups de sort pour arriver à 1.
   `etapes(27)` ?
2. Quel nombre inférieur à 100 résiste le plus longtemps ? Combien de
   coups ?
3. Combien de nombres inférieurs à 100 demandent plus de 100 coups ?

## Étape 2 - Le meilleur score

`scores = [12, 47, 3, 91, 25, 68, 91, 7]`

1. `maximum(scores)` reçoit une liste **non vide** et renvoie le meilleur
   score **et sa première position**, sans `max()` ni `index()`.
2. ★ 91 est présent deux fois. Votre fonction renvoie quelle position ?
   Quel caractère changer pour obtenir l'autre ?

## Étape 3 - Rejouer à l'envers

1. `inverser(t)` retourne la liste **sur place**, en échangeant les
   éléments deux à deux depuis les bouts. Un échange tient en une ligne.
2. Affichez la partie `[1, 2, 3, 4, 5, 6, 7]` rejouée à l'envers, sur une
   ligne, séparée par des espaces : `" ".join(...)`.
3. Trouvez `t[::-1]` dans le REPL. Votre programme tient-il en deux
   lignes ?
4. ★ Ce que Python a rendu inutile ici par rapport au C - et ce qui est
   obligatoire en Python et n'existait pas en C.

> `python donjon.py` : les deux portes de la salle 1 doivent s'ouvrir.

---

# TD 2 - La compagnie

**Sur machine** · dans `compagnie.py`

## Étape 0 - Lire les données

```python
from aventuriers import AVENTURIERS
len(AVENTURIERS)
AVENTURIERS[0]
AVENTURIERS[-1]["pv"]
```

1. Qu'est-ce que `AVENTURIERS` ? `AVENTURIERS[0]` ? L'or du troisième
   aventurier ?

## Étape 1 - Compter, filtrer

1. Chaque aventurier, un par ligne : nom, guilde, niveau.
2. Le nombre d'aventuriers au-dessus du niveau 5. Pronostic, puis
   mesure.
3. Les noms de ceux qui ont plus de 1 000 pièces d'or. Combien ?
4. L'or de toute la compagnie, puis la moyenne des points de vie.

## Étape 2 - Le plus riche, sans max()

1. `plus_riche(aventuriers)` renvoie l'aventurier entier. Combien de
   lignes ?
2. ★ Le plus rentable : le plus d'or **par niveau**. Qu'est-ce qui change
   par rapport à la question 1 ?
3. Le moins rentable. Notez les deux noms et les deux valeurs.

## Étape 3 - S'arrêter

1. Le premier aventurier de la liste qui a moins de 10 points de vie,
   puis `break`. Son indice ? Il faut le soigner d'abord.
2. Ceux qui ont moins de 20 points de vie, avec `continue`, puis sans.
   Laquelle des deux versions gardez-vous ?
3. ★ Une seule boucle de ce TD a besoin d'un indice : laquelle, et
   pourquoi celle-là ?

---

# TD 3 - Les guildes

**Sur machine** · dans `guildes.py`, testé dans le REPL

## Étape 1 - Des fonctions

1. `rentabilite(aventurier)` : l'or divisé par le niveau, avec une
   docstring.
2. `extremes_niveau(aventuriers)` : renvoie deux valeurs, le plus bas
   niveau et le plus haut.
3. `au_dessus(aventuriers, seuil=5)` : la liste des noms au-dessus du
   seuil, en une ligne. Appelez `au_dessus(AVENTURIERS)`, puis `au_dessus(AVENTURIERS, 9)`.

## Étape 2 - Regrouper

```python
totaux = {}
for a in AVENTURIERS:
    totaux[a["guilde"]] = totaux.get(a["guilde"], 0) + a["or"]
```

1. Que fait `get(..., 0)` la première fois qu'une guilde apparaît ? Les
   suivantes ? Quelle guilde est la plus riche, laquelle la moins ?
2. Le nombre d'aventuriers par guilde. Qu'est-ce qui change ?
3. ★ Le plus haut niveau de chaque guilde : un dictionnaire dont les
   valeurs sont des aventuriers. Écrivez la condition qui décide si on
   remplace. Les quatre noms.
4. `par_guilde(aventuriers)` renvoie le dictionnaire de la question 1 ;
   affichez-le avec `.items()`.

## Étape 3 - Le registre

```python
import csv
with open("aventuriers.csv", newline="") as f:
    lignes = list(csv.DictReader(f))
lignes[0]
```

1. Comparez `lignes[0]` à `AVENTURIERS[0]`. Qu'est-ce qui diffère ?
2. L'or total depuis `lignes`. Recopiez l'erreur, corrigez-la.
3. ★ `charger(chemin)` renvoie une liste du même type que `AVENTURIERS`.
   `charger("aventuriers.csv") == AVENTURIERS` doit répondre `True`.
   Pourquoi la conversion est-elle à votre charge et pas à celle de
   `csv` ?

## Étape 4 - Relire

1. Réécrivez les questions 1.2 et 1.3 du TD 2 en compréhensions.

> `python donjon.py` : cinq portes ouvertes en fin de séance 1.

---

# Séance 2 - Les tris

# TD 4 - Le tableau des scores

**Sur machine** · dans `scores.py`

## Étape 1 - Une clé

1. Les cinq aventuriers les plus riches : `classement(aventuriers)`
   renvoie la compagnie triée par or décroissant ; affichez les cinq
   premiers.
2. Les trois plus mal en point (points de vie).
3. Les noms par ordre alphabétique. La clé est-elle nécessaire ?
4. ★ Par longueur de nom. Deux noms de même longueur : dans quel ordre
   sortent-ils, et pourquoi celui-là ?

## Étape 2 - Deux critères

1. Par guilde, puis or décroissant dans chaque guilde. Un tuple en clé,
   sans `reverse`.
2. Niveau croissant et guilde décroissante. Où le `-` ne marche-t-il
   plus ? Trouvez une autre façon.

## Étape 3 - Ce qu'un tri laisse au suivant ★

```python
etape1 = sorted(AVENTURIERS, key=lambda a: a["or"], reverse=True)
etape2 = sorted(etape1, key=lambda a: a["guilde"])
```

1. Affichez `etape2`. Dans chaque guilde, dans quel ordre sont les
   aventuriers ? D'où vient cet ordre ?
2. ★ `sorted` est **stable**. Définissez-le avec le mot « ex æquo ».
   Corvin et Quitterie ont le même or : qui sort en premier, et
   pourquoi ? En quoi la stabilité rend le tuple de 2.1 inutile - et
   pourquoi on le préfère quand même ?

## Étape 4 - En place

1. `t = [3, 1, 2]` ; `t.sort()` renvoie quoi ? `t` vaut quoi ? Quand
   `sort`, quand `sorted` ?

---

# TD 5 - La main de cartes

**Sur machine** · dans `tris.py`

Vous tenez sept cartes : `main = [7, 12, 3, 9, 1, 11, 4]`. Les deux
façons de ranger une main sont les deux premiers tris de ce TD. Chaque
tri prend une liste de nombres et renvoie `triee, comparaisons`, sans
modifier l'entrée. Le compteur est un entier positif ou nul ; il vaut
zéro pour une liste vide ou un singleton.

## Étape 1 - La sélection

Le geste : chercher la plus petite carte de ce qui reste, la mettre à
gauche, recommencer avec le reste.

1. L'invariant, avant le code : après le tour `i`, que dire de
   `t[:i+1]` ? Deux choses.
2. `tri_selection(t)`. Commencez par `t = list(t)`. Comptez chaque
   `t[j] < t[mini]`.
3. Sur `main` : pronostic puis mesure, combien de comparaisons pour sept
   cartes ? Vérifiez contre `sorted(main)`.
4. ★ Tracez un tour sur une main déjà triée et sur une main inversée.
   Expliquez quelles cartes sont définitivement placées.

## Étape 2 - L'insertion

Le geste : prendre la carte suivante, la glisser vers la gauche tant que
sa voisine est plus grande.

1. L'invariant. En quoi diffère-t-il de la sélection ?
2. `tri_insertion(t)`. Comptez chaque `t[j] > x`.
3. Pronostic puis mesure sur `main`, `sorted(main)`,
   `sorted(main, reverse=True)`.
4. ★ Expliquez le plus petit et le plus grand des trois. Lequel des deux
   tris pour une main presque rangée ?

## Étape 3 - Vérifier ★

Vérifiez les deux tris sur les valeurs d'or de la compagnie, puis sur
`[]`, `[7]`, `[2, 2, 1]` et `[-3, 0, -8]`. Résultat égal à `sorted`,
doublons conservés et entrée inchangée : mêmes critères que le TD 5
principal. Gardez les compteurs, sans chercher de formule ici.

## Étape 4 - Bonus : les bulles

Parcourir les cartes voisines de gauche à droite et échanger celles qui
sont mal rangées. Après un passage, le maximum restant est au bout ; le
passage suivant s'arrête une case plus tôt. Tester sur les mêmes entrées.

---

# TD 6 - Le gardien

**Sur machine** · dans `recherche.py`

Le gardien de la salle 6 a caché la clé dans une des 1 000 salles du
donjon. Il répond à chaque question « plus haut », « plus bas » ou
« trouvé », et il compte les questions.

## Étape 1 - Linéaire

```python
niveaux = sorted(a["niveau"] for a in AVENTURIERS)
```

1. `recherche_lineaire(t, x)` : l'indice ou `-1`, et le nombre de cases
   regardées. Testez `9`, `1`, `12`, `13`.

## Étape 2 - Dichotomique

Deux bornes `g` et `d`, le milieu `m = (g + d) // 2` ; trop petit,
`g = m + 1` ; trop grand, `d = m - 1` ; on s'arrête quand `g > d`.

1. L'invariant : si `x` est dans `t`, où est-il à chaque tour ?
2. `recherche_dichotomique(t, x)`, avec le compteur de regards. Les
   quatre mêmes valeurs.
3. ★ Tracez les bornes sur une petite liste. Pourquoi exclure le milieu
   testé de la prochaine zone ? Testez aussi une liste vide et un singleton.

## Étape 3 - Contre le gardien

```python
from gardien import question, questions_posees, nouvelle_partie
question(500)
questions_posees()
```

1. La stratégie naïve : 1, 2, 3... jusqu'à « trouvé ». Combien de
   questions ? `nouvelle_partie()` avant de recommencer.
2. `deviner(question)` reçoit la fonction du gardien et renvoie la salle
   de la clé, en posant le moins de questions possible. Pronostic, puis
   `questions_posees()`.
3. Lancez cinq parties et vérifiez que la clé est trouvée. Le jeu fixe
   un défi facultatif de dix questions ; sa justification viendra au chapitre 3.

## Étape 4 - La liste qui n'est pas triée ★

```python
ors = [a["or"] for a in AVENTURIERS]
```

1. `recherche_dichotomique(ors, 1310)` - 1310 est dans la liste. Que
   répond-elle ? Et la linéaire ? Et `recherche_dichotomique(ors, 20)` ?
2. ★ Écrivez la précondition : la liste doit être triée. Sinon le
   résultat n’est pas garanti. Vérifiez les éléments voisins avant une série
   de recherches ; le coût de la vérification vient au chapitre 3.

## Étape 5 - Python le sait

1. `bisect.bisect_left(niveaux, 9)`, puis `bisect_left(niveaux, 13)`. À
   quoi sert le second nombre ? Pour vérifier la présence de `x`,
   testez `i < len(niveaux) and niveaux[i] == x` après la dichotomie.

> `python donjon.py` : dix portes ouvertes en fin de séance 2.

---

# Séance 3 - La récursivité

# TD 7 - L'escalier

**Sur papier, puis sur machine** · dans `recursif.py`

Reprenez les quatre étapes du [TD 7 principal](td-enonces.md#td-7-le-cas-de-base-et-les-retours) :
trace de factorielle, somme et puissance naïve, pile, petit arbre de Fibonacci.
Écrivez les entrées autorisées, le résultat, le cas de base et la progression.

- `factorielle(n)` compte les façons de ranger n aventuriers. `21!`
  dépasse un entier signé de 64 bits ; `20!` y tient.
- `somme(t)` additionne l'or des coffres ; tester une liste vide.
- `puissance(x, n)` répète le même sort, pour un entier `n >= 0`.
- `fib(4)` : tracer chaque appel et chaque retour. Remettre le compteur
  à zéro avant `fib(5)` : résultat et nombre d'appels sont distincts.

La salle 7 vérifie `fib(5)`. La mémoïsation et la puissance rapide
appartiennent au chapitre 3 ; elles ne sont pas nécessaires pour ouvrir cette porte.

---

# TD 8 - Le tournoi

**Sur machine** · dans `tris.py` du TD 5

Deux files d'aventuriers déjà classées arrivent au tournoi ; il faut une
seule file classée.

## Étape 1 - Fusionner

Même contrat que le TD 8 principal : `fusion(g, d)` a **deux arguments**,
renvoie une nouvelle liste triée et incrémente une globale `comparaisons`.
Remettre le compteur à zéro avant chaque mesure. Tester une liste vide,
des doublons et la recopie du reste.

## Étape 2 - Trier

`tri_fusion(t)` renvoie **seulement la liste triée** ; son compteur se lit
après l'appel. Cas de base : **zéro ou un élément**. Couper, trier les
moitiés, fusionner. Vérifier le résultat et la conservation de l'entrée.

## Étape 3 - Tracer ★

Tracer appels et retours sur `[4, 1, 3, 2]`, puis les deux cas de base.
Les tableaux de grandes tailles sont construits au chapitre 3, sur une
même série de données pour les différents tris.

---

# TD 9 - Tracer et vérifier

Faire le [TD 9 principal](td-enonces.md#td-9-tracer-et-vérifier), sur papier,
puis vérifier les réponses sur machine. L'exploration suivante est facultative.

---

# Bonus - Le labyrinthe

**Facultatif, sur machine et sur papier** · dans `labyrinthe.py`

`#` un mur, `.` une salle libre, `D` le départ. Une salle est
**atteignable** si on peut y aller depuis `D` en passant de salle en
salle, par le haut, le bas, la gauche ou la droite.

## Partie A - L'exemple, sur papier

`exemple.txt` :

```text
#######
#D.#..#
#.##.##
#...#.#
#######
```

La fonction qu'on va écrire :

```python
def explorer(grille, i, j):
    if grille[i][j] == "#" or grille[i][j] == "o":   # mur, ou déjà vue
        return
    grille[i][j] = "o"                                # on marque
    explorer(grille, i - 1, j)                        # haut
    explorer(grille, i + 1, j)                        # bas
    explorer(grille, i, j - 1)                        # gauche
    explorer(grille, i, j + 1)                        # droite
```

Les seize premiers appels de `explorer(grille, 1, 1)`, un par ligne,
indentés selon la profondeur :

```text
 1 explorer(1, 1)  'D'  → marquée
 2   explorer(0, 1)  '#'  → mur, retour
 3   explorer(2, 1)  '.'  → marquée
 4     explorer(1, 1)  'o'  → déjà vue, retour
 5     explorer(3, 1)  '.'  → marquée
 6       explorer(2, 1)  'o'  → déjà vue, retour
 7       explorer(4, 1)  '#'  → mur, retour
 8       explorer(3, 0)  '#'  → mur, retour
 9       explorer(3, 2)  '.'  → marquée
10         explorer(2, 2)  '#'  → mur, retour
11         explorer(4, 2)  '#'  → mur, retour
12         explorer(3, 1)  'o'  → déjà vue, retour
13         explorer(3, 3)  '.'  → marquée
14           explorer(2, 3)  '#'  → mur, retour
15           explorer(4, 3)  '#'  → mur, retour
16           explorer(3, 2)  'o'  → déjà vue, retour
```

1. La grille après l'appel 13 : dessinez-la, avec les `o`.
2. ★ Continuez la trace jusqu'au dernier appel. Combien d'appels en
   tout ? Combien de salles marquées ? Lesquelles ne le sont pas, et
   pourquoi ?
3. ★ À l'appel 4, `explorer(1, 1)` revient sur la case de départ.
   Retirez « déjà vue » de la condition d'arrêt : que se passe-t-il à
   partir de cet appel ?
4. Pourquoi n'a-t-on jamais besoin de vérifier qu'on sort de la grille ?

## Partie B - Le vrai labyrinthe, sur machine

```python
grille = [list(ligne) for ligne in open("labyrinthe.txt").read().splitlines()]
```

1. Lignes, colonnes, position de `D`, nombre de salles libres.
2. Recopiez `explorer`, lancez-la depuis `D`, affichez la grille avec les
   salles atteintes en `o`. Vérifiez d'abord sur `exemple.txt` : votre
   grille doit être celle de la question A.2.
3. Pronostic puis mesure : combien de salles atteignables ? Lesquelles
   ne le sont pas ?
4. ★ Retirez « déjà vue » de la condition d'arrêt. Recopiez ce qui se
   passe, expliquez avec les mots du TD 7.
5. `compter_cases(grille, i, j)` renvoie le **nombre** de salles
   atteignables depuis `(i, j)`. Le cas de base renvoie quoi ? L'appel
   additionne quoi ? Rechargez une grille intacte avant chaque appel. Testez sur l’exemple,
   puis sur le labyrinthe.

## Partie C - Sur papier ★

1. Tracez `puissance(2, 3)`, version naïve : un appel par ligne,
   indenté selon la profondeur, ses arguments, sa valeur de retour.
   Combien d'appels ?
2. ★ Tracez `fusion([3, 8], [1, 9])` : à chaque comparaison, les deux
   têtes et l'élément ajouté. Combien de comparaisons ?
3. ★ Tracez `compter_cases` sur l'exemple, depuis `(3, 3)` : la valeur
   renvoyée par chaque appel.

> `python donjon.py` : treize portes. Gardez `tris.py` et `recursif.py`
> pour le chapitre 3.
