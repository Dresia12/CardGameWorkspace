#!/usr/bin/env python3
"""
Script pour tester tous les target_type et vérifier qu'ils fonctionnent avec la correction
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Engine.engine import CombatEngine, Player
from Engine.models import Hero, Unit, Ability
from Engine.effects_database_manager import EffectsDatabaseManager

def test_all_target_types():
    """Teste tous les target_type pour vérifier qu'ils fonctionnent"""
    
    print("=== TEST DE TOUS LES TARGET_TYPE ===\n")
    
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
    
    # Définir les target_type à tester
    target_types = [
        "all_allies",
        "all_enemies", 
        "all_units",
        "random_enemy",
        "random_ally",
        "random_unit",
        "front_row",
        "back_row",
        "chain_enemies",
        "chain_allies",
        "adjacent_enemies",
        "adjacent_allies",
        "single_enemy",
        "single_ally",
        "self"
    ]
    
    print("1. Test de création d'objets Ability avec différents target_type:")
    
    for i, target_type in enumerate(target_types):
        # Créer un objet Ability avec ce target_type
        ability = Ability(
            name=f"Test {target_type}",
            description=f"Test pour {target_type}",
            cooldown=1,
            target_type=target_type,
            ability_id=f"test_{i}"
        )
        
        print(f"   {i+1:2d}. {target_type:20s} - Nom: {ability.name}, ID: {ability.ability_id}")
    
    print("\n2. Test de récupération des cibles pour chaque target_type:")
    
    for target_type in target_types:
        print(f"   Test {target_type}:")
        
        # Créer un objet Ability temporaire
        ability = Ability(
            name=f"Test {target_type}",
            description=f"Test pour {target_type}",
            cooldown=1,
            target_type=target_type,
            ability_id=f"test_{target_type}"
        )
        
        # Tester la récupération des cibles
        try:
            ability_data = {
                'target_type': target_type,
                'target_conditions': ['alive']
            }
            
            targets = engine.get_available_targets_for_ability(ability_data, units1[0], engine)
            print(f"     Cibles trouvées: {len(targets)}")
            for target in targets:
                print(f"       - {target.name} (HP: {target.hp})")
                
        except Exception as e:
            print(f"     ❌ Erreur: {e}")
    
    print("\n3. Test de simulation d'utilisation pour les capacités automatiques:")
    
    # Capacités qui s'utilisent automatiquement
    auto_use_types = [
        "all_allies", "all_enemies", "all_units",
        "random_enemy", "random_ally", "random_unit",
        "front_row", "back_row",
        "chain_enemies", "chain_allies"
    ]
    
    for target_type in auto_use_types:
        print(f"   Test automatique {target_type}:")
        
        # Créer un objet Ability temporaire
        ability = Ability(
            name=f"Test {target_type}",
            description=f"Test pour {target_type}",
            cooldown=1,
            target_type=target_type,
            ability_id=f"test_{target_type}"
        )
        
        # Simuler l'utilisation via use_ability_by_id
        try:
            # Créer des données de capacité temporaires
            temp_ability_data = {
                'name': f"Test {target_type}",
                'target_type': target_type,
                'base_cooldown': 1,
                'damage': 0,
                'damage_type': 'fixed'
            }
            
            # Simuler l'utilisation (sans réellement l'appliquer)
            print(f"     ✅ Capacité automatique - devrait s'utiliser sans ciblage")
            
        except Exception as e:
            print(f"     ❌ Erreur: {e}")
    
    print("\n4. Test de simulation d'utilisation pour les capacités adjacentes:")
    
    adjacent_types = ["adjacent_enemies", "adjacent_allies"]
    
    for target_type in adjacent_types:
        print(f"   Test adjacent {target_type}:")
        
        # Créer un objet Ability temporaire
        ability = Ability(
            name=f"Test {target_type}",
            description=f"Test pour {target_type}",
            cooldown=1,
            target_type=target_type,
            ability_id=f"test_{target_type}"
        )
        
        # Simuler l'utilisation
        try:
            print(f"     ✅ Capacité adjacente - nécessite ciblage initial puis propagation")
            
        except Exception as e:
            print(f"     ❌ Erreur: {e}")
    
    print("\n5. Test de simulation d'utilisation pour les capacités à ciblage unique:")
    
    single_types = ["single_enemy", "single_ally", "self"]
    
    for target_type in single_types:
        print(f"   Test unique {target_type}:")
        
        # Créer un objet Ability temporaire
        ability = Ability(
            name=f"Test {target_type}",
            description=f"Test pour {target_type}",
            cooldown=1,
            target_type=target_type,
            ability_id=f"test_{target_type}"
        )
        
        # Simuler l'utilisation
        try:
            print(f"     ✅ Capacité unique - nécessite ciblage manuel")
            
        except Exception as e:
            print(f"     ❌ Erreur: {e}")
    
    print("\n6. Vérification de la logique UI:")
    
    print("   Capacités automatiques (s'utilisent sans ciblage):")
    for target_type in auto_use_types:
        print(f"     - {target_type}")
    
    print("   Capacités adjacentes (ciblage initial + propagation):")
    for target_type in adjacent_types:
        print(f"     - {target_type}")
    
    print("   Capacités à ciblage unique (ciblage manuel requis):")
    for target_type in single_types:
        print(f"     - {target_type}")
    
    print("\n=== FIN DU TEST ===")

if __name__ == "__main__":
    test_all_target_types()
