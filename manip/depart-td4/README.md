# Commencer directement au TD 4

Ce dossier sert **uniquement** aux séances qui démarrent au TD 4 sans avoir
fait les TD 1 à 3. Il contient le `graphes.py` que vous auriez écrit au TD 2.

Si vous avez fait les TD 1 à 3, **ignorez ce dossier** : votre `graphes.py`
est déjà le bon, et l'écraser vous ferait perdre votre travail.

## Ce qu'il contient

| Fichier | Rôle |
| --- | --- |
| `graphes.py` | `charger_routes`, `voisins` et `km`, les trois fonctions du TD 2 |

## L'utiliser

Depuis `algo3/chapitre4/`, où vous avez déjà copié le contenu de `manip/` :

```bash
cp depart-td4/graphes.py graphes.py
```

Vérifiez ensuite que la base répond :

```bash
uv run python -c "from graphes import charger_routes, voisins; g = charger_routes('routes.csv'); print(len(g), voisins(g, 'Isulacciu'))"
```

La sortie attendue est `24 ['Caldarella', 'Finosella']` : 24 communes, et les
deux voisines d'Isulacciu dans l'ordre alphabétique.

Vous ajouterez vos propres fonctions à la suite de ce fichier, TD après TD.
Les trois fonctions fournies ne sont plus à modifier.

## Ce qui n'y est pas

`vers_networkx`, écrite au TD 3, n'est pas dans ce fichier : le TD 4 n'en a pas
besoin et NetworkX n'est donc pas à installer pour cette séance. Les TD 5 et 7
la réutilisent ; reprenez-la dans l'énoncé du TD 3 le jour où vous en aurez
besoin, après un `uv add networkx`.
