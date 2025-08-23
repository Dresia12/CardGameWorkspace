#!/usr/bin/env python3
"""
Script pour diagnostiquer le problème de synchronisation des cooldowns
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Engine.engine import CombatEngine, Player
from Engine.models import Hero, Unit, Ability
from Engine.effects_database_manager import EffectsDatabaseManager

def debug_cooldown_sync_issue():
    """Diagnostique le problème de synchronisation des cooldowns"""
    
    print("=== DIAGNOSTIC PROBLÈME SYNCHRONISATION COOLDOWNS ===\n")
    
    # Créer un moteur de combat
    hero1 = Hero("Héros Test 1", "Air", {"hp": 1000, "attack": 30, "defense": 20})
    hero2 = Hero("Héros Test 2", "Feu", {"hp": 1000, "attack": 30, "defense": 20})
    
    units1 = [
        Unit("Gelidar", "Glace", {"hp": 1100, "attack": 25, "defense": 28}),
        Unit("Frimousse", "Glace", {"hp": 780, "attack": 23, "defense": 13}),
        Unit("Skyla", "Air", {"hp": 1010, "attack": 28, "defense": 21})
    ]
    
    units2 = [
        Unit("Pyrodrake", "Feu", {"hp": 1200, "attack": 35, "defense": 22}),
        Unit("Terra", "Terre", {"hp": 1400, "attack": 18, "defense": 41}),
        Unit("Bersi", "Terre", {"hp": 1160, "attack": 26, "defense": 30})
    ]
    
    player1 = Player("Joueur 1", [], hero1, units1)
    player2 = Player("Joueur 2", [], hero2, units2)
    
    engine = CombatEngine(player1, player2)
    
    # Configurer les propriétaires
    for unit in units1:
        unit.owner = player1
    for unit in units2:
        unit.owner = player2
    
    skyla = units1[2]  # Skyla
    
    print("1. État initial des cooldowns:")
    
    # Vérifier l'état initial
    cooldown1_initial = engine.get_unit_ability_cooldown(skyla, "5754")
    cooldown2_initial = engine.get_unit_ability_cooldown(skyla, "5755")
    
    print(f"   Capacité 1 (5754): {cooldown1_initial}")
    print(f"   Capacité 2 (5755): {cooldown2_initial}")
    
    print("\n2. Utilisation de la Capacité 1:")
    
    # Utiliser Capacité 1
    success1, message1 = engine.use_ability_by_id(skyla, "5754", None)
    print(f"   Résultat: {success1} - {message1}")
    
    print("\n3. Vérification immédiate après Capacité 1:")
    
    # Vérifier les cooldowns immédiatement après
    cooldown1_after1 = engine.get_unit_ability_cooldown(skyla, "5754")
    cooldown2_after1 = engine.get_unit_ability_cooldown(skyla, "5755")
    
    print(f"   Capacité 1 (5754): {cooldown1_after1}")
    print(f"   Capacité 2 (5755): {cooldown2_after1}")
    
    print("\n4. Vérification des systèmes de cooldown:")
    
    # Système 1: ability_cooldowns sur l'unité
    print("   Système 1 - ability_cooldowns sur l'unité:")
    if hasattr(skyla, 'ability_cooldowns'):
        print(f"     {skyla.ability_cooldowns}")
    else:
        print(f"     Non initialisé")
    
    # Système 2: unit_cooldowns du moteur
    print("   Système 2 - unit_cooldowns du moteur:")
    entity_id = id(skyla)
    if entity_id in engine.unit_cooldowns:
        print(f"     {engine.unit_cooldowns[entity_id]}")
    else:
        print(f"     Non initialisé")
    
    # Système 3: current_cooldown des objets Ability
    print("   Système 3 - current_cooldown des objets Ability:")
    for i, ability in enumerate(skyla.abilities):
        if hasattr(ability, 'current_cooldown'):
            print(f"     Capacité {i+1} ({getattr(ability, 'ability_id', 'N/A')}): {ability.current_cooldown}")
        else:
            print(f"     Capacité {i+1} ({getattr(ability, 'ability_id', 'N/A')}): Pas de current_cooldown")
    
    print("\n5. Test de can_use_ability_by_id:")
    
    # Tester can_use_ability_by_id pour les deux capacités
    can_use1 = engine.can_use_ability_by_id(skyla, "5754")
    can_use2 = engine.can_use_ability_by_id(skyla, "5755")
    
    print(f"   Peut utiliser Capacité 1 (5754): {can_use1}")
    print(f"   Peut utiliser Capacité 2 (5755): {can_use2}")
    
    print("\n6. Test de can_use_ability avec objets Ability:")
    
    # Tester can_use_ability avec les objets Ability
    for i, ability in enumerate(skyla.abilities):
        can_use = engine.can_use_ability(skyla, ability)
        print(f"   Peut utiliser Capacité {i+1} ({getattr(ability, 'name', 'N/A')}): {can_use}")
    
    print("\n7. Simulation de l'utilisation de Capacité 2:")
    
    if can_use2:
        success2, message2 = engine.use_ability_by_id(skyla, "5755", None)
        print(f"   Capacité 2 utilisée: {success2} - {message2}")
    else:
        print(f"   ❌ Capacité 2 ne peut pas être utilisée")
        
        # Analyser pourquoi
        print(f"   Analyse du problème:")
        print(f"     - Cooldown Capacité 2: {cooldown2_after1}")
        print(f"     - get_unit_ability_cooldown retourne: {engine.get_unit_ability_cooldown(skyla, '5755')}")
        
        # Vérifier si le problème vient de la méthode get_unit_ability_cooldown
        if hasattr(skyla, 'ability_cooldowns') and '5755' in skyla.ability_cooldowns:
            print(f"     - ability_cooldowns contient '5755': {skyla.ability_cooldowns['5755']}")
        else:
            print(f"     - ability_cooldowns ne contient PAS '5755'")
    
    print("\n8. Logs du moteur:")
    
    # Afficher les logs pertinents
    print("   Logs pertinents:")
    for log in engine.log[-10:]:
        if "COOLDOWN" in log or "CAPACITÉ" in log:
            print(f"     {log}")
    
    print("\n9. Diagnostic du problème:")
    
    print("   Problème identifié:")
    if not can_use2:
        print("   - La Capacité 2 ne peut pas être utilisée après la Capacité 1")
        print("   - Cela suggère un problème de synchronisation entre les systèmes de cooldown")
        print("   ")
        print("   Solutions possibles:")
        print("   1. Vérifier que get_unit_ability_cooldown() fonctionne correctement")
        print("   2. S'assurer que les cooldowns sont correctement appliqués")
        print("   3. Vérifier la synchronisation entre les 3 systèmes de cooldown")
        print("   4. Vérifier que can_use_ability_by_id() utilise la bonne méthode")
    
    print("\n=== FIN DU DIAGNOSTIC ===")

if __name__ == "__main__":
    debug_cooldown_sync_issue()
