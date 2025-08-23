#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test de la correction de la chaîne de ciblage pour Danse des Alizés
"""

import json
import sys
import os

# Ajouter le répertoire parent au path pour les imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Engine.engine import CombatEngine, Player
from Engine.models import Unit, Hero, Ability

def test_chain_correction():
    """Test de la correction de la chaîne de ciblage"""
    
    print("=== TEST CORRECTION CHAÎNE DE CIBLAGE ===")
    
    # Créer un environnement de test simple
    skyla_unit = Unit(
        name="Skyla, Danseuse des Nuages",
        element="Air",
        stats={"hp": 1010, "attack": 28, "defense": 18},
        abilities=[]
    )
    
    ally1 = Unit(
        name="Allié Test 1",
        element="4",
        stats={"hp": 100, "attack": 50, "defense": 30},
        abilities=[]
    )
    ally1.crit_pct = 5
    ally1.esquive_pct = 3
    
    ally2 = Unit(
        name="Allié Test 2", 
        element="1",
        stats={"hp": 80, "attack": 60, "defense": 20},
        abilities=[]
    )
    ally2.crit_pct = 8
    ally2.esquive_pct = 2
    
    # Créer des héros et joueurs
    hero1 = Hero("Héros Test 1", "Air", {"hp": 100, "attack": 20, "defense": 15})
    hero2 = Hero("Héros Test 2", "Feu", {"hp": 100, "attack": 20, "defense": 15})
    
    player1 = Player("Joueur 1", [], hero1, [skyla_unit, ally1, ally2])
    player2 = Player("Joueur 2", [], hero2, [])
    
    # Assigner l'attribut owner
    skyla_unit.owner = player1
    ally1.owner = player1
    ally2.owner = player1
    hero1.owner = player1
    hero2.owner = player2
    
    # Créer le moteur de combat
    engine = CombatEngine(player1, player2)
    
    # Charger et créer la capacité
    with open("Data/effects_database.json", 'r', encoding='utf-8') as f:
        effects_data = json.load(f)
    
    abilities_data = effects_data.get("abilities", {})
    danse_alizes = abilities_data.get("5754", {})
    
    print(f"Capacité Danse des Alizés:")
    print(f"  target_type: {danse_alizes.get('target_type', 'N/A')}")
    print(f"  crit_boost: {danse_alizes.get('crit_boost', 'N/A')}")
    print(f"  crit_duration: {danse_alizes.get('crit_duration', 'N/A')}")
    
    ability = Ability(
        name=danse_alizes.get('name', 'Danse des Alizés'),
        description=danse_alizes.get('description', ''),
        cooldown=danse_alizes.get('base_cooldown', 0)
    )
    ability.ability_id = "5754"
    skyla_unit.abilities = [ability]
    
    print("\nAVANT utilisation:")
    for unit in [skyla_unit, ally1, ally2]:
        print(f"  {unit.name}: {len(getattr(unit, 'temporary_effects', []))} effets")
    
    # Utiliser la capacité
    success, message = engine.use_ability_by_id(skyla_unit, "5754")
    
    print(f"\nRésultat: {success} - {message}")
    
    print("\nAPRÈS utilisation:")
    for unit in [skyla_unit, ally1, ally2]:
        effects = getattr(unit, 'temporary_effects', [])
        print(f"  {unit.name}: {len(effects)} effets")
        if effects:
            for effect in effects:
                print(f"    * {effect}")
    
    # Vérifier si tous ont reçu crit_boost ET dodge_boost
    print("\nVÉRIFICATION:")
    for unit in [skyla_unit, ally1, ally2]:
        effects = getattr(unit, 'temporary_effects', [])
        crit_boost = any(e.get('type') == 'crit_boost' for e in effects)
        dodge_boost = any(e.get('type') == 'dodge_boost' for e in effects)
        print(f"  {unit.name}: Crit boost={crit_boost}, Dodge boost={dodge_boost}")
        
        if crit_boost and dodge_boost:
            print(f"    ✅ {unit.name} a reçu les deux effets !")
        elif crit_boost:
            print(f"    ⚠️  {unit.name} n'a reçu que crit_boost")
        elif dodge_boost:
            print(f"    ⚠️  {unit.name} n'a reçu que dodge_boost")
        else:
            print(f"    ❌ {unit.name} n'a reçu aucun effet")
    
    print("\n=== FIN TEST ===")

if __name__ == "__main__":
    test_chain_correction()
