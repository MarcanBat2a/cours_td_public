# Mémo - Complexité

**UE 0 - Algo 3 avec Python · Chapitre 3**
Distribué en fin de séance 2 · à garder pour tout le module

## Les classes

| Classe | n = 1 000 | n = 10⁶ | n × 10 → | Exemple |
| --- | ---: | ---: | --- | --- |
| O(1) | 1 | 1 | × 1 | `t[i]`, `x in ensemble` |
| O(log n) | 10 | 20 | + 3 | dichotomie, `n // 2` en boucle |
| O(n) | 10³ | 10⁶ | × 10 | un parcours, `x in liste`, `sum` |
| O(n log n) | 10⁴ | 2 · 10⁷ | × 13 | tri fusion, `sorted` |
| O(n²) | 10⁶ | 10¹² | × 100 | deux boucles imbriquées, sélection, insertion |
| O(2ⁿ) | 10³⁰¹ | - | × 2 par élément | Fibonacci naïf, Hanoï |

**O(f(n))** : le terme qui domine, sans sa constante. Python fait
10⁷ à 10⁸ opérations simples par seconde : 10⁶ en un centième de
seconde, 10¹² en trois heures. En une seconde : n ≈ 3 000 en O(n²),
500 000 en O(n log n), 23 en O(2ⁿ).

## Lire le coût

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
| `t[i]`, `append`, `len` | 1 | | `x in liste` | n |
| `x in ensemble / dict` | 1 | | `insert(0, x)`, `pop(0)` | n |
| `d[k]`, `d.get(k)` | 1 | | `t[1:]`, `t + u`, `list(t)` | n |
| | | | `sorted`, `sort` | n log n |
| | | | `min`, `sum`, `index`, `count` | n |

**Un `in` liste dans une boucle : n².**

## Les récursions

| L'appel | Coût |
| --- | --- |
| `f(n - 1)`, travail constant | n |
| `f(n - 1)`, travail n (`t[1:]`) | n² |
| `f(n - 1)` deux fois | 2ⁿ (Fibonacci : 1,618ⁿ) |
| `f(n // 2)` | log n |
| `f(n // 2)` deux fois, travail n | n log n |

## Les tris du module

| Tri | Comparaisons | Meilleur | Pire |
| --- | --- | --- | --- |
| sélection | n(n-1)/2, toujours | n² | n² |
| insertion | ≈ n²/4 en moyenne | n (déjà trié) | n²/2 (inversé) |
| fusion | ≈ n · log₂ n | n log n | n log n |
| rapide (pivot en tête) | ≈ n log n | n log n | n² (déjà trié) |
| `sorted` (Timsort) | n log n | n (déjà trié) | n log n |

La classe qu'on annonce est celle du **pire** cas, sauf mention.

## Optimiser : deux gestes

| Symptôme | Remède | Avant → après |
| --- | --- | --- |
| `x in liste` dans une boucle | un `set` construit une fois | n² → n |
| doublons, paires qui font une somme | un ensemble des déjà vus | n² → n |
| la même somme d'intervalle, souvent | sommes de préfixes | q · n → n + q |
| la même recherche, souvent | trier une fois, dichotomie | q · n → n log n + q log n |
| un appel récursif recalculé | un dictionnaire (mémoïsation) | 2ⁿ → n |
| le même total recalculé par question | un dictionnaire (regrouper) | q · n → n + q |

**La méthode** : mesurer chaque partie, la plus lente d'abord, nommer la
cause, changer de structure ou précalculer, remesurer - **le résultat ne
doit pas changer**.
