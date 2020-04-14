Guide d'administration
**********************

Cette documentation couvre l'administration de l'application par les
administrateurs.

.. toctree::
   :maxdepth: 1


Créer un compte administrateur
==============================

Il est conseillé de créer un compte dédié à l'administration, qui doit être
utilisé avec la plus grande parcimonie.

Sur le serveur de production :

::

    $ ./venv/bin/python manage.py createsuperuser
    Adresse mail: admin@example.org
    Password: •••••••••••••
    Password (again): •••••••••••••
    Superuser created successfully.


Utilisation du compte administrateur
====================================

L'accès à l'administration se fait à l'emplacement `/admin`.

Une fois connecté avec le compte administrateur, le CMS Wagtail est utilisable
comme `indiqué dans sa documentation
<https://docs.wagtail.io/en/v2.7/editor_manual/index.html>`_.

Spécificités CMS de GvoT par rapport à Wagtail
==============================================

Gestion des scrutins dans GvoT
==============================

Ajout d'un index des scrutins
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Ajout d'un scrutin
^^^^^^^^^^^^^^^^^^

Ajout des pouvoirs
^^^^^^^^^^^^^^^^^^

Importation des pouvoirs
^^^^^^^^^^^^^^^^^^^^^^^^

Expédition d'un mailling
^^^^^^^^^^^^^^^^^^^^^^^^
