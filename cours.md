# Rappel des structures algorithmiques

**UE 0 · Algo 3 avec Python · Chapitre 2**

Ce chapitre fait écrire des conditions, des boucles, des tris et des
fonctions récursives. Pour chaque notion : lire un exemple, suivre son
exécution, compléter un programme, puis résoudre un problème voisin.
Les durées, les formules de coût et les optimisations seront étudiées au
chapitre 3 à partir de ces programmes.

Ce cours accompagne les [neuf TD](td-enonces.md) et le
[mémo de syntaxe](memo-a4.md). Les exemples expliqués ici servent de modèles ;
les exercices demandent de les adapter.

## 1. Choisir et répéter

Un **algorithme** décrit précisément les instructions qui transforment
une entrée en un résultat. Une **variable** donne un nom à une valeur.
L’**affectation** `total = 0` associe ce nom à cette valeur ; `total == 0`
teste une égalité.

Une **condition** choisit une branche. Python utilise les deux-points et
l’indentation pour délimiter les blocs :

```python
n = 8
if n % 2 == 0:
    message = "pair"
else:
    message = "impair"
```

`%` calcule le reste : `8 % 2` vaut `0`. La première branche est donc
exécutée. Pour des entiers positifs, `//` donne le quotient entier :
`9 // 2` vaut `4` ; `/` donne ici `4.5`.

Une **boucle** répète des instructions. `for` parcourt une collection ;
`while` continue tant que son test est vrai. `break` quitte la boucle ;
`continue` passe au tour suivant.

```python
total = 0
for x in [5, -2, 8]:
    if x > 0:
        total = total + x
```

Une **trace** est un tableau ou un récit des étapes exécutées. On lit les
lignes dans l’ordre et on note la nouvelle valeur après chaque affectation.

| Moment | `x` | `x > 0` | `total` après le tour |
| --- | --- | --- | --- |
| avant la boucle | — | — | 0 |
| premier tour | 5 | vrai | 5 |
| deuxième tour | -2 | faux | 5 |
| troisième tour | 8 | vrai | 13 |

`total` est un **accumulateur** : il conserve un résultat partiel.
Le bloc du `if` ne s’exécute pas au deuxième tour, mais la boucle continue.

## 2. Listes et parcours

Une **liste** est une séquence ordonnée et modifiable. Le premier indice
est `0`. Pour `t = [6, 2, 9, 4]`, `t[0]` vaut `6` et `t[-1]` vaut `4`.
Une **tranche** `t[a:b]` contient les éléments entre `a` inclus et `b`
exclu : `t[1:3]` vaut `[2, 9]`. `t.copy()` crée une nouvelle liste.

Un **parcours séquentiel** visite les éléments dans leur ordre. On peut
compter, sommer, chercher ou filtrer pendant ce parcours. `enumerate(t)`
fournit les couples `(indice, élément)`.

Pour chercher le maximum d’une liste non vide, retenir le premier élément
puis remplacer le candidat quand une valeur plus grande apparaît :

| Élément examiné | Candidat avant | Candidat après |
| --- | --- | --- |
| initialisation avec 6 | — | 6 |
| 2 | 6 | 6 |
| 9 | 6 | 9 |
| 4 | 9 | 9 |

L’**invariant** exprime ce qui reste vrai au même point de chaque tour :
« le candidat est le maximum des éléments déjà examinés ». À la fin,
tous les éléments ont été examinés ; le candidat est donc le maximum.
Initialiser à `0` serait faux pour une liste de nombres tous négatifs.

Chercher une première occurrence permet de s’arrêter dès qu’on l’a trouvée.
Compter toutes les occurrences exige de continuer jusqu’à la fin.

## 3. Fonctions et contrats

Une **fonction** est un bloc nommé qui reçoit des arguments. Un
**paramètre** est le nom utilisé dans sa définition ; un **argument** est
la valeur donnée à l’appel. `return` termine l’appel et transmet une valeur.
`print` affiche une valeur. Une fonction sans `return` explicite renvoie `None`.

```python
def double(x):
    """Renvoie deux fois le nombre reçu."""
    return 2 * x

resultat = double(7)  # resultat vaut 14 ; rien n’est affiché
```

Le **contrat** précise les entrées acceptées et le résultat promis. Une
**précondition** doit être vraie avant l’appel, par exemple « la liste est
non vide ». Une **postcondition** décrit le résultat, par exemple « la valeur
renvoyée est le maximum de la liste reçue ».

Un **test** compare un résultat calculé à un résultat attendu :

```python
assert double(7) == 14
assert double(0) == 0
assert double(-3) == -6
```

`assert` ne dit rien si la condition est vraie ; sinon, Python lève
`AssertionError`. Plusieurs tests détectent des erreurs, sans prouver la
correction sur toutes les entrées possibles. Choisir des **cas limites** :
liste vide, un élément, doublons, valeurs négatives, cible absente.

## 4. Dictionnaires et données structurées

Un **dictionnaire** associe des clés à des valeurs. Une clé doit être
**hachable** : son hash reste stable et respecte l’égalité. Chaînes et
entiers conviennent ; listes et dictionnaires ne conviennent pas.
Un tuple convient si chacun de ses éléments est hachable.

```python
totaux = {}
for secteur, nombre in [("Nord", 12), ("Sud", 5), ("Nord", 8)]:
    totaux[secteur] = totaux.get(secteur, 0) + nombre
# {"Nord": 20, "Sud": 5}
```

`get(cle, 0)` lit la valeur associée ou donne `0` si la clé manque.
L’affectation qui suit crée ou modifie cette association.

Une **compréhension** construit une liste à partir d’un parcours et d’un
filtre éventuel : `[x for x in [5, -2, 8] if x > 0]` donne `[5, 8]`.

Le format **CSV** représente un tableau dans un fichier texte.
`csv.DictReader` utilise les noms de colonnes comme clés. Avec les options
utilisées dans ce chapitre, les champs lus sont des chaînes : convertir
avec `int` ou `float` avant de calculer. Le bloc `with open(...)` ferme le
fichier quand on le quitte.

## 5. Trier avec Python

**Trier** signifie ordonner les éléments selon un critère.
`sorted(t)` renvoie une nouvelle liste ; `t.sort()` modifie `t` et renvoie
`None`. Une fonction passée dans `key` extrait la **clé de tri**.

```python
mots = ["rive", "lac", "mer", "sommet"]
classes = sorted(mots, key=len)
# ["lac", "mer", "rive", "sommet"] ; mots reste inchangée
```

Le tri est **stable** : les éléments ayant la même clé gardent leur ordre
relatif. Ici, `lac` reste avant `mer`, car les deux mots ont trois lettres.
`reverse=True` demande l’ordre décroissant tout en conservant cette stabilité.

Un tuple permet plusieurs critères : `(canton, -population)` compare
d’abord le canton, puis la population décroissante à canton égal.
Avec deux tris successifs, commencer par le critère **secondaire** puis
trier selon le **principal**. La stabilité conserve le classement secondaire
parmi les éléments dont le critère principal est égal.

## 6. Écrire un tri et suivre ses étapes

Le **tri par sélection** place successivement le plus petit élément restant.
Dans `[6, 3, 5, 1]`, on échange `6` et `1`, puis `3` reste à sa place,
puis `5` reste à sa place : `[1, 3, 5, 6]`.
Après chaque tour, le préfixe trié contient les plus petits éléments ;
ils ne bougeront plus. Le symbole `<=` est nécessaire dans l’invariant,
car les doublons sont autorisés.

Le **tri par insertion** agrandit un préfixe déjà trié. Il mémorise le
prochain élément `x`, décale les valeurs plus grandes et insère `x` dans
la place libérée.

| Tour sur `[6, 3, 5, 1]` | Valeur insérée | Liste après insertion |
| --- | --- | --- |
| `i = 1` | 3 | `[3, 6, 5, 1]` |
| `i = 2` | 5 | `[3, 5, 6, 1]` |
| `i = 3` | 1 | `[1, 3, 5, 6]` |

Invariant : le préfixe est trié. Il peut encore changer au tour suivant.
On s’assure aussi que toutes les valeurs sont conservées, avec leurs doublons.
Dans nos TD, les tris travaillent sur une copie et renvoient
`(liste_triee, comparaisons)`. Le compteur porte sur les comparaisons de
valeurs et sera exploité au chapitre suivant.

## 7. Chercher par dichotomie

La **recherche dichotomique** élimine une partie des candidats à chaque
comparaison avec le milieu. Sa précondition est une liste **triée**.
On utilise ici deux bornes inclusives : `g = 0`, `d = len(t)-1`.

Pour chercher `9` dans `[1, 4, 6, 9, 12]` :

| `g` | `d` | `m = (g+d)//2` | `t[m]` | Décision |
| --- | --- | --- | --- | --- |
| 0 | 4 | 2 | 6 | trop petit : `g = 3` |
| 3 | 4 | 3 | 9 | trouvé : indice 3 |

Pour chercher `8`, le second test donne `d = 2` : alors `g > d`,
l’intervalle est vide et on renvoie `-1`.

Invariant : si la cible est présente et n’a pas été trouvée, elle est
encore entre les bornes. La **progression** est la diminution du nombre
de candidats. Exclure le milieu déjà testé avec `m+1` ou `m-1` garantit
que l’intervalle diminue. Une liste non triée peut donner un résultat
juste par hasard ; la méthode ne garantit alors plus la réponse.

`bisect_left(t, x)` donne un **point d’insertion**, pas une preuve de présence.
Après `i = bisect_left(t, x)`, tester `i < len(t) and t[i] == x`.

## 8. Comprendre la récursivité

Une fonction est **récursive** si elle s’appelle elle-même. Chaque appel
possède ses propres paramètres et variables locales.

```python
def compte_a_rebours(n):
    print(n)
    if n > 0:
        compte_a_rebours(n - 1)
```

Pour l’entrée `3`, l’affichage est `3`, `2`, `1`, `0`. Le **cas de base**
est `n = 0` : aucun nouvel appel. La **progression** est la diminution de
`n`. Cet exemple affiche des nombres ; il ne calcule pas une valeur à
réutiliser. Chaque appel finit par renvoyer `None`.

Pour calculer un résultat, il faut aussi suivre les **retours**.
La **factorielle** `n!` est le produit des entiers de 1 à `n` ; on adopte
`0! = 1`. Ainsi, `3! = 3 × 2 × 1 = 6`.

```python
def factorielle(n):
    """n est un entier >= 0 ; renvoie n!."""
    if n <= 1:
        return 1
    return n * factorielle(n - 1)
```

## 9. Tracer factorielle(3), pas à pas

**Tracer**, c’est raconter les étapes exécutées, en écrivant les arguments
et les résultats. Une ligne indentée représente un nouvel appel.

```text
1. factorielle(3) attend 3 * factorielle(2)
2.   factorielle(2) attend 2 * factorielle(1)
3.     factorielle(1) renvoie 1 (cas de base)
4.   factorielle(2) reprend : 2 * 1 = 2, puis renvoie 2
5. factorielle(3) reprend : 3 * 2 = 6, puis renvoie 6
```

Aux lignes 1 et 2, les multiplications attendent une valeur : c’est la
**descente des appels**. À la ligne 3, le résultat est connu immédiatement.
On remplace alors chaque appel terminé par son résultat, aux lignes 4 et 5 :
c’est la **remontée des retours**. Le résultat final vaut `6`.

Le programme ne descend pas jusqu’à `0` dans cet exemple : le test
`n <= 1` l’arrête à `1`. Un appel initial avec `0` renverrait directement `1`.

La **pile d’appels** mémorise les appels en cours et le calcul qu’ils doivent
reprendre. Le dernier appel commencé termine avant son appelant.
Python limite la profondeur : `sys.getrecursionlimit()` indique la limite
courante. Un cas de base inatteignable ou une entrée trop grande peut
conduire à `RecursionError`.

Pour écrire une récursion, préciser le contrat, trouver le résultat du
cas de base, réduire l’entrée et transmettre le résultat par `return`.
Une somme traite le premier élément puis le reste ; une puissance naïve
multiplie par `x` puis traite l’exposant précédent.

## 10. Diviser pour régner et trier par fusion

**Diviser pour régner** consiste à découper un problème en sous-problèmes,
à les résoudre et à combiner leurs résultats. Le **tri fusion** découpe une
liste en deux moitiés, trie chaque moitié par le même procédé, puis les fusionne.
Une liste vide ou d’un élément est déjà triée : c’est le cas de base.

La **fusion** combine deux listes déjà triées. Elle compare leurs prochaines
valeurs et ajoute la plus petite à une nouvelle liste. Quand une entrée est
épuisée, on ajoute tout ce qui reste dans l’autre.

| Fusion de `[2, 7]` et `[3, 8]` | Valeur ajoutée | Résultat partiel |
| --- | --- | --- |
| comparer 2 et 3 | 2 | `[2]` |
| comparer 7 et 3 | 3 | `[2, 3]` |
| comparer 7 et 8 | 7 | `[2, 3, 7]` |
| la gauche est épuisée | reste `[8]` | `[2, 3, 7, 8]` |

Pour trier `[7, 2, 8, 3]`, le programme suit cet ordre :

1. trier `[7, 2]` : les appels sur `[7]` et `[2]` reviennent directement ;
   leur fusion donne `[2, 7]` ;
2. trier `[8, 3]` de la même façon, ce qui donne `[3, 8]` ;
3. fusionner les deux résultats pour obtenir `[2, 3, 7, 8]`.

L’exécution termine donc la moitié gauche avant de commencer la droite.
Pour conserver la stabilité, prendre la valeur de gauche en cas d’égalité.
Dans le TD, `fusion(g, d)` a deux arguments et `tri_fusion(t)` renvoie
uniquement la nouvelle liste. Le compteur global est remis à zéro avant
le tri complet, puis lu après son retour.

## 11. Vérifier et réutiliser

Pour chaque fonction, vérifier le contrat et prévoir des tests avant le code.
Une récursion peut contenir un bon cas de base mais ne jamais l’atteindre.
Elle peut terminer mais oublier de renvoyer le résultat calculé.

Pour les tris, contrôler l’ordre, la conservation des éléments et l’entrée
inchangée. Pour une recherche, tester cible présente, absente et liste vide.
Pour les récursions, tester d’abord le cas de base puis une toute petite entrée.
Conserver les programmes : le chapitre 3 expliquera comment comparer leurs coûts.

## Pour poursuivre avec qkzk

La progression pédagogique s’appuie sur les ressources signalées en cours ;
les exemples, données et consignes de ce support sont adaptés à l’UE 0.

- Première : [parcours séquentiels](https://qkzk.xyz/docs/nsi/cours_premiere/algorithmique/sequentiel/cours/),
  [TD de parcours](https://qkzk.xyz/docs/nsi/cours_premiere/algorithmique/sequentiel/td/),
  [sélection](https://qkzk.xyz/docs/nsi/cours_premiere/algorithmique/tris/1_select/),
  [insertion et sorted](https://qkzk.xyz/docs/nsi/cours_premiere/algorithmique/tris/3_insert/),
  [dichotomie](https://qkzk.xyz/docs/nsi/cours_premiere/algorithmique/dichotomie/1_cours/).
- Terminale : [récursivité](https://qkzk.xyz/docs/nsi/cours_terminale/prog/recursivite/cours/),
  [exercices de récursivité](https://qkzk.xyz/docs/nsi/cours_terminale/prog/recursivite/td/),
  [tri fusion](https://qkzk.xyz/docs/nsi/cours_terminale/algorithmique/diviser_pour_regner/tri_fusion/).
