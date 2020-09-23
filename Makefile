# -*- mode: makefile-gmake -*-
## Définition des variables
# Le nom de l'exécutable Python à utiliser ou son chemin absolu
# (ex. : python ou python3).
PYTHON_EXE := python3
# S'il faut utiliser un environnement virtuel (y ou n).
USE_VENV := y
# Configuration de l'environnement virtuel.
VENV_DIR := venv
VENV_OPT := --system-site-packages

# Définis les chemins et options des exécutables.
PYTHON_EXE_BASENAME := $(shell basename $(PYTHON_EXE))
VENV_PYTHON := --python=$(PYTHON_EXE_BASENAME)
ifeq ($(USE_VENV), y)
  PYTHON := $(VENV_DIR)/bin/$(PYTHON_EXE_BASENAME)
  PIP := $(VENV_DIR)/bin/pip
else
  PYTHON := $(shell which $(PYTHON_EXE))
  PIP := $(shell which pip)
endif

# Détermine si black est présent.
USE_BLACK := $(shell $(PYTHON) -c 'import black; print("1")' 2>/dev/null)

# Détermine s'il faut charger le fichier de configuration.
ifneq ($(READ_CONFIG_FILE), 0)
  READ_CONFIG_FILE := 1
else
  READ_CONFIG_FILE := 0
endif

# Détermine l'environnement à utiliser.
DEFAULT_ENV := production
ifndef ENV
  ifeq ($(READ_CONFIG_FILE), 1)
      # Commence par chercher la dernière valeur de DJANGO_SETTINGS_MODULE,
      # puis de ENV s'il n'y en a pas, ou utilise l'environnement par défaut.
      ENV = $(shell \
        sed -n -e '/^DJANGO_SETTINGS_MODULE/s/[^.]*\.settings\.\([^.]*\)/\1/p' \
            -e '/^ENV/s/[^=]*=\(.*\)/\1/p' config.env 2> /dev/null \
          | tail -n 1 | grep -Ee '^..*' || echo "$(DEFAULT_ENV)")
  else
    ifdef DJANGO_SETTINGS_MODULE
      ENV = $(shell echo $(DJANGO_SETTINGS_MODULE) | cut -d. -f3)
    else
      ENV := $(DEFAULT_ENV)
    endif  # ifdef DJANGO_SETTINGS_MODULE
  endif  # ifeq READ_CONFIG_FILE
endif  # ifndef ENV

# Définis EDITOR pour l'édition interactive.
ifndef EDITOR
  ifdef VISUAL
    EDITOR := $(VISUAL)
  else
    EDITOR := vi
  endif
endif

# Définition des cibles -------------------------------------------------------

.PHONY: clean-pyc clean-build clean-static clear-venv help check check-config docs clean-docs
.DEFAULT_GOAL := help

# Commentaire d'une cible : #-> interne ##-> aide production+dev ###-> aide dev
help: ## affiche cette aide
ifeq ($(ENV), production)
	@perl -nle'print $& if m{^[a-zA-Z_-]+:[^#]*?## .*$$}' $(MAKEFILE_LIST) \
	  | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'
else
	@perl -nle'print $& if m{^[a-zA-Z_-]+:[^#]*?###? .*$$}' $(MAKEFILE_LIST) \
	  | sort | awk 'BEGIN {FS = ":.*?###? "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'
endif

clean: clean-build clean-pyc clean-static ## nettoie tous les fichiers temporaires

clean-build: ### nettoie les fichiers de construction du paquet
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info

clean-pyc: ### nettoie les fichiers temporaires python
	find gvot/ \
	  \( -name '*.pyc' -o -name '*.pyo' -o -name '*~' \) -exec rm -f {} +

clean-static: ### nettoie les fichiers "static" collectés
	rm -rf var/static

init: create-venv config.env update ## initialise l'environnement et l'application

config.env:
ifeq ($(READ_CONFIG_FILE), 1)
	cp config.env.example config.env
	chmod go-rwx config.env
	$(EDITOR) config.env
endif

update: check-config install-deps migrate static docs ## mets à jour l'application et ses dépendances
	touch gvot/wsgi.py

check: check-config ## vérifie la configuration de l'instance
	$(PYTHON) manage.py check

check-config:
	@find . -maxdepth 1 -name config.env -perm /o+rwx -exec false {} + || \
	{ echo "\033[31mErreur :\033[0m les permissions de config.env ne sont pas bonnes, \
	vous devriez au moins faire : chmod o-rwx config.env"; false; }

install-deps: ## installe les dépendances de l'application
	$(PIP) install --upgrade --requirement requirements/$(ENV).txt

migrate: ## mets à jour le schéma de la base de données
	$(PYTHON) manage.py migrate

static: ## collecte les fichiers statiques
ifeq ($(ENV), production)
	@echo "Collecte des fichiers statiques..."
	$(PYTHON) manage.py collectstatic --no-input --verbosity 0
endif

## Cibles liées à l'environnement virtuel

create-venv: $(PYTHON)

$(PYTHON):
ifeq ($(USE_VENV), y)
	virtualenv $(VENV_OPT) $(VENV_PYTHON) $(VENV_DIR)
else
	@echo "\033[31mErreur !\033[0m Impossible de trouver l'exécutable Python $(PYTHON)"
	@exit 1
endif

clear-venv: ## supprime l'environnement virtuel
	-rm -rf $(VENV_DIR)

## Cibles pour le développement

serve: ### démarre un serveur local pour l'application
	$(PYTHON) manage.py runserver

test: ### lance les tests de l'application
	$(PYTHON) -m pytest --cov --cov-report=term:skip-covered

cov: test ### vérifie la couverture de code
	$(PYTHON) -m coverage html
	@echo open htmlcov/index.html

lint: ### vérifie la syntaxe et le code python
	@$(PYTHON) -m flake8 gvot \
	  || echo "\033[31m[flake8]\033[0m Veuillez corriger les erreurs ci-dessus."
	@$(PYTHON) -m isort --check gvot \
	  || echo "\033[31m[isort]\033[0m Veuillez corriger l'ordre des imports avec : make fix-lint"
ifdef USE_BLACK
	@$(PYTHON) -m black --check gvot
endif

fix-lint: ### corrige la syntaxe et ordonne les imports python
	$(PYTHON) -m isort gvot
ifdef USE_BLACK
	$(PYTHON) -m black gvot
endif

## Cibles pour la documentation

docs: ## construit la documentation
	$(MAKE) -C docs/ html SPHINXBUILD=../$(VENV_DIR)/bin/sphinx-build

clean-docs:  ## supprime la documentation (docs/build)
	$(MAKE) -C docs/ clean SPHINXBUILD=../$(VENV_DIR)/bin/sphinx-build
