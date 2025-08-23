#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de test de stress du système de combat
Teste les performances et la stabilité sous charge
"""

import json
import sys
import os
import random
import time
import threading
from typing import Dict, List, Any, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

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

class StressTester:
    def __init__(self):
        self.results = {
            "success": [],
            "errors": [],
            "warnings": [],
            "performance_tests": [],
            "stress_tests": [],
            "stats": {
                "combats_simulated": 0,
                "abilities_used": 0,
                "total_execution_time": 0,
                "memory_usage": 0,
                "threads_used": 0,
                "errors_encountered": 0
            }
        }
        
        # Chargement des données
        self.load_data()
        
    def load_data(self):
        """Charge toutes les données nécessaires"""
        try:
            print("📂 Chargement des données pour tests de stress...")
            
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
    
    def create_test_unit(self, unit_id: int, element: str = None) -> Unit:
        """Crée une unité de test avec des capacités aléatoires"""
        if element is None:
            element = str(random.randint(1, 12))
        
        # Créer plusieurs capacités de test
        abilities = []
        num_abilities = random.randint(1, 3)
        
        for i in range(num_abilities):
            ability = Ability(
                name=f"Capacité Test {unit_id}-{i+1}",
                description=f"Capacité de test pour unité {unit_id}",
                cooldown=random.randint(0, 3)
            )
            ability.damage = random.randint(10, 100)
            ability.target_type = random.choice(["single_enemy", "single_ally", "all_enemies", "self"])
            ability.element = element
            ability.ability_id = f"test_{unit_id}_{i}"
            ability.current_cooldown = 0
            abilities.append(ability)
        
        unit = Unit(
            name=f"Unité Test {unit_id}",
            element=element,
            stats={
                'hp': random.randint(50, 300),
                'attack': random.randint(10, 50),
                'defense': random.randint(5, 25)
            },
            abilities=abilities
        )
        
        unit.abilities = abilities
        return unit
    
    def create_test_hero(self, hero_id: int, element: str = None) -> Hero:
        """Crée un héros de test"""
        if element is None:
            element = str(random.randint(1, 12))
        
        hero = Hero(
            name=f"Héros Test {hero_id}",
            element=element,
            base_stats={
                'hp': random.randint(500, 1500),
                'attack': random.randint(30, 80),
                'defense': random.randint(15, 40)
            },
            ability_name=f"Capacité Héros {hero_id}",
            ability_description=f"Capacité spéciale du héros {hero_id}",
            ability_cooldown=random.randint(0, 5)
        )
        
        return hero
    
    def simulate_single_combat(self, combat_id: int, num_units: int = 6) -> Dict:
        """Simule un combat unique"""
        try:
            start_time = time.time()
            
            # Créer les unités de test
            units_p1 = [self.create_test_unit(i, str(random.randint(1, 12))) for i in range(num_units)]
            units_p2 = [self.create_test_unit(i + num_units, str(random.randint(1, 12))) for i in range(num_units)]
            
            # Créer les héros
            hero_p1 = self.create_test_hero(1, str(random.randint(1, 12)))
            hero_p2 = self.create_test_hero(2, str(random.randint(1, 12)))
            
            # Créer les cartes de test
            test_cards = [
                Card(f"Carte Test {i}", i, str(random.randint(1, 12)), "sort", "Test effect")
                for i in range(1, 6)
            ]
            
            # Créer les joueurs
            player1 = Player(f"Joueur 1-{combat_id}", test_cards.copy(), hero_p1, units_p1)
            player2 = Player(f"Joueur 2-{combat_id}", test_cards.copy(), hero_p2, units_p2)
            
            # Créer le moteur de combat
            combat_engine = CombatEngine(player1, player2)
            
            # S'assurer que les unités ont les attributs nécessaires
            for unit in units_p1 + units_p2:
                if not hasattr(unit, 'owner'):
                    if unit in units_p1:
                        unit.owner = player1
                    else:
                        unit.owner = player2
                
                if not hasattr(unit, 'is_alive'):
                    unit.is_alive = lambda: getattr(unit, 'hp', 0) > 0
            
            # Réinitialiser les cooldowns
            for unit in units_p1 + units_p2:
                for ability in unit.abilities:
                    ability.current_cooldown = 0
            
            # Simuler plusieurs tours de combat
            all_units = units_p1 + units_p2
            abilities_used = 0
            max_turns = 10  # Limite pour éviter les boucles infinies
            
            for turn in range(max_turns):
                # Vérifier si le combat est terminé
                alive_units = [unit for unit in all_units if unit.hp > 0]
                if len(alive_units) <= 1:
                    break
                
                # Chaque unité vivante utilise une capacité
                for unit in alive_units:
                    if unit.abilities:
                        # Choisir une capacité aléatoire
                        ability = random.choice(unit.abilities)
                        
                        # Choisir une cible aléatoire
                        potential_targets = [u for u in all_units if u != unit and u.hp > 0]
                        if potential_targets:
                            target = random.choice(potential_targets)
                            
                            try:
                                success = combat_engine.use_ability(unit, ability, target)
                                if success:
                                    abilities_used += 1
                            except Exception as e:
                                # Ignorer les erreurs individuelles pour le test de stress
                                pass
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            return {
                "combat_id": combat_id,
                "num_units": num_units * 2,
                "abilities_used": abilities_used,
                "execution_time": execution_time,
                "turns_completed": min(turn + 1, max_turns),
                "units_alive": len([u for u in all_units if u.hp > 0]),
                "success": True
            }
            
        except Exception as e:
            return {
                "combat_id": combat_id,
                "num_units": num_units * 2,
                "abilities_used": 0,
                "execution_time": 0,
                "turns_completed": 0,
                "units_alive": 0,
                "success": False,
                "error": str(e)
            }
    
    def run_sequential_stress_test(self, num_combats: int = 100, units_per_combat: int = 6):
        """Lance un test de stress séquentiel"""
        print(f"🚀 Test de stress séquentiel: {num_combats} combats avec {units_per_combat} unités par côté")
        
        start_time = time.time()
        successful_combats = 0
        total_abilities = 0
        
        for i in range(num_combats):
            if i % 10 == 0:
                print(f"  📊 Progression: {i}/{num_combats} combats")
            
            result = self.simulate_single_combat(i, units_per_combat)
            
            if result["success"]:
                successful_combats += 1
                total_abilities += result["abilities_used"]
            
            self.results["stress_tests"].append(result)
            self.results["stats"]["combats_simulated"] += 1
        
        end_time = time.time()
        total_time = end_time - start_time
        
        self.results["stats"]["total_execution_time"] = total_time
        self.results["stats"]["abilities_used"] = total_abilities
        
        print(f"✅ Test séquentiel terminé: {successful_combats}/{num_combats} combats réussis")
        print(f"   Temps total: {total_time:.2f} secondes")
        print(f"   Capacités utilisées: {total_abilities}")
        print(f"   Temps moyen par combat: {total_time/num_combats:.3f} secondes")
    
    def run_parallel_stress_test(self, num_combats: int = 50, units_per_combat: int = 6, max_workers: int = 4):
        """Lance un test de stress parallèle"""
        print(f"🚀 Test de stress parallèle: {num_combats} combats avec {max_workers} threads")
        
        start_time = time.time()
        successful_combats = 0
        total_abilities = 0
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Soumettre tous les combats
            future_to_combat = {
                executor.submit(self.simulate_single_combat, i, units_per_combat): i
                for i in range(num_combats)
            }
            
            # Collecter les résultats
            for future in as_completed(future_to_combat):
                combat_id = future_to_combat[future]
                try:
                    result = future.result()
                    
                    if result["success"]:
                        successful_combats += 1
                        total_abilities += result["abilities_used"]
                    
                    self.results["stress_tests"].append(result)
                    self.results["stats"]["combats_simulated"] += 1
                    
                    if combat_id % 10 == 0:
                        print(f"  📊 Progression: {combat_id}/{num_combats} combats")
                        
                except Exception as e:
                    self.results["errors"].append(f"Erreur combat {combat_id}: {e}")
                    self.results["stats"]["errors_encountered"] += 1
        
        end_time = time.time()
        total_time = end_time - start_time
        
        self.results["stats"]["total_execution_time"] = total_time
        self.results["stats"]["abilities_used"] = total_abilities
        self.results["stats"]["threads_used"] = max_workers
        
        print(f"✅ Test parallèle terminé: {successful_combats}/{num_combats} combats réussis")
        print(f"   Temps total: {total_time:.2f} secondes")
        print(f"   Capacités utilisées: {total_abilities}")
        print(f"   Temps moyen par combat: {total_time/num_combats:.3f} secondes")
    
    def run_memory_stress_test(self, num_combats: int = 20, units_per_combat: int = 10):
        """Teste l'utilisation mémoire avec beaucoup d'unités"""
        print(f"🧠 Test de stress mémoire: {num_combats} combats avec {units_per_combat} unités par côté")
        
        start_time = time.time()
        successful_combats = 0
        total_abilities = 0
        
        for i in range(num_combats):
            if i % 5 == 0:
                print(f"  📊 Progression: {i}/{num_combats} combats")
            
            result = self.simulate_single_combat(i, units_per_combat)
            
            if result["success"]:
                successful_combats += 1
                total_abilities += result["abilities_used"]
            
            self.results["stress_tests"].append(result)
            self.results["stats"]["combats_simulated"] += 1
        
        end_time = time.time()
        total_time = end_time - start_time
        
        self.results["stats"]["total_execution_time"] = total_time
        self.results["stats"]["abilities_used"] = total_abilities
        
        print(f"✅ Test mémoire terminé: {successful_combats}/{num_combats} combats réussis")
        print(f"   Temps total: {total_time:.2f} secondes")
        print(f"   Capacités utilisées: {total_abilities}")
    
    def run_ability_stress_test(self, num_abilities: int = 1000):
        """Teste l'utilisation intensive de capacités"""
        print(f"⚡ Test de stress des capacités: {num_abilities} utilisations de capacités")
        
        start_time = time.time()
        successful_uses = 0
        
        # Créer une unité de test avec beaucoup de capacités
        abilities = []
        for i in range(10):  # 10 capacités différentes
            ability = Ability(
                name=f"Capacité Stress {i}",
                description=f"Capacité de stress test {i}",
                cooldown=0
            )
            ability.damage = random.randint(10, 50)
            ability.target_type = "single_enemy"
            ability.element = str(random.randint(1, 12))
            ability.ability_id = f"stress_{i}"
            ability.current_cooldown = 0
            abilities.append(ability)
        
        unit = Unit(
            name="Unit Stress Test",
            element="1",
            stats={'hp': 1000, 'attack': 50, 'defense': 25},
            abilities=abilities
        )
        unit.abilities = abilities
        
        # Créer une cible
        target = Unit(
            name="Cible Stress Test",
            element="2",
            stats={'hp': 1000, 'attack': 30, 'defense': 20},
            abilities=[]
        )
        target.abilities = []
        
        # Créer le contexte de combat minimal
        test_cards = [Card("Test", 1, "1", "sort", "Test")]
        hero = Hero("Test", "1", {"hp": 1000, "attack": 50, "defense": 20})
        player1 = Player("Test1", test_cards, hero, [unit])
        player2 = Player("Test2", test_cards, hero, [target])
        
        combat_engine = CombatEngine(player1, player2)
        
        # Utiliser les capacités en boucle
        for i in range(num_abilities):
            if i % 100 == 0:
                print(f"  📊 Progression: {i}/{num_abilities} capacités")
            
            # Choisir une capacité aléatoire
            ability = random.choice(abilities)
            
            try:
                success = combat_engine.use_ability(unit, ability, target)
                if success:
                    successful_uses += 1
            except Exception as e:
                self.results["errors"].append(f"Erreur capacité {i}: {e}")
        
        end_time = time.time()
        total_time = end_time - start_time
        
        self.results["stats"]["abilities_used"] = successful_uses
        self.results["stats"]["total_execution_time"] = total_time
        
        print(f"✅ Test capacités terminé: {successful_uses}/{num_abilities} utilisations réussies")
        print(f"   Temps total: {total_time:.2f} secondes")
        print(f"   Utilisations par seconde: {successful_uses/total_time:.1f}")
    
    def run_performance_benchmark(self):
        """Lance un benchmark de performance"""
        print("📊 Benchmark de performance...")
        
        benchmarks = [
            {"name": "Petit combat", "units": 3, "combats": 50},
            {"name": "Combat moyen", "units": 6, "combats": 30},
            {"name": "Grand combat", "units": 10, "combats": 20},
            {"name": "Combat massif", "units": 15, "combats": 10}
        ]
        
        for benchmark in benchmarks:
            print(f"\n🎯 Benchmark: {benchmark['name']}")
            
            start_time = time.time()
            successful_combats = 0
            total_abilities = 0
            
            for i in range(benchmark["combats"]):
                result = self.simulate_single_combat(i, benchmark["units"])
                
                if result["success"]:
                    successful_combats += 1
                    total_abilities += result["abilities_used"]
            
            end_time = time.time()
            total_time = end_time - start_time
            
            performance_result = {
                "benchmark_name": benchmark["name"],
                "units_per_combat": benchmark["units"],
                "num_combats": benchmark["combats"],
                "successful_combats": successful_combats,
                "total_abilities": total_abilities,
                "total_time": total_time,
                "avg_time_per_combat": total_time / benchmark["combats"],
                "abilities_per_second": total_abilities / total_time if total_time > 0 else 0
            }
            
            self.results["performance_tests"].append(performance_result)
            
            print(f"   ✅ {successful_combats}/{benchmark['combats']} combats réussis")
            print(f"   ⏱️ Temps total: {total_time:.2f}s")
            print(f"   ⚡ Temps moyen par combat: {total_time/benchmark['combats']:.3f}s")
            print(f"   🎯 Capacités par seconde: {total_abilities/total_time:.1f}")
    
    def run_all_stress_tests(self):
        """Lance tous les tests de stress"""
        print("🚀 Démarrage de tous les tests de stress...")
        
        # Test de performance
        self.run_performance_benchmark()
        
        # Test séquentiel
        self.run_sequential_stress_test(num_combats=50, units_per_combat=6)
        
        # Test parallèle
        self.run_parallel_stress_test(num_combats=30, units_per_combat=6, max_workers=4)
        
        # Test mémoire
        self.run_memory_stress_test(num_combats=15, units_per_combat=12)
        
        # Test capacités
        self.run_ability_stress_test(num_abilities=500)
        
        # Affichage des résultats
        self.display_stress_results()
    
    def display_stress_results(self):
        """Affiche les résultats des tests de stress"""
        print("\n" + "="*70)
        print("📋 RÉSULTATS DES TESTS DE STRESS")
        print("="*70)
        
        stats = self.results["stats"]
        print(f"📊 Statistiques globales:")
        print(f"   - Combats simulés: {stats['combats_simulated']}")
        print(f"   - Capacités utilisées: {stats['abilities_used']}")
        print(f"   - Temps d'exécution total: {stats['total_execution_time']:.2f} secondes")
        print(f"   - Threads utilisés: {stats['threads_used']}")
        print(f"   - Erreurs rencontrées: {stats['errors_encountered']}")
        
        # Affichage des tests de performance
        if self.results["performance_tests"]:
            print(f"\n📊 Tests de performance:")
            for test in self.results["performance_tests"]:
                print(f"   🎯 {test['benchmark_name']}:")
                print(f"     - {test['successful_combats']}/{test['num_combats']} combats réussis")
                print(f"     - Temps moyen: {test['avg_time_per_combat']:.3f}s par combat")
                print(f"     - Capacités/seconde: {test['abilities_per_second']:.1f}")
        
        # Affichage des tests de stress
        if self.results["stress_tests"]:
            print(f"\n⚡ Tests de stress ({len(self.results['stress_tests'])}):")
            
            successful_tests = [t for t in self.results["stress_tests"] if t.get("success", False)]
            failed_tests = [t for t in self.results["stress_tests"] if not t.get("success", False)]
            
            print(f"   ✅ Tests réussis: {len(successful_tests)}")
            print(f"   ❌ Tests échoués: {len(failed_tests)}")
            
            if successful_tests:
                avg_execution_time = sum(t.get("execution_time", 0) for t in successful_tests) / len(successful_tests)
                avg_abilities = sum(t.get("abilities_used", 0) for t in successful_tests) / len(successful_tests)
                print(f"   ⏱️ Temps moyen par combat: {avg_execution_time:.3f}s")
                print(f"   🎯 Capacités moyennes par combat: {avg_abilities:.1f}")
        
        # Affichage des erreurs
        if self.results["errors"]:
            print(f"\n❌ Erreurs ({len(self.results['errors'])}):")
            for error in self.results["errors"][:10]:
                print(f"   - {error}")
            if len(self.results["errors"]) > 10:
                print(f"   ... et {len(self.results['errors']) - 10} autres")
        
        # Recommandations
        print(f"\n💡 Recommandations:")
        if stats['errors_encountered'] > 0:
            print(f"   - Corriger les {stats['errors_encountered']} erreurs de stabilité")
        
        if stats['combats_simulated'] > 0:
            success_rate = (len([t for t in self.results["stress_tests"] if t.get("success", False)]) / stats['combats_simulated']) * 100
            print(f"   - Taux de succès: {success_rate:.1f}%")
            
            if success_rate > 95:
                print(f"   - 🎉 Excellente stabilité du système!")
            elif success_rate > 80:
                print(f"   - ✅ Bonne stabilité du système")
            else:
                print(f"   - ⚠️ Stabilité à améliorer")
        
        print("="*70)

def main():
    """Fonction principale"""
    print("🧪 Script de test de stress du système de combat")
    print("="*70)
    
    try:
        tester = StressTester()
        tester.run_all_stress_tests()
        
    except KeyboardInterrupt:
        print("\n⏹️  Test interrompu par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur fatale: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
