"""
Gestionnaire de cibles pour le système de combat
Gère tous les types de cibles : unique, multiple, aléatoire, chaîne, etc.
"""

import random
from typing import List, Dict, Any, Optional
from enum import Enum


class TargetType(Enum):
    """Types de cibles supportés"""
    SINGLE_ENEMY = "single_enemy"
    SINGLE_ALLY = "single_ally"
    SELF = "self"
    ALL_ENEMIES = "all_enemies"
    ALL_ALLIES = "all_allies"
    ALL_UNITS = "all_units"
    RANDOM_ENEMY = "random_enemy"
    RANDOM_ALLY = "random_ally"
    RANDOM_UNIT = "random_unit"
    CHAIN_ENEMIES = "chain_enemies"
    CHAIN_ALLIES = "chain_allies"
    FRONT_ROW = "front_row"
    BACK_ROW = "back_row"
    ADJACENT_ENEMIES = "adjacent_enemies"
    ADJACENT_ALLIES = "adjacent_allies"


class TargetPriority(Enum):
    """Priorités de sélection de cibles"""
    LOWEST_HP = "lowest_hp"
    HIGHEST_HP = "highest_hp"
    LOWEST_DEFENSE = "lowest_defense"
    HIGHEST_DEFENSE = "highest_defense"
    RANDOM = "random"
    FIRST = "first"
    LAST = "last"


class TargetManager:
    """Gestionnaire de sélection et validation de cibles"""
    
    def __init__(self):
        self.target_types = TargetType
        self.priorities = TargetPriority
    
    def get_valid_targets(self, target_type: str, caster, battlefield, target_conditions: List[str] = None) -> List[Any]:
        """
        Retourne la liste des cibles valides selon le type demandé
        
        Args:
            target_type: Type de cible (TargetType)
            caster: Le lanceur de la capacité
            battlefield: Le champ de bataille actuel
            target_conditions: Conditions supplémentaires (alive, not_immune, etc.)
        
        Returns:
            Liste des cibles valides
        """
        if target_conditions is None:
            target_conditions = ["alive"]
        
        # Récupérer toutes les unités selon le type
        if target_type == TargetType.SINGLE_ENEMY.value:
            targets = self._get_enemies(battlefield, caster)
        elif target_type == TargetType.SINGLE_ALLY.value:
            targets = self._get_allies(battlefield, caster)
        elif target_type == TargetType.SELF.value:
            targets = [caster]
        elif target_type == TargetType.ALL_ENEMIES.value:
            targets = self._get_enemies(battlefield, caster)
        elif target_type == TargetType.ALL_ALLIES.value:
            targets = self._get_allies(battlefield, caster)
        elif target_type == TargetType.ALL_UNITS.value:
            targets = self._get_all_units(battlefield)
        elif target_type == TargetType.RANDOM_ENEMY.value:
            targets = self._get_enemies(battlefield, caster)
        elif target_type == TargetType.RANDOM_ALLY.value:
            targets = self._get_allies(battlefield, caster)
        elif target_type == TargetType.RANDOM_UNIT.value:
            targets = self._get_all_units(battlefield)
        elif target_type == TargetType.CHAIN_ENEMIES.value:
            targets = self._get_enemies(battlefield, caster)
        elif target_type == TargetType.CHAIN_ALLIES.value:
            targets = self._get_allies(battlefield, caster)
        elif target_type == TargetType.FRONT_ROW.value:
            targets = self._get_front_row(battlefield)
        elif target_type == TargetType.BACK_ROW.value:
            targets = self._get_back_row(battlefield)
        elif target_type == TargetType.ADJACENT_ENEMIES.value:
            targets = self._get_adjacent_enemies(battlefield, caster)
        elif target_type == TargetType.ADJACENT_ALLIES.value:
            targets = self._get_adjacent_allies(battlefield, caster)
        else:
            targets = []
        
        # Appliquer les conditions de filtrage
        valid_targets = self._apply_conditions(targets, target_conditions)
        
        return valid_targets
    
    def select_targets(self, target_type: str, caster, battlefield, target_count: int = 1, 
                      priority: str = TargetPriority.RANDOM.value, 
                      bounce_count: int = 0) -> List[Any]:
        """
        Sélectionne les cibles finales selon le type et la priorité
        
        Args:
            target_type: Type de cible
            caster: Le lanceur
            battlefield: Le champ de bataille
            target_count: Nombre de cibles à sélectionner
            priority: Priorité de sélection
            bounce_count: Nombre de rebonds pour les chaînes
        
        Returns:
            Liste des cibles sélectionnées
        """
        valid_targets = self.get_valid_targets(target_type, caster, battlefield)
        
        if not valid_targets:
            return []
        
        # Sélection selon le type
        if target_type in [TargetType.ALL_ENEMIES.value, TargetType.ALL_ALLIES.value, 
                          TargetType.ALL_UNITS.value, TargetType.FRONT_ROW.value, 
                          TargetType.BACK_ROW.value]:
            return valid_targets
        
        elif target_type in [TargetType.RANDOM_ENEMY.value, TargetType.RANDOM_ALLY.value, 
                            TargetType.RANDOM_UNIT.value]:
            return [random.choice(valid_targets)]
        
        elif target_type in [TargetType.CHAIN_ENEMIES.value, TargetType.CHAIN_ALLIES.value]:
            return self._select_chain_targets(valid_targets, bounce_count, priority)
        
        elif target_type in [TargetType.SINGLE_ENEMY.value, TargetType.SINGLE_ALLY.value, 
                            TargetType.SELF.value]:
            return [self._select_single_target(valid_targets, priority)]
        
        else:
            # Sélection multiple selon la priorité
            return self._select_multiple_targets(valid_targets, target_count, priority)
    
    def _get_enemies(self, battlefield, caster) -> List[Any]:
        """Récupère tous les ennemis"""
        enemies = []
        for unit in battlefield.get_all_units():
            if unit.owner != caster.owner:
                enemies.append(unit)
        return enemies
    
    def _get_allies(self, battlefield, caster) -> List[Any]:
        """Récupère tous les alliés"""
        allies = []
        # Ajouter les unités alliées
        for unit in battlefield.get_all_units():
            if unit.owner == caster.owner:
                allies.append(unit)
        return allies
    
    def _get_all_units(self, battlefield) -> List[Any]:
        """Récupère toutes les unités"""
        return battlefield.get_all_units()
    
    def _get_front_row(self, battlefield) -> List[Any]:
        """Récupère la première ligne"""
        # Logique pour identifier la première ligne
        return battlefield.get_front_row_units()
    
    def _get_back_row(self, battlefield) -> List[Any]:
        """Récupère la ligne arrière"""
        # Logique pour identifier la ligne arrière
        return battlefield.get_back_row_units()
    
    def _get_adjacent_enemies(self, battlefield, caster) -> List[Any]:
        """Récupère les ennemis adjacents"""
        # Logique pour identifier les ennemis adjacents
        return battlefield.get_adjacent_enemies(caster)
    
    def _get_adjacent_allies(self, battlefield, caster) -> List[Any]:
        """Récupère les alliés adjacents"""
        # Logique pour identifier les alliés adjacents
        return battlefield.get_adjacent_allies(caster)
    
    def _apply_conditions(self, targets: List[Any], conditions: List[str]) -> List[Any]:
        """Applique les conditions de filtrage"""
        valid_targets = targets.copy()
        
        for condition in conditions:
            if condition == "alive":
                valid_targets = [t for t in valid_targets if t.is_alive()]
            elif condition == "not_immune":
                valid_targets = [t for t in valid_targets if not t.has_immunity()]
            elif condition == "has_debuff":
                valid_targets = [t for t in valid_targets if t.has_debuffs()]
            elif condition == "has_buff":
                valid_targets = [t for t in valid_targets if t.has_buffs()]
            elif condition == "low_hp":
                valid_targets = [t for t in valid_targets if t.hp < t.max_hp * 0.5]
            elif condition == "high_hp":
                valid_targets = [t for t in valid_targets if t.hp > t.max_hp * 0.8]
        
        return valid_targets
    
    def _select_single_target(self, targets: List[Any], priority: str) -> Any:
        """Sélectionne une cible unique selon la priorité"""
        if not targets:
            return None
        
        if priority == TargetPriority.RANDOM.value:
            return random.choice(targets)
        elif priority == TargetPriority.LOWEST_HP.value:
            return min(targets, key=lambda t: t.hp)
        elif priority == TargetPriority.HIGHEST_HP.value:
            return max(targets, key=lambda t: t.hp)
        elif priority == TargetPriority.LOWEST_DEFENSE.value:
            return min(targets, key=lambda t: t.defense)
        elif priority == TargetPriority.HIGHEST_DEFENSE.value:
            return max(targets, key=lambda t: t.defense)
        elif priority == TargetPriority.FIRST.value:
            return targets[0]
        elif priority == TargetPriority.LAST.value:
            return targets[-1]
        else:
            return random.choice(targets)
    
    def _select_multiple_targets(self, targets: List[Any], count: int, priority: str) -> List[Any]:
        """Sélectionne plusieurs cibles selon la priorité"""
        if not targets:
            return []
        
        if count >= len(targets):
            return targets
        
        # Trier selon la priorité
        if priority == TargetPriority.LOWEST_HP.value:
            sorted_targets = sorted(targets, key=lambda t: t.hp)
        elif priority == TargetPriority.HIGHEST_HP.value:
            sorted_targets = sorted(targets, key=lambda t: t.hp, reverse=True)
        elif priority == TargetPriority.LOWEST_DEFENSE.value:
            sorted_targets = sorted(targets, key=lambda t: t.defense)
        elif priority == TargetPriority.HIGHEST_DEFENSE.value:
            sorted_targets = sorted(targets, key=lambda t: t.defense, reverse=True)
        else:
            # Aléatoire
            sorted_targets = targets.copy()
            random.shuffle(sorted_targets)
        
        return sorted_targets[:count]
    
    def _select_chain_targets(self, targets: List[Any], bounce_count: int, priority: str) -> List[Any]:
        """Sélectionne les cibles pour un effet en chaîne"""
        if not targets:
            return []
        
        chain_targets = []
        available_targets = targets.copy()
        
        for i in range(min(bounce_count, len(targets))):
            if not available_targets:
                break
            
            # Sélectionner la prochaine cible selon la priorité
            next_target = self._select_single_target(available_targets, priority)
            if next_target:
                chain_targets.append(next_target)
                available_targets.remove(next_target)
        
        return chain_targets
    
    def validate_target_selection(self, ability: Dict[str, Any], selected_targets: List[Any], 
                                caster, battlefield) -> bool:
        """
        Valide la sélection de cibles pour une capacité
        
        Args:
            ability: Définition de la capacité
            selected_targets: Cibles sélectionnées
            caster: Le lanceur
            battlefield: Le champ de bataille
        
        Returns:
            True si la sélection est valide
        """
        target_type = ability.get("target_type", "single_enemy")
        valid_targets = self.get_valid_targets(target_type, caster, battlefield)
        
        # Vérifier que toutes les cibles sélectionnées sont valides
        for target in selected_targets:
            if target not in valid_targets:
                return False
        
        # Vérifier le nombre de cibles selon le type
        if target_type in [TargetType.SINGLE_ENEMY.value, TargetType.SINGLE_ALLY.value, 
                          TargetType.SELF.value, TargetType.RANDOM_ENEMY.value, 
                          TargetType.RANDOM_ALLY.value, TargetType.RANDOM_UNIT.value]:
            if len(selected_targets) != 1:
                return False
        
        return True


# Instance globale du gestionnaire de cibles
target_manager = TargetManager()
