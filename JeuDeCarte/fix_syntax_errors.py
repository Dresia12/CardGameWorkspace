#!/usr/bin/env python3
"""
Script pour corriger les erreurs de syntaxe dans test_all_abilities_fixed.py
"""

def fix_syntax_errors():
    """Corrige les erreurs de syntaxe dans le script de test"""
    
    # Lire le fichier de test actuel
    with open('test_all_abilities_fixed.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Correction 1: Corriger l'indentation et les blocs try/except mal fermés
    # Remplacer le bloc problématique autour de la ligne 421
    content = content.replace(
        '''                # Adapter le caster pour le moteur
        caster_obj = type('Caster', (), {
            'attack': caster_dict['stats']['attack'],
            'name': caster_dict['name'],
            'element': caster_dict['element']
        })()
        damage = self.engine.calculate_ability_damage(test_ability, caster_obj)
                self.record_test_result(f"Dégâts {damage_type}", damage >= 0, test_ability)
            else:
                self.record_error(f"Impossible de tester les dégâts {damage_type}: caster ou target manquant")
                
        except Exception as e:
            self.record_error(f"Erreur lors du test des dégâts {damage_type}: {e}")''',
        '''                # Adapter le caster pour le moteur
                caster_obj = type('Caster', (), {
                    'attack': caster_dict['stats']['attack'],
                    'name': caster_dict['name'],
                    'element': caster_dict['element']
                })()
                damage = self.engine.calculate_ability_damage(test_ability, caster_obj)
                self.record_test_result(f"Dégâts {damage_type}", damage >= 0, test_ability)
            else:
                self.record_error(f"Impossible de tester les dégâts {damage_type}: caster ou target manquant")
        except Exception as e:
            self.record_error(f"Erreur lors du test des dégâts {damage_type}: {e}")'''
    )
    
    # Correction 2: Corriger le bloc problématique autour de la ligne 470
    content = content.replace(
        '''                # Créer des objets compatibles pour apply_advanced_effects
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
        self.engine.apply_advanced_effects(caster_obj, test_ability, target_obj)
                self.record_test_result(f"Effet {effect}", True, test_ability)
            else:
                self.record_error(f"Impossible de tester l'effet {effect}: caster ou target manquant")
                
        except Exception as e:
            self.record_error(f"Erreur lors du test de l'effet {effect}: {e}")''',
        '''                # Créer des objets compatibles pour apply_advanced_effects
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
                self.engine.apply_advanced_effects(caster_obj, test_ability, target_obj)
                self.record_test_result(f"Effet {effect}", True, test_ability)
            else:
                self.record_error(f"Impossible de tester l'effet {effect}: caster ou target manquant")
        except Exception as e:
            self.record_error(f"Erreur lors du test de l'effet {effect}: {e}")'''
    )
    
    # Écrire le fichier corrigé
    with open('test_all_abilities_fixed.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Erreurs de syntaxe corrigées dans test_all_abilities_fixed.py")
    print("Les corrections apportées:")
    print("1. Correction de l'indentation des blocs try/except")
    print("2. Fermeture correcte des blocs try/except")
    print("3. Alignement de l'indentation pour tous les blocs de code")

if __name__ == "__main__":
    fix_syntax_errors()
