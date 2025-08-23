#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de debug spécifique pour "Danse des Alizés"
"""

import json
import sys
import os

# Ajouter le répertoire parent au path pour les imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Engine.engine import CombatEngine, Player
from Engine.models import Unit, Hero, Ability

def debug_danse_alizes():
    """Debug spécifique pour Danse des Alizés"""
    
    print("=== DEBUG DANSE DES ALIZÉS ===")
    
    # 1. Créer un environnement de test
    print("\n1. Création environnement de test...")
    
    # Créer Skyla
    skyla_unit = Unit(
        name="Skyla, Danseuse des Nuages",
        element="Air",
        stats={"hp": 1010, "attack": 28, "defense": 18},
        abilities=[]
    )
    
    # Créer des alliés avec des stats de base
    ally1 = Unit(
        name="Allié Test 1",
        element="4",
        stats={"hp": 100, "attack": 50, "defense": 30},
        abilities=[]
    )
    ally1.crit_pct = 5  # 5% de base
    ally1.esquive_pct = 3  # 3% de base
    ally1.precision_pct = 95  # 95% de base
    
    ally2 = Unit(
        name="Allié Test 2", 
        element="1",
        stats={"hp": 80, "attack": 60, "defense": 20},
        abilities=[]
    )
    ally2.crit_pct = 8  # 8% de base
    ally2.esquive_pct = 2  # 2% de base
    ally2.precision_pct = 90  # 90% de base
    
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
    print(f"   Skyla: {skyla_unit.name}")
    print(f"   Allié 1: {ally1.name} (Crit: {ally1.crit_pct}%, Esq: {ally1.esquive_pct}%)")
    print(f"   Allié 2: {ally2.name} (Crit: {ally2.crit_pct}%, Esq: {ally2.esquive_pct}%)")
    
    # 2. Charger la capacité "Danse des Alizés"
    print("\n2. Chargement de la capacité 'Danse des Alizés'...")
    try:
        with open("Data/effects_database.json", 'r', encoding='utf-8') as f:
            effects_data = json.load(f)
        
        abilities_data = effects_data.get("abilities", {})
        danse_alizes = abilities_data.get("5754", {})
        
        print(f"   Nom: {danse_alizes.get('name', 'N/A')}")
        print(f"   Target type: {danse_alizes.get('target_type', 'N/A')}")
        print(f"   Crit boost: {danse_alizes.get('crit_boost', 'N/A')}")
        print(f"   Crit duration: {danse_alizes.get('crit_duration', 'N/A')}")
        
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
    
    # 3. Tester la capacité
    print("\n3. Test de la capacité 'Danse des Alizés'...")
    
    print("   AVANT utilisation:")
    print(f"   - Allié 1: Crit {ally1.crit_pct}%, Esq {ally1.esquive_pct}%")
    print(f"   - Allié 2: Crit {ally2.crit_pct}%, Esq {ally2.esquive_pct}%")
    print(f"   - Allié 1 effets: {len(getattr(ally1, 'temporary_effects', []))}")
    print(f"   - Allié 2 effets: {len(getattr(ally2, 'temporary_effects', []))}")
    
    try:
        # Utiliser la capacité
        success, message = engine.use_ability_by_id(skyla_unit, "5754")
        
        print(f"   Résultat: {success} - {message}")
        
        print("   APRÈS utilisation:")
        print(f"   - Allié 1: Crit {ally1.crit_pct}%, Esq {ally1.esquive_pct}%")
        print(f"   - Allié 2: Crit {ally2.crit_pct}%, Esq {ally2.esquive_pct}%")
        print(f"   - Allié 1 effets: {len(getattr(ally1, 'temporary_effects', []))}")
        print(f"   - Allié 2 effets: {len(getattr(ally2, 'temporary_effects', []))}")
        
        # Afficher les effets détaillés
        for unit in [ally1, ally2]:
            effects = getattr(unit, 'temporary_effects', [])
            if effects:
                print(f"   - {unit.name} effets détaillés:")
                for effect in effects:
                    print(f"     * {effect}")
            else:
                print(f"   - {unit.name}: Aucun effet temporaire")
        
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
    debug_danse_alizes()
