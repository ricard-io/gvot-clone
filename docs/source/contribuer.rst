Contribuer
**********

Ceci est le guide de contribution pour **GvoT**, qui est basé sur Python
et Django. Si vous êtes habité au développement de logiciels libres et démarrer
rapidement, vous pouvez directement regarder la `liste des bugs et demandes de
fonctionnalités <https://forge.cliss21.org/cliss21/gvot/issues>`_.

Autrement cette section est faite pour vous.

Ressources
==========

* Dépôt et suivi de bugs : https://forge.cliss21.org/cliss21/gvot
* Forum : non défini
* Messagerie instantanée : non définie
* Licence : `AGPLv3+ <https://forge.cliss21.org/cliss21/gvot/src/branch/master/LICENSE>`_
* Contact : :doc:`voir l'équipe <equipe>`
* Pré-requis à la contribution : `Tests d'intégrations`_, `Analyse statique`_

Organisation
============

L':doc:`équipe de développement <equipe>` de **GvoT** est organisée
horizontalement.

Les contributions sont discutées puis intégrées à l'issue d'un consensus.

Il est d'usage que les contributions ne soient pas intégrées par la personne
qui les soumet, mais par une tierce personne qui vérifie la qualité et la
cohérence de la contribution.

Pour démarrer avec **GvoT**
===========================

Suivre `README.md
<https://forge.cliss21.org/cliss21/gvot/src/branch/master/README.md>`_
pour obtenir une instance de test et construire les `assets`.


Organisation du dépôt
=====================

* ``docs/`` contient la documentation.
* ``asset/`` contient les sources du `frontend`.
* ``gvot/`` contient le projet Django.
* ``gvot/settings/`` contient les réglages du projet Django.
* ``gvot/templates/`` contient les gabarits html du projet Django.
* ``gvot/<app>/`` contient l'application `<app>` du projet Django.
* ``gvot/<app>/tests`` contient les tests de l'application `<app>`.
* etc.

Tests d'intégrations
====================

S'agissant du `backend`, les tests unitaires sont bienvenus. Les tests
d'intégration sont obligatoires.

Toute contribution modifiant ou ajoutant un comportement au `backend` est a
priori attendue avec un test qui vérifie le comportement attendu, et
l'exécution suivante doit être un succès :

::

    make test

Un résumé de la couverture de test sera annoncé :

* Une contribution ne devra pas, a priori, réduire la couverture de tests.
* Une contribution ne devra pas, a priori, comporter de code non couvert.
* Le code mort résultant de potentiel traitement d'erreur est toléré.


Analyse statique
================

Toute contribution est priée de valider l'analyse statique du code.

`Backend`
^^^^^^^^^

S'agissant du `backend`, l'exécution suivante doit être un succès :

::

    make lint

Par ailleurs le code Python d'une contribution est attendu après un passage de
`Black <https://black.readthedocs.io/en/stable/>`_ pour formatter uniformément
son style. Black peut être ininstallable du fait de la version de Python de
votre système (Python < 3.6).  Dans ce cas précis il se peut que vous deviez
l'installer et l'utiliser séparément.

`Frontend`
^^^^^^^^^^

S'agissant du `frontend`, l'exécution suivante doit être un succès :

::

    npm run lint

