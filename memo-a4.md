# Mémo - l'atelier Python avec uv

**UE 0 - Algo 3 avec Python · Chapitre 1**
Distribué en fin de séance · à rouvrir à chaque nouveau projet

> Une page. Tout ce que le chapitre a fait faire, dans l'ordre où on le
> refait : quel Python, le projet, les paquets, le contrat, le dépôt.
> Les commandes `uv` sont identiques sous macOS, Linux et Windows.

## Installer uv, une fois par poste

| macOS, Linux | Windows (PowerShell) |
| --- | --- |
| `curl -LsSf https://astral.sh/uv/install.sh \| sh` | `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 \| iex"` |

Puis rouvrir le terminal : `uv --version`. uv installe lui-même les Python
dont un projet a besoin ; aucun autre téléchargement à faire à la main.

## Quel Python ?

| | commande |
| --- | --- |
| ceux qu'uv connaît | `uv python list --only-installed` |
| celui qu'uv choisirait ici | `uv python find` |
| celui qui exécute, de l'intérieur | `import sys; sys.executable` |
| ceux du PATH (le shell) | `which -a python3` (Windows : `where python`) |

**`uv run script.py`** : le script tourne avec le Python **du projet**
courant, et son atelier. `uv run --python 3.13 script.py` : avec un
autre, téléchargé s'il manque.

## Le projet : un atelier par dossier

```text
uv init monprojet        pyproject.toml, .python-version, main.py, .gitignore, README.md, git
uv run main.py           crée .venv/ et uv.lock au premier passage, puis exécute
```

`.venv/` est l'atelier : un Python lié à l'original (`pyvenv.cfg`, ligne
`home`), un `site-packages` à lui. **Jetable** : `rm -rf .venv`, puis
`uv sync` le refait. Il ne se commite pas, ne s'envoie pas, ne se déplace pas.

Activer (`source .venv/bin/activate`, Windows `.venv/Scripts/activate`)
met `.venv/bin` en tête du PATH : `python` devient celui du projet. Rien
d'autre. `uv run` fait la même chose sans y toucher.

## Les paquets

```text
uv add requests               installer et l'écrire dans pyproject.toml (>= la version du jour)
uv add "requests==2.31.0"     exactement celle-là
uv add "requests>=2.31,<3"    dans une fourchette
uv tree                       qui a amené qui
uv pip show requests          Version, Location, Requires, Required-by
uv remove requests            retirer, avec ses dépendances devenues inutiles
```

**Versions** : `MAJEUR.MINEUR.CORRECTIF` - un majeur qui change, relisez
votre code. `==` épingle, `>=2.31,<3` encadre, rien du tout = « la
dernière », qui change de sens chaque semaine.

## Le contrat : deux fichiers

| fichier | rôle | écrit par |
| --- | --- | --- |
| `pyproject.toml` | l'**intention** : ce que le projet demande | `uv add`, ou vous |
| `uv.lock` | la **photo** : chaque paquet, sa version exacte | uv seulement |

```text
uv sync                       reconstruire .venv/ depuis uv.lock, à l'identique
```

**Quand uv refuse**, lire la phrase `Because ...` avant de toucher au fichier.
« *there is no version of X* » : le nom existe, pas ce numéro. « *X was not
found in the package registry* » : ce nom n'existe pas ; vérifier aussi
la compatibilité Python et l'accès à l'index. Corriger une ligne, relancer,
relire.

## Le dépôt

```text
algo3/
├── .venv/               jamais dans git (uv init l'a mis dans .gitignore)
├── .python-version      toujours : le Python qu'uv doit fournir
├── pyproject.toml       toujours : l'intention
├── uv.lock              toujours : la photo
├── README.md            les deux commandes ci-dessous
└── chapitre1/           votre code
```

Reconstruire un projet cloné, sur un poste où seul uv est installé :

```text
uv sync                       Python compris, si .python-version le demande
uv run version_pypi.py
```

