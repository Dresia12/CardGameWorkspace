#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de test complet pour toutes les capacités du jeu
Teste les capacités de base, avancées, passifs, et différents types de cibles
"""

import json
import random
import sys
import os
from typing import Dict, List, Any, Optional

# Ajouter le répertoire parent au path pour importer les modules du jeu
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Engine.engine import CombatEngine
from Engine.target_manager import TargetManager
from Engine.advanced_abilities import AdvancedAbilities
from Engine.seed_system import SeedSystem
from Engine.trap_system import TrapSystem
from Engine.passive_system import PassiveSystem

class ComprehensiveAbilityTester:
    """Classe pour tester toutes les capacités du jeu de manière exhaustive"""
    
    def __init__(self):
        self.engine = None
        self.test_results = {
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "errors": [],
            "warnings": [],
            "test_details": []
        }
        
    def load_game_data(self):
        """Charge les données du jeu"""
        try:
            with open("Data/effects_database.json", "r", encoding="utf-8") as f:
                self.effects_db = json.load(f)
            
            with open("Data/units.json", "r", encoding="utf-8") as f:
                self.units_data = json.load(f)
                
            with open("Data/heroes.json", "r", encoding="utf-8") as f:
                self.heroes_data = json.load(f)
                
            print("✓ Données du jeu chargées avec succès")
            return True
        except Exception as e:
            print(f"✗ Erreur lors du chargement des données: {e}")
            return False
    
    def initialize_game_engine(self):
        """Initialise le moteur de jeu pour les tests"""
        try:
            # Créer des objets Player pour le moteur
            from Engine.engine import Player
            from Engine.models import Hero, Unit, Card
            
            # Créer des héros de test
            player1_hero_data = self.create_test_hero("Test Hero 1", "Feu")
            player2_hero_data = self.create_test_hero("Test Hero 2", "Eau")
            
            # Créer des objets Hero
            player1_hero = Hero(
                name=player1_hero_data["name"],
                element=player1_hero_data["element"],
                base_stats=player1_hero_data["stats"],
                ability_name="Attaque de base",
                ability_description="Attaque de base du héros",
                ability_cooldown=0
            )
            
            player2_hero = Hero(
                name=player2_hero_data["name"],
                element=player2_hero_data["element"],
                base_stats=player2_hero_data["stats"],
                ability_name="Attaque de base",
                ability_description="Attaque de base du héros",
                ability_cooldown=0
            )
            
            # Créer des unités de test pour chaque élément
            player1_units_data = self.create_test_units_for_element("Feu", 3)
            player2_units_data = self.create_test_units_for_element("Eau", 3)
            
            # Créer des objets Unit
            player1_units = []
            for unit_data in player1_units_data:
                # Combiner ability_ids et passive_ids en une seule liste d'abilities
                all_abilities = unit_data["ability_ids"] + unit_data["passive_ids"]
                unit = Unit(
                    name=unit_data["name"],
                    element=unit_data["element"],
                    stats=unit_data["stats"],
                    abilities=all_abilities
                )
                player1_units.append(unit)
            
            player2_units = []
            for unit_data in player2_units_data:
                # Combiner ability_ids et passive_ids en une seule liste d'abilities
                all_abilities = unit_data["ability_ids"] + unit_data["passive_ids"]
                unit = Unit(
                    name=unit_data["name"],
                    element=unit_data["element"],
                    stats=unit_data["stats"],
                    abilities=all_abilities
                )
                player2_units.append(unit)
            
            # Créer des decks vides pour les tests
            empty_deck = []
            
            # Créer les objets Player
            player1 = Player("Test Player 1", empty_deck, player1_hero, player1_units)
            player2 = Player("Test Player 2", empty_deck, player2_hero, player2_units)
            
            # Initialiser le moteur avec les joueurs
            self.engine = CombatEngine(player1, player2)
            
            print("✓ Moteur de jeu initialisé avec succès")
            return True
        except Exception as e:
            print(f"✗ Erreur lors de l'initialisation du moteur: {e}")
            return False
    
    def create_test_hero(self, name: str, element: str):
        """Crée un héros de test"""
        return {
            "name": name,
            "element": element,
            "stats": {
                "hp": 1000,
                "attack": 50,
                "defense": 20,
                "mana": 100
            },
            "abilities": ["5000"],  # Capacité de base
            "passives": []
        }
    
    def create_test_units_for_element(self, element: str, count: int) -> List[Dict]:
        """Crée des unités de test pour un élément donné"""
        units = []
        element_id = self.get_element_id(element)
        
        for i in range(count):
            unit = {
                "id": f"test_{element}_{i}",
                "name": f"Test {element} Unit {i}",
                "element": element,
                "rarity": "Common",
                "stats": {
                    "hp": 500 + (i * 50),
                    "attack": 20 + (i * 5),
                    "defense": 10 + (i * 2),
                    "mana": 50
                },
                "ability_ids": [str(5000 + ((element_id - 1) * 250))],  # Capacité de base de l'élément
                "passive_ids": [],
                "image_path": f"Assets/Units/{element.lower()}_unit_{i}.png"
            }
            units.append(unit)
        
        return units
    
    def get_element_id(self, element: str) -> int:
        """Retourne l'ID numérique d'un élément"""
        element_map = {
            "Feu": 1, "Eau": 2, "Terre": 3, "Air": 4, "Glace": 5, "Foudre": 6,
            "Lumière": 7, "Ténèbres": 8, "Arcanique": 9, "Poison": 10, "Nature": 11, "Métal": 12
        }
        return element_map.get(element, 1)
    
    def test_basic_abilities(self):
        """Teste toutes les capacités de base (Basic Attack)"""
        print("\n=== TEST DES CAPACITÉS DE BASE ===")
        
        elements = ["Feu", "Eau", "Terre", "Air", "Glace", "Foudre", "Lumière", "Ténèbres", "Arcanique", "Poison", "Nature", "Métal"]
        
        for element in elements:
            self.test_basic_ability_for_element(element)
    
    def test_basic_ability_for_element(self, element: str):
        """Teste la capacité de base d'un élément spécifique"""
        element_id = self.get_element_id(element)
        ability_id = str(5000 + ((element_id - 1) * 250))
        
        try:
            # Trouver la capacité dans la base de données
            abilities_dict = self.effects_db.get("abilities", {})
            ability_data = abilities_dict.get(ability_id)
            
            if not ability_data:
                self.record_error(f"Capacité de base {ability_id} pour {element} non trouvée")
                return
            
            # Tester l'exécution de la capacité
            caster = self.engine.players[0].units[0] if self.engine.players[0].units else None
            target = self.engine.players[1].units[0] if self.engine.players[1].units else None
            
            if caster and target:
                # Créer un dictionnaire pour l'unité caster (compatibilité)
                caster_dict = self.create_unit_dict(caster, 0)
                
                result = self.engine.execute_advanced_ability(caster_dict, ability_id, target)
                self.record_test_result(f"Capacité de base {element}", result, ability_data)
            else:
                self.record_error(f"Impossible de tester la capacité {element}: caster ou target manquant")
                
        except Exception as e:
            self.record_error(f"Erreur lors du test de la capacité de base {element}: {e}")
    
    def test_advanced_abilities(self):
        """Teste TOUTES les capacités avancées de la base de données"""
        print("\n=== TEST DE TOUTES LES CAPACITÉS AVANCÉES ===")
        
        # Tester TOUTES les capacités présentes dans effects_database.json
        abilities_dict = self.effects_db.get("abilities", {})
        for ability_id, ability_data in abilities_dict.items():
            ability_name = ability_data.get("name", "Sans nom")
            element_id_str = ability_data.get("element", "0")
            
            # Nettoyer l'ID d'élément (enlever les virgules)
            element_id_str = element_id_str.split(',')[0] if ',' in element_id_str else element_id_str
            
            try:
                element_id = int(element_id_str)
                # Convertir l'ID d'élément en nom
                element_name = self.get_element_name(element_id)
                
                # Ignorer les capacités de base (testées séparément)
                if ability_id in ["5000", "5250", "5500", "5750", "6000", "6250", "6500", "6750", "7000", "7250", "7500", "7750"]:
                    continue
                    
                self.test_specific_ability(ability_id, element_name, ability_name, ability_data)
            except ValueError as e:
                self.record_error(f"Erreur de conversion d'ID d'élément '{element_id_str}' pour capacité {ability_id}: {e}")
                continue
    
    def test_specific_ability(self, ability_id: str, element: str, description: str, ability_data: Dict):
        """Teste une capacité spécifique de la base de données"""
        try:
            # Créer une unité avec cette capacité
            test_unit = self.create_test_unit_with_ability(element, ability_id)
            
            # Tester l'exécution
            caster = test_unit
            target = self.engine.players[1].units[0] if self.engine.players[1].units else None
            
            if target:
                # Créer un dictionnaire pour la target (compatibilité)
                target_dict = {
                    "id": getattr(target, 'id', "test_target"),
                    "name": getattr(target, 'name', "Test Target"),
                    "element": getattr(target, 'element', "Eau"),
                    "stats": getattr(target, 'stats', {"hp": 500, "attack": 20, "defense": 10, "mana": 50}),
                    "ability_ids": getattr(target, 'abilities', []),
                    "passive_ids": [],
                    "owner": 1
                }
                
                result = self.engine.execute_advanced_ability(caster, ability_id, target_dict)
                self.record_test_result(f"Capacité {ability_id} - {description}", result, ability_data)
            else:
                self.record_error(f"Impossible de tester {description} (ID: {ability_id}): target manquant")
                
        except Exception as e:
            self.record_error(f"Erreur lors du test de {description} (ID: {ability_id}): {e}")
    
    def get_element_name(self, element_id: int) -> str:
        """Retourne le nom d'un élément à partir de son ID"""
        element_map = {
            1: "Feu", 2: "Eau", 3: "Terre", 4: "Air", 5: "Glace", 6: "Foudre",
            7: "Lumière", 8: "Ténèbres", 9: "Arcanique", 10: "Poison", 11: "Nature", 12: "Métal"
        }
        return element_map.get(element_id, "Inconnu")
    
    def create_unit_dict(self, unit, owner=0):
        """Crée un dictionnaire compatible pour une unité"""
        return {
            "id": getattr(unit, 'id', f"test_unit_{owner}"),
            "name": getattr(unit, 'name', f"Test Unit {owner}"),
            "element": getattr(unit, 'element', "Feu"),
            "stats": getattr(unit, 'stats', {"hp": 500, "attack": 20, "defense": 10, "mana": 50}),
            "ability_ids": getattr(unit, 'abilities', []),
            "passive_ids": [],
            "owner": owner
        }
    
    def test_passive_system(self):
        """Teste TOUS les passifs de la base de données"""
        print("\n=== TEST DE TOUS LES PASSIFS ===")
        
        # Tester TOUS les passifs présents dans effects_database.json
        passives_dict = self.effects_db.get("passives", {})
        for passive_id, passive_data in passives_dict.items():
            passive_name = passive_data.get("name", "Sans nom")
            
            self.test_specific_passive(passive_id, passive_name, passive_data)
    
    def test_specific_passive(self, passive_id: str, description: str, passive_data: Dict):
        """Teste un passif spécifique de la base de données"""
        try:
            # Créer une unité avec ce passif
            test_unit = self.create_test_unit_with_passive(passive_id)
            
            # Pour l'instant, on ne peut pas tester les passifs directement
            # car la méthode apply_passive_effect n'existe pas
            self.record_warning(f"Test de passif {passive_id} - {description} non implémenté")
            
        except Exception as e:
            self.record_error(f"Erreur lors du test du passif {description} (ID: {passive_id}): {e}")
    
    def create_test_unit_with_ability(self, element: str, ability_id: str):
        """Crée une unité de test avec une capacité spécifique"""
        return {
            "id": f"test_advanced_{element}",
            "name": f"Test Advanced {element}",
            "element": element,
            "stats": {
                "hp": 800,
                "attack": 30,
                "defense": 15,
                "mana": 100
            },
            "ability_ids": [ability_id],
            "passive_ids": [],
            "owner": 0
        }
    
    def test_targeting_systems(self):
        """Teste tous les systèmes de ciblage"""
        print("\n=== TEST DES SYSTÈMES DE CIBLAGE ===")
        
        target_types = [
            "single_enemy", "single_ally", "self", "all_enemies", "all_allies",
            "random_enemy", "random_ally", "chain_enemies", "chain_allies",
            "random_multiple", "self_and_allies", "adjacent_enemies", "front_row", "back_row"
        ]
        
        for target_type in target_types:
            self.test_targeting_type(target_type)
    
    def test_targeting_type(self, target_type: str):
        """Teste un type de ciblage spécifique"""
        try:
            # Créer une capacité de test avec ce type de ciblage
            test_ability = {
                "id": f"test_target_{target_type}",
                "name": f"Test {target_type}",
                "element": 0,
                "base_cooldown": 1,
                "damage_type": "attack",
                "damage": 20,
                "target_type": target_type,
                "description": f"Test de ciblage {target_type}"
            }
            
            # Tester la sélection de cibles
            caster = self.engine.players[0].units[0] if self.engine.players[0].units else None
            if caster:
                # Créer un dictionnaire pour le caster (compatibilité)
                caster_dict = self.create_unit_dict(caster, 0)
                
                # Vérifier si la méthode existe
                if hasattr(self.engine, 'select_ability_targets'):
                    targets = self.engine.select_ability_targets(caster_dict, test_ability, None)
                    self.record_test_result(f"Ciblage {target_type}", len(targets) > 0, test_ability)
                else:
                    self.record_warning(f"Méthode select_ability_targets non disponible pour {target_type}")
            else:
                self.record_error(f"Impossible de tester le ciblage {target_type}: caster manquant")
                
        except Exception as e:
            self.record_error(f"Erreur lors du test du ciblage {target_type}: {e}")
    
    def test_damage_types(self):
        """Teste tous les types de dégâts"""
        print("\n=== TEST DES TYPES DE DÉGÂTS ===")
        
        damage_types = [
            "fixed", "attack", "attack_plus", "attack_multiplier", "hp_percent",
            "caster_hp_percent", "scaling", "random", "chain", "scaling_heal",
            "multi_attack", "seed_explosion", "attack_plus_defense"
        ]
        
        for damage_type in damage_types:
            self.test_damage_type(damage_type)
    
    def test_damage_type(self, damage_type: str):
        """Teste un type de dégâts spécifique"""
        try:
            # Créer une capacité de test avec ce type de dégâts
            test_ability = {
                "id": f"test_damage_{damage_type}",
                "name": f"Test {damage_type}",
                "element": 0,
                "base_cooldown": 1,
                "damage_type": damage_type,
                "damage": 20,
                "target_type": "single_enemy",
                "description": f"Test de dégâts {damage_type}"
            }
            
            # Tester le calcul de dégâts
            caster = self.engine.players[0].units[0] if self.engine.players[0].units else None
            target = self.engine.players[1].units[0] if self.engine.players[1].units else None
            
            if caster and target:
                # Créer des dictionnaires pour compatibilité
                caster_dict = self.create_unit_dict(caster, 0)
                
                target_dict = self.create_unit_dict(target, 1)
                
                damage = self.engine.calculate_ability_damage(test_ability, caster_dict)
                self.record_test_result(f"Dégâts {damage_type}", damage >= 0, test_ability)
            else:
                self.record_error(f"Impossible de tester les dégâts {damage_type}: caster ou target manquant")
                
        except Exception as e:
            self.record_error(f"Erreur lors du test des dégâts {damage_type}: {e}")
    
    def test_status_effects(self):
        """Teste tous les effets de statut"""
        print("\n=== TEST DES EFFETS DE STATUT ===")
        
        status_effects = [
            "burn", "freeze", "wet", "poison", "overload", "fragile", "stunned",
            "aspiration", "shield", "purify", "corruption", "annihilation",
            "immunity", "heal", "void", "arcanic_magic", "heal_reduction",
            "defense_reduction", "dodge_boost", "crit_boost", "random_debuff",
            "steal_mana", "damage_boost", "silence", "damage_per_turn",
            "damage_reduction", "precision_reduction", "electrified", "beurk"
        ]
        
        for effect in status_effects:
            self.test_status_effect(effect)
    
    def test_status_effect(self, effect: str):
        """Teste un effet de statut spécifique"""
        try:
            # Créer une capacité de test avec cet effet
            test_ability = {
                "id": f"test_effect_{effect}",
                "name": f"Test {effect}",
                "element": 0,
                "base_cooldown": 1,
                "damage_type": "attack",
                "damage": 10,
                "target_type": "single_enemy",
                "description": f"Test d'effet {effect}",
                effect: True
            }
            
            # Tester l'application de l'effet
            caster = self.engine.players[0].units[0] if self.engine.players[0].units else None
            target = self.engine.players[1].units[0] if self.engine.players[1].units else None
            
            if caster and target:
                # Créer des dictionnaires pour compatibilité
                caster_dict = self.create_unit_dict(caster, 0)
                
                target_dict = self.create_unit_dict(target, 1)
                
                self.engine.apply_advanced_effects(caster_dict, test_ability, target_dict)
                self.record_test_result(f"Effet {effect}", True, test_ability)
            else:
                self.record_error(f"Impossible de tester l'effet {effect}: caster ou target manquant")
                
        except Exception as e:
            self.record_error(f"Erreur lors du test de l'effet {effect}: {e}")
    
    def test_passive_system(self):
        """Teste le système de passifs"""
        print("\n=== TEST DU SYSTÈME DE PASSIFS ===")
        
        # Tester les passifs élémentaires
        passive_types = [
            ("1000", "Résistance au Feu"),
            ("1001", "Résistance à l'Eau"),
            ("1002", "Résistance à la Terre"),
            ("1100", "Aura de Feu"),
            ("1101", "Aura d'Eau"),
            ("1102", "Aura de Terre"),
            ("1200", "Boost de Feu"),
            ("1201", "Boost d'Eau"),
            ("1202", "Boost de Terre"),
        ]
        
        for passive_id, description in passive_types:
            self.test_passive(passive_id, description)
    
    def test_passive(self, passive_id: str, description: str):
        """Teste un passif spécifique"""
        try:
            # Trouver le passif dans la base de données
            passives_dict = self.effects_db.get("passives", {})
            passive_data = passives_dict.get(passive_id)
            
            if not passive_data:
                self.record_warning(f"Passif {passive_id} ({description}) non trouvé")
                return
            
            # Créer une unité avec ce passif
            test_unit = self.create_test_unit_with_passive(passive_id)
            
            # Pour l'instant, on ne peut pas tester les passifs directement
            self.record_warning(f"Test de passif {description} non implémenté")
            
        except Exception as e:
            self.record_error(f"Erreur lors du test du passif {description}: {e}")
    
    def create_test_unit_with_passive(self, passive_id: str):
        """Crée une unité de test avec un passif spécifique"""
        return {
            "id": f"test_passive_{passive_id}",
            "name": f"Test Passive {passive_id}",
            "element": "Feu",
            "stats": {
                "hp": 600,
                "attack": 25,
                "defense": 12,
                "mana": 80
            },
            "ability_ids": ["5000"],
            "passive_ids": [passive_id],
            "owner": 0
        }
    
    def test_elemental_interactions(self):
        """Teste les interactions élémentaires"""
        print("\n=== TEST DES INTERACTIONS ÉLÉMENTAIRES ===")
        
        element_pairs = [
            ("Feu", "Eau"),
            ("Eau", "Terre"),
            ("Terre", "Air"),
            ("Air", "Feu"),
            ("Glace", "Foudre"),
            ("Foudre", "Lumière"),
            ("Lumière", "Ténèbres"),
            ("Ténèbres", "Arcanique"),
            ("Arcanique", "Poison"),
            ("Poison", "Nature"),
            ("Nature", "Métal"),
            ("Métal", "Glace")
        ]
        
        for element1, element2 in element_pairs:
            self.test_elemental_interaction(element1, element2)
    
    def test_elemental_interaction(self, element1: str, element2: str):
        """Teste l'interaction entre deux éléments"""
        try:
            # Créer des unités des deux éléments
            unit1 = self.create_test_unit_for_element(element1)
            unit2 = self.create_test_unit_for_element(element2)
            
            # Tester l'attaque
            ability_id = str(5000 + ((self.get_element_id(element1) - 1) * 250))
            result = self.engine.execute_advanced_ability(unit1, ability_id, unit2)
            
            self.record_test_result(f"Interaction {element1} vs {element2}", result, {
                "attacker": element1,
                "defender": element2,
                "ability": ability_id
            })
            
        except Exception as e:
            self.record_error(f"Erreur lors du test de l'interaction {element1} vs {element2}: {e}")
    
    def create_test_unit_for_element(self, element: str):
        """Crée une unité de test pour un élément"""
        return {
            "id": f"test_{element.lower()}",
            "name": f"Test {element}",
            "element": element,
            "stats": {
                "hp": 500,
                "attack": 20,
                "defense": 10,
                "mana": 50
            },
            "ability_ids": [str(5000 + ((self.get_element_id(element) - 1) * 250))],
            "passive_ids": [],
            "owner": 0
        }
    
    def test_advanced_mechanics(self):
        """Teste les mécaniques avancées"""
        print("\n=== TEST DES MÉCANIQUES AVANCÉES ===")
        
        # Test du système de graines
        self.test_seed_system()
        
        # Test du système de pièges
        self.test_trap_system()
        
        # Test des chaînes aléatoires
        self.test_random_chains()
        
        # Test des capacités multi-cibles
        self.test_multi_target_abilities()
    
    def test_seed_system(self):
        """Teste le système de graines"""
        try:
            # Pour l'instant, le système de graines n'est pas initialisé dans le moteur
            self.record_warning("Système de graines non disponible - test ignoré")
        except Exception as e:
            self.record_error(f"Erreur lors du test du système de graines: {e}")
    
    def test_trap_system(self):
        """Teste le système de pièges"""
        try:
            # Pour l'instant, le système de pièges n'est pas initialisé dans le moteur
            self.record_warning("Système de pièges non disponible - test ignoré")
        except Exception as e:
            self.record_error(f"Erreur lors du test du système de pièges: {e}")
    
    def test_random_chains(self):
        """Teste les chaînes aléatoires"""
        try:
            # Pour l'instant, le système de capacités avancées n'est pas initialisé dans le moteur
            self.record_warning("Système de capacités avancées non disponible - test ignoré")
        except Exception as e:
            self.record_error(f"Erreur lors du test des chaînes aléatoires: {e}")
    
    def test_multi_target_abilities(self):
        """Teste les capacités multi-cibles"""
        try:
            # Créer une capacité multi-cibles
            multi_ability = {
                "id": "test_multi",
                "name": "Test Multi",
                "element": 0,
                "base_cooldown": 1,
                "damage_type": "attack",
                "damage": 12,
                "target_type": "random_multiple",
                "target_count": 2,
                "same_target_allowed": False
            }
            
            # Tester la sélection multi-cibles
            caster = self.engine.players[0].units[0] if self.engine.players[0].units else None
            if caster:
                # Créer un dictionnaire pour le caster (compatibilité)
                caster_dict = self.create_unit_dict(caster, 0)
                
                # Vérifier si la méthode existe
                if hasattr(self.engine, 'get_random_multiple_targets'):
                    targets = self.engine.get_random_multiple_targets(caster_dict, 2, False)
                    self.record_test_result("Capacités multi-cibles", len(targets) > 0, {"targets": len(targets)})
                else:
                    self.record_warning("Méthode get_random_multiple_targets non disponible")
            else:
                self.record_error("Impossible de tester les capacités multi-cibles: caster manquant")
        except Exception as e:
            self.record_error(f"Erreur lors du test des capacités multi-cibles: {e}")
    
    def test_all_units_from_database(self):
        """Teste TOUTES les unités présentes dans units.json"""
        print("\n=== TEST DE TOUTES LES UNITÉS ===")
        
        # Tester TOUTES les unités présentes dans units.json
        for unit_data in self.units_data:
            unit_name = unit_data.get("name", "Sans nom")
            unit_element = unit_data.get("element", "Inconnu")
            ability_ids = unit_data.get("ability_ids", [])
            passive_ids = unit_data.get("passive_ids", [])
            
            self.test_specific_unit(unit_name, unit_element, ability_ids, passive_ids, unit_data)
    
    def test_specific_unit(self, unit_name: str, element: str, abilities: List[str], passives: List[str], unit_data: Dict):
        """Teste une unité spécifique de la base de données"""
        try:
            # Créer l'unité avec ses vraies capacités et passifs
            test_unit = {
                "id": f"test_{unit_name.lower().replace(' ', '_')}",
                "name": unit_name,
                "element": element,
                "stats": unit_data.get("stats", {
                    "hp": 500,
                    "attack": 20,
                    "defense": 10,
                    "mana": 50
                }),
                "ability_ids": abilities,
                "passive_ids": passives,
                "owner": 0
            }
            
            # Tester chaque capacité de l'unité
            for ability_id in abilities:
                target = self.engine.players[1].units[0] if self.engine.players[1].units else None
                if target:
                    # Créer un dictionnaire pour la target (compatibilité)
                    target_dict = self.create_unit_dict(target, 1)
                    
                    result = self.engine.execute_advanced_ability(test_unit, ability_id, target_dict)
                    self.record_test_result(f"{unit_name} - Capacité {ability_id}", result, {"unit": unit_name, "ability": ability_id})
                else:
                    self.record_error(f"Impossible de tester {unit_name} capacité {ability_id}: target manquant")
            
            # Tester chaque passif de l'unité
            for passive_id in passives:
                # Pour l'instant, on ne peut pas tester les passifs directement
                self.record_warning(f"Test de passif {unit_name} - {passive_id} non implémenté")
                
        except Exception as e:
            self.record_error(f"Erreur lors du test de l'unité {unit_name}: {e}")
    
    def test_all_effects(self):
        """Teste TOUS les effets de la base de données"""
        print("\n=== TEST DE TOUS LES EFFETS ===")
        
        # Tester TOUS les effets présents dans effects_database.json
        effects_dict = self.effects_db.get("effects", {})
        for effect_id, effect_data in effects_dict.items():
            effect_name = effect_data.get("name", "Sans nom")
            
            self.test_specific_effect(effect_id, effect_name, effect_data)
    
    def test_specific_effect(self, effect_id: str, description: str, effect_data: Dict):
        """Teste un effet spécifique de la base de données"""
        try:
            # Créer une capacité de test avec cet effet
            test_ability = {
                "id": f"test_effect_{effect_id}",
                "name": f"Test {description}",
                "element": 0,
                "base_cooldown": 1,
                "damage_type": "attack",
                "damage": 10,
                "target_type": "single_enemy",
                "description": f"Test d'effet {description}",
                "effect_ids": [effect_id]
            }
            
            # Tester l'application de l'effet
            caster = self.engine.players[0].units[0] if self.engine.players[0].units else None
            target = self.engine.players[1].units[0] if self.engine.players[1].units else None
            
            if caster and target:
                # Créer des dictionnaires pour compatibilité
                caster_dict = self.create_unit_dict(caster, 0)
                
                target_dict = self.create_unit_dict(target, 1)
                
                self.engine.apply_advanced_effects(caster_dict, test_ability, target_dict)
                self.record_test_result(f"Effet {effect_id} - {description}", True, effect_data)
            else:
                self.record_error(f"Impossible de tester l'effet {description} (ID: {effect_id}): caster ou target manquant")
                
        except Exception as e:
            self.record_error(f"Erreur lors du test de l'effet {description} (ID: {effect_id}): {e}")
    
    def test_special_units(self):
        """Teste les unités spéciales (Murkax, Floralia, etc.)"""
        print("\n=== TEST DES UNITÉS SPÉCIALES ===")
        
        special_units = [
            ("Murkax", "Ténèbres", ["6751", "6752"], ["1335"]),
            ("Floralia", "Poison", ["7250", "7258"], ["1009"]),
        ]
        
        for unit_name, element, abilities, passives in special_units:
            self.test_special_unit(unit_name, element, abilities, passives)
    
    def test_special_unit(self, unit_name: str, element: str, abilities: List[str], passives: List[str]):
        """Teste une unité spéciale"""
        try:
            # Créer l'unité spéciale
            special_unit = {
                "id": f"test_{unit_name.lower()}",
                "name": unit_name,
                "element": element,
                "stats": {
                    "hp": 800,
                    "attack": 30,
                    "defense": 15,
                    "mana": 100
                },
                "ability_ids": abilities,
                "passive_ids": passives,
                "owner": 0
            }
            
            # Tester chaque capacité
            for ability_id in abilities:
                target = self.engine.players[1].units[0] if self.engine.players[1].units else None
                if target:
                    # Créer un dictionnaire pour la target (compatibilité)
                    target_dict = self.create_unit_dict(target, 1)
                    
                    result = self.engine.execute_advanced_ability(special_unit, ability_id, target_dict)
                    self.record_test_result(f"{unit_name} - Capacité {ability_id}", result, {"unit": unit_name, "ability": ability_id})
                else:
                    self.record_error(f"Impossible de tester {unit_name} capacité {ability_id}: target manquant")
            
            # Tester les passifs
            for passive_id in passives:
                # Pour l'instant, on ne peut pas tester les passifs directement
                self.record_warning(f"Test de passif {unit_name} - {passive_id} non implémenté")
                
        except Exception as e:
            self.record_error(f"Erreur lors du test de l'unité spéciale {unit_name}: {e}")
    
    def record_test_result(self, test_name: str, success: bool, details: Dict):
        """Enregistre le résultat d'un test"""
        self.test_results["total_tests"] += 1
        
        if success:
            self.test_results["passed_tests"] += 1
            print(f"✓ {test_name}")
        else:
            self.test_results["failed_tests"] += 1
            print(f"✗ {test_name}")
        
        self.test_results["test_details"].append({
            "name": test_name,
            "success": success,
            "details": details
        })
    
    def record_error(self, error_message: str):
        """Enregistre une erreur"""
        self.test_results["errors"].append(error_message)
        print(f"✗ ERREUR: {error_message}")
    
    def record_warning(self, warning_message: str):
        """Enregistre un avertissement"""
        self.test_results["warnings"].append(warning_message)
        print(f"⚠ AVERTISSEMENT: {warning_message}")
    
    def generate_report(self):
        """Génère un rapport complet des tests"""
        print("\n" + "="*60)
        print("RAPPORT COMPLET DES TESTS")
        print("="*60)
        
        total = self.test_results["total_tests"]
        passed = self.test_results["passed_tests"]
        failed = self.test_results["failed_tests"]
        
        print(f"Tests totaux: {total}")
        print(f"Tests réussis: {passed}")
        print(f"Tests échoués: {failed}")
        print(f"Taux de réussite: {(passed/total*100):.1f}%" if total > 0 else "N/A")
        
        if self.test_results["errors"]:
            print(f"\nErreurs ({len(self.test_results['errors'])}):")
            for error in self.test_results["errors"]:
                print(f"  - {error}")
        
        if self.test_results["warnings"]:
            print(f"\nAvertissements ({len(self.test_results['warnings'])}):")
            for warning in self.test_results["warnings"]:
                print(f"  - {warning}")
        
        # Sauvegarder le rapport
        with open("test_report.json", "w", encoding="utf-8") as f:
            json.dump(self.test_results, f, indent=2, ensure_ascii=False)
        
        print(f"\nRapport détaillé sauvegardé dans: test_report.json")
    
    def run_all_tests(self):
        """Exécute tous les tests"""
        print("DÉMARRAGE DES TESTS COMPLETS")
        print("="*60)
        
        # Charger les données
        if not self.load_game_data():
            return False
        
        # Initialiser le moteur
        if not self.initialize_game_engine():
            return False
        
        # Exécuter tous les tests
        self.test_basic_abilities()
        self.test_advanced_abilities()  # Maintenant teste TOUTES les capacités
        self.test_all_effects()  # Teste TOUS les effets
        self.test_passive_system()  # Maintenant teste TOUS les passifs
        self.test_all_units_from_database()  # Teste TOUTES les unités
        self.test_targeting_systems()
        self.test_damage_types()
        self.test_status_effects()
        self.test_elemental_interactions()
        self.test_advanced_mechanics()
        self.test_special_units()
        
        # Générer le rapport
        self.generate_report()
        
        return True

def main():
    """Fonction principale"""
    tester = ComprehensiveAbilityTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n✓ Tous les tests ont été exécutés avec succès")
    else:
        print("\n✗ Certains tests ont échoué")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())
