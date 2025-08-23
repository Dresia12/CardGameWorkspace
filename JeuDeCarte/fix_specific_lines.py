#!/usr/bin/env python3
"""
Script pour corriger spécifiquement les lignes problématiques dans test_all_abilities_fixed.py
"""

def fix_specific_lines():
    """Corrige les lignes spécifiques avec des erreurs d'indentation"""
    
    # Lire le fichier de test actuel
    with open('test_all_abilities_fixed.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Correction 1: Ligne 199 - self.record_error après if not ability_data
    content = content.replace(
        '''            if not ability_data:
            self.record_error(f"Capacité de base {ability_id} pour {element} non trouvée")
                return''',
        '''            if not ability_data:
                self.record_error(f"Capacité de base {ability_id} pour {element} non trouvée")
                return'''
    )
    
    # Correction 2: Ligne 210 - self.record_test_result après execute_advanced_ability
    content = content.replace(
        '''                result = self.engine.execute_advanced_ability(caster_dict, ability_id, target)
            self.record_test_result(f"Capacité de base {element}", result, ability_data)
        else:''',
        '''                result = self.engine.execute_advanced_ability(caster_dict, ability_id, target)
                self.record_test_result(f"Capacité de base {element}", result, ability_data)
            else:'''
    )
    
    # Correction 3: Ligne 212 - record_error dans le else
    content = content.replace(
        '''        else:
            self.record_error(f"Impossible de tester la capacité {element}: caster ou target manquant")
                
        except Exception as e:''',
        '''        else:
                self.record_error(f"Impossible de tester la capacité {element}: caster ou target manquant")
        except Exception as e:'''
    )
    
    # Correction 4: Ligne 260 - self.record_test_result après execute_advanced_ability dans test_specific_ability
    content = content.replace(
        '''                result = self.engine.execute_advanced_ability(caster, ability_id, target_dict)
            self.record_test_result(f"Capacité {ability_id} - {description}", result, ability_data)
        else:''',
        '''                result = self.engine.execute_advanced_ability(caster, ability_id, target_dict)
                self.record_test_result(f"Capacité {ability_id} - {description}", result, ability_data)
            else:'''
    )
    
    # Correction 5: Ligne 262 - record_error dans le else de test_specific_ability
    content = content.replace(
        '''        else:
            self.record_error(f"Impossible de tester {description} (ID: {ability_id}): target manquant")
                
        except Exception as e:''',
        '''        else:
                self.record_error(f"Impossible de tester {description} (ID: {ability_id}): target manquant")
        except Exception as e:'''
    )
    
    # Écrire le fichier corrigé
    with open('test_all_abilities_fixed.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Lignes spécifiques corrigées dans test_all_abilities_fixed.py")
    print("Les corrections apportées:")
    print("1. Correction de l'indentation de self.record_error après if not ability_data")
    print("2. Correction de l'indentation de self.record_test_result après execute_advanced_ability")
    print("3. Correction de l'indentation des blocs else et except")
    print("4. Alignement correct de tous les blocs de code")

if __name__ == "__main__":
    fix_specific_lines()
