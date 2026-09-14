# Mémo - Python, les tris, la récursion

**UE 0 - Algo 3 avec Python · Chapitre 2**
À garder pour les TD et les révisions. Les coûts seront étudiés au chapitre 3.

## Conditions, boucles et fonctions

```python
if n > 1000:
    taille = "ville"
elif n > 100:
    taille = "village"
else:
    taille = "hameau"

for i, valeur in enumerate(t):
    if valeur < 0:
        continue
    print(i, valeur)

while n > 1:
    n = n // 2

def extremes(t):
    return min(t), max(t)
```

`for x in t` donne les éléments ; `enumerate(t)` ajoute leur indice.
`range(5)` donne 0 à 4. `break` sort de la boucle ; `continue` passe
au tour suivant. `and`, `or`, `not` combinent les conditions.
`//` est la division entière, `%` le reste, `==` teste l'égalité.
Un bloc suit `:` et s'indente ; on utilise quatre espaces.
`return` fournit le résultat ; une fonction sans retour explicite renvoie `None`.

## Listes et dictionnaires

| Structure | Écrire | Lire / parcourir |
| --- | --- | --- |
| Liste | `t = [1, 2, 3]`, `t.append(4)`, `t[0] = 7` | `t[-1]`, `t[1:3]`, `len(t)`, `x in t` |
| Dictionnaire | `d = {}`, `d["Littoral"] = 1840` | `d[cle]`, `d.get(cle, 0)`, `d.items()` |

`t[a:b]` : borne basse incluse, haute exclue ; une tranche de liste
crée une nouvelle liste. `t[::-1]` en donne une copie inversée.
Une clé de dictionnaire doit être **hachable** : chaîne, entier,
ou tuple d'éléments hachables ; une liste ne convient pas.

```python
hauts = [c["nom"] for c in communes if c["altitude"] > 500]
for c in communes:
    totaux[c["canton"]] = totaux.get(c["canton"], 0) + c["population"]
```

Initialiser `totaux = {}` avant la boucle. Avec `csv.DictReader` dans
ces TD, les valeurs des colonnes sont des chaînes : convertir les
nombres avec `int` ou `float` lors du chargement.

## Trier et chercher

```python
sorted(t)                 # nouvelle liste ; t reste inchangée
t.sort()                  # modifie t ; renvoie None
sorted(communes, key=lambda c: (c["canton"], -c["population"]))
```

Un tri **stable** conserve l'ordre initial des éléments de même clé.
Pour deux tris successifs : critère secondaire d'abord, principal ensuite.

| Tri | Le geste | Ce qui est vrai après un tour |
| --- | --- | --- |
| Sélection | placer le minimum restant | préfixe trié, éléments ≤ à ceux du reste |
| Insertion | glisser l'élément dans le préfixe trié | préfixe trié, susceptible de changer ensuite |
| Fusion | trier chaque moitié, puis fusionner | les deux listes reçues par `fusion` sont triées |

La **dichotomie** exige une liste triée. Les bornes se resserrent autour
du milieu testé. Sur une liste non triée, le résultat n'est pas garanti.
`bisect_left(t, x)` renvoie un point d'insertion `i`. Pour tester la
présence : `i < len(t) and t[i] == x`.

## Écrire une récursion

Avant le code : **entrées autorisées, résultat, cas de base, progression**.

```python
def somme(t):
    if not t:                    # liste vide : arrêt
        return 0
    return t[0] + somme(t[1:])    # liste plus courte
```

`somme([2, 3])` attend `somme([3])`, qui attend `somme([])`.
Les retours remontent dans l'ordre inverse : **0, puis 3, puis 5**.
Chaque appel en attente occupe un cadre de pile. La limite courante
se lit avec `sys.getrecursionlimit()` ; son dépassement provoque
`RecursionError`. Le seuil exact dépend de l'environnement.

**Tri fusion : cas de base zéro ou un élément.**
Tester liste vide, singleton, doublons et négatifs ; vérifier le résultat
et la conservation de l'entrée quand le contrat l'exige.
