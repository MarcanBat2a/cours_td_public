# Mémo - Complexité

**UE 0 - Algo 3 avec Python · Chapitre 3**
Distribué en fin de séance 2 · à garder pour tout le module

## Les classes

| Classe | n = 1 000 | n = 10⁶ | n × 10 → | Exemple |
| --- | ---: | ---: | --- | --- |
| O(1) | 1 | 1 | × 1 | `t[i]`, `x in ensemble` en moyenne |
| O(log n) | 10 | 20 | + 3,32 environ | dichotomie, `n // 2` en boucle |
| O(n) | 10³ | 10⁶ | × 10 | un parcours, `x in liste`, `sum` |
| O(n log n) | 10⁴ | 2 · 10⁷ | facteur 10 log₂(10n) / log₂ n | tri fusion, `sorted` au pire |
| O(n²) | 10⁶ | 10¹² | × 100 | n × n comparaisons, sélection, insertion au pire |
| O(2ⁿ) | 10³⁰¹ | - | facteur 2⁹ⁿ | Hanoï, borne pour Fibonacci naïf |

**n** est la taille étudiée. **O(f(n))** est une borne supérieure : pour
n assez grand, le coût ne dépasse pas une constante fois f(n). On cherche
une borne précise : `3n² + 5n + 2` est en O(n²). O(1) ne signifie pas
une seule instruction. Les constantes restent utiles pour les temps réels.
Le tableau évalue les fonctions de référence, avec log en base 2 et des
valeurs arrondies. Pour n log n, le facteur est environ 13,3 de 1 000 à
10 000, mais 11,7 de 10⁶ à 10⁷. Pour 2ⁿ, **un seul élément de plus**
double le modèle. Mesurer la cadence sur le poste avant d'estimer des secondes.

## Lire le coût

Compter les tours et le travail par tour. Deux boucles **successives**
de n tours font 2n tours, donc O(n) si chaque tour coûte O(1).
Si le travail varie d'un tour à l'autre, additionner les coûts.
Dans les exemples suivants, `...` représente un travail constant.

```python
for x in t: ...                    # n
for x in t:                        # n²
    for y in t: ...
for i in range(n):                 # n²/2 → n²
    for j in range(i): ...
while n > 1: n = n // 2            # log n
```

| Caché | Coût | | Caché | Coût |
| --- | --- | --- | --- | --- |
| `t[i]`, `len` | 1 | | `x in liste` | n au pire |
| `append` | 1 amorti | | `insert(0, x)`, `pop(0)` | n |
| `x in ensemble / dict`, `d[k]`, `d.get(k)` | 1 en moyenne | | `t[1:]`, `list(t)` | n |
| | | | `t + u` | len(t) + len(u) |
| | | | `sorted`, `sort` | n log n au pire |
| | | | `min`, `sum`, `index`, `count` | n |

**q recherches dans n éléments : O(qn) au pire en liste.** Construire
un ensemble une fois, puis rechercher : O(n + q) en moyenne. `append`
est amorti : un agrandissement ponctuel coûte plus cher, mais son coût
se répartit sur une série d'ajouts. Comparaisons et hachages supposés O(1).

## Les récursions

| L'appel | Coût |
| --- | --- |
| `f(n - 1)`, travail constant | n |
| `f(n - 1)`, travail n (`t[1:]`) | n² |
| `f(n - 1)` deux fois, travail propre constant, sans mémoire | 2ⁿ |
| Fibonacci naïf : `f(n-1) + f(n-2)` | environ 1,618ⁿ |
| `f(n // 2)`, travail propre constant | log n |
| `f(n // 2)` deux fois, travail n | n log n |

## Les tris du module

| Tri | Comparaisons | Meilleur | Pire |
| --- | --- | --- | --- |
| sélection | n(n-1)/2, toujours | n² | n² |
| insertion | ≈ n²/4 en moyenne | n (déjà trié) | n²/2 (inversé) |
| fusion | ≈ n · log₂ n | n log n | n log n |
| rapide (pivot en tête) | de l'ordre de n log n en moyenne | n log n | n² (déjà trié) |
| `sorted` (Timsort) | n log n | n (déjà trié) | n log n |

La classe qu'on annonce est celle du **pire** cas, sauf mention.
O ne signifie pas « pire cas ». Les coûts des ensembles et dictionnaires
sont ici **moyens**, ceux d'`append` sont **amortis**.

## Optimiser : deux gestes

| Symptôme | Remède | Avant → après |
| --- | --- | --- |
| q recherches dans une liste de n éléments | un `set` construit une fois | q · n → n + q en moyenne |
| détecter des doublons, chercher une paire de somme donnée | un ensemble des déjà vus | n² → n en moyenne |
| la même somme d'intervalle, souvent | sommes de préfixes | q · n → n + q |
| la même recherche, souvent | trier une fois, dichotomie | q · n → n log n + q log n |
| Fibonacci naïf | un dictionnaire (mémoïsation) | exponentiel → O(n) appels |
| le même total recalculé par question | un dictionnaire (regrouper) | q · n → n + q en moyenne |

Préfixes : `[3, 5, 2]` donne `[0, 3, 8, 10]`. La somme de `t[1:3]`
vaut `10 - 3 = 7`. Construction O(n), mémoire O(n), puis O(1) par somme.
La rentabilité dépend du nombre et de la longueur des requêtes.
Pour toute mémoïsation, compter les sous-problèmes distincts et leur
travail : la complexité ne devient pas automatiquement linéaire.

**La méthode** : mesurer chaque partie, la plus lente d'abord, nommer la
cause, changer de structure ou précalculer, remesurer - **le résultat ne
doit pas changer**.


Pour comparer Fibonacci naïf et mémoïsé (TD 8), commencer chaque mesure
indépendante par `memo.clear()` et `appels = 0`. Un second appel sur une
valeur déjà mémorisée mesure une réutilisation, pas une première résolution.
La puissance rapide du TD 5 fait un nombre logarithmique d'appels : le
résultat de l'appel sur n // 2 doit être calculé une fois et conservé.
