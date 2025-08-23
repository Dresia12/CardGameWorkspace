#!/usr/bin/env python3
"""
Script pour analyser le problème d'ordre d'utilisation des capacités
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Engine.engine import CombatEngine, Player
from Engine.models import Hero, Unit, Ability
from Engine.effects_database_manager import EffectsDatabaseManager

def test_ability_order_issue():
    """Teste le problème d'ordre d'utilisation des capacités"""
    
    print("=== ANALYSE PROBLÈME ORDRE D'UTILISATION DES CAPACITÉS ===\n")
    
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
    
    # Récupérer les capacités de Skyla depuis effects_database.json
    effects_mgr = EffectsDatabaseManager()
    
    # Capacité 1: Danse des Alizés (ID 5754)
    danse_alizes_data = effects_mgr.get_ability("5754")
    if danse_alizes_data:
        print(f"   Capacité 1 - Danse des Alizés:")
        print(f"     - ID: 5754")
        print(f"     - Cooldown: {danse_alizes_data.get('base_cooldown', 'N/A')}")
        print(f"     - Target Type: {danse_alizes_data.get('target_type', 'N/A')}")
        print(f"     - Crit Boost: {danse_alizes_data.get('crit_boost', 'N/A')}")
        print(f"     - Crit Duration: {danse_alizes_data.get('crit_duration', 'N/A')}")
    
    # Capacité 2: Symphonie de l'Air (ID 5755)
    symphonie_data = effects_mgr.get_ability("5755")
    if symphonie_data:
        print(f"   Capacité 2 - Symphonie de l'Air:")
        print(f"     - ID: 5755")
        print(f"     - Cooldown: {symphonie_data.get('base_cooldown', 'N/A')}")
        print(f"     - Target Type: {symphonie_data.get('target_type', 'N/A')}")
        print(f"     - Crit Boost: {symphonie_data.get('crit_boost', 'N/A')}")
        print(f"     - Crit Duration: {symphonie_data.get('crit_duration', 'N/A')}")
    
    print("\n2. Test d'utilisation Capacité 1 puis Capacité 2:")
    
    # Créer les objets Ability
    danse_alizes = Ability(
        name="Danse des Alizés",
        description="Une danse majestueuse et aussi gracieuse que le vent",
        cooldown=3,
        target_type="all_allies",
        ability_id="5754"
    )
    
    symphonie = Ability(
        name="Symphonie de l'Air",
        description="Une mélodie harmonieuse qui inspire les alliés",
        cooldown=2,
        target_type="all_allies",
        ability_id="5755"
    )
    
    # Test 1: Utiliser Capacité 1 puis Capacité 2
    print("   Test 1: Capacité 1 → Capacité 2")
    
    # Utiliser Capacité 1
    success1, message1 = engine.use_ability_by_id(units1[2], "5754", None)
    print(f"     Capacité 1 utilisée: {success1} - {message1}")
    
    # Vérifier les cooldowns après Capacité 1
    cooldown1_after = engine.get_unit_ability_cooldown(units1[2], "5754")
    cooldown2_after = engine.get_unit_ability_cooldown(units1[2], "5755")
    print(f"     Cooldown Capacité 1 après utilisation: {cooldown1_after}")
    print(f"     Cooldown Capacité 2 après Capacité 1: {cooldown2_after}")
    
    # Vérifier si Capacité 2 peut être utilisée
    can_use2 = engine.can_use_ability_by_id(units1[2], "5755")
    print(f"     Peut utiliser Capacité 2 après Capacité 1: {can_use2}")
    
    # Utiliser Capacité 2
    if can_use2:
        success2, message2 = engine.use_ability_by_id(units1[2], "5755", None)
        print(f"     Capacité 2 utilisée: {success2} - {message2}")
    else:
        print(f"     ❌ Capacité 2 ne peut pas être utilisée")
    
    print("\n3. Test d'utilisation Capacité 2 puis Capacité 1:")
    
    # Réinitialiser les cooldowns pour le test
    if hasattr(units1[2], 'ability_cooldowns'):
        units1[2].ability_cooldowns = {}
    
    # Test 2: Utiliser Capacité 2 puis Capacité 1
    print("   Test 2: Capacité 2 → Capacité 1")
    
    # Utiliser Capacité 2
    success2_first, message2_first = engine.use_ability_by_id(units1[2], "5755", None)
    print(f"     Capacité 2 utilisée: {success2_first} - {message2_first}")
    
    # Vérifier les cooldowns après Capacité 2
    cooldown1_after2 = engine.get_unit_ability_cooldown(units1[2], "5754")
    cooldown2_after2 = engine.get_unit_ability_cooldown(units1[2], "5755")
    print(f"     Cooldown Capacité 1 après Capacité 2: {cooldown1_after2}")
    print(f"     Cooldown Capacité 2 après utilisation: {cooldown2_after2}")
    
    # Vérifier si Capacité 1 peut être utilisée
    can_use1 = engine.can_use_ability_by_id(units1[2], "5754")
    print(f"     Peut utiliser Capacité 1 après Capacité 2: {can_use1}")
    
    # Utiliser Capacité 1
    if can_use1:
        success1_second, message1_second = engine.use_ability_by_id(units1[2], "5754", None)
        print(f"     Capacité 1 utilisée: {success1_second} - {message1_second}")
    else:
        print(f"     ❌ Capacité 1 ne peut pas être utilisée")
    
    print("\n4. Analyse des logs du moteur:")
    
    # Afficher les logs pertinents
    print("   Logs du moteur:")
    for log in engine.log[-20:]:  # 20 derniers logs
        if "COOLDOWN" in log or "CAPACITÉ" in log or "EFFET" in log:
            print(f"     {log}")
    
    print("\n5. Vérification des systèmes de cooldown:")
    
    # Vérifier les différents systèmes de cooldown
    print("   Systèmes de cooldown:")
    
    # Système 1: ability_cooldowns sur l'unité
    if hasattr(units1[2], 'ability_cooldowns'):
        print(f"     ability_cooldowns: {units1[2].ability_cooldowns}")
    else:
        print(f"     ability_cooldowns: Non initialisé")
    
    # Système 2: unit_cooldowns du moteur
    entity_id = id(units1[2])
    if entity_id in engine.unit_cooldowns:
        print(f"     unit_cooldowns du moteur: {engine.unit_cooldowns[entity_id]}")
    else:
        print(f"     unit_cooldowns du moteur: Non initialisé")
    
    # Système 3: current_cooldown des objets Ability
    print(f"     current_cooldown des objets Ability:")
    for i, ability in enumerate(units1[2].abilities):
        if hasattr(ability, 'current_cooldown'):
            print(f"       Capacité {i+1}: {ability.current_cooldown}")
        else:
            print(f"       Capacité {i+1}: Pas de current_cooldown")
    
    print("\n=== FIN DE L'ANALYSE ===")

if __name__ == "__main__":
    test_ability_order_issue()
