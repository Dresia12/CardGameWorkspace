#!/usr/bin/env python3
"""
Script pour corriger toutes les erreurs de syntaxe dans test_all_abilities_fixed.py
"""

def fix_all_syntax():
    """Corrige toutes les erreurs de syntaxe dans le script de test"""
    
    # Lire le fichier de test actuel
    with open('test_all_abilities_fixed.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Correction des problèmes d'indentation et de blocs try/except
    fixed_lines = []
    in_try_block = False
    try_indent_level = 0
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        # Détecter le début d'un bloc try
        if stripped.startswith('try:'):
            in_try_block = True
            try_indent_level = len(line) - len(line.lstrip())
            fixed_lines.append(line)
            continue
        
        # Détecter le début d'un bloc except
        if stripped.startswith('except') and in_try_block:
            in_try_block = False
            # S'assurer que l'indentation est correcte
            if len(line) - len(line.lstrip()) != try_indent_level:
                # Corriger l'indentation
                fixed_line = ' ' * try_indent_level + stripped + '\n'
                fixed_lines.append(fixed_line)
            else:
                fixed_lines.append(line)
            continue
        
        # Corriger les lignes avec des objets type() mal indentés
        if 'caster_obj = type(' in stripped and in_try_block:
            # Corriger l'indentation pour être dans le bloc try
            fixed_line = ' ' * (try_indent_level + 4) + stripped + '\n'
            fixed_lines.append(fixed_line)
            continue
        
        if 'target_obj = type(' in stripped and in_try_block:
            # Corriger l'indentation pour être dans le bloc try
            fixed_line = ' ' * (try_indent_level + 4) + stripped + '\n'
            fixed_lines.append(fixed_line)
            continue
        
        if 'self.engine.apply_advanced_effects(' in stripped and in_try_block:
            # Corriger l'indentation pour être dans le bloc try
            fixed_line = ' ' * (try_indent_level + 4) + stripped + '\n'
            fixed_lines.append(fixed_line)
            continue
        
        if 'self.engine.calculate_ability_damage(' in stripped and in_try_block:
            # Corriger l'indentation pour être dans le bloc try
            fixed_line = ' ' * (try_indent_level + 4) + stripped + '\n'
            fixed_lines.append(fixed_line)
            continue
        
        if 'self.record_test_result(' in stripped and in_try_block:
            # Corriger l'indentation pour être dans le bloc try
            fixed_line = ' ' * (try_indent_level + 4) + stripped + '\n'
            fixed_lines.append(fixed_line)
            continue
        
        # Corriger les lignes else mal indentées
        if stripped.startswith('else:') and in_try_block:
            # L'else doit être au même niveau que le try
            fixed_line = ' ' * try_indent_level + stripped + '\n'
            fixed_lines.append(fixed_line)
            continue
        
        if stripped.startswith('self.record_error(') and in_try_block:
            # Les appels à record_error dans le else doivent être indentés
            current_indent = len(line) - len(line.lstrip())
            if current_indent != try_indent_level + 4:
                fixed_line = ' ' * (try_indent_level + 4) + stripped + '\n'
                fixed_lines.append(fixed_line)
            else:
                fixed_lines.append(line)
            continue
        
        # Ajouter la ligne telle quelle si aucune correction n'est nécessaire
        fixed_lines.append(line)
    
    # Écrire le fichier corrigé
    with open('test_all_abilities_fixed.py', 'w', encoding='utf-8') as f:
        f.writelines(fixed_lines)
    
    print("Toutes les erreurs de syntaxe corrigées dans test_all_abilities_fixed.py")
    print("Les corrections apportées:")
    print("1. Correction de l'indentation de tous les blocs try/except")
    print("2. Alignement correct des objets type() dans les blocs try")
    print("3. Correction de l'indentation des blocs else")
    print("4. Alignement des appels aux méthodes du moteur")

if __name__ == "__main__":
    fix_all_syntax()
