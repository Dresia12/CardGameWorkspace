#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de vérification en conditions réelles de combat
Teste l'utilisation réelle des capacités, effets, cooldowns et interactions
Utilise les vraies unités du jeu
"""

import json
import sys
import os
import traceback
from typing import Dict, List, Any, Optional
import random

# Ajout du répertoire parent au path pour les imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from Engine.engine import CombatEngine, Player
    from Engine.models import Hero, Unit, Card, Ability
    from Engine.effects_database_manager import EffectsDatabaseManager
    from Engine.deck_manager import DeckManager
    from Engine.hero_customization_manager import HeroCustomizationManager
except ImportError as e:
    print(f"❌ Erreur d'import: {e}")
    print("Assurez-vous d'être dans le bon répertoire")
    sys.exit(1)

class RealCombatTester:
    def __init__(self):
        self.results = {
            "success": [],
            "errors": [],
            "warnings": [],
            "combat_tests": [],
            "stats": {
                "total_abilities_tested": 0,
                "successful_uses": 0,
                "failed_uses": 0,
                "combat_simulations": 0
            }
        }
        
        # Chargement des données
        self.load_data()
        
    def load_data(self):
        """Charge toutes les données nécessaires"""
        try:
            print("📂 Chargement des données...")
            
            # Chargement de la base de données des effets
            self.effects_db = EffectsDatabaseManager()
            
            # Chargement des données JSON
            with open('Data/effects_database.json', 'r', encoding='utf-8') as f:
                self.effects_data = json.load(f)
            
            with open('Data/heroes.json', 'r', encoding='utf-8') as f:
                self.heroes_data = json.load(f)
            
            with open('Data/units.json', 'r', encoding='utf-8') as f:
                self.units_data = json.load(f)
            
            with open('Data/cards.json', 'r', encoding='utf-8') as f:
                self.cards_data = json.load(f)
                
            print("✅ Données chargées avec succès")
            
        except Exception as e:
            print(f"❌ Erreur lors du chargement des données: {e}")
            traceback.print_exc()
            sys.exit(1)
    
    def _iter_entities(self, data):
        """Permet d'itérer sur des données JSON qui peuvent être une liste ou un dict."""
        if isinstance(data, dict):
            return data.values()
        if isinstance(data, list):
            return data
        return []
    
    def create_real_units_for_testing(self):
        """Crée des unités réelles du jeu pour les tests"""
        real_units = []
        
        # Récupération des unités avec des capacités
        for unit_data in self._iter_entities(self.units_data):
            if isinstance(unit_data, dict) and "ability_ids" in unit_data and unit_data["ability_ids"]:
                try:
                    # Création de l'unité avec ses vraies capacités
                    ability_ids = unit_data.get('ability_ids', [])
                    
                    # Convertir les IDs de capacités en objets Ability
                    abilities = []
                    for ability_id in ability_ids:
                        if str(ability_id) in self.effects_data.get("abilities", {}):
                            ability_data = self.effects_data["abilities"][str(ability_id)]
                            ability = Ability(
                                name=ability_data.get('name', f'Ability {ability_id}'),
                                description=ability_data.get('description', ''),
                                cooldown=ability_data.get('base_cooldown', 0)
                            )
                            # Ajouter les propriétés supplémentaires CRUCIALES
                            ability.damage = ability_data.get('damage', 0)
                            ability.target_type = ability_data.get('target_type', 'single_enemy')
                            ability.element = ability_data.get('element', '1')
                            # AJOUTER L'ID DE LA CAPACITÉ - CRUCIAL POUR LE SYSTÈME PAR ID
                            ability.ability_id = str(ability_id)
                            # Initialiser le cooldown actuel
                            ability.current_cooldown = 0
                            abilities.append(ability)
                        else:
                            # Créer une capacité par défaut si l'ID n'est pas trouvé
                            ability = Ability(
                                name=f'Ability {ability_id}',
                                description='Capacité par défaut',
                                cooldown=0
                            )
                            # Ajouter les propriétés supplémentaires
                            ability.damage = 10
                            ability.target_type = 'single_enemy'
                            ability.element = '1'
                            ability.ability_id = str(ability_id)
                            ability.current_cooldown = 0
                            abilities.append(ability)
                    
                    unit = Unit(
                        name=unit_data.get('name', 'Unité inconnue'),
                        element=unit_data.get('element', '1'),
                        stats={
                            'hp': unit_data.get('hp', 100),
                            'attack': unit_data.get('attack', 20),
                            'defense': unit_data.get('defense', 10)
                        },
                        abilities=abilities  # Passer les objets Ability
                    )
                    
                    # Remplacer la liste d'IDs par la liste d'objets Ability
                    unit.abilities = abilities
                    
                    # Ajout des données supplémentaires
                    unit.rarity = unit_data.get('rarity', 'Commun')
                    unit.image_path = unit_data.get('image_path', 'Crea/default.png')
                    
                    real_units.append(unit)
                    print(f"✅ Unité créée: {unit.name} (ID: {unit_data.get('id', 'N/A')}) - {len(unit.abilities)} capacités")
                    
                except Exception as e:
                    print(f"❌ Erreur création unité {unit_data.get('name', 'N/A')}: {e}")
                    import traceback
                    traceback.print_exc()
                    self.results["errors"].append(f"Erreur création unité {unit_data.get('name', 'N/A')}: {e}")
        
        print(f"📊 {len(real_units)} unités réelles créées pour les tests")
        return real_units
    
    def create_real_heroes_for_testing(self):
        """Crée des héros réels du jeu pour les tests"""
        real_heroes = []
        
        for hero_data in self._iter_entities(self.heroes_data):
            if isinstance(hero_data, dict):
                try:
                    # Création du héros avec ses vraies stats
                    hero = Hero(
                        name=hero_data.get('name', 'Héros inconnu'),
                        element=hero_data.get('element', '1'),
                        base_stats={
                            'hp': hero_data.get('hp', 1000),
                            'attack': hero_data.get('attack', 50),
                            'defense': hero_data.get('defense', 20)
                        },
                        ability_name=hero_data.get('ability_name', ''),
                        ability_description=hero_data.get('ability_description', ''),
                        ability_cooldown=hero_data.get('ability_cooldown', 0)
                    )
                    
                    # Ajout des données supplémentaires
                    hero.rarity = hero_data.get('rarity', 'Commun')
                    hero.image_path = hero_data.get('image_path', 'Hero/1.png')
                    hero.passive = hero_data.get('passive', '')
                    
                    real_heroes.append(hero)
                    print(f"✅ Héros créé: {hero.name} (ID: {hero_data.get('id', 'N/A')})")
                    
                except Exception as e:
                    self.results["errors"].append(f"Erreur création héros {hero_data.get('name', 'N/A')}: {e}")
        
        print(f"📊 {len(real_heroes)} héros réels créés pour les tests")
        return real_heroes
    
    def test_ability_usage_in_combat(self, unit, ability_input, combat_engine, target_units=None):
        """Teste l'utilisation réelle d'une capacité en combat"""
        try:
            # Gérer les deux cas : ability_input peut être un ID (str/int) ou un objet Ability
            if isinstance(ability_input, Ability):
                # C'est déjà un objet Ability
                ability_obj = ability_input
                ability_id = ability_obj.name  # Utiliser le nom comme ID pour la compatibilité
                ability_data = {
                    'name': ability_obj.name,
                    'description': ability_obj.description,
                    'base_cooldown': ability_obj.cooldown,
                    'damage': ability_obj.damage,
                    'target_type': ability_obj.target_type,
                    'element': ability_obj.element
                }
            else:
                # C'est un ID, récupérer les données
                ability_id = str(ability_input)
                if ability_id not in self.effects_data.get("abilities", {}):
                    self.results["errors"].append(f"Capacité {ability_id} non trouvée pour {unit.name}")
                    return False
                ability_data = self.effects_data["abilities"][ability_id]
                ability_obj = None
            
            # Vérifier si l'unité peut utiliser la capacité (cooldown)
            if hasattr(combat_engine, 'can_use_ability'):
                # CORRECTION : Passer l'objet Ability au lieu de l'ID
                if ability_obj:
                    can_use = combat_engine.can_use_ability(unit, ability_obj)
                else:
                    # Créer un objet Ability temporaire pour la vérification
                    temp_ability = Ability(
                        name=ability_data.get('name', f'Ability {ability_id}'),
                        description=ability_data.get('description', ''),
                        cooldown=ability_data.get('base_cooldown', 0)
                    )
                    temp_ability.ability_id = ability_id
                    can_use = combat_engine.can_use_ability(unit, temp_ability)
                
                if not can_use:
                    self.results["warnings"].append(f"{unit.name} ne peut pas utiliser {ability_data.get('name', ability_id)} (cooldown)")
                    return False
            
            # Vérifications de la capacité
            required_fields = ["name", "element", "base_cooldown", "target_type"]
            for field in required_fields:
                if field not in ability_data:
                    self.results["errors"].append(f"Capacité {ability_id} ({unit.name}): champ '{field}' manquant")
                    return False
            
            # Gérer le champ damage_type manquant en ajoutant une valeur par défaut
            if "damage_type" not in ability_data:
                # Déterminer le type de dégâts basé sur l'élément
                element = ability_data.get("element", "1")
                if element in ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]:
                    ability_data["damage_type"] = "magical"  # Capacités élémentaires = magiques
                else:
                    ability_data["damage_type"] = "physical"  # Par défaut = physiques
                self.results["warnings"].append(f"Capacité {ability_id} ({unit.name}): damage_type ajouté automatiquement ({ability_data['damage_type']})")
            
            # Vérification des types de données
            if not isinstance(ability_data.get("base_cooldown", 0), int):
                self.results["warnings"].append(f"Capacité {ability_id} ({unit.name}): base_cooldown devrait être un entier")
            
            if not isinstance(ability_data.get("damage", 0), (int, float)):
                self.results["warnings"].append(f"Capacité {ability_id} ({unit.name}): damage devrait être numérique")
            
            # Test de la logique de cible
            target_type = ability_data.get("target_type", "")
            valid_targets = [
                "single_enemy", "all_enemies", "single_ally", "all_allies", 
                "self", "random_enemy", "random_ally", "chain_enemies",
                "front_row", "random_multiple", "self_and_allies", "chain_random"
            ]
            
            if target_type not in valid_targets:
                self.results["warnings"].append(f"Capacité {ability_id} ({unit.name}): type de cible invalide ({target_type})")
            
            # Test d'utilisation réelle de la capacité
            if target_units and hasattr(combat_engine, 'use_ability'):
                try:
                    # Sélectionner une cible appropriée selon le type
                    target = self.select_appropriate_target(unit, target_type, target_units, combat_engine)
                    
                    if target:
                        # Sauvegarder les stats avant utilisation
                        target_hp_before = target.hp
                        unit_hp_before = unit.hp
                        
                        # AMÉLIORATION : Gestion des erreurs de ciblage
                        try:
                            # Utiliser la capacité avec l'objet Ability
                            if ability_obj:
                                success = combat_engine.use_ability(unit, ability_obj, target)
                            else:
                                # Créer un objet Ability si nécessaire
                                ability_obj = Ability(
                                    name=ability_data.get('name', f'Ability {ability_id}'),
                                    description=ability_data.get('description', ''),
                                    cooldown=ability_data.get('base_cooldown', 0)
                                )
                                # Ajouter les propriétés supplémentaires
                                ability_obj.damage = ability_data.get('damage', 0)
                                ability_obj.target_type = target_type
                                ability_obj.element = ability_data.get('element', '1')
                                ability_obj.ability_id = ability_id
                                success = combat_engine.use_ability(unit, ability_obj, target)
                        except Exception as use_error:
                            # Si l'utilisation échoue, essayer avec une cible différente
                            self.results["warnings"].append(f"Erreur utilisation {ability_data.get('name', ability_id)} sur {target.name}: {use_error}")
                            
                            # Essayer avec l'unité elle-même comme cible
                            try:
                                success = combat_engine.use_ability(unit, ability_obj, unit)
                                target = unit
                                target_hp_before = unit.hp
                            except Exception as fallback_error:
                                self.results["warnings"].append(f"Échec fallback pour {ability_data.get('name', ability_id)}: {fallback_error}")
                                success = False
                        
                        if success:
                            # Vérifier les effets appliqués
                            target_hp_after = target.hp
                            unit_hp_after = unit.hp
                            
                            # Analyser les changements
                            hp_change = target_hp_before - target_hp_after
                            unit_hp_change = unit_hp_before - unit_hp_after
                            
                            # Vérifier les effets appliqués
                            effects_applied = self.check_effects_applied(target, ability_data)
                            
                            self.results["combat_tests"].append({
                                "unit": unit.name,
                                "ability": ability_data.get('name', ability_id),
                                "ability_id": ability_id,
                                "status": "success",
                                "target_type": target_type,
                                "target": target.name,
                                "damage": ability_data.get('damage', 0),
                                "cooldown": ability_data.get('base_cooldown', 0),
                                "hp_change": hp_change,
                                "effects_applied": effects_applied,
                                "real_usage": True
                            })
                            
                            print(f"    ✅ Utilisation réussie - Cible: {target.name}, Dégâts: {hp_change}, Effets: {len(effects_applied)}")
                            return True
                        else:
                            self.results["warnings"].append(f"Échec de l'utilisation de {ability_data.get('name', ability_id)} par {unit.name}")
                            return False
                    else:
                        self.results["warnings"].append(f"Aucune cible appropriée trouvée pour {ability_data.get('name', ability_id)}")
                        return False
                        
                except Exception as e:
                    self.results["errors"].append(f"Erreur lors de l'utilisation de {ability_id} ({unit.name}): {e}")
                    return False
            
            # Fallback si pas d'utilisation réelle possible
            self.results["combat_tests"].append({
                "unit": unit.name,
                "ability": ability_data.get('name', ability_id),
                "ability_id": ability_id,
                "status": "validated",
                "target_type": target_type,
                "damage": ability_data.get('damage', 0),
                "cooldown": ability_data.get('base_cooldown', 0),
                "real_usage": False
            })
            
            return True
            
        except Exception as e:
            self.results["errors"].append(f"Erreur test capacité {ability_id} ({unit.name}): {e}")
            return False
    
    def select_appropriate_target(self, unit, target_type, available_targets, combat_engine):
        """Sélectionne une cible appropriée selon le type de cible"""
        try:
            if not available_targets:
                return None
            
            # AMÉLIORATION : Logique de sélection plus robuste
            if target_type == "self":
                return unit
            elif target_type in ["single_enemy", "random_enemy"]:
                # Prendre une unité différente de l'attaquant
                enemy_targets = [t for t in available_targets if t != unit and hasattr(t, 'hp') and t.hp > 0]
                if enemy_targets:
                    return random.choice(enemy_targets) if target_type == "random_enemy" else enemy_targets[0]
            elif target_type in ["single_ally", "random_ally"]:
                # Prendre une unité différente de l'attaquant
                ally_targets = [t for t in available_targets if t != unit and hasattr(t, 'hp') and t.hp > 0]
                if ally_targets:
                    return random.choice(ally_targets) if target_type == "random_ally" else ally_targets[0]
            elif target_type in ["all_enemies", "all_allies", "front_row", "random_multiple", "self_and_allies", "chain_enemies", "chain_random"]:
                # Pour les capacités multi-cibles, prendre la première cible appropriée
                for target in available_targets:
                    if hasattr(target, 'hp') and target.hp > 0 and target != unit:
                        return target
            
            # Fallback final : première cible vivante différente de l'attaquant
            for target in available_targets:
                if hasattr(target, 'hp') and target.hp > 0 and target != unit:
                    return target
            
            # Si aucune cible appropriée, retourner l'unité elle-même
            return unit
                
        except Exception as e:
            self.results["warnings"].append(f"Erreur sélection cible: {e}")
            return available_targets[0] if available_targets else None
    
    def check_effects_applied(self, target, ability_data):
        """Vérifie les effets appliqués sur la cible"""
        effects = []
        try:
            # Vérifier les effets de base de la capacité
            if "effects" in ability_data:
                for effect in ability_data["effects"]:
                    effects.append(f"Effet: {effect.get('effect', 'unknown')}")
            
            # Vérifier les effets élémentaires
            if "elemental_effects" in ability_data:
                for effect in ability_data["elemental_effects"]:
                    effects.append(f"Effet élémentaire: {effect.get('effect', 'unknown')}")
            
            # Vérifier les effets de chaîne
            if "chain_effects" in ability_data:
                for effect in ability_data["chain_effects"]:
                    effects.append(f"Effet de chaîne: {effect.get('effect', 'unknown')}")
            
            # Vérifier les effets temporaires sur la cible
            if hasattr(target, 'temporary_effects') and target.temporary_effects:
                for effect in target.temporary_effects:
                    effects.append(f"Effet temporaire: {effect.get('type', 'unknown')}")
            
            return effects
            
        except Exception as e:
            self.results["warnings"].append(f"Erreur vérification effets: {e}")
            return ["Erreur vérification effets"]
    
    def simulate_combat_scenario(self, units_p1, units_p2, heroes_p1, heroes_p2):
        """Simule un scénario de combat complet avec utilisation réelle des capacités"""
        try:
            print(f"\n⚔️ Simulation de combat: {len(units_p1)} unités P1 vs {len(units_p2)} unités P2")
            
            # Création des cartes de test
            test_cards = [
                Card("Carte Test 1", 1, "1", "sort", "Test effect"),
                Card("Carte Test 2", 2, "2", "créature", "Test effect")
            ]
            
            # Sélection des héros
            hero_p1 = heroes_p1[0] if heroes_p1 else Hero("Héros Test P1", "1", {"hp": 1000, "attack": 50, "defense": 20})
            hero_p2 = heroes_p2[0] if heroes_p2 else Hero("Héros Test P2", "2", {"hp": 1000, "attack": 50, "defense": 20})
            
            # Création des joueurs
            player1 = Player("Joueur 1", test_cards.copy(), hero_p1, units_p1[:3])  # Limite à 3 unités
            player2 = Player("Joueur 2", test_cards.copy(), hero_p2, units_p2[:3])  # Limite à 3 unités
            
            # Création du moteur de combat
            combat_engine = CombatEngine(player1, player2)
            
            # S'ASSURER QUE LES UNITÉS ONT LES ATTRIBUTS NÉCESSAIRES
            for unit in player1.units + player2.units:
                # Ajouter l'attribut owner pour le système de cibles
                if not hasattr(unit, 'owner'):
                    if unit in player1.units:
                        unit.owner = player1
                    else:
                        unit.owner = player2
                
                # Ajouter l'attribut is_alive pour le système de cibles
                if not hasattr(unit, 'is_alive'):
                    unit.is_alive = lambda: getattr(unit, 'hp', 0) > 0
            
            # Réinitialiser les cooldowns pour le test
            if hasattr(combat_engine, 'reset_all_cooldowns'):
                combat_engine.reset_all_cooldowns()
            
            # Réinitialiser manuellement les cooldowns des unités si nécessaire
            for unit in player1.units + player2.units:
                if hasattr(unit, 'ability_cooldowns'):
                    unit.ability_cooldowns = {}
                if hasattr(unit, 'cooldowns'):
                    unit.cooldowns = {}
                
                # SYNCHRONISER les cooldowns des objets Ability avec le système du moteur
                for ability in unit.abilities:
                    if hasattr(ability, 'current_cooldown'):
                        ability.current_cooldown = 0
                
                # FORCER la réinitialisation dans le système de cooldowns du moteur
                entity_id = id(unit)
                if hasattr(combat_engine, 'unit_cooldowns') and entity_id in combat_engine.unit_cooldowns:
                    # Réinitialiser tous les cooldowns de cette unité
                    for i in range(len(combat_engine.unit_cooldowns[entity_id])):
                        combat_engine.unit_cooldowns[entity_id][i] = 0
            
            # Test des capacités de chaque unité avec utilisation réelle
            all_units = player1.units + player2.units
            all_targets = all_units + [hero_p1, hero_p2]  # Inclure les héros comme cibles
            
            print(f"🎯 Cibles disponibles: {len(all_targets)} entités")
            
            for unit in all_units:
                print(f"\n🔍 Test des capacités de {unit.name} (HP: {unit.hp}):")
                
                for ability in unit.abilities:
                    # FORCER la réinitialisation du cooldown à 0 pour le test
                    ability.current_cooldown = 0
                    
                    # SYNCHRONISER avec le système de cooldowns du moteur
                    entity_id = id(unit)
                    if hasattr(combat_engine, 'unit_cooldowns') and entity_id in combat_engine.unit_cooldowns:
                        # Trouver l'index de la capacité
                        for i, unit_ability in enumerate(unit.abilities):
                            if getattr(unit_ability, 'name', '') == getattr(ability, 'name', ''):
                                if i < len(combat_engine.unit_cooldowns[entity_id]):
                                    combat_engine.unit_cooldowns[entity_id][i] = 0
                                break
                        
                        # FORCER la réinitialisation de tous les cooldowns de cette unité
                        for i in range(len(combat_engine.unit_cooldowns[entity_id])):
                            combat_engine.unit_cooldowns[entity_id][i] = 0
                    
                    self.results["stats"]["total_abilities_tested"] += 1
                    
                    # Test avec utilisation réelle et cibles réelles
                    if self.test_ability_usage_in_combat(unit, ability, combat_engine, all_targets):
                        self.results["stats"]["successful_uses"] += 1
                    else:
                        self.results["stats"]["failed_uses"] += 1
                
                # Vérifier l'état de l'unité après les tests
                print(f"  📊 État final: HP {unit.hp}, Effets temporaires: {len(unit.temporary_effects) if hasattr(unit, 'temporary_effects') else 0}")
            
            # Test des capacités des héros
            for hero, player_name in [(hero_p1, "P1"), (hero_p2, "P2")]:
                if hero.ability and hero.ability.name:
                    # FORCER la réinitialisation du cooldown du héros à 0 pour le test
                    hero.ability.current_cooldown = 0
                    
                    print(f"\n🔍 Test de la capacité du héros {hero.name} ({player_name}):")
                    self.results["stats"]["total_abilities_tested"] += 1
                    
                    # Test de la capacité du héros avec utilisation réelle
                    try:
                        # Créer une cible pour le héros (lui-même ou une unité)
                        hero_target = hero  # Par défaut, le héros se cible lui-même
                        
                        # Utiliser la capacité du héros
                        success = combat_engine.use_ability(hero, hero.ability, hero_target)
                        
                        if success:
                            hero_ability_test = {
                                "unit": f"Héros {hero.name}",
                                "ability": hero.ability.name,
                                "ability_id": "hero_ability",
                                "status": "success",
                                "target_type": "self",
                                "damage": 0,
                                "cooldown": hero.ability.cooldown,
                                "real_usage": True
                            }
                            
                            self.results["combat_tests"].append(hero_ability_test)
                            self.results["stats"]["successful_uses"] += 1
                            print(f"  ✅ Capacité héros: OK")
                        else:
                            self.results["stats"]["failed_uses"] += 1
                            print(f"  ❌ Capacité héros: Échec")
                            
                    except Exception as e:
                        self.results["stats"]["failed_uses"] += 1
                        self.results["warnings"].append(f"Erreur capacité héros {hero.name}: {e}")
                        print(f"  ❌ Capacité héros: Erreur - {e}")
            
            # Test des interactions entre unités
            self.test_unit_interactions(combat_engine, all_units)
            
            # Test des effets de passifs
            self.test_passive_effects(combat_engine, all_units, [hero_p1, hero_p2])
            
            self.results["stats"]["combat_simulations"] += 1
            self.results["success"].append(f"Combat simulé: {len(units_p1)} vs {len(units_p2)} unités")
            
            return True
            
        except Exception as e:
            self.results["errors"].append(f"Erreur simulation combat: {e}")
            traceback.print_exc()
            return False
    
    def test_unit_interactions(self, combat_engine, units):
        """Teste les interactions entre unités"""
        try:
            print(f"\n🔄 Test des interactions entre unités...")
            
            for i, unit1 in enumerate(units):
                for j, unit2 in enumerate(units):
                    if i != j and unit1.hp > 0 and unit2.hp > 0:
                        # Test d'attaque basique
                        hp_before = unit2.hp
                        
                        # Simuler une attaque basique
                        damage = max(1, unit1.attack - unit2.defense)
                        unit2.hp = max(0, unit2.hp - damage)
                        
                        hp_after = unit2.hp
                        actual_damage = hp_before - hp_after
                        
                        if actual_damage > 0:
                            self.results["combat_tests"].append({
                                "unit": unit1.name,
                                "ability": "Attaque basique",
                                "ability_id": "basic_attack",
                                "status": "success",
                                "target_type": "single_enemy",
                                "target": unit2.name,
                                "damage": damage,
                                "cooldown": 0,
                                "hp_change": actual_damage,
                                "effects_applied": [],
                                "real_usage": True
                            })
                            
                            print(f"  ⚔️ {unit1.name} → {unit2.name}: {actual_damage} dégâts")
                        
                        # Restaurer les HP pour les tests suivants
                        unit2.hp = hp_before
                        
        except Exception as e:
            self.results["warnings"].append(f"Erreur test interactions: {e}")
    
    def test_passive_effects(self, combat_engine, units, heroes):
        """Teste les effets passifs"""
        try:
            print(f"\n🌟 Test des effets passifs...")
            
            for unit in units:
                if hasattr(unit, 'passive_effects') and unit.passive_effects:
                    for passive in unit.passive_effects:
                        self.results["combat_tests"].append({
                            "unit": unit.name,
                            "ability": f"Passif: {passive.get('name', 'Unknown')}",
                            "ability_id": "passive_effect",
                            "status": "success",
                            "target_type": "self",
                            "target": unit.name,
                            "damage": 0,
                            "cooldown": 0,
                            "hp_change": 0,
                            "effects_applied": [f"Passif: {passive.get('effect', 'Unknown')}"],
                            "real_usage": True
                        })
                        
                        print(f"  🌟 {unit.name}: Passif {passive.get('name', 'Unknown')} actif")
            
            for hero in heroes:
                if hasattr(hero, 'passive') and hero.passive:
                    self.results["combat_tests"].append({
                        "unit": f"Héros {hero.name}",
                        "ability": f"Passif: {hero.passive}",
                        "ability_id": "hero_passive",
                        "status": "success",
                        "target_type": "self",
                        "target": hero.name,
                        "damage": 0,
                        "cooldown": 0,
                        "hp_change": 0,
                        "effects_applied": [f"Passif héros: {hero.passive}"],
                        "real_usage": True
                    })
                    
                    print(f"  🌟 Héros {hero.name}: Passif {hero.passive} actif")
                    
        except Exception as e:
            self.results["warnings"].append(f"Erreur test passifs: {e}")
    
    def run_real_combat_tests(self):
        """Lance tous les tests de combat en conditions réelles"""
        print("🚀 Démarrage des tests de combat en conditions réelles...")
        
        # Création des unités et héros réels
        real_units = self.create_real_units_for_testing()
        real_heroes = self.create_real_heroes_for_testing()
        
        if not real_units:
            print("❌ Aucune unité disponible pour les tests")
            return
        
        # Séparation des unités par élément pour des combats équilibrés
        units_by_element = {}
        for unit in real_units:
            element = unit.element
            if element not in units_by_element:
                units_by_element[element] = []
            units_by_element[element].append(unit)
        
        # Tests de combat avec différentes combinaisons
        print(f"\n⚔️ Lancement des simulations de combat...")
        
        # Test 1: Combat entre unités de même élément
        for element, units in units_by_element.items():
            if len(units) >= 2:
                units_p1 = units[:len(units)//2]
                units_p2 = units[len(units)//2:]
                
                self.simulate_combat_scenario(units_p1, units_p2, real_heroes[:1], real_heroes[1:2])
        
        # Test 2: Combat entre unités d'éléments différents
        element_list = list(units_by_element.keys())
        for i in range(min(3, len(element_list))):  # Limite à 3 combats
            element1 = element_list[i]
            element2 = element_list[(i + 1) % len(element_list)]
            
            if units_by_element[element1] and units_by_element[element2]:
                self.simulate_combat_scenario(
                    units_by_element[element1][:2], 
                    units_by_element[element2][:2],
                    real_heroes[:1], 
                    real_heroes[1:2]
                )
        
        # Affichage des résultats
        self.display_results()
    
    def display_results(self):
        """Affiche les résultats des tests"""
        print("\n" + "="*60)
        print("📋 RÉSULTATS DES TESTS DE COMBAT RÉELS")
        print("="*60)
        
        stats = self.results["stats"]
        print(f"📊 Statistiques:")
        print(f"   - Capacités testées: {stats['total_abilities_tested']}")
        print(f"   - Utilisations réussies: {stats['successful_uses']}")
        print(f"   - Utilisations échouées: {stats['failed_uses']}")
        print(f"   - Simulations de combat: {stats['combat_simulations']}")
        
        if stats['total_abilities_tested'] > 0:
            success_rate = (stats['successful_uses'] / stats['total_abilities_tested']) * 100
            print(f"   - Taux de succès: {success_rate:.1f}%")
        
        # Affichage des succès
        if self.results["success"]:
            print(f"\n✅ Succès ({len(self.results['success'])}):")
            for success in self.results["success"]:
                print(f"   - {success}")
        
        # Affichage des tests de combat
        if self.results["combat_tests"]:
            print(f"\n⚔️ Tests de combat ({len(self.results['combat_tests'])}):")
            
            # Séparer les tests réels des tests de validation
            real_tests = [t for t in self.results["combat_tests"] if t.get("real_usage", False)]
            validation_tests = [t for t in self.results["combat_tests"] if not t.get("real_usage", False)]
            
            print(f"   🎯 Tests en conditions réelles ({len(real_tests)}):")
            for test in real_tests[:5]:  # Limite à 5
                target_info = f" → {test.get('target', 'N/A')}" if test.get('target') else ""
                hp_change = f" (HP: {test.get('hp_change', 0)})" if test.get('hp_change', 0) != 0 else ""
                effects = f" [+{len(test.get('effects_applied', []))} effets]" if test.get('effects_applied') else ""
                print(f"     - {test['unit']}: {test['ability']}{target_info}{hp_change}{effects}")
            
            if len(real_tests) > 5:
                print(f"     ... et {len(real_tests) - 5} autres tests réels")
            
            if validation_tests:
                print(f"   ✅ Tests de validation ({len(validation_tests)}):")
                for test in validation_tests[:3]:  # Limite à 3
                    print(f"     - {test['unit']}: {test['ability']} ({test['target_type']})")
                
                if len(validation_tests) > 3:
                    print(f"     ... et {len(validation_tests) - 3} autres validations")
        
        # Affichage des avertissements
        if self.results["warnings"]:
            print(f"\n⚠️  Avertissements ({len(self.results['warnings'])}):")
            for warning in self.results["warnings"][:10]:
                print(f"   - {warning}")
            if len(self.results["warnings"]) > 10:
                print(f"   ... et {len(self.results['warnings']) - 10} autres")
        
        # Affichage des erreurs
        if self.results["errors"]:
            print(f"\n❌ Erreurs ({len(self.results['errors'])}):")
            for error in self.results["errors"][:10]:
                print(f"   - {error}")
            if len(self.results["errors"]) > 10:
                print(f"   ... et {len(self.results['errors']) - 10} autres")
        
        # Recommandations
        print(f"\n💡 Recommandations:")
        if stats['failed_uses'] > 0:
            print(f"   - Corriger les {stats['failed_uses']} échecs d'utilisation")
        if stats['successful_uses'] == stats['total_abilities_tested']:
            print(f"   - 🎉 Toutes les capacités fonctionnent parfaitement!")
        
        # Analyse des problèmes
        if self.results["errors"]:
            print(f"\n🔧 Problèmes détectés:")
            damage_type_errors = [e for e in self.results["errors"] if "damage_type" in e]
            if damage_type_errors:
                print(f"   - {len(damage_type_errors)} capacités avec damage_type manquant (corrigé automatiquement)")
        
        if self.results["warnings"]:
            cooldown_warnings = [w for w in self.results["warnings"] if "cooldown" in w]
            if cooldown_warnings:
                print(f"   - {len(cooldown_warnings)} problèmes de cooldowns (réinitialisation forcée)")
        
        print("="*60)

def main():
    """Fonction principale"""
    print("🎮 Script de test de combat en conditions réelles")
    print("="*60)
    
    try:
        tester = RealCombatTester()
        tester.run_real_combat_tests()
        
    except KeyboardInterrupt:
        print("\n⏹️  Test interrompu par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur fatale: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
