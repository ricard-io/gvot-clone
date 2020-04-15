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

Sur le serveur de production :

::

    $ ./venv/bin/python manage.py createsuperuser
    Adresse mail: admin@example.org
    Password: •••••••••••••
    Password (again): •••••••••••••
    Superuser created successfully.


Utilisation du compte administrateur
====================================

L'accès à l'administration se fait à l'emplacement `/admin`.

Une fois connecté avec le compte administrateur, le CMS Wagtail est pleinement
utilisable.

.. note:: 

  À partir d'ici, nous recommandons fortement de découvrir la `documentation de
  Wagtail <https://docs.wagtail.io/en/v2.7/editor_manual/index.html>`_ avant de
  poursuivre.

Spécificités CMS de **GvoT** par rapport à Wagtail
==================================================

Blocs éditoriaux
^^^^^^^^^^^^^^^^

Les pages de base de **GvoT** tirent parti des `streamfields` pour leur contenu
principal.

Vous pouvez dans toute page et dans tous scrutins ajouter les blocs éditoriaux
suivants : titre, paragraphe, bouton, image, contenu embarqué.

Ces pages doivent vous permettre de publier tout contenu utile au tour du
service : présentation, aide, accès à l'assistance, etc.

Paramétrage des menus
^^^^^^^^^^^^^^^^^^^^^

**GvoT** dispose de deux menus additionnels paramétrables dans l'interface :

* le menu principal (sur la barre supérieure) ;
* le menu secondaire (pied de page).

Ces menus doivent vous permettre de mettre en valeur n'importe quelle page
servant à la présentation du service. De fait, les scrutins étant temporaires
et n'étant pas publics n'ont pas vraiment leur place ici.

Gestion des scrutins dans **GvoT**
==================================

Ajout d'un index des scrutins
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Avant de pouvoir ajouter des scrutins dans **GvoT** vous allez devoir ajouter
une page de type « Liste des scrutins ». Cette manipulation sert simplement à
définir le point d'ancrage pour les scrutin, dans l'arbre des page de Wagtail.

Il suffit de choisir un emplacement dans
les pages, d'ajouter une page, choisir le bon type, donner un titre et publier.

Ajout d'un scrutin
^^^^^^^^^^^^^^^^^^

Vous pouvez ajouter un scrutin via la liste des pages (dans le contexte de la
« Liste des scrutins »), ou directement depuis le panel « Scrutins ».

Un scrutin possède de nombreux attributs dont les principaux sont dans l'onglet
« détail ». Ces attributs sont documentés dans l'interface.

Le questionnaire du scrutin est paramétrable dans l'onglet « Questionnaire ».

Des détails techniques restent paramétrables dans les onglets « Promotion » et
« Paramètres ».

Ajout des pouvoirs
^^^^^^^^^^^^^^^^^^

Un pouvoir est un droit de vote, pondéré, associé à un scrutin. Pour des
raisons d'organisation on y adjoint les noms, prénom et moyens de contact des
participants.

Vous pouvez ajouter un pouvoir directement depuis le panel « Pouvoirs ».

Importation des pouvoirs
^^^^^^^^^^^^^^^^^^^^^^^^

Vous pouvez démarrer une importation de pouvoirs, directement depuis le panel
« Pouvoirs ».

Le format d'entrée doit être un fichier « CSV » dans un codage utf-8 ;
séparateur : « , » ; délimiteur de texte : « " » (doubles quotes). Un exemple
est proposé au téléchargement.

Les colonnes attendues sont : « nom », « prenom », « courriel », « contact » et
« ponderation ».

Les colonnes « nom », « prenom » et « courriel » ne peuvent être vides.

Une pondération absente sera interprétée à la valeur « 1 ».

Une fois votre fichier téléversé, les entrées du fichier vont être validées
unes à unes et les erreurs ou les alertes vous seront rapportées. Une
prévisualisation de l'importation vous sera également présentée.

C'est seulement après avoir validé la prévisualisation que l'import sera
effectué.

Expédition d'un mailling
^^^^^^^^^^^^^^^^^^^^^^^^

Vous pouvez démarrer un mailling pour expédier les pouvoirs, directement depuis
le panel « Pouvoirs ».

Une fois les modalités d'envois définies, une confirmation avec
prévisualisation du mailling vous sera présentée.

.. note::

  La prévisualisation nécessite que vous ayez renseigné les champs « prénom »
  et « nom » de votre profil d'utilisateur dans l'interface.

C'est seulement après avoir validé la prévisualisation que l'expédition sera
programmée.
