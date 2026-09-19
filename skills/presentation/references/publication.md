# Publier un deck sur le cockpit

Un deck bento est **un seul fichier HTML autoportant** : il entre tel quel dans
le canal `/l/*` du cockpit (lien signé, `noindex`, expiration). C'est ce qui
rend le format intéressant ici — le destinataire reçoit un lien, pas une pièce
jointe de 40 Mo, et il n'installe rien.

## Les notes orateur partent avec le fichier

Elles voyagent dans le document et la vue orateur les affiche : **tout ce qui est
écrit en note est lisible par le destinataire.** C'est facile à oublier parce
qu'on les écrit pour soi, en langage de travail — et c'est exactement ce qui les
rend gênantes une fois transmises. Les formes à surveiller : un point de
désaccord anticipé avec l'interlocuteur qu'on nomme, un retard imputé à son
équipe, une intention commerciale, une réserve qu'il a exprimée et qu'on lui
ressort. Rien d'inavouable — mais des notes de consultant sur son interlocuteur,
envoyées à cet interlocuteur.

Avant de produire un fichier de remise, **relire les notes et les réécrire pour
celui qui va lire** — une note tournée vers le lecteur reste utile, elle explique
au lieu de commenter. C'est pour ça que `document(readonly=True)` refuse de
produire tant que `notes_publiques=True` n'est pas passé : l'oubli ne se voit
pas, et il devient irréversible dès que le lien est transmis.

Le fichier de travail, lui, garde ses notes de travail. Deux fichiers, deux
publics.

## La règle qui prime sur tout : publier une copie read-only

Le document livré par ce skill ne porte **ni `docId` ni `collab`** ; le contrôle
de `bento.py` le refuse autrement. Mais **dès que le fichier est ouvert et
enregistré**, l'application forge son identité et des identifiants de
collaboration dormants. Ils vivent alors dans le fichier.

C'est par conception : le fichier *est* l'invitation, c'est ce qui permet de
partager une session sans compte. La conséquence se rate facilement, parce que
rien dans un document ne ressemble à un identifiant : **publier un fichier de
travail, c'est distribuer avec le lien la clé qui permet d'écrire dedans.**

Donc, avant toute publication :

1. Ouvrir le deck, **Save ▾ → Save read-only copy…**
2. Publier cette copie-là. Elle démarre directement en présentation, sans
   éditeur — ce qui est de toute façon ce qu'on veut envoyer à un client.
3. Le fichier de travail reste en local, c'est lui qu'on rouvre pour corriger.

Vérification : `window.bento.validate()` signale `collab-secrets-present`.
Retirer les clés après coup ne les révoque pas — si un deck partagé est déjà
parti, le seul remède est **Share → Rotate keys**, qui invalide l'ancienne
session.

## Le passage de relais vers /publier

Ne pas réimplémenter la publication. `/publier` porte les treize étapes, la
signature du jeton, le manifeste, l'attente Vercel et le contrôle de l'URL
vivante. Ce skill s'arrête au fichier ; `/publier` prend la suite.

Ce qu'il attend et qu'il faut préparer :

- **Un `.html`** — un `.bento.html` en est un, aucune adaptation nécessaire.
- **Un slug** conforme à `^[a-z0-9]+(-[a-z0-9]+)*$` : c'est le nom du fichier
  sans extension. Nommer le fichier en conséquence dès la génération évite une
  question de plus. Attention : `mon-deck.bento.html` donne le slug
  `mon-deck.bento`, que le point rend non conforme — **nommer sans point interne**
  (`mon-deck.html`) quand le deck est destiné à la publication.
- **Un `<title>`** — bento le renseigne depuis `doc.title`.
- **Une marque** : `mia`, `devprom`, `vde` ou `perso`. Elle doit correspondre à
  la charte utilisée pour composer le deck. Un deck en charte VDE publié sous
  marque `mia` est une incohérence visible par le destinataire.
- **Un espace** (2ᵉ segment de l'URL) : le client en mode projet, un slug libre
  sinon.

Deux points de contrôle appartiennent à `/publier` et ne se contournent pas :
la validation avant `push origin main`, et le contrôle anti-fuite sur marque
`perso` (le HTML ne doit contenir aucune mention Mister IA). Ce dernier compte
double ici : un deck contient beaucoup de texte, y compris dans les **notes
orateur**, qui voyagent dans le fichier et que personne ne relit avant
publication. Relire les notes avant de publier en marque `perso`.

## Le chemin vers Canva

Deux voies, et la première suffit dans la plupart des cas.

**Import manuel du PPTX** — la voie nominale, et elle suffit à tout.
`python3 scripts/rendu_pptx.py <deck>` produit un fichier en formes natives ;
on le glisse dans Canva. Dix secondes, aucune dépendance, comportement
prévisible. C'est le geste déjà pratiqué avec `claudia-6`.

Éprouvé de bout en bout sur un témoin, et voici ce qui a été vérifié dans
Canva après import : les formes restent **éditables** (on change la couleur
d'une carte), le graphique reste **modifiable** (ses données s'ouvrent, il
n'est pas figé), les **notes orateur survivent**, et les polices de charte sont
respectées sans substitution. Rien ne se perd de ce qui compte.

**Import automatique — seulement si le deck est déjà publié.** L'outil
`import-design-from-url` du connecteur Canva prend une URL et crée le design.
Il accepte le HTML, et le rendu plat porte l'annotation qu'il attend : une page
par slide (`data-document-role="page"`), le titre en `data-label`, les notes en
`data-speaker-notes`. Son seul apport réel est d'épargner le glisser-déposer :
le PPTX conservant déjà les notes, il n'y a pas de raison de fidélité de le
préférer.

La contrainte est nette et ne se contourne pas : **cet outil n'accepte que du
contenu déjà publiquement accessible**, et il est interdit de déposer un fichier
sur un service de partage pour lui fabriquer une URL — cela publierait
irréversiblement le contenu sur l'internet ouvert. Ce qui reste légitime, c'est
le cas où le deck **a déjà été publié** par `/publier` : l'URL existe alors pour
une raison métier, et l'importer n'ajoute aucune exposition.

Donc, concrètement :

| Situation | Voie |
|---|---|
| deck publié sur le cockpit | import automatique depuis son URL |
| deck local, non publié | rendu PPTX + import manuel |
| deck local qu'on ne veut pas publier | rendu PPTX + import manuel, sans exception |

Publier un deck *dans le seul but* de l'importer dans Canva n'est pas un
raccourci : c'est une publication, avec ses conséquences. Si le PPTX suffit,
c'est le PPTX.

## Quand ne pas publier

La route `/l/*` sert des liens privés destinés à être transmis à quelqu'un. Ce
n'est pas un canal de diffusion publique indexable — pour ça, un hébergement
statique est le bon outil. Et un deck de travail interne n'a pas besoin d'URL :
le fichier suffit, il s'ouvre en double-cliquant.
