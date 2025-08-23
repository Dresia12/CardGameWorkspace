#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Debug final du ciblage de Danse des Alizés dans le jeu réel
"""

import json
import sys
import os

# Ajouter le répertoire parent au path pour les imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Engine.engine import CombatEngine, Player
from Engine.models import Unit, Hero, Ability

def debug_targeting_final():
    """Debug final du ciblage de Danse des Alizés"""
    
    print("=== DEBUG FINAL CIBLAGE DANSE DES ALIZÉS ===")
    
    # 1. Créer un environnement de test identique au jeu
    print("\n1. Création environnement de test...")
    
    # Créer Skyla avec les mêmes stats que dans le jeu
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
    
    # 2. Configurer les propriétaires
    print("\n2. Configuration des propriétaires...")
    
    # Créer le héros
    hero = Hero("Héros Test", "Air", {"hp": 1000, "attack": 30, "defense": 20})
    
    # Créer le joueur avec les bonnes arguments
    player1 = Player("Joueur 1", [], hero, [gelidar, frimousse, skyla_unit, roktus, corvus])
    
    # Assigner les propriétaires et initialiser temporary_effects
    for unit in player1.units:
        unit.owner = player1
        unit.temporary_effects = []
    player1.hero.owner = player1
    player1.hero.temporary_effects = []
    
    # 3. Créer le moteur de combat
    print("\n3. Création du moteur de combat...")
    
    # Créer un deuxième joueur vide pour le moteur de combat
    player2 = Player("Joueur 2", [], Hero("Héros Ennemi", "Feu", {"hp": 1000, "attack": 30, "defense": 20}), [])
    
    engine = CombatEngine(player1, player2)
    
    # 4. Tester le ciblage
    print("\n4. Test du ciblage...")
    
    # Créer un battlefield simple
    battlefield = engine
    
    # Charger les données de la capacité "Danse des Alizés"
    with open("Data/effects_database.json", "r", encoding="utf-8") as f:
        effects_db = json.load(f)
    
    ability_data = effects_db.get("abilities", {}).get("5754", {})
    print(f"Données de la capacité: {ability_data}")
    
    # Obtenir les cibles disponibles pour "Danse des Alizés"
    targets = engine.get_available_targets_for_ability(ability_data, skyla_unit, battlefield)
    print(f"Nombre de cibles trouvées: {len(targets)}")
    
    for i, target in enumerate(targets):
        print(f"  Cible {i+1}: {target.name}")
    
    # 5. Vérifier les alliés manuellement
    print("\n5. Vérification manuelle des alliés...")
    
    all_allies = [player1.hero] + player1.units
    print(f"Nombre total d'alliés: {len(all_allies)}")
    
    for i, ally in enumerate(all_allies):
        if hasattr(ally, 'stats'):
            hp = ally.stats.get('hp', 0)
        else:
            hp = getattr(ally, 'hp', 0)
        print(f"  Allié {i+1}: {ally.name} (HP: {hp})")
    
    # 6. Tester l'utilisation de la capacité
    print("\n6. Test de l'utilisation de la capacité...")
    
    # Afficher les stats avant
    print("\nStats AVANT utilisation:")
    for ally in all_allies:
        if hasattr(ally, 'temporary_effects'):
            print(f"  {ally.name}: {len(ally.temporary_effects)} effets temporaires")
        else:
            print(f"  {ally.name}: Pas d'effets temporaires")
    
    # Utiliser la capacité
    # Pour une capacité all_allies, passer toutes les cibles
    if ability_data.get("target_type") == "all_allies":
        result = engine.use_ability_by_id(skyla_unit, "5754", targets)
    else:
        result = engine.use_ability_by_id(skyla_unit, "5754", targets[0] if targets else None)
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
    
    # 7. Vérifier les logs du moteur
    print("\n7. Logs du moteur:")
    for log in engine.log[-20:]:  # Derniers 20 logs
        print(f"  {log}")
    
    print("\n=== FIN DU DEBUG ===")

if __name__ == "__main__":
    debug_targeting_final()
