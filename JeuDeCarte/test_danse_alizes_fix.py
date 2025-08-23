#!/usr/bin/env python3
"""
Script de test pour vérifier que Danse des Alizés fonctionne après la correction
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Engine.engine import CombatEngine, Player
from Engine.models import Hero, Unit, Ability
from Engine.effects_database_manager import EffectsDatabaseManager

def test_danse_alizes_fix():
    """Teste que Danse des Alizés fonctionne après la correction"""
    
    print("=== TEST CORRECTION DANSE DES ALIZÉS ===\n")
    
    # Créer un moteur de combat
    hero1 = Hero("Héros Test 1", "Air", {"hp": 1000, "attack": 30, "defense": 20})
    hero2 = Hero("Héros Test 2", "Feu", {"hp": 1000, "attack": 30, "defense": 20})
    
    units1 = [
        Unit("Gelidar", "Glace", {"hp": 1100, "attack": 25, "defense": 28}),
        Unit("Frimousse", "Glace", {"hp": 780, "attack": 23, "defense": 13}),
        Unit("Skyla", "Air", {"hp": 1010, "attack": 28, "defense": 21})
    ]
    
    units2 = [
        Unit("Pyrodrake", "Feu", {"hp": 1200, "attack": 35, "defense": 22}),
        Unit("Terra", "Terre", {"hp": 1400, "attack": 18, "defense": 41}),
        Unit("Bersi", "Terre", {"hp": 1160, "attack": 26, "defense": 30})
    ]
    
    player1 = Player("Joueur 1", [], hero1, units1)
    player2 = Player("Joueur 2", [], hero2, units2)
    
    engine = CombatEngine(player1, player2)
    
    # Configurer les propriétaires
    for unit in units1:
        unit.owner = player1
    for unit in units2:
        unit.owner = player2
    
    print("1. Test de création d'objet Ability avec target_type:")
    
    # Créer un objet Ability pour Danse des Alizés
    danse_alizes = Ability(
        name="Danse des Alizés",
        description="Une danse majestueuse et aussi gracieuse que le vent",
        cooldown=3,
        target_type="all_allies",
        ability_id="5754"
    )
    
    print(f"   Nom: {danse_alizes.name}")
    print(f"   Target Type: {danse_alizes.target_type}")
    print(f"   Ability ID: {danse_alizes.ability_id}")
    print(f"   Cooldown: {danse_alizes.cooldown}")
    
    print("\n2. Test de vérification des capacités automatiques:")
    
    # Vérifier si c'est une capacité automatique
    auto_use_types = [
        "all_allies", "all_enemies", "all_units",
        "random_enemy", "random_ally", "random_unit",
        "front_row", "back_row",
        "chain_enemies", "chain_allies"
    ]
    
    if danse_alizes.target_type in auto_use_types:
        print(f"   ✅ {danse_alizes.name} est une capacité automatique ({danse_alizes.target_type})")
        print(f"   → Elle devrait s'utiliser sans ciblage manuel")
    else:
        print(f"   ❌ {danse_alizes.name} n'est PAS une capacité automatique ({danse_alizes.target_type})")
        print(f"   → Elle nécessite un ciblage manuel")
    
    print("\n3. Test de récupération des cibles:")
    
    # Tester la récupération des cibles
    try:
        ability_data = {
            'target_type': danse_alizes.target_type,
            'target_conditions': ['alive']
        }
        
        targets = engine.get_available_targets_for_ability(ability_data, units1[2], engine)  # Skyla
        print(f"   Cibles trouvées: {len(targets)}")
        for target in targets:
            print(f"     - {target.name} (HP: {target.hp})")
            
    except Exception as e:
        print(f"   ❌ Erreur lors de la récupération des cibles: {e}")
    
    print("\n4. Test de simulation d'utilisation via use_ability_by_id:")
    
    # Tester l'utilisation directe via use_ability_by_id
    try:
        success, message = engine.use_ability_by_id(units1[2], "5754", None)  # Skyla utilise Danse des Alizés
        
        if success:
            print(f"   ✅ Capacité utilisée avec succès")
            print(f"   Message: {message}")
        else:
            print(f"   ❌ Échec de l'utilisation")
            print(f"   Message: {message}")
            
    except Exception as e:
        print(f"   ❌ Erreur lors de l'utilisation: {e}")
    
    print("\n5. Test de vérification des effets appliqués:")
    
    # Vérifier si les effets ont été appliqués
    effects_manager = EffectsDatabaseManager()
    danse_alizes_data = effects_manager.get_ability("5754")
    
    if danse_alizes_data:
        print(f"   Données de la capacité:")
        print(f"     - Crit Boost: {danse_alizes_data.get('crit_boost', 'N/A')}")
        print(f"     - Crit Duration: {danse_alizes_data.get('crit_duration', 'N/A')}")
        print(f"     - Effect IDs: {danse_alizes_data.get('effect_ids', [])}")
    
    print("\n6. Test de vérification des logs du moteur:")
    
    # Afficher les derniers logs
    print(f"   Derniers logs du moteur:")
    for log in engine.log[-10:]:  # 10 derniers logs
        print(f"     {log}")
    
    print("\n=== FIN DU TEST ===")

if __name__ == "__main__":
    test_danse_alizes_fix()
