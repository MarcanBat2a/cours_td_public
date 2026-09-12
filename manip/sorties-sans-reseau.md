# Sorties réelles (repli sans réseau)

Les TD 2 et 3 installent des paquets depuis PyPI, et le TD 1 télécharge
un second Python : sans réseau, ils s'arrêtent là. Les sorties ci-dessous
sont celles, exactes, d'un poste macOS avec uv 0.10.0 et Python 3.14.2 le
12 septembre 2026. **Les numéros de version changent chaque mois** ; la
forme des réponses, non. Faites les fiches sur papier avec ces sorties,
et rejouez-les chez vous.

Les chemins commencent par `/Users/lou/` : chez vous, c'est votre dossier
personnel (`C:\Users\lou\` sous Windows).

## TD 1 - les Python du poste

```text
$ uv --version
uv 0.10.0 (0ba432459 2026-02-05)

$ uv python list --only-installed
cpython-3.14.2-macos-aarch64-none    /Users/lou/.local/bin/python3 -> /Users/lou/.local/share/uv/python/cpython-3.14.2-macos-aarch64-none/bin/python3
cpython-3.14.2-macos-aarch64-none    /Users/lou/.local/share/uv/python/cpython-3.14-macos-aarch64-none/bin/python3.14
cpython-3.9.6-macos-aarch64-none     /usr/bin/python3

$ which -a python3
/Users/lou/.local/bin/python3
/usr/bin/python3

$ uv python find
/Users/lou/.local/share/uv/python/cpython-3.14-macos-aarch64-none/bin/python3.14
```

`quel_python.py`, lancé par uv puis par le `python3` du shell :

```text
$ uv run manip/quel_python.py
version      : 3.14.2
exécutable   : /Users/lou/.local/share/uv/python/cpython-3.14-macos-aarch64-none/bin/python3.14
préfixe      : /Users/lou/.local/share/uv/python/cpython-3.14.2-macos-aarch64-none
dans un venv : False

$ python3 manip/quel_python.py
version      : 3.14.2
exécutable   : /Users/lou/.local/bin/python3
préfixe      : /Users/lou/.local/share/uv/python/cpython-3.14.2-macos-aarch64-none
dans un venv : False
```

Un autre Python, sans rien casser :

```text
$ uv run --python 3.13 manip/quel_python.py
Downloading cpython-3.13.12-macos-aarch64-none (download) (16.9MiB)
 Downloaded cpython-3.13.12-macos-aarch64-none (download)
version      : 3.13.12
exécutable   : /Users/lou/.local/share/uv/python/cpython-3.13.12-macos-aarch64-none/bin/python3.13
préfixe      : /Users/lou/.local/share/uv/python/cpython-3.13.12-macos-aarch64-none
dans un venv : False
```

## TD 2 - un projet neuf

```text
$ uv init algo3
Initialized project `algo3` at `/Users/lou/projets/algo3`

$ cd algo3 && ls -a
.  ..  .git  .gitignore  .python-version  README.md  main.py  pyproject.toml

$ cat pyproject.toml
[project]
name = "algo3"
version = "0.1.0"
description = "Add your description here"
readme = "README.md"
requires-python = ">=3.14"
dependencies = []

$ cat .python-version
3.14

$ uv run main.py
Using CPython 3.14.2
Creating virtual environment at: .venv
Hello from algo3!

$ ls -a
.  ..  .git  .gitignore  .python-version  .venv  README.md  main.py  pyproject.toml  uv.lock

$ ls .venv
CACHEDIR.TAG  bin  lib  pyvenv.cfg

$ cat .venv/pyvenv.cfg
home = /Users/lou/.local/share/uv/python/cpython-3.14-macos-aarch64-none/bin
implementation = CPython
uv = 0.10.0
version_info = 3.14.2
include-system-site-packages = false
prompt = algo3

$ uv run ../manip/quel_python.py
version      : 3.14.2
exécutable   : /Users/lou/projets/algo3/.venv/bin/python3
préfixe      : /Users/lou/projets/algo3/.venv
dans un venv : True
```

Activer, ou pas :

```text
$ echo $PATH | cut -d: -f1
/Users/lou/.local/bin
$ source .venv/bin/activate
(algo3) $ echo $PATH | cut -d: -f1
/Users/lou/projets/algo3/.venv/bin
(algo3) $ which python
/Users/lou/projets/algo3/.venv/bin/python
(algo3) $ deactivate
$ .venv/bin/python ../manip/quel_python.py
version      : 3.14.2
exécutable   : /Users/lou/projets/algo3/.venv/bin/python
préfixe      : /Users/lou/projets/algo3/.venv
dans un venv : True
```

## TD 2 - requests, deux fois

```text
$ uv add requests
Resolved 6 packages in 1.44s
Prepared 2 packages in 217ms
Installed 5 packages in 25ms
 + certifi==2026.7.22
 + charset-normalizer==3.5.1
 + idna==3.19
 + requests==2.34.2
 + urllib3==2.7.0

$ cat pyproject.toml
[project]
name = "algo3"
version = "0.1.0"
description = "Add your description here"
readme = "README.md"
requires-python = ">=3.14"
dependencies = [
    "requests>=2.34.2",
]

$ uv tree
Resolved 6 packages in 7ms
algo3 v0.1.0
└── requests v2.34.2
    ├── certifi v2026.7.22
    ├── charset-normalizer v3.5.1
    ├── idna v3.19
    └── urllib3 v2.7.0

$ uv pip show requests
Name: requests
Version: 2.34.2
Location: /Users/lou/projets/algo3/.venv/lib/python3.14/site-packages
Requires: certifi, charset-normalizer, idna, urllib3
Required-by:

$ uv run version_pypi.py requests
paquet            : requests
dernière version  : 2.34.2
versions publiées : 163
résumé            : Python HTTP for Humans.
requests utilisé  : 2.34.2
```

Dans `vieux-projet`, avec `requests==2.25.1` :

```text
$ uv add "requests==2.25.1"
Using CPython 3.14.2
Creating virtual environment at: .venv
Resolved 6 packages in 905ms
Prepared 4 packages in 241ms
Installed 5 packages in 9ms
 + certifi==2026.7.22
 + chardet==4.0.0
 + idna==2.10
 + requests==2.25.1
 + urllib3==1.26.20

$ uv tree
Resolved 6 packages in 5ms
vieux-projet v0.1.0
└── requests v2.25.1
    ├── certifi v2026.7.22
    ├── chardet v4.0.0
    ├── idna v2.10
    └── urllib3 v1.26.20

$ uv run ../algo3/version_pypi.py requests
paquet            : requests
dernière version  : 2.34.2
versions publiées : 163
résumé            : Python HTTP for Humans.
requests utilisé  : 2.25.1
```

Hors de tout projet :

```text
$ python3 -c "import requests"
Traceback (most recent call last):
  File "<string>", line 1, in <module>
    import requests
ModuleNotFoundError: No module named 'requests'
```

## TD 3 - remove, sync

```text
$ uv remove requests
Resolved 1 package in 35ms
Uninstalled 5 packages in 43ms
 - certifi==2026.7.22
 - charset-normalizer==3.5.1
 - idna==3.19
 - requests==2.34.2
 - urllib3==2.7.0

$ uv pip list
(rien)

$ uv add requests
Resolved 6 packages in 17ms
Installed 5 packages in 19ms
 + certifi==2026.7.22
 + charset-normalizer==3.5.1
 + idna==3.19
 + requests==2.34.2
 + urllib3==2.7.0

$ grep '^name = \|^version = ' uv.lock
version = 1
name = "algo3"
version = "0.1.0"
name = "certifi"
version = "2026.7.22"
name = "charset-normalizer"
version = "3.5.1"
name = "idna"
version = "3.19"
name = "requests"
version = "2.34.2"
name = "urllib3"
version = "2.7.0"

$ rm -rf .venv
$ uv sync
Using CPython 3.14.2
Creating virtual environment at: .venv
Resolved 6 packages in 1ms
Installed 5 packages in 17ms
 + certifi==2026.7.22
 + charset-normalizer==3.5.1
 + idna==3.19
 + requests==2.34.2
 + urllib3==2.7.0

$ uv sync
Resolved 6 packages in 5ms
Audited 5 packages in 0.61ms
```

## TD 3 - le contrat qui ment

```text
$ uv sync
Using CPython 3.14.2
Creating virtual environment at: .venv
  × No solution found when resolving dependencies:
  ╰─▶ Because there is no version of cowsay==999.0 and your project depends
      on cowsay==999.0, we can conclude that your project's requirements are
      unsatisfiable.
```

Après correction de la première ligne (`cowsay==6.1`) :

```text
  × No solution found when resolving dependencies:
  ╰─▶ Because richh was not found in the package registry and your project
      depends on richh==15.0.0, we can conclude that your project's
      requirements are unsatisfiable.
```

Après correction de la seconde (`rich==15.0.0`) :

```text
$ uv sync
Resolved 6 packages in 836ms
Prepared 1 package in 575ms
Installed 5 packages in 61ms
 + cowsay==6.1
 + markdown-it-py==4.2.0
 + mdurl==0.1.2
 + pygments==2.21.0
 + rich==15.0.0

$ uv tree
Resolved 6 packages in 4ms
tableau-de-bord v0.1.0
├── cowsay v6.1
└── rich v15.0.0
    ├── markdown-it-py v4.2.0
    │   └── mdurl v0.1.2
    └── pygments v2.21.0

$ uv run tableau.py
Atelier prêt : les deux paquets répondent.
  ____________
| Atelier prêt |
  ============
            \
             \
               ^__^
               (oo)\_______
               (__)\       )\/\
                   ||----w |
                   ||     ||
```

## TD 3 - prêt à cloner

```text
$ git status
On branch main

No commits yet

Untracked files:
	.gitignore
	.python-version
	README.md
	main.py
	pyproject.toml
	uv.lock
	version_pypi.py
```

`.venv/` n'apparaît pas : `uv init` l'a mis dans `.gitignore` dès le départ.
