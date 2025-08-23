#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de test des interactions élémentaires
Teste les bonus/malus entre éléments et les effets spéciaux
"""

import json
import sys
import os
import random
import time
from typing import Dict, List, Any, Tuple

# Ajout du répertoire parent au path pour les imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from Engine.engine import CombatEngine, Player
    from Engine.models import Hero, Unit, Card, Ability
    from Engine.effects_database_manager import EffectsDatabaseManager
except ImportError as e:
    print(f"❌ Erreur d'import: {e}")
    print("Assurez-vous d'être dans le bon répertoire")
    sys.exit(1)

class ElementalInteractionTester:
    def __init__(self):
        self.results = {
            "success": [],
            "errors": [],
            "warnings": [],
            "elemental_tests": [],
            "stats": {
                "tests_performed": 0,
                "successful_interactions": 0,
                "failed_interactions": 0,
                "element_combinations": 0
            }
        }
        
        # Matrice des interactions élémentaires
        self.elemental_matrix = {
            "1": {"weak_to": ["2"], "strong_against": ["3"], "neutral": ["4", "5", "6", "7", "8", "9", "10", "11", "12"]},  # Feu
            "2": {"weak_to": ["3"], "strong_against": ["1"], "neutral": ["4", "5", "6", "7", "8", "9", "10", "11", "12"]},  # Eau
            "3": {"weak_to": ["1"], "strong_against": ["2"], "neutral": ["4", "5", "6", "7", "8", "9", "10", "11", "12"]},  # Air
            "4": {"weak_to": ["5"], "strong_against": ["6"], "neutral": ["1", "2", "3", "7", "8", "9", "10", "11", "12"]},  # Terre
            "5": {"weak_to": ["6"], "strong_against": ["4"], "neutral": ["1", "2", "3", "7", "8", "9", "10", "11", "12"]},  # Foudre
            "6": {"weak_to": ["4"], "strong_against": ["5"], "neutral": ["1", "2", "3", "7", "8", "9", "10", "11", "12"]},  # Glace
            "7": {"weak_to": ["8"], "strong_against": ["9"], "neutral": ["1", "2", "3", "4", "5", "6", "10", "11", "12"]},  # Lumière
            "8": {"weak_to": ["9"], "strong_against": ["7"], "neutral": ["1", "2", "3", "4", "5", "6", "10", "11", "12"]},  # Ténèbres
            "9": {"weak_to": ["7"], "strong_against": ["8"], "neutral": ["1", "2", "3", "4", "5", "6", "10", "11", "12"]},  # Néant
            "10": {"weak_to": ["11"], "strong_against": ["12"], "neutral": ["1", "2", "3", "4", "5", "6", "7", "8", "9"]},  # Poison
            "11": {"weak_to": ["12"], "strong_against": ["10"], "neutral": ["1", "2", "3", "4", "5", "6", "7", "8", "9"]},  # Arcanique
            "12": {"weak_to": ["10"], "strong_against": ["11"], "neutral": ["1", "2", "3", "4", "5", "6", "7", "8", "9"]}   # Neutre
        }
        
        # Noms des éléments
        self.element_names = {
            "1": "Feu", "2": "Eau", "3": "Air", "4": "Terre", "5": "Foudre", "6": "Glace",
            "7": "Lumière", "8": "Ténèbres", "9": "Néant", "10": "Poison", "11": "Arcanique", "12": "Neutre"
        }
        
        # Chargement des données
        self.load_data()
        
    def load_data(self):
        """Charge toutes les données nécessaires"""
        try:
            print("📂 Chargement des données pour tests élémentaires...")
            
            # Chargement de la base de données des effets
            self.effects_db = EffectsDatabaseManager()
            
            # Chargement des données JSON
            with open('Data/effects_database.json', 'r', encoding='utf-8') as f:
                self.effects_data = json.load(f)
            
            with open('Data/units.json', 'r', encoding='utf-8') as f:
                self.units_data = json.load(f)
            
            with open('Data/heroes.json', 'r', encoding='utf-8') as f:
                self.heroes_data = json.load(f)
                
            print("✅ Données chargées avec succès")
            
        except Exception as e:
            print(f"❌ Erreur lors du chargement des données: {e}")
            sys.exit(1)
    
    def _iter_entities(self, data):
        """Permet d'itérer sur des données JSON qui peuvent être une liste ou un dict."""
        if isinstance(data, dict):
            return data.values()
        if isinstance(data, list):
            return data
        return []
    
    def create_elemental_unit(self, element: str, name: str = None) -> Unit:
        """Crée une unité avec un élément spécifique"""
        if name is None:
            name = f"Test {self.element_names.get(element, element)}"
        
        # Créer une capacité élémentaire de base
        ability = Ability(
            name=f"Attaque {self.element_names.get(element, element)}",
            description=f"Attaque élémentaire de {self.element_names.get(element, element)}",
            cooldown=0
        )
        ability.damage = 50
        ability.target_type = "single_enemy"
        ability.element = element
        ability.ability_id = f"test_{element}"
        ability.current_cooldown = 0
        
        # Créer l'unité
        unit = Unit(
            name=name,
            element=element,
            stats={
                'hp': 200,
                'attack': 30,
                'defense': 15
            },
            abilities=[ability]
        )
        
        # Remplacer la liste d'IDs par la liste d'objets Ability
        unit.abilities = [ability]
        
        return unit
    
    def get_elemental_interaction(self, attacker_element: str, defender_element: str) -> str:
        """Détermine l'interaction élémentaire entre deux éléments"""
        if attacker_element not in self.elemental_matrix:
            return "neutral"
        
        matrix = self.elemental_matrix[attacker_element]
        
        if defender_element in matrix["strong_against"]:
            return "strong"
        elif defender_element in matrix["weak_to"]:
            return "weak"
        else:
            return "neutral"
    
    def calculate_elemental_damage(self, base_damage: int, interaction: str) -> int:
        """Calcule les dégâts en tenant compte de l'interaction élémentaire"""
        if interaction == "strong":
            return int(base_damage * 1.5)  # +50% de dégâts
        elif interaction == "weak":
            return int(base_damage * 0.5)  # -50% de dégâts
        else:
            return base_damage  # Dégâts normaux
    
    def test_elemental_interaction(self, attacker_element: str, defender_element: str) -> Dict:
        """Teste une interaction élémentaire spécifique"""
        try:
            print(f"\n⚔️ Test interaction: {self.element_names.get(attacker_element, attacker_element)} → {self.element_names.get(defender_element, defender_element)}")
            
            # Créer les unités de test
            attacker = self.create_elemental_unit(attacker_element, f"Attaquant {self.element_names.get(attacker_element, attacker_element)}")
            defender = self.create_elemental_unit(defender_element, f"Défenseur {self.element_names.get(defender_element, defender_element)}")
            
            # Créer les cartes de test
            test_cards = [
                Card("Carte Test 1", 1, "1", "sort", "Test effect"),
                Card("Carte Test 2", 2, "2", "créature", "Test effect")
            ]
            
            # Créer les héros de test
            hero_p1 = Hero("Héros Test P1", "1", {"hp": 1000, "attack": 50, "defense": 20})
            hero_p2 = Hero("Héros Test P2", "2", {"hp": 1000, "attack": 50, "defense": 20})
            
            # Créer les joueurs
            player1 = Player("Joueur 1", test_cards.copy(), hero_p1, [attacker])
            player2 = Player("Joueur 2", test_cards.copy(), hero_p2, [defender])
            
            # Créer le moteur de combat
            combat_engine = CombatEngine(player1, player2)
            
            # S'assurer que les unités ont les attributs nécessaires
            for unit in [attacker, defender]:
                if not hasattr(unit, 'owner'):
                    if unit == attacker:
                        unit.owner = player1
                    else:
                        unit.owner = player2
                
                if not hasattr(unit, 'is_alive'):
                    unit.is_alive = lambda: getattr(unit, 'hp', 0) > 0
            
            # Réinitialiser les cooldowns
            for unit in [attacker, defender]:
                for ability in unit.abilities:
                    ability.current_cooldown = 0
            
            # Déterminer l'interaction attendue
            expected_interaction = self.get_elemental_interaction(attacker_element, defender_element)
            
            # Calculer les dégâts attendus
            base_damage = attacker.abilities[0].damage
            expected_damage = self.calculate_elemental_damage(base_damage, expected_interaction)
            
            # Effectuer l'attaque
            defender_hp_before = defender.hp
            attacker_hp_before = attacker.hp
            
            try:
                success = combat_engine.use_ability(attacker, attacker.abilities[0], defender)
                
                if success:
                    defender_hp_after = defender.hp
                    actual_damage = defender_hp_before - defender_hp_after
                    
                    # Vérifier si les dégâts correspondent à l'interaction attendue
                    damage_correct = abs(actual_damage - expected_damage) <= 5  # Tolérance de 5 points
                    
                    # Déterminer l'interaction réelle basée sur les dégâts
                    if actual_damage > base_damage * 1.2:
                        actual_interaction = "strong"
                    elif actual_damage < base_damage * 0.8:
                        actual_interaction = "weak"
                    else:
                        actual_interaction = "neutral"
                    
                    # Vérifier la cohérence
                    interaction_correct = actual_interaction == expected_interaction
                    
                    test_result = {
                        "attacker_element": attacker_element,
                        "defender_element": defender_element,
                        "attacker_name": self.element_names.get(attacker_element, attacker_element),
                        "defender_name": self.element_names.get(defender_element, defender_element),
                        "expected_interaction": expected_interaction,
                        "actual_interaction": actual_interaction,
                        "base_damage": base_damage,
                        "expected_damage": expected_damage,
                        "actual_damage": actual_damage,
                        "damage_correct": damage_correct,
                        "interaction_correct": interaction_correct,
                        "success": True
                    }
                    
                    if interaction_correct and damage_correct:
                        self.results["stats"]["successful_interactions"] += 1
                        print(f"  ✅ Interaction correcte: {actual_damage} dégâts (attendu: {expected_damage})")
                    else:
                        self.results["stats"]["failed_interactions"] += 1
                        print(f"  ❌ Interaction incorrecte: {actual_damage} dégâts (attendu: {expected_damage})")
                        if not interaction_correct:
                            print(f"     Interaction attendue: {expected_interaction}, réelle: {actual_interaction}")
                    
                else:
                    test_result = {
                        "attacker_element": attacker_element,
                        "defender_element": defender_element,
                        "attacker_name": self.element_names.get(attacker_element, attacker_element),
                        "defender_name": self.element_names.get(defender_element, defender_element),
                        "expected_interaction": expected_interaction,
                        "actual_interaction": "unknown",
                        "base_damage": base_damage,
                        "expected_damage": expected_damage,
                        "actual_damage": 0,
                        "damage_correct": False,
                        "interaction_correct": False,
                        "success": False,
                        "error": "Échec de l'utilisation de la capacité"
                    }
                    
                    self.results["stats"]["failed_interactions"] += 1
                    print(f"  ❌ Échec de l'utilisation de la capacité")
                
            except Exception as e:
                test_result = {
                    "attacker_element": attacker_element,
                    "defender_element": defender_element,
                    "attacker_name": self.element_names.get(attacker_element, attacker_element),
                    "defender_name": self.element_names.get(defender_element, defender_element),
                    "expected_interaction": expected_interaction,
                    "actual_interaction": "error",
                    "base_damage": base_damage,
                    "expected_damage": expected_damage,
                    "actual_damage": 0,
                    "damage_correct": False,
                    "interaction_correct": False,
                    "success": False,
                    "error": str(e)
                }
                
                self.results["stats"]["failed_interactions"] += 1
                self.results["errors"].append(f"Erreur test {attacker_element}→{defender_element}: {e}")
                print(f"  ❌ Erreur: {e}")
            
            self.results["elemental_tests"].append(test_result)
            self.results["stats"]["tests_performed"] += 1
            
            return test_result
            
        except Exception as e:
            self.results["errors"].append(f"Erreur test interaction {attacker_element}→{defender_element}: {e}")
            return None
    
    def test_all_elemental_combinations(self):
        """Teste toutes les combinaisons d'éléments"""
        print("🚀 Test de toutes les combinaisons élémentaires...")
        
        elements = list(self.elemental_matrix.keys())
        self.results["stats"]["element_combinations"] = len(elements) * len(elements)
        
        for attacker_element in elements:
            for defender_element in elements:
                self.test_elemental_interaction(attacker_element, defender_element)
    
    def test_specific_elemental_scenarios(self):
        """Teste des scénarios élémentaires spécifiques"""
        print("\n🎯 Test de scénarios élémentaires spécifiques...")
        
        # Test des interactions fortes
        strong_interactions = [
            ("1", "3"),  # Feu > Air
            ("2", "1"),  # Eau > Feu
            ("3", "2"),  # Air > Eau
            ("4", "6"),  # Terre > Glace
            ("5", "4"),  # Foudre > Terre
            ("6", "5"),  # Glace > Foudre
            ("7", "9"),  # Lumière > Néant
            ("8", "7"),  # Ténèbres > Lumière
            ("9", "8"),  # Néant > Ténèbres
            ("10", "12"), # Poison > Neutre
            ("11", "10"), # Arcanique > Poison
            ("12", "11")  # Neutre > Arcanique
        ]
        
        print("🔥 Test des interactions fortes...")
        for attacker, defender in strong_interactions:
            self.test_elemental_interaction(attacker, defender)
        
        # Test des interactions faibles
        weak_interactions = [
            ("1", "2"),  # Feu < Eau
            ("2", "3"),  # Eau < Air
            ("3", "1"),  # Air < Feu
            ("4", "5"),  # Terre < Foudre
            ("5", "6"),  # Foudre < Glace
            ("6", "4"),  # Glace < Terre
            ("7", "8"),  # Lumière < Ténèbres
            ("8", "9"),  # Ténèbres < Néant
            ("9", "7"),  # Néant < Lumière
            ("10", "11"), # Poison < Arcanique
            ("11", "12"), # Arcanique < Neutre
            ("12", "10")  # Neutre < Poison
        ]
        
        print("💧 Test des interactions faibles...")
        for attacker, defender in weak_interactions:
            self.test_elemental_interaction(attacker, defender)
        
        # Test des interactions neutres
        neutral_interactions = [
            ("1", "4"),  # Feu vs Terre
            ("2", "5"),  # Eau vs Foudre
            ("3", "6"),  # Air vs Glace
            ("7", "10"), # Lumière vs Poison
            ("8", "11"), # Ténèbres vs Arcanique
            ("9", "12")  # Néant vs Neutre
        ]
        
        print("⚖️ Test des interactions neutres...")
        for attacker, defender in neutral_interactions:
            self.test_elemental_interaction(attacker, defender)
    
    def test_real_units_elemental_interactions(self):
        """Teste les interactions élémentaires avec de vraies unités du jeu"""
        print("\n🎮 Test des interactions avec de vraies unités...")
        
        # Collecter les unités par élément
        units_by_element = {}
        for unit_data in self._iter_entities(self.units_data):
            if isinstance(unit_data, dict) and "element" in unit_data and "ability_ids" in unit_data:
                element = unit_data["element"]
                if element not in units_by_element:
                    units_by_element[element] = []
                units_by_element[element].append(unit_data)
        
        # Tester quelques combinaisons avec de vraies unités
        test_combinations = [
            ("1", "2"),  # Feu vs Eau
            ("2", "3"),  # Eau vs Air
            ("3", "1"),  # Air vs Feu
            ("4", "5"),  # Terre vs Foudre
            ("5", "6"),  # Foudre vs Glace
        ]
        
        for attacker_element, defender_element in test_combinations:
            if attacker_element in units_by_element and defender_element in units_by_element:
                # Prendre la première unité de chaque élément
                attacker_data = units_by_element[attacker_element][0]
                defender_data = units_by_element[defender_element][0]
                
                print(f"\n⚔️ Test réel: {attacker_data.get('name', 'N/A')} ({self.element_names.get(attacker_element, attacker_element)}) vs {defender_data.get('name', 'N/A')} ({self.element_names.get(defender_element, defender_element)})")
                
                # Créer les unités avec leurs vraies capacités
                attacker = self.create_real_unit(attacker_data)
                defender = self.create_real_unit(defender_data)
                
                if attacker and defender:
                    self.test_real_unit_interaction(attacker, defender)
    
    def create_real_unit(self, unit_data):
        """Crée une unité réelle du jeu"""
        try:
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
                    ability.damage = ability_data.get('damage', 0)
                    ability.target_type = ability_data.get('target_type', 'single_enemy')
                    ability.element = ability_data.get('element', '1')
                    ability.ability_id = str(ability_id)
                    ability.current_cooldown = 0
                    abilities.append(ability)
            
            if not abilities:
                # Créer une capacité par défaut
                ability = Ability(
                    name=f"Attaque {self.element_names.get(unit_data.get('element', '1'), 'Base')}",
                    description="Attaque élémentaire de base",
                    cooldown=0
                )
                ability.damage = 30
                ability.target_type = "single_enemy"
                ability.element = unit_data.get('element', '1')
                ability.ability_id = "default"
                ability.current_cooldown = 0
                abilities = [ability]
            
            unit = Unit(
                name=unit_data.get('name', 'Unité inconnue'),
                element=unit_data.get('element', '1'),
                stats={
                    'hp': unit_data.get('hp', 100),
                    'attack': unit_data.get('attack', 20),
                    'defense': unit_data.get('defense', 10)
                },
                abilities=abilities
            )
            
            unit.abilities = abilities
            return unit
            
        except Exception as e:
            self.results["errors"].append(f"Erreur création unité réelle {unit_data.get('name', 'N/A')}: {e}")
            return None
    
    def test_real_unit_interaction(self, attacker, defender):
        """Teste l'interaction entre deux unités réelles"""
        try:
            # Créer les cartes de test
            test_cards = [
                Card("Carte Test 1", 1, "1", "sort", "Test effect"),
                Card("Carte Test 2", 2, "2", "créature", "Test effect")
            ]
            
            # Créer les héros de test
            hero_p1 = Hero("Héros Test P1", "1", {"hp": 1000, "attack": 50, "defense": 20})
            hero_p2 = Hero("Héros Test P2", "2", {"hp": 1000, "attack": 50, "defense": 20})
            
            # Créer les joueurs
            player1 = Player("Joueur 1", test_cards.copy(), hero_p1, [attacker])
            player2 = Player("Joueur 2", test_cards.copy(), hero_p2, [defender])
            
            # Créer le moteur de combat
            combat_engine = CombatEngine(player1, player2)
            
            # S'assurer que les unités ont les attributs nécessaires
            for unit in [attacker, defender]:
                if not hasattr(unit, 'owner'):
                    if unit == attacker:
                        unit.owner = player1
                    else:
                        unit.owner = player2
                
                if not hasattr(unit, 'is_alive'):
                    unit.is_alive = lambda: getattr(unit, 'hp', 0) > 0
            
            # Réinitialiser les cooldowns
            for unit in [attacker, defender]:
                for ability in unit.abilities:
                    ability.current_cooldown = 0
            
            # Déterminer l'interaction attendue
            expected_interaction = self.get_elemental_interaction(attacker.element, defender.element)
            
            # Effectuer l'attaque avec la première capacité
            if attacker.abilities:
                defender_hp_before = defender.hp
                
                try:
                    success = combat_engine.use_ability(attacker, attacker.abilities[0], defender)
                    
                    if success:
                        defender_hp_after = defender.hp
                        actual_damage = defender_hp_before - defender_hp_after
                        
                        print(f"  ✅ Attaque réussie: {actual_damage} dégâts")
                        print(f"     Interaction attendue: {expected_interaction}")
                        
                        # Vérifier si les dégâts correspondent à l'interaction
                        base_damage = attacker.abilities[0].damage
                        expected_damage = self.calculate_elemental_damage(base_damage, expected_interaction)
                        
                        if abs(actual_damage - expected_damage) <= 10:  # Tolérance plus large pour les vraies unités
                            print(f"     ✅ Dégâts cohérents avec l'interaction élémentaire")
                        else:
                            print(f"     ⚠️ Dégâts incohérents (attendu: {expected_damage}, réel: {actual_damage})")
                    else:
                        print(f"  ❌ Échec de l'attaque")
                        
                except Exception as e:
                    print(f"  ❌ Erreur lors de l'attaque: {e}")
            
        except Exception as e:
            self.results["errors"].append(f"Erreur test unités réelles: {e}")
    
    def run_elemental_tests(self):
        """Lance tous les tests élémentaires"""
        start_time = time.time()
        print("🚀 Démarrage des tests d'interactions élémentaires...")
        
        # Test des combinaisons de base
        self.test_specific_elemental_scenarios()
        
        # Test avec de vraies unités
        self.test_real_units_elemental_interactions()
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Affichage des résultats
        self.display_elemental_results(execution_time)
    
    def display_elemental_results(self, execution_time):
        """Affiche les résultats des tests élémentaires"""
        print("\n" + "="*70)
        print("📋 RÉSULTATS DES TESTS D'INTERACTIONS ÉLÉMENTAIRES")
        print("="*70)
        
        stats = self.results["stats"]
        print(f"📊 Statistiques:")
        print(f"   - Tests effectués: {stats['tests_performed']}")
        print(f"   - Interactions réussies: {stats['successful_interactions']}")
        print(f"   - Interactions échouées: {stats['failed_interactions']}")
        print(f"   - Combinaisons d'éléments: {stats['element_combinations']}")
        print(f"   - Temps d'exécution: {execution_time:.2f} secondes")
        
        if stats['tests_performed'] > 0:
            success_rate = (stats['successful_interactions'] / stats['tests_performed']) * 100
            print(f"   - Taux de succès: {success_rate:.1f}%")
        
        # Affichage des tests élémentaires
        if self.results["elemental_tests"]:
            print(f"\n⚔️ Tests d'interactions ({len(self.results['elemental_tests'])}):")
            
            # Grouper par type d'interaction
            strong_tests = [t for t in self.results["elemental_tests"] if t.get("expected_interaction") == "strong"]
            weak_tests = [t for t in self.results["elemental_tests"] if t.get("expected_interaction") == "weak"]
            neutral_tests = [t for t in self.results["elemental_tests"] if t.get("expected_interaction") == "neutral"]
            
            print(f"   🔥 Interactions fortes ({len(strong_tests)}):")
            successful_strong = [t for t in strong_tests if t.get("interaction_correct", False)]
            print(f"     - Réussies: {len(successful_strong)}/{len(strong_tests)}")
            
            print(f"   💧 Interactions faibles ({len(weak_tests)}):")
            successful_weak = [t for t in weak_tests if t.get("interaction_correct", False)]
            print(f"     - Réussies: {len(successful_weak)}/{len(weak_tests)}")
            
            print(f"   ⚖️ Interactions neutres ({len(neutral_tests)}):")
            successful_neutral = [t for t in neutral_tests if t.get("interaction_correct", False)]
            print(f"     - Réussies: {len(successful_neutral)}/{len(neutral_tests)}")
            
            # Afficher quelques exemples
            print(f"\n📝 Exemples d'interactions:")
            for test in self.results["elemental_tests"][:5]:
                status = "✅" if test.get("interaction_correct", False) else "❌"
                print(f"   {status} {test.get('attacker_name', 'N/A')} → {test.get('defender_name', 'N/A')}: {test.get('actual_damage', 0)} dégâts (attendu: {test.get('expected_damage', 0)})")
        
        # Affichage des erreurs
        if self.results["errors"]:
            print(f"\n❌ Erreurs ({len(self.results['errors'])}):")
            for error in self.results["errors"][:10]:
                print(f"   - {error}")
            if len(self.results["errors"]) > 10:
                print(f"   ... et {len(self.results['errors']) - 10} autres")
        
        # Recommandations
        print(f"\n💡 Recommandations:")
        if stats['failed_interactions'] > 0:
            print(f"   - Corriger les {stats['failed_interactions']} interactions échouées")
        if stats['successful_interactions'] == stats['tests_performed']:
            print(f"   - 🎉 Toutes les interactions élémentaires fonctionnent parfaitement!")
        
        print("="*70)

def main():
    """Fonction principale"""
    print("⚔️ Script de test des interactions élémentaires")
    print("="*70)
    
    try:
        tester = ElementalInteractionTester()
        tester.run_elemental_tests()
        
    except KeyboardInterrupt:
        print("\n⏹️  Test interrompu par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur fatale: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
