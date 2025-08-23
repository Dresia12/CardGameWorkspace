# hero_customization_manager.py - Gestionnaire de personnalisation des héros

import json
import os
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

class StatType(Enum):
    HP = "hp"
    ATTACK = "attack"
    DEFENSE = "defense"

class CustomizationOption:
    """Option de personnalisation pour une statistique"""
    def __init__(self, bonus_percent: int, mana_cost: int, description: str):
        self.bonus_percent = bonus_percent
        self.mana_cost = mana_cost
        self.description = description

class HeroCustomization:
    """Personnalisation d'un héros"""
    def __init__(self, hero_name: str):
        self.hero_name = hero_name
        self.hp_bonus = 0  # 0, 5, 10, ou 15%
        self.attack_bonus = 0  # 0, 5, 10, ou 15%
        self.defense_bonus = 0  # 0, 5, 10, ou 15%
        self.use_hero_ability = True  # True = capacité du héros, False = attaque basique
        self.has_passive = False  # True = passif activé, False = passif désactivé
        self.activation_cost = 3  # Coût de base d'activation
    
    def calculate_activation_cost(self, hero_data: Dict[str, Any] = None) -> int:
        """Calcule le coût d'activation total selon la documentation"""
        cost = 3  # Coût de base
        
        # Ajouter le coût des bonus de stats
        if self.hp_bonus == 5:
            cost += 1
        elif self.hp_bonus == 10:
            cost += 2
        elif self.hp_bonus == 15:
            cost += 3
        
        if self.attack_bonus == 5:
            cost += 1
        elif self.attack_bonus == 10:
            cost += 2
        elif self.attack_bonus == 15:
            cost += 3
        
        if self.defense_bonus == 5:
            cost += 1
        elif self.defense_bonus == 10:
            cost += 2
        elif self.defense_bonus == 15:
            cost += 3
        
        # Ajouter le coût pour utiliser la capacité du héros
        if self.use_hero_ability:
            cost += 1
        
        # Ajouter le coût pour activer le passif (basé sur le passif du héros)
        if self.has_passive and hero_data:
            passive_cost = self._get_passive_cost(hero_data)
            cost += passive_cost
        
        self.activation_cost = cost
        return cost
    
    def _get_passive_cost(self, hero_data: Dict[str, Any]) -> int:
        """Calcule le coût du passif selon le héros"""
        passive_text = hero_data.get("passive", "")
        
        # Extraire le coût du passif depuis le texte (format: "... (+X coût)")
        if "(+1 coût)" in passive_text:
            return 1
        elif "(+2 coût)" in passive_text:
            return 2
        elif "(+3 coût)" in passive_text:
            return 3
        elif "(+4 coût)" in passive_text:
            return 4
        else:
            return 2  # Coût par défaut
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit la personnalisation en dictionnaire"""
        return {
            "hero_name": self.hero_name,
            "hp_bonus": self.hp_bonus,
            "attack_bonus": self.attack_bonus,
            "defense_bonus": self.defense_bonus,
            "use_hero_ability": self.use_hero_ability,
            "has_passive": self.has_passive,
            "activation_cost": self.activation_cost
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'HeroCustomization':
        """Crée une personnalisation à partir d'un dictionnaire"""
        customization = cls(data.get("hero_name", "Héros inconnu"))
        customization.hp_bonus = data.get("hp_bonus", 0)
        customization.attack_bonus = data.get("attack_bonus", 0)
        customization.defense_bonus = data.get("defense_bonus", 0)
        customization.use_hero_ability = data.get("use_hero_ability", False)
        customization.has_passive = data.get("has_passive", False)
        customization.activation_cost = data.get("activation_cost", 3)
        return customization

class HeroCustomizationManager:
    """Gestionnaire de personnalisation des héros"""
    
    def __init__(self):
        self.customization_options = self._initialize_customization_options()
        self.customizations: Dict[str, HeroCustomization] = {}
        self.customizations_file = "JeuDeCarte/Decks/hero_customizations.json"
        
        # Charger les personnalisations existantes
        self.load_customizations()
    
    def _initialize_customization_options(self) -> Dict[str, List[CustomizationOption]]:
        """Initialise les options de personnalisation selon la documentation"""
        return {
            "hp": [
                CustomizationOption(0, 0, "HP de base"),
                CustomizationOption(5, 1, "HP +5% (+1 mana)"),
                CustomizationOption(10, 2, "HP +10% (+2 mana)"),
                CustomizationOption(15, 3, "HP +15% (+3 mana)")
            ],
            "attack": [
                CustomizationOption(0, 0, "Attaque de base"),
                CustomizationOption(5, 1, "Attaque +5% (+1 mana)"),
                CustomizationOption(10, 2, "Attaque +10% (+2 mana)"),
                CustomizationOption(15, 3, "Attaque +15% (+3 mana)")
            ],
            "defense": [
                CustomizationOption(0, 0, "Défense de base"),
                CustomizationOption(5, 1, "Défense +5% (+1 mana)"),
                CustomizationOption(10, 2, "Défense +10% (+2 mana)"),
                CustomizationOption(15, 3, "Défense +15% (+3 mana)")
            ],
            "ability": [
                CustomizationOption(0, 0, "Attaque basique"),
                CustomizationOption(1, 1, "Capacité du héros (+1 mana)")
            ]
        }
    
    def get_customization_options(self, stat_type: str) -> List[CustomizationOption]:
        """Retourne les options de personnalisation pour un type de statistique"""
        return self.customization_options.get(stat_type, [])
    
    def create_customization(self, hero_name: str) -> HeroCustomization:
        """Crée une nouvelle personnalisation pour un héros"""
        customization = HeroCustomization(hero_name)
        self.customizations[hero_name] = customization
        return customization
    
    def get_customization(self, hero_name: str) -> Optional[HeroCustomization]:
        """Retourne la personnalisation d'un héros"""
        return self.customizations.get(hero_name)
    
    def update_customization(self, hero_name: str, stat_type: str, value: int) -> bool:
        """Met à jour une personnalisation"""
        try:
            print(f"[DEBUG] update_customization called: {hero_name}, {stat_type}, {value}")
            if hero_name not in self.customizations:
                self.create_customization(hero_name)
            
            customization = self.customizations[hero_name]
            
            if stat_type == "hp":
                print(f"[DEBUG] Setting hp_bonus from {customization.hp_bonus} to {value}")
                customization.hp_bonus = value
            elif stat_type == "attack":
                print(f"[DEBUG] Setting attack_bonus from {customization.attack_bonus} to {value}")
                customization.attack_bonus = value
            elif stat_type == "defense":
                print(f"[DEBUG] Setting defense_bonus from {customization.defense_bonus} to {value}")
                customization.defense_bonus = value
            elif stat_type == "ability":
                customization.use_hero_ability = bool(value)
            elif stat_type == "passive":
                customization.has_passive = bool(value)
            else:
                raise ValueError(f"Type de statistique invalide: {stat_type}")
            
            # Recalculer le coût d'activation
            customization.calculate_activation_cost()
            
            return True
            
        except Exception as e:
            print(f"[ERREUR] Impossible de mettre à jour la personnalisation: {e}")
            return False
    
    def update_and_save_customization(self, hero_name: str, stat_type: str, value: int) -> bool:
        """Met à jour une personnalisation et la sauvegarde"""
        if self.update_customization(hero_name, stat_type, value):
            return self.save_customizations()
        return False
    
    def apply_customization_to_hero(self, hero_data: Dict[str, Any], customization: HeroCustomization) -> Dict[str, Any]:
        """Applique une personnalisation à un héros"""
        try:
            # Créer une copie profonde du héros
            import copy
            customized_hero = copy.deepcopy(hero_data)
            
            # S'assurer que base_stats existe
            if "base_stats" not in customized_hero:
                customized_hero["base_stats"] = {}
            
            # Récupérer les stats de base originales (sans modifications précédentes)
            original_base_stats = hero_data.get("base_stats", {})
            base_hp = original_base_stats.get("hp", 1000)
            base_attack = original_base_stats.get("attack", 30)
            base_defense = original_base_stats.get("defense", 25)
            
            # Appliquer les bonus de stats en utilisant les valeurs de base originales
            if hasattr(customization, 'hp_bonus') and customization.hp_bonus > 0:
                bonus = int(base_hp * (customization.hp_bonus / 100))
                customized_hero["base_stats"]["hp"] = base_hp + bonus
            else:
                customized_hero["base_stats"]["hp"] = base_hp
            
            if hasattr(customization, 'attack_bonus') and customization.attack_bonus > 0:
                bonus = int(base_attack * (customization.attack_bonus / 100))
                customized_hero["base_stats"]["attack"] = base_attack + bonus
            else:
                customized_hero["base_stats"]["attack"] = base_attack
            
            if hasattr(customization, 'defense_bonus') and customization.defense_bonus > 0:
                bonus = int(base_defense * (customization.defense_bonus / 100))
                customized_hero["base_stats"]["defense"] = base_defense + bonus
            else:
                customized_hero["base_stats"]["defense"] = base_defense
            
            # Ajouter les informations de personnalisation
            customized_hero["customization"] = customization.to_dict()
            customized_hero["activation_cost"] = customization.activation_cost
            
            return customized_hero
            
        except Exception as e:
            print(f"[ERREUR] Impossible d'appliquer la personnalisation: {e}")
            return hero_data
    
    def get_customized_hero_stats(self, hero_data: Dict[str, Any], customization: HeroCustomization) -> Dict[str, Any]:
        """Retourne les stats personnalisées d'un héros"""
        try:
            # Récupérer les stats de base originales
            base_stats = hero_data.get("base_stats", {})
            customized_stats = {}
            
            # Récupérer les valeurs de base originales
            base_hp = base_stats.get("hp", 1000)
            base_attack = base_stats.get("attack", 30)
            base_defense = base_stats.get("defense", 25)
            
            # Calculer les stats personnalisées en utilisant les valeurs de base originales
            if customization.hp_bonus > 0:
                bonus = int(base_hp * (customization.hp_bonus / 100))
                customized_stats["hp"] = base_hp + bonus
            else:
                customized_stats["hp"] = base_hp
            
            if customization.attack_bonus > 0:
                bonus = int(base_attack * (customization.attack_bonus / 100))
                customized_stats["attack"] = base_attack + bonus
            else:
                customized_stats["attack"] = base_attack
            
            if customization.defense_bonus > 0:
                bonus = int(base_defense * (customization.defense_bonus / 100))
                customized_stats["defense"] = base_defense + bonus
            else:
                customized_stats["defense"] = base_defense
            
            return customized_stats
            
        except Exception as e:
            print(f"[ERREUR] Impossible de calculer les stats personnalisées: {e}")
            return base_stats
    
    def validate_customization(self, customization: HeroCustomization) -> Tuple[bool, List[str]]:
        """Valide une personnalisation"""
        errors = []
        
        # Vérifier les valeurs des bonus
        valid_bonuses = [0, 5, 10, 15]
        if customization.hp_bonus not in valid_bonuses:
            errors.append(f"Bonus HP invalide: {customization.hp_bonus}% (doit être 0, 5, 10 ou 15)")
        
        if customization.attack_bonus not in valid_bonuses:
            errors.append(f"Bonus Attaque invalide: {customization.attack_bonus}% (doit être 0, 5, 10 ou 15)")
        
        if customization.defense_bonus not in valid_bonuses:
            errors.append(f"Bonus Défense invalide: {customization.defense_bonus}% (doit être 0, 5, 10 ou 15)")
        
        # Vérifier le coût d'activation
        calculated_cost = customization.calculate_activation_cost()
        if calculated_cost != customization.activation_cost:
            errors.append(f"Coût d'activation incorrect: {customization.activation_cost} (devrait être {calculated_cost})")
        
        return len(errors) == 0, errors
    
    def reset_customization(self, hero_name: str) -> bool:
        """Remet à zéro la personnalisation d'un héros"""
        try:
            if hero_name in self.customizations:
                del self.customizations[hero_name]
                self.save_customizations()
                print(f"[CUSTOMIZATION] Personnalisation remise à zéro pour {hero_name}")
                return True
            return False
            
        except Exception as e:
            print(f"[ERREUR] Impossible de remettre à zéro la personnalisation: {e}")
            return False
    
    def save_customizations(self) -> bool:
        """Sauvegarde toutes les personnalisations"""
        try:
            # Créer le dossier si nécessaire
            os.makedirs(os.path.dirname(self.customizations_file), exist_ok=True)
            
            data = {
                "customizations": {
                    name: customization.to_dict() 
                    for name, customization in self.customizations.items()
                },
                "version": "1.0"
            }
            
            with open(self.customizations_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"[CUSTOMIZATION] {len(self.customizations)} personnalisations sauvegardées")
            return True
            
        except Exception as e:
            print(f"[ERREUR] Impossible de sauvegarder les personnalisations: {e}")
            return False
    
    def load_customizations(self) -> bool:
        """Charge toutes les personnalisations"""
        try:
            if not os.path.exists(self.customizations_file):
                print(f"[CUSTOMIZATION] Aucun fichier de personnalisations trouvé")
                return True
            
            with open(self.customizations_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.customizations.clear()
            for name, customization_data in data.get("customizations", {}).items():
                customization = HeroCustomization.from_dict(customization_data)
                self.customizations[name] = customization
            
            print(f"[CUSTOMIZATION] {len(self.customizations)} personnalisations chargées")
            return True
            
        except Exception as e:
            print(f"[ERREUR] Impossible de charger les personnalisations: {e}")
            return False
    
    def get_customization_summary(self, hero_name: str) -> Dict[str, Any]:
        """Retourne un résumé de la personnalisation d'un héros"""
        customization = self.get_customization(hero_name)
        if not customization:
            return {
                "hero_name": hero_name,
                "has_customization": False,
                "total_bonus": 0,
                "activation_cost": 3,
                "modifications": []
            }
        
        modifications = []
        if customization.hp_bonus > 0:
            modifications.append(f"HP +{customization.hp_bonus}%")
        if customization.attack_bonus > 0:
            modifications.append(f"Attaque +{customization.attack_bonus}%")
        if customization.defense_bonus > 0:
            modifications.append(f"Défense +{customization.defense_bonus}%")
        if customization.use_hero_ability:
            modifications.append("Capacité du héros")
        if customization.has_passive:
            modifications.append("Passif activé")
        
        total_bonus = customization.hp_bonus + customization.attack_bonus + customization.defense_bonus
        
        return {
            "hero_name": hero_name,
            "has_customization": True,
            "hp_bonus": customization.hp_bonus,
            "attack_bonus": customization.attack_bonus,
            "defense_bonus": customization.defense_bonus,
            "use_hero_ability": customization.use_hero_ability,
            "has_passive": customization.has_passive,
            "total_bonus": total_bonus,
            "activation_cost": customization.activation_cost,
            "modifications": modifications
        }
    
    def get_all_customizations_summary(self) -> Dict[str, Dict[str, Any]]:
        """Retourne un résumé de toutes les personnalisations"""
        return {
            hero_name: self.get_customization_summary(hero_name)
            for hero_name in self.customizations.keys()
        }

# Instance globale du gestionnaire
hero_customization_manager = HeroCustomizationManager()