#!/usr/bin/env python3
"""
Script final pour corriger toutes les erreurs de syntaxe dans test_all_abilities_fixed.py
"""

def fix_final_syntax():
    """Corrige toutes les erreurs de syntaxe restantes"""
    
    # Lire le fichier de test actuel
    with open('test_all_abilities_fixed.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Correction 1: Problème avec les blocs else mal placés autour de la ligne 372
    content = content.replace(
        '''                    targets = self.engine.select_ability_targets(caster_dict, test_ability, None)
            self.record_test_result(f"Ciblage {target_type}", len(targets) > 0, test_ability)
        else:
                    self.record_warning(f"Méthode select_ability_targets non disponible pour {target_type}")
        else:
            self.record_error(f"Impossible de tester le ciblage {target_type}: caster manquant")''',
        '''                    targets = self.engine.select_ability_targets(caster_dict, test_ability, None)
                    self.record_test_result(f"Ciblage {target_type}", len(targets) > 0, test_ability)
                else:
                    self.record_warning(f"Méthode select_ability_targets non disponible pour {target_type}")
            else:
                self.record_error(f"Impossible de tester le ciblage {target_type}: caster manquant")'''
    )
    
    # Correction 2: Problème avec l'indentation dans test_damage_type
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
        except Exception as e:''',
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
        except Exception as e:'''
    )
    
    # Correction 3: Problème avec l'indentation dans test_status_effect
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
    
    print("Toutes les erreurs de syntaxe finales corrigées dans test_all_abilities_fixed.py")
    print("Les corrections apportées:")
    print("1. Correction des blocs else mal placés")
    print("2. Correction de l'indentation dans test_damage_type")
    print("3. Correction de l'indentation dans test_status_effect")
    print("4. Alignement correct de tous les blocs try/except/else")

if __name__ == "__main__":
    fix_final_syntax()
