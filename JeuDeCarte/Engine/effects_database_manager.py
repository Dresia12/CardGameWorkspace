# effects_database_manager.py - Gestionnaire de la base de données d'effets

import json
import os
import random
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field

@dataclass
class EffectResult:
    """Résultat de l'application d'un effet"""
    success: bool
    damage: int = 0
    effects_applied: List[str] = field(default_factory=list)
    chain_effects: List[str] = field(default_factory=list)
    message: str = ""

class EffectsDatabaseManager:
    """Gestionnaire de la base de données d'effets"""
    
    def __init__(self, database_path: str = "Data/effects_database.json"):
        self.database_path = database_path
        self.database = self._load_database()
        
    def _load_database(self) -> Dict[str, Any]:
        """Charge la base de données d'effets"""
        try:
            with open(self.database_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Base de données d'effets non trouvée: {self.database_path}")
            return {}
        except json.JSONDecodeError as e:
            print(f"Erreur de décodage JSON: {e}")
            return {}
    
    def get_element_name(self, element_id: str) -> str:
        """Récupère le nom d'un élément par son ID"""
        element = self.database.get("elements", {}).get(element_id, {})
        return element.get("name", "Inconnu")
    
    def get_element_id(self, element_name: str) -> str:
        """Récupère l'ID d'un élément par son nom"""
        for element_id, element_data in self.database.get("elements", {}).items():
            if element_data.get("name") == element_name:
                return element_id
        return "12"  # NEUTRE par défaut
    
    def get_base_effect(self, effect_id: str) -> Dict[str, Any]:
        """Récupère un effet de base par son ID"""
        return self.database.get("base_effects", {}).get(effect_id, {})
    
    def get_chain_effect(self, effect_id: str) -> Dict[str, Any]:
        """Récupère un effet en chaîne par son ID"""
        return self.database.get("chain_effects", {}).get(effect_id, {})
    
    def get_ability(self, ability_id: str) -> Dict[str, Any]:
        """Récupère une capacité par son ID"""
        return self.database.get("abilities", {}).get(ability_id, {})
    
    def get_passive(self, passive_id: str) -> Dict[str, Any]:
        """Récupère un passif par son ID"""
        return self.database.get("passives", {}).get(passive_id, {})
    
    def calculate_ability_damage(self, ability_id: str, caster_attack: int, 
                               damage_modifiers: float = 1.0) -> int:
        """Calcule les dégâts d'une capacité"""
        ability = self.get_ability(ability_id)
        if not ability:
            return 0
            
        damage_type = ability.get("damage_type", "fixed")
        base_damage = ability.get("damage", 0)
        
        if damage_type == "fixed":
            return int(base_damage * damage_modifiers)
        elif damage_type == "attack_plus":
            return int((caster_attack + base_damage) * damage_modifiers)
        elif damage_type == "attack_only":
            return int(caster_attack * damage_modifiers)
        else:
            return int(base_damage * damage_modifiers)
    
    def get_ability_cooldown(self, ability_id: str, unit_cooldown_modifiers: Dict[str, int] = None) -> int:
        """Calcule le cooldown final d'une capacité"""
        ability = self.get_ability(ability_id)
        if not ability:
            return 1
            
        base_cooldown = ability.get("base_cooldown", 1)
        
        if unit_cooldown_modifiers and ability_id in unit_cooldown_modifiers:
            return max(1, base_cooldown + unit_cooldown_modifiers[ability_id])
        
        return base_cooldown
    
    def apply_elemental_attack_effects(self, element_id: str, source, target, 
                                      engine, ability_target_type: str = None) -> List[str]:
        """Applique les effets automatiques d'un élément d'attaque"""
        applied_effects = []
        
        # Chercher l'effet automatique pour cet élément
        for effect_id, effect_data in self.database.get("elemental_attack_effects", {}).items():
            if effect_data.get("element") == element_id:
                if self._should_apply_effect(effect_data):
                    effect_name = effect_data.get("name", "")
                    applied_effects.append(effect_name)
                    
                    # Appliquer l'effet selon son type
                    if "effects" in effect_data:
                        # Effets multiples (comme Foudre)
                        for sub_effect in effect_data["effects"]:
                            if self._should_apply_effect(sub_effect):
                                self._apply_single_effect(sub_effect, source, target, engine, ability_target_type)
                    else:
                        # Effet simple
                        self._apply_single_effect(effect_data, source, target, engine, ability_target_type)
        
        return applied_effects
    
    def _should_apply_effect(self, effect_data: Dict[str, Any]) -> bool:
        """Détermine si un effet doit être appliqué selon sa chance"""
        chance = effect_data.get("chance", 100)
        return random.randint(1, 100) <= chance
    
    def _apply_single_effect(self, effect_data: Dict[str, Any], source, target, engine, ability_target_type: str = None):
        """Applique un effet simple"""
        effect_type = effect_data.get("effect", "")
        effect_target_type = effect_data.get("target", "enemy")
        duration = effect_data.get("duration", 1)
        value = effect_data.get("value", 0)
        
        # PRIORITÉ : Utiliser le target_type de la capacité si disponible
        # Sinon, utiliser le target de l'effet
        final_target_type = ability_target_type if ability_target_type else effect_target_type
        
        # Déterminer la vraie cible
        # Si target est une liste (capacité all_allies), appliquer à tous les alliés
        if isinstance(target, list):
            # Capacité qui cible tous les alliés
            for ally_target in target:
                self._apply_effect_to_target(effect_type, final_target_type, duration, value, source, ally_target, engine)
        else:
            # Cible unique
            actual_target = target if final_target_type == "enemy" else source
            self._apply_effect_to_target(effect_type, final_target_type, duration, value, source, actual_target, engine)
    
    def _apply_effect_to_target(self, effect_type: str, target_type: str, duration: int, value: float, source, target, engine):
        """Applique un effet à une cible spécifique"""
        # Déterminer la vraie cible pour cet effet
        # CORRECTION : Pour les capacités all_allies, appliquer à la cible (allié) et non au lanceur
        if target_type == "all_allies":
            actual_target = target  # La cible est déjà un allié
        elif target_type == "enemy":
            actual_target = target
        else:
            actual_target = source  # self, single_ally, etc.
        
        # Appliquer l'effet selon son type
        if effect_type == "burn":
            self._apply_burn_effect(actual_target, duration, engine)
        elif effect_type == "freeze":
            self._apply_freeze_effect(actual_target, duration, engine)
        elif effect_type == "poison":
            self._apply_poison_effect(actual_target, duration, engine)
        elif effect_type == "heal_reduction":
            self._apply_heal_reduction_effect(actual_target, duration, value, engine)
        elif effect_type == "defense_reduction":
            self._apply_defense_reduction_effect(actual_target, duration, value, engine)
        elif effect_type == "dodge_boost":
            self._apply_dodge_boost_effect(actual_target, duration, value, engine)
        elif effect_type == "crit_boost":
            self._apply_crit_boost_effect(actual_target, duration, value, engine)
        elif effect_type == "purify":
            self._apply_purify_effect(actual_target, engine)
        elif effect_type == "steal_mana":
            self._apply_steal_mana_effect(source, target, value, engine)
        elif effect_type == "random_debuff":
            self._apply_random_debuff_effect(actual_target, duration, engine)
        elif effect_type == "dispel_positive":
            self._apply_dispel_positive_effect(actual_target, engine)
        elif effect_type == "damage_boost":
            self._apply_damage_boost_effect(actual_target, duration, value, engine)
        elif effect_type == "overload":
            self._apply_overload_effect(actual_target, duration, engine)
        elif effect_type == "all_effects":
            self._apply_all_effects(actual_target, duration, engine)
    
    def _apply_burn_effect(self, target, duration: int, engine):
        """Applique l'effet de brûlure"""
        if hasattr(target, 'temporary_effects'):
            # Calculer les dégâts selon les vraies valeurs du jeu
            max_hp = getattr(target, 'max_hp', 100)
            current_hp = getattr(target, 'hp', 100)
            
            immediate_damage = int(max_hp * 0.01)  # 1% PV max
            damage_per_turn = int(current_hp * 0.03)  # 3% PV actuels
            
            # Appliquer les dégâts immédiats
            if hasattr(target, 'hp'):
                target.hp = max(0, target.hp - immediate_damage)
            
            # Ajouter l'effet temporaire
            burn_effect = {
                "type": "burn",
                "duration": duration,
                "damage_per_turn": damage_per_turn,
                "source": "elemental_attack"
            }
            target.temporary_effects.append(burn_effect)
    
    def _apply_freeze_effect(self, target, duration: int, engine):
        """Applique l'effet de gel"""
        if hasattr(target, 'temporary_effects'):
            freeze_effect = {
                "type": "freeze",
                "duration": duration,
                "effect": "stun",
                "source": "elemental_attack"
            }
            target.temporary_effects.append(freeze_effect)
    
    def _apply_poison_effect(self, target, duration: int, engine):
        """Applique l'effet de poison"""
        if hasattr(target, 'temporary_effects'):
            max_hp = getattr(target, 'max_hp', 100)
            damage_per_turn = int(max_hp * 0.03)  # 3% PV max
            
            poison_effect = {
                "type": "poison",
                "duration": duration,
                "damage_per_turn": damage_per_turn,
                "source": "elemental_attack"
            }
            target.temporary_effects.append(poison_effect)
    
    def _apply_heal_reduction_effect(self, target, duration: int, value: float, engine):
        """Applique la réduction de soins"""
        if hasattr(target, 'temporary_effects'):
            heal_reduction_effect = {
                "type": "heal_reduction",
                "duration": duration,
                "value": value,
                "source": "elemental_attack"
            }
            target.temporary_effects.append(heal_reduction_effect)
    
    def _apply_defense_reduction_effect(self, target, duration: int, value: float, engine):
        """Applique la réduction de défense"""
        if hasattr(target, 'temporary_effects'):
            defense_reduction_effect = {
                "type": "defense_reduction",
                "duration": duration,
                "value": value,
                "source": "elemental_attack"
            }
            target.temporary_effects.append(defense_reduction_effect)
    
    def _apply_dodge_boost_effect(self, target, duration: int, value: float, engine):
        """Applique le boost d'esquive"""
        # Initialiser temporary_effects si nécessaire
        if not hasattr(target, 'temporary_effects'):
            target.temporary_effects = []
        
        dodge_boost_effect = {
            "type": "dodge_boost",
            "duration": duration,
            "value": value,
            "source": "elemental_attack"
        }
        target.temporary_effects.append(dodge_boost_effect)
    
    def _apply_crit_boost_effect(self, target, duration: int, value: float, engine):
        """Applique le boost de critique"""
        # Initialiser temporary_effects si nécessaire
        if not hasattr(target, 'temporary_effects'):
            target.temporary_effects = []
        
        crit_boost_effect = {
            "type": "crit_boost",
            "duration": duration,
            "value": value,
            "source": "elemental_attack"
        }
        target.temporary_effects.append(crit_boost_effect)
        # Debug log
        target_name = getattr(target, 'name', 'Cible')
        print(f"[DEBUG] _apply_crit_boost_effect: {target_name} a maintenant {len(target.temporary_effects)} effets temporaires")
    
    def _apply_purify_effect(self, target, engine):
        """Applique l'effet de purification"""
        if hasattr(target, 'temporary_effects'):
            # Supprimer un effet négatif aléatoire
            negative_effects = [eff for eff in target.temporary_effects 
                              if eff.get("type") in ["burn", "poison", "freeze", "wet", "corruption"]]
            if negative_effects:
                effect_to_remove = random.choice(negative_effects)
                target.temporary_effects.remove(effect_to_remove)
    
    def _apply_steal_mana_effect(self, source, target, value: int, engine):
        """Applique le vol de mana"""
        if hasattr(target, 'mana') and hasattr(source, 'mana'):
            stolen_mana = min(value, target.mana)
            target.mana -= stolen_mana
            source.mana += stolen_mana
    
    def _apply_overload_effect(self, target, duration: int, engine):
        """Applique l'effet de surcharge (overload)"""
        if hasattr(target, 'temporary_effects'):
            overload_effect = {
                "type": "overload",
                "duration": duration,
                "source": "elemental_attack"
            }
            target.temporary_effects.append(overload_effect)
    
    def _apply_all_effects(self, target, duration: int, engine):
        """Applique tous les effets possibles (effet spécial)"""
        if hasattr(target, 'temporary_effects'):
            # Appliquer plusieurs effets aléatoires
            all_possible_effects = ["burn", "freeze", "poison", "fragile", "stunned", "corruption"]
            effects_to_apply = random.sample(all_possible_effects, min(3, len(all_possible_effects)))
            
            for effect_type in effects_to_apply:
                effect = {
                    "type": effect_type,
                    "duration": duration,
                    "source": "elemental_attack"
                }
                target.temporary_effects.append(effect)
    
    def _apply_direct_ability_effects(self, ability: Dict[str, Any], source, target, engine) -> List[str]:
        """Applique les effets directs d'une capacité (crit_boost, grant_passive, etc.)"""
        applied_effects = []
        
        # CORRECTION : Gérer les listes de cibles pour les capacités all_allies
        target_type = ability.get("target_type", "single_enemy")
        
        # Si target est une liste (capacité all_allies), traiter chaque cible individuellement
        if isinstance(target, list):
            for individual_target in target:
                individual_effects = self._apply_direct_ability_effects_to_single_target(ability, source, individual_target, engine)
                applied_effects.extend(individual_effects)
        else:
            # Cible unique
            individual_effects = self._apply_direct_ability_effects_to_single_target(ability, source, target, engine)
            applied_effects.extend(individual_effects)
        
        return applied_effects
    
    def _apply_direct_ability_effects_to_single_target(self, ability: Dict[str, Any], source, target, engine) -> List[str]:
        """Applique les effets directs d'une capacité à une cible unique"""
        applied_effects = []
        
        # Logique de ciblage pour une cible unique
        target_type = ability.get("target_type", "single_enemy")
        
        if target_type == "self":
            actual_target = source
        elif target_type in ["single_enemy", "single_ally", "random_enemy", "front_row", "all_enemies", "all_allies", "self_and_allies"]:
            actual_target = target
        elif target_type in ["random_multiple", "chain_enemies", "chain_random"]:
            actual_target = target
        else:
            actual_target = target
        
        # Appliquer crit_boost
        if "crit_boost" in ability:
            crit_boost = ability.get("crit_boost", 0.2)
            crit_duration = ability.get("crit_duration", 1)
            self._apply_crit_boost_effect(actual_target, crit_duration, crit_boost, engine)
            applied_effects.append(f"crit_boost_{crit_boost}")
            # Debug log
            target_name = getattr(actual_target, 'name', 'Cible')
            print(f"[DEBUG] crit_boost appliqué à {target_name}: +{crit_boost} pour {crit_duration} tours")
        
        # Appliquer grant_passive
        if "grant_passive" in ability:
            passive_id = ability.get("grant_passive")
            passive_duration = ability.get("passive_duration", 1)
            self._apply_grant_passive_effect(actual_target, passive_id, passive_duration, engine)
            applied_effects.append(f"grant_passive_{passive_id}")
            # Debug log
            target_name = getattr(actual_target, 'name', 'Cible')
            print(f"[DEBUG] grant_passive appliqué à {target_name}: passif {passive_id} pour {passive_duration} tours")
        
        # Appliquer dodge_boost
        if "dodge_boost" in ability:
            dodge_boost = ability.get("dodge_boost", 0.1)
            dodge_duration = ability.get("dodge_duration", 1)
            self._apply_dodge_boost_effect(actual_target, dodge_duration, dodge_boost, engine)
            applied_effects.append(f"dodge_boost_{dodge_boost}")
        
        # Appliquer crit_multiplier_boost
        if "crit_multiplier_boost" in ability:
            crit_multiplier_boost = ability.get("crit_multiplier_boost", 0.5)
            if hasattr(actual_target, 'crit_multiplier'):
                actual_target.crit_multiplier += crit_multiplier_boost
                applied_effects.append(f"crit_multiplier_boost_{crit_multiplier_boost}")
        
        # Appliquer reset_all_cooldowns
        if "reset_all_cooldowns" in ability and ability.get("reset_all_cooldowns", False):
            if hasattr(actual_target, 'ability_cooldowns'):
                for ability_id in actual_target.ability_cooldowns:
                    actual_target.ability_cooldowns[ability_id] = 0
                applied_effects.append("reset_all_cooldowns")
        
        return applied_effects
        
        # Appliquer grant_passive
        if "grant_passive" in ability:
            passive_id = ability.get("grant_passive")
            passive_duration = ability.get("passive_duration", 1)
            self._apply_grant_passive_effect(actual_target, passive_id, passive_duration, engine)
            applied_effects.append(f"grant_passive_{passive_id}")
            # Debug log
            target_name = getattr(actual_target, 'name', 'Cible')
            print(f"[DEBUG] grant_passive appliqué à {target_name}: passif {passive_id} pour {passive_duration} tours")
        
        # Appliquer dodge_boost
        if "dodge_boost" in ability:
            dodge_boost = ability.get("dodge_boost", 0.1)
            dodge_duration = ability.get("dodge_duration", 1)
            self._apply_dodge_boost_effect(actual_target, dodge_duration, dodge_boost, engine)
            applied_effects.append(f"dodge_boost_{dodge_boost}")
        
        # Appliquer crit_multiplier_boost
        if "crit_multiplier_boost" in ability:
            crit_multiplier_boost = ability.get("crit_multiplier_boost", 0.5)
            if hasattr(actual_target, 'crit_multiplier'):
                actual_target.crit_multiplier += crit_multiplier_boost
                applied_effects.append(f"crit_multiplier_boost_{crit_multiplier_boost}")
        
        # Appliquer reset_all_cooldowns
        if "reset_all_cooldowns" in ability and ability.get("reset_all_cooldowns", False):
            if hasattr(actual_target, 'ability_cooldowns'):
                for ability_id in actual_target.ability_cooldowns:
                    actual_target.ability_cooldowns[ability_id] = 0
                applied_effects.append("reset_all_cooldowns")
        
        return applied_effects
    
    def _apply_grant_passive_effect(self, target, passive_id: str, duration: int, engine):
        """Applique un passif temporaire"""
        if hasattr(target, 'temporary_effects'):
            passive_effect = {
                "type": "grant_passive",
                "passive_id": passive_id,
                "duration": duration,
                "source": "ability"
            }
            target.temporary_effects.append(passive_effect)
            # Debug log
            target_name = getattr(target, 'name', 'Cible')
            print(f"[DEBUG] _apply_grant_passive_effect: {target_name} a maintenant {len(target.temporary_effects)} effets temporaires")
        else:
            print(f"[DEBUG] _apply_grant_passive_effect: {getattr(target, 'name', 'Cible')} n'a pas d'attribut temporary_effects")
    
    def _apply_random_debuff_effect(self, target, duration: int, engine):
        """Applique un debuff aléatoire"""
        debuffs = ["burn", "poison", "freeze", "wet", "corruption", "fragile", "stunned", "overload"]
        random_debuff = random.choice(debuffs)
        
        if hasattr(target, 'temporary_effects'):
            debuff_effect = {
                "type": random_debuff,
                "duration": duration,
                "source": "elemental_attack"
            }
            target.temporary_effects.append(debuff_effect)
    
    def _apply_dispel_positive_effect(self, target, engine):
        """Dissipe les effets positifs"""
        if hasattr(target, 'temporary_effects'):
            positive_effects = [eff for eff in target.temporary_effects 
                              if eff.get("type") in ["shield", "dodge_boost", "crit_boost", "heal_reduction"]]
            if positive_effects:
                effect_to_remove = random.choice(positive_effects)
                target.temporary_effects.remove(effect_to_remove)
    
    def _apply_damage_boost_effect(self, target, duration: int, value: float, engine):
        """Applique le boost de dégâts"""
        if hasattr(target, 'temporary_effects'):
            damage_boost_effect = {
                "type": "damage_boost",
                "duration": duration,
                "value": value,
                "source": "elemental_attack"
            }
            target.temporary_effects.append(damage_boost_effect)
    
    def check_elemental_interactions(self, element1_id: str, element2_id: str) -> List[str]:
        """Vérifie les interactions élémentaires et retourne les effets en chaîne"""
        chain_effects = []
        
        for interaction_id, interaction_data in self.database.get("elemental_interactions", {}).items():
            elements = interaction_data.get("elements", [])
            if element1_id in elements and element2_id in elements:
                chain_effects.extend(interaction_data.get("chain_effects", []))
        
        return chain_effects
    
    def check_special_combos(self, active_effects: List[str]) -> List[str]:
        """Vérifie les combos spéciaux et retourne les effets en chaîne"""
        chain_effects = []
        
        for combo_id, combo_data in self.database.get("special_combos", {}).items():
            required_effects = combo_data.get("effects", [])
            if all(effect in active_effects for effect in required_effects):
                chain_effects.extend(combo_data.get("chain_effects", []))
        
        return chain_effects
    
    def apply_ability_effects(self, ability_id: str, source, target, engine) -> EffectResult:
        """Applique tous les effets d'une capacité"""
        ability = self.get_ability(ability_id)
        if not ability:
            return EffectResult(success=False, message="Capacité non trouvée")
        
        effects_applied = []
        chain_effects = []
        target_type = ability.get("target_type", "single_enemy")
        
        # CORRECTION : Gérer les listes de cibles pour les capacités all_allies
        if target_type == "all_allies" and isinstance(target, list):
            # Appliquer les effets à chaque cible individuellement
            for individual_target in target:
                individual_result = self._apply_ability_effects_to_single_target(ability_id, source, individual_target, engine, ability)
                if individual_result:
                    effects_applied.extend(individual_result.get('effects_applied', []))
                    chain_effects.extend(individual_result.get('chain_effects', []))
        else:
            # Cible unique ou autre type de ciblage
            individual_result = self._apply_ability_effects_to_single_target(ability_id, source, target, engine, ability)
            if individual_result:
                effects_applied.extend(individual_result.get('effects_applied', []))
                chain_effects.extend(individual_result.get('chain_effects', []))
        
        return EffectResult(
            success=True,
            effects_applied=effects_applied,
            chain_effects=chain_effects,
            message=f"Capacité {ability.get('name', '')} appliquée"
        )
    
    def _apply_ability_effects_to_single_target(self, ability_id: str, source, target, engine, ability) -> Dict:
        """Applique tous les effets d'une capacité à une cible unique"""
        effects_applied = []
        chain_effects = []
        
        # Appliquer les effets de base de la capacité
        effect_ids = ability.get("effect_ids", [])
        for effect_id in effect_ids:
            effect_data = self.get_base_effect(effect_id)
            if effect_data:
                effect_name = effect_data.get("name", "")
                effects_applied.append(effect_name)
                
                # Appliquer l'effet selon son type
                self._apply_base_effect(effect_data, source, target, engine)
        
        # Appliquer les effets directs de la capacité
        direct_effects = self._apply_direct_ability_effects_to_single_target(ability, source, target, engine)
        effects_applied.extend(direct_effects)
        
        # Appliquer les effets automatiques de l'élément
        element_id = ability.get("element", "12")
        ability_target_type = ability.get("target_type", "single_enemy")
        elemental_effects = self.apply_elemental_attack_effects(element_id, source, target, engine, ability_target_type)
        effects_applied.extend(elemental_effects)
        
        # Vérifier les interactions et combos
        if hasattr(target, 'temporary_effects'):
            active_effects = [eff.get("type") for eff in target.temporary_effects]
            
            # Interactions élémentaires
            source_element = self.get_element_name(element_id)
            target_element = getattr(target, 'element', 'NEUTRE')
            target_element_id = self.get_element_id(target_element)
            
            interaction_chains = self.check_elemental_interactions(element_id, target_element_id)
            chain_effects.extend(interaction_chains)
            
            # Combos spéciaux
            combo_chains = self.check_special_combos(active_effects)
            chain_effects.extend(combo_chains)
        
        return {
            'effects_applied': effects_applied,
            'chain_effects': chain_effects
        }
    
    def _apply_base_effect(self, effect_data: Dict[str, Any], source, target, engine):
        """Applique un effet de base"""
        effect_type = effect_data.get("name", "")
        duration = effect_data.get("default_duration", 1)
        
        if effect_type == "burn":
            self._apply_burn_effect(target, duration, engine)
        elif effect_type == "freeze":
            self._apply_freeze_effect(target, duration, engine)
        elif effect_type == "poison":
            self._apply_poison_effect(target, duration, engine)
        elif effect_type == "wet":
            self._apply_wet_effect(target, duration, engine)
        elif effect_type == "corruption":
            self._apply_corruption_effect(target, duration, engine)
        elif effect_type == "fragile":
            self._apply_fragile_effect(target, duration, engine)
        elif effect_type == "stunned":
            self._apply_stunned_effect(target, duration, engine)
        elif effect_type == "shield":
            self._apply_shield_effect(target, duration, engine)
        elif effect_type == "heal":
            self._apply_heal_effect(target, duration, engine)
        elif effect_type == "purify":
            self._apply_purify_effect(target, engine)
    
    def _apply_wet_effect(self, target, duration: int, engine):
        """Applique l'effet mouillé"""
        if hasattr(target, 'temporary_effects'):
            wet_effect = {
                "type": "wet",
                "duration": duration,
                "damage_reduction": 0.20,  # -20% dégâts
                "source": "ability"
            }
            target.temporary_effects.append(wet_effect)
    
    def _apply_corruption_effect(self, target, duration: int, engine):
        """Applique l'effet de corruption"""
        if hasattr(target, 'temporary_effects'):
            max_hp = getattr(target, 'max_hp', 100)
            damage_per_turn = int(max_hp * 0.02)  # 2% PV max
            
            corruption_effect = {
                "type": "corruption",
                "duration": duration,
                "damage_per_turn": damage_per_turn,
                "stat_reduction": 0.10,  # -10% toutes stats
                "source": "ability"
            }
            target.temporary_effects.append(corruption_effect)
    
    def _apply_fragile_effect(self, target, duration: int, engine):
        """Applique l'effet fragilisé"""
        if hasattr(target, 'temporary_effects'):
            fragile_effect = {
                "type": "fragile",
                "duration": duration,
                "defense_reduction": 0.20,  # -20% défense
                "source": "ability"
            }
            target.temporary_effects.append(fragile_effect)
    
    def _apply_stunned_effect(self, target, duration: int, engine):
        """Applique l'effet étourdi"""
        if hasattr(target, 'temporary_effects'):
            stunned_effect = {
                "type": "stunned",
                "duration": duration,
                "effect": "stun",
                "source": "ability"
            }
            target.temporary_effects.append(stunned_effect)
    
    def _apply_shield_effect(self, target, duration: int, engine):
        """Applique l'effet bouclier"""
        if hasattr(target, 'temporary_effects'):
            shield_effect = {
                "type": "shield",
                "duration": duration,
                "damage_absorption": True,
                "source": "ability"
            }
            target.temporary_effects.append(shield_effect)
    
    def _apply_heal_effect(self, target, duration: int, engine):
        """Applique l'effet de soin"""
        if hasattr(target, 'hp') and hasattr(target, 'max_hp'):
            heal_amount = int(target.max_hp * 0.20)  # 20% PV max
            target.hp = min(target.max_hp, target.hp + heal_amount)
