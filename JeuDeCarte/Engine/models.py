# models.py - Modèles de données pour JeuDeCarte

from typing import Dict, List, Optional, Any

class Ability:
    """Classe représentant une capacité"""
    def __init__(self, name: str, description: str, cooldown: int = 0, target_type: str = "single_enemy", ability_id: str = ""):
        self.name = name
        self.description = description
        self.cooldown = cooldown
        self.current_cooldown = 0  # Commencer à 0 pour être prêt à utiliser
        self.target_type = target_type  # Type de ciblage
        self.ability_id = ability_id  # ID de la capacité

class Hero:
    """Classe représentant un héros"""
    def __init__(self, name: str, element: str, base_stats: Dict[str, int], 
                 ability_name: str = "", ability_description: str = "", ability_cooldown: int = 0):
        self.name = name
        self.element = element
        self.base_stats = base_stats.copy()
        self.current_stats = base_stats.copy()
        self.ability = Ability(ability_name, ability_description, ability_cooldown) if ability_name else None
        self.temporary_effects = []  # Effets temporaires pour compatibilité
        # Initialiser le current_cooldown à 0 pour être prêt à utiliser
        if self.ability:
            self.ability.current_cooldown = 0
    
    @property
    def hp(self):
        """HP actuels du héros"""
        return self.current_stats.get('hp', 0)
    
    @hp.setter
    def hp(self, value):
        """Définit les HP actuels du héros"""
        self.current_stats['hp'] = max(0, value)  # Empêcher les HP négatifs
    
    @property
    def max_hp(self):
        """HP maximum du héros"""
        return self.base_stats.get('hp', 0)
    
    @property
    def attack(self):
        """Attaque du héros"""
        return self.current_stats.get('attack', 0)
    
    @property
    def defense(self):
        """Défense du héros"""
        return self.current_stats.get('defense', 0)
    
    def __getitem__(self, key):
        """Permet d'accéder aux stats comme un dictionnaire pour la compatibilité"""
        if key == 'hp':
            return self.hp
        elif key == 'attack':
            return self.attack
        elif key == 'defense':
            return self.defense
        else:
            return self.current_stats.get(key, 0)
    
    def get_activation_cost(self):
        """Retourne le coût d'activation du héros"""
        # Coût de base : 2 mana
        base_cost = 2
        
        # Vérifier si le passif est activé et ajoute du coût
        if hasattr(self, '_passive_active') and self._passive_active:
            # Vérifier le passif pour voir s'il ajoute du coût
            if hasattr(self, '_passive_description'):
                passive = self._passive_description
                if '+2 coût' in passive:
                    base_cost += 2
                elif '+1 coût' in passive:
                    base_cost += 1
        
        return base_cost
    
    @property
    def is_active(self):
        """Indique si le héros est activé"""
        return getattr(self, '_is_active', False)
    
    @is_active.setter
    def is_active(self, value):
        """Définit si le héros est activé"""
        self._is_active = value
    
    @property
    def abilities(self):
        """Retourne la liste des capacités du héros (compatibilité)"""
        if self.ability:
            return [self.ability]
        return []
    
    @property
    def ability_name(self):
        """Retourne le nom de la capacité du héros"""
        if self.ability:
            return self.ability.name
        return ""
    
    @property
    def ability_description(self):
        """Retourne la description de la capacité du héros"""
        if self.ability:
            return self.ability.description
        return ""
    
    @property
    def ability_cooldown(self):
        """Retourne le cooldown de la capacité du héros"""
        if self.ability:
            return self.ability.cooldown
        return 0
    
    def is_alive(self):
        """Vérifie si le héros est vivant"""
        return self.hp > 0

class Unit:
    """Classe représentant une unité"""
    def __init__(self, name: str, element: str, stats: Dict[str, int], 
                 abilities: List[str] = None, temporary_effects: List[Dict] = None):
        self.name = name
        self.element = element
        self.base_stats = stats.copy()  # Stats de base (pour les références)
        self.stats = stats.copy()  # Stats actuelles (peuvent être modifiées)
        self.abilities = abilities or []
        self.temporary_effects = temporary_effects or []
        self.active_effects = []  # Effets actifs (pour compatibilité)
        self.position = None  # Position sur le plateau
    
    @property
    def hp(self):
        """HP actuels de l'unité"""
        return self.stats.get('hp', 0)
    
    @hp.setter
    def hp(self, value):
        """Définit les HP actuels de l'unité"""
        self.stats['hp'] = max(0, value)  # Empêcher les HP négatifs
    
    @property
    def max_hp(self):
        """HP maximum de l'unité"""
        return self.base_stats.get('hp', 0)
    
    @property
    def attack(self):
        """Attaque de l'unité"""
        return self.stats.get('attack', 0)
    
    @property
    def defense(self):
        """Défense de l'unité"""
        return self.stats.get('defense', 0)
    
    def __getitem__(self, key):
        """Permet d'accéder aux stats comme un dictionnaire pour la compatibilité"""
        if key == 'hp':
            return self.hp
        elif key == 'attack':
            return self.attack
        elif key == 'defense':
            return self.defense
        else:
            return self.stats.get(key, 0)
    
    def is_alive(self):
        """Vérifie si l'unité est vivante"""
        return self.hp > 0

class Card:
    """Classe représentant une carte"""
    def __init__(self, name: str, cost: int, element: str, card_type: str, 
                 effect: str = "", target_type: str = "any", effects: list = None):
        self.name = name
        self.cost = cost
        self.element = element
        self.card_type = card_type
        self.effect = effect
        self.target_type = target_type
        self.effects = effects or []  # Ajouter l'attribut effects
    
    @property
    def type(self):
        """Propriété pour maintenir la compatibilité avec l'ancien code"""
        return self.card_type 