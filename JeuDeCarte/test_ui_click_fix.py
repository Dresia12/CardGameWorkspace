#!/usr/bin/env python3
"""
Script pour tester la correction du problème de clic UI
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Engine.engine import CombatEngine, Player
from Engine.models import Hero, Unit, Ability
from Engine.effects_database_manager import EffectsDatabaseManager

def test_ui_click_fix():
    """Teste la correction du problème de clic UI"""
    
    print("=== TEST CORRECTION CLIC UI ===\n")
    
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
    
    print("1. Test de l'état initial:")
    
    # Vérifier que les capacités sont utilisables au début
    for i, ability in enumerate(skyla.abilities):
        can_use = engine.can_use_ability(skyla, ability)
        ability_name = getattr(ability, 'name', 'N/A')
        print(f"   Capacité {i+1} ({ability_name}): {can_use}")
    
    print("\n2. Test après utilisation de Capacité 1:")
    
    # Utiliser Capacité 1
    success1, message1 = engine.use_ability_by_id(skyla, "5754", None)
    print(f"   Capacité 1 utilisée: {success1} - {message1}")
    
    print("\n3. Test de can_use_ability après Capacité 1:")
    
    # Vérifier que la Capacité 2 peut être utilisée après la Capacité 1
    for i, ability in enumerate(skyla.abilities):
        can_use = engine.can_use_ability(skyla, ability)
        ability_name = getattr(ability, 'name', 'N/A')
        ability_id = getattr(ability, 'ability_id', 'N/A')
        print(f"   Capacité {i+1} ({ability_name} - ID: {ability_id}): {can_use}")
        
        # Vérifier la cohérence avec can_use_ability_by_id
        if hasattr(ability, 'ability_id'):
            can_use_by_id = engine.can_use_ability_by_id(skyla, ability.ability_id)
            print(f"     can_use_ability_by_id: {can_use_by_id}")
            
            if can_use != can_use_by_id:
                print(f"     ⚠️  INCOHÉRENCE DÉTECTÉE!")
            else:
                print(f"     ✅ Cohérence OK")
    
    print("\n4. Test de get_ability_cooldown:")
    
    # Vérifier que get_ability_cooldown retourne des valeurs correctes
    for i, ability in enumerate(skyla.abilities):
        cooldown = engine.get_ability_cooldown(skyla, ability)
        ability_name = getattr(ability, 'name', 'N/A')
        print(f"   Capacité {i+1} ({ability_name}): cooldown = {cooldown}")
        
        # Vérifier que le cooldown n'est pas -1
        if cooldown == -1:
            print(f"     ❌ ERREUR: get_ability_cooldown retourne -1")
        else:
            print(f"     ✅ OK: get_ability_cooldown retourne {cooldown}")
    
    print("\n5. Test de simulation de clic UI:")
    
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
    
    print("\n6. Test de l'utilisation de Capacité 2:")
    
    # Tester si la Capacité 2 peut être utilisée
    can_use2 = engine.can_use_ability(skyla, skyla.abilities[1])  # Capacité 2
    if can_use2:
        print("   ✅ Capacité 2 peut être utilisée")
        success2, message2 = engine.use_ability_by_id(skyla, "5755", None)
        print(f"   Capacité 2 utilisée: {success2} - {message2}")
    else:
        print("   ❌ Capacité 2 ne peut pas être utilisée")
        print("   Le problème persiste malgré la correction")
    
    print("\n7. Logs du moteur:")
    
    # Afficher les logs pertinents
    print("   Logs pertinents:")
    for log in engine.log[-15:]:
        if "COOLDOWN" in log or "DEBUG" in log or "ERREUR" in log:
            print(f"     {log}")
    
    print("\n8. Conclusion:")
    
    if can_use2:
        print("   ✅ CORRECTION RÉUSSIE!")
        print("   Le problème de clic UI a été résolu")
        print("   La Capacité 2 peut maintenant être utilisée après la Capacité 1")
    else:
        print("   ❌ CORRECTION ÉCHOUÉE")
        print("   Le problème persiste")
        print("   Il faut investiguer plus en profondeur")
    
    print("\n=== FIN DU TEST ===")

if __name__ == "__main__":
    test_ui_click_fix()
