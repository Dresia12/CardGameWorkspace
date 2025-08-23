#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de vérification complète des capacités et effets en conditions réelles de combat
Teste toutes les capacités, passifs et effets de la base de données
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

class CombatVerificationTester:
    def __init__(self):
        self.results = {
            "success": [],
            "errors": [],
            "warnings": [],
            "stats": {
                "total_tested": 0,
                "successful": 0,
                "failed": 0,
                "warnings": 0
            }
        }
        
        # Chargement des données
        self.load_data()
    
    def _iter_entities(self, data):
        """Permet d'itérer sur des données JSON qui peuvent être une liste ou un dict."""
        if isinstance(data, dict):
            return data.values()
        if isinstance(data, list):
            return data
        return []
        
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
    
    def create_test_entities(self):
        """Crée des entités de test pour le combat"""
        try:
            # Création d'un héros de test
            test_hero = Hero(
                name="Héros Test",
                element="1",
                base_stats={"hp": 100, "attack": 50, "defense": 20},
                ability_name="",
                ability_description="",
                ability_cooldown=0
            )
            
            # Création d'unités de test avec différentes capacités
            test_units = []
            
            # Récupération de toutes les capacités uniques
            all_abilities = set()
            
            # Capacités des héros
            for hero_data in self._iter_entities(self.heroes_data):
                if isinstance(hero_data, dict) and "ability_ids" in hero_data:
                    all_abilities.update(hero_data.get("ability_ids", []))
            
            # Capacités des unités
            for unit_data in self._iter_entities(self.units_data):
                if isinstance(unit_data, dict) and "ability_ids" in unit_data:
                    all_abilities.update(unit_data.get("ability_ids", []))
            
            # Capacités des cartes
            for card_data in self._iter_entities(self.cards_data):
                if isinstance(card_data, dict) and "ability_ids" in card_data:
                    all_abilities.update(card_data.get("ability_ids", []))
            
            print(f"🔍 {len(all_abilities)} capacités uniques trouvées")
            
            # Création d'unités de test avec différentes capacités
            ability_list = list(all_abilities)
            for i, ability_id in enumerate(ability_list[:10]):  # Test des 10 premières pour commencer
                test_units.append(Unit(
                    name=f"Unité Test {i}",
                    element=str((i % 12) + 1),  # Éléments 1-12
                    stats={"hp": 80, "attack": 30, "defense": 15},
                    abilities=[ability_id]
                ))
            
            return test_hero, test_units
            
        except Exception as e:
            print(f"❌ Erreur lors de la création des entités de test: {e}")
            traceback.print_exc()
            return None, None
    
    def test_ability_loading(self, ability_id: str) -> bool:
        """Teste le chargement d'une capacité"""
        try:
            # Vérification dans la base de données des effets
            if ability_id in self.effects_data.get("abilities", {}):
                ability_data = self.effects_data["abilities"][ability_id]
                
                # Vérifications de base
                required_fields = ["name", "element", "base_cooldown", "damage_type", "target_type"]
                for field in required_fields:
                    if field not in ability_data:
                        self.results["errors"].append(f"Capacité {ability_id}: champ '{field}' manquant")
                        return False
                
                # Vérification des types de données
                if not isinstance(ability_data["base_cooldown"], int):
                    self.results["warnings"].append(f"Capacité {ability_id}: base_cooldown devrait être un entier")
                
                if not isinstance(ability_data["damage"], (int, float)):
                    self.results["warnings"].append(f"Capacité {ability_id}: damage devrait être numérique")
                
                return True
            else:
                self.results["errors"].append(f"Capacité {ability_id}: non trouvée dans la base de données")
                return False
                
        except Exception as e:
            self.results["errors"].append(f"Capacité {ability_id}: erreur lors du test - {e}")
            return False
    
    def test_passive_loading(self, passive_id: str) -> bool:
        """Teste le chargement d'un passif"""
        try:
            if passive_id in self.effects_data.get("passives", {}):
                passive_data = self.effects_data["passives"][passive_id]
                
                # Vérifications de base
                required_fields = ["name", "description"]
                for field in required_fields:
                    if field not in passive_data:
                        self.results["errors"].append(f"Passif {passive_id}: champ '{field}' manquant")
                        return False
                
                return True
            else:
                self.results["errors"].append(f"Passif {passive_id}: non trouvé dans la base de données")
                return False
                
        except Exception as e:
            self.results["errors"].append(f"Passif {passive_id}: erreur lors du test - {e}")
            return False
    
    def test_effect_loading(self, effect_id: str) -> bool:
        """Teste le chargement d'un effet"""
        try:
            # Vérification dans toutes les sections d'effets
            effect_sections = ["base_effects", "chain_effects", "elemental_interactions", 
                             "special_combos", "elemental_attack_effects"]
            
            for section in effect_sections:
                if effect_id in self.effects_data.get(section, {}):
                    effect_data = self.effects_data[section][effect_id]
                    
                    # Vérifications de base
                    required_fields = ["name", "description"]
                    for field in required_fields:
                        if field not in effect_data:
                            self.results["errors"].append(f"Effet {effect_id}: champ '{field}' manquant")
                            return False
                    
                    return True
            
            self.results["errors"].append(f"Effet {effect_id}: non trouvé dans la base de données")
            return False
                
        except Exception as e:
            self.results["errors"].append(f"Effet {effect_id}: erreur lors du test - {e}")
            return False
    
    def test_combat_engine_initialization(self):
        """Teste l'initialisation du moteur de combat"""
        try:
            print("🔧 Test d'initialisation du moteur de combat...")
            
            # Création d'un héros de test
            test_hero = Hero(
                name="Héros Test",
                element="1",
                base_stats={"hp": 100, "attack": 50, "defense": 20},
                ability_name="",
                ability_description="",
                ability_cooldown=0
            )
            
            # Création de cartes de test
            test_cards = [
                Card("Carte Test 1", 1, "1", "sort", "Test effect"),
                Card("Carte Test 2", 2, "2", "créature", "Test effect")
            ]
            
            # Création d'unités de test
            test_units = [
                Unit("Unité Test 1", "1", {"hp": 50, "attack": 20, "defense": 10}, []),
                Unit("Unité Test 2", "2", {"hp": 60, "attack": 25, "defense": 15}, [])
            ]
            
            # Création des joueurs de test
            player1 = Player("Joueur 1", test_cards.copy(), test_hero, test_units.copy())
            player2 = Player("Joueur 2", test_cards.copy(), test_hero, test_units.copy())
            
            # Création d'un moteur de combat
            combat_engine = CombatEngine(player1, player2)
            
            self.results["success"].append("Moteur de combat initialisé avec succès")
            return True
            
        except Exception as e:
            self.results["errors"].append(f"Erreur d'initialisation du moteur de combat: {e}")
            traceback.print_exc()
            return False
    
    def test_ability_usage_simulation(self, ability_id: str):
        """Simule l'utilisation d'une capacité"""
        try:
            if ability_id not in self.effects_data.get("abilities", {}):
                return False
            
            ability_data = self.effects_data["abilities"][ability_id]
            
            # Simulation des vérifications de cooldown
            base_cooldown = ability_data.get("base_cooldown", 1)
            if base_cooldown < 0:
                self.results["warnings"].append(f"Capacité {ability_id}: cooldown négatif ({base_cooldown})")
            
            # Simulation des vérifications de dégâts
            damage = ability_data.get("damage", 0)
            if damage < 0:
                self.results["warnings"].append(f"Capacité {ability_id}: dégâts négatifs ({damage})")
            
            # Simulation des vérifications de cible
            target_type = ability_data.get("target_type", "")
            valid_targets = [
                "single_enemy", "all_enemies", "single_ally", "all_allies", 
                "self", "random_enemy", "random_ally", "chain_enemies",
                # Types de cible avancés/intentionnels
                "front_row", "random_multiple", "self_and_allies", "chain_random"
            ]
            
            if target_type not in valid_targets:
                self.results["warnings"].append(f"Capacité {ability_id}: type de cible invalide ({target_type})")
            
            return True
            
        except Exception as e:
            self.results["errors"].append(f"Capacité {ability_id}: erreur lors de la simulation - {e}")
            return False
    
    def run_comprehensive_tests(self):
        """Lance tous les tests de vérification"""
        print("🚀 Démarrage des tests de vérification complète...")
        
        # Test d'initialisation du moteur de combat
        if not self.test_combat_engine_initialization():
            print("❌ Échec de l'initialisation du moteur de combat")
            return
        
        # Récupération de toutes les capacités, passifs et effets
        all_abilities = set()
        all_passives = set()
        all_effects = set()
        
        # Capacités
        for hero_data in self._iter_entities(self.heroes_data):
            if isinstance(hero_data, dict) and "ability_ids" in hero_data:
                all_abilities.update(hero_data.get("ability_ids", []))
        
        for unit_data in self._iter_entities(self.units_data):
            if isinstance(unit_data, dict) and "ability_ids" in unit_data:
                all_abilities.update(unit_data.get("ability_ids", []))
        
        for card_data in self._iter_entities(self.cards_data):
            if isinstance(card_data, dict) and "ability_ids" in card_data:
                all_abilities.update(card_data.get("ability_ids", []))
        
        # Passifs
        for hero_data in self._iter_entities(self.heroes_data):
            if isinstance(hero_data, dict) and "passive_ids" in hero_data:
                all_passives.update(hero_data.get("passive_ids", []))
        
        for unit_data in self._iter_entities(self.units_data):
            if isinstance(unit_data, dict) and "passive_ids" in unit_data:
                all_passives.update(unit_data.get("passive_ids", []))
        
        # Effets (depuis la base de données)
        for section in ["base_effects", "chain_effects", "elemental_interactions", 
                       "special_combos", "elemental_attack_effects"]:
            if section in self.effects_data:
                all_effects.update(self.effects_data[section].keys())
        
        print(f"📊 Tests à effectuer:")
        print(f"   - {len(all_abilities)} capacités")
        print(f"   - {len(all_passives)} passifs")
        print(f"   - {len(all_effects)} effets")
        
        # Tests des capacités
        print("\n🔍 Test des capacités...")
        for ability_id in all_abilities:
            self.results["stats"]["total_tested"] += 1
            if self.test_ability_loading(ability_id):
                self.results["stats"]["successful"] += 1
                self.test_ability_usage_simulation(ability_id)
            else:
                self.results["stats"]["failed"] += 1
        
        # Tests des passifs
        print("\n🔍 Test des passifs...")
        for passive_id in all_passives:
            self.results["stats"]["total_tested"] += 1
            if self.test_passive_loading(passive_id):
                self.results["stats"]["successful"] += 1
            else:
                self.results["stats"]["failed"] += 1
        
        # Tests des effets
        print("\n🔍 Test des effets...")
        for effect_id in all_effects:
            self.results["stats"]["total_tested"] += 1
            if self.test_effect_loading(effect_id):
                self.results["stats"]["successful"] += 1
            else:
                self.results["stats"]["failed"] += 1
        
        self.results["stats"]["warnings"] = len(self.results["warnings"])
        
        # Affichage des résultats
        self.display_results()
    
    def display_results(self):
        """Affiche les résultats des tests"""
        print("\n" + "="*60)
        print("📋 RÉSULTATS DES TESTS DE VÉRIFICATION")
        print("="*60)
        
        stats = self.results["stats"]
        print(f"📊 Statistiques:")
        print(f"   - Total testé: {stats['total_tested']}")
        print(f"   - Succès: {stats['successful']}")
        print(f"   - Échecs: {stats['failed']}")
        print(f"   - Avertissements: {stats['warnings']}")
        
        if stats['total_tested'] > 0:
            success_rate = (stats['successful'] / stats['total_tested']) * 100
            print(f"   - Taux de succès: {success_rate:.1f}%")
        
        # Affichage des succès
        if self.results["success"]:
            print(f"\n✅ Succès ({len(self.results['success'])}):")
            for success in self.results["success"]:
                print(f"   - {success}")
        
        # Affichage des avertissements
        if self.results["warnings"]:
            print(f"\n⚠️  Avertissements ({len(self.results['warnings'])}):")
            for warning in self.results["warnings"][:10]:  # Limite à 10 pour éviter le spam
                print(f"   - {warning}")
            if len(self.results["warnings"]) > 10:
                print(f"   ... et {len(self.results['warnings']) - 10} autres")
        
        # Affichage des erreurs
        if self.results["errors"]:
            print(f"\n❌ Erreurs ({len(self.results['errors'])}):")
            for error in self.results["errors"][:10]:  # Limite à 10 pour éviter le spam
                print(f"   - {error}")
            if len(self.results["errors"]) > 10:
                print(f"   ... et {len(self.results['errors']) - 10} autres")
        
        # Recommandations
        print(f"\n💡 Recommandations:")
        if stats['failed'] > 0:
            print(f"   - Corriger les {stats['failed']} erreurs identifiées")
        if stats['warnings'] > 0:
            print(f"   - Examiner les {stats['warnings']} avertissements")
        if stats['successful'] == stats['total_tested']:
            print(f"   - 🎉 Tous les tests sont passés avec succès!")
        
        print("="*60)

def main():
    """Fonction principale"""
    print("🎮 Script de vérification des capacités et effets en combat")
    print("="*60)
    
    try:
        tester = CombatVerificationTester()
        tester.run_comprehensive_tests()
        
    except KeyboardInterrupt:
        print("\n⏹️  Test interrompu par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur fatale: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
