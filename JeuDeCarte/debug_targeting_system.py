#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de debug pour analyser le système de ciblage
"""

import json
import sys
import os

# Ajouter le répertoire parent au path pour les imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Engine.engine import CombatEngine, Player
from Engine.models import Unit, Hero, Ability

def debug_targeting_system():
    """Debug du système de ciblage"""
    
    print("=== DEBUG SYSTÈME DE CIBLAGE ===")
    
    # 1. Créer un environnement de test
    print("\n1. Création environnement de test...")
    
    # Créer Skyla
    skyla_unit = Unit(
        name="Skyla, Danseuse des Nuages",
        element="Air",
        stats={"hp": 1010, "attack": 28, "defense": 18},
        abilities=[]
    )
    
    # Créer des alliés
    ally1 = Unit(
        name="Allié Test 1",
        element="4",
        stats={"hp": 100, "attack": 50, "defense": 30},
        abilities=[]
    )
    
    ally2 = Unit(
        name="Allié Test 2", 
        element="1",
        stats={"hp": 80, "attack": 60, "defense": 20},
        abilities=[]
    )
    
    # Créer des héros
    hero1 = Hero("Héros Test 1", "Air", {"hp": 100, "attack": 20, "defense": 15})
    hero2 = Hero("Héros Test 2", "Feu", {"hp": 100, "attack": 20, "defense": 15})
    
    # Créer des joueurs
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
    
    print(f"✅ Environnement créé")
    print(f"   Skyla: {skyla_unit.name} (owner: {skyla_unit.owner.name})")
    print(f"   Allié 1: {ally1.name} (owner: {ally1.owner.name})")
    print(f"   Allié 2: {ally2.name} (owner: {ally2.owner.name})")
    
    # 2. Tester le système de ciblage
    print("\n2. Test du système de ciblage...")
    
    # Test all_allies
    print("\n   Test ciblage 'all_allies':")
    try:
        targets = engine.get_all_allies_targets(skyla_unit)
        print(f"   Cibles trouvées: {len(targets)}")
        for i, target in enumerate(targets):
            print(f"   - Cible {i+1}: {target.name} (owner: {target.owner.name})")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    # Test single_ally
    print("\n   Test ciblage 'single_ally':")
    try:
        targets = engine.get_single_ally_targets(skyla_unit, ally1)
        print(f"   Cibles trouvées: {len(targets)}")
        for i, target in enumerate(targets):
            print(f"   - Cible {i+1}: {target.name} (owner: {target.owner.name})")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    # 3. Tester les capacités avec debug détaillé
    print("\n3. Test des capacités avec debug détaillé...")
    
    # Charger les capacités
    with open("Data/effects_database.json", 'r', encoding='utf-8') as f:
        effects_data = json.load(f)
    
    abilities_data = effects_data.get("abilities", {})
    
    # Créer les objets Ability
    abilities = []
    for ability_id in ["5754", "5755"]:
        if ability_id in abilities_data:
            ability_data = abilities_data[ability_id]
            ability = Ability(
                name=ability_data.get('name', 'Capacité inconnue'),
                description=ability_data.get('description', ''),
                cooldown=ability_data.get('base_cooldown', 0)
            )
            ability.ability_id = ability_id
            abilities.append(ability)
    
    skyla_unit.abilities = abilities
    
    # Test capacité 5754 (Danse des Alizés)
    print("\n   Test capacité 5754 (Danse des Alizés):")
    print(f"   Target type: {abilities_data['5754'].get('target_type', 'N/A')}")
    
    try:
        # Utiliser la capacité
        success, message = engine.use_ability_by_id(skyla_unit, "5754")
        print(f"   Résultat: {success} - {message}")
        
        # Vérifier les effets
        print(f"   Effets après utilisation:")
        print(f"   - Skyla: {len(skyla_unit.temporary_effects)} effets")
        for effect in skyla_unit.temporary_effects:
            print(f"     * {effect}")
        
        print(f"   - Allié 1: {len(ally1.temporary_effects)} effets")
        for effect in ally1.temporary_effects:
            print(f"     * {effect}")
        
        print(f"   - Allié 2: {len(ally2.temporary_effects)} effets")
        for effect in ally2.temporary_effects:
            print(f"     * {effect}")
        
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
    
    # 4. Vérifier les logs du moteur
    print("\n4. Logs du moteur de combat:")
    for log_entry in engine.log[-10:]:
        print(f"   {log_entry}")
    
    print("\n=== FIN DEBUG ===")

if __name__ == "__main__":
    debug_targeting_system()
