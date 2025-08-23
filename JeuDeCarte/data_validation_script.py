#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de validation des données du jeu
Vérifie la cohérence des fichiers JSON et identifie les problèmes potentiels
"""

import json
import sys
import os
from typing import Dict, List, Any, Set
from collections import defaultdict

class DataValidator:
    def __init__(self):
        self.results = {
            "errors": [],
            "warnings": [],
            "success": [],
            "stats": {
                "abilities_checked": 0,
                "units_checked": 0,
                "heroes_checked": 0,
                "cards_checked": 0,
                "passives_checked": 0,
                "effects_checked": 0
            }
        }
        
        # Mapping des éléments
        self.element_names = {
            "1": "Feu", "2": "Eau", "3": "Terre", "4": "Air", 
            "5": "Glace", "6": "Foudre", "7": "Lumiere", "8": "Tenebres",
            "9": "Poison", "10": "Neant", "11": "Arcanique", "12": "Neutre"
        }
        
        # Chargement des données
        self.load_data()
        
    def load_data(self):
        """Charge toutes les données JSON"""
        try:
            print("📂 Chargement des données pour validation...")
            
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
            sys.exit(1)
    
    def _iter_entities(self, data):
        """Permet d'itérer sur des données JSON qui peuvent être une liste ou un dict."""
        if isinstance(data, dict):
            return data.values()
        if isinstance(data, list):
            return data
        return []
    
    def validate_abilities(self):
        """Valide toutes les capacités"""
        print("\n🔍 Validation des capacités...")
        
        abilities = self.effects_data.get("abilities", {})
        self.results["stats"]["abilities_checked"] = len(abilities)
        
        # Collecter tous les IDs de capacités référencés
        referenced_ability_ids = set()
        
        # Vérifier les références dans les unités
        for unit_data in self._iter_entities(self.units_data):
            if isinstance(unit_data, dict) and "ability_ids" in unit_data:
                for ability_id in unit_data["ability_ids"]:
                    referenced_ability_ids.add(str(ability_id))
        
        # Vérifier les références dans les héros
        for hero_data in self._iter_entities(self.heroes_data):
            if isinstance(hero_data, dict) and "ability_ids" in hero_data:
                for ability_id in hero_data["ability_ids"]:
                    referenced_ability_ids.add(str(ability_id))
        
        # Vérifier chaque capacité
        for ability_id, ability_data in abilities.items():
            self.validate_single_ability(ability_id, ability_data)
        
        # Vérifier les capacités référencées mais inexistantes
        missing_abilities = referenced_ability_ids - set(abilities.keys())
        if missing_abilities:
            for missing_id in missing_abilities:
                self.results["errors"].append(f"Capacité {missing_id} référencée mais inexistante")
        
        # Vérifier les capacités orphelines (non référencées)
        orphan_abilities = set(abilities.keys()) - referenced_ability_ids
        if orphan_abilities:
            for orphan_id in orphan_abilities:
                self.results["warnings"].append(f"Capacité {orphan_id} ({abilities[orphan_id].get('name', 'N/A')}) non référencée")
    
    def validate_single_ability(self, ability_id, ability_data):
        """Valide une capacité individuelle"""
        # Champs requis
        required_fields = ["name", "element", "base_cooldown", "target_type"]
        for field in required_fields:
            if field not in ability_data:
                self.results["errors"].append(f"Capacité {ability_id}: champ '{field}' manquant")
        
        # Vérifications spécifiques
        if "base_cooldown" in ability_data:
            cooldown = ability_data["base_cooldown"]
            if not isinstance(cooldown, int) or cooldown < 0:
                self.results["errors"].append(f"Capacité {ability_id}: cooldown invalide ({cooldown})")
        
        if "damage" in ability_data:
            damage = ability_data["damage"]
            if not isinstance(damage, (int, float)) or damage < 0:
                self.results["errors"].append(f"Capacité {ability_id}: dégâts invalides ({damage})")
        
        # Vérifier les types de cible valides
        valid_target_types = [
            "self", "single_enemy", "single_ally", "all_enemies", "all_allies",
            "random_enemy", "random_ally", "front_row", "random_multiple",
            "self_and_allies", "chain_enemies", "chain_random"
        ]
        
        if "target_type" in ability_data:
            target_type = ability_data["target_type"]
            if target_type not in valid_target_types:
                self.results["warnings"].append(f"Capacité {ability_id}: type de cible inconnu ({target_type})")
        
        # Vérifier les éléments valides
        valid_elements = list(self.element_names.keys()) + list(self.element_names.values())
        if "element" in ability_data:
            element = str(ability_data["element"])
            if element not in valid_elements:
                self.results["warnings"].append(f"Capacité {ability_id}: élément invalide ({element})")
    
    def validate_units(self):
        """Valide toutes les unités"""
        print("\n🔍 Validation des unités...")
        
        units = self._iter_entities(self.units_data)
        self.results["stats"]["units_checked"] = len(units)
        
        for unit_data in units:
            if isinstance(unit_data, dict):
                self.validate_single_unit(unit_data)
    
    def validate_single_unit(self, unit_data):
        """Valide une unité individuelle"""
        unit_id = unit_data.get("id", "N/A")
        unit_name = unit_data.get("name", "N/A")
        
        # Champs requis
        required_fields = ["name", "element", "hp", "attack", "defense"]
        for field in required_fields:
            if field not in unit_data:
                self.results["errors"].append(f"Unité {unit_id} ({unit_name}): champ '{field}' manquant")
        
        # Vérifications des stats
        for stat in ["hp", "attack", "defense"]:
            if stat in unit_data:
                value = unit_data[stat]
                if not isinstance(value, (int, float)) or value < 0:
                    self.results["errors"].append(f"Unité {unit_id} ({unit_name}): {stat} invalide ({value})")
        
        # Vérifier l'élément
        if "element" in unit_data:
            element = unit_data["element"]
            valid_elements = list(self.element_names.keys()) + list(self.element_names.values())
            if element not in valid_elements:
                self.results["errors"].append(f"Unité {unit_id} ({unit_name}): élément invalide ({element})")
        
        # Vérifier les capacités référencées
        if "ability_ids" in unit_data:
            ability_ids = unit_data["ability_ids"]
            if not isinstance(ability_ids, list):
                self.results["errors"].append(f"Unité {unit_id} ({unit_name}): ability_ids doit être une liste")
            else:
                for ability_id in ability_ids:
                    if str(ability_id) not in self.effects_data.get("abilities", {}):
                        self.results["errors"].append(f"Unité {unit_id} ({unit_name}): capacité {ability_id} inexistante")
    
    def validate_heroes(self):
        """Valide tous les héros"""
        print("\n🔍 Validation des héros...")
        
        heroes = self._iter_entities(self.heroes_data)
        self.results["stats"]["heroes_checked"] = len(heroes)
        
        for hero_data in heroes:
            if isinstance(hero_data, dict):
                self.validate_single_hero(hero_data)
    
    def validate_single_hero(self, hero_data):
        """Valide un héros individuel"""
        hero_id = hero_data.get("id", "N/A")
        hero_name = hero_data.get("name", "N/A")
        
        # Champs requis
        required_fields = ["name", "element"]
        for field in required_fields:
            if field not in hero_data:
                self.results["errors"].append(f"Héros {hero_id} ({hero_name}): champ '{field}' manquant")
        
        # Vérifier base_stats
        if "base_stats" not in hero_data:
            self.results["errors"].append(f"Héros {hero_id} ({hero_name}): champ 'base_stats' manquant")
        else:
            base_stats = hero_data["base_stats"]
            required_stats = ["hp", "attack", "defense"]
            for stat in required_stats:
                if stat not in base_stats:
                    self.results["errors"].append(f"Héros {hero_id} ({hero_name}): stat '{stat}' manquante dans base_stats")
                elif not isinstance(base_stats[stat], (int, float)) or base_stats[stat] <= 0:
                    self.results["errors"].append(f"Héros {hero_id} ({hero_name}): {stat} invalide ({base_stats[stat]})")
        
        # Vérifier l'élément
        if "element" in hero_data:
            element = hero_data["element"]
            valid_elements = list(self.element_names.keys()) + list(self.element_names.values())
            if element not in valid_elements:
                self.results["errors"].append(f"Héros {hero_id} ({hero_name}): élément invalide ({element})")
        
        # Vérifier les capacités référencées
        if "ability_ids" in hero_data:
            ability_ids = hero_data["ability_ids"]
            if not isinstance(ability_ids, list):
                self.results["errors"].append(f"Héros {hero_id} ({hero_name}): ability_ids doit être une liste")
            else:
                for ability_id in ability_ids:
                    if str(ability_id) not in self.effects_data.get("abilities", {}):
                        self.results["errors"].append(f"Héros {hero_id} ({hero_name}): capacité {ability_id} inexistante")
    
    def validate_passives(self):
        """Valide tous les passifs"""
        print("\n🔍 Validation des passifs...")
        
        passives = self.effects_data.get("passives", {})
        self.results["stats"]["passives_checked"] = len(passives)
        
        for passive_id, passive_data in passives.items():
            self.validate_single_passive(passive_id, passive_data)
    
    def validate_single_passive(self, passive_id, passive_data):
        """Valide un passif individuel"""
        # Champs requis
        required_fields = ["name", "description"]
        for field in required_fields:
            if field not in passive_data:
                self.results["errors"].append(f"Passif {passive_id}: champ '{field}' manquant")
        
        # Vérifier les effets
        if "effects" in passive_data:
            effects = passive_data["effects"]
            if not isinstance(effects, list):
                self.results["errors"].append(f"Passif {passive_id}: effects doit être une liste")
    
    def validate_effects(self):
        """Valide tous les effets"""
        print("\n🔍 Validation des effets...")
        
        effects = self.effects_data.get("effects", {})
        self.results["stats"]["effects_checked"] = len(effects)
        
        for effect_id, effect_data in effects.items():
            self.validate_single_effect(effect_id, effect_data)
    
    def validate_single_effect(self, effect_id, effect_data):
        """Valide un effet individuel"""
        # Champs requis
        required_fields = ["name", "description"]
        for field in required_fields:
            if field not in effect_data:
                self.results["errors"].append(f"Effet {effect_id}: champ '{field}' manquant")
        
        # Vérifier la durée
        if "default_duration" in effect_data:
            duration = effect_data["default_duration"]
            if not isinstance(duration, int) or duration < 0:
                self.results["errors"].append(f"Effet {effect_id}: durée invalide ({duration})")
    
    def validate_cards(self):
        """Valide toutes les cartes"""
        print("\n🔍 Validation des cartes...")
        
        cards = self._iter_entities(self.cards_data)
        self.results["stats"]["cards_checked"] = len(cards)
        
        for card_data in cards:
            if isinstance(card_data, dict):
                self.validate_single_card(card_data)
    
    def validate_single_card(self, card_data):
        """Valide une carte individuelle"""
        card_id = card_data.get("id", "N/A")
        card_name = card_data.get("name", "N/A")
        
        # Champs requis
        required_fields = ["name", "element", "cost", "type"]
        for field in required_fields:
            if field not in card_data:
                self.results["errors"].append(f"Carte {card_id} ({card_name}): champ '{field}' manquant")
        
        # Vérifier le coût
        if "cost" in card_data:
            cost = card_data["cost"]
            if not isinstance(cost, (int, str)) or (isinstance(cost, int) and cost < 0):
                self.results["errors"].append(f"Carte {card_id} ({card_name}): coût invalide ({cost})")
    
    def check_data_consistency(self):
        """Vérifie la cohérence globale des données"""
        print("\n🔍 Vérification de la cohérence des données...")
        
        # Vérifier les références croisées
        self.check_cross_references()
        
        # Vérifier les doublons
        self.check_duplicates()
        
        # Vérifier les incohérences de nommage
        self.check_naming_consistency()
    
    def check_cross_references(self):
        """Vérifie les références croisées entre les données"""
        # Collecter tous les IDs utilisés
        all_ability_ids = set(self.effects_data.get("abilities", {}).keys())
        all_passive_ids = set(self.effects_data.get("passives", {}).keys())
        all_effect_ids = set(self.effects_data.get("effects", {}).keys())
        
        # Vérifier les références dans les capacités
        for ability_id, ability_data in self.effects_data.get("abilities", {}).items():
            # Vérifier les références aux passifs
            if "passive_effects" in ability_data:
                for passive_ref in ability_data["passive_effects"]:
                    if passive_ref not in all_passive_ids:
                        self.results["warnings"].append(f"Capacité {ability_id}: passif {passive_ref} inexistant")
            
            # Vérifier les références aux effets
            if "effects" in ability_data:
                for effect_ref in ability_data["effects"]:
                    if effect_ref not in all_effect_ids:
                        self.results["warnings"].append(f"Capacité {ability_id}: effet {effect_ref} inexistant")
    
    def check_duplicates(self):
        """Vérifie les doublons dans les données"""
        # Vérifier les noms de capacités dupliqués
        ability_names = defaultdict(list)
        for ability_id, ability_data in self.effects_data.get("abilities", {}).items():
            name = ability_data.get("name", "")
            if name:
                ability_names[name].append(ability_id)
        
        for name, ids in ability_names.items():
            if len(ids) > 1:
                self.results["warnings"].append(f"Nom de capacité dupliqué '{name}' dans: {ids}")
        
        # Vérifier les noms d'unités dupliqués
        unit_names = defaultdict(list)
        for unit_data in self._iter_entities(self.units_data):
            if isinstance(unit_data, dict):
                name = unit_data.get("name", "")
                unit_id = unit_data.get("id", "N/A")
                if name:
                    unit_names[name].append(unit_id)
        
        for name, ids in unit_names.items():
            if len(ids) > 1:
                self.results["warnings"].append(f"Nom d'unité dupliqué '{name}' dans: {ids}")
    
    def check_naming_consistency(self):
        """Vérifie la cohérence du nommage"""
        # Vérifier les noms vides ou invalides
        for ability_id, ability_data in self.effects_data.get("abilities", {}).items():
            name = ability_data.get("name", "")
            if not name or name.strip() == "":
                self.results["warnings"].append(f"Capacité {ability_id}: nom vide ou invalide")
        
        for unit_data in self._iter_entities(self.units_data):
            if isinstance(unit_data, dict):
                name = unit_data.get("name", "")
                unit_id = unit_data.get("id", "N/A")
                if not name or name.strip() == "":
                    self.results["warnings"].append(f"Unité {unit_id}: nom vide ou invalide")
    
    def run_validation(self):
        """Lance toute la validation"""
        print("🚀 Démarrage de la validation des données...")
        
        # Validations individuelles
        self.validate_abilities()
        self.validate_units()
        self.validate_heroes()
        self.validate_passives()
        self.validate_effects()
        self.validate_cards()
        
        # Validations globales
        self.check_data_consistency()
        
        # Affichage des résultats
        self.display_results()
    
    def display_results(self):
        """Affiche les résultats de la validation"""
        print("\n" + "="*70)
        print("📋 RÉSULTATS DE LA VALIDATION DES DONNÉES")
        print("="*70)
        
        stats = self.results["stats"]
        print(f"📊 Statistiques:")
        print(f"   - Capacités vérifiées: {stats['abilities_checked']}")
        print(f"   - Unités vérifiées: {stats['units_checked']}")
        print(f"   - Héros vérifiés: {stats['heroes_checked']}")
        print(f"   - Cartes vérifiées: {stats['cards_checked']}")
        print(f"   - Passifs vérifiés: {stats['passives_checked']}")
        print(f"   - Effets vérifiés: {stats['effects_checked']}")
        
        # Affichage des erreurs
        if self.results["errors"]:
            print(f"\n❌ Erreurs ({len(self.results['errors'])}):")
            for error in self.results["errors"][:20]:
                print(f"   - {error}")
            if len(self.results["errors"]) > 20:
                print(f"   ... et {len(self.results['errors']) - 20} autres erreurs")
        else:
            print(f"\n✅ Aucune erreur détectée!")
        
        # Affichage des avertissements
        if self.results["warnings"]:
            print(f"\n⚠️  Avertissements ({len(self.results['warnings'])}):")
            for warning in self.results["warnings"][:20]:
                print(f"   - {warning}")
            if len(self.results["warnings"]) > 20:
                print(f"   ... et {len(self.results['warnings']) - 20} autres avertissements")
        else:
            print(f"\n✅ Aucun avertissement!")
        
        # Recommandations
        print(f"\n💡 Recommandations:")
        if self.results["errors"]:
            print(f"   - Corriger les {len(self.results['errors'])} erreurs détectées")
        if self.results["warnings"]:
            print(f"   - Examiner les {len(self.results['warnings'])} avertissements")
        if not self.results["errors"] and not self.results["warnings"]:
            print(f"   - 🎉 Toutes les données sont cohérentes!")
        
        print("="*70)

def main():
    """Fonction principale"""
    print("🔍 Script de validation des données du jeu")
    print("="*70)
    
    try:
        validator = DataValidator()
        validator.run_validation()
        
    except KeyboardInterrupt:
        print("\n⏹️  Validation interrompue par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur fatale: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
