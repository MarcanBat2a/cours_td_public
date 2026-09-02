# Mémo - Python, les tris, la récursion

**UE 0 - Algo 3 avec Python · Chapitre 2**
Distribué en fin de séance 2 · à garder pour tout le module

> Une page : l'orthographe Python, les structures, les tris avec
> leurs comptes, la récursion. Ce qui a été tapé en TD, condensé.

## L'orthographe

```python
n = 5                          # pas de type déclaré, pas de ;
if n > 3 and n < 10:           # and, or, not - ou : 3 < n < 10
    ...                        # : puis indentation (4 espaces) - obligatoire
elif n == 3:
    ...
else:
    ...
for c in communes:             # parcourt les ÉLÉMENTS
for i in range(10):            # 0..9 - quand on compte
for i, c in enumerate(t):      # l'indice et l'élément
while cond:  break  continue   # comme en C
def f(x, n=5):                 # valeur par défaut
    """Une phrase."""
    return a, b                # deux valeurs = un tuple ; a, b = f(...)
print(f"{nom} : {pop} hab")    # f-string
int("12")  float("3.5")  str(4)   # conversions explicites - tout ce qui vient d'un fichier est str
```

## Les structures

| | Créer | Lire | Écrire | Le reste |
| --- | --- | --- | --- | --- |
| **liste** | `[1, 2, 3]` | `t[0]`, `t[-1]`, `t[1:3]` (3 exclu) | `t.append(x)`, `t[i] = x` | `len(t)`, `x in t`, `t[::-1]` |
| **dictionnaire** | `{}` , `{"a": 1}` | `d["a"]`, `d.get("a", 0)` | `d["a"] = 1` | `"a" in d`, `d.items()`, `d.keys()` |
| **compréhension** | `[c["nom"] for c in t if c["alt"] > 500]` | | | boucle + filtre + liste, une ligne |

**Regrouper** - le motif : `d[cle] = d.get(cle, 0) + valeur`.

**Fichier CSV** : `with open(p, newline="") as f: lignes = list(csv.DictReader(f))`
puis convertir les nombres (`int`, `float`).

## Trier

```python
sorted(t)                                            # nouvelle liste ; t.sort() trie en place
sorted(t, key=lambda c: c["population"], reverse=True)
sorted(t, key=lambda c: (c["canton"], -c["population"]))   # deux critères
```

`sorted` est **stable** : les ex æquo gardent leur ordre - deux tris de
suite se composent.

| Tri | L'idée | Invariant après le tour i | Comparaisons pour n |
| --- | --- | --- | --- |
| **sélection** | le plus petit du reste, à sa place | `t[:i+1]` trié **et** plus petit que le reste | toujours n(n-1)/2 |
| **insertion** | glisser `t[i]` dans la partie triée | `t[:i+1]` trié | de n-1 (déjà trié) à n(n-1)/2 (inversé) |
| **fusion** | couper, trier chaque moitié, fusionner | - | environ n · log₂ n, quel que soit l'ordre |

**Chercher** dans une liste **triée** : la dichotomie - milieu, moitié,
milieu... au plus log₂ n étapes (30 pour un milliard). Sur une liste non
triée elle répond faux **sans erreur**. `bisect.bisect_left(t, x)` le fait
en Python.

## La récursion

```python
def f(n):
    if n <= 1:              # 1. le cas de base - D'ABORD
        return ...
    return ... f(n - 1)     # 2. l'appel, sur un problème plus petit
```

- chaque appel en attente occupe la **pile** : limite 1 000 par défaut
  (`sys.getrecursionlimit()`) - une liste de 1 000 éléments en récursif
  casse ;
- `fib(n) = fib(n-1) + fib(n-2)` recalcule : **2 692 537** appels pour
  `fib(30)`. Un dictionnaire des résultats (**mémoïsation**) : 59 ;
- **diviser pour régner** : couper en deux, résoudre chaque moitié,
  recombiner - tri fusion, dichotomie ;
- **explorer** ce qui est emboîté : « mur ou déjà vu ? je m'arrête ; sinon
  je marque et je vais voir les voisines ». Oublier de marquer =
  `RecursionError`.

**Tracer un appel** : une ligne par appel, indentée selon la profondeur,
ses arguments, puis ce qu'il renvoie. C'est le geste de l'évaluation.
