Présentation
************

**GvoT** est une application Web visant à permettre le vote en ligne à
large échelle dans les organisation.

**GvoT** est né d’un besoin pendant la crise du COVID19 : permettre
l'organisation de votes d'assemblées générales en ligne pour les collectifs
démocratiques d'envergure régionale voire nationale.

**GvoT** est né d’une coopération entre acteurs qui ont convergé quant
aux besoins de leurs membres et qui ont décidé d’investir du temps pour que cet
outil aboutisse au-delà de leurs propres besoins et qu’il serve, d’une manière
plus générale, les associations en France.


Fonctionnalités
===============

* Permet de publier les contenus web usuels (pages, images, documents, ...) via
  un gestionnaire de contenu (`Wagtail <https://wagtail.io>`_).
* Permet de publier des questionnaires en ligne, les « scrutins ».
* Permet un vote à bulletin secret, :doc:`avec les limites que cela implique
  <considerations>`.
* Permet de gérer tout type de question dans l'interface (texte libre, choix
  unique, choix multiples, etc.).
* Permet de gérer les « pouvoirs » donnant accès au scrutin. L'interface est
  conçue pour gérer des milliers de pouvoirs.
* Permet l'importation des pouvoirs depuis un fichier tableur, avec
  dédoublonnage et validateur intégré.
* Permet la transmission des pouvoirs par courriel avec une prévisualisation
  des courriels envoyés.
* Permet de pondérer les pouvoirs pour les organisations de type fédération qui
  le nécessitent.
* Permet au participant de revenir vérifier et corriger son choix.
* Notifie le participant de son vote.
* Permet de notifier par courriel un tiers à chaque vote.

Ne sont pas encore implantés dans le logiciel :

* Gestion des collèges.
* Personnalisation des gabarits de courriels dans l'interface.

Pourquoi **GvoT** ?
===================

Habituellement, les rencontres physiques sont des moments privilégiées de la
vie associative et peu d'organisations ont recours au vote en ligne. Seule
éventuellement des grosses organisations d'envergures nationales y recourent
pour augmenter leur participation et atteindre un quorum.

Néanmoins la crise du COVID19 fait émerger le besoin de valider en urgence
et à distance des décisions d'assemblées, pour faire face par exemple à des
obligations statutaires ou des contraintes budgétaires.

Pour répondre à ce besoin, Cliss XXI a choisi de développer et de mettre à
disposition un outil dédié : **GvoT**. Cet outil est destiné principalement
aux moyennes et grosses associations. Il est cependant libre et peut donc
être déployé partout où le besoin s'en ferait sentir.

Qui est à l'origine de **GvoT** ?
=================================

`Cliss XXI <https://www.cliss21.com>`_ est une SCIC (société coopérative
d’intérêt collectif). Son objectif d’utilité sociale consiste à accompagner
le développement technologique des PME-PMI, des collectivités territoriales et
des associations de la région, en aidant leurs personnels (utilisateurs et
informaticiens) à comprendre quels usages ils peuvent faire des logiciels libres,
et à développer avec eux des solutions concrètes.

Il nous semble important de préciser ici que **GvoT** est né d’une demande de
la Ligue de l'Enseignement du Pas de Calais, et s'enrichie par ailleurs des
pratiques connues des organisations du logiciel libre, notamment celles de
l’`April <https://april.org/>`_ (voir par exemple leur `excellente synthèse
<https://wiki.april.org/w/Discussion_vote_%C3%A9lectronique>`_ sur le sujet).
