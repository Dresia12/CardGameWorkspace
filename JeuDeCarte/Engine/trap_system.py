"""
Système de gestion des pièges
Gère les pièges posés par les unités comme Roktus
"""

class TrapSystem:
    def __init__(self):
        self.traps = {}  # {target_id: {trap_data}}
    
    def plant_trap(self, target_id, trap_data):
        """Pose un piège sur une cible"""
        self.traps[target_id] = {
            'damage': trap_data.get('trap_damage', 10),
            'duration': trap_data.get('trap_duration', 3),
            'turns_left': trap_data.get('trap_duration', 3),
            'targets_attacker': trap_data.get('trap_targets_attacker', True),
            'original_damage': trap_data.get('damage', 0),
            'planted_by': trap_data.get('planted_by', None)
        }
    
    def check_trap_trigger(self, target_id, attacker_id):
        """Vérifie si un piège se déclenche quand quelqu'un attaque la cible"""
        if target_id in self.traps:
            trap = self.traps[target_id]
            if trap['targets_attacker']:
                # Le piège blesse l'attaquant
                return {
                    'triggered': True,
                    'target': attacker_id,
                    'damage': trap['damage'],
                    'trap_id': target_id
                }
            else:
                # Le piège blesse la cible piégée
                return {
                    'triggered': True,
                    'target': target_id,
                    'damage': trap['damage'],
                    'trap_id': target_id
                }
        return {'triggered': False}
    
    def remove_trap(self, target_id):
        """Retire un piège"""
        if target_id in self.traps:
            del self.traps[target_id]
    
    def update_traps(self):
        """Met à jour la durée des pièges et les fait exploser si nécessaire"""
        expired_traps = []
        for target_id, trap in self.traps.items():
            trap['turns_left'] -= 1
            if trap['turns_left'] <= 0:
                expired_traps.append(target_id)
        
        # Faire exploser les pièges expirés
        for target_id in expired_traps:
            self.remove_trap(target_id)
            # Retourner les dégâts à la cible initiale
            return {
                'expired_trap': True,
                'target': target_id,
                'damage': self.traps.get(target_id, {}).get('original_damage', 0)
            }
        
        return {'expired_trap': False}
    
    def get_trap_count(self, target_id):
        """Retourne le nombre de pièges sur une cible"""
        return 1 if target_id in self.traps else 0
    
    def get_all_traps(self):
        """Retourne tous les pièges actifs"""
        return self.traps.copy()

# Instance globale
trap_system = TrapSystem()
