Considérations générales sur le vote en ligne
*********************************************

Il nous semble important de préciser ici que **GvoT** est une solution de vote
en ligne et que, à ce titre, il faut être conscient des limites d'un tel outil.

A fortiori, **GvoT** est conçu pour des besoins typiques d'un contexte de prises
de décisions formelles. Le caractère d'urgence et de force majeur que nous
impose la crise du COVID19 pourrait sembler justifier quelques libertés prises
avec la forme d'un scrutin. Après tout, pourrait on se dire, « *papier ou
électronique, quelle différence cela fait pour les participants au vote ?* »

Néanmoins il se trouve qu'un scrutin électronique n'a pas les propriétés d'un
scrutin à bulletin secret dans une urne transparente et il faut en être
conscient. À ce titre, il n'offre pas du tout les mêmes garanties (voir par
exemple l’`excellente synthèse
<https://wiki.april.org/w/Discussion_vote_%C3%A9lectronique>`_ de
l’`April <https://april.org/>`_ sur le sujet). Le fait que **GvoT** soit
un logiciel libre ne protège pas de tous les risques de manipulation.

Difficultés techniques
======================

Compromis contrôlabilité/traçabilité
------------------------------------

La nature d'un scrutin en ligne est différente de celui impliquant une urne
physique. En particulier, il n'existe aucune méthode connue permettant à la
fois :

* Le **contrôle** du scrutin par les participant⋅e⋅s (vérifier que ce tous les
  votes sont pris en compte et seulement eux).

* La **non-traçabilité** du scrutin (préservation de l'anonymat des
  participant⋅e⋅s).

En l'état de l'art, cette aporie est un problème théorique ouvert qui ne
possède pas à notre connaissance de solution technologique (y compris à base de
chiffrement et/ou autre blockchain).

Le chiffrement n'est pas une solution, notamment car il ne protège pas contre
le bourrage d'urnes. Contrôler un scrutin ne se limite pas à ce que je contrôle
que mon expression est prise en compte. Cela implique aussi de contrôler que
l'expression de chacun et seulement elle est prise en compte.

La conséquence est qu'en cas de réclamation, la seule manière possible
d'établir les faits est d'ouvrir le scrutin afin que **chacun** puisse
**contrôler** que **tous les votes** sont pris en compte et **seulement eux**.
Cela s'apparenterait à « rejouer » le scrutin, à main levée.

L'ouverture du scrutin doit donc pouvoir être demandée à l'organisateur.
L'intégralité des personnes devraient alors recevoir un accès à l'intégralité
des données propres au scrutin concerné. 

Dépendance à la technologie email
---------------------------------

Pour des raisons de rapidité d'organisation et d'interopérabilité, l'envoi des
pouvoirs se fera par courriel.

Un hébergeur de **GvoT** devrait s'engager à une obligation de moyen pour
permettre au mieux la délivrance des pouvoirs aux adresses destinataires par
courriel.

Néanmoins, du fait de la nature décentralisée des protocoles de courriels et de
la difficulté majeure de vérifier des identités en ligne :

* Les hébergeurs ne peuvent garantir que les courriels seront **présentés** aux
  personnes jugées légitimes. Hors de notre périmètre, nous ne contrôlons pas
  que le courriel atterrit dans le dossier des courriels à lire en urgence.

* Les hébergeurs ne peuvent garantir que les courriels envoyés **seront lus**
  par les personnes jugées légitimes. Hors de notre périmètre nous ne
  contrôlons  pas que les personnes relèvent la bonne boite.

* Les hébergeurs ne peuvent garantir que les courriels envoyés seront lus **par
  les seules personnes** jugées légitimes. Rien n'empêche les fuites
  d'information et donc la fuite des pouvoirs.

Conseils aux usagers
====================

La coopérative Cliss XXI reconnaît la nature particulièrement sensible des
données et des résultats d'un scrutin d'assemblée générale, de modification de
statut ou d'un règlement intérieur.

À ce titre elle insiste sur ce qui fait la bonne tenue d'un scrutin au travers
3 axes : ouverture, transparence et neutralité.

`<Ouverture>`_ car le logiciel est libre. `<Transparence>`_ des pratiques et
reconnaissance des limitations existantes. `<Neutralité>`_ par déontologie,
en tant que prestataire technique d'hébergement tel que défini par la
loi sur la confiance en l'économie numérique (LCEN).

Ouverture
---------

**GvoT** est un logiciel libre : sous licence `GNU Affero GPL
<https://forge.cliss21.org/cliss21/gvot/src/branch/master/LICENSE>`_. Une
disposition spéciale de cette licence est que tout utilisateur⋅ice du logiciel
est en droit d'obtenir une copie de son code source avec les permissions
usuelles du logiciel libre (droits d'usage, d'étude, de modification, de
redistribution).

Le code du logiciel est disponible sur la `forge de Cliss XXI
<https://forge.cliss21.org/cliss21/gvot>`_ .

Un hébergeur de **GvoT** devrait s’engager sur l'honneur à ce que le code
utilisé pour le vote soit celui publié et librement auditable par ailleurs.

Un hébergeur de **GvoT** devrait s’engager sur l’honneur à ce que l'accès aux
données du vote ne soit accessible à aucune autre application que la présente
plateforme hébergée ainsi que le socle technique qui la porte.

La procédure de vote et d'administration du vote sur le site web devrait être
protégée par le chiffrement **TLS** en vigueur au moment du vote (TLS version
1.2 ou 1.3 au moment du COVID19). Il s’agit d’un standard international
recommandé et conforme aux préconisations de l'ANSSI.

Transparence
------------

Un hébergeur de **GvoT** devrait reconnaître les limites technologiques et
déontologiques qui affectent le vote en ligne pour un scrutin à bulletin
secret.

Un hébergeur de **GvoT** devrait s’engager sur l'honneur à ce que les données
du scrutin soient recueillies dans le seul but décrit en introduction du
scrutin.  En conséquence ces données ainsi que celles recueillies dans le cadre
du vote ne seraient pas utilisées à d’autres fins ni transmises à un tiers.

Un hébergeur de **GvoT** devrait s’engager sur l'honneur en accord avec
l'organisateur, à ce que ces données **soient détruites** une fois le scrutin
passé, et dans tous les cas au plus tard un certain nombre de jours après la
fin de la tenue du scrutin.

Dans tous les cas, les participant⋅e⋅s disposent d’un droit d’accès, de
modification, de rectification et de suppression des données les concernant
(loi « Informatique et Liberté » du 6 janvier 1978).

Un hébergeur de **GvoT** devrait s’engager sur l’honneur à ne pas cacher la
détection d'un comportement anormal s'il était détecté (piratage, fuite
accidentelle d'informations, etc.).

Neutralité
----------

Un hébergeur de **GvoT** devrait s'engager à une obligation de moyens pour
permettre la tenue du scrutin dans les meilleurs conditions.

Cela implique, de façon non exhaustive à :

* suivre l'expédition des courriels d'annonce,
* veiller à la disponibilité de la plateforme aux heures ouvrées pendant la
  durée du scrutin,
* répondre aux demandes d'assistance des utilisateur⋅ices.

Un moyen d'accéder à l'assistance devrait être précisée sur la plateforme de
vote ainsi que dans chaque courriel expédié aux participant⋅e⋅s.

Un hébergeur de **GvoT** devrait s'engager sur l'honneur à ne procéder à aucune
intervention qui soit de nature à biaiser l'issue du scrutin. Les éventuelles
interventions se feront uniquement sous la forme d'une assistance avec une
éventuelle intervention qui sera strictement proportionnée à la demande de la
personne assistée dans le vote.

En cas d'intervention impliquant les données du scrutin, un journal des
interventions devrait être tenu avec soin.
