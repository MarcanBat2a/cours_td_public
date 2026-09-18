# TD - Graphes

**UE 0 - Algo 3 avec Python · Chapitre 4**
Marcu-Andria Battesti · Bachelor CLIC · 2026-2027

Neuf TD sur trois séances. Chaque TD contient deux ou trois étapes.
Le paragraphe **Résultat attendu** indique ce que vous devez présenter à
la correction. Les bonus sont facultatifs ; la suite n'en dépend pas.

## Préparer les fichiers

Ouvrez votre projet `algo3/`. Si vous ne l'avez pas encore, créez-le avec
`uv init --no-package algo3`, puis entrez dedans avec `cd algo3`.

Créez un dossier `chapitre4/` dans ce projet. Copiez-y **le contenu** du
dossier `manip/` de cette branche GitHub. Créez aussi un fichier vide
`graphes.py`. Vous créerez `td1.py`, puis `td2.py`, etc., au début de
chaque TD : ces fichiers ne sont pas fournis.

```text
algo3/
├── pyproject.toml
└── chapitre4/
    ├── graphes.py          # vos fonctions réutilisées entre les TD
    ├── td1.py              # vos essais du TD 1, puis td2.py, etc.
    ├── routes.csv
    ├── communes.py
    ├── communes.csv
    ├── dependances.py
    ├── grilles.py
    ├── chrono.py
    ├── labyrinthe.py
    ├── labyrinthe.txt
    └── depart-td4/          # utile seulement si vous commencez au TD 4
```

- Dans `graphes.py`, ajoutez les fonctions et les imports demandés, en
  conservant ceux des TD précédents. N'y mettez pas vos essais ni vos `print`.
- Dans `td1.py`, `td2.py`, etc., placez les essais du TD concerné. Une
  variable créée dans un fichier n'est pas disponible dans les autres :
  les blocs de démarrage ci-dessous rechargent les données nécessaires.
- Pour lancer un essai, placez-vous dans `algo3/chapitre4/`, puis tapez
  `uv run td1.py`, en remplaçant le numéro par celui du TD.
- Notez les réponses écrites, tableaux et résultats dans `reponses.md`
  ou sur papier, en indiquant le numéro du TD et de l'étape.
- Le dossier `depart-td4/` ne sert qu'aux séances qui commencent au TD 4
  sans avoir fait les TD 1 à 3. Si vous suivez le chapitre depuis le TD 1,
  laissez-le de côté : il contient le `graphes.py` du TD 2, que vous écrivez
  vous-même.

Les blocs marqués **Code fourni** sont à recopier. Lorsqu'une fonction
est à écrire, la consigne précise ses paramètres et ce qu'elle doit
**renvoyer**. Renvoyer avec `return` et afficher avec `print` sont deux
opérations différentes.

Le [cours Google Slides](https://docs.google.com/presentation/d/1DY6Ydij2eapXi6QLVJx4quNBKjpL9AeifFiobzH4SA0/edit)
présente les algorithmes sur de petits graphes. Dans les TD,
`profondeur` renvoie toujours l'ordre de visite. `largeur` et `dijkstra`
ajoutent les parents pour reconstruire les chemins : leurs résultats
sont expliqués au moment de leur utilisation.

---

# Séance 1 - Voir, ranger, vérifier

# TD 1 - Trois situations

**Objectif : reconnaître les sommets et les arêtes d'un graphe.**

## Étape 1 - Dessiner les routes du canton *(sur papier)*

Ouvrez `routes.csv`. Chaque ligne décrit une route à double sens avec
ses deux communes et sa longueur en kilomètres.

Dessinez uniquement les routes dont **les deux extrémités** appartiennent
à cette liste : Bucchiniccia, Erbaghjolu, Ghjuncaghju, Ortoli,
Scandulaghju et Ulmetu Vecchiu. Ces six communes forment le canton Plateau.
Représentez chaque commune par un point et chaque route par un trait
portant sa longueur.

**Résultat attendu :** un dessin avec les six noms et les distances.
Gardez-le : vous l'utiliserez au TD 7.

## Étape 2 - Décrire trois graphes *(sur papier)*

Complétez les cases vides du tableau. Pour « Orienté », écrivez oui ou
non ; pour « Poids », indiquez ce que mesure le poids, ou « aucun ».
Les problèmes à résoudre sont déjà donnés.

Dans `labyrinthe.txt`, `#` représente un mur, `.` une case libre et `D`
le départ. On se déplace d'une case vers une case voisine horizontalement
ou verticalement. Dans `dependances.py`, `DEPEND_DE[p]` contient les
paquets nécessaires au paquet `p` : la flèche signifie « dépend de ».

| Problème | Sommets | Arêtes | Orienté | Poids |
| --- | --- | --- | --- | --- |
| Trouver un trajet routier en kilomètres | communes | routes | non | distance en km |
| Trouver un trajet dans le labyrinthe | | | | |
| Placer chaque paquet après ses prérequis dans une liste | | | | |

**Résultat attendu :** les deux lignes complétées. Aucun programme à
écrire à cette étape.

## Étape 3 - Compter les données *(sur machine)*

**Code fourni**, à placer au début de `td1.py` :

```python
import csv

with open("routes.csv", encoding="utf-8") as f:
    routes = [
        (ligne["depart"], ligne["arrivee"], int(ligne["km"]))
        for ligne in csv.DictReader(f)
    ]
```

Complétez ce fichier pour afficher le nombre de routes et le nombre de
communes **distinctes**. Pour le second compte, ajoutez les deux
extrémités de chaque route dans un ensemble (`set`).

**Résultat attendu :** deux lignes de sortie clairement nommées :
« Nombre de routes » et « Nombre de communes ».

---

# TD 2 - Construire

**Objectif : représenter les routes en Python et utiliser cette représentation.**

## Étape 1 - Charger les routes

Dans `graphes.py`, écrivez `charger_routes(chemin)` : son paramètre est
le nom du fichier CSV et son résultat est un dictionnaire de la forme
`{commune: {voisine: distance}}`. Ajoutez `import csv` en tête du fichier.
Vous pouvez reprendre la lecture du CSV du TD 1.

Pour chaque route de `a` vers `b` de distance `d`, créez les dictionnaires
de `a` et de `b` s'ils n'existent pas, puis enregistrez `g[a][b] = d`
**et** `g[b][a] = d`. La fonction se termine par `return g`.

**Code de vérification fourni**, à placer dans `td2.py` :

```python
from graphes import charger_routes

g = charger_routes("routes.csv")
assert len(g) == 24
assert g["Isulacciu"] == {"Caldarella": 6, "Finosella": 14}
assert g["Caldarella"]["Isulacciu"] == 6
print("Chargement validé")
```

Un `assert` qui échoue signale un résultat différent de celui attendu.

**Résultat attendu :** la fonction dans `graphes.py` et le message
« Chargement validé » à l'exécution de `td2.py`.

## Étape 2 - Accéder aux voisins et aux distances

Ajoutez ces **deux fonctions** dans `graphes.py` :

| Fonction à écrire | Paramètres | Valeur à renvoyer |
| --- | --- | --- |
| `voisins(g, s)` | un graphe et une commune présente dans le graphe | la liste des communes voisines de `s`, triée avec `sorted` |
| `km(g, a, b)` | un graphe et deux communes reliées par une route | la distance de cette route |

Dans notre représentation, `g[s]` est un dictionnaire. Le parcourir donne
ses clés, donc les voisins ; `g[s].items()` donne les voisins **et** les poids.
Toutes les visites des TD utilisent l'ordre alphabétique de `voisins`.

Ajoutez ces vérifications dans `td2.py` :

```python
from graphes import voisins, km

assert voisins(g, "Isulacciu") == ["Caldarella", "Finosella"]
assert km(g, "Isulacciu", "Caldarella") == 6
print("Accès aux routes validé")
```

**Résultat attendu :** les deux fonctions et un script qui passe les
vérifications sans erreur.

## Étape 3 - Comparer l'espace occupé *(sur papier)*

Une matrice d'adjacence réserve une case pour chaque paire de communes.
Le dictionnaire réserve une entrée par commune et deux entrées par route,
car nos routes sont à double sens. Ici, n = 24 communes et m = 32 routes.

Complétez le tableau en comptant des **entrées**, pas des octets. Pour
le dictionnaire, comptez les clés du dictionnaire principal et les
entrées des dictionnaires de voisins.

| Représentation | Nombre d'entrées avec n sommets et m arêtes | Valeur pour nos routes |
| --- | --- | --- |
| Matrice | | |
| Dictionnaire d'adjacence non orienté | | |

**Résultat attendu :** le tableau complété et une phrase indiquant la
représentation qui réserve le moins d'entrées pour ces données.

## Bonus - Construire la matrice

Dans `td2.py`, construisez une liste de listes `matrice` de taille
24 × 24 à partir de `g`. Les lignes et colonnes suivent `noms = sorted(g)`.
La case `[i][j]` contient la distance de la route, ou 0 s'il n'y en a pas.
Ce marqueur est possible ici car toutes les routes ont un poids strictement positif.

**Résultat attendu :** une matrice symétrique et un affichage du nombre
de cases non nulles.

---

# TD 3 - La bibliothèque

**Objectif : vérifier votre graphe avec NetworkX.**

## Étape 1 - Installer NetworkX

Depuis le dossier `algo3/`, exécutez :

```bash
uv add networkx
uv tree
```

Ouvrez `pyproject.toml` et `uv.lock`. Recopiez dans vos réponses la ligne
qui déclare NetworkX dans le premier et sa version exacte dans le second.
Enregistrez les deux fichiers dans un commit de **votre projet** :

```bash
git add pyproject.toml uv.lock
git commit -m "Ajouter NetworkX pour le chapitre Graphes"
```

Le fichier `uv.lock` permet de réinstaller les mêmes versions.
Revenez ensuite dans `algo3/chapitre4/` pour lancer vos programmes.

**Résultat attendu :** les deux informations relevées et le commit.

## Étape 2 - Convertir le graphe

**Code fourni**, à ajouter dans `graphes.py`. Cette fonction convertit
notre graphe de routes non orientées en objet NetworkX. Elle sera réutilisée.

```python
import networkx as nx

def vers_networkx(g):
    G = nx.Graph()
    G.add_nodes_from(g)
    for a, adjacents in g.items():
        for b, distance in adjacents.items():
            G.add_edge(a, b, km=distance)
    return G
```

Créez `td3.py` avec ce bloc :

```python
from graphes import charger_routes, vers_networkx

g = charger_routes("routes.csv")
G = vers_networkx(g)
print("Sommets :", G.number_of_nodes())
print("Arêtes :", G.number_of_edges())
```

Exécutez-le et comparez les deux nombres à ceux du TD 1. Une route est
lue dans les deux sens, mais `nx.Graph` conserve une seule arête entre
les deux communes.

**Résultat attendu :** les deux nombres et une indication « identiques »
ou « différents » par rapport au TD 1. Corrigez le chargement s'ils diffèrent.

## Étape 3 - Identifier les composantes

Un graphe non orienté est **connexe** si un chemin relie toute paire de
sommets. Une **composante connexe** regroupe tous les sommets reliés entre
eux ; aucun chemin ne la relie à une autre composante.

Ajoutez ce code dans `td3.py` :

```python
import networkx as nx

print("Connexe :", nx.is_connected(G))
print("Tailles des composantes :", sorted(len(c) for c in nx.connected_components(G)))
```

**Résultat attendu :** les deux lignes de sortie et une phrase expliquant
si toutes les communes sont accessibles les unes depuis les autres.

---

# Séance 2 - Parcourir

# TD 4 - En profondeur

**Objectif : parcourir un graphe et comparer récursion et pile explicite.**

## Avant de commencer - la base du TD 2

Ce TD s'appuie sur deux fonctions écrites au TD 2 : `charger_routes(chemin)`,
qui lit `routes.csv` et renvoie le graphe sous la forme
`{commune: {voisine: distance}}`, et `voisins(g, s)`, qui renvoie les communes
voisines de `s` triées par ordre alphabétique. C'est cet ordre qui fixe l'ordre
de visite des parcours.

**Vous avez fait le TD 2 ?** Votre `graphes.py` contient déjà ces fonctions.
Passez directement à l'étape 1.

**Vous commencez le chapitre à ce TD ?** La base est fournie. Depuis
`algo3/chapitre4/`, où vous avez copié le contenu de `manip/` :

```bash
cp depart-td4/graphes.py graphes.py
```

Vérifiez-la avant d'aller plus loin :

```bash
uv run python -c "from graphes import charger_routes, voisins; g = charger_routes('routes.csv'); print(len(g), voisins(g, 'Isulacciu'))"
```

La sortie attendue est `24 ['Caldarella', 'Finosella']` : le fichier décrit
24 communes, et Isulacciu en a deux pour voisines. Une autre sortie signale un
`routes.csv` absent ou tronqué ; corrigez-la avant de continuer.

Ce fichier est votre `graphes.py` pour la suite : vous y ajoutez les fonctions
des étapes ci-dessous, sans toucher aux trois qui s'y trouvent déjà.
NetworkX, installé au TD 3, n'est pas utilisé ici : n'installez rien.

**Résultat attendu :** la ligne `24 ['Caldarella', 'Finosella']`.

## Étape 1 - Exécuter le parcours récursif

**Code fourni**, à ajouter dans `graphes.py` :

```python
def explorer(g, s, vus, ordre):
    if s in vus:
        return
    vus.add(s)
    ordre.append(s)
    for v in voisins(g, s):
        explorer(g, v, vus, ordre)
```

`explorer` remplit l'ensemble `vus` et la liste `ordre` passés en
paramètres. Elle ne renvoie pas de résultat. Créez `td4.py` avec :

```python
from graphes import charger_routes, explorer

g = charger_routes("routes.csv")
vus, ordre = set(), []
explorer(g, "Isulacciu", vus, ordre)
print("Huit premières communes :", ordre[:8])
print("Nombre de communes atteintes :", len(vus))
print("Communes inaccessibles :", sorted(set(g) - vus))
```

Exécutez ce programme. En lisant `explorer`, expliquez en une phrase
pourquoi le test `if s in vus` empêche de tourner en rond.

**Résultat attendu :** les trois sorties et cette phrase d'explication.

## Étape 2 - Remplacer la récursion par une pile

**Code fourni**, à ajouter dans `graphes.py`. Cette version renvoie la
liste des sommets dans leur ordre de visite.

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

Ajoutez ce code dans `td4.py`, après celui de l'étape 1 :

```python
from graphes import profondeur
from grilles import grille

assert profondeur(g, "Isulacciu") == ordre

g50 = grille(50)  # 50 × 50 cases, soit 2 500 sommets
try:
    explorer(g50, (0, 0), set(), [])
    print("Récursion terminée")
except RecursionError:
    print("Limite de récursion atteinte")
print("Sommets atteints avec la pile :", len(profondeur(g50, (0, 0))))
```

**Résultat attendu :** une comparaison de deux lignes : le résultat de
la version récursive sur la grille et celui de la version avec pile.
Précisez quelle limite Python explique une éventuelle `RecursionError`.

## Étape 3 - Justifier le coût *(sur papier)*

On note n le nombre de sommets et m le nombre d'arêtes. Avec des listes
ou dictionnaires d'adjacence, un parcours complet coûte O(n + m), **hors
tri des voisins**.

Justifiez cette formule en deux phrases : une sur le nombre de fois
qu'un sommet est marqué, une sur le nombre de fois qu'une arête non
orientée est lue. Appuyez-vous sur le code de `profondeur`.

`voisins` utilise `sorted`, de coût O(d log d) au pire pour d voisins.
Sur nos routes et grilles, d ≤ 4 : ce coût reste borné par sommet et
la classe O(n + m) est conservée. Les slides préparent l'ordre à l'avance.

**Résultat attendu :** les deux phrases qui justifient O(n + m).

## Bonus - Mesurer le parcours

Dans `td4.py`, utilisez `chrono(profondeur, grille(k), (0, 0))` pour
k = 100, 200 et 400, après `from chrono import chrono`.

**Résultat attendu :** un tableau k / nombre de sommets / durée. Calculez
le rapport entre deux durées successives et comparez-le à 4.

---

# TD 5 - En largeur

**Objectif : trouver un chemin qui utilise le moins de routes possible.**

## Étape 1 - Calculer les distances en étapes

**Code fourni**, à ajouter dans `graphes.py` :

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

La largeur des slides renvoie l'ordre de visite. Ici, on renvoie deux
dictionnaires : `dist[v]` est le nombre minimal de routes pour atteindre
`v`, et `parent[v]` est la commune depuis laquelle on l'a découverte.
Le départ a pour parent `None`. Un sommet inaccessible est absent des deux.

Créez `td5.py` avec :

```python
from graphes import charger_routes, largeur

g = charger_routes("routes.csv")
dist, parent = largeur(g, "Isulacciu")
for etape in (1, 2, 3):
    communes = sorted(s for s in dist if dist[s] == etape)
    print(etape, communes)
```

Exécutez-le. Expliquez en une phrase pourquoi une file traite toutes les
communes à distance d avant celles à distance d + 1.

**Résultat attendu :** les communes à une, deux et trois étapes du départ,
et la phrase d'explication.

## Étape 2 - Retrouver un chemin

Dans `graphes.py`, écrivez `chemin(parent, arrivee)`. La fonction doit
**renvoyer une liste** allant du départ à l'arrivée, les deux compris.
Partez de `arrivee`, suivez les parents jusqu'à `None`, puis inversez la
liste obtenue. On suppose que l'arrivée figure dans `parent`.

> **Aide si vous bloquez.** Avec `parent = {"A": None, "B": "A", "C": "B"}`,
> partir de C fait lire C, puis B, puis A. La liste construite est
> `["C", "B", "A"]` ; la fonction doit renvoyer `["A", "B", "C"]`.
> À chaque tour de boucle, ajoutez le sommet courant puis remplacez-le
> par son parent. Arrêtez-vous quand le sommet courant vaut `None`.

Ajoutez ce code de vérification dans `td5.py` :

```python
from graphes import chemin, km, vers_networkx
import networkx as nx

trajet = chemin(parent, "Scandulaghju")
distance_km = sum(km(g, a, b) for a, b in zip(trajet, trajet[1:]))
print("Trajet :", trajet)
print("Nombre de routes :", len(trajet) - 1)
print("Distance en km :", distance_km)
G = vers_networkx(g)
assert len(trajet) - 1 == nx.shortest_path_length(G, "Isulacciu", "Scandulaghju")
```

`zip(trajet, trajet[1:])` énumère les paires de communes consécutives.
La largeur minimise le **nombre de routes** ; elle ne regarde pas les
kilomètres. Le TD 7 permettra de comparer les deux critères.

**Résultat attendu :** la fonction et les trois lignes de sortie.
Conservez ce résultat pour la comparaison du TD 7.

---

# TD 6 - L'arbre

**Objectif : lire et parcourir l'arbre produit par la largeur.**

## Étape 1 - Afficher l'arbre des parents

Créez `td6.py` avec ce **code fourni** :

```python
from graphes import charger_routes, largeur

g = charger_routes("routes.csv")
dist, parent = largeur(g, "Isulacciu")
enfants = {}
for sommet, p in parent.items():
    if p is not None:
        enfants.setdefault(p, []).append(sommet)
```

`enfants[p]` contient les communes dont le parent est `p`. Isulacciu est
la **racine** ; une commune sans enfant est une **feuille**.

Dans **ce même fichier `td6.py`**, écrivez `afficher(s, niveau=0)`.
Elle doit afficher `s`, précédé de `niveau` espaces, puis appeler
`afficher(enfant, niveau + 2)` pour chaque enfant, dans l'ordre alphabétique.
`enfants.get(s, [])` donne une liste vide pour une feuille.
Lancez ensuite `afficher("Isulacciu")`.

Le traitement du sommet avant ses enfants est un parcours **préfixe**.
Cette structure est un arbre : tous ses sommets sont reliés à la racine,
et chacun sauf la racine possède exactement une arête vers son parent.

**Résultat attendu :** l'arbre affiché avec deux espaces supplémentaires
à chaque niveau. Les trois premières lignes doivent montrer Isulacciu,
Caldarella puis Acquaviva, de plus en plus indentées.

## Étape 2 - Calculer la taille et la hauteur

Ajoutez ces deux fonctions dans `td6.py` ; elles utilisent `enfants` :

| Fonction | Valeur à renvoyer | Règle de calcul |
| --- | --- | --- |
| `taille(s)` | nombre de sommets du sous-arbre de `s`, lui compris | 1 + la somme des tailles de ses enfants |
| `hauteur(s)` | nombre maximal d'arêtes entre `s` et une feuille de son sous-arbre | 0 pour une feuille, sinon 1 + la plus grande hauteur des enfants |

Le calcul utilise les résultats des enfants avant de produire celui du
sommet : c'est un traitement **postfixe**.

> **Aide pour démarrer la récursion.** Une feuille contient seulement
> elle-même : sa taille vaut 1 et sa hauteur vaut 0. Traitez ce cas
> avant de calculer à partir des enfants ; cela évite notamment
> d'appeler `max` sur une liste vide.

**Résultat attendu :** affichez `taille("Isulacciu")`,
`taille("Finosella")` et `hauteur("Isulacciu")`, avec un libellé pour chaque
valeur. Vérifiez que la hauteur obtenue est égale à `max(dist.values())`.

## Bonus - Compter les cycles du canton

Reprenez le dessin du TD 1. Un graphe non orienté connexe est un arbre
s'il a exactement n − 1 arêtes. Dans un graphe connexe, m − n + 1 compte
les **cycles indépendants**, pas tous les cycles simples possibles.

**Résultat attendu :** comptez n et m pour le canton, déduisez le nombre
de cycles indépendants et tracez-les de couleurs différentes sur le dessin.

---

# Séance 3 - Le plus court chemin

# TD 7 - Le plus court en kilomètres

**Objectif : appliquer Dijkstra et distinguer distance en étapes et en kilomètres.**

## Étape 1 - Dérouler Dijkstra à la main *(sur papier)*

Utilisez uniquement le canton Plateau dessiné au TD 1, avec **Ortoli**
comme départ. Recopiez le tableau ci-dessous et ajoutez une ligne par
tour, jusqu'à ce que les six communes soient fixées.

| Tour | Commune fixée | Ortoli | Ulmetu Vecchiu | Ghjuncaghju | Bucchiniccia | Scandulaghju | Erbaghjolu |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | aucune | 0 | ∞ | ∞ | ∞ | ∞ | ∞ |

À chaque tour, choisissez la commune non fixée de distance provisoire
minimale. Marquez-la comme fixée. Pour chaque voisine non fixée,
comparez sa distance actuelle à `distance de la commune fixée + km de la route`
et gardez le minimum. Recopiez les autres distances sans les changer.
À égalité, choisissez la première commune dans l'ordre alphabétique.

**Résultat attendu :** le tableau complet, avec la commune fixée à
chaque tour et les distances finales. Ajoutez une phrase expliquant
pourquoi la justification de Dijkstra nécessite des poids positifs ou nuls.

## Étape 2 - Exécuter la version naïve *(sur machine)*

**Code fourni**, à ajouter dans `graphes.py` :

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
        for v, poids in g[x].items():
            if dist[x] + poids < dist[v]:
                dist[v] = dist[x] + poids
                parent[v] = x
    return dist, parent
```

Les poids doivent être finis et positifs ou nuls. Le départ et tous les
voisins sont des clés de `g`. `dist` contient tous les sommets ; ceux
qui sont inaccessibles restent à `INF`. `parent` ne contient que les
sommets atteignables.

Créez `td7.py` avec :

```python
from graphes import charger_routes, dijkstra_naif

g = charger_routes("routes.csv")
dist_km, parent_km = dijkstra_naif(g, "Isulacciu")
print("Distance vers Scandulaghju :", dist_km["Scandulaghju"])
print("Distance vers Diavulinu :", dist_km["Diavulinu"])
```

**Résultat attendu :** les deux sorties, en précisant ce que signifie
`inf` pour la possibilité de rejoindre la commune.

## Étape 3 - Comparer les deux chemins *(sur machine)*

Dans `td7.py`, calculez aussi `dist_etapes, parent_etapes = largeur(g, "Isulacciu")`,
après avoir importé `largeur`, `chemin` et `km` depuis `graphes`.
Reconstituez les deux chemins vers Scandulaghju avec `chemin`.
Pour leurs kilomètres, reprenez le calcul du TD 5.

| Algorithme | Liste des communes du chemin | Nombre de routes | Total en km |
| --- | --- | --- | --- |
| Largeur | | | |
| Dijkstra | | | |

Vérifiez la distance de Dijkstra avec ce **code fourni** :

```python
from graphes import vers_networkx
import networkx as nx

G = vers_networkx(g)
assert dist_km["Scandulaghju"] == nx.dijkstra_path_length(
    G, "Isulacciu", "Scandulaghju", weight="km"
)
```

**Résultat attendu :** le tableau complété et une phrase indiquant ce
que minimise chaque algorithme.

---

# TD 8 - La file de priorité

**Objectif : comprendre ce que le tas change dans Dijkstra.**

## Étape 1 - Observer une file de priorité

Une file de priorité retire l'entrée de plus petite priorité. `heapq`
la représente par un **tas**, stocké dans une liste Python. `heappush`
ajoute une entrée et `heappop` retire la plus petite.

Créez `td8.py` avec ce **code fourni**, puis exécutez-le :

```python
from heapq import heappush, heappop

tas = []
entrees = [(14, "Finosella"), (6, "Caldarella"), (22, "Petralba"), (6, "Bracciolu")]
for distance, commune in entrees:
    heappush(tas, (distance, commune))
while tas:
    print(heappop(tas))
```

Python compare les couples par leur premier élément, puis par le second
en cas d'égalité.

**Résultat attendu :** les quatre sorties dans l'ordre, en indiquant
pourquoi Bracciolu et Caldarella ne sortent pas dans leur ordre d'insertion.

## Étape 2 - Utiliser le tas dans Dijkstra

**Code fourni**, à ajouter dans `graphes.py`, en gardant la version naïve.
`INF` a été défini au TD 7. C'est le code des slides, avec les parents en plus.

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

Les préconditions et les valeurs renvoyées sont les mêmes qu'au TD 7.
Les sommets doivent en plus être comparables pour départager les égalités
dans le tas : c'est le cas des noms de communes et des couples `(ligne, colonne)`.

Ajoutez cette vérification dans `td8.py` :

```python
from graphes import charger_routes, dijkstra_naif, dijkstra

g = charger_routes("routes.csv")
dist_naif, _ = dijkstra_naif(g, "Isulacciu")
dist_tas, _ = dijkstra(g, "Isulacciu")
assert dist_tas == dist_naif
print("Distances identiques")
```

Une commune peut être ajoutée plusieurs fois au tas lorsqu'on trouve
des trajets de plus en plus courts vers elle.

**Résultat attendu :** la vérification réussie et une phrase expliquant
quelle entrée est écartée par `if d != dist[x]`.

## Étape 3 - Comparer les temps

Ajoutez dans `td8.py` ce **code fourni**. La génération du graphe se fait
avant le chronométrage ; les deux algorithmes reçoivent le même graphe.

```python
from grilles import grille
from chrono import chrono

for k in (15, 30, 60):
    gk = grille(k)
    t_naif = chrono(dijkstra_naif, gk, (0, 0))
    t_tas = chrono(dijkstra, gk, (0, 0))
    print(k, len(gk), t_naif, t_tas)
```

Reportez les mesures dans ce tableau. À partir de la deuxième ligne,
calculez chaque rapport en divisant la durée par celle de la ligne précédente.

| k | n = k² | Durée naïve (s) | Rapport naïve | Durée tas (s) | Rapport tas |
| --- | --- | --- | --- | --- | --- |
| 15 | 225 | | — | | — |
| 30 | 900 | | | | |
| 60 | 3 600 | | | | |

La sélection par `min` coûte O(n²) au total. Avec un tas, le coût est
O((n + m) log n) pour un graphe simple. Sur ces grilles, le nombre
d'arêtes est proportionnel à n. Quand n est multiplié par 4, on attend
un temps naïf proche de × 16, et un temps avec tas proche de × 4,
un peu plus à cause du logarithme. Les mesures peuvent s'en écarter.

**Résultat attendu :** le tableau mesuré et une phrase indiquant si les
tendances observées correspondent aux classes annoncées.

## Bonus - Faire une extrapolation

À partir de votre temps naïf pour k = 60, estimez le temps pour k = 120
sans exécuter cette version. Calculez d'abord le facteur d'augmentation
de n, puis appliquez le modèle quadratique.

**Résultat attendu :** le calcul et une durée estimée en secondes.

---

# TD 9 - Modéliser

**Objectif : choisir et adapter un parcours à un problème.**

## Étape 1 - Trouver la case la plus éloignée

Le fichier **fourni** `labyrinthe.py` contient `charger_labyrinthe(chemin)`.
Cette fonction renvoie `(graphe, depart)`. Chaque sommet est une case
libre `(ligne, colonne)`, avec des indices commençant à 0. Deux cases
voisines horizontalement ou verticalement sont reliées, avec un poids de 1.
Vous n'avez pas à écrire la lecture du fichier.

On reprend la largeur du TD 5 : les sommets sont maintenant des **couples
de coordonnées**, au lieu de noms de communes. Le numéro de ligne augmente
vers le bas et celui de colonne vers la droite. Par exemple, `(1, 2)`
désigne la deuxième ligne et la troisième colonne du fichier.

Créez `td9.py` avec :

```python
from labyrinthe import charger_labyrinthe
from graphes import largeur, chemin

gl, depart = charger_labyrinthe("labyrinthe.txt")
dist, parent = largeur(gl, depart)

# Points de contrôle avant de chercher la case la plus éloignée.
assert depart == (1, 1), "Vérifiez le fichier labyrinthe.txt utilisé"
assert dist[depart] == 0, "Le départ doit avoir une distance de zéro"
assert len(dist) == 43, "Vérifiez votre parcours en largeur et les données"
```

`dist[case]` donne le nombre minimal de **pas** depuis le départ.
`parent[case]` donne la case précédente dans le trajet. Par exemple :

| Case | `dist[case]` | `parent[case]` |
| --- | --- | --- |
| `(1, 1)`, le départ | 0 | `None` |
| `(1, 2)`, juste à droite du départ | 1 | `(1, 1)` |

Si un point de contrôle échoue, reprenez le chargement ou la largeur
avec l'enseignant avant de continuer. Si votre fonction `chemin` du TD 5
n'est pas encore opérationnelle, demandez une version corrigée pour
pouvoir poursuivre cet exercice.

Ajoutez le bloc suivant. **Remplacez seulement `pass` par un test et
une mise à jour** : si `nb_pas` est supérieur à `dist[arrivee]`,
retenez `case` comme nouvelle arrivée. `dist.items()` fournit les couples
`(case, nombre de pas)` ; comparez les distances, pas les coordonnées.

```python
arrivee = depart
for case, nb_pas in dist.items():
    # Retenir cette case si elle est plus éloignée que l'arrivée actuelle.
    pass  # à remplacer

trajet = chemin(parent, arrivee)
print("Case la plus éloignée :", arrivee)
print("Distance en pas :", dist[arrivee])
print("Trajet :", trajet)
assert len(trajet) - 1 == dist[arrivee]
```

Les cases inaccessibles sont absentes de `dist` : cette boucle examine
seulement les cases atteignables. En cas d'égalité, conserver la première
case trouvée convient. Plusieurs trajets optimaux peuvent être corrects.

**Résultat attendu :** les coordonnées de la case, sa distance en pas et
la liste des cases du trajet. Le nombre de déplacements doit être égal
à `len(trajet) - 1`.

## Étape 2 - Ordonner les dépendances

Dans `dependances.py`, `DEPEND_DE[p]` est la liste des prérequis du paquet `p`.
On veut placer chaque paquet **après** ses prérequis. Le graphe fourni
n'a pas de cycle.

Dans `graphes.py`, écrivez `ordre_installation(dep)`, qui renvoie la liste
ordonnée des noms de paquets. Inspirez-vous du parcours récursif : gardez
un ensemble `vus`, visitez les dépendances d'un paquet avant de l'ajouter
au résultat et lancez la visite depuis chaque clé de `dep`. Un paquet
ne doit apparaître qu'une fois.

**Aide facultative si la récursion bloque.** Vous pouvez partir de ce
squelette dans `graphes.py`. Remplacez `pass` par la visite des prérequis,
puis l'ajout du paquet au résultat, dans cet ordre :

```python
def ordre_installation(dep):
    vus, ordre = set(), []
    def visiter(paquet):
        if paquet in vus:
            return
        vus.add(paquet)
        # Appeler visiter pour chaque prérequis présent dans dep[paquet].
        # Ajouter ensuite paquet à ordre.
        pass  # à remplacer
    for paquet in dep:
        visiter(paquet)
    return ordre
```

Sur le petit exemple `{"application": ["outil"], "outil": []}`, le résultat
doit être `["outil", "application"]` : on ajoute l'application après le
retour de la visite de l'outil. Ce principe est celui du postfixe au TD 6.

**Code de vérification fourni**, à ajouter dans `td9.py` :

```python
from dependances import DEPEND_DE
from graphes import ordre_installation

ordre = ordre_installation(DEPEND_DE)
assert len(ordre) == len(DEPEND_DE) and set(ordre) == set(DEPEND_DE)
positions = {p: i for i, p in enumerate(ordre)}
assert all(
    positions[prerequis] < positions[paquet]
    for paquet, prerequis_liste in DEPEND_DE.items()
    for prerequis in prerequis_liste
)
print("Ordre valide :", ordre)
```

**Résultat attendu :** la fonction et une liste qui passe les vérifications.
Indiquez en une phrase pourquoi l'ajout au résultat est **postfixe**.
Plusieurs ordres valides sont possibles.

## Étape 3 - Choisir un algorithme *(sur papier)*

Complétez une ligne par situation. Les demandes sont :

- Un bâtiment : trouver une sortie en franchissant le moins de portes
  possible. Les portes se franchissent dans les deux sens.
- Des vols entre aéroports : trouver un trajet au prix total minimal,
  escales comprises. Les billets ont des prix positifs ; un vol aller
  et un vol retour sont deux offres différentes.

| Situation | Sommets | Arêtes et orientation | Poids utilisés | Algorithme choisi |
| --- | --- | --- | --- | --- |
| Bâtiment | | | | |
| Vols | | | | |

**Résultat attendu :** les deux lignes complétées. Appuyez votre choix
sur ce que le problème demande de minimiser.

## Bonus - Choisir un centre de secours

On cherche une commune où placer un centre de secours. Pour chaque
commune candidate, on calcule la distance à sa commune la plus éloignée.
On choisit le candidat pour lequel ce maximum est le plus petit.

Travaillez uniquement sur les 22 communes de la composante d'Isulacciu,
aussi bien pour les candidats que pour les destinations. Les deux autres
communes sont inaccessibles : leur distance infinie fausserait le maximum.
Dans `td9.py`, rechargez les routes avec `charger_routes("routes.csv")`
et utilisez Dijkstra depuis chaque candidat.

**Résultat attendu :** le nom de la commune retenue et sa distance maximale
en kilomètres. Importez les fonctions utilisées depuis `graphes`.
