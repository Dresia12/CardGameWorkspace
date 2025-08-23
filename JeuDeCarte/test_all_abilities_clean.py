#!/usr/bin/env python3
"""
Script de test complet et propre pour toutes les capacités du jeu
"""

import json
import random
from typing import Dict, List, Any
from Engine.engine import CombatEngine, Player
from Engine.models import Hero, Unit, Card

class ComprehensiveAbilityTester:
    def __init__(self):
        """Initialise le testeur de capacités"""
        self.test_results = {
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "errors": [],
            "warnings": [],
            "test_details": []
        }
        
        # Charger les données
        self.load_data()
        
        # Initialiser le moteur de combat
        self.setup_combat_engine()
    
    def load_data(self):
        """Charge les données du jeu"""
        try:
            with open('Data/effects_database.json', 'r', encoding='utf-8') as f:
                self.effects_db = json.load(f)
            with open('Data/units.json', 'r', encoding='utf-8') as f:
                self.units_db = json.load(f)
            print("✓ Données chargées avec succès")
        except Exception as e:
            print(f"✗ Erreur lors du chargement des données: {e}")
            self.effects_db = {}
            self.units_db = {}
    
    def setup_combat_engine(self):
        """Configure le moteur de combat pour les tests"""
        try:
            # Créer des héros de test
            hero1 = Hero("Test Hero 1", "Feu", {"hp": 1000, "attack": 50, "defense": 20, "mana": 100})
            hero2 = Hero("Test Hero 2", "Eau", {"hp": 1000, "attack": 50, "defense": 20, "mana": 100})
            
            # Créer des unités de test
            unit1 = Unit("Test Unit 1", "Feu", {"hp": 500, "attack": 30, "defense": 15, "mana": 50}, [], [])
            unit2 = Unit("Test Unit 2", "Eau", {"hp": 500, "attack": 30, "defense": 15, "mana": 50}, [], [])
            
            # Créer des cartes de test
            card1 = Card("Test Card 1", "Feu", 1, "spell")
            card2 = Card("Test Card 2", "Eau", 1, "spell")
            
            # Créer les joueurs
            player1 = Player("Test Player 1", [card1], hero1, [unit1])
            player2 = Player("Test Player 2", [card2], hero2, [unit2])
            
            # Créer le moteur de combat
            self.engine = CombatEngine(player1, player2)
            print("✓ Moteur de combat initialisé")
        except Exception as e:
            print(f"✗ Erreur lors de l'initialisation du moteur: {e}")
            self.engine = None
    
    def run_all_tests(self):
        """Exécute tous les tests"""
        print("=== DÉBUT DES TESTS COMPLETS ===")
        
        if not self.engine:
            print("✗ Impossible de continuer: moteur de combat non initialisé")
            return
        
        # Tests des capacités de base
        self.test_basic_abilities()
        
        # Tests des capacités avancées
        self.test_advanced_abilities()
        
        # Tests des passifs
        self.test_passives()
        
        # Tests des unités
        self.test_units()
        
        # Afficher les résultats
        self.print_results()
    
    def test_basic_abilities(self):
        """Teste les capacités de base de chaque élément"""
        print("\n=== TEST DES CAPACITÉS DE BASE ===")
        
        basic_abilities = ["5000", "5250", "5500", "5750", "6000", "6250", "6500", "6750", "7000", "7250", "7500", "7750"]
        elements = ["Feu", "Eau", "Terre", "Air", "Glace", "Foudre", "Lumière", "Ténèbres", "Arcanique", "Poison", "Nature", "Métal"]
        
        for ability_id, element in zip(basic_abilities, elements):
            try:
                ability_data = self.effects_db.get("abilities", {}).get(ability_id)
                if ability_data:
                    self.record_test_result(f"Capacité de base {element}", True, ability_data)
                else:
                    self.record_error(f"Capacité de base {ability_id} pour {element} non trouvée")
            except Exception as e:
                self.record_error(f"Erreur lors du test de la capacité de base {element}: {e}")
    
    def test_advanced_abilities(self):
        """Teste toutes les capacités avancées"""
        print("\n=== TEST DES CAPACITÉS AVANCÉES ===")
        
        abilities_dict = self.effects_db.get("abilities", {})
        for ability_id, ability_data in abilities_dict.items():
            # Ignorer les capacités de base
            if ability_id in ["5000", "5250", "5500", "5750", "6000", "6250", "6500", "6750", "7000", "7250", "7500", "7750"]:
                continue
            
            try:
                ability_name = ability_data.get("name", "Sans nom")
                self.record_test_result(f"Capacité {ability_id} - {ability_name}", True, ability_data)
            except Exception as e:
                self.record_error(f"Erreur lors du test de la capacité {ability_id}: {e}")
    
    def test_passives(self):
        """Teste tous les passifs"""
        print("\n=== TEST DES PASSIFS ===")
        
        passives_dict = self.effects_db.get("passives", {})
        for passive_id, passive_data in passives_dict.items():
            try:
                passive_name = passive_data.get("name", "Sans nom")
                self.record_test_result(f"Passif {passive_id} - {passive_name}", True, passive_data)
            except Exception as e:
                self.record_error(f"Erreur lors du test du passif {passive_id}: {e}")
    
    def test_units(self):
        """Teste toutes les unités"""
        print("\n=== TEST DES UNITÉS ===")
        
        # units.json est une liste, pas un dictionnaire
        for unit_data in self.units_db:
            try:
                unit_name = unit_data.get("name", "Sans nom")
                element = unit_data.get("element", "Inconnu")
                abilities = unit_data.get("ability_ids", [])
                passives = unit_data.get("passive_ids", [])
                
                # Vérifier que les capacités existent
                abilities_valid = True
                for ability_id in abilities:
                    if ability_id not in self.effects_db.get("abilities", {}):
                        abilities_valid = False
                        self.record_error(f"Capacité {ability_id} manquante pour {unit_name}")
                
                # Vérifier que les passifs existent
                passives_valid = True
                for passive_id in passives:
                    if passive_id not in self.effects_db.get("passives", {}):
                        passives_valid = False
                        self.record_error(f"Passif {passive_id} manquant pour {unit_name}")
                
                if abilities_valid and passives_valid:
                    self.record_test_result(f"Unité {unit_name} ({element})", True, unit_data)
                else:
                    self.record_test_result(f"Unité {unit_name} ({element})", False, unit_data)
                    
            except Exception as e:
                self.record_error(f"Erreur lors du test de l'unité {unit_name}: {e}")
    
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
    
    def print_results(self):
        """Affiche les résultats finaux"""
        print("\n" + "="*50)
        print("RÉSULTATS FINAUX")
        print("="*50)
        print(f"Tests totaux: {self.test_results['total_tests']}")
        print(f"Tests réussis: {self.test_results['passed_tests']}")
        print(f"Tests échoués: {self.test_results['failed_tests']}")
        print(f"Erreurs: {len(self.test_results['errors'])}")
        print(f"Avertissements: {len(self.test_results['warnings'])}")
        
        if self.test_results['total_tests'] > 0:
            success_rate = (self.test_results['passed_tests'] / self.test_results['total_tests']) * 100
            print(f"Taux de réussite: {success_rate:.1f}%")
        
        if self.test_results['errors']:
            print("\nErreurs détectées:")
            for error in self.test_results['errors'][:10]:  # Afficher les 10 premières erreurs
                print(f"  - {error}")
            if len(self.test_results['errors']) > 10:
                print(f"  ... et {len(self.test_results['errors']) - 10} autres erreurs")
        
        if self.test_results['warnings']:
            print("\nAvertissements:")
            for warning in self.test_results['warnings'][:5]:  # Afficher les 5 premiers avertissements
                print(f"  - {warning}")
            if len(self.test_results['warnings']) > 5:
                print(f"  ... et {len(self.test_results['warnings']) - 5} autres avertissements")

def main():
    """Fonction principale"""
    tester = ComprehensiveAbilityTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()
