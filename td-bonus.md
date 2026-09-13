# Bonus - Comprendre l'environnement Python

**UE 0 - Algo 3 avec Python · Chapitre 1**

Ces manipulations sont **facultatives**, après le parcours de
[td-enonces.md](td-enonces.md). Elles peuvent servir de démonstrations
enseignant. Chaque bonus commence dans `travail-python`, dans un terminal
où aucun environnement n'a été activé.

Si vous venez de terminer le TD 3 ou un autre bonus, tapez `cd ..` pour
revenir dans `travail-python`. Vérifiez le dossier avec `pwd`.

## Bonus 1 - Quel Python lance le programme ?

```bash
uv run manip/quel_python.py
cd algo3
uv run ../manip/quel_python.py
```

Regardez seulement les lignes `exécutable` et `dans un venv`. Dans `algo3`,
l'exécutable est dans `.venv` et la dernière ligne indique `True`.
Un **environnement virtuel** est un environnement Python réservé à un projet.

Pour montrer le mode interactif, l'enseignant peut ensuite lancer :

```bash
uv run python
```

Quand `>>>` apparaît, tapez ces deux lignes **dans Python** :

```python
print("Bonjour")
exit()
```

Attendez d'être revenu au terminal avant de taper d'autres commandes `uv`.

## Bonus 2 - Deux projets, deux versions d'un paquet

Depuis `travail-python`, après le TD 2 :

```bash
cd algo3
uv run version_pypi.py requests
cd ..
uv init --no-package vieux-projet
cd vieux-projet
uv add "requests==2.25.1"
cp ../manip/version_pypi.py .
uv run version_pypi.py requests
```

Comparez seulement la ligne `requests utilisé` : chaque projet utilise sa
propre version. `==2.25.1` demande cette version précise, choisie ici pour
la comparaison. Le programme est le même dans les deux cas.

L'enseignant peut afficher `uv tree` dans chacun des deux projets pour montrer
les autres paquets installés avec `requests`.

## Bonus 3 - Lire une erreur, avec l'enseignant

Depuis `travail-python`, copiez le projet fourni :

```bash
cp -R manip/tableau-de-bord .
cd tableau-de-bord
uv sync
```

**Une erreur est attendue.** Le fichier `pyproject.toml` contient deux
problèmes volontaires. Ouvrez-le dans l'éditeur. Les paquets nécessaires au
programme s'appellent `cowsay` et `rich`.

1. Repérez dans l'erreur le nom du paquet en cause. L'ordre peut varier.
2. Si le numéro demandé n'existe pas, retirez `==` et le numéro, en gardant
   le nom entre guillemets. Si le nom est mal écrit, corrigez son orthographe ;
   retirez aussi le numéro pour laisser uv choisir une version disponible.
3. Enregistrez, relancez `uv sync`, puis recommencez pour le second problème.
4. Lorsque `uv sync` réussit, lancez `uv run tableau.py`.

Vous devez voir `Atelier prêt` et une vache dessinée dans le terminal.
Les numéros de version choisis par uv n'ont pas à être ceux d'une autre machine.

## Repère enseignant - Si vous montrez l'activation

Le parcours principal utilise `uv run`, qui prépare et utilise l'environnement
du projet. Il n'est pas nécessaire de montrer l'activation manuelle.

Si vous la montrez, depuis le dossier `algo3` :

```bash
source .venv/bin/activate         # Windows / Git Bash : source .venv/Scripts/activate
python ../manip/quel_python.py
deactivate
```

**Terminez par `deactivate` avant de changer de projet.** `cd ..` change de
dossier, mais ne désactive pas l'environnement.
