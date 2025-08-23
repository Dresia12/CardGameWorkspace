# 🎮 GUIDE D'UTILISATION - JEU DE CARTES

## 🚀 LANCEMENT DU JEU

### Prérequis
- Python 3.7 ou supérieur
- Pygame installé (`pip install pygame`)

### Lancement
```bash
cd JeuDeCarte
python main.py
```

### Test de fonctionnement
```bash
python test_game.py
```

## 🎯 FLUX DE JEU COMPLET

### 1. Menu Principal
- **JOUER** → Lance le flux de combat
- **DECK** → Accès direct au constructeur de deck
- **BOUTIQUE** → À implémenter
- **OPTIONS** → À implémenter
- **QUITTER** → Ferme le jeu

### 2. Écran Pre-Combat
- **Validation automatique** du deck
- **Affichage des informations** : Héros, Unités (5/5), Cartes (30/30)
- **COMBAT IA** → Lance un combat contre l'IA
- **RETOUR** → Retour au menu principal

### 3. Deck Builder
- **3 onglets** : Héros, Unités, Cartes
- **Filtres** : Par élément, coût, recherche
- **Sélection** : Clic pour ajouter/retirer
- **Personnalisation** : Bouton pour personnaliser le héros
- **Sauvegarde** : Bouton pour sauvegarder le deck
- **JOUER** : Lance directement un combat

### 4. Personnalisation du Héros
- **Sliders** : HP, Attaque, Défense (+0% à +15%)
- **Capacités** : Attaque Basique ou Capacité du Héros
- **Passif** : Activation/désactivation
- **Coût d'activation** : Calculé automatiquement
- **Prévisualisation** : Stats en temps réel
- **Boutons** : RETOUR, RÉINITIALISER, APPLIQUER

### 5. Écran de Combat
- **Plateau central** : Zone de combat
- **Héros** : Côtés gauche (joueur) et droite (adversaire)
- **Unités** : Affichées sur le plateau
- **Mains** : Cartes du joueur (bas) et adversaire (haut)
- **Interface** : Mana, tour, phase, boutons d'action
- **Logs** : Historique des actions

## 🎴 RÈGLES DU DECK

### Composition obligatoire
- **1 Héros** (obligatoire)
- **5 Unités** (exactement, toutes différentes)
- **30 Cartes** (exactement, max 2 exemplaires par carte)

### Validation automatique
- Vérification de la composition
- Messages d'erreur explicites
- Impossible de lancer un combat avec un deck invalide

## ⚔️ SYSTÈME DE COMBAT

### Phases de tour
1. **Pioche** : Tirage de cartes
2. **Mana** : Gain de mana (+1 par tour)
3. **Actions** : Jouer des cartes, utiliser des capacités
4. **Combat** : Combat automatique entre unités
5. **Fin de tour** : Nettoyage des effets

### Actions disponibles
- **Jouer des cartes** : Clic sur carte puis cible
- **Utiliser capacités** : Clic sur unité/héros
- **Activer héros** : Bouton "ACTIVER HÉROS"
- **Fin de tour** : Bouton "FIN DE TOUR"

### Interface de combat
- **Boutons d'action** : En bas de l'écran
- **Informations** : Mana, tour, phase (haut droite)
- **Logs** : Bouton "LOGS" pour l'historique
- **Abandon** : Bouton "ABANDON"

## 🎨 PERSONNALISATION DES HÉROS

### Stats modifiables
- **HP** : +0% à +15% (coût : +1 mana par +5%)
- **Attaque** : +0% à +15% (coût : +1 mana par +5%)
- **Défense** : +0% à +15% (coût : +1 mana par +5%)

### Capacités
- **Attaque Basique** : Cooldown 1, coût +0 mana
- **Capacité du Héros** : Capacité spéciale, coût +1 mana

### Passifs
- **Activation** : Toggle pour activer/désactiver
- **Coût** : Extrait automatiquement de la description

### Sauvegarde
- **APPLIQUER** : Sauvegarde les modifications
- **RÉINITIALISER** : Remet tout à zéro
- **RETOUR** : Annule les modifications non sauvegardées

## 🎯 CONTRÔLES

### Souris
- **Clic gauche** : Sélection, action
- **Survol** : Tooltips, informations
- **Clic droit** : Annulation (dans certains contextes)

### Clavier
- **Échap** : Retour au menu principal
- **F11** : Plein écran/Fenêtré
- **Touches directionnelles** : Navigation dans les listes
- **Entrée** : Validation
- **Suppr/Backspace** : Suppression dans les champs de recherche

## 🔧 FONCTIONNALITÉS AVANCÉES

### Filtres et recherche
- **Par élément** : Feu, Eau, Terre, Air, etc.
- **Par coût** : 0-2, 3-5, 6+
- **Recherche textuelle** : Tapez pour filtrer

### Tooltips informatifs
- **Survol des cartes** : Description complète
- **Survol des unités** : Stats et capacités
- **Survol des héros** : Capacités et passifs
- **Survol des boutons** : Explication des actions

### Sauvegarde automatique
- **Decks** : Sauvegardés automatiquement
- **Personnalisations** : Sauvegardées par héros
- **Backups** : Sauvegardes de sécurité automatiques

## 🐛 DÉPANNAGE

### Problèmes courants
1. **"Aucun deck sauvegardé"** → Créez un deck dans le Deck Builder
2. **"Deck invalide"** → Vérifiez la composition (1 héros, 5 unités, 30 cartes)
3. **"Erreur d'import"** → Vérifiez que tous les fichiers de données existent

### Logs de debug
- **Console** : Messages d'erreur détaillés
- **Logs de combat** : Historique des actions
- **Test automatique** : `python test_game.py`

## 🎉 FÉLICITATIONS !

Votre jeu de cartes est maintenant **100% fonctionnel** ! 

Vous pouvez :
- ✅ Construire des decks
- ✅ Personnaliser des héros
- ✅ Lancer des combats
- ✅ Jouer contre l'IA
- ✅ Sauvegarder vos progrès

**Amusez-vous bien !** 🎮✨ 