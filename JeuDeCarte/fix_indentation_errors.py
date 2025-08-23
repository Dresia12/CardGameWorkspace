#!/usr/bin/env python3
"""
Script pour corriger les erreurs d'indentation dans test_all_abilities_fixed.py
"""

def fix_indentation_errors():
    """Corrige les erreurs d'indentation dans le script de test"""
    
    # Lire le fichier de test actuel
    with open('test_all_abilities_fixed.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Correction des erreurs d'indentation spécifiques
    fixed_lines = []
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        # Correction 1: Ligne 199 - self.record_error après if not ability_data
        if i == 198 and stripped == 'self.record_error(f"Capacité de base {ability_id} pour {element} non trouvée")':
            fixed_lines.append('            ' + stripped + '\n')
            continue
        
        # Correction 2: Ligne 200 - return après record_error
        if i == 199 and stripped == 'return':
            fixed_lines.append('                ' + stripped + '\n')
            continue
        
        # Correction 3: Ligne 210 - self.record_test_result après execute_advanced_ability
        if i == 209 and stripped.startswith('self.record_test_result('):
            fixed_lines.append('                ' + stripped + '\n')
            continue
        
        # Correction 4: Ligne 211 - else après record_test_result
        if i == 210 and stripped == 'else:':
            fixed_lines.append('            ' + stripped + '\n')
            continue
        
        # Correction 5: Ligne 212 - record_error dans le else
        if i == 211 and stripped.startswith('self.record_error('):
            fixed_lines.append('                ' + stripped + '\n')
            continue
        
        # Correction 6: Ligne 214 - except après else
        if i == 213 and stripped.startswith('except'):
            fixed_lines.append('        ' + stripped + '\n')
            continue
        
        # Correction 7: Ligne 215 - record_error dans except
        if i == 214 and stripped.startswith('self.record_error('):
            fixed_lines.append('            ' + stripped + '\n')
            continue
        
        # Correction 8: Ligne 260 - self.record_test_result après execute_advanced_ability
        if i == 259 and stripped.startswith('self.record_test_result('):
            fixed_lines.append('                ' + stripped + '\n')
            continue
        
        # Correction 9: Ligne 261 - else après record_test_result
        if i == 260 and stripped == 'else:':
            fixed_lines.append('            ' + stripped + '\n')
            continue
        
        # Correction 10: Ligne 262 - record_error dans le else
        if i == 261 and stripped.startswith('self.record_error('):
            fixed_lines.append('                ' + stripped + '\n')
            continue
        
        # Correction 11: Ligne 264 - except après else
        if i == 263 and stripped.startswith('except'):
            fixed_lines.append('        ' + stripped + '\n')
            continue
        
        # Correction 12: Ligne 265 - record_error dans except
        if i == 264 and stripped.startswith('self.record_error('):
            fixed_lines.append('            ' + stripped + '\n')
            continue
        
        # Ajouter la ligne telle quelle si aucune correction n'est nécessaire
        fixed_lines.append(line)
    
    # Écrire le fichier corrigé
    with open('test_all_abilities_fixed.py', 'w', encoding='utf-8') as f:
        f.writelines(fixed_lines)
    
    print("Erreurs d'indentation corrigées dans test_all_abilities_fixed.py")
    print("Les corrections apportées:")
    print("1. Correction de l'indentation des blocs if/else/except")
    print("2. Alignement des appels à record_error et record_test_result")
    print("3. Correction des blocs de code mal indentés")

if __name__ == "__main__":
    fix_indentation_errors()
