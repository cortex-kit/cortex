---
type: meta
tags:
  - memo
  - claude-code
cree: 2026-09-07
maj: 2026-09-07
---
# Mémo - Brancher ses boîtes mail

Remonte vers [[Centre]]. Comment donner à Claude l'accès à vos messageries, sur autant de
boîtes que vous voulez. Vingt minutes pour trois boîtes, aucun compte développeur, gratuit.

Dépôt et documentation à jour : https://github.com/tnemelclement/mcp-email (licence MIT).

## À vérifier avant de commencer

**Outlook, Hotmail et Microsoft 365 ne fonctionnent pas.** Microsoft a supprimé la connexion
par mot de passe sur IMAP et SMTP au profit d'un mécanisme que ce serveur ne gère pas. Vérifiez
ce point en premier : il décide de tout le reste.

Fonctionnent : Gmail et Google Workspace, iCloud, Yahoo, Infomaniak, OVH, la plupart des
serveurs d'entreprise. Il faut aussi la validation en deux étapes active sur chaque boîte, et
Node.js 18 ou plus récent (`node --version`).

## Les cinq gestes

**1. Installer.**

```bash
git clone https://github.com/tnemelclement/mcp-email.git
cd mcp-email && npm install
```

**2. Déclarer les boîtes.** `cp accounts.json.example accounts.json`, puis un bloc par boîte.
La clé du bloc (`perso`, `pro`) est le nom court par lequel vous appellerez cette boîte.

```json
{ "default": "pro",
  "accounts": {
    "pro": { "imap_host": "imap.gmail.com", "imap_port": 993,
             "smtp_host": "smtp.gmail.com", "smtp_port": 587,
             "user": "vous@societe.fr", "from": "Votre Nom <vous@societe.fr>" } } }
```

Réglages par fournisseur dans le README du dépôt. L'identifiant est l'adresse complète, sauf
sur iCloud où c'est la partie avant le `@` : cause d'échec numéro un.

**3. Un mot de passe d'application par boîte.** Sur Gmail :
https://myaccount.google.com/apppasswords. Coller les seize caractères sans les espaces.

```bash
python3 set-password.py pro
```

Saisie masquée, écriture dans un `.env` lisible par vous seul. Jamais le mot de passe du
compte : celui d'application se révoque en un clic sans toucher à votre connexion.

**4. Brancher.**

```bash
claude mcp add -s user email -- npx tsx /chemin/absolu/vers/mcp-email/src/index.ts
```

**5. Vérifier.** Demandez « liste mes comptes email ». Si les noms courts apparaissent, c'est
fini.

## Ce que ça change dans le vault

Le mail devient une source d'ingest comme une autre : recherche sur plusieurs boîtes à la fois,
brouillons préparés depuis la bonne adresse, classement automatique. Douze opérations
disponibles, du listage à la pièce jointe.

Claude peut lire **et** écrire, dans des limites précises. Aucun outil ne supprime un message :
la suppression n'existe pas dans ce connecteur. Deux opérations partent sans repasser par vous,
l'envoi direct et la réponse dans le fil ; le brouillon se dépose sans rien expédier.

Deux comportements à connaître. Lire un message par Claude le marque comme lu, le retour en
non-lu se demande. Et la liste des comptes est lue au démarrage : une boîte ajoutée à
`accounts.json` reste invisible tant que Claude n'a pas redémarré.

Commencer par une boîte secondaire. Demander un brouillon pour tout message qui engage.

Pour couper l'accès : révoquer le mot de passe d'application chez le fournisseur. Effet
immédiat.
