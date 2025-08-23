#!/usr/bin/env python3
"""
Script de test pour vérifier l'affichage des capacités avec cooldown visuel
"""

import sys
import os

# Ajouter le chemin du projet au sys.path
project_root = os.path.join(os.path.dirname(__file__))
sys.path.insert(0, project_root)

from Engine.models import Ability, Unit
from Engine.engine import CombatEngine

def test_ability_menu_visual():
    """Test de l'affichage des capacités avec cooldown visuel"""
    print("=== Test de l'affichage des capacités avec cooldown visuel ===")
    
    # Créer un moteur de combat
    engine = CombatEngine()
    
    # Créer une unité avec deux capacités
    unit = Unit(
        name="Test Unit",
        stats={"hp": 100, "attack": 10, "defense": 5},
        abilities=[
            Ability(name="Capacité 1", ability_id="test_1", target_type="single_enemy"),
            Ability(name="Capacité 2", ability_id="test_2", target_type="single_enemy")
        ]
    )
    
    # Simuler l'utilisation de la Capacité 1 (mise en cooldown)
    print("\n1. État initial des capacités :")
    for i, ability in enumerate(unit.abilities):
        can_use = engine.can_use_ability(unit, ability)
        cooldown = engine.get_ability_cooldown(unit, ability)
        status = "✅ Utilisable" if can_use else f"❌ Cooldown: {cooldown}"
        print(f"   - {ability.name}: {status}")
    
    # Simuler l'utilisation de la Capacité 1
    print("\n2. Utilisation de la Capacité 1...")
    # Appliquer un cooldown de 2 tours à la Capacité 1
    if hasattr(engine, '_apply_ability_cooldown'):
        engine._apply_ability_cooldown(unit, "test_1", 2)
    
    print("\n3. État après utilisation de la Capacité 1 :")
    for i, ability in enumerate(unit.abilities):
        can_use = engine.can_use_ability(unit, ability)
        cooldown = engine.get_ability_cooldown(unit, ability)
        status = "✅ Utilisable" if can_use else f"❌ Cooldown: {cooldown}"
        print(f"   - {ability.name}: {status}")
    
    # Simuler le passage d'un tour
    print("\n4. Passage d'un tour...")
    if hasattr(engine, '_reduce_player_cooldowns'):
        # Créer un joueur temporaire pour la réduction des cooldowns
        from Engine.models import Player
        player = Player("Test Player")
        player.units = [unit]
        engine._reduce_player_cooldowns(player)
    
    print("\n5. État après passage d'un tour :")
    for i, ability in enumerate(unit.abilities):
        can_use = engine.can_use_ability(unit, ability)
        cooldown = engine.get_ability_cooldown(unit, ability)
        status = "✅ Utilisable" if can_use else f"❌ Cooldown: {cooldown}"
        print(f"   - {ability.name}: {status}")
    
    print("\n=== Résultats attendus ===")
    print("✅ Les deux capacités doivent toujours être visibles dans le menu")
    print("✅ Capacité 1 doit avoir un fond semi-transparent rouge (40% d'opacité)")
    print("✅ Capacité 1 doit afficher 'CD: 1' à droite")
    print("✅ Capacité 2 doit rester normale et utilisable")
    print("✅ Le texte de Capacité 1 doit être en gris foncé")
    print("✅ Le texte de Capacité 2 doit rester en blanc")

if __name__ == "__main__":
    test_ability_menu_visual()
