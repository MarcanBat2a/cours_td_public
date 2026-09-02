# TD - Rappel des structures algorithmiques

**UE 0 - Algo 3 avec Python · Chapitre 2**
Marcu-Andria Battesti · Bachelor CLIC · 2026-2027

> Neuf travaux dirigés sur trois séances, tous sur machine. Gardez vos
> fichiers : les tris et leurs compteurs resservent au chapitre 3.
>
> On travaille dans `algo3/` (chapitre 1), venv activé, dans un dossier
> `chapitre2/` où `manip/` est copié. Le REPL pour une ligne, un fichier
> `.py` dès trois lignes. En binôme, un terminal chacun.
>
> **Le pronostic avant la mesure** : quand la fiche demande un chiffre,
> écrivez-le avant de lancer.
>
> **★** : les questions dont la réponse doit tenir en une phrase juste ou
> un tracé propre - celles que l'évaluation peut reprendre.
>
> Le jeu de données : `manip/communes.py`, 24 communes imaginaires, quatre
> cantons - `from communes import COMMUNES`.

---

# Séance 1

# TD 1 - Prise en main

**40 minutes · en binôme · sur machine**

## Étape 0 - Le REPL *(6 min)*

```python
t = [12, 47, 3, 91, 25]
t[-2]
t[2:]
t[:2]
t.append(7)
91 in t
```

1. Notez les trois réponses. La règle de `t[a:b]`, en une phrase.

## Étape 1 - Collatz *(12 min)*

Suite de Collatz : si `n` est pair, `n / 2` ; sinon `3n + 1` ; on
s'arrête à 1.

1. `etapes(n)` : le nombre d'étapes pour atteindre 1. `etapes(27)` ?
2. Quel `n` inférieur à 100 demande le plus d'étapes ? Combien ?
3. Combien de `n` inférieurs à 100 demandent plus de 100 étapes ?

## Étape 2 - Le maximum *(10 min)*

`valeurs = [12, 47, 3, 91, 25, 68, 91, 7]`

1. `maximum(valeurs)` renvoie le plus grand élément **et** sa position,
   sans `max()` ni `index()`.
2. ★ 91 est présent deux fois. Votre fonction renvoie quelle position ?
   Quel caractère changer pour obtenir l'autre ?

## Étape 3 - À l'envers *(12 min)*

1. `inverser(t)` retourne la liste **sur place**, en échangeant les
   éléments deux à deux depuis les bouts. Un échange tient en une ligne.
2. Affichez `[1, 2, 3, 4, 5, 6, 7]` inversée, sur une ligne, séparée par
   des espaces : `" ".join(...)`.
3. Trouvez `t[::-1]` dans le REPL. Votre programme tient-il en deux
   lignes ?
4. ★ Ce que Python a rendu inutile ici par rapport au C - et ce qui est
   obligatoire en Python et n'existait pas en C.

---

# TD 2 - Parcourir les communes

**42 minutes · en binôme · sur machine**

## Étape 0 - Lire les données *(4 min)*

```python
from communes import COMMUNES
len(COMMUNES)
COMMUNES[0]
COMMUNES[-1]["altitude"]
```

1. Qu'est-ce que `COMMUNES` ? `COMMUNES[0]` ? La population de la
   troisième commune ?

## Étape 1 - Compter, filtrer *(12 min)*

Dans `parcours.py` :

1. Chaque commune, une par ligne, nom et population.
2. Le nombre de communes au-dessus de 500 m. Pronostic, puis mesure.
3. Les noms des communes de plus de 1 000 habitants. Combien ?
4. La population totale, puis l'altitude moyenne.

## Étape 2 - Le maximum, sans max() *(12 min)*

1. La commune la plus peuplée. Combien de lignes ?
2. ★ La plus dense (habitants par km²). Qu'est-ce qui change par rapport
   à la question 1 ?
3. La moins dense. Notez les deux noms et les deux valeurs.

## Étape 3 - S'arrêter *(10 min)*

1. La première commune de la liste au-dessus de 900 m, puis `break`.
   Son indice ?
2. Les communes de moins de 100 habitants, avec `continue`, puis sans.
   Laquelle gardez-vous ?
3. ★ Une seule boucle de ce TD a besoin d'un indice : laquelle, et
   pourquoi celle-là ?

---

# TD 3 - Les cantons

**46 minutes · en binôme · sur machine**

## Étape 1 - Des fonctions *(12 min)*

Dans `cantons.py`, testées dans le REPL :

1. `densite(commune)`, avec une docstring.
2. `plus_peuplee(communes)` : renvoie la commune entière, sans `max()`.
3. `extremes_altitude(communes)` : renvoie deux valeurs, la plus basse
   et la plus haute.
4. `au_dessus(communes, seuil=500)` : la liste des noms, en une ligne.
   Appelez-la sans argument, puis avec `900`.

## Étape 2 - Regrouper *(14 min)*

```python
totaux = {}
for c in COMMUNES:
    totaux[c["canton"]] = totaux.get(c["canton"], 0) + c["population"]
```

1. Que fait `get(..., 0)` la première fois qu'un canton apparaît ? Les
   suivantes ? Quel canton est le plus peuplé, lequel le moins ?
2. Le nombre de communes par canton. Qu'est-ce qui change ?
3. ★ La commune la plus haute de chaque canton : un dictionnaire dont les
   valeurs sont des communes. Écrivez la condition qui décide si on
   remplace. Les quatre noms.
4. `par_canton(communes)` renvoie le dictionnaire de la question 1 ;
   affichez-le avec `.items()`.

## Étape 3 - Depuis un fichier *(14 min)*

```python
import csv
with open("communes.csv", newline="") as f:
    lignes = list(csv.DictReader(f))
lignes[0]
```

1. Comparez `lignes[0]` à `COMMUNES[0]`. Qu'est-ce qui diffère ?
2. La population totale depuis `lignes`. Recopiez l'erreur, corrigez-la.
3. ★ `charger(chemin)` renvoie une liste du même type que `COMMUNES`.
   `charger("communes.csv") == COMMUNES` doit répondre `True`. Pourquoi
   la conversion est-elle à votre charge et pas à celle de `csv` ?

## Étape 4 - Relire *(6 min)*

1. Réécrivez les questions 1.2 et 1.3 du TD 2 en compréhensions.

> Gardez `cantons.py` : `charger` sert aux chapitres 3 et 4.

---

# Séance 2

# TD 4 - Trier les communes

**36 minutes · en binôme · sur machine**

Dans `tris_python.py`.

## Étape 1 - Une clé *(10 min)*

1. Les cinq communes les plus peuplées.
2. Les trois plus basses.
3. Les noms par ordre alphabétique. La clé est-elle nécessaire ?
4. ★ Par longueur de nom. Deux noms de même longueur : dans quel ordre
   sortent-ils, et pourquoi celui-là ?

## Étape 2 - Deux critères *(10 min)*

1. Par canton, puis population décroissante dans chaque canton. Un
   tuple en clé, sans `reverse`.
2. Population croissante et canton décroissant. Où le `-` ne marche-t-il
   plus ? Trouvez une autre façon.

## Étape 3 - Ce qu'un tri laisse au suivant ★ *(12 min)*

```python
etape1 = sorted(COMMUNES, key=lambda c: c["population"], reverse=True)
etape2 = sorted(etape1, key=lambda c: c["canton"])
```

1. Affichez `etape2`. Dans chaque canton, dans quel ordre sont les
   communes ? D'où vient cet ordre ?
2. ★ `sorted` est **stable**. Définissez-le avec le mot « ex æquo ». En
   quoi ça rend le tuple de 2.1 inutile - et pourquoi on le préfère
   quand même ?

## Étape 4 - En place *(4 min)*

1. `t = [3, 1, 2]` ; `t.sort()` renvoie quoi ? `t` vaut quoi ? Quand
   `sort`, quand `sorted` ?

---

# TD 5 - Trois tris, un compteur

**50 minutes · en binôme · sur machine**

Dans `tris.py`. Chaque tri prend une liste de nombres et renvoie
`triee, comparaisons`. Les données :

```python
from communes import COMMUNES
pops = [c["population"] for c in COMMUNES]
```

## Étape 1 - La sélection *(14 min)*

À chaque tour `i` : le plus petit de `t[i:]`, échangé avec `t[i]`.

1. L'invariant, avant le code : après le tour `i`, que dire de
   `t[:i+1]` ? Deux choses.
2. `tri_selection(t)`. Commencez par `t = list(t)`. Comptez chaque
   `t[j] < t[mini]`.
3. Vérifiez contre `sorted(pops)`. Pronostic puis mesure : combien de
   comparaisons pour 24 valeurs ?
4. ★ Sur `sorted(pops)`, puis `sorted(pops, reverse=True)`. Pronostic,
   mesure. La formule en fonction de `n`.

## Étape 2 - L'insertion *(16 min)*

À chaque tour `i` : `x = t[i]` glisse vers la gauche tant que son voisin
est plus grand.

1. L'invariant. En quoi diffère-t-il de la sélection ?
2. `tri_insertion(t)`. Comptez chaque `t[j] > x`.
3. Pronostic puis mesure sur `pops`, `sorted(pops)`,
   `sorted(pops, reverse=True)`.
4. ★ Expliquez le plus petit et le plus grand des trois. Lequel des deux
   tris pour une liste presque triée ?

## Étape 3 - Mille valeurs *(14 min)*

```python
import random
random.seed(2026)
grande = random.sample(range(100000), 1000)
```

1. Pronostic pour la sélection (vous avez la formule), mesure.
2. Pronostic pour l'insertion, mesure. Le rapport avec la sélection ?
3. ★ Le tableau, à garder pour le chapitre 3 :

| n | sélection | insertion |
| --- | --- | --- |
| 10 | | |
| 100 | | |
| 1 000 | | |

Quand `n` est multiplié par 10, chaque colonne est multipliée par
combien ?

## Étape 4 - Bonus : les bulles *(6 min)*

Échanger deux voisins mal ordonnés, recommencer tant qu'il y a eu un
échange. Comptez, comparez à la sélection sur `pops`.

---

# TD 6 - La dichotomie

**38 minutes · en binôme · sur machine**

Dans `recherche.py` :

```python
alts = sorted(c["altitude"] for c in COMMUNES)
```

## Étape 1 - Linéaire *(6 min)*

1. `recherche_lineaire(t, x)` : l'indice ou `-1`, et le nombre de cases
   regardées. Testez `610`, `5`, `1180`, `500`.

## Étape 2 - Dichotomique *(16 min)*

Deux bornes `g` et `d`, le milieu `m = (g + d) // 2` ; trop petit,
`g = m + 1` ; trop grand, `d = m - 1` ; on s'arrête quand `g > d`.

1. L'invariant : si `x` est dans `t`, où est-il à chaque tour ?
2. `recherche_dichotomique(t, x)`, avec le compteur. Les quatre mêmes
   valeurs.
3. ★ Pronostic : le pire nombre d'étapes pour 24 valeurs ? Vérifiez sur
   `range(0, 1300)`. Puis sans machine : 1 000 valeurs ? Un million ? Un
   milliard ? Nommez la fonction mathématique.

## Étape 3 - La liste qui n'est pas triée ★ *(12 min)*

```python
pops = [c["population"] for c in COMMUNES]
```

1. `recherche_dichotomique(pops, 3120)` - 3120 est dans la liste. Que
   répond-elle ? Et la linéaire ?
2. ★ Aucune erreur, une réponse fausse. Écrivez la phrase qui manque à
   la docstring. Comment se protéger en une ligne - et que coûte cette
   ligne ?

## Étape 4 - Python le sait *(4 min)*

1. `bisect.bisect_left(alts, 610)`, puis `bisect_left(alts, 500)`. À quoi
   sert le second nombre ?

---

# Séance 3

# TD 7 - Le cas de base

**42 minutes · en binôme · sur machine**

Dans `recursif.py`. Pour chaque fonction, le cas de base s'écrit sur la
fiche **avant** l'appel.

## Étape 1 - Quatre fonctions *(16 min)*

1. `factorielle(n)`. `factorielle(20)` : ce que le C n'aurait pas su
   afficher ?
2. `somme(t)` : le premier élément plus la somme du reste. Cas de base ?
   Testez sur `range(1, 101)`.
3. `puissance(x, n)`, puis la version rapide : si `n` est pair,
   `puissance(x, n // 2)` au carré. Combien d'appels pour
   `puissance(2, 500)` dans chaque version ?
4. `pgcd(a, b)` : `a` si `b` vaut 0, sinon `pgcd(b, a % b)`.
   `pgcd(1071, 462)` ?

## Étape 2 - La pile *(8 min)*

1. `somme(list(range(900)))`, puis 1 000, puis 2 000. Recopiez l'erreur.
2. `sys.getrecursionlimit()`. Pourquoi 900 passe et 1 000 ne passe pas ?
3. ★ `somme` en boucle marche sur `range(100000)`. Ce que la récursion
   coûte que la boucle ne coûte pas - deux choses.

## Étape 3 - Fibonacci *(12 min)*

```python
appels = 0
def fib(n):
    global appels
    appels += 1
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)
```

1. `fib(5)` : combien d'appels ? Dessinez `fib(4)`.
2. ★ Pronostic écrit pour `fib(20)`, puis `fib(30)`. Mesurez. Le rapport
   entre les deux, pour dix de plus ? Nommez cette croissance.

## Étape 4 - Réparer *(6 min)*

```python
memo = {}
def fib_memo(n):
    ...
    if n not in memo:
        memo[n] = fib_memo(n - 1) + fib_memo(n - 2)
    return memo[n]
```

1. Complétez. Appels pour `fib_memo(30)`, `fib_memo(100)`. Formule ?
2. ★ Qu'est-ce que le dictionnaire évite, exactement ?

---

# TD 8 - Le tri fusion

**44 minutes · en binôme · sur machine**

Dans `tris.py` du TD 5.

## Étape 1 - Fusionner *(14 min)*

`fusion(g, d)` : deux listes triées, une liste triée qui contient tout.

1. Écrivez-la, avec le compteur (une comparaison par « quelle tête est la
   plus petite ? »).
2. Testez seule : `fusion([1, 5], [2, 3, 4])`, `fusion([], [1])`,
   `fusion([1, 2], [3, 4])`, `fusion([3, 4], [1, 2])`. Le troisième test
   attrape un bug classique : lequel ?
3. Au maximum, combien de comparaisons pour des longueurs `a` et `b` ?
   Au minimum ?

## Étape 2 - Trier *(14 min)*

1. `tri_fusion(t)` : cas de base, couper, trier chaque moitié, fusionner.
   Le compteur : une liste `cpt = [0]` passée aux appels, ou une globale.
2. Vérifiez sur `pops`. Pronostic, mesure. Comparez à l'insertion.
3. ★ L'arbre des appels de `tri_fusion([47, 12, 91, 3])`. Combien de
   niveaux ? Pour 8 éléments ? Pour 1 024 ?

## Étape 3 - Le tableau du chapitre 3 ★ *(12 min)*

`random.seed(2026)` puis `random.sample(range(10**6), n)` :

| n | insertion | fusion |
| --- | --- | --- |
| 10 | | |
| 100 | | |
| 1 000 | | |
| 10 000 | *(ne pas lancer)* | |

1. Pronostic pour la fusion à 1 000 et 10 000, mesure. Pourquoi la fiche
   interdit-elle l'insertion à 10 000 ?
2. ★ Quand `n` × 10, l'insertion × 100 environ. Et la fusion ? Reliez ce
   facteur au nombre de niveaux.

## Étape 4 - Bonus : le tri rapide *(4 min)*

Un pivot, les plus petits à gauche, les plus grands à droite, trier
chaque côté. Comptez sur `pops`, puis sur `sorted(pops)`.

---

# TD 9 - Le labyrinthe

**40 minutes · en binôme · sur machine, puis sur papier**

## Partie A - Sur machine *(24 min)*

`manip/labyrinthe.txt` : `#` un mur, `.` une case libre, `D` le départ.

```python
grille = [list(ligne) for ligne in open("labyrinthe.txt").read().splitlines()]
```

1. Lignes, colonnes, position de `D`, nombre de cases libres.
2. `explorer(i, j)` : mur ou déjà vue, ne rien faire ; sinon marquer et
   appeler sur les quatre voisines. Lancez depuis `D`, affichez la
   grille avec les cases atteintes en `o`.
3. Pronostic puis mesure : combien de cases atteignables ? Lesquelles ne
   le sont pas ?
4. ★ Retirez « déjà vue » de la condition d'arrêt. Recopiez ce qui se
   passe, expliquez avec les mots du TD 7.
5. Pourquoi n'a-t-on jamais besoin de vérifier qu'on sort de la grille ?

## Partie B - Sur papier ★ *(16 min)*

1. ★ Tracez `puissance(2, 5)`, version rapide : un appel par ligne,
   indenté selon la profondeur, ses arguments, sa valeur de retour.
   Combien d'appels ?
2. ★ Tracez `fusion([3, 8], [1, 9])` : à chaque comparaison, les deux
   têtes et l'élément ajouté. Combien de comparaisons ?
3. ★ `compter_cases(i, j)` renvoie le **nombre** de cases atteignables
   depuis `(i, j)`. Écrivez-la : le cas de base renvoie quoi ? L'appel
   additionne quoi ?

> Gardez `tris.py` et `recursif.py` : le chapitre 3 commence par les
> relancer.
