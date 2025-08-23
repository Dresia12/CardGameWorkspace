#!/usr/bin/env python3
"""
Script pour tester la logique de clic UI et identifier le problème
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Engine.engine import CombatEngine, Player
from Engine.models import Hero, Unit, Ability
from Engine.effects_database_manager import EffectsDatabaseManager

def test_ui_click_logic():
    """Teste la logique de clic UI pour identifier le problème"""
    
    print("=== TEST LOGIQUE CLIC UI ===\n")
    
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
    
    print("1. Test de l'état initial des capacités:")
    
    # Vérifier les capacités de Skyla
    print(f"   Capacités de Skyla: {len(skyla.abilities)}")
    for i, ability in enumerate(skyla.abilities):
        ability_id = getattr(ability, 'ability_id', 'N/A')
        ability_name = getattr(ability, 'name', 'N/A')
        print(f"     Capacité {i+1}: {ability_name} (ID: {ability_id})")
    
    print("\n2. Test de can_use_ability (méthode utilisée par l'UI):")
    
    # Tester can_use_ability pour chaque capacité
    for i, ability in enumerate(skyla.abilities):
        can_use = engine.can_use_ability(skyla, ability)
        ability_id = getattr(ability, 'ability_id', 'N/A')
        ability_name = getattr(ability, 'name', 'N/A')
        print(f"   Capacité {i+1} ({ability_name}): {can_use}")
        
        # Vérifier si l'objet Ability a un ability_id
        if hasattr(ability, 'ability_id'):
            print(f"     ✅ Objet Ability a un ability_id: {ability.ability_id}")
        else:
            print(f"     ❌ Objet Ability n'a PAS d'ability_id")
    
    print("\n3. Test de can_use_ability_by_id (méthode alternative):")
    
    # Tester can_use_ability_by_id pour chaque capacité
    for i, ability in enumerate(skyla.abilities):
        ability_id = getattr(ability, 'ability_id', 'N/A')
        if ability_id != 'N/A':
            can_use = engine.can_use_ability_by_id(skyla, ability_id)
            ability_name = getattr(ability, 'name', 'N/A')
            print(f"   Capacité {i+1} ({ability_name} - ID: {ability_id}): {can_use}")
        else:
            print(f"   Capacité {i+1}: Pas d'ID disponible")
    
    print("\n4. Test après utilisation de Capacité 1:")
    
    # Utiliser Capacité 1
    success1, message1 = engine.use_ability_by_id(skyla, "5754", None)
    print(f"   Capacité 1 utilisée: {success1} - {message1}")
    
    print("\n5. Test de can_use_ability après Capacité 1:")
    
    # Tester can_use_ability après utilisation
    for i, ability in enumerate(skyla.abilities):
        can_use = engine.can_use_ability(skyla, ability)
        ability_id = getattr(ability, 'ability_id', 'N/A')
        ability_name = getattr(ability, 'name', 'N/A')
        print(f"   Capacité {i+1} ({ability_name}): {can_use}")
        
        # Vérifier la délégation dans can_use_ability
        if hasattr(ability, 'ability_id'):
            delegated_result = engine.can_use_ability_by_id(skyla, ability.ability_id)
            print(f"     Délégation vers can_use_ability_by_id: {delegated_result}")
            
            if can_use != delegated_result:
                print(f"     ⚠️  INCOHÉRENCE DÉTECTÉE!")
    
    print("\n6. Test de get_ability_cooldown (utilisé par can_use_ability):")
    
    # Tester get_ability_cooldown pour chaque capacité
    for i, ability in enumerate(skyla.abilities):
        cooldown = engine.get_ability_cooldown(skyla, ability)
        ability_name = getattr(ability, 'name', 'N/A')
        print(f"   Capacité {i+1} ({ability_name}): cooldown = {cooldown}")
    
    print("\n7. Test de get_unit_ability_cooldown (utilisé par can_use_ability_by_id):")
    
    # Tester get_unit_ability_cooldown pour chaque capacité
    for i, ability in enumerate(skyla.abilities):
        ability_id = getattr(ability, 'ability_id', 'N/A')
        if ability_id != 'N/A':
            cooldown = engine.get_unit_ability_cooldown(skyla, ability_id)
            ability_name = getattr(ability, 'name', 'N/A')
            print(f"   Capacité {i+1} ({ability_name} - ID: {ability_id}): cooldown = {cooldown}")
        else:
            print(f"   Capacité {i+1}: Pas d'ID disponible")
    
    print("\n8. Simulation de la logique UI:")
    
    # Simuler la logique de handle_ability_menu_click
    print("   Simulation de handle_ability_menu_click:")
    for i, ability in enumerate(skyla.abilities):
        ability_name = getattr(ability, 'name', 'N/A')
        print(f"   Capacité {i+1} ({ability_name}):")
        
        # Étape 1: Vérifier si la capacité peut être utilisée
        can_use = engine.can_use_ability(skyla, ability)
        print(f"     can_use_ability: {can_use}")
        
        if can_use:
            print(f"     ✅ Capacité utilisable - devrait lancer start_ability_targeting")
            
            # Étape 2: Simuler start_ability_targeting
            target_type = getattr(ability, 'target_type', 'N/A')
            print(f"     target_type: {target_type}")
            
            # Étape 3: Vérifier si c'est une capacité automatique
            auto_use_types = [
                "all_allies", "all_enemies", "all_units",
                "random_enemy", "random_ally", "random_unit",
                "front_row", "back_row",
                "chain_enemies", "chain_allies"
            ]
            
            if target_type in auto_use_types:
                print(f"     ✅ Capacité automatique - devrait s'utiliser directement")
            elif target_type in ["adjacent_enemies", "adjacent_allies"]:
                print(f"     ✅ Capacité adjacente - nécessite ciblage initial")
            else:
                print(f"     ✅ Capacité unique - nécessite ciblage manuel")
        else:
            print(f"     ❌ Capacité non utilisable - ne lance pas start_ability_targeting")
    
    print("\n9. Diagnostic du problème:")
    
    print("   Problème identifié:")
    print("   - La capacité affiche un cooldown de 0")
    print("   - Le menu peut être activé")
    print("   - Mais le clic ne déclenche pas l'action")
    print("   ")
    print("   Cela suggère que:")
    print("   1. can_use_ability() retourne False même si le cooldown est 0")
    print("   2. Il y a une incohérence entre can_use_ability et can_use_ability_by_id")
    print("   3. La délégation dans can_use_ability ne fonctionne pas correctement")
    print("   4. Il y a un problème dans get_ability_cooldown vs get_unit_ability_cooldown")
    
    print("\n=== FIN DU TEST ===")

if __name__ == "__main__":
    test_ui_click_logic()
