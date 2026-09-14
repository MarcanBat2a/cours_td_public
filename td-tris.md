# TD - Cinq tris, un chronomètre

**UE 0 - Algo 3 avec Python · Chapitre 3 · TD à part**
Marcu-Andria Battesti · Bachelor CLIC · 2026-2027

> Un TD complet, sur machine, à faire après le TD 4. Cinq tris écrits par
> vous - sélection, bulle, insertion, rapide, fusion - chronométrés sur
> **le même jeu de données**, et pour finir un tableau : lequel, dans
> quel cas.
>
> Dans `algo3/chapitre3/`, venv activé, `manip/chrono.py` à côté. Votre
> `tris.py` du chapitre 2 (sélection, insertion, fusion) ou
> `manip/tris_ch2.py` en secours.
>
> **Le pronostic avant la mesure**, sur la fiche. Les temps varient d'un
> poste à l’autre ; les rapports entre lignes et colonnes donnent une
> tendance, mais varient aussi avec les données et les conditions de mesure.
>
> **★** : les questions dont la réponse doit tenir en une phrase juste ou
> un tableau rempli.

---

**Sur machine**

## Étape 0 - Le jeu de données

```python
from chrono import chrono, liste_aleatoire
t = liste_aleatoire(1000)
t[:5]
len(t)
```

1. Appelez `liste_aleatoire(10)` deux fois. Même liste ? Pourquoi la
   fiche y tient-elle : que peut-on comparer si tout le monde trie la
   même liste ?
2. Dans `cinq_tris.py`, quatre formes de la même liste :

```python
import random

def jeux(n):
    aleatoire = liste_aleatoire(n)
    triee = sorted(aleatoire)
    inversee = sorted(aleatoire, reverse=True)
    presque = list(triee)
    random.seed(1)
    for _ in range(10):
        i, j = random.randrange(n), random.randrange(n)
        presque[i], presque[j] = presque[j], presque[i]
    return {"aléatoire": aleatoire, "triée": triee,
            "inversée": inversee, "presque triée": presque}
```

   Combien d'éléments de `presque` ne sont pas à leur place, au plus ?

## Étape 1 - Cinq tris, une signature

Dans `cinq_tris.py`. Chaque tri prend une liste et **renvoie une nouvelle
liste triée**, sans compteur cette fois. Le test, pour chacun :
`tri(liste_aleatoire(1000)) == sorted(liste_aleatoire(1000))`.

1. **Sélection, insertion, fusion** : reprenez celles du chapitre 2 en
   retirant le compteur (ou `tris_ch2` : gardez `[0]` du tuple renvoyé).
2. **Bulle** : parcourir la liste, échanger deux voisins mal ordonnés ;
   recommencer tant qu'un passage a fait au moins un échange. Après un
   passage complet, où se trouve le plus grand élément ? Le passage
   suivant peut donc s'arrêter une case plus tôt : faites-le.
3. **Rapide** : le pivot est `t[0]` ; `petits` reçoit ce qui est plus
   petit que lui, `grands` le reste ; le résultat est
   `tri_rapide(petits) + [pivot] + tri_rapide(grands)`. Le cas de base
   s'écrit sur la fiche avant l'appel.
4. ★ Pour chacun des cinq, une phrase : « à chaque tour, ce tri ... ».
5. ★ Deux des cinq fabriquent des listes nouvelles à chaque appel :
   lesquelles, et que coûte cette copie en mémoire par rapport aux trois
   autres ?

## Étape 2 - Le même jeu, n croissant

```python
TRIS = [tri_selection, tri_bulle, tri_insertion, tri_rapide, tri_fusion]
for n in (100, 1000, 3000):
    t = liste_aleatoire(n)
    print(n, *[f"{chrono(f, t):.4f}" for f in TRIS], f"{chrono(sorted, t):.4f}")
```

Le tableau, temps en secondes :

| n | sélection | bulle | insertion | rapide | fusion | `sorted` |
| --- | --- | --- | --- | --- | --- | --- |
| 100 | | | | | | |
| 1 000 | | | | | | |
| 3 000 | | | | | | |
| 10 000 | *(pronostic)* | *(pronostic)* | *(pronostic)* | | | |
| 100 000 | *(pronostic)* | *(pronostic)* | *(pronostic)* | | | |

1. Pronostic avant de lancer : classez les cinq tris du plus rapide au
   plus lent pour n = 3 000. Puis mesurez les trois premières lignes.
2. De 1 000 à 3 000, n est multiplié par 3. Par combien chaque colonne
   est-elle multipliée ? Rangez les colonnes en deux groupes.
3. ★ Pour 10 000 puis 100 000, calculez le temps de la sélection, de
   la bulle et de l'insertion à partir de la ligne 3 000 - sans les
   lancer. Écrivez-les en secondes, puis en minutes. Lancez seulement
   `rapide`, `fusion` et `sorted`.
4. `sorted` contre votre fusion à 100 000 : le rapport ? Il vient de
   deux choses - lesquelles ? *(Indice : dans quel langage est écrit
   `sorted` ? Et que fait-il des morceaux déjà en ordre ?)*

## Étape 3 - Le même n, quatre entrées

```python
for nom, t in jeux(3000).items():
    print(nom, *[f"{chrono(f, t):.4f}" for f in TRIS])
```

| n = 3 000 | aléatoire | triée | inversée | presque triée |
| --- | --- | --- | --- | --- |
| sélection | | | | |
| bulle | | | | |
| insertion | | | | |
| rapide | | | | |
| fusion | | | | |

1. Pronostic, case par case, avec trois mots seulement : « pareil »,
   « bien plus vite », « bien plus lent » que la colonne aléatoire.
2. Lancez. Le tri rapide s'arrête sur une erreur pour deux entrées :
   recopiez la dernière ligne du message. Expliquez avec le vocabulaire
   du TD 5 : que vaut la profondeur des appels quand le pivot est le
   premier élément d'une liste déjà triée ?
3. ★ Le remède tient en une ligne : `pivot = t[len(t) // 2]` (et une
   liste `egaux` pour ne pas perdre les doublons du pivot). Remesurez
   `rapide` sur les quatre entrées. Le pire cas a-t-il disparu, ou
   seulement changé de place ?
4. ★ La sélection a quatre temps égaux. Pourquoi est-elle la seule ?
5. L'insertion sur la liste presque triée : le rapport avec la colonne
   aléatoire ? Avec le compteur du chapitre 2, mesurez ses comparaisons
   sur `presque triée` : vous trouverez à peu près 8 × n. D'où viennent
   ces 8 n, sachant que dix échanges ont déplacé vingt éléments ?
6. ★ La bulle profite de l'ordre sur la liste triée, mais très peu sur
   la presque triée. Suivez un élément déplacé vers le début de la liste :
   de combien de cases avance-t-il à chaque passage ? Combien de passages
   la bulle fait-elle alors, contre combien pour l'insertion ?

## Étape 4 - Vingt éléments

```python
import time
t = liste_aleatoire(20)
for f in TRIS + [sorted]:
    debut = time.perf_counter()
    for _ in range(1000):
        f(t)
    print(f.__name__, f"{(time.perf_counter() - debut) / 1000 * 1e6:.1f} µs")
```

1. Pronostic : les deux tris en n log n gagnent-ils encore à n = 20 ?
   Mesurez.
2. ★ Rangez les cinq. Qu'est-ce qui décide du classement quand n est
   petit, puisque ce n'est plus la classe ?

## Étape 5 - Lequel, quand ★

À partir de vos trois tableaux, et de rien d'autre :

| La situation | Le tri | Une phrase, un chiffre |
| --- | --- | --- |
| une liste de vingt éléments | | |
| une liste presque triée, quelle que soit sa taille | | |
| une grande liste dont on ne sait rien | | |
| une grande liste, et le pire cas est interdit (temps garanti) | | |
| une liste dont on veut juste savoir si elle est déjà triée | | |
| dans un programme Python | | |

1. ★ Remplissez le tableau. Chaque case « une phrase, un chiffre » cite
   un rapport lu dans vos mesures.
2. ★ Deux tris n'apparaissent dans aucune ligne. Lesquels, et pourquoi
   les a-t-on quand même écrits ?
3. ★ `sorted` de Python est un tri fusion qui confie les petits morceaux
   (quelques dizaines d'éléments) à l'insertion, et qui repère d'abord les
   suites déjà en ordre. Avec vos tableaux, justifiez chacun des trois
   choix en une phrase.
4. ★ « Un tri en O(n log n) est toujours le meilleur choix. » Vrai ou
   faux ? Deux contre-exemples tirés de vos mesures.

> Gardez `cinq_tris.py` : le tableau de l'étape 5 est une question
> d'évaluation type.
