#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de debug pour analyser les capacités de Skyla
"""

import json
import sys
import os

# Ajouter le répertoire parent au path pour les imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Engine.engine import CombatEngine, Player
from Engine.models import Unit, Hero
from Engine.effects_database_manager import EffectsDatabaseManager

def debug_skyla_abilities():
    """Debug spécifique pour les capacités de Skyla"""
    
    print("=== DEBUG SKYLA CAPACITÉS ===")
    
    # 1. Charger les données de Skyla
    print("\n1. Chargement des données de Skyla...")
    try:
        with open("Data/units.json", 'r', encoding='utf-8') as f:
            units_data = json.load(f)
        
        skyla_data = None
        for unit_data in units_data:
            if unit_data.get("name") == "Skyla, Danseuse des Nuages":
                skyla_data = unit_data
                break
        
        if not skyla_data:
            print("❌ Skyla non trouvée dans units.json")
            return
        
        print(f"✅ Skyla trouvée: {skyla_data['name']}")
        print(f"   Capacités: {skyla_data.get('ability_ids', [])}")
        
    except Exception as e:
        print(f"❌ Erreur chargement units.json: {e}")
        return
    
    # 2. Charger les capacités
    print("\n2. Chargement des capacités...")
    try:
        with open("Data/effects_database.json", 'r', encoding='utf-8') as f:
            effects_data = json.load(f)
        
        abilities_data = effects_data.get("abilities", {})
        
        for ability_id in skyla_data.get('ability_ids', []):
            if ability_id in abilities_data:
                ability = abilities_data[ability_id]
                print(f"✅ Capacité {ability_id}: {ability.get('name', 'N/A')}")
                print(f"   Target type: {ability.get('target_type', 'N/A')}")
                print(f"   Crit boost: {ability.get('crit_boost', 'N/A')}")
                print(f"   Grant passive: {ability.get('grant_passive', 'N/A')}")
            else:
                print(f"❌ Capacité {ability_id} non trouvée")
                
    except Exception as e:
        print(f"❌ Erreur chargement effects_database.json: {e}")
        return
    
    # 3. Créer un environnement de test
    print("\n3. Création environnement de test...")
    try:
        # Créer Skyla
        skyla_unit = Unit(
            name=skyla_data["name"],
            element=skyla_data["element"],
            stats={
                "hp": skyla_data["hp"],
                "attack": skyla_data["attack"],
                "defense": skyla_data["defense"],
                "crit_pct": skyla_data.get("crit_pct", 0),
                "esquive_pct": skyla_data.get("esquive_pct", 0),
                "precision_pct": skyla_data.get("precision_pct", 0)
            },
            abilities=skyla_data.get("ability_ids", [])
        )
        
        # Créer des alliés de test
        ally1 = Unit(
            name="Allié Test 1",
            element="4",  # Air
            stats={"hp": 100, "attack": 50, "defense": 30},
            abilities=[]
        )
        
        ally2 = Unit(
            name="Allié Test 2", 
            element="1",  # Feu
            stats={"hp": 80, "attack": 60, "defense": 20},
            abilities=[]
        )
        
        # Créer des héros de test
        hero1 = Hero("Héros Test 1", "Air", {"hp": 100, "attack": 20, "defense": 15})
        hero2 = Hero("Héros Test 2", "Feu", {"hp": 100, "attack": 20, "defense": 15})
        
        # Créer des decks vides
        deck1 = []
        deck2 = []
        
        # Créer des joueurs
        player1 = Player("Joueur 1", deck1, hero1, [skyla_unit, ally1, ally2])
        player2 = Player("Joueur 2", deck2, hero2, [])
        
        # Ajouter l'attribut owner pour le système de cibles (après création des joueurs)
        skyla_unit.owner = player1
        ally1.owner = player1
        ally2.owner = player1
        
        # Créer le moteur de combat
        engine = CombatEngine(player1, player2)
        
        print(f"✅ Environnement créé")
        print(f"   Skyla: {skyla_unit.name} (HP: {skyla_unit.hp})")
        print(f"   Allié 1: {ally1.name} (HP: {ally1.hp})")
        print(f"   Allié 2: {ally2.name} (HP: {ally2.hp})")
        
    except Exception as e:
        print(f"❌ Erreur création environnement: {e}")
        return
    
    # 4. Tester la capacité "Danse des Alizés" (5754)
    print("\n4. Test capacité 'Danse des Alizés' (5754)...")
    try:
        print("   Avant utilisation:")
        print(f"   - Skyla effets temporaires: {len(getattr(skyla_unit, 'temporary_effects', []))}")
        print(f"   - Allié 1 effets temporaires: {len(getattr(ally1, 'temporary_effects', []))}")
        print(f"   - Allié 2 effets temporaires: {len(getattr(ally2, 'temporary_effects', []))}")
        
        # Utiliser la capacité
        success, message = engine.use_ability_by_id(skyla_unit, "5754")
        
        print(f"   Résultat: {success} - {message}")
        print("   Après utilisation:")
        print(f"   - Skyla effets temporaires: {len(getattr(skyla_unit, 'temporary_effects', []))}")
        print(f"   - Allié 1 effets temporaires: {len(getattr(ally1, 'temporary_effects', []))}")
        print(f"   - Allié 2 effets temporaires: {len(getattr(ally2, 'temporary_effects', []))}")
        
        # Afficher les effets détaillés
        for unit in [skyla_unit, ally1, ally2]:
            effects = getattr(unit, 'temporary_effects', [])
            if effects:
                print(f"   - {unit.name} effets:")
                for effect in effects:
                    print(f"     * {effect}")
        
    except Exception as e:
        print(f"❌ Erreur test capacité 5754: {e}")
        import traceback
        traceback.print_exc()
    
    # 5. Tester la capacité "Symphonie de l'Air" (5755)
    print("\n5. Test capacité 'Symphonie de l'Air' (5755)...")
    try:
        print("   Avant utilisation:")
        print(f"   - Skyla effets temporaires: {len(getattr(skyla_unit, 'temporary_effects', []))}")
        print(f"   - Allié 1 effets temporaires: {len(getattr(ally1, 'temporary_effects', []))}")
        
        # Utiliser la capacité sur l'allié 1
        success, message = engine.use_ability_by_id(skyla_unit, "5755", ally1)
        
        print(f"   Résultat: {success} - {message}")
        print("   Après utilisation:")
        print(f"   - Skyla effets temporaires: {len(getattr(skyla_unit, 'temporary_effects', []))}")
        print(f"   - Allié 1 effets temporaires: {len(getattr(ally1, 'temporary_effects', []))}")
        
        # Afficher les effets détaillés
        for unit in [skyla_unit, ally1]:
            effects = getattr(unit, 'temporary_effects', [])
            if effects:
                print(f"   - {unit.name} effets:")
                for effect in effects:
                    print(f"     * {effect}")
        
    except Exception as e:
        print(f"❌ Erreur test capacité 5755: {e}")
        import traceback
        traceback.print_exc()
    
    # 6. Vérifier les logs du moteur
    print("\n6. Logs du moteur de combat:")
    for log_entry in engine.log[-10:]:  # 10 dernières entrées
        print(f"   {log_entry}")
    
    print("\n=== FIN DEBUG ===")

if __name__ == "__main__":
    debug_skyla_abilities()
