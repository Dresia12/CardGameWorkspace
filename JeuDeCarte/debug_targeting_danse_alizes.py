#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de debug pour le ciblage de "Danse des Alizés"
"""

import json
import sys
import os

# Ajouter le répertoire parent au path pour les imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Engine.engine import CombatEngine, Player
from Engine.models import Unit, Hero, Ability

def debug_targeting_danse_alizes():
    """Debug du ciblage de Danse des Alizés"""
    
    print("=== DEBUG CIBLAGE DANSE DES ALIZÉS ===")
    
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
    
    ally3 = Unit(
        name="Allié Test 3", 
        element="2",
        stats={"hp": 90, "attack": 40, "defense": 25},
        abilities=[]
    )
    ally3.crit_pct = 6
    ally3.esquive_pct = 4
    
    # Créer des héros
    hero1 = Hero("Héros Test 1", "Air", {"hp": 100, "attack": 20, "defense": 15})
    hero2 = Hero("Héros Test 2", "Feu", {"hp": 100, "attack": 20, "defense": 15})
    
    # Créer des joueurs
    player1 = Player("Joueur 1", [], hero1, [skyla_unit, ally1, ally2, ally3])
    player2 = Player("Joueur 2", [], hero2, [])
    
    # Assigner l'attribut owner
    skyla_unit.owner = player1
    ally1.owner = player1
    ally2.owner = player1
    ally3.owner = player1
    hero1.owner = player1
    hero2.owner = player2
    
    # Créer le moteur de combat
    engine = CombatEngine(player1, player2)
    
    print(f"✅ Environnement créé")
    print(f"   Skyla: {skyla_unit.name}")
    print(f"   Allié 1: {ally1.name}")
    print(f"   Allié 2: {ally2.name}")
    print(f"   Allié 3: {ally3.name}")
    
    # 2. Charger la capacité "Danse des Alizés"
    print("\n2. Chargement de la capacité 'Danse des Alizés'...")
    try:
        with open("Data/effects_database.json", 'r', encoding='utf-8') as f:
            effects_data = json.load(f)
        
        abilities_data = effects_data.get("abilities", {})
        danse_alizes = abilities_data.get("5754", {})
        
        print(f"   Nom: {danse_alizes.get('name', 'N/A')}")
        print(f"   Target type: {danse_alizes.get('target_type', 'N/A')}")
        print(f"   Description: {danse_alizes.get('description', 'N/A')}")
        
        # Créer l'objet Ability
        ability = Ability(
            name=danse_alizes.get('name', 'Danse des Alizés'),
            description=danse_alizes.get('description', ''),
            cooldown=danse_alizes.get('base_cooldown', 0)
        )
        ability.ability_id = "5754"
        skyla_unit.abilities = [ability]
        
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return
    
    # 3. Tester le ciblage
    print("\n3. Test du ciblage...")
    
    try:
        # Tester get_available_targets_for_ability
        targets = engine.get_available_targets_for_ability(danse_alizes, skyla_unit, engine)
        print(f"   Cibles trouvées par get_available_targets_for_ability: {len(targets)}")
        for i, target in enumerate(targets):
            print(f"   - Cible {i+1}: {target.name}")
        
        # Tester manuellement le ciblage all_allies
        print(f"\n   Test manuel ciblage 'all_allies':")
        if hasattr(engine, 'players') and engine.players:
            source_player = None
            for player in engine.players:
                if skyla_unit in player.units or skyla_unit == player.hero:
                    source_player = player
                    break
            
            if source_player:
                all_allies = [source_player.hero] + source_player.units
                print(f"   Alliés trouvés: {len(all_allies)}")
                for i, ally in enumerate(all_allies):
                    print(f"   - Allié {i+1}: {ally.name}")
            else:
                print("   ❌ Joueur source non trouvé")
        else:
            print("   ❌ Aucun joueur trouvé")
        
    except Exception as e:
        print(f"   ❌ Erreur ciblage: {e}")
        import traceback
        traceback.print_exc()
    
    # 4. Tester l'utilisation de la capacité
    print("\n4. Test de l'utilisation de la capacité...")
    
    print("   AVANT utilisation:")
    for unit in [ally1, ally2, ally3]:
        print(f"   - {unit.name}: {len(getattr(unit, 'temporary_effects', []))} effets")
    
    try:
        # Utiliser la capacité
        success, message = engine.use_ability_by_id(skyla_unit, "5754")
        
        print(f"   Résultat: {success} - {message}")
        
        print("   APRÈS utilisation:")
        for unit in [ally1, ally2, ally3]:
            effects = getattr(unit, 'temporary_effects', [])
            print(f"   - {unit.name}: {len(effects)} effets")
            if effects:
                for effect in effects:
                    print(f"     * {effect}")
        
    except Exception as e:
        print(f"   ❌ Erreur utilisation: {e}")
        import traceback
        traceback.print_exc()
    
    # 5. Vérifier les logs du moteur
    print("\n5. Logs du moteur de combat:")
    for log_entry in engine.log[-15:]:
        print(f"   {log_entry}")
    
    print("\n=== FIN DEBUG ===")

if __name__ == "__main__":
    debug_targeting_danse_alizes()
