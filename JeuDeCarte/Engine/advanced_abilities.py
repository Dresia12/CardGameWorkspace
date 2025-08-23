"""
Système de gestion des capacités avancées
Gère les capacités complexes comme le scaling, les chaînes aléatoires, etc.
"""

from typing import Dict, List, Any, Optional
import random
try:
    from .seed_system import seed_system
except ImportError:
    try:
        from seed_system import seed_system
    except ImportError:
        seed_system = None

class AdvancedAbilities:
    """Gestionnaire des capacités avancées"""
    
    def __init__(self):
        self.ability_usage_count: Dict[str, Dict[str, int]] = {}  # unit_id -> {ability_id -> count}
        self.temporary_passives: Dict[str, List[Dict[str, Any]]] = {}  # unit_id -> list of passives
        self.aura_effects: Dict[str, List[Dict[str, Any]]] = {}  # unit_id -> list of auras
        self.temporary_effects: Dict[str, List[Dict[str, Any]]] = {}  # unit_id -> list of temporary effects (dodge, silence, etc.)
        self.heal_usage_count: Dict[str, Dict[str, int]] = {}  # unit_id -> {ability_id -> count} for healing scaling
    
    def get_scaling_damage(self, unit_id: str, ability_id: str, base_damage: float, scaling_factor: float = 1.0) -> float:
        """
        Calcule les dégâts avec scaling par utilisation
        
        Args:
            unit_id: ID de l'unité
            ability_id: ID de la capacité
            base_damage: Dégâts de base
            scaling_factor: Facteur de scaling par utilisation
        
        Returns:
            Dégâts calculés
        """
        if unit_id not in self.ability_usage_count:
            self.ability_usage_count[unit_id] = {}
        
        if ability_id not in self.ability_usage_count[unit_id]:
            self.ability_usage_count[unit_id][ability_id] = 0
        
        usage_count = self.ability_usage_count[unit_id][ability_id]
        scaling_multiplier = 1.0 + (usage_count * scaling_factor)
        
        return base_damage * scaling_multiplier
    
    def get_scaling_heal(self, unit_id: str, ability_id: str, base_heal: float, scaling_factor: float = 1.0) -> float:
        """
        Calcule les soins avec scaling par utilisation
        
        Args:
            unit_id: ID de l'unité
            ability_id: ID de la capacité
            base_heal: Soins de base
            scaling_factor: Facteur de scaling par utilisation
        
        Returns:
            Soins calculés
        """
        if unit_id not in self.heal_usage_count:
            self.heal_usage_count[unit_id] = {}
        
        if ability_id not in self.heal_usage_count[unit_id]:
            self.heal_usage_count[unit_id][ability_id] = 0
        
        usage_count = self.heal_usage_count[unit_id][ability_id]
        scaling_multiplier = 1.0 + (usage_count * scaling_factor)
        
        return base_heal * scaling_multiplier
    
    def increment_ability_usage(self, unit_id: str, ability_id: str):
        """Incrémente le compteur d'utilisation d'une capacité"""
        if unit_id not in self.ability_usage_count:
            self.ability_usage_count[unit_id] = {}
        
        if ability_id not in self.ability_usage_count[unit_id]:
            self.ability_usage_count[unit_id][ability_id] = 0
        
        self.ability_usage_count[unit_id][ability_id] += 1
    
    def increment_heal_usage(self, unit_id: str, ability_id: str):
        """Incrémente le compteur d'utilisation d'un soin"""
        if unit_id not in self.heal_usage_count:
            self.heal_usage_count[unit_id] = {}
        
        if ability_id not in self.heal_usage_count[unit_id]:
            self.heal_usage_count[unit_id][ability_id] = 0
        
        self.heal_usage_count[unit_id][ability_id] += 1
    
    def add_temporary_effect(self, unit_id: str, effect_type: str, duration: int, value: float = 0.0):
        """
        Ajoute un effet temporaire à une unité
        
        Args:
            unit_id: ID de l'unité
            effect_type: Type d'effet (dodge, silence, defense, crit_boost, etc.)
            duration: Durée en tours
            value: Valeur de l'effet (optionnel)
        """
        if unit_id not in self.temporary_effects:
            self.temporary_effects[unit_id] = []
        
        effect = {
            "type": effect_type,
            "value": value,
            "duration": duration,
            "turns_remaining": duration
        }
        
        self.temporary_effects[unit_id].append(effect)
    
    def get_temporary_effects(self, unit_id: str) -> Dict[str, float]:
        """Retourne les effets temporaires actifs d'une unité"""
        effects = {}
        if unit_id in self.temporary_effects:
            for effect in self.temporary_effects[unit_id]:
                effects[effect["type"]] = effect["value"]
        return effects
    
    def update_temporary_effects(self) -> List[Dict[str, Any]]:
        """
        Met à jour les effets temporaires
        
        Returns:
            Liste des effets expirés
        """
        expired_effects = []
        
        for unit_id, effects in list(self.temporary_effects.items()):
            for effect in effects[:]:
                effect["turns_remaining"] -= 1
                
                if effect["turns_remaining"] <= 0:
                    expired_effects.append({
                        "unit_id": unit_id,
                        "effect_type": effect["type"]
                    })
                    effects.remove(effect)
        
        # Nettoyer les unités sans effets temporaires
        self.temporary_effects = {k: v for k, v in self.temporary_effects.items() if v}
        
        return expired_effects
    
    def chain_random_targets(self, caster, battlefield, base_targets: List[Any], chain_chance: float, max_bounces: int) -> List[Any]:
        """
        Gère les chaînes aléatoires
        
        Args:
            caster: Le lanceur
            battlefield: Le champ de bataille
            base_targets: Cibles initiales
            chain_chance: Probabilité de rebond (0.0 à 100.0)
            max_bounces: Nombre maximum de rebonds
        
        Returns:
            Liste des cibles touchées
        """
        if not base_targets:
            return []
        
        targets_hit = base_targets.copy()
        current_targets = base_targets.copy()
        
        for bounce in range(max_bounces):
            if not current_targets:
                break
            
            # Vérifier la probabilité de rebond
            if random.random() * 100 > chain_chance:
                break
            
            # Sélectionner une nouvelle cible aléatoire
            all_enemies = [unit for unit in battlefield.get_all_units() if unit.owner != caster.owner]
            available_targets = [t for t in all_enemies if t not in targets_hit]
            
            if not available_targets:
                break
            
            new_target = random.choice(available_targets)
            targets_hit.append(new_target)
            current_targets = [new_target]
        
        return targets_hit
    
    def add_temporary_passive(self, unit_id: str, passive_id: str, duration: int):
        """
        Ajoute un passif temporaire à une unité
        
        Args:
            unit_id: ID de l'unité
            passive_id: ID du passif
            duration: Durée en tours
        """
        if unit_id not in self.temporary_passives:
            self.temporary_passives[unit_id] = []
        
        passive = {
            "id": passive_id,
            "duration": duration,
            "turns_remaining": duration
        }
        
        self.temporary_passives[unit_id].append(passive)
    
    def update_temporary_passives(self) -> List[Dict[str, Any]]:
        """
        Met à jour les passifs temporaires
        
        Returns:
            Liste des passifs expirés
        """
        expired_passives = []
        
        for unit_id, passives in list(self.temporary_passives.items()):
            for passive in passives[:]:
                passive["turns_remaining"] -= 1
                
                if passive["turns_remaining"] <= 0:
                    expired_passives.append({
                        "unit_id": unit_id,
                        "passive_id": passive["id"]
                    })
                    passives.remove(passive)
        
        # Nettoyer les unités sans passifs temporaires
        self.temporary_passives = {k: v for k, v in self.temporary_passives.items() if v}
        
        return expired_passives
    
    def get_temporary_passives(self, unit_id: str) -> List[str]:
        """Retourne les IDs des passifs temporaires d'une unité"""
        return [p["id"] for p in self.temporary_passives.get(unit_id, [])]
    
    def add_aura_effect(self, unit_id: str, aura_type: str, boost_value: float, target_type: str):
        """
        Ajoute un effet d'aura
        
        Args:
            unit_id: ID de l'unité avec l'aura
            aura_type: Type d'aura (attack, defense, etc.)
            boost_value: Valeur du boost
            target_type: Type de cible (allies, self, etc.)
        """
        if unit_id not in self.aura_effects:
            self.aura_effects[unit_id] = []
        
        aura = {
            "type": aura_type,
            "boost": boost_value,
            "target": target_type
        }
        
        self.aura_effects[unit_id].append(aura)
    
    def get_aura_effects(self, unit_id: str) -> List[Dict[str, Any]]:
        """Retourne les effets d'aura d'une unité"""
        return self.aura_effects.get(unit_id, [])
    
    def calculate_aura_boosts(self, target_unit, battlefield) -> Dict[str, float]:
        """
        Calcule les boosts d'aura pour une unité cible
        
        Args:
            target_unit: L'unité cible
            battlefield: Le champ de bataille
        
        Returns:
            Dictionnaire des boosts par type
        """
        boosts = {}
        
        for aura_unit_id, auras in self.aura_effects.items():
            # Trouver l'unité avec l'aura
            aura_unit = None
            for unit in battlefield.get_all_units():
                if unit.id == aura_unit_id:
                    aura_unit = unit
                    break
            
            if not aura_unit or not aura_unit.is_alive():
                continue
            
            # Vérifier si la cible est affectée par l'aura
            for aura in auras:
                if aura["target"] == "allies" and target_unit.owner == aura_unit.owner and target_unit != aura_unit:
                    aura_type = aura["type"]
                    if aura_type not in boosts:
                        boosts[aura_type] = 0
                    boosts[aura_type] += aura["boost"]
                elif aura["target"] == "self" and target_unit == aura_unit:
                    aura_type = aura["type"]
                    if aura_type not in boosts:
                        boosts[aura_type] = 0
                    boosts[aura_type] += aura["boost"]
        
        return boosts

    def get_max_dodge_effect(self, unit_id: str) -> bool:
        """Vérifie si une unité a l'effet d'esquive maximale"""
        if unit_id in self.temporary_effects:
            for effect in self.temporary_effects[unit_id]:
                if effect["type"] == "max_dodge" and effect["turns_remaining"] > 0:
                    return True
        return False
    
    def get_max_crit_effect(self, unit_id: str) -> bool:
        """Vérifie si une unité a l'effet de critique maximale"""
        if unit_id in self.temporary_effects:
            for effect in self.temporary_effects[unit_id]:
                if effect["type"] == "max_crit" and effect["turns_remaining"] > 0:
                    return True
        return False
    
    def get_crit_boost_effect(self, unit_id: str) -> float:
        """Retourne le bonus de critique d'une unité"""
        if unit_id in self.temporary_effects:
            for effect in self.temporary_effects[unit_id]:
                if effect["type"] == "crit_boost" and effect["turns_remaining"] > 0:
                    return effect["value"]
        return 0.0
    
    def get_damage_reduction_effect(self, unit_id: str) -> float:
        """Retourne la réduction de dégâts d'une unité"""
        if unit_id in self.temporary_effects:
            for effect in self.temporary_effects[unit_id]:
                if effect["type"] == "damage_reduction" and effect["turns_remaining"] > 0:
                    return effect["value"]
        return 0.0
    
    def get_damage_per_turn_effect(self, unit_id: str) -> float:
        """Retourne les dégâts par tour d'une unité"""
        if unit_id in self.temporary_effects:
            for effect in self.temporary_effects[unit_id]:
                if effect["type"] == "damage_per_turn" and effect["turns_remaining"] > 0:
                    return effect["value"]
        return 0.0
    
    def reset_unit_cooldowns(self, unit_id: str):
        """Réinitialise tous les cooldowns d'une unité"""
        # Cette méthode sera appelée par le système principal
        # pour réinitialiser les cooldowns d'une unité
        pass
    
    def calculate_meteor_shower_targets(self, base_targets: int, crit_count: int, max_bonus: int) -> int:
        """
        Calcule le nombre de cibles pour la pluie de météores
        
        Args:
            base_targets: Nombre de cibles de base
            crit_count: Nombre de critiques obtenus
            max_bonus: Nombre maximum de cibles bonus
        
        Returns:
            Nombre total de cibles
        """
        bonus_targets = min(crit_count, max_bonus)
        return base_targets + bonus_targets

# Instance globale du gestionnaire de capacités avancées
advanced_abilities = AdvancedAbilities()
