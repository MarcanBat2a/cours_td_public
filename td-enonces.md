# TD - Graphes

**UE 0 - Algo 3 avec Python · Chapitre 4**
Marcu-Andria Battesti · Bachelor CLIC · 2026-2027

> Neuf travaux dirigés sur trois séances, sur machine sauf mention. Dans
> `algo3/` (le projet uv du chapitre 1), avec `uv run`, un dossier
> `chapitre4/` avec le **contenu** de `manip/` copié à côté de vos
> programmes. Pas encore de projet `algo3/` : `uv init --no-package algo3`,
> puis `cd algo3`.
>
> Dans `manip/`, rien à apporter des chapitres précédents : `routes.csv`,
> les 32 routes entre les 24 communes du module, avec leur longueur en
> kilomètres ; `communes.py`, les 24 communes ; `labyrinthe.txt`, celui du
> chapitre 2 ; `chrono.py`, celui du chapitre 3 ; `grilles.py`, qui
> fabrique des graphes de la taille qu'on veut ; `dependances.py`, ce
> qu'uv installe au chapitre 1.
>
> Les fonctions qui resservent d'un TD à l'autre (`charger_routes`,
> `voisins`, `km`, `profondeur`, `largeur`, `chemin`, `dijkstra`...) vont
> dans un fichier `graphes.py` ; vos essais dans `td1.py`, `td2.py`..., qui
> commencent par `from graphes import ...`. Depuis `chapitre4/` :
> `uv run td1.py`.
> Les imports nécessaires aux fonctions (`csv`, `deque`, `heappop`, `heappush`) et
> `INF = float("inf")` vont aussi dans `graphes.py`. Dans chaque script
> d'essai, rechargez `g` et recalculez les résultats utilisés : les
> variables de `td1.py` ne sont pas partagées automatiquement avec `td2.py`.
>
> **Le pronostic avant la mesure**, sur la fiche. Les temps varient d'un
> poste à l'autre ; comparez surtout les rapports et leur tendance.
>
> **★** : les questions dont la réponse doit tenir en une phrase juste ou
> un calcul propre.
>
> **Bonus** : pour qui a fini avant la correction ; sinon en
> démonstration, ou chez soi. Aucune étape de la suite n'en dépend.

Le [cours Google Slides](https://docs.google.com/presentation/d/1DY6Ydij2eapXi6QLVJx4quNBKjpL9AeifFiobzH4SA0/edit)
présente les algorithmes sur un petit graphe. Les TD les appliquent aux
routes et ajoutent les informations nécessaires pour retrouver les chemins :

| Fonction | Dans les slides | Dans les TD et le mémo |
| --- | --- | --- |
| `profondeur` | liste des sommets dans l'ordre de visite, avec récursion | même résultat, avec une pile explicite au TD 4 |
| `largeur` | liste des sommets dans l'ordre de visite | `(dist, parent)` au TD 5 : distances en étapes et prédécesseurs du chemin |
| `dijkstra` | dictionnaire des distances en poids | `(dist, parent)` au TD 8 : mêmes distances, plus les prédécesseurs du chemin |

Pour `largeur`, seuls les sommets atteignables figurent dans `dist`.
Pour Dijkstra, tous les sommets y figurent et les inaccessibles restent
à `INF`, comme dans les slides. Dans les deux cas, `parent` contient
seulement les sommets atteignables, avec `None` pour le départ.

---

# Séance 1 - Voir, ranger, vérifier

# TD 1 - Trois situations

**Sur papier, puis sur machine**

## Étape 1 - Un canton *(sur papier)*

Dans `routes.csv`, les routes dont les deux communes sont du canton
**Plateau** (Bucchiniccia, Erbaghjolu, Ghjuncaghju, Ortoli, Scandulaghju,
Ulmetu Vecchiu).

1. Dessinez-les : un point par commune, un trait par route, la longueur
   sur le trait. Gardez le dessin : il sert au TD 7.
2. Le degré de chaque commune (son nombre de routes).
3. ★ Six communes, combien de routes ? Pour les relier toutes sans
   cycle, combien en faudrait-il ? Combien de routes y a-t-il en plus ?

## Étape 2 - Deux autres situations *(sur papier)*

Le labyrinthe du chapitre 2 (`labyrinthe.txt`) et ce qu'uv installe
(`dependances.py`).

| Situation | Sommets | Arêtes | Orienté ? | Pondéré ? | La question qu'on pose |
| --- | --- | --- | --- | --- | --- |
| les routes | les communes | les routes | non | oui, km | |
| le labyrinthe | | | | | |
| les paquets | | | | | |

1. Remplissez les cinq premières colonnes.
2. ★ La dernière colonne : pour chaque situation, la question qu'on
   voudrait poser au graphe. Une phrase chacune.
3. ★ Pourquoi les dépendances sont-elles orientées et pas les routes ?
   Donnez une situation de routes qui devrait l'être.

## Étape 3 - Lire le fichier *(sur machine)*

```python
import csv
with open("routes.csv", encoding="utf-8") as f:
    routes = [(l["depart"], l["arrivee"], int(l["km"])) for l in csv.DictReader(f)]
```

1. Combien de routes ? Combien de communes distinctes y apparaissent ?
   Les 24 du module y sont-elles toutes (`communes.py`) ?
2. Pour chaque commune, le nombre de routes qui la touchent, sans autre
   structure qu'un dictionnaire de compteurs. Laquelle en a le plus ?
3. ★ Deux communes n'ont qu'une route. Lesquelles ? Que peut-on
   soupçonner, sans encore pouvoir le prouver ?

---

# TD 2 - Construire

**Sur machine**

## Étape 1 - Le dictionnaire

`charger_routes(chemin)` renvoie un dictionnaire commune → {voisine :
km}. Une route non orientée s'écrit dans les deux sens.
Dans les slides, `g[s]` est une liste de voisins pour le graphe non
pondéré, puis un dictionnaire voisin → poids pour le graphe pondéré.
Nous utilisons cette seconde forme : `for v in g[s]` parcourt ses clés,
donc les voisins ; `g[s].items()` donne aussi les poids.

1. Écrivez-la. `g["Isulacciu"]` ? `len(g)` ?
2. `degre(g, s)` en une ligne. Le degré maximal, le minimal, la somme
   de tous les degrés.
3. ★ La somme des degrés vaut le double du nombre de routes. Pourquoi,
   toujours ?

## Étape 2 - La matrice, et sa place

L'autre rangement : les communes dans l'ordre alphabétique, numérotées de
0 à 23, et `m[i][j]` = la longueur de la route entre i et j, 0 sinon.
Les routes du fichier ont des poids strictement positifs : 0 peut donc
désigner une absence de route. Sans la construire :

1. Combien de cases ? Combien de non nulles ? Et dans `g` : combien de
   clés, combien de voisines rangées en tout ?
2. ★ Place occupée par les deux rangements, en fonction de n et m. Pour
   les 36 000 communes de France et leurs 100 000 routes : combien de
   cases pour la matrice ? Quand la matrice vaut-elle le coup ?

## Étape 3 - Trois fonctions

1. `voisins(g, s)` : les voisines de `s`, **dans l'ordre alphabétique**.
   Tout le chapitre l'utilise : chacun doit visiter dans le même ordre.
   Avec `sorted`, trier d voisines coûte O(d log d) au pire ; les
   parcourir sans les trier coûte O(d).
2. `existe_route(g, a, b)` et `km(g, a, b)`. Coût de chacune ?
3. ★ `dependances.py` : `DEPEND_DE["requests"]` se lit en O(1). Qui a
   besoin de `mdurl` ? Écrivez `depend_de_moi(dep, p)` : son coût, et le
   dictionnaire à construire une fois pour répondre en O(1).

## Bonus - Construire la matrice

1. Construisez `m` depuis `g`. Vérifiez vos deux comptes de l'étape 2.
2. `voisins_matrice(m, i)` : la liste des j tels que `m[i][j] > 0`. Son
   coût, en fonction de n ? Celui d'un parcours de `g[s]`, sans tri ?

---

# TD 3 - La bibliothèque

**Sur machine**

## Étape 1 - Installer, épingler

Dans `algo3/` :

```bash
uv add networkx
uv tree
grep -A1 'name = "networkx"' uv.lock
```

1. Ce que `uv add` a écrit dans `pyproject.toml`, et ce que `uv.lock` a
   noté. Un commit des deux.
2. `uv tree` : combien de dépendances sous `networkx` ? Comparez avec
   `requests` au chapitre 1.
3. ★ Pourquoi commiter `uv.lock`, en une phrase - celle du chapitre 1.

## Étape 2 - Le même graphe

```python
import networkx as nx
from dependances import DEPEND_DE
from graphes import charger_routes

g = charger_routes("routes.csv")
G = nx.Graph()
G.add_nodes_from(g)
for a in g:
    for b, d in g[a].items():
        G.add_edge(a, b, km=d)
```

Chaque route est lue deux fois ; `nx.Graph` conserve une seule arête
non orientée entre a et b.

1. `G.number_of_nodes()`, `G.number_of_edges()`. Les mêmes qu'au TD 1 ?
2. `G.degree("Ulmetu Vecchiu")`, `sorted(G.neighbors("Isulacciu"))`,
   `G["Isulacciu"]["Caldarella"]["km"]`. Comparez à vos fonctions du TD 2,
   sur trois communes.
3. `D = nx.DiGraph(DEPEND_DE)`. `D.out_degree("requests")`,
   `D.in_degree("mdurl")`, `list(D.predecessors("mdurl"))`. Retrouvez
   votre `depend_de_moi`.

## Étape 3 - Une question

Un graphe non orienté est **connexe** si un chemin relie toute paire
de sommets. Une **composante connexe** est un groupe maximal de sommets
reliés entre eux ; aucun chemin ne le relie aux autres composantes.

1. `nx.is_connected(G)`. Puis `[len(c) for c in nx.connected_components(G)]`.
2. ★ La bibliothèque répond en une ligne. Le TD 4 vous fera écrire ce
   qu'elle a fait pour répondre. Sans le savoir encore : comment
   prouveriez-vous que deux communes ne sont reliées à rien d'autre ?

## Bonus - La densité

`nx.density(G)` : la part des paires de communes reliées par une route.
Recalculez-la à la main : m divisé par le nombre de paires.

---

# Séance 2 - Parcourir

# TD 4 - En profondeur

**Sur machine**

## Étape 1 - Récursif

On reprend la récursion du cours en passant explicitement `vus` et
`ordre` à la fonction `explorer`. Après sa définition, appelez-la avec
un ensemble et une liste vides : elle les remplit, sans les renvoyer.

```python
def explorer(g, s, vus, ordre):
    if s in vus:
        return
    vus.add(s)
    ordre.append(s)
    for v in voisins(g, s):
        explorer(g, v, vus, ordre)
```

1. Depuis Isulacciu : l'ordre de visite, les huit premières communes.
   Combien de communes atteintes ? Lesquelles manquent ?
2. Depuis Diavulinu ? Depuis Ortoli ?
3. ★ Ce que `vus` empêche. Mettez les deux premières lignes d'`explorer`
   en commentaire, le temps d'un essai : que dit Python, et pourquoi ?

## Étape 2 - Avec une pile

```python
def profondeur(g, s):
    vus, ordre, pile = set(), [], [s]
    while pile:
        x = pile.pop()
        if x in vus:
            continue
        vus.add(x)
        ordre.append(x)
        for v in reversed(voisins(g, x)):
            pile.append(v)
    return ordre
```

1. Depuis Isulacciu : même ensemble qu'à l'étape 1 ? Même ordre ?
2. `from grilles import grille` ; `g50 = grille(50)` (2 500 sommets).
   `explorer(g50, (0, 0), set(), [])` : que dit Python ? Et
   `profondeur(g50, (0, 0))` ?
3. ★ Pourquoi la pile fait-elle le même travail que la récursion, sans
   sa limite ? (Le chapitre 2 a donné la limite.)

## Étape 3 - Le labyrinthe, et la classe

1. `labyrinthe.txt` en graphe : un sommet par case libre `(i, j)`, une
   arête entre deux cases libres voisines. Combien de sommets ? D'arêtes ?
2. `profondeur` depuis la case `D`. Combien de cases atteintes ? Lesquelles
   manquent ? (Le bonus « Le labyrinthe » du chapitre 2 posait la même
   question.)
3. ★ La classe de `profondeur`, en lisant son code : combien de fois
   chaque sommet est-il marqué ? Chaque arête regardée ?
   Distinguez le parcours du tri dans `voisins` : le degré est au plus
   4 sur les routes et les grilles de ce chapitre, mais peut grandir
   dans un autre graphe.

## Bonus - Au chronomètre

`from chrono import chrono`, puis `chrono(profondeur, grille(k), (0, 0))`
pour k = 100, 200, 400 (10 000, 40 000, 160 000 sommets). Le rapport quand
n × 4 ? Confirme-t-il la classe de l'étape 3 ?

---

# TD 5 - En largeur

**Sur machine**

## Étape 1 - La file

La largeur du cours renvoie l'ordre de visite. Ici, on mémorise aussi
la distance en étapes et le parent qui permettra de retrouver un chemin.
`dist` remplace `vus` : un sommet y entre dès son ajout dans la file.
La fonction renvoie donc deux dictionnaires : `dist, parent = largeur(g, s)`.

```python
from collections import deque

def largeur(g, s):
    dist, parent, file = {s: 0}, {s: None}, deque([s])
    while file:
        x = file.popleft()
        for v in voisins(g, x):
            if v not in dist:
                dist[v] = dist[x] + 1
                parent[v] = x
                file.append(v)
    return dist, parent
```

1. Depuis Isulacciu : les communes à 1 étape, à 2, à 3. La plus
   lointaine, en étapes.
2. L'ordre de visite (ajoutez une liste `ordre`). Comparez aux huit
   premières du TD 4 : ce qui change, et pourquoi.
3. ★ Une pile visite « le dernier arrivé », une file « le premier
   arrivé ». Pourquoi est-ce la file qui donne les distances ?

## Étape 2 - Le chemin

`chemin(parent, s)` : remonter de `s` à la racine par les parents, et
renverser. On l'appelle seulement si `s in parent` ; sinon, le sommet
est inaccessible et aucun chemin ne peut être reconstruit.

1. Le chemin d'Isulacciu à Scandulaghju. Combien d'étapes ?
2. Sa longueur en kilomètres, avec `km(g, a, b)` du TD 2.
3. ★ Est-ce le chemin le plus court en kilomètres ? Regardez les
   kilomètres de chaque étape : laquelle pèse le plus ? Cherchez à la
   main, dans `g`, un chemin qui l'évite. Gardez la question pour la
   séance 3.

## Étape 3 - Vérifier

1. `nx.shortest_path(G, "Isulacciu", "Scandulaghju")` : le même chemin ?
   `nx.single_source_shortest_path_length(G, "Isulacciu")` : les mêmes
   distances que votre `dist` ?
2. ★ Une liste avec `pop(0)` à la place de la `deque` avec `popleft()` :
   quel coût caché du chapitre 3 ? Pourquoi `deque` ?

## Bonus - Au chronomètre

`chrono(largeur, grille(k), (0, 0))` pour k = 100, 200, 400. Rapports,
classe. La même mesure pour `profondeur` : lequel des deux parcours est
le plus rapide ?

---

# TD 6 - L'arbre

**Sur machine**

## Étape 1 - L'arbre des parents

Les `parent` du TD 5, depuis Isulacciu, retournés : `enfants[p]` = la
liste des sommets dont le parent est `p`.
Dans `td6.py`, rechargez les routes et recalculez
`_, parent = largeur(g, "Isulacciu")`. Construisez `enfants` et gardez
les fonctions `afficher`, `taille` et `hauteur` dans ce même fichier :
elles utilisent ce dictionnaire.

Dans cet arbre, **Isulacciu est la racine**. Chaque autre sommet a un
parent, ses enfants sont les sommets découverts depuis lui. Sa
**profondeur** est le nombre d'arêtes depuis la racine. Une **feuille**
n'a pas d'enfant ; la **hauteur** de l'arbre est la profondeur maximale.

1. `afficher(s, niveau)` : `s` indenté de `niveau` espaces, puis ses
   enfants, à `niveau + 2`. Lancez depuis Isulacciu. C'est un parcours
   **préfixe**.
2. Les feuilles : les sommets sans enfant. Combien ? La hauteur : la
   profondeur maximale. Quelle valeur du TD 5 retrouvez-vous ?
3. ★ Pourquoi cette structure est-elle un arbre ? Trois mots : sommets,
   arêtes, cycle. Comptez les arêtes.

## Étape 2 - Postfixe

Un traitement **préfixe** se fait avant les appels aux enfants ; un
traitement **postfixe** se fait après leur retour. Pour calculer une
taille ou une hauteur, il faut d'abord les résultats des enfants.

1. `taille(s)` : le nombre de sommets du sous-arbre de `s` - 1 plus la
   somme des tailles des enfants. `taille("Isulacciu")`,
   `taille("Finosella")`, `taille("Acquaviva")`.
2. `hauteur(s)` : 0 pour une feuille, sinon 1 plus la plus grande hauteur
   d'un enfant.
3. ★ `compter_cases(i, j)` du labyrinthe (bonus du chapitre 2) : 0 pour
   un mur ou une case déjà vue, sinon 1 plus la somme des quatre appels
   voisins. Préfixe ou postfixe ? Pourquoi `afficher` est l'un et `taille`
   l'autre ?

## Étape 3 - Est-ce un arbre ?

Un graphe non orienté est un arbre s'il est connexe et a exactement
n - 1 arêtes. Pour un graphe connexe, m - n + 1 compte les **cycles
indépendants**, pas tous les cycles que l'on peut dessiner.

1. Le canton Plateau du TD 1 : n, m, arbre ou pas ? Combien de cycles
   indépendants ? Montrez-en deux sur le dessin, puis un troisième cycle
   obtenu en combinant les deux premiers.
2. ★ `DEPEND_DE` : orienté, sans cycle. Combien de sommets, d'arêtes ?
   En oubliant le sens des flèches, est-ce un arbre ? Combien de
   composantes ? Dans le graphe orienté, combien de racines (paquets
   dont personne ne dépend) ? Le mot qui convient à plusieurs arbres.

## Bonus - Les cycles du labyrinthe

Les 43 cases atteintes depuis `D` (TD 4), et les arêtes entre elles.
Arbre ? Combien de cycles indépendants ? Trouvez-les sur la grille.

---

# Séance 3 - Le plus court chemin

# TD 7 - Le plus court en kilomètres

**Sur papier, puis sur machine**

## Étape 1 - À la main *(sur papier)*

Le canton Plateau du TD 1, depuis **Ortoli**. Un tableau : une colonne par
commune, une ligne par tour.

1. Tour 0 : Ortoli à 0, les autres à ∞. À chaque tour : la commune non
   fixée la plus proche est **fixée** (entourez-la) ; ses voisines non
   fixées reçoivent `min(actuelle, fixée + km)`.
2. L'ordre dans lequel les six communes sont fixées, et leur distance.
   Deux ont la même : laquelle fixer d'abord ? Est-ce grave ?
3. ★ Pourquoi la commune la plus proche peut-elle être fixée sans risque ?
   Que faudrait-il pour que ce soit faux ?

## Étape 2 - En Python *(sur machine)*

Comme dans les slides : le départ et tous les voisins sont des clés
de `g`, et les poids sont finis et positifs ou nuls. On ajoute `parent`
pour reconstruire un chemin, comme au TD 5.

```python
INF = float("inf")

def dijkstra_naif(g, s):
    dist = {x: INF for x in g}
    dist[s] = 0
    parent, restants = {s: None}, set(g)
    while restants:
        x = min(restants, key=lambda y: dist[y])
        if dist[x] == INF:
            break
        restants.remove(x)
        for v, km in g[x].items():
            if dist[x] + km < dist[v]:
                dist[v] = dist[x] + km
                parent[v] = x
    return dist, parent
```

1. Depuis Isulacciu : les cinq autres communes les plus proches en km, la plus
   lointaine. Comparez à la plus lointaine en étapes (TD 5).
2. Deux communes restent à `INF`. Lesquelles ? Que signifie le `break` ?
3. ★ n tours, un `min` sur `restants` à chaque tour : la classe ?

## Étape 3 - Deux plus courts *(sur machine)*

1. `chemin(parent, "Scandulaghju")` : les communes, le nombre d'étapes,
   les kilomètres. À côté, le chemin du TD 5.
2. `nx.dijkstra_path(G, "Isulacciu", "Scandulaghju", weight="km")` et
   `nx.dijkstra_path_length(...)`. Les mêmes ?
3. ★ Deux chemins, deux « plus courts ». Une phrase pour chacun : plus
   court en quoi, trouvé par quel algorithme. Dans quelle situation
   veut-on l'un, dans quelle situation l'autre ?

---

# TD 8 - La file de priorité

**Sur machine**

## Étape 1 - heapq

Une **file de priorité** retire l'entrée de plus petite priorité.
`heapq` la représente par un **tas** dans une liste Python : `heappush`
ajoute une entrée, `heappop` retire la plus petite. Ici, les entrées sont
des couples `(distance, sommet)`.

```python
import heapq
tas = []
for d, s in [(14, "Finosella"), (6, "Caldarella"), (22, "Petralba"), (6, "Bracciolu")]:
    heapq.heappush(tas, (d, s))
while tas:
    print(heapq.heappop(tas))
```

1. L'ordre de sortie. Deux entrées à 6 : laquelle sort d'abord, et
   pourquoi ?
2. ★ Insérer et retirer le minimum coûtent log n dans un tas. Sur une
   liste, retirer le minimum coûte combien ?

## Étape 2 - Dijkstra avec un tas

C'est la version des slides, complétée par `parent`. Elle garde les
sommets inaccessibles à `INF`, comme `dijkstra_naif`.
En cas d'égalité, le tas compare les sommets : les noms de communes
(chaînes) et les cases des grilles (couples d'entiers) le permettent.

```python
from heapq import heappop, heappush

def dijkstra(g, s):
    dist = {x: INF for x in g}
    dist[s] = 0
    parent, tas = {s: None}, [(0, s)]
    while tas:
        d, x = heappop(tas)
        if d != dist[x]:
            continue
        for v, poids in g[x].items():
            nouveau = d + poids
            if nouveau < dist[v]:
                dist[v] = nouveau
                parent[v] = x
                heappush(tas, (nouveau, v))
    return dist, parent
```

1. Depuis Isulacciu : les mêmes distances que la version naïve ? Vérifiez
   avec `dist_tas == dist_naif`, y compris les communes à `INF`.
2. Une commune peut entrer plusieurs fois dans le tas. Pourquoi ? Que fait
   `if d != dist[x]: continue` ?
3. `chrono` des deux versions (`from chrono import chrono`) sur
   `grille(k)`, k = 15, 30, 60. Les rapports quand n × 4, pour chacune.
   À k = 60, le rapport entre les deux.

## Étape 3 - Jusqu'où

1. Le tableau : pour n = 10⁴ puis 10⁶ sommets et m = 2n arêtes, le
   nombre d'opérations de n² et de (n + m) log₂ n.
2. ★ Jusqu'à quel n la version naïve reste-t-elle acceptable (une
   seconde) ? Partez de votre mesure à k = 60. Pourquoi étudier cette
   version malgré son coût ?

## Bonus 1 - heapq au chronomètre

`heappush` puis `heappop` sur 100 000 entrées : `chrono`. Puis `min` +
`remove` sur une liste de 100 000, mille fois seulement. Rapport ?

## Bonus 2 - Pousser le tas

La version tas seule, k = 60, 120, 240 (jusqu'à 57 600 sommets). Rapports.
La naïve à k = 120 : pronostic, sans la lancer.

---

# TD 9 - Modéliser

**Sur machine, puis sur papier**

## Partie A - Deux questions, deux parcours *(sur machine)*

1. **Le labyrinthe.** Depuis `D`, la case la plus éloignée en nombre de
   pas, et le chemin pour y aller. Quel parcours ? Pourquoi pas l'autre ?
2. **Les paquets.** L'ordre dans lequel uv doit installer les neuf
   paquets de `DEPEND_DE` pour que chacun arrive **après** ce dont il a
   besoin. Ce graphe n'a pas de cycle. Écrivez `ordre_installation(dep)` :
   un parcours en profondeur qui ajoute un paquet à la liste **après**
   avoir traité ses dépendances.
   Comparez à `list(reversed(list(nx.topological_sort(D))))` : les ordres
   peuvent différer, mais doivent respecter chaque dépendance.
   ★ Préfixe ou postfixe, et pourquoi ?

## Partie B - Sur papier ★

Pour chaque situation : les sommets, les arêtes (orientées ?), les poids
(lesquels ?), la question, l'algorithme, sa classe.

1. ★ Les salles d'un bâtiment et leurs portes. On cherche la sortie la
   plus proche, en nombre de portes à franchir.
2. ★ Les vols entre aéroports, avec leur prix. On cherche le trajet le
   moins cher entre deux villes, escales comprises.
3. ★ Les modules d'un bachelor et leurs prérequis. On cherche un ordre
   pour les suivre.
4. ★ Un réseau routier de 10⁶ carrefours et 3 · 10⁶ routes. Le plus
   court chemin en km : combien d'opérations avec un tas ? Sans ? Et si
   toutes les routes faisaient un kilomètre ?

## Bonus - Les secours

La préfecture place un centre de secours dans une commune : celle dont la
commune **la plus lointaine** (en km) est la moins lointaine. Dijkstra
depuis chacune des 22 communes de la composante d'Isulacciu, en limitant
aussi les destinations à cette composante. Les deux autres communes
restent à `INF` : les inclure dans le maximum rendrait tous les candidats
ex æquo à l'infini. Laquelle choisir ? Quel coût total, en fonction de
n et m ?
