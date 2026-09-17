# Mémo - Graphes

**UE 0 - Algo 3 avec Python · Chapitre 4**
Distribué en fin de séance 2 · le dernier du module

Les fonctions suivent les TD : `profondeur` renvoie l'ordre de visite ;
`largeur` et `dijkstra` ajoutent les parents aux exemples du cours et
renvoient `(dist, parent)`.

## Les mots

| Terme | En une ligne |
| --- | --- |
| **sommet, arête** | les choses, les liens ; n sommets, m arêtes |
| **degré** | le nombre d'arêtes d'un sommet ; en non orienté, la somme des degrés vaut 2m |
| **orienté** | les arêtes ont un sens (« a besoin de ») ; sinon, une route s'écrit deux fois |
| **pondéré** | un nombre sur chaque arête (des km, un prix) |
| **chemin, cycle** | une suite de sommets reliés ; un cycle simple revient au départ sans autre sommet répété |
| **connexe (non orienté)** | tout sommet est atteignable depuis n'importe lequel ; sinon, des composantes |
| **arbre** | non orienté, connexe et m = n - 1 : pas de cycle ; choisir une racine définit parents, feuilles et hauteur |
| **forêt** | un ou plusieurs arbres ; k composantes, m = n - k |

Cycles **indépendants** d'un graphe non orienté : m - n + k, avec k
composantes (m - n + 1 si connexe). Ce n'est pas le total des cycles simples.

## Ranger

```python
g = {"Isulacciu": {"Caldarella": 6, "Finosella": 14}}       # extrait : sommet → {voisin: poids}
g[a][b]                 # le poids, ou KeyError : O(1)
b in g[a]               # y a-t-il une arête ? O(1)
len(g[a])               # le degré
def voisins(g, s): return sorted(g[s])                       # dans un ordre fixe
```

| | Dictionnaire | Matrice n × n |
| --- | --- | --- |
| place | n + 2m | n² |
| parcourir les voisins sans tri | degré d de s | n |
| arête a-b ? | 1 | 1 |
| quand | presque toujours | graphe dense, calcul matriciel |

`voisins` trie : O(d log d) au pire. Accès aux dictionnaires : O(1) en
moyenne. Ici, 0 signifie « pas de route » dans la matrice car les km sont
strictement positifs ; pour des poids nuls, choisir un autre marqueur.

## Parcourir - n + m hors tri des voisins

```python
def profondeur(g, s):                      # une PILE : le dernier arrivé
    vus, ordre, pile = set(), [], [s]
    while pile:
        x = pile.pop()
        if x in vus: continue
        vus.add(x)
        ordre.append(x)
        for v in reversed(voisins(g, x)): pile.append(v)
    return ordre
```

```python
from collections import deque
def largeur(g, s):                         # une FILE : le premier arrivé
    dist, parent, file = {s: 0}, {s: None}, deque([s])
    while file:
        x = file.popleft()
        for v in voisins(g, x):
            if v not in dist:
                dist[v], parent[v] = dist[x] + 1, x
                file.append(v)
    return dist, parent
```

| | Profondeur | Largeur |
| --- | --- | --- |
| structure | pile (ou récursion, limite souvent à 1 000) | file (`deque`, `popleft` en O(1)) |
| donne | les sommets atteignables, l'ordre « s'enfoncer » | les mêmes, plus **les distances en étapes** et les parents |
| sert à | connexe ? composantes ; ordre avant/après (postfixe) | le plus court chemin **en étapes** |

Chemin : remonter les `parent` depuis l'arrivée, puis renverser.
L'arrivée doit figurer dans `parent` ; sinon, elle est inaccessible.
Avec `sorted`, ajouter Σ d(s) log d(s) au pire. Sur nos routes et grilles,
le degré est au plus 4 : les deux parcours restent O(n + m).
La pile explicite ci-dessus peut contenir des doublons : O(n + m) de
mémoire auxiliaire au pire. Les versions des slides utilisent O(n).

## L'arbre des parents

```python
def afficher(s, p=0):                      # PRÉFIXE : le sommet avant ses enfants
    print(" " * p + s)
    for e in enfants.get(s, []): afficher(e, p + 2)

def taille(s):                             # POSTFIXE : le sommet après ses enfants
    return 1 + sum(taille(e) for e in enfants.get(s, []))
```

Hauteur de l'arbre de largeur = la distance maximale. Ordre
d'installation, ordre des prérequis : un parcours en profondeur qui
ajoute le sommet **après** ses successeurs (postfixe), sur un graphe
orienté sans cycle.
Sens des flèches : élément → ses prérequis. Dans le sens inverse,
il faut renverser l'ordre obtenu.

## Dijkstra - le plus court en poids

```python
from heapq import heappop, heappush
INF = float("inf")
def dijkstra(g, s):
    dist = {x: INF for x in g}
    dist[s] = 0
    parent, tas = {s: None}, [(0, s)]
    while tas:
        d, x = heappop(tas)
        if d != dist[x]: continue          # ancienne proposition périmée
        for v, poids in g[x].items():
            nouveau = d + poids
            if nouveau < dist[v]:
                dist[v], parent[v] = nouveau, x
                heappush(tas, (nouveau, v))
    return dist, parent
```

- Comme dans les slides, les sommets inaccessibles restent à `INF` dans
  `dist`. Ils sont absents de `parent` (et de `dist` pour la largeur).
- Le départ et tous les voisins sont des clés du graphe. Poids finis,
  sommets comparables en cas d'égalité dans le tas : chaînes pour les
  communes, couples d'entiers pour les grilles.
- **Fixer la plus proche** est sûr parce que les poids sont positifs ou nuls ;
  jamais de poids négatif.
- Version naïve : `min` sur les restants à chaque tour, **n²**. Avec un
  tas : **(n + m) log n**. Chaque insertion ou retrait coûte O(log h)
  pour h entrées dans le tas, entrées périmées comprises.
- À la main : une colonne par sommet, une ligne par tour, la fixée
  entourée, ses voisines mises à jour par `min(actuelle, fixée + poids)`.

| n | n² | (n + m) log₂ n, m = 2n (arrondi) |
| ---: | ---: | ---: |
| 10³ | 10⁶ | 3 · 10⁴ |
| 10⁴ | 10⁸ | 4 · 10⁵ |
| 10⁶ | 10¹² | 6 · 10⁷ |

## Modéliser - quatre questions

1. **Les sommets** : quoi ?
2. **Les arêtes** : quelle relation ? un sens, ou deux ?
3. **Les poids** : lesquels, ou aucun ?
4. **La question** → l'algorithme :

| La question | L'algorithme | Coût |
| --- | --- | --- |
| atteignable ? en un seul morceau ? | profondeur ou largeur | n + m |
| le moins d'étapes | largeur | n + m |
| le moins cher, poids ≥ 0 | Dijkstra, avec un tas | (n + m) log n |
| dans quel ordre (dépendances sans cycle) | profondeur postfixe | n + m |

Coûts des parcours hors tri des voisins. Poids tous égaux et ≥ 0 : la
largeur suffit, pas de tas à payer.

## networkx - vérifier

```python
import networkx as nx                       # uv add networkx → pyproject.toml, uv.lock
G = nx.Graph(); G.add_edge(a, b, km=6)      # nx.DiGraph(dico) pour un orienté
G.number_of_nodes(), G.number_of_edges(), G.degree(s), list(G.neighbors(s))
nx.is_connected(G), [len(c) for c in nx.connected_components(G)]
nx.shortest_path(G, a, b)                                   # en étapes
nx.dijkstra_path(G, a, b, weight="km"), nx.dijkstra_path_length(G, a, b, weight="km")
nx.is_directed_acyclic_graph(D)                            # vérifier l'absence de cycle
list(reversed(list(nx.topological_sort(D))))               # flèches « dépend de »
```
