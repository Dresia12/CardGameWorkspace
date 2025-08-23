#!/usr/bin/env python3
"""
Script de test pour vérifier tous les types de ciblage
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Engine.engine import CombatEngine, Player
from Engine.models import Hero, Unit
from Engine.target_manager import TargetManager

def test_target_types():
    """Teste tous les types de ciblage"""
    
    print("=== TEST DES TYPES DE CIBLAGE ===\n")
    
    # Créer un moteur de combat
    engine = CombatEngine()
    
    # Créer des joueurs et unités de test
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
    
    # Configurer le moteur
    engine.players = [player1, player2]
    engine.current_player = player1
    
    # Tester chaque type de ciblage
    target_types = [
        "single_enemy",
        "single_ally", 
        "self",
        "all_enemies",
        "all_allies",
        "all_units",
        "random_enemy",
        "random_ally",
        "random_unit",
        "chain_enemies",
        "chain_allies",
        "front_row",
        "back_row",
        "adjacent_enemies",
        "adjacent_allies"
    ]
    
    for target_type in target_types:
        print(f"--- Test {target_type} ---")
        
        # Créer une capacité de test
        test_ability = {
            "target_type": target_type,
            "target_conditions": ["alive"]
        }
        
        # Obtenir les cibles
        try:
            targets = engine.get_available_targets_for_ability(test_ability, units1[0], engine)
            print(f"  Cibles trouvées: {len(targets)}")
            for target in targets:
                print(f"    - {target.name} (HP: {target.hp})")
        except Exception as e:
            print(f"  Erreur: {e}")
        
        print()
    
    print("=== FIN DES TESTS ===")

if __name__ == "__main__":
    test_target_types()
