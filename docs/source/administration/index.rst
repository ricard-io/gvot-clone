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

L'accès à l'administration se fait à l'emplacement ``/admin``.

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

Une fois le scrutin créé, des modèles de courriels sont créés et assignés
au scrutin. Il est possible de les gérer dans le panel « Modèles de courriels ».

Ajout des pouvoirs
^^^^^^^^^^^^^^^^^^

Un pouvoir est un droit de vote, pondéré, associé à un scrutin. Pour des
raisons d'organisation on y adjoint les noms, prénom (ou bien nom du collectif,
le cas échéant) et moyens de contact des participants.

Dans le cas d'un pouvoir destiné à un collectif,

Vous pouvez ajouter un pouvoir directement depuis le panel « Pouvoirs ».

Importation des pouvoirs
^^^^^^^^^^^^^^^^^^^^^^^^

Vous pouvez démarrer une importation de pouvoirs, directement depuis le panel
« Pouvoirs ».

Le format d'entrée doit être un fichier « CSV » dans un codage utf-8 ;
séparateur : « ``,`` » ; délimiteur de texte : « ``"`` » (doubles quotes). Un
exemple est proposé au téléchargement.

Les colonnes attendues sont : « nom », « prenom », « collectif » « courriel »,
« contact » et « ponderation ».

Les colonnes « nom », « prenom » et « collectif » ne peuvent être vides toutes
à la fois. Dit autrement le pouvoir doit au moins désigner un nom, un prénom
ou un nom de collectif.

La colonne « courriel » ne peut être vide.

Une pondération absente sera interprétée à la valeur « 1 ».

Une fois votre fichier téléversé, les entrées du fichier vont être validées
unes à unes et les erreurs ou les alertes vous seront signalées. Une
prévisualisation de l'importation vous sera également présentée.

C'est seulement après avoir validé la prévisualisation que l'import sera
effectué.

Modèles de courriels
^^^^^^^^^^^^^^^^^^^^

Vous pouvez personnaliser vos modèles d'emails et en définir de nouveaux via
le panel « Modèles de courriels ». Un modèle doit avoir un nom, être lié à un
scrutin, et posséder un sujet et un contenu texte. Il est aussi possible
d'associer un contenu HTML qui sera présenté au format `multipart/alternative
<https://fr.wikipedia.org/wiki/Multipurpose_Internet_Mail_Extensions#alternative>`_.

Les différents champs qui composent le courriel peuvent tirer parti du moteur
de gabarit de django. Sa documentation est accessible ici :
`<https://docs.djangoproject.com/fr/3.0/ref/templates/language/>`_

FIXME: retreindre à une liste fermée de variables.
Le contexte des gabarits est chargé avec les variables suivantes :
- pouvoir
- request
- settings

**GvoT** réserve pour chaque scrutin un modèle de courriel servant à la
confirmation des votes auprès des participants. Ce modèle est éditable et peut
être configuré dans l'onglet « Paramètres » du scrutin. Il est possible
également de le supprimer ou le déconfigurer pour que les participants ne
recoivent pas de confirmation.

Expédition d'un courriel
^^^^^^^^^^^^^^^^^^^^^^^^

Vous pouvez envoyer un courriel à un participant, directement depuis le panel
« Pouvoirs ».

Une fois les modalités d'envoi définies, une confirmation avec
prévisualisation du mailing vous sera présentée.

C'est seulement après avoir validé la prévisualisation que l'expédition sera
programmée.

Expédition d'un mailing
^^^^^^^^^^^^^^^^^^^^^^^

Vous pouvez démarrer un mailing d'annonce, directement depuis le panel
« Pouvoirs ».

Une fois les modalités d'envoi définies, une confirmation avec
prévisualisation du mailing vous sera présentée.

.. note::

  La prévisualisation nécessite que vous ayez renseigné les champs « prénom »
  et « nom » de votre profil d'utilisateur dans l'interface.

C'est seulement après avoir validé la prévisualisation que l'expédition sera
programmée.
