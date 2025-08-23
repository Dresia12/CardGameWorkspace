#!/usr/bin/env python3
"""
Script pour tester spécifiquement la logique de can_use_ability_by_id
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Engine.engine import CombatEngine, Player
from Engine.models import Hero, Unit, Ability
from Engine.effects_database_manager import EffectsDatabaseManager

def test_can_use_ability_logic():
    """Teste spécifiquement la logique de can_use_ability_by_id"""
    
    print("=== TEST LOGIQUE CAN_USE_ABILITY_BY_ID ===\n")
    
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
    
    skyla = units1[2]  # Skyla
    
    print("1. Test de la logique de base:")
    
    # Test 1: Vérifier que les capacités sont utilisables au début
    can_use1_initial = engine.can_use_ability_by_id(skyla, "5754")
    can_use2_initial = engine.can_use_ability_by_id(skyla, "5755")
    
    print(f"   Capacité 1 (5754) utilisable au début: {can_use1_initial}")
    print(f"   Capacité 2 (5755) utilisable au début: {can_use2_initial}")
    
    print("\n2. Test après utilisation de Capacité 1:")
    
    # Utiliser Capacité 1
    success1, message1 = engine.use_ability_by_id(skyla, "5754", None)
    print(f"   Capacité 1 utilisée: {success1}")
    
    # Vérifier immédiatement après
    can_use1_after = engine.can_use_ability_by_id(skyla, "5754")
    can_use2_after = engine.can_use_ability_by_id(skyla, "5755")
    
    print(f"   Capacité 1 (5754) utilisable après: {can_use1_after}")
    print(f"   Capacité 2 (5755) utilisable après: {can_use2_after}")
    
    print("\n3. Test détaillé de get_unit_ability_cooldown:")
    
    # Vérifier les cooldowns directement
    cooldown1 = engine.get_unit_ability_cooldown(skyla, "5754")
    cooldown2 = engine.get_unit_ability_cooldown(skyla, "5755")
    
    print(f"   Cooldown Capacité 1 (5754): {cooldown1}")
    print(f"   Cooldown Capacité 2 (5755): {cooldown2}")
    
    print("\n4. Test de la logique can_use_ability_by_id:")
    
    # Tester la logique manuellement
    cooldown1_check = engine.get_unit_ability_cooldown(skyla, "5754")
    cooldown2_check = engine.get_unit_ability_cooldown(skyla, "5755")
    
    can_use1_manual = cooldown1_check <= 0
    can_use2_manual = cooldown2_check <= 0
    
    print(f"   Logique manuelle - Capacité 1: cooldown={cooldown1_check}, <=0={can_use1_manual}")
    print(f"   Logique manuelle - Capacité 2: cooldown={cooldown2_check}, <=0={can_use2_manual}")
    
    print(f"   Méthode engine - Capacité 1: {can_use1_after}")
    print(f"   Méthode engine - Capacité 2: {can_use2_after}")
    
    print("\n5. Test de l'utilisation de Capacité 2:")
    
    if can_use2_after:
        print("   ✅ Capacité 2 peut être utilisée")
        success2, message2 = engine.use_ability_by_id(skyla, "5755", None)
        print(f"   Capacité 2 utilisée: {success2} - {message2}")
    else:
        print("   ❌ Capacité 2 ne peut pas être utilisée")
        print("   Cela indique un problème dans la logique de vérification")
    
    print("\n6. Analyse des systèmes de cooldown:")
    
    # Système 1: ability_cooldowns sur l'unité
    print("   Système 1 - ability_cooldowns:")
    if hasattr(skyla, 'ability_cooldowns'):
        for ability_id, cooldown in skyla.ability_cooldowns.items():
            print(f"     {ability_id}: {cooldown}")
    else:
        print("     Non initialisé")
    
    # Système 2: unit_cooldowns du moteur
    print("   Système 2 - unit_cooldowns du moteur:")
    entity_id = id(skyla)
    if entity_id in engine.unit_cooldowns:
        for i, cooldown in enumerate(engine.unit_cooldowns[entity_id]):
            print(f"     Index {i}: {cooldown}")
    else:
        print("     Non initialisé")
    
    # Système 3: current_cooldown des objets Ability
    print("   Système 3 - current_cooldown des objets Ability:")
    for i, ability in enumerate(skyla.abilities):
        ability_id = getattr(ability, 'ability_id', 'N/A')
        current_cd = getattr(ability, 'current_cooldown', 'N/A')
        print(f"     Capacité {i+1} ({ability_id}): {current_cd}")
    
    print("\n7. Test de la méthode can_use_ability (avec objets Ability):")
    
    # Tester avec les objets Ability
    for i, ability in enumerate(skyla.abilities):
        ability_id = getattr(ability, 'ability_id', 'N/A')
        can_use_obj = engine.can_use_ability(skyla, ability)
        can_use_id = engine.can_use_ability_by_id(skyla, ability_id)
        
        print(f"   Capacité {i+1} ({ability_id}):")
        print(f"     can_use_ability: {can_use_obj}")
        print(f"     can_use_ability_by_id: {can_use_id}")
        
        if can_use_obj != can_use_id:
            print(f"     ⚠️  INCOHÉRENCE DÉTECTÉE!")
    
    print("\n8. Conclusion:")
    
    if can_use2_after:
        print("   ✅ La logique fonctionne correctement")
        print("   Le problème n'est pas dans can_use_ability_by_id")
    else:
        print("   ❌ Problème détecté dans can_use_ability_by_id")
        print("   La Capacité 2 devrait être utilisable après la Capacité 1")
        print("   ")
        print("   Causes possibles:")
        print("   1. Le cooldown de la Capacité 1 affecte la Capacité 2")
        print("   2. Problème dans get_unit_ability_cooldown")
        print("   3. Problème dans _apply_ability_cooldown")
        print("   4. Problème de synchronisation entre systèmes")
    
    print("\n=== FIN DU TEST ===")

if __name__ == "__main__":
    test_can_use_ability_logic()
