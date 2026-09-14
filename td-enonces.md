# TD - Rappel des structures algorithmiques

**UE 0 - Algo 3 avec Python · Chapitre 2**
Marcu-Andria Battesti · Bachelor CLIC · 2026-2027

> Neuf travaux dirigés sur trois séances, sur machine et sur papier. Gardez vos
> fichiers : les tris et leurs compteurs resservent au chapitre 3.
>
> On travaille dans `algo3/` (chapitre 1), venv activé, dans un dossier
> `chapitre2/` où le **contenu** de `manip/` est copié : `communes.py`,
> `communes.csv`, `trace_factorielle.py` et `labyrinthe.txt` à côté de vos fichiers, pas dans un
> sous-dossier. Le REPL pour une ligne, un fichier `.py` dès trois lignes.
>
> **Méthode** : lisez d’abord l’exemple du [cours](cours.md), faites une
> trace à la main, complétez la partie guidée, puis écrivez votre solution.
> Pour une trace, notez les valeurs **après** chaque instruction ou tour.
> Écrivez le résultat attendu avant d’exécuter les tests avec `assert`.
>
> **★** : les questions dont la réponse doit tenir en une phrase juste ou
> un tracé propre - celles que l'évaluation peut reprendre.
>
> Le jeu de données : `manip/communes.py`, 24 communes imaginaires, quatre
> cantons - `from communes import COMMUNES`.

---

# Séance 1

# TD 1 - Prise en main

**Sur machine**

## Étape 0 - Le REPL

```python
t = [12, 47, 3, 91, 25]
t[-2]
t[2:]
t[:2]
t.append(7)
91 in t
```

1. Notez les trois réponses. La règle de `t[a:b]`, en une phrase.

## Exemple guidé - Lire une boucle ★

Le cours montre comment remplir un tableau de trace. Faites maintenant
celui-ci, sans ordinateur :

```python
total = 0
for x in [4, -1, 6, 0]:
    if x >= 0:
        total += x
```

| Tour | `x` | Test `x >= 0` | `total` après le tour |
| --- | --- | --- | --- |
| avant | — | — | 0 |
| 1 | 4 | vrai | 4 |
| 2 | -1 | … | … |
| 3 | 6 | … | … |
| 4 | 0 | … | … |

Expliquez le tour où le bloc du `if` n’est pas exécuté. Exécutez ensuite
le programme et vérifiez votre dernière ligne.

## Étape 1 - Collatz

Suite de Collatz : pour un entier `n >= 1`, si `n` est pair, `n // 2` ; sinon `3 * n + 1` ; on
s'arrête à 1.

`//` donne le quotient entier ; `%` donne le reste. `n % 2 == 0` teste la parité.

1. Exemple : depuis `3`, les valeurs sont `3, 10, 5, 16, 8, 4, 2, 1`.
   Il y a **7 transformations**. Tracez de même depuis `6`.
2. Complétez le programme :

   ```python
   def etapes(n):
       """n >= 1 ; nombre de transformations jusqu’à 1."""
       compteur = 0
       while ...:
           if n % 2 == 0:
               n = ...
           else:
               n = ...
           compteur += 1
       return compteur
   ```

3. Écrivez les tests pour `1`, `3` et `6`, puis calculez `etapes(27)`.
4. **Pour aller plus loin :** quel entier strictement inférieur à 100
   demande le plus d’étapes ? Combien en demandent plus de 100 ?

## Étape 2 - Le maximum

`valeurs = [12, 47, 3, 91, 25, 68, 91, 7]`

1. `maximum(valeurs)` reçoit une liste **non vide** et renvoie le plus
   grand élément **et** sa première position, sans `max()` ni `index()`.
   Initialisez le candidat avec le premier élément, puis tenez un tableau
   `indice / valeur lue / maximum retenu / position retenue`.
   Testez aussi `[-8, -3, -5]` : pourquoi ne pas initialiser le maximum à 0 ?
2. ★ 91 est présent deux fois. Votre fonction renvoie quelle position ?
   Quel caractère changer pour obtenir l'autre ?

## Étape 3 - Pour aller plus loin : à l’envers

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

**Sur machine**

## Étape 0 - Lire les données

```python
from communes import COMMUNES
len(COMMUNES)
COMMUNES[0]
COMMUNES[-1]["altitude"]
```

1. Qu'est-ce que `COMMUNES` ? `COMMUNES[0]` ? La population de la
   troisième commune ?

## Exemple guidé - Compter ou sommer ? ★

Pour les altitudes `[120, 640, 510, 80]`, on veut le **nombre** de valeurs
au-dessus de 500. Le premier tour laisse le compteur à 0.

```python
compteur = 0
for altitude in [120, 640, 510, 80]:
    if altitude > 500:
        compteur += ...
```

Complétez et tracez. Que calculerait-on en remplaçant la mise à jour par
`compteur += altitude` ? Adaptez ensuite le parcours aux dictionnaires
`c` du jeu `COMMUNES`.

## Étape 1 - Compter, filtrer

Dans `parcours.py` :

1. Chaque commune, une par ligne, nom et population.
2. Le nombre de communes au-dessus de 500 m. Pronostic, puis mesure.
3. Les noms des communes de plus de 1 000 habitants. Combien ?
4. La population totale, puis l'altitude moyenne.

## Étape 2 - Le maximum, sans max()

1. La commune la plus peuplée. Écrivez d’abord la phrase décrivant
   le candidat conservé après chaque tour, puis adaptez le maximum du TD 1.
2. ★ La plus dense (habitants par km²). Qu'est-ce qui change par rapport
   à la question 1 ?
3. **Pour aller plus loin :** la moins dense. Notez les deux noms et densités.

## Étape 3 - S'arrêter

1. La première commune de la liste au-dessus de 900 m, puis `break`.
   Son indice ?
2. Les communes de moins de 100 habitants, avec `continue`, puis sans.
   Laquelle gardez-vous ?
3. ★ Une seule boucle de ce TD a besoin d'un indice : laquelle, et
   pourquoi celle-là ?

---

# TD 3 - Les cantons

**Sur machine**

## Exemple guidé - Afficher ou renvoyer ? ★

```python
def affiche_double(x):
    print(2 * x)

def calcule_double(x):
    return 2 * x

a = affiche_double(4)
b = calcule_double(4)
```

Sans exécuter, distinguez ce qui est affiché, la valeur de `a` et celle de
`b`. Quelle fonction permet de calculer `resultat = ... + 1` ?
Écrivez un `assert` pour cette fonction et vérifiez-le.

## Étape 1 - Des fonctions

Dans `cantons.py`, testées dans le REPL :

1. `densite(commune)`, avec une docstring.
2. `plus_peuplee(communes)` : liste non vide, renvoie la commune entière,
   sans `max()`. Notez cette précondition dans la docstring.
3. `extremes_altitude(communes)` : liste non vide, renvoie deux valeurs,
   la plus basse et la plus haute.
4. `au_dessus(communes, seuil=500)` : la liste des noms, en une ligne.
   Appelez `au_dessus(COMMUNES)`, puis `au_dessus(COMMUNES, 900)`.

## Étape 2 - Regrouper

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

## Étape 3 - Prolongement guidé : depuis un fichier

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

## Étape 4 - Relire

1. Réécrivez les questions 1.2 et 1.3 du TD 2 en compréhensions.

> Gardez `cantons.py` : `charger` sert aux chapitres 3 et 4.

---

# Séance 2

# TD 4 - Trier les communes

**Sur machine**

Dans `tris_python.py`.

## Exemple guidé - Prédire avant de trier ★

```python
mots = ["pic", "rive", "lac", "col"]
a = sorted(mots, key=len)
b = mots.sort()
```

1. Donnez `a`, `b` et la valeur finale de `mots`.
2. Dans `a`, pourquoi `pic` reste-t-il avant `lac` et `col` ?
3. Vérifiez au clavier puis définissez « stable » et « en place ».

## Étape 1 - Une clé

1. Les cinq communes les plus peuplées.
2. Les trois plus basses.
3. Les noms par ordre alphabétique. La clé est-elle nécessaire ?
4. ★ Par longueur de nom. Deux noms de même longueur : dans quel ordre
   sortent-ils, et pourquoi celui-là ?

## Étape 2 - Deux critères

1. Par canton, puis population décroissante dans chaque canton. Un
   tuple en clé, sans `reverse`.
2. Population croissante, puis canton décroissant **à population égale**.
   Identifiez le critère principal et le secondaire. Un `-` ne s’applique
   pas à une chaîne ; utilisez deux tris successifs, secondaire d’abord.
   Testez avec deux communes de même population et de cantons différents.

## Étape 3 - Ce qu'un tri laisse au suivant ★

```python
etape1 = sorted(COMMUNES, key=lambda c: c["population"], reverse=True)
etape2 = sorted(etape1, key=lambda c: c["canton"])
```

1. Affichez `etape2`. Dans chaque canton, dans quel ordre sont les
   communes ? D'où vient cet ordre ?
2. ★ `sorted` est **stable**. Définissez-le avec le mot « ex æquo ». En
   quoi ça rend le tuple de 2.1 inutile - et pourquoi on le préfère
   quand même ?

## Étape 4 - En place

1. `t = [3, 1, 2]` ; `t.sort()` renvoie quoi ? `t` vaut quoi ? Quand
   `sort`, quand `sorted` ?

---

# TD 5 - Écrire et vérifier deux tris

**Sur machine**

Dans `tris.py`. Chaque tri prend une liste de nombres et renvoie
`triee, comparaisons`, sans modifier la liste reçue. Le compteur servira
au chapitre 3 ; ici, on vérifie le résultat et on suit les déplacements.

```python
from communes import COMMUNES
pops = [c["population"] for c in COMMUNES]
```

## Exemple guidé - Vérifier l’ordre ★

Un **prédicat** est une fonction qui renvoie un booléen. Écrivez
`est_triee(t)` : examiner chaque paire de voisins, renvoyer `False` dès
qu’une paire est mal ordonnée, et `True` à la fin.

```python
assert est_triee([])
assert est_triee([7])
assert est_triee([1, 1, 4])
assert not est_triee([1, 4, 2])
```

Le cours donne les étapes des tris sur `[6, 3, 5, 1]`. Pour les exercices
suivants, utilisez `[4, 2, 3, 1]` et notez le préfixe trié après chaque tour.

## Étape 1 - La sélection

À chaque tour `i` : le plus petit de `t[i:]`, échangé avec `t[i]`.

1. ★ Sur `[4, 2, 3, 1]`, écrivez la liste après chaque tour.
   Après le tour `i`, que dire de `t[:i+1]` et du reste ?
2. Complétez le squelette. `mini` contient un **indice**, pas une valeur.

   ```python
   def tri_selection(t):
       t = list(t)
       comparaisons = 0
       for i in range(len(t) - 1):
           mini = i
           for j in range(i + 1, len(t)):
               comparaisons += 1
               if ...:
                   mini = ...
           t[i], t[mini] = ...
       return t, comparaisons
   ```
3. Vérifiez contre `sorted(pops)`. Notez le compteur pour ces 24 valeurs.
4. ★ Expliquez pourquoi les valeurs déjà placées ne bougeront plus.

## Étape 2 - L'insertion

À chaque tour `i` : `x = t[i]` glisse vers la gauche tant que son voisin
est plus grand.

1. ★ Tracez les tours sur `[4, 2, 3, 1]`. Quel préfixe est trié après
   chaque tour ? Peut-il encore changer au tour suivant ?
2. Écrivez `tri_insertion(t)` sur une copie. Mémorisez `x = t[i]` et
   commencez avec `j = i - 1`. Tant que `j >= 0`, comptez le test
   `t[j] > x` : s’il est vrai, décalez et reculez ; sinon quittez la
   boucle. Réinsérez `x` à l’indice `j + 1`, même si aucun décalage n’a lieu.
   Le test de borne `j >= 0` n’est pas compté.
3. Vérifiez sur `pops`, puis sur `sorted(pops)` et son inverse.
   Observez les déplacements sur une petite liste déjà triée.
4. ★ Quel test empêche de lire un indice négatif ? Pourquoi faut-il
   remettre `x` dans la liste après les décalages ?

## Étape 3 - Les cas limites ★

Testez **les deux tris** sur `[]`, `[7]`, `[2, 2, 1]`, `[-3, 0, -8]`,
une liste triée et une liste inversée. Pour chacun :

1. résultat égal à `sorted(entree)` ;
2. mêmes valeurs, doublons conservés ;
3. liste d'origine inchangée.

Gardez les fonctions et leurs compteurs. Les formules et les tableaux
pour de grandes tailles seront construits au chapitre 3.

## Étape 4 - Bonus : les bulles

Parcourir les voisins de gauche à droite et échanger ceux qui sont mal
ordonnés ; après un passage, le plus grand du reste est à sa place.
Le passage suivant s'arrête une case plus tôt. Écrivez ce tri et
soumettez-le aux mêmes tests.

---

# TD 6 - La dichotomie

**Sur machine**

Dans `recherche.py` :

```python
from communes import COMMUNES
alts = sorted(c["altitude"] for c in COMMUNES)
```

## Étape 1 - Linéaire

1. `recherche_lineaire(t, x)` : renvoie l'indice ou `-1`, et le nombre
   de cases regardées. Testez `610`, `5`, `1180`, `500`, puis la liste vide.

## Étape 2 - Dichotomique

Deux bornes inclusives `g = 0` et `d = len(t) - 1`, le milieu
`m = (g + d) // 2` ; trop petit, `g = m + 1` ; trop grand, `d = m - 1`.
On s'arrête quand on trouve `x` ou quand `g > d`.

1. ★ Complétez cette trace pour chercher `8` dans `[2, 4, 6, 8, 10]` :

   | `g` | `d` | `m` | `t[m]` | Action |
   | --- | --- | --- | --- | --- |
   | 0 | 4 | 2 | 6 | trop petit : `g = 3` |
   | … | … | … | … | … |

   Refaites le tableau pour `7`. Si la cible est présente, où doit-elle
   rester à chaque tour ? Écrivez la condition de sortie dans chaque cas.
2. `recherche_dichotomique(t, x)`, avec le compteur. Testez les mêmes
   entrées que pour la recherche linéaire, puis `[5]` et `[5, 5]`.
3. ★ Pourquoi `m + 1` et `m - 1`, plutôt que `m` ? Quelle quantité
   diminue tant que la recherche continue ?

## Étape 3 - La liste qui n'est pas triée ★

```python
pops = [c["population"] for c in COMMUNES]
```

1. `recherche_dichotomique(pops, 3120)` : comparez à la linéaire.
   Essayez aussi `4250`. Le résultat est-il toujours faux ?
2. ★ Écrivez la précondition dans la docstring. Vérifiez une fois que
   les éléments voisins sont dans l'ordre avant une série de recherches.
   Le chapitre 3 étudiera le coût de cette vérification.

## Étape 4 - Python le sait

1. `from bisect import bisect_left`, puis `bisect_left(alts, 610)` et
   `bisect_left(alts, 500)`. Ce sont des **points d'insertion**.
2. ★ Après `i = bisect_left(alts, x)`, testez
   `i < len(alts) and alts[i] == x` pour savoir si `x` est présent.

---

# Séance 3

# TD 7 - Le cas de base et les retours

**Sur papier, puis sur machine**

Dans `recursif.py`. Avant chaque fonction : les entrées autorisées,
le résultat attendu, le cas de base et ce qui diminue à chaque appel.
Pour les fonctions numériques ci-dessous, `n` est un entier positif ou nul.

## Avant de calculer - Une récursion qui affiche

Relisez `compte_a_rebours` dans le cours. Prévoyez l’affichage pour `3`,
puis exécutez-le. Entourez l’appel récursif et le test qui empêche un
nouvel appel. Chaque appel a son propre `n`.

## Étape 1 - Lire une trace ★

```python
def factorielle(n):
    if n <= 1:
        return 1
    return n * factorielle(n - 1)
```

La factorielle `3!` est le produit `3 × 2 × 1`. La **trace** raconte
comment le programme calcule ce résultat. Lisez ensemble les cinq lignes :

```text
1. factorielle(3) attend 3 * factorielle(2)
2.   factorielle(2) attend 2 * factorielle(1)
3.     factorielle(1) renvoie 1 (cas de base)
4.   factorielle(2) reprend : 2 * 1 = 2
5. factorielle(3) reprend : 3 * 2 = 6
```

Les lignes 1 et 2 commencent des appels : les produits attendent.
Les lignes 3 à 5 remplacent chaque appel terminé par sa valeur : on peut
alors calculer le produit. La fonction s’arrête à `1`, pas à `0`, dans
cet exemple. Pour revoir ces étapes au clavier : `python trace_factorielle.py`.
Ce fichier illustre l’exemple ; les fonctions à écrire restent dans `recursif.py`.

1. Trace guidée de `factorielle(4)` : ajoutez `factorielle(4) attend
   4 * factorielle(3)` **avant** l’exemple. Les cinq lignes du milieu
   restent les mêmes. Complétez la dernière : `factorielle(4) reprend :
   4 * ... = ...`. Tracez ensuite `factorielle(0)` en une seule ligne.
2. ★ À quel moment effectue-t-on la multiplication ? Dans une copie nommée
   `factorielle_sans_return`, retirez seulement le `return` devant le produit
   et adaptez le nom de l'appel récursif. Prévoyez puis vérifiez le résultat
   pour `2`, puis pour `3`. Distinguez une valeur renvoyée d'une erreur
   levée dans l'appel parent. Gardez la version correcte pour la suite.
3. Exécutez `factorielle(21)` : ce résultat dépasse la valeur maximale
   d'un entier signé de 64 bits. Python conserve sa valeur exacte.

## Étape 2 - Écrire et tester

1. `somme(t)` : le premier élément plus la somme du reste. Écrivez le
   cas de base, puis testez `[]`, `[5]`, `[2, -1, 4]` et `list(range(1, 101))`.
2. `puissance(x, n)` : utilisez `x * puissance(x, n - 1)`. Testez
   `(2, 0)`, `(2, 5)`, `(-2, 3)`. On adopte `puissance(0, 0) = 1`.
3. ★ Tracez `somme([2, 3])`, arguments et retours. Pourquoi un cas de
   base correct ne suffit-il pas si l'appel conserve le même argument ?

## Étape 3 - La pile

1. `import sys`, puis `sys.getrecursionlimit()`.
2. Essayez `somme(list(range(100)))`, puis une liste dont la longueur
   vaut la limite affichée. Relevez l'erreur sans changer cette limite.
3. ★ Expliquez les appels en attente. Le seuil exact dépend aussi des
   appels déjà présents dans l'environnement d'exécution.

## Étape 4 - Deux appels, un résultat

```python
appels = 0

def fib(n):
    global appels
    appels += 1
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)
```

1. Exemple de départ : `fib(2)` appelle `fib(1)` qui renvoie `1`, puis
   `fib(0)` qui renvoie `0` ; il renvoie donc `1`. C’est un arbre à deux
   branches. ★ Construisez celui de `fib(4)` en utilisant ce petit arbre
   à chaque occurrence de `fib(2)`. Inscrivez les retours à côté des appels.
2. Remettez `appels` à zéro, puis vérifiez `fib(5)`. Distinguez le
   résultat de la fonction et le nombre d'appels. Gardez ce code pour
   les mesures et la mémoïsation du chapitre 3.

**Bonus :** `pgcd(a, b)`, pour deux entiers positifs ou nuls, non tous
les deux nuls : renvoyer `a` si `b == 0`, sinon `pgcd(b, a % b)`.
Testez `(1071, 462)` et `(12, 0)`.

---

# TD 8 - Le tri fusion

**Sur machine, puis sur papier**

Dans `tris.py` du TD 5.

## Étape 1 - Fusionner

`fusion(g, d)` reçoit deux listes triées et renvoie une nouvelle liste
triée qui contient tous leurs éléments, doublons compris.

1. Complétez la trace de `fusion([1, 5], [2, 3, 4])` après avoir lu
   l’exemple du cours :

   | Tête gauche | Tête droite | Élément ajouté | Résultat partiel |
   | --- | --- | --- | --- |
   | 1 | 2 | 1 | `[1]` |
   | 5 | 2 | … | … |
   | … | … | … | … |

   Ajoutez la ligne où l’une des deux listes est épuisée.
2. Écrivez la fonction. Comptez une comparaison entre deux têtes dans
   une globale `comparaisons`, remise à zéro avant chaque mesure.
3. Testez `([], [])`, `([], [1])`, `([1, 2], [3, 4])`, `([3, 4], [1, 2])`
   et `([1, 2], [2, 3])`. Pourquoi faut-il recopier la partie restante ?

## Étape 2 - Trier

1. ★ Écrivez le contrat puis complétez ce squelette. Les deux appels
   doivent être terminés avant de fusionner leurs résultats.

   ```python
   def tri_fusion(t):
       if len(t) <= ...:
           return list(t)
       milieu = len(t) // 2
       gauche = tri_fusion(...)
       droite = tri_fusion(...)
       return fusion(..., ...)
   ```

   La fonction renvoie uniquement la liste triée. La liste vide est
   autorisée : il faut traiter **zéro ou un élément** avant de découper.
2. Vérifiez sur `pops`. Le compteur se lit après l'appel. Comparez le
   **résultat** aux deux autres tris ; le coût sera étudié au chapitre 3.
3. ★ Tracez les appels et les retours de `tri_fusion([4, 1, 3, 2])`.
   Que renvoie chaque feuille ? Quand la première fusion a-t-elle lieu ?

## Étape 3 - Vérifier ★

Reprenez les cas limites du TD 5 : liste vide, singleton, doublons,
négatifs, liste triée et inversée.

1. Vérifiez le résultat et la conservation de l'entrée.
2. Expliquez pourquoi les moitiés deviennent strictement plus courtes
   lorsqu'il y a au moins deux éléments.
3. Gardez les trois tris. Au chapitre 3, on variera la taille des données
   pour comparer leurs compteurs et expliquer leurs différences.

---

# TD 9 - Tracer et vérifier

**Sur papier, puis sur machine**

## Partie A - Les retours ★

1. Tracez `puissance(2, 3)`, version du TD 7 : un appel par ligne,
   indenté, ses arguments et sa valeur de retour.
2. Tracez `fusion([3, 8], [1, 9])` : les deux têtes comparées et l'élément
   ajouté à chaque étape, puis la recopie finale.
3. Tracez `tri_fusion([])` et `tri_fusion([7])`. Pourquoi ces deux
   entrées doivent-elles être traitées avant la découpe ?

## Partie B - Corriger une fonction ★

```python
def somme_bug(t):
    if not t:
        return 0
    t[0] + somme_bug(t)
```

1. Identifiez les deux erreurs et corrigez-les.
2. Écrivez trois tests, dont un sur une liste vide et un avec un négatif.
3. Écrivez la version en boucle. Vérifiez que les deux versions renvoient
   le même résultat pour ces tests. L'analyse de leur coût viendra ensuite.

## Partie C - Réutiliser la méthode : palindrome ★

Un **palindrome** se lit de la même façon dans les deux sens. On compare
les caractères exactement, sans supprimer les espaces ni changer la casse.

Écrivez un prédicat récursif `palindrome(mot)` :

1. une chaîne de longueur 0 ou 1 convient immédiatement ;
2. si les deux caractères aux extrémités diffèrent, le résultat est faux ;
3. sinon, il reste à examiner l’intérieur, `mot[1:-1]`.

Tracez `palindrome("kayak")` avant de coder : quelle chaîne est traitée
à chaque appel ? Testez aussi `""`, `"x"`, `"ab"` et `"Kayak"`.
N’utilisez pas `mot[::-1]` dans cette version.

---

# Bonus - Le labyrinthe

**Facultatif, après les TD 7 à 9 ; repris au chapitre 4.**

`labyrinthe.txt` : `#` un mur, `.` une case libre, `D` le départ.

```python
grille = [list(ligne) for ligne in open("labyrinthe.txt").read().splitlines()]
```

1. Lignes, colonnes, position de `D`, nombre de cases libres.
2. `explorer(i, j)` : mur ou déjà vue, ne rien faire ; sinon marquer et
   appeler sur les quatre voisines. Affichez les cases atteintes en `o`.
3. Comptez les cases atteignables. Lesquelles ne le sont pas ?
4. Retirez « déjà vue » de la condition d'arrêt. Expliquez ce qui se passe.
5. Pourquoi la bordure de murs dispense-t-elle de vérifier les indices ?
6. `compter_cases(i, j)` : cas de base `0`, sinon `1` plus la somme des
   quatre appels voisins. Videz l'ensemble des cases vues avant ce calcul.

> Gardez `tris.py`, `recherche.py` et `recursif.py` pour le chapitre 3.

## Ressources pour s’entraîner

La [fin du cours](cours.md#pour-poursuivre-avec-qkzk) référence les cours
et exercices de qkzk utilisés pour construire cette progression :
parcours, sélection, insertion, dichotomie, récursivité et tri fusion.
Les exercices de coût sur ces pages prépareront le chapitre 3.
