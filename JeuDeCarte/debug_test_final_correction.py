#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import json
import random

# Ajouter le répertoire parent au path pour importer les modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Engine.engine import CombatEngine, Player
from Engine.effects_database_manager import EffectsDatabaseManager
from Engine.target_manager import TargetManager
from Engine.models import Hero, Unit

def test_final_correction():
    """Test final de la correction pour Danse des Alizés"""
    print("=== TEST FINAL DE LA CORRECTION ===")
    
    # Créer le héros
    hero_data = {
        "id": "hero_1",
        "name": "Héros Test",
        "element": "AIR",
        "hp": 100,
        "max_hp": 100,
        "attack": 50,
        "defense": 30,
        "crit_rate": 0.1,
        "crit_damage": 1.5,
        "dodge": 0.05,
        "precision": 0.9,
        "mana": 100,
        "max_mana": 100
    }
    hero = Hero(hero_data)
    
    # Créer les unités
    units_data = [
        {
            "id": "unit_1",
            "name": "Skyla",
            "element": "AIR",
            "hp": 80,
            "max_hp": 80,
            "attack": 40,
            "defense": 25,
            "crit_rate": 0.15,
            "crit_damage": 1.6,
            "dodge": 0.1,
            "precision": 0.85,
            "mana": 80,
            "max_mana": 80,
            "abilities": ["5754", "5755"]
        },
        {
            "id": "unit_2", 
            "name": "Gelidar",
            "element": "GLACE",
            "hp": 90,
            "max_hp": 90,
            "attack": 35,
            "defense": 30,
            "crit_rate": 0.1,
            "crit_damage": 1.5,
            "dodge": 0.05,
            "precision": 0.9,
            "mana": 90,
            "max_mana": 90,
            "abilities": []
        },
        {
            "id": "unit_3",
            "name": "Pyro",
            "element": "FEU", 
            "hp": 85,
            "max_hp": 85,
            "attack": 45,
            "defense": 20,
            "crit_rate": 0.12,
            "crit_damage": 1.7,
            "dodge": 0.03,
            "precision": 0.88,
            "mana": 85,
            "max_mana": 85,
            "abilities": []
        },
        {
            "id": "unit_4",
            "name": "Terra",
            "element": "TERRE",
            "hp": 95,
            "max_hp": 95,
            "attack": 30,
            "defense": 35,
            "crit_rate": 0.08,
            "crit_damage": 1.4,
            "dodge": 0.02,
            "precision": 0.92,
            "mana": 95,
            "max_mana": 95,
            "abilities": []
        }
    ]
    
    units = []
    for unit_data in units_data:
        unit = Unit(unit_data)
        unit.temporary_effects = []
        unit.ability_cooldowns = {}
        units.append(unit)
    
    # Créer les joueurs avec les bons arguments
    player1 = Player("Joueur 1", [], hero, units)
    player2 = Player("Joueur 2", [], Hero({"id": "hero_2", "name": "Héros Ennemi", "element": "FEU", "hp": 100, "max_hp": 100, "attack": 50, "defense": 30, "crit_rate": 0.1, "crit_damage": 1.5, "dodge": 0.05, "precision": 0.9, "mana": 100, "max_mana": 100}), [])
    
    # Assigner les propriétaires
    hero.owner = player1
    for unit in units:
        unit.owner = player1
    
    # Créer le moteur de combat
    engine = CombatEngine(player1, player2)
    
    # Charger les données de la capacité
    with open("Data/effects_database.json", "r", encoding="utf-8") as f:
        effects_db = json.load(f)
    
    ability_data = effects_db.get("abilities", {}).get("5754", {})
    print(f"Capacité testée: {ability_data.get('name', 'Inconnue')}")
    print(f"Target type: {ability_data.get('target_type', 'Inconnu')}")
    
    # Obtenir les cibles
    targets = engine.get_available_targets_for_ability(ability_data, player1.units[0], engine)
    
    print(f"\nNombre de cibles trouvées: {len(targets)}")
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
    
    # Utiliser la capacité
    result = engine.use_ability_by_id(player1.units[0], "5754")
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
    test_final_correction()
