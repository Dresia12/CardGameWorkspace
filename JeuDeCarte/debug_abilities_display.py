#!/usr/bin/env python3
"""
Script de debug pour vérifier l'affichage des capacités dans le clic droit
Vérifie la correspondance entre ability_ids et effects_database.json
"""

import json
import sys
import os

def load_data():
    """Charge les données du jeu"""
    try:
        with open("Data/effects_database.json", 'r', encoding='utf-8') as f:
            effects_data = json.load(f)
        print("✅ effects_database.json chargé avec succès")
        
        with open("Data/units.json", 'r', encoding='utf-8') as f:
            units_data = json.load(f)
        print("✅ units.json chargé avec succès")
        
        return effects_data, units_data
    except Exception as e:
        print(f"❌ Erreur chargement: {e}")
        return None, None

def debug_abilities_loading():
    """Debug le chargement des capacités"""
    print("🔍 DEBUG DU CHARGEMENT DES CAPACITÉS")
    print("====================================")
    
    effects_data, units_data = load_data()
    if not effects_data or not units_data:
        return
    
    # Vérifier la structure de effects_database.json
    print("\n📊 Structure de effects_database.json:")
    print(f"   - Clés principales: {list(effects_data.keys())}")
    
    if "abilities" in effects_data:
        abilities_data = effects_data["abilities"]
        print(f"   - Nombre de capacités: {len(abilities_data)}")
        print(f"   - Premières clés: {list(abilities_data.keys())[:5]}")
        print(f"   - Types des clés: {[type(k) for k in list(abilities_data.keys())[:3]]}")
        
        # Vérifier une capacité spécifique
        test_ability_id = "6009"
        if test_ability_id in abilities_data:
            test_ability = abilities_data[test_ability_id]
            print(f"\n✅ Capacité {test_ability_id} trouvée:")
            print(f"   - Nom: {test_ability.get('name', 'N/A')}")
            print(f"   - Description: {test_ability.get('description', 'N/A')}")
            print(f"   - Cooldown: {test_ability.get('base_cooldown', 'N/A')}")
        else:
            print(f"\n❌ Capacité {test_ability_id} NON trouvée")
    else:
        print("❌ Section 'abilities' manquante dans effects_database.json")
    
    # Vérifier les unités
    print("\n📊 Vérification des unités:")
    units_with_abilities = 0
    total_abilities = 0
    
    for unit in units_data:
        if "ability_ids" in unit and unit["ability_ids"]:
            units_with_abilities += 1
            total_abilities += len(unit["ability_ids"])
            
            # Tester la première unité avec des capacités
            if units_with_abilities == 1:
                print(f"\n🧪 Test de la première unité avec capacités:")
                print(f"   - Nom: {unit.get('name', 'N/A')}")
                print(f"   - Ability IDs: {unit['ability_ids']}")
                print(f"   - Types des IDs: {[type(ability_id) for ability_id in unit['ability_ids']]}")
                
                # Vérifier chaque capacité
                for i, ability_id in enumerate(unit['ability_ids']):
                    print(f"\n   📋 Capacité {i+1} (ID: {ability_id}):")
                    if ability_id in abilities_data:
                        ability = abilities_data[ability_id]
                        print(f"      ✅ Trouvée: {ability.get('name', 'N/A')}")
                        print(f"      - Description: {ability.get('description', 'N/A')[:50]}...")
                    else:
                        print(f"      ❌ NON trouvée dans abilities_data")
                        print(f"      - Type de ability_id: {type(ability_id)}")
                        print(f"      - Clés disponibles: {list(abilities_data.keys())[:10]}")
    
    print(f"\n📊 Résumé:")
    print(f"   - Unités avec capacités: {units_with_abilities}")
    print(f"   - Total de capacités: {total_abilities}")

def debug_passives_loading():
    """Debug le chargement des passifs"""
    print("\n🔍 DEBUG DU CHARGEMENT DES PASSIFS")
    print("===================================")
    
    effects_data, units_data = load_data()
    if not effects_data or not units_data:
        return
    
    # Vérifier la structure des passifs
    if "passives" in effects_data:
        passives_data = effects_data["passives"]
        print(f"📊 Structure des passifs:")
        print(f"   - Nombre de passifs: {len(passives_data)}")
        print(f"   - Premières clés: {list(passives_data.keys())[:5]}")
        
        # Vérifier un passif spécifique
        test_passive_id = "1000"
        if test_passive_id in passives_data:
            test_passive = passives_data[test_passive_id]
            print(f"\n✅ Passif {test_passive_id} trouvé:")
            print(f"   - Nom: {test_passive.get('name', 'N/A')}")
            print(f"   - Description: {test_passive.get('description', 'N/A')}")
        else:
            print(f"\n❌ Passif {test_passive_id} NON trouvé")
    else:
        print("❌ Section 'passives' manquante dans effects_database.json")
    
    # Vérifier les unités avec passifs
    print("\n📊 Vérification des unités avec passifs:")
    units_with_passives = 0
    total_passives = 0
    
    for unit in units_data:
        if "passive_ids" in unit and unit["passive_ids"]:
            units_with_passives += 1
            total_passives += len(unit["passive_ids"])
            
            # Tester la première unité avec des passifs
            if units_with_passives == 1:
                print(f"\n🧪 Test de la première unité avec passifs:")
                print(f"   - Nom: {unit.get('name', 'N/A')}")
                print(f"   - Passive IDs: {unit['passive_ids']}")
                
                # Vérifier chaque passif
                for i, passive_id in enumerate(unit['passive_ids']):
                    print(f"\n   🛡️ Passif {i+1} (ID: {passive_id}):")
                    if passive_id in passives_data:
                        passive = passives_data[passive_id]
                        print(f"      ✅ Trouvé: {passive.get('name', 'N/A')}")
                        print(f"      - Description: {passive.get('description', 'N/A')[:50]}...")
                    else:
                        print(f"      ❌ NON trouvé dans passives_data")
    
    print(f"\n📊 Résumé des passifs:")
    print(f"   - Unités avec passifs: {units_with_passives}")
    print(f"   - Total de passifs: {total_passives}")

def main():
    """Fonction principale"""
    print("🧪 DEBUG DE L'AFFICHAGE DES CAPACITÉS ET PASSIFS")
    print("================================================")
    
    debug_abilities_loading()
    debug_passives_loading()
    
    print("\n🎯 RÉSUMÉ DU DEBUG")
    print("===================")
    print("Ce script vérifie:")
    print("1. ✅ Le chargement de effects_database.json")
    print("2. ✅ La structure des capacités et passifs")
    print("3. ✅ La correspondance entre ability_ids/passive_ids et les données")
    print("4. ✅ Les types de données (string vs int)")

if __name__ == "__main__":
    main()
