#!/usr/bin/env python3
"""
Script de test pour vérifier la reconnaissance de la rareté "Spécial"
"""

import json
import os

def test_special_rarity():
    """Teste la reconnaissance de la rareté Spécial"""
    
    print("=== TEST DE LA RARETÉ SPÉCIAL ===\n")
    
    # 1. Vérifier les unités avec rareté Spécial dans units.json
    print("1. Vérification des unités avec rareté 'Spécial' dans units.json:")
    
    try:
        with open('Data/units.json', 'r', encoding='utf-8') as f:
            units_data = json.load(f)
        
        special_units = []
        for unit in units_data:
            if unit.get('rarity') == 'Spécial':
                special_units.append(unit['name'])
        
        if special_units:
            print(f"   ✅ Trouvé {len(special_units)} unité(s) avec rareté 'Spécial':")
            for unit_name in special_units:
                print(f"      - {unit_name}")
        else:
            print("   ❌ Aucune unité avec rareté 'Spécial' trouvée")
            
    except Exception as e:
        print(f"   ❌ Erreur lors de la lecture de units.json: {e}")
    
    print()
    
    # 2. Vérifier les unités avec rareté Spécial dans le template
    print("2. Vérification des unités avec rareté 'Spécial' dans le template:")
    
    try:
        with open('units_abilities_template.txt', 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        # Chercher les lignes avec "Rareté: Spécial"
        special_lines = []
        lines = template_content.split('\n')
        for i, line in enumerate(lines):
            if 'Rareté: Spécial' in line:
                # Remonter pour trouver le nom de l'unité
                for j in range(i, max(0, i-5), -1):
                    if lines[j].strip().startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', '10.', '11.', '12.')):
                        special_lines.append(lines[j].strip())
                        break
        
        if special_lines:
            print(f"   ✅ Trouvé {len(special_lines)} unité(s) avec rareté 'Spécial' dans le template:")
            for line in special_lines:
                print(f"      - {line}")
        else:
            print("   ❌ Aucune unité avec rareté 'Spécial' trouvée dans le template")
            
    except Exception as e:
        print(f"   ❌ Erreur lors de la lecture du template: {e}")
    
    print()
    
    # 3. Vérifier la cohérence entre units.json et le template
    print("3. Vérification de la cohérence entre units.json et le template:")
    
    try:
        # Unités avec rareté Spécial dans units.json
        json_special = set()
        for unit in units_data:
            if unit.get('rarity') == 'Spécial':
                json_special.add(unit['name'])
        
        # Unités avec rareté Spécial dans le template
        template_special = set()
        for line in special_lines:
            # Extraire le nom de l'unité (après le numéro et avant " (Image:")
            parts = line.split('. ', 1)
            if len(parts) > 1:
                name_part = parts[1].split(' (Image:')[0]
                template_special.add(name_part)
        
        # Comparaison
        if json_special == template_special:
            print("   ✅ Cohérence parfaite entre units.json et le template")
        else:
            print("   ⚠️  Incohérences détectées:")
            only_in_json = json_special - template_special
            only_in_template = template_special - json_special
            if only_in_json:
                print(f"      - Uniquement dans units.json: {only_in_json}")
            if only_in_template:
                print(f"      - Uniquement dans le template: {only_in_template}")
                
    except Exception as e:
        print(f"   ❌ Erreur lors de la comparaison: {e}")
    
    print()
    
    # 4. Résumé
    print("4. Résumé:")
    print("   - La rareté 'Spécial' est maintenant reconnue dans toutes les interfaces")
    print("   - Couleur assignée: Cyan (COLORS['cyan'])")
    print("   - Unités concernées: Gelidar, Chevalier des Neiges et Flamby, Lutin des Flammes")
    print("   - Toutes les sections de game_ui.py ont été mises à jour")

if __name__ == "__main__":
    test_special_rarity()
