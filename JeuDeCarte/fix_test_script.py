#!/usr/bin/env python3
"""
Script pour corriger les erreurs dans test_all_abilities.py
"""

def fix_test_script():
    """Corrige les erreurs dans le script de test"""
    
    # Lire le fichier de test actuel
    with open('test_all_abilities.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Correction 1: Adapter les appels à calculate_ability_damage pour utiliser les attributs corrects
    # Le moteur s'attend à caster.attack mais reçoit un dictionnaire
    content = content.replace(
        'damage = self.engine.calculate_ability_damage(test_ability, caster_dict)',
        '''# Adapter le caster pour le moteur
        caster_obj = type('Caster', (), {
            'attack': caster_dict['stats']['attack'],
            'name': caster_dict['name'],
            'element': caster_dict['element']
        })()
        damage = self.engine.calculate_ability_damage(test_ability, caster_obj)'''
    )
    
    # Correction 2: Adapter les appels à get_random_multiple_targets pour passer une liste
    content = content.replace(
        'targets = self.engine.get_random_multiple_targets(caster_dict, 3, False)',
        '''# Créer une liste de cibles pour la sélection aléatoire
        available_targets = [target_dict]
        targets = self.engine.get_random_multiple_targets(available_targets, 3, False)'''
    )
    
    # Correction 3: Adapter les autres appels à get_random_multiple_targets
    content = content.replace(
        'targets = self.engine.get_random_multiple_targets(caster_dict, 2, True)',
        '''available_targets = [target_dict]
        targets = self.engine.get_random_multiple_targets(available_targets, 2, True)'''
    )
    
    # Correction 4: Adapter les appels à apply_advanced_effects
    content = content.replace(
        'self.engine.apply_advanced_effects(caster_dict, test_ability, target_dict)',
        '''# Créer des objets compatibles pour apply_advanced_effects
        caster_obj = type('Caster', (), {
            'id': caster_dict['id'],
            'name': caster_dict['name'],
            'element': caster_dict['element'],
            'stats': caster_dict['stats']
        })()
        target_obj = type('Target', (), {
            'id': target_dict['id'],
            'name': target_dict['name'],
            'element': target_dict['element'],
            'stats': target_dict['stats']
        })()
        self.engine.apply_advanced_effects(caster_obj, test_ability, target_obj)'''
    )
    
    # Correction 5: Adapter les appels à select_ability_targets
    content = content.replace(
        'targets = self.engine.select_ability_targets(test_ability, caster_dict, [target_dict])',
        '''# Créer des objets compatibles pour select_ability_targets
        caster_obj = type('Caster', (), {
            'id': caster_dict['id'],
            'name': caster_dict['name'],
            'element': caster_dict['element'],
            'stats': caster_dict['stats'],
            'owner': caster_dict['owner']
        })()
        target_obj = type('Target', (), {
            'id': target_dict['id'],
            'name': target_dict['name'],
            'element': target_dict['element'],
            'stats': target_dict['stats'],
            'owner': target_dict['owner']
        })()
        targets = self.engine.select_ability_targets(test_ability, caster_obj, [target_obj])'''
    )
    
    # Correction 6: Adapter les appels à validate_ability_targets
    content = content.replace(
        'is_valid = self.engine.validate_ability_targets(test_ability, caster_dict, [target_dict])',
        '''# Créer des objets compatibles pour validate_ability_targets
        caster_obj = type('Caster', (), {
            'id': caster_dict['id'],
            'name': caster_dict['name'],
            'element': caster_dict['element'],
            'stats': caster_dict['stats'],
            'owner': caster_dict['owner']
        })()
        target_obj = type('Target', (), {
            'id': target_dict['id'],
            'name': target_dict['name'],
            'element': target_dict['element'],
            'stats': target_dict['stats'],
            'owner': target_dict['owner']
        })()
        is_valid = self.engine.validate_ability_targets(test_ability, caster_obj, [target_obj])'''
    )
    
    # Correction 7: Adapter les appels à get_available_targets_for_ability
    content = content.replace(
        'available_targets = self.engine.get_available_targets_for_ability(test_ability, caster_dict)',
        '''# Créer un objet compatible pour get_available_targets_for_ability
        caster_obj = type('Caster', (), {
            'id': caster_dict['id'],
            'name': caster_dict['name'],
            'element': caster_dict['element'],
            'stats': caster_dict['stats'],
            'owner': caster_dict['owner']
        })()
        available_targets = self.engine.get_available_targets_for_ability(test_ability, caster_obj)'''
    )
    
    # Écrire le fichier corrigé
    with open('test_all_abilities_fixed.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Script de test corrigé créé: test_all_abilities_fixed.py")
    print("Les principales corrections apportées:")
    print("1. Adaptation des appels à calculate_ability_damage pour utiliser des objets avec attributs")
    print("2. Correction des appels à get_random_multiple_targets pour passer des listes")
    print("3. Adaptation des appels à apply_advanced_effects avec des objets compatibles")
    print("4. Correction des appels aux méthodes de ciblage avec des objets appropriés")

if __name__ == "__main__":
    fix_test_script()
