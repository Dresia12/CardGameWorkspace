#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test de la correction dans le jeu réel
"""

import json
import sys
import os

# Ajouter le répertoire parent au path pour les imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Engine.engine import CombatEngine, Player
from Engine.models import Unit, Hero, Ability

def test_game_real():
    """Test de la correction dans le jeu réel"""
    
    print("=== TEST CORRECTION JEU RÉEL ===")
    
    # Créer un environnement de test identique au jeu
    skyla_unit = Unit(
        name="Skyla, Danseuse des Nuages",
        element="Air",
        stats={"hp": 1010, "attack": 28, "defense": 18},
        abilities=[]
    )
    
    # Créer les alliés avec les mêmes stats que dans le jeu
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
    
    corvus = Unit(
        name="Corvus, Corbeau Mystique",
        element="Ténèbres",
        stats={"hp": 1113, "attack": 33, "defense": 21},
        abilities=[]
    )
    
    # Créer le héros
    hero = Hero("Héros Test", "Air", {"hp": 1000, "attack": 30, "defense": 20})
    
    # Créer le joueur
    player1 = Player("Joueur 1", [], hero, [gelidar, frimousse, skyla_unit, roktus, corvus])
    
    # Créer un deuxième joueur vide
    player2 = Player("Joueur 2", [], Hero("Héros Ennemi", "Feu", {"hp": 1000, "attack": 30, "defense": 20}), [])
    
    # Créer le moteur de combat
    engine = CombatEngine(player1, player2)
    
    # Charger les données de la capacité
    with open("Data/effects_database.json", "r", encoding="utf-8") as f:
        effects_db = json.load(f)
    
    ability_data = effects_db.get("abilities", {}).get("5754", {})
    
    # Obtenir les cibles
    targets = engine.get_available_targets_for_ability(ability_data, skyla_unit, engine)
    
    print(f"Nombre de cibles trouvées: {len(targets)}")
    for i, target in enumerate(targets):
        print(f"  Cible {i+1}: {target.name}")
    
    # Afficher les stats avant
    print("\nStats AVANT utilisation:")
    all_allies = [player1.hero] + player1.units
    for ally in all_allies:
        if hasattr(ally, 'temporary_effects'):
            print(f"  {ally.name}: {len(ally.temporary_effects)} effets temporaires")
        else:
            print(f"  {ally.name}: Pas d'effets temporaires")
    
    # Utiliser la capacité avec la nouvelle logique
    result = engine.use_ability_by_id(skyla_unit, "5754", targets)
    print(f"\nRésultat de l'utilisation: {result}")
    
    # Afficher les stats après
    print("\nStats APRÈS utilisation:")
    for ally in all_allies:
        if hasattr(ally, 'temporary_effects'):
            print(f"  {ally.name}: {len(ally.temporary_effects)} effets temporaires")
            for effect in ally.temporary_effects:
                print(f"    - {effect.get('type', 'inconnu')}: {effect}")
        else:
            print(f"  {ally.name}: Pas d'effets temporaires")
    
    # Vérifier les logs du moteur
    print("\nLogs du moteur:")
    for log in engine.log[-20:]:  # Derniers 20 logs
        print(f"  {log}")
    
    print("\n=== FIN DU TEST ===")

if __name__ == "__main__":
    test_game_real()
