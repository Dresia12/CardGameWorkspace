# Systèmes Implémentés - JeuDeCarte

## 📋 Vue d'ensemble

Ce document décrit les systèmes critiques qui ont été implémentés pour compléter le projet JeuDeCarte selon la documentation.

## 🔧 1. Gestionnaire de Mécaniques (`card_mechanics_manager.py`)

### Fonctionnalités
- **Interactions élémentaires complètes** : Tous les bonus/malus selon la documentation
- **Effets temporaires** : Poison, Brûlure, Gel, Corruption, etc.
- **Système de ciblage** : Ennemi, Allié, Zone, Ligne
- **Gestion des dégâts** : Calcul automatique avec multiplicateurs élémentaires

### Utilisation
```python
from Engine.card_mechanics_manager import card_mechanics_manager, EffectContext

# Calculer un multiplicateur élémentaire
multiplier = card_mechanics_manager.get_elemental_multiplier("Feu", "Terre")  # 1.20

# Appliquer un effet temporaire
card_mechanics_manager.apply_temporary_effect(target, "poison", 2, 1, "Poison")

# Traiter les effets d'un tour
logs = card_mechanics_manager.process_temporary_effects(unit)
```

### Interactions Élémentaires Implémentées
- **Feu > Terre** : +20% dégâts
- **Eau > Feu** : +20% dégâts
- **Terre > Air** : +20% dégâts
- **Air > Eau** : +20% dégâts
- **Lumière ↔ Ténèbres** : +30% dégâts
- **Poison > Tous** : +15% dégâts (sauf Arcanique)
- **Arcanique > Poison** : +30% dégâts
- **Néant > Tous** : +10% dégâts (sauf Lumière)

## 💾 2. Gestionnaire de Decks (`deck_manager.py`)

### Fonctionnalités
- **Sauvegarde/chargement automatique** : Persistance des decks
- **Système de multiple decks** : Création, suppression, renommage
- **Validation complète** : Vérification des règles du jeu
- **Sauvegardes automatiques** : 5 dernières sauvegardes conservées
- **Export/Import** : Partage de decks entre joueurs

### Utilisation
```python
from Engine.deck_manager import deck_manager

# Créer un nouveau deck
deck_manager.create_deck("Mon Deck")

# Sauvegarder un deck
deck_manager.update_deck("Mon Deck", hero=hero_data, units=units_data, cards=cards_data)

# Charger un deck
current_deck = deck_manager.get_current_deck()

# Valider un deck
deck_manager.validate_deck(deck)
```

### Règles de Validation
- **1 héros obligatoire**
- **5 unités maximum** (toutes différentes)
- **30 cartes exactement**
- **Maximum 2 exemplaires** de la même carte

## 👑 3. Gestionnaire de Personnalisation (`hero_customization_manager.py`)

### Fonctionnalités
- **Personnalisation des stats** : HP, Attaque, Défense (+0%, +5%, +10%, +15%)
- **Calcul automatique du coût** : Coût d'activation basé sur les modifications
- **Choix de capacité** : Attaque basique ou Capacité du héros
- **Persistance** : Sauvegarde des personnalisations
- **Validation** : Vérification des valeurs autorisées

### Utilisation
```python
from Engine.hero_customization_manager import hero_customization_manager

# Créer une personnalisation
customization = hero_customization_manager.create_customization("Solaris")

# Modifier les stats
hero_customization_manager.update_customization("Solaris", "hp", 10)  # +10% HP
hero_customization_manager.update_customization("Solaris", "attack", 5)  # +5% Attaque

# Calculer le coût d'activation
cost = customization.calculate_activation_cost()  # 3 + 2 + 1 = 6 mana

# Appliquer à un héros
customized_hero = hero_customization_manager.apply_customization_to_hero(hero_data, customization)
```

### Calcul du Coût d'Activation
- **Base** : 3 mana
- **+5% stats** : +1 mana
- **+10% stats** : +2 mana
- **+15% stats** : +3 mana
- **Capacité du héros** : +1 mana

## 🎮 4. Intégration avec l'Interface

### Mise à jour de `game_ui.py`
- **Import des gestionnaires** : Intégration automatique
- **Sauvegarde de deck** : Utilisation du gestionnaire de decks
- **Personnalisation** : Interface complète avec le gestionnaire
- **Gestion d'erreurs** : Fallback en cas de problème

### Écran de Personnalisation
- **Interface intuitive** : Clics pour changer les options
- **Prévisualisation en temps réel** : Stats et coût mis à jour
- **Validation visuelle** : Options disponibles clairement affichées

## 🧪 5. Système de Tests (`test_system.py`)

### Tests Inclus
- **Gestionnaire de mécaniques** : Interactions élémentaires et effets
- **Gestionnaire de decks** : Création, validation, sauvegarde
- **Gestionnaire de personnalisation** : Modifications et calculs
- **Intégration** : Tests d'utilisation combinée

### Exécution des Tests
```bash
cd JeuDeCarte
python test_system.py
```

## 📁 Structure des Fichiers

```
JeuDeCarte/
├── Engine/
│   ├── card_mechanics_manager.py    # Gestionnaire de mécaniques
│   ├── deck_manager.py              # Gestionnaire de decks
│   ├── hero_customization_manager.py # Gestionnaire de personnalisation
│   ├── engine.py                    # Moteur de jeu (mis à jour)
│   └── models.py                    # Modèles de données
├── UI/
│   └── game_ui.py                   # Interface (mise à jour)
├── Decks/
│   ├── decks.json                   # Sauvegarde des decks
│   ├── hero_customizations.json     # Sauvegarde des personnalisations
│   └── backups/                     # Sauvegardes automatiques
├── test_system.py                   # Tests du système
└── README_SYSTEMES.md               # Cette documentation
```

## ✅ État d'Implémentation

### Point 1 - Gestionnaire de Mécaniques : ✅ COMPLET
- [x] Interactions élémentaires complètes
- [x] Effets temporaires (Poison, Brûlure, Gel, etc.)
- [x] Système de ciblage
- [x] Intégration avec le moteur de jeu
- [x] Gestion des erreurs et fallback

### Point 2 - Système de Sauvegarde/Chargement : ✅ COMPLET
- [x] Gestionnaire de decks complet
- [x] Sauvegarde automatique avec backups
- [x] Validation des decks
- [x] Système de multiple decks
- [x] Export/Import de decks
- [x] Gestionnaire de personnalisation
- [x] Persistance des personnalisations

## 🚀 Prochaines Étapes

Avec ces systèmes en place, le projet peut maintenant :

1. **Jouer des cartes** avec effets complets
2. **Sauvegarder/charger** des decks personnalisés
3. **Personnaliser les héros** avec calcul automatique des coûts
4. **Valider** la conformité des decks aux règles

Les éléments manquants restants sont principalement :
- Interface de combat complète
- Système de boutique
- Multijoueur (prévu pour plus tard)

## 🔧 Dépannage

### Erreurs Courantes
1. **Import Error** : Vérifiez que tous les fichiers sont dans le bon dossier
2. **Validation Error** : Vérifiez que le deck respecte les règles (1 héros, 5 unités, 30 cartes)
3. **Sauvegarde Error** : Vérifiez les permissions d'écriture dans le dossier Decks

### Logs de Debug
Les gestionnaires produisent des logs détaillés pour faciliter le débogage :
- `[MÉCANIQUES]` : Logs du gestionnaire de mécaniques
- `[DECK MANAGER]` : Logs du gestionnaire de decks
- `[CUSTOMIZATION]` : Logs du gestionnaire de personnalisation