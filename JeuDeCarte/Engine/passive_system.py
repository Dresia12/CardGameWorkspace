"""
Système de gestion des passifs complexes
Gère les passifs comme la rage, les contre-attaques, etc.
"""

class PassiveSystem:
    def __init__(self):
        self.damage_history = {}  # {unit_id: {attacker_id: last_turn_damage}}
        self.counter_attack_queue = []  # Liste des contre-attaques à exécuter
        self.rage_units = {}  # {unit_id: rage_data}
        self.broken_units = {}  # {unit_id: broken_data}
        self.immobile_units = {}  # {unit_id: target_position}
    
    def record_damage(self, target_id, attacker_id, damage, turn):
        """Enregistre les dégâts reçus pour les passifs comme Hargneu"""
        if target_id not in self.damage_history:
            self.damage_history[target_id] = {}
        self.damage_history[target_id][attacker_id] = {
            'damage': damage,
            'turn': turn
        }
    
    def check_hate_bonus(self, attacker_id, target_id, current_turn):
        """Vérifie si l'attaquant a le bonus de haine contre sa cible"""
        if target_id in self.damage_history:
            if attacker_id in self.damage_history[target_id]:
                last_damage = self.damage_history[target_id][attacker_id]
                if last_damage['turn'] == current_turn - 1:  # Tour précédent
                    return True
        return False
    
    def add_counter_attack(self, unit_id, target_id):
        """Ajoute une contre-attaque à la queue"""
        self.counter_attack_queue.append({
            'unit_id': unit_id,
            'target_id': target_id
        })
    
    def get_counter_attacks(self):
        """Récupère et vide la queue des contre-attaques"""
        attacks = self.counter_attack_queue.copy()
        self.counter_attack_queue.clear()
        return attacks
    
    def calculate_rage_damage_boost(self, unit_id, current_hp, max_hp):
        """Calcule le bonus de dégâts de rage basé sur les PV manquants"""
        if current_hp <= 0 or max_hp <= 0:
            return 0
        
        missing_hp_percent = (max_hp - current_hp) / max_hp
        return missing_hp_percent  # 1% de bonus par % de PV manquant
    
    def calculate_broken_defense_penalty(self, unit_id, current_hp, max_hp, base_defense):
        """Calcule la pénalité de défense pour les unités brisées"""
        if current_hp <= 0 or max_hp <= 0:
            return 0
        
        missing_hp_percent = (max_hp - current_hp) / max_hp
        # Chaque tranche de 10% de PV manquant = -2 défense
        penalty = int(missing_hp_percent * 10) * 2
        return penalty
    
    def set_immobile_target(self, unit_id, target_position):
        """Définit la cible pour une unité immobile"""
        self.immobile_units[unit_id] = target_position
    
    def get_immobile_target(self, unit_id, enemy_positions):
        """Retourne la cible pour une unité immobile"""
        if unit_id not in self.immobile_units:
            return None
        
        target_pos = self.immobile_units[unit_id]
        
        # Vérifier si la cible existe encore
        if target_pos in enemy_positions:
            return target_pos
        
        # Si la cible est morte, trouver la plus proche
        if enemy_positions:
            # Logique simplifiée : prendre la première position disponible
            new_target = min(enemy_positions)
            self.immobile_units[unit_id] = new_target
            return new_target
        
        return None
    
    def clear_unit_data(self, unit_id):
        """Nettoie les données d'une unité quand elle meurt"""
        if unit_id in self.damage_history:
            del self.damage_history[unit_id]
        if unit_id in self.rage_units:
            del self.rage_units[unit_id]
        if unit_id in self.broken_units:
            del self.broken_units[unit_id]
        if unit_id in self.immobile_units:
            del self.immobile_units[unit_id]

# Instance globale
passive_system = PassiveSystem()
