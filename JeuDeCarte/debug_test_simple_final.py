#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test simple de la correction pour Danse des Alizés
"""

import json
import sys
import os

# Ajouter le répertoire parent au path pour les imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Engine.engine import CombatEngine, Player
from Engine.models import Unit, Hero, Ability

def test_simple_final():
    """Test simple de la correction"""
    
    print("=== TEST SIMPLE DE LA CORRECTION ===")
    
    # Créer Skyla
    skyla_unit = Unit(
        name="Skyla, Danseuse des Nuages",
        element="Air",
        stats={"hp": 1010, "attack": 28, "defense": 18},
        abilities=[]
    )
    
    # Créer les alliés
    gelidar = Unit(
        name="Gelidar, Chevalier des Neiges",
        element="Glace",
        stats={"hp": 1100, "attack": 25, "defense": 28},
        abilities=[]
    )
    
    frimousse = Unit(
        name="Frimousse, Esprit Givré",
        element="Glace",
        stats={"hp": 773, "attack": 23, "defense": 13},
        abilities=[]
    )
    
    roktus = Unit(
        name="Roktus, Gobelin Mineur",
        element="Terre",
        stats={"hp": 845, "attack": 26, "defense": 12},
        abilities=[]
    )
    
    # Créer le héros
    hero = Hero("Héros Test", "Air", {"hp": 1000, "attack": 30, "defense": 20})
    
    # Créer le joueur
    player1 = Player("Joueur 1", [], hero, [gelidar, frimousse, skyla_unit, roktus])
    
    # Assigner les propriétaires et initialiser temporary_effects
    for unit in player1.units:
        unit.owner = player1
        unit.temporary_effects = []
    player1.hero.owner = player1
    player1.hero.temporary_effects = []
    
    # Créer le deuxième joueur
    player2 = Player("Joueur 2", [], Hero("Héros Ennemi", "Feu", {"hp": 1000, "attack": 30, "defense": 20}), [])
    
    # Créer le moteur de combat
    engine = CombatEngine(player1, player2)
    
    # Afficher les stats avant
    print("\nStats AVANT utilisation:")
    all_allies = [player1.hero] + player1.units
    for ally in all_allies:
        print(f"  {ally.name}: {len(ally.temporary_effects)} effets temporaires")
    
    # Utiliser la capacité
    result = engine.use_ability_by_id(skyla_unit, "5754")
    print(f"\nRésultat de l'utilisation: {result}")
    
    # Afficher les stats après
    print("\nStats APRÈS utilisation:")
    for ally in all_allies:
        print(f"  {ally.name}: {len(ally.temporary_effects)} effets temporaires")
        for effect in ally.temporary_effects:
            print(f"    - {effect.get('type', 'inconnu')}: {effect}")
    
    # Vérifier les logs du moteur
    print("\nLogs du moteur:")
    for log in engine.log[-10:]:  # Derniers 10 logs
        print(f"  {log}")
    
    print("\n=== FIN DU TEST ===")

if __name__ == "__main__":
    test_simple_final()
