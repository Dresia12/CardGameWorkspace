#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour standardiser le format du template des unités
"""

import re

def standardize_template():
    """Standardise le format du template"""
    
    with open('units_abilities_template.txt', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Diviser en sections par élément
    sections = content.split('## ÉLÉMENT')
    
    standardized_content = sections[0]  # Garder l'en-tête
    
    for i, section in enumerate(sections[1:], 1):
        lines = section.strip().split('\n')
        if not lines:
            continue
            
        element_name = lines[0].split()[0].strip()
        standardized_content += f"\n## ÉLÉMENT {element_name.upper()}\n"
        standardized_content += "## " + "=" * (len(element_name) + 8) + "\n\n"
        
        current_unit = None
        unit_number = 1
        
        for line in lines[1:]:
            line = line.strip()
            
            # Détecter une nouvelle unité
            if re.match(r'^\d+\.\s*[^,]+,\s*[^,]+', line) or re.match(r'^[^,]+,\s*[^,]+', line):
                # Extraire le nom de l'unité
                if re.match(r'^\d+\.\s*', line):
                    unit_name = re.sub(r'^\d+\.\s*', '', line)
                else:
                    unit_name = line
                
                # Nettoyer le nom
                unit_name = re.sub(r'\s*\(Image:\s*\d+\)\s*$', '', unit_name).strip()
                
                standardized_content += f"{unit_number}. {unit_name}\n"
                current_unit = unit_name
                unit_number += 1
                
            # Stats
            elif line.startswith('- Stats') or line.startswith('Stats'):
                standardized_content += f"    - Stats (primaires/secondaires): {line.split(':', 1)[1].strip()}\n"
                
            # Rareté
            elif line.startswith('- Rareté') or line.startswith('Rareté'):
                rarity = line.split(':', 1)[1].strip() if ':' in line else line.split()[1]
                standardized_content += f"    - Rareté: {rarity}\n"
                
            # Passifs
            elif line.startswith('- Passifs') or line.startswith('Passifs'):
                passives = line.split(':', 1)[1].strip() if ':' in line else ""
                standardized_content += f"    - Passifs: {passives}\n"
                
            # Capacités
            elif line.startswith('- Capacités') or line.startswith('Capacités'):
                standardized_content += "    - Capacités à définir:\n"
                
            # Capacité individuelle
            elif line.startswith('Capacité') and ':' in line:
                standardized_content += f"      {line}\n"
                
            # Lignes de capacité détaillées
            elif line.startswith('      -') or line.startswith('        -'):
                standardized_content += f"      {line}\n"
                
            # Lignes vides importantes
            elif line == '':
                standardized_content += "\n"
                
            # Ignorer les autres lignes non standardisées
    
    # Écrire le fichier standardisé
    with open('units_abilities_template_standardized.txt', 'w', encoding='utf-8') as f:
        f.write(standardized_content)
    
    print("Template standardisé créé dans 'units_abilities_template_standardized.txt'")

if __name__ == "__main__":
    standardize_template()
