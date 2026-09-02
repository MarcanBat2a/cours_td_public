# TD - Complexité

**UE 0 - Algo 3 avec Python · Chapitre 3**
Marcu-Andria Battesti · Bachelor CLIC · 2026-2027

> Neuf travaux dirigés sur trois séances, tous sur machine. Dans
> `algo3/`, venv activé, un dossier `chapitre3/` avec `manip/` copié.
> Vos `tris.py` et `recursif.py` du chapitre 2 servent tels quels ;
> `manip/tris_ch2.py` en secours.
>
> **Le pronostic avant la mesure**, sur la fiche. Les temps varient d'un
> poste à l'autre ; les rapports entre lignes, non - ce sont eux qu'on
> lit.
>
> `manip/chrono.py` : `chrono(f, *args)` renvoie le meilleur de trois
> temps ; `tableau(f, tailles)` affiche n, temps et rapport pour des listes
> aléatoires de taille n, toujours les mêmes.
>
> **★** : les questions dont la réponse doit tenir en une phrase juste ou
> un calcul propre.

---

# Séance 1 - Mesurer, nommer, lire

# TD 1 - Chronomètre

**40 minutes · en binôme · sur machine**

## Étape 1 - À la main *(8 min)*

```python
import time
from chrono import liste_aleatoire
from tris import tri_insertion          # ou tris_ch2

t = liste_aleatoire(1000)
debut = time.perf_counter()
tri_insertion(t)
print(time.perf_counter() - debut)
```

1. Lancez trois fois. Les trois temps sont-ils égaux ? Lequel garder ?
2. Le même tri sur 2 000. Pronostic écrit, puis mesure.

## Étape 2 - Le tableau *(18 min)*

```python
from chrono import tableau
tableau(tri_insertion, [100, 1000, 3000, 10000])
```

1. Recopiez la colonne « rapport ». De 1 000 à 10 000, n × 10 : temps × ?
2. Même chose pour `tri_selection`, `tri_fusion`, et `sorted` (pour
   `sorted`, allez jusqu'à 1 000 000).
3. ★ Classez les quatre tris par leur rapport « n × 10 → temps × ? ».
   Deux familles apparaissent : lesquelles ?

## Étape 3 - Extrapoler *(14 min)*

1. Le temps de l'insertion à 10 000. Pronostic pour 100 000 ? Pour un
   million ? En secondes, minutes, heures.
2. Même calcul pour la fusion à un million. Vérifiez au chronomètre
   pour la fusion ; pour l'insertion, lancez 30 000 et comparez à votre
   règle.
3. ★ Le chapitre 2 a interdit l'insertion à 10 000 sur la fiche. Avec
   votre règle, dites en une phrase ce qui se passerait sur un million.

---

# TD 2 - Classer

**42 minutes · en binôme · sur machine**

## Étape 1 - La constante *(14 min)*

Les compteurs du chapitre 2 (les vôtres, ou `tris_ch2`) sur
`liste_aleatoire(n)` pour n = 100, 1 000, 10 000 :

| n | sélection / n² | insertion / n² | fusion / (n · log₂ n) |
| --- | --- | --- | --- |
| 100 | | | |
| 1 000 | | | |
| 10 000 | | | |

1. Remplissez. Qu'est-ce qui se stabilise ?
2. ★ La sélection tend vers 0,5 : d'où vient ce chiffre ? Et le 0,25 de
   l'insertion ?

## Étape 2 - Les classes *(14 min)*

Pour chaque classe, le nombre d'opérations à n = 1 000 et n = 10⁶ :

| Classe | n = 1 000 | n = 10⁶ | n × 10 → × ? |
| --- | --- | --- | --- |
| O(log n) | | | |
| O(n) | | | |
| O(n log n) | | | |
| O(n²) | | | |
| O(2ⁿ) | | | |

1. Remplissez sans machine. Python fait environ 10⁷ à 10⁸ opérations
   simples par seconde : convertissez la colonne 10⁶ en temps.
2. ★ Attribuez sa classe à chaque tri du TD 1, et à `sorted`. Justifiez
   par le rapport mesuré.

## Étape 3 - Jusqu'où *(14 min)*

Vous avez une seconde de calcul.

1. Quel n maximal pour un algorithme en O(n²) ? En O(n log n) ? En
   O(2ⁿ) ?
2. ★ Deux algorithmes en O(n²) : l'un compte 0,5 · n², l'autre 0,25 · n².
   Que dit la notation O ? Que dit le chronomètre ? Quand l'un des deux
   compte-t-il ?

---

# TD 3 - Lire le coût

**44 minutes · en binôme · sur machine**

`manip/fonctions.py` : huit fonctions, `f1` à `f8`.

## Étape 1 - En lisant *(16 min)*

Pour chacune, sans la lancer : la classe, et la ligne qui la décide.

| | classe | la ligne qui coûte |
| --- | --- | --- |
| f1 | | |
| f2 | | |
| f3 | | |
| f4 | | |
| f5 | | |
| f6 | | |
| f7 | | |
| f8 | | |

## Étape 2 - Au chronomètre *(20 min)*

`tableau(f, tailles)` avec des tailles adaptées : trois valeurs, chacune
double de la précédente, la plus grande sous une seconde. Pour `f4`,
`chrono(f4, n)` avec n = 10³, 10⁶, 10⁹.

1. Le rapport « n × 2 → temps × ? » pour chaque fonction. Corrigez votre
   tableau.
2. ★ `f5` et `f7` : où est le coût caché ? Réécrivez chacune en O(n).
3. ★ `f6` fait le travail de `min(t)`. Combien de fois plus cher, à
   100 000 ? Pourquoi ?

## Étape 3 - Deux pièges *(8 min)*

1. `f8` a une boucle intérieure de longueur `i`, pas `n`. Pourquoi est-ce
   quand même O(n²) ? Le rapport mesuré le confirme-t-il ?
2. ★ `f1` sur dix millions d'éléments : le temps ne bouge pas. Quelle
   opération sur une liste Python est en O(1), et pourquoi ?

---

# Séance 2 - Les algorithmes du chapitre 2

# TD 4 - Les constantes

**40 minutes · en binôme · sur machine**

## Étape 1 - Exact *(12 min)*

1. `tri_selection` sur `liste_aleatoire(n)` pour n = 10, 100, 1 000 :
   vérifiez n(n-1)/2 au compteur, exactement.
2. ★ Écrivez la somme qui donne n(n-1)/2 : combien de comparaisons au
   tour 0, au tour 1, ..., au dernier ?

## Étape 2 - En moyenne *(14 min)*

1. `tri_insertion` sur cinq listes aléatoires différentes de 1 000
   (changez la graine : `random.seed(k)` puis `random.sample`). Les cinq
   compteurs, leur moyenne, divisée par n².
2. ★ Pourquoi 0,25 et pas 0,5 ? Où s'arrête un élément qui glisse, en
   moyenne ?

## Étape 3 - Prédire *(14 min)*

1. Le temps d'une comparaison : temps de l'insertion à 10 000 (TD 1)
   divisé par son compteur. En nanosecondes.
2. Avec ce temps et n²/4 : l'insertion sur un million, en secondes puis
   en heures. Sur dix millions ?
3. ★ La fusion sur un million : compteur prédit avec 0,9 · n · log₂ n,
   temps prédit, temps mesuré. L'écart ?

---

# TD 5 - Compter les appels

**42 minutes · en binôme · sur machine**

`recursif.py` du chapitre 2, ou réécrit en cinq minutes.

## Étape 1 - Fibonacci *(14 min)*

1. Le nombre d'appels de `fib(n)` pour n de 20 à 30, et le rapport d'un n
   au suivant.
2. ★ Le rapport se stabilise. Sur quelle valeur ? Combien d'appels pour
   `fib(40)` ? Pour `fib(50)` - en temps ?
3. Même mesure sur `fib_memo`. Formule ?

## Étape 2 - Hanoï *(10 min)*

```python
def hanoi(n, cpt):
    if n == 0:
        return
    hanoi(n - 1, cpt)
    cpt[0] += 1
    hanoi(n - 1, cpt)
```

1. Compteur pour n = 5, 10, 15, 20. Formule ? Classe ?
2. Temps pour n = 20. Pronostic pour n = 30, puis n = 64.

## Étape 3 - La copie cachée *(18 min)*

```python
def somme_rec(t):
    if not t:
        return 0
    return t[0] + somme_rec(t[1:])
```

1. `sys.setrecursionlimit(5000)`, puis `chrono(somme_rec, list(range(n)))`
   pour n = 200, 400, 800, 1 600, 3 200. Rapport quand n × 2 ?
2. Même chose pour `somme` en boucle. Rapport ?
3. ★ Où sont les n² de la version récursive ? Réécrivez-la en récursif
   **sans** copie : un indice en argument. Rapport ?

---

# TD 6 - Pire cas

**44 minutes · en binôme · sur machine**

## Étape 1 - L'insertion *(12 min)*

Pour n = 1 000 et 3 000, trois entrées : `liste_aleatoire(n)`, la même
triée, la même inversée.

1. Compteurs et temps. Le rapport entre le meilleur et le pire ?
2. ★ Formule du meilleur cas, du pire cas. Lequel des deux la notation
   O(n²) décrit-elle ?

## Étape 2 - Le tri rapide *(12 min)*

Le bonus du chapitre 2 (pivot = premier élément), ou :

```python
def tri_rapide(t, cpt):
    if len(t) <= 1:
        return list(t)
    pivot, petits, grands = t[0], [], []
    for x in t[1:]:
        cpt[0] += 1
        (petits if x < pivot else grands).append(x)
    return tri_rapide(petits, cpt) + [pivot] + tri_rapide(grands, cpt)
```

1. Compteur sur `liste_aleatoire(n)` puis sur la même triée, n = 1 000
   et 2 000. Classe dans chaque cas ?
2. ★ Pourquoi la liste triée est-elle le pire cas de **ce** tri rapide ?
   Un remède en une ligne ?

## Étape 3 - sorted *(12 min)*

1. `sorted` sur un million : aléatoire, déjà trié, inversé. Les trois
   temps.
2. ★ Le déjà-trié est bien plus rapide. Quelle classe pour ce cas ? Que
   fait `sorted` que votre tri fusion ne fait pas ?

## Étape 4 - Le mot juste *(8 min)*

1. ★ Complétez : « l'insertion est en O(...) dans le pire cas, O(...)
   dans le meilleur, O(...) en moyenne ; `sorted` est en O(...) dans le
   pire cas et O(...) sur une liste déjà triée. » Quelle classe donne-t-on
   quand on n'en donne qu'une ?

---

# Séance 3 - Optimiser

# TD 7 - La bonne structure

**42 minutes · en binôme · sur machine**

## Étape 1 - in *(14 min)*

```python
from chrono import liste_aleatoire, chrono
import random
identifiants = liste_aleatoire(100000)
random.seed(7)
requetes = [random.randrange(0, 1000010) for _ in range(1000)]
```

1. `connus(requetes, identifiants)` : combien de requêtes sont dans la
   liste ? Temps.
2. La même fonction avec `set(identifiants)` construit **une fois**.
   Temps, et le résultat, identique ?
3. ★ Coût de la version liste en fonction de n (liste) et q (requêtes).
   De la version ensemble. Le rapport mesuré est-il cohérent ?

## Étape 2 - Les doublons *(14 min)*

`random.seed(n)` puis `[random.randrange(0, n) for _ in range(n)]`, pour
n = 2 000, 4 000, 8 000.

1. `doublons_n2(t)` : deux boucles. Temps, rapport quand n × 2.
2. `doublons_set(t)` : un ensemble des valeurs déjà vues. Temps, rapport.
3. ★ Le nombre de doublons trouvés est-il le même ? Si non, pourquoi, et
   laquelle des deux a raison ?

## Étape 3 - Deux qui font n *(14 min)*

Les paires de communes dont les populations font exactement 1 000.

1. En deux boucles, sur `pops`. Résultat.
2. Avec un ensemble des valeurs déjà vues : pour chaque `x`, `1000 - x`
   a-t-il déjà été vu ? Même résultat ?
3. ★ Les deux sur `random.sample(range(0, 4 * n), n)` pour n = 2 000,
   4 000, 8 000. Classes, rapports, et la phrase qui résume le TD.

---

# TD 8 - Précalculer

**44 minutes · en binôme · sur machine**

## Étape 1 - Sommes d'intervalles *(16 min)*

```python
t = liste_aleatoire(100000)
random.seed(8)
requetes = [sorted(random.sample(range(100000), 2)) for _ in range(2000)]
```

1. `sommes_naif(t, requetes)` : `sum(t[a:b])` pour chaque `(a, b)`.
   Temps.
2. `sommes_prefixe(t, requetes)` : `prefixe[i]` = somme de `t[:i]`,
   construit une fois ; puis `prefixe[b] - prefixe[a]`. Temps, résultat
   identique ?
3. ★ Coût de chaque version en fonction de n et q. Pour combien de
   requêtes le précalcul est-il rentable ?

## Étape 2 - Trier une fois *(14 min)*

1 000 recherches dans la liste de 100 000 (les `requetes` du TD 7).

1. `x in t` mille fois. Temps.
2. `sorted(t)` une fois, puis `bisect.bisect_left` mille fois. Temps,
   même compte ?
3. ★ Le tri coûte n log n. À partir de combien de recherches est-il
   remboursé ?

## Étape 3 - Collatz, avec mémoire *(14 min)*

1. Le `n < 100 000` qui demande le plus d'étapes, avec `etapes(n)` du
   chapitre 2. Temps.
2. La même chose avec un dictionnaire des longueurs déjà calculées :
   `etapes(n) = 1 + etapes(suivant)`, mémorisé.
   `sys.setrecursionlimit(10000)`. Temps, même réponse ?
3. ★ Qu'est-ce qui est mémorisé, et pourquoi ça sert d'un `n` à l'autre ?

---

# TD 9 - Le programme lent

**40 minutes · en binôme · sur machine, puis sur papier**

## Partie A - lent.py *(26 min)*

```bash
python manip/lent.py
```

1. Les trois temps. Laquelle des trois parties d'abord ?
2. Pour chaque partie : la classe, la ligne qui coûte, le remède du
   chapitre. Réparez, dans le même fichier, sans changer les résultats
   affichés.
3. ★ Les trois nouveaux temps, et le gain total. Quelle partie a le plus
   gagné, et pourquoi celle-là ?

## Partie B - Sur papier ★ *(14 min)*

```python
def a(t):
    return len(set(t)) == len(t)

def b(t):
    for i in range(len(t)):
        if t[i] in t[i + 1:]:
            return False
    return True

def c(t, x):
    t = sorted(t)
    g, d = 0, len(t) - 1
    while g <= d:
        m = (g + d) // 2
        if t[m] == x:
            return True
        if t[m] < x:
            g = m + 1
        else:
            d = m - 1
    return False
```

1. ★ `a` et `b` répondent à la même question. Laquelle ? Classe de
   chacune, avec la ligne qui coûte.
2. ★ Classe de `c`. Elle est pire que `x in t` : pourquoi ? Dans quel cas
   d'usage la trier vaudrait-elle le coup ?
3. ★ Une fonction reçoit une liste de n communes et, pour chaque commune,
   compte celles du même canton en parcourant toute la liste. Classe ?
   Réécrivez-la en une classe de moins, en trois lignes.
