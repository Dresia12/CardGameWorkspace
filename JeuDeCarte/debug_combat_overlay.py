#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import sys
import os

# Ajouter le chemin du projet au sys.path
project_root = os.path.join(os.path.dirname(__file__))
sys.path.insert(0, project_root)

from Engine.models import Unit, Hero, Player
from Engine.engine import CombatEngine

def debug_combat_overlay():
    """Debug pour vérifier les attributs des unités en combat"""
    
    print("=== DEBUG COMBAT OVERLAY ===")
    
    # 1. Vérifier la structure des données
    print("\n1. Vérification de effects_database.json:")
    try:
        with open("Data/effects_database.json", 'r', encoding='utf-8') as f:
            effects_data = json.load(f)
        
        abilities = effects_data.get("abilities", {})
        passives = effects_data.get("passives", {})
        
        print(f"   - Nombre d'abilités: {len(abilities)}")
        print(f"   - Nombre de passifs: {len(passives)}")
        
        # Vérifier quelques exemples
        if abilities:
            first_ability_id = list(abilities.keys())[0]
            first_ability = abilities[first_ability_id]
            print(f"   - Exemple d'abilité ({first_ability_id}): {first_ability.get('name', 'N/A')}")
        
        if passives:
            first_passive_id = list(passives.keys())[0]
            first_passive = passives[first_passive_id]
            print(f"   - Exemple de passif ({first_passive_id}): {first_passive.get('name', 'N/A')}")
            
    except Exception as e:
        print(f"   ERREUR: {e}")
        return
    
    # 2. Vérifier les unités
    print("\n2. Vérification de units.json:")
    try:
        with open("Data/units.json", 'r', encoding='utf-8') as f:
            units_data = json.load(f)
        
        print(f"   - Nombre d'unités: {len(units_data)}")
        
        # Vérifier quelques unités avec leurs capacités/passifs
        for i, (unit_id, unit_data) in enumerate(units_data.items()):
            if i >= 3:  # Limiter à 3 exemples
                break
                
            name = unit_data.get('name', 'N/A')
            ability_ids = unit_data.get('ability_ids', [])
            passive_ids = unit_data.get('passive_ids', [])
            
            print(f"   - {name}:")
            print(f"     * Abilités: {ability_ids}")
            print(f"     * Passifs: {passive_ids}")
            
            # Vérifier si les IDs existent dans effects_database
            for ability_id in ability_ids:
                if ability_id in abilities:
                    ability_name = abilities[ability_id].get('name', 'N/A')
                    print(f"       ✓ Abilité {ability_id}: {ability_name}")
                else:
                    print(f"       ✗ Abilité {ability_id}: NON TROUVÉE")
            
            for passive_id in passive_ids:
                if passive_id in passives:
                    passive_name = passives[passive_id].get('name', 'N/A')
                    print(f"       ✓ Passif {passive_id}: {passive_name}")
                else:
                    print(f"       ✗ Passif {passive_id}: NON TROUVÉE")
                    
    except Exception as e:
        print(f"   ERREUR: {e}")
        return
    
    # 3. Créer une unité de test et vérifier ses attributs
    print("\n3. Test de création d'unité:")
    try:
        # Créer une unité de test basée sur les données réelles
        test_unit_data = units_data.get('1', {})  # Première unité
        if test_unit_data:
            test_unit = Unit(
                name=test_unit_data.get('name', 'Test Unit'),
                element=test_unit_data.get('element', 'Feu'),
                hp=test_unit_data.get('hp', 100),
                max_hp=test_unit_data.get('hp', 100),
                attack=test_unit_data.get('attack', 10),
                defense=test_unit_data.get('defense', 5),
                image_path=test_unit_data.get('image_path', 'default.png'),
                rarity=test_unit_data.get('rarity', 'Commun'),
                cost=test_unit_data.get('cost', 0),
                ability_ids=test_unit_data.get('ability_ids', []),
                passive_ids=test_unit_data.get('passive_ids', [])
            )
            
            print(f"   - Unité créée: {test_unit.name}")
            print(f"   - ability_ids: {test_unit.ability_ids}")
            print(f"   - passive_ids: {test_unit.passive_ids}")
            print(f"   - hasattr(ability_ids): {hasattr(test_unit, 'ability_ids')}")
            print(f"   - hasattr(passive_ids): {hasattr(test_unit, 'passive_ids')}")
            
            # Vérifier si les attributs sont accessibles
            if hasattr(test_unit, 'ability_ids') and test_unit.ability_ids:
                print(f"   - Nombre d'abilités: {len(test_unit.ability_ids)}")
                for ability_id in test_unit.ability_ids:
                    if ability_id in abilities:
                        ability_name = abilities[ability_id].get('name', 'N/A')
                        print(f"     * {ability_id}: {ability_name}")
                    else:
                        print(f"     * {ability_id}: NON TROUVÉE")
            
            if hasattr(test_unit, 'passive_ids') and test_unit.passive_ids:
                print(f"   - Nombre de passifs: {len(test_unit.passive_ids)}")
                for passive_id in test_unit.passive_ids:
                    if passive_id in passives:
                        passive_name = passives[passive_id].get('name', 'N/A')
                        print(f"     * {passive_id}: {passive_name}")
                    else:
                        print(f"     * {passive_id}: NON TROUVÉE")
        else:
            print("   - Aucune unité trouvée dans units.json")
            
    except Exception as e:
        print(f"   ERREUR: {e}")
        import traceback
        traceback.print_exc()
    
    # 4. Test de simulation de l'overlay
    print("\n4. Test de simulation de l'overlay:")
    try:
        # Simuler le chargement des données comme dans l'overlay
        with open("Data/effects_database.json", 'r', encoding='utf-8') as f:
            effects_data = json.load(f)
        abilities_data = effects_data.get("abilities", {})
        passives_data = effects_data.get("passives", {})
        
        print(f"   - Données chargées: {len(abilities_data)} abilités, {len(passives_data)} passifs")
        
        # Tester avec une unité spécifique (Alice par exemple)
        alice_unit = None
        for unit_id, unit_data in units_data.items():
            if 'Alice' in unit_data.get('name', ''):
                alice_unit = unit_data
                break
        
        if alice_unit:
            print(f"   - Test avec Alice: {alice_unit.get('name')}")
            ability_ids = alice_unit.get('ability_ids', [])
            passive_ids = alice_unit.get('passive_ids', [])
            
            print(f"     * Abilités: {ability_ids}")
            for ability_id in ability_ids:
                if ability_id in abilities_data:
                    ability = abilities_data[ability_id]
                    name = ability.get('name', 'N/A')
                    description = ability.get('description', 'N/A')
                    cooldown = ability.get('base_cooldown', 0)
                    print(f"       ✓ {ability_id}: {name} (CD: {cooldown})")
                    print(f"         Description: {description[:50]}...")
                else:
                    print(f"       ✗ {ability_id}: NON TROUVÉE")
            
            print(f"     * Passifs: {passive_ids}")
            for passive_id in passive_ids:
                if passive_id in passives_data:
                    passive = passives_data[passive_id]
                    name = passive.get('name', 'N/A')
                    description = passive.get('description', 'N/A')
                    print(f"       ✓ {passive_id}: {name}")
                    print(f"         Description: {description[:50]}...")
                else:
                    print(f"       ✗ {passive_id}: NON TROUVÉE")
        else:
            print("   - Alice non trouvée dans units.json")
            
    except Exception as e:
        print(f"   ERREUR: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n=== FIN DU DEBUG ===")

if __name__ == "__main__":
    debug_combat_overlay()
