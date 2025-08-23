#!/usr/bin/env python3
"""
Script de test pour les capacités adjacentes
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Engine.engine import CombatEngine, Player
from Engine.models import Hero, Unit

def test_adjacent_abilities():
    """Teste les capacités adjacentes"""
    
    print("=== TEST DES CAPACITÉS ADJACENTES ===\n")
    
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
    
    # Configurer les propriétaires
    for unit in units1:
        unit.owner = player1
    for unit in units2:
        unit.owner = player2
    
    print("Unités du Joueur 1:")
    for i, unit in enumerate(units1):
        print(f"  {i}: {unit.name} (HP: {unit.hp})")
    
    print("\nUnités du Joueur 2:")
    for i, unit in enumerate(units2):
        print(f"  {i}: {unit.name} (HP: {unit.hp})")
    
    print("\n=== TEST DES CIBLES ADJACENTES ===")
    
    # Tester adjacent_enemies
    print("\n--- Test adjacent_enemies ---")
    for i, enemy in enumerate(units2):
        print(f"\nCible principale: {enemy.name}")
        adjacent = engine._get_adjacent_targets(enemy, "adjacent_enemies")
        if adjacent:
            print(f"  Cibles adjacentes: {[t.name for t in adjacent]}")
        else:
            print("  Aucune cible adjacente")
    
    # Tester adjacent_allies
    print("\n--- Test adjacent_allies ---")
    for i, ally in enumerate(units1):
        print(f"\nCible principale: {ally.name}")
        adjacent = engine._get_adjacent_targets(ally, "adjacent_allies")
        if adjacent:
            print(f"  Cibles adjacentes: {[t.name for t in adjacent]}")
        else:
            print("  Aucune cible adjacente")
    
    print("\n=== FIN DES TESTS ===")

if __name__ == "__main__":
    test_adjacent_abilities()
