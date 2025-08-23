# 🔥 Guide du Système d'Effets - JeuDeCarte

## 📋 Vue d'ensemble

Le nouveau système d'effets offre une gestion centralisée et modulaire des capacités, effets, et interactions élémentaires. Tous les éléments sont identifiés par des IDs numériques pour une meilleure organisation et flexibilité.

## 🏗️ Architecture du Système

### Structure des IDs
- **Éléments** : 1-12
- **Effets de base** : 100-115
- **Effets en chaîne** : 150-190
- **Interactions élémentaires** : 200-207
- **Combos spéciaux** : 300-304
- **Effets d'attaque automatiques** : 400-410
- **Passifs** : 1000-1010
- **Capacités** : 5000-5020

## 📊 Base de Données d'Effets

### Fichier : `Data/effects_database.json`

```json
{
  "metadata": {
    "version": "1.0",
    "description": "Base de données des effets élémentaires et leurs chaînes"
  },
  "elements": {
    "1": {"name": "Feu", "description": "Élément de destruction et de brûlure"},
    "2": {"name": "Eau", "description": "Élément de soin et de fluidité"}
  },
  "base_effects": {
    "100": {"name": "burn", "element": "1", "default_duration": 1}
  },
  "abilities": {
    "5001": {
      "name": "Explosion",
      "element": "1",
      "base_cooldown": 3,
      "damage_type": "fixed",
      "damage": 120,
      "effect_ids": ["100", "150", "160"]
    }
  }
}
```

## ⚔️ Types de Dégâts

### 1. `"fixed"` - Dégâts fixes
```json
{
  "name": "Explosion",
  "damage_type": "fixed",
  "damage": 120
}
```
**Résultat** : Toujours 120 dégâts (modifiés par les buffs)

### 2. `"attack_plus"` - Attaque + bonus
```json
{
  "name": "Morsure",
  "damage_type": "attack_plus",
  "damage": 10
}
```
**Résultat** : Attaque de la créature + 10 (modifiés par les buffs)

### 3. `"attack_only"` - Attaque pure
```json
{
  "name": "Attaque pure",
  "damage_type": "attack_only",
  "damage": 0
}
```
**Résultat** : Seulement l'attaque de la créature (modifiés par les buffs)

## 🔄 Système de Cooldown

### Cooldown de base (dans les capacités)
```json
{
  "name": "Explosion",
  "base_cooldown": 3
}
```

### Modificateurs de cooldown (dans les unités)
```json
{
  "name": "Pyrodrake",
  "ability_ids": ["5001", "5002"],
  "cooldown_modifiers": {
    "5001": 1,   // +1 tour → Cooldown final = 4 tours
    "5002": -1   // -1 tour → Cooldown final = 1 tour
  }
}
```

## 🌟 Effets Automatiques des Éléments

Chaque élément applique automatiquement des effets lors d'une attaque :

### Exemples
- **Feu** : Brûlure sur la cible (100% de chance)
- **Eau** : Réduction des soins reçus de 10% (100% de chance)
- **Foudre** : Effets multiples selon probabilités (25% burn, 25% dodge, 45% crit, 5% tous)
- **Neutre** : +50% dégâts si 3+ cartes jouées ce tour

## ⚡ Interactions Élémentaires

### Déclenchement automatique
```json
{
  "name": "feu_eau",
  "elements": ["1", "2"],
  "chain_effects": ["150"]  // Déclenche "steam"
}
```

### Exemples d'interactions
- **Feu + Eau** → Vapeur
- **Feu + Glace** → Échaudé
- **Lumière + Ténèbres** → Purification

## 🔗 Effets en Chaîne

Les effets en chaîne sont déclenchés par :
1. **Interactions élémentaires** (Feu + Eau)
2. **Combos spéciaux** (Brûlure + Mouillé)

**IMPORTANT** : Les effets de base ne déclenchent pas automatiquement d'effets en chaîne.

## 📝 Utilisation dans le Code

### 1. Initialisation
```python
from Engine.effects_database_manager import EffectsDatabaseManager

# Dans le moteur de combat
self.effects_manager = EffectsDatabaseManager()
```

### 2. Utilisation d'une capacité
```python
# Utiliser une capacité par ID
success, message = engine.use_ability_by_id(unit, "5001", target)

# Vérifier si une capacité peut être utilisée
can_use = engine.can_use_ability(unit, "5001")

# Récupérer le cooldown
cooldown = engine.get_unit_ability_cooldown(unit, "5001")
```

### 3. Calcul des dégâts
```python
# Calculer les dégâts d'une capacité
damage = effects_manager.calculate_ability_damage("5001", unit.attack, 1.0)

# Récupérer les informations d'une capacité
ability_data = effects_manager.get_ability("5001")
```

### 4. Application d'effets automatiques
```python
# Appliquer les effets automatiques d'un élément
elemental_effects = engine.apply_elemental_attack_effects("Feu", source, target)
```

## 🔄 Conversion des Unités Existantes

### Script de conversion
```bash
python convert_units_to_new_system.py
```

### Structure avant conversion
```json
{
  "name": "Pyrodrake",
  "abilities": [
    {
      "name": "Explosion",
      "secondary_effects": ["burn", "steam"]
    }
  ]
}
```

### Structure après conversion
```json
{
  "name": "Pyrodrake",
  "ability_ids": ["5001"],
  "cooldown_modifiers": {},
  "abilities": [
    {
      "id": "5001",
      "name": "Explosion",
      "damage_type": "fixed",
      "base_cooldown": 3,
      "element": "1",
      "effect_ids": ["100", "150"]
    }
  ]
}
```

## 🧪 Tests

### Test du système complet
```bash
python test_effects_system.py
```

### Test des unités converties
```bash
python test_converted_units.py
```

## 📊 Exemples Concrets

### Exemple 1 : Pyrodrake vs Aquamage

**Pyrodrake** (Feu, 80 attaque) utilise **Explosion** (ID 5001) sur **Aquamage** (Eau, 90 PV) :

1. **Dégâts de base** : 120 (fixe)
2. **Effet automatique Feu** : Brûlure appliquée
3. **Interaction Feu + Eau** : Vapeur déclenchée
4. **Résultat** : 120 dégâts + Brûlure + Vapeur

### Exemple 2 : Capacité avec attaque + bonus

**Guerrier** (50 attaque) utilise **Morsure** (ID 5016) :

1. **Dégâts** : 50 + 10 = 60
2. **Effet automatique Poison** : Poison appliqué (15 dégâts par tour)
3. **Résultat** : 60 dégâts + Poison

## ⚠️ Points Importants

### 1. Dégâts d'effets vs Dégâts d'attaque
- **Dégâts d'attaque** : Affectés par les buffs (+20% dégâts, etc.)
- **Dégâts d'effets** : Fixes et indépendants des buffs

### 2. Durée des effets
- **Durée par défaut** : 1 tour pour tous les effets
- **Override** : Possibilité de spécifier une durée différente

### 3. Effets en chaîne
- **Ne se déclenchent PAS** automatiquement depuis les effets de base
- **Se déclenchent** uniquement via interactions ou combos

### 4. Cooldowns
- **Base** : Défini dans la capacité
- **Modificateurs** : Définis au niveau de l'unité
- **Final** : Base + Modificateurs (minimum 1)

## 🚀 Avantages du Nouveau Système

1. **Modularité** : Capacités réutilisables par ID
2. **Flexibilité** : Cooldowns personnalisables par unité
3. **Clarté** : Séparation nette entre capacité et équilibrage
4. **Extensibilité** : Facile d'ajouter de nouveaux effets
5. **Performance** : Recherche par ID plus rapide que par nom
6. **Maintenance** : Centralisation des définitions d'effets

## 🔧 Maintenance

### Ajouter une nouvelle capacité
1. Ajouter l'entrée dans `effects_database.json` (section "abilities")
2. Assigner un ID unique (5000+)
3. Définir les propriétés (dégâts, cooldown, effets)

### Ajouter un nouvel effet
1. Ajouter l'entrée dans `effects_database.json` (section "base_effects" ou "chain_effects")
2. Assigner un ID unique
3. Implémenter la logique dans `EffectsDatabaseManager`

### Modifier les interactions
1. Éditer la section "elemental_interactions" dans `effects_database.json`
2. Définir les éléments et effets en chaîne

## 📞 Support

Pour toute question ou problème avec le système d'effets :
1. Vérifier les logs de debug dans `logs/`
2. Utiliser les scripts de test
3. Consulter la base de données d'effets
4. Vérifier la cohérence des IDs

---

**🎉 Le système d'effets est maintenant prêt à être utilisé !**
