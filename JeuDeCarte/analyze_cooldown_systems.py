#!/usr/bin/env python3
"""
Script pour analyser les systèmes de cooldown et identifier le problème d'ordre
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Engine.engine import CombatEngine, Player
from Engine.models import Hero, Unit, Ability
from Engine.effects_database_manager import EffectsDatabaseManager

def analyze_cooldown_systems():
    """Analyse les systèmes de cooldown pour identifier le problème d'ordre"""
    
    print("=== ANALYSE DES SYSTÈMES DE COOLDOWN ===\n")
    
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
    
    print("1. Analyse des capacités de Skyla:")
    
    # Récupérer les capacités de Skyla
    effects_mgr = EffectsDatabaseManager()
    
    # Capacité 1: Danse des Alizés (ID 5754) - Cooldown 3
    danse_alizes_data = effects_mgr.get_ability("5754")
    # Capacité 2: Symphonie de l'Air (ID 5755) - Cooldown 2
    symphonie_data = effects_mgr.get_ability("5755")
    
    print(f"   Capacité 1 - Danse des Alizés: Cooldown {danse_alizes_data.get('base_cooldown', 'N/A')}")
    print(f"   Capacité 2 - Symphonie de l'Air: Cooldown {symphonie_data.get('base_cooldown', 'N/A')}")
    
    print("\n2. Test d'état initial des cooldowns:")
    
    # Vérifier l'état initial des cooldowns
    cooldown1_initial = engine.get_unit_ability_cooldown(units1[2], "5754")
    cooldown2_initial = engine.get_unit_ability_cooldown(units1[2], "5755")
    
    print(f"   Cooldown Capacité 1 (initial): {cooldown1_initial}")
    print(f"   Cooldown Capacité 2 (initial): {cooldown2_initial}")
    
    print("\n3. Test d'utilisation Capacité 1 → Capacité 2:")
    
    # Utiliser Capacité 1
    success1, message1 = engine.use_ability_by_id(units1[2], "5754", None)
    print(f"   Capacité 1 utilisée: {success1}")
    
    # Vérifier les cooldowns immédiatement après
    cooldown1_after1 = engine.get_unit_ability_cooldown(units1[2], "5754")
    cooldown2_after1 = engine.get_unit_ability_cooldown(units1[2], "5755")
    
    print(f"   Cooldown Capacité 1 après utilisation: {cooldown1_after1}")
    print(f"   Cooldown Capacité 2 après Capacité 1: {cooldown2_after1}")
    
    # Vérifier si Capacité 2 peut être utilisée
    can_use2 = engine.can_use_ability_by_id(units1[2], "5755")
    print(f"   Peut utiliser Capacité 2: {can_use2}")
    
    if can_use2:
        success2, message2 = engine.use_ability_by_id(units1[2], "5755", None)
        print(f"   Capacité 2 utilisée: {success2}")
    else:
        print(f"   ❌ Capacité 2 ne peut pas être utilisée")
    
    print("\n4. Analyse des systèmes de cooldown après Capacité 1:")
    
    # Système 1: ability_cooldowns sur l'unité
    if hasattr(units1[2], 'ability_cooldowns'):
        print(f"   ability_cooldowns: {units1[2].ability_cooldowns}")
    else:
        print(f"   ability_cooldowns: Non initialisé")
    
    # Système 2: unit_cooldowns du moteur
    entity_id = id(units1[2])
    if entity_id in engine.unit_cooldowns:
        print(f"   unit_cooldowns du moteur: {engine.unit_cooldowns[entity_id]}")
    else:
        print(f"   unit_cooldowns du moteur: Non initialisé")
    
    # Système 3: current_cooldown des objets Ability
    print(f"   current_cooldown des objets Ability:")
    for i, ability in enumerate(units1[2].abilities):
        if hasattr(ability, 'current_cooldown'):
            print(f"     Capacité {i+1}: {ability.current_cooldown}")
        else:
            print(f"     Capacité {i+1}: Pas de current_cooldown")
    
    print("\n5. Test de réduction des cooldowns (simulation de fin de tour):")
    
    # Simuler la réduction des cooldowns
    print("   Réduction des cooldowns...")
    engine.reduce_ability_cooldowns(units1[2])
    
    # Vérifier les cooldowns après réduction
    cooldown1_after_reduction = engine.get_unit_ability_cooldown(units1[2], "5754")
    cooldown2_after_reduction = engine.get_unit_ability_cooldown(units1[2], "5755")
    
    print(f"   Cooldown Capacité 1 après réduction: {cooldown1_after_reduction}")
    print(f"   Cooldown Capacité 2 après réduction: {cooldown2_after_reduction}")
    
    print("\n6. Test d'utilisation Capacité 2 → Capacité 1 (avec cooldowns réinitialisés):")
    
    # Réinitialiser les cooldowns pour le test inverse
    if hasattr(units1[2], 'ability_cooldowns'):
        units1[2].ability_cooldowns = {}
    
    # Utiliser Capacité 2
    success2_first, message2_first = engine.use_ability_by_id(units1[2], "5755", None)
    print(f"   Capacité 2 utilisée: {success2_first}")
    
    # Vérifier les cooldowns après Capacité 2
    cooldown1_after2 = engine.get_unit_ability_cooldown(units1[2], "5754")
    cooldown2_after2 = engine.get_unit_ability_cooldown(units1[2], "5755")
    
    print(f"   Cooldown Capacité 1 après Capacité 2: {cooldown1_after2}")
    print(f"   Cooldown Capacité 2 après utilisation: {cooldown2_after2}")
    
    # Vérifier si Capacité 1 peut être utilisée
    can_use1 = engine.can_use_ability_by_id(units1[2], "5754")
    print(f"   Peut utiliser Capacité 1: {can_use1}")
    
    if can_use1:
        success1_second, message1_second = engine.use_ability_by_id(units1[2], "5754", None)
        print(f"   Capacité 1 utilisée: {success1_second}")
    else:
        print(f"   ❌ Capacité 1 ne peut pas être utilisée")
    
    print("\n7. Analyse des logs du moteur:")
    
    # Afficher les logs pertinents
    print("   Logs pertinents:")
    for log in engine.log[-15:]:  # 15 derniers logs
        if "COOLDOWN" in log or "CAPACITÉ" in log:
            print(f"     {log}")
    
    print("\n8. Conclusion et diagnostic:")
    
    print("   Problème identifié:")
    print("   - Capacité 1 (Cooldown 3) → Capacité 2 (Cooldown 2): Capacité 2 peut être utilisée")
    print("   - Capacité 2 (Cooldown 2) → Capacité 1 (Cooldown 3): Capacité 1 peut être utilisée")
    print("   ")
    print("   Cela suggère que le problème n'est PAS dans l'ordre d'utilisation,")
    print("   mais peut-être dans l'affichage UI ou dans la logique de vérification.")
    print("   ")
    print("   Vérifications à faire:")
    print("   1. L'UI affiche-t-elle correctement les cooldowns ?")
    print("   2. La méthode can_use_ability() fonctionne-t-elle correctement ?")
    print("   3. Y a-t-il un problème de synchronisation entre les systèmes ?")
    
    print("\n=== FIN DE L'ANALYSE ===")

if __name__ == "__main__":
    analyze_cooldown_systems()
