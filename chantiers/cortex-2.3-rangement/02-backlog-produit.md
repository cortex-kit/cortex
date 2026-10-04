# 02 : Backlog produit

## Valeur utilisateur

| Profil | Ce que le rangement change pour la personne |
|---|---|
| Employé | Ses dossiers portent des noms qu'elle et son assistant comprennent. Ses procédures à elle restent chez elle ; celles de l'entreprise sont lues dans le dossier commun, à jour, sans copie. |
| Dirigeant | Il range une fois les documents qui font tourner l'entreprise (procédures, charte, signatures, modèles), au même endroit, avec un index que toute IA lit. Ses collaborateurs et leurs assistants lisent la même version. |
| Société | Chaque rédacteur pointe vers le même référentiel ; le commun fédéré le cite. Une procédure n'existe qu'en un exemplaire. |

## Parcours

1. Fin du maillon 3 : la carte des domaines est signée. Le message de fin propose d'abord « rangeons mes dossiers », puis rappelle qu'on peut passer directement à « construis mon second cerveau ».
2. « rangeons mes dossiers » : Cortex parcourt les dossiers déclarés et rend un résumé à l'écran.

   > J'ai relevé 37 changements possibles dans vos dossiers : 22 noms illisibles à renommer, 9 procédures à regrouper, 6 fichiers à sortir du dossier « Divers ». Rien n'est supprimé, rien n'est copié, tout peut être défait. On les regarde quatre par quatre ?

3. Lots de quatre lignes, chacune visible en entier avant la question : avant, après, raison.

   > 1. `Nouveau document (3).docx` devient `Accueil d'un nouveau client - 2026-03-12.docx` (nom illisible ; titre lu dans le document)
   > 2. ...

   Choix multiple : la personne coche les lignes qu'elle garde. Une ligne non cochée ne se fait pas.
4. Lignes qui touchent un dossier partagé : un lot à part, après les autres, avec la phrase « D'autres personnes travaillent dans ce dossier : leurs liens et leurs raccourcis vers ces fichiers ne marcheront plus. » La confirmation est séparée de la première.
5. Procédures au classement douteux : « Cette procédure vaut-elle pour toute l'entreprise, ou c'est votre façon de faire à vous ? »
6. Référentiel :
   - existant : « Votre dossier commun garde son organisation. J'y ajoute un sommaire que toute IA lira avant de répondre sur une procédure, la charte ou les signatures. » Le sommaire s'affiche en entier avant l'accord.
   - absent : « Votre entreprise n'a pas de dossier commun pour ses procédures. Je peux en créer un dans [espace partagé] et y ranger les 6 procédures qui valent pour tous. Voyez avec qui de droit avant de dire oui. »
7. Gestes manuels (entre deux espaces différents) : une liste « à faire vous-même dans OneDrive / Drive », avec le chemin de départ et d'arrivée. Cortex vérifie à la demande.
8. Base en ligne : « Votre base de projets gagnerait à … » ; proposition affichée, la personne l'applique, rien ne s'écrit dans la base.
9. Fin : bilan affiché (faits, refusés, manuels en attente), notice ouverte, phrase suivante « construis mon second cerveau ». « annule le rangement » défait tout, à tout moment avant la construction.

## Décisions métier actées dans cette phase

- Le rangement se propose, il ne s'impose pas : un refus entier vaut décision et s'inscrit (`arbitre`, raison « refusé »).
- Un nom proposé reprend le vocabulaire des domaines décidés au maillon 3 quand un domaine s'applique ; aucun préfixe de code n'est imposé aux dossiers existants.
- Un document « en ligne seulement » ne s'ouvre pas : si son nom ne se déduit pas du dossier, la ligne demande le nom à la personne.
- Le propriétaire d'un document dans l'index se demande ; sans réponse, il s'écrit `Non renseigné`.
- Un doublon probable (même nom, même taille, deux endroits) se signale, ne se supprime pas.

## Mots

Devant la personne, jamais : racine, journal, plan, JSON, geste, référentiel, AGENTS.md, régime, pointeur, profil (doctrine §8). On dit : vos dossiers, la liste des changements, le dossier commun, le sommaire pour les IA, défaire.

## Hors scope produit

Voir `01-cadrage.md`, non-objectifs. En plus : aucune vue nouvelle dans la notice HTML au-delà de l'entrée de l'étape et de sa phrase.
