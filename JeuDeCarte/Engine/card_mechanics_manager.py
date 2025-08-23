# card_mechanics_manager.py - Gestionnaire de mécaniques pour JeuDeCarte

import json
import os
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

class EffectType(Enum):
    DAMAGE = "damage"
    HEAL = "heal"
    SHIELD = "shield"
    BUFF = "buff"
    DEBUFF = "debuff"
    DISPEL = "dispel"
    TEMPORARY_EFFECT = "temporary_effect"
    DRAW = "draw"
    MANA = "mana"
    SILENCE = "silence"
    STUN = "stun"
    POISON = "poison"
    BURN = "burn"
    WET = "wet"
    FREEZE = "freeze"
    SCALD = "scald"
    STEAM = "steam"
    CORRUPTION = "corruption"
    ANNIHILATION = "annihilation"
    ARCANIC_MAGIC = "arcanic_magic"
    OVERLOAD = "overload"
    FRAGILE = "fragile"
    STUNNED = "stunned"
    ASPIRATION = "aspiration"

class TargetType(Enum):
    ENEMY = "enemy"
    ALLY = "ally"
    ALL_ENEMIES = "all_enemies"
    ALL_ALLIES = "all_allies"
    SELF = "self"
    ANY = "any"
    ZONE = "zone"
    LINE = "line"

@dataclass
class EffectContext:
    """Contexte pour l'application d'un effet"""
    source: Any
    target: Any
    caster: Any
    engine: Any
    additional_data: Dict[str, Any] = None

class TemporaryEffect:
    """Classe représentant un effet temporaire"""
    def __init__(self, effect_type: str, duration: int, intensity: int = 1, 
                 source_element: str = None, description: str = ""):
        self.effect_type = effect_type
        self.duration = duration
        self.original_duration = duration
        self.intensity = intensity
        self.source_element = source_element
        self.description = description

class CardMechanicsManager:
    """Gestionnaire principal des mécaniques de cartes"""
    
    def __init__(self):
        self.elemental_interactions = self._initialize_elemental_interactions()
        self.temporary_effects = self._initialize_temporary_effects()
        
    def _initialize_elemental_interactions(self) -> Dict[str, Dict[str, float]]:
        """Initialise les interactions élémentaires selon la documentation"""
        return {
            "Feu": {
                "Terre": 1.2,  # +20% dégâts
                "Eau": 0.95,   # -5% dégâts
                "Glace": 1.0,  # Normal
                "Air": 1.0,    # Normal
                "Lumière": 1.0, # Normal
                "Ténèbres": 1.0, # Normal
                "Arcanique": 1.0, # Normal
                "Poison": 1.0,  # Normal
                "Néant": 1.0,   # Normal
                "NEUTRE": 1.0   # Normal
            },
            "Eau": {
                "Feu": 1.2,     # +20% dégâts
                "Terre": 0.95,  # -5% dégâts
                "Air": 1.0,     # Normal
                "Foudre": 0.95, # -5% dégâts
                "Lumière": 1.0, # Normal
                "Ténèbres": 1.0, # Normal
                "Arcanique": 1.0, # Normal
                "Poison": 1.0,  # Normal
                "Néant": 1.0,   # Normal
                "NEUTRE": 1.0   # Normal
            },
            "Terre": {
                "Air": 1.2,     # +20% dégâts
                "Eau": 0.95,    # -5% dégâts
                "Feu": 1.0,     # Normal
                "Lumière": 1.0, # Normal
                "Ténèbres": 1.0, # Normal
                "Arcanique": 1.0, # Normal
                "Poison": 1.0,  # Normal
                "Néant": 1.0,   # Normal
                "NEUTRE": 1.0   # Normal
            },
            "Air": {
                "Eau": 1.2,     # +20% dégâts
                "Terre": 0.95,  # -5% dégâts
                "Feu": 1.0,     # Normal
                "Glace": 1.0,   # Normal
                "Lumière": 1.0, # Normal
                "Ténèbres": 1.0, # Normal
                "Arcanique": 1.0, # Normal
                "Poison": 1.0,  # Normal
                "Néant": 1.0,   # Normal
                "NEUTRE": 1.0   # Normal
            },
            "Lumière": {
                "Ténèbres": 1.3, # +30% dégâts
                "Néant": 1.3,    # +30% dégâts
                "Feu": 1.0,      # Normal
                "Eau": 1.0,      # Normal
                "Terre": 1.0,    # Normal
                "Air": 1.0,      # Normal
                "Arcanique": 1.0, # Normal
                "Poison": 1.0,   # Normal
                "NEUTRE": 1.0    # Normal
            },
            "Ténèbres": {
                "Lumière": 1.3,  # +30% dégâts
                "Feu": 1.0,      # Normal
                "Eau": 1.0,      # Normal
                "Terre": 1.0,    # Normal
                "Air": 1.0,      # Normal
                "Arcanique": 1.0, # Normal
                "Poison": 1.0,   # Normal
                "Néant": 1.0,    # Normal
                "NEUTRE": 1.0    # Normal
            },
            "Foudre": {
                "Eau": 1.2,      # +20% dégâts
                "Feu": 1.0,      # Normal
                "Terre": 1.0,    # Normal
                "Air": 1.0,      # Normal
                "Lumière": 1.0,  # Normal
                "Ténèbres": 1.0, # Normal
                "Arcanique": 1.0, # Normal
                "Poison": 1.0,   # Normal
                "Néant": 1.0,    # Normal
                "NEUTRE": 1.0    # Normal
            },
            "Glace": {
                "Air": 1.2,      # +20% dégâts
                "Feu": 1.0,      # Normal
                "Eau": 1.0,      # Normal
                "Terre": 1.0,    # Normal
                "Lumière": 1.0,  # Normal
                "Ténèbres": 1.0, # Normal
                "Arcanique": 1.0, # Normal
                "Poison": 1.0,   # Normal
                "Néant": 1.0,    # Normal
                "NEUTRE": 1.0    # Normal
            },
            "Poison": {
                "Arcanique": 0.95, # -5% dégâts
                "Feu": 1.15,       # +15% dégâts
                "Eau": 1.15,       # +15% dégâts
                "Terre": 1.15,     # +15% dégâts
                "Air": 1.15,       # +15% dégâts
                "Lumière": 1.15,   # +15% dégâts
                "Ténèbres": 1.15,  # +15% dégâts
                "Foudre": 1.15,    # +15% dégâts
                "Glace": 1.15,     # +15% dégâts
                "Néant": 1.15,     # +15% dégâts
                "NEUTRE": 1.15     # +15% dégâts
            },
            "Arcanique": {
                "Poison": 1.3,     # +30% dégâts
                "Feu": 1.0,        # Normal
                "Eau": 1.0,        # Normal
                "Terre": 1.0,      # Normal
                "Air": 1.0,        # Normal
                "Lumière": 1.0,    # Normal
                "Ténèbres": 1.0,   # Normal
                "Foudre": 1.0,     # Normal
                "Glace": 1.0,      # Normal
                "Néant": 1.0,      # Normal
                "NEUTRE": 1.0      # Normal
            },
            "Néant": {
                "Lumière": 0.95,   # -5% dégâts
                "Feu": 1.1,        # +10% dégâts
                "Eau": 1.1,        # +10% dégâts
                "Terre": 1.1,      # +10% dégâts
                "Air": 1.1,        # +10% dégâts
                "Ténèbres": 1.1,   # +10% dégâts
                "Foudre": 1.1,     # +10% dégâts
                "Glace": 1.1,      # +10% dégâts
                "Arcanique": 1.1,  # +10% dégâts
                "Poison": 1.1,     # +10% dégâts
                "NEUTRE": 1.1      # +10% dégâts
            },
            "NEUTRE": {
                "Feu": 1.0,        # Normal
                "Eau": 1.0,        # Normal
                "Terre": 1.0,      # Normal
                "Air": 1.0,        # Normal
                "Lumière": 1.0,    # Normal
                "Ténèbres": 1.0,   # Normal
                "Foudre": 1.0,     # Normal
                "Glace": 1.0,      # Normal
                "Arcanique": 1.0,  # Normal
                "Poison": 1.0,     # Normal
                "Néant": 1.0       # Normal
            }
        }
    
    def _initialize_temporary_effects(self) -> Dict[str, Dict[str, Any]]:
        """Initialise les effets temporaires selon la documentation"""
        return {
            "poison": {
                "duration": 1,
                "damage_per_turn": 0.03,  # 3% PV max
                "cumulative": True,
                "remedy": ["time", "heal", "purification"],
                "elements": ["Poison", "Ténèbres"]
            },
            "burn": {
                "duration": 3,
                "immediate_damage": 0.01,  # 1% PV max
                "damage_per_turn": 0.03,   # 3% PV actuel
                "cumulative": True,
                "remedy": ["time", "water", "purification", "heal"],
                "elements": ["Feu", "Foudre"]
            },
            "wet": {
                "duration": 2,
                "damage_reduction": 0.20,  # -20% dégâts
                "cumulative": False,
                "remedy": ["fire", "time"],
                "elements": ["Eau", "Glace"]
            },
            "freeze": {
                "duration": 1,
                "effect": "stun",  # Ne peut pas attaquer
                "cumulative": True,
                "remedy": ["fire", "time", "purification"],
                "elements": ["Glace", "Air"]
            },
            "scald": {
                "duration": 1,
                "heal_reduction": 0.50,  # -50% soins
                "cumulative": False,
                "remedy": ["time", "purification"],
                "elements": ["Feu"]
            },
            "steam": {
                "duration": 1,
                "precision_reduction": 0.20,  # -20% précision
                "cumulative": False,
                "remedy": ["time"],
                "elements": ["Feu"]
            },
            "corruption": {
                "duration": 3,
                "damage_per_turn": 0.02,  # 2% PV max
                "stat_reduction": 0.10,    # -10% toutes stats
                "cumulative": True,
                "remedy": ["light", "purification"],
                "elements": ["Ténèbres", "Néant"]
            },
            "annihilation": {
                "duration": 1,
                "damage": 0.10,  # 10% PV max
                "effect": "remove_positive_effects",
                "cumulative": False,
                "remedy": ["light"],
                "elements": ["Néant"]
            },
            "overload": {
                "duration": 2,
                "damage_per_turn": 0.05,  # 5% PV actuel
                "cumulative": True,
                "remedy": ["time", "purification"],
                "elements": ["Foudre"]
            },
            "fragile": {
                "duration": 2,
                "defense_reduction": 0.20,  # -20% défense
                "cumulative": True,
                "remedy": ["time", "purification"],
                "elements": ["Terre", "Glace"]
            },
            "stunned": {
                "duration": 1,
                "effect": "stun",  # Ne peut pas attaquer
                "cumulative": True,
                "remedy": ["time", "purification"],
                "elements": ["Air", "Foudre"]
            },
            "aspiration": {
                "duration": 1,
                "mana_reduction": 1,  # -1 mana
                "cumulative": True,
                "remedy": ["time"],
                "elements": ["Arcanique"]
            },
            "shield": {
                "duration": 2,
                "damage_absorption": True,  # Absorbe les dégâts
                "cumulative": True,
                "remedy": ["time"],
                "elements": ["Terre", "Lumière"]
            }
        }
    
    def get_elemental_multiplier(self, attacker_element: str, defender_element: str) -> float:
        """Calcule le multiplicateur de dégâts basé sur les interactions élémentaires"""
        if attacker_element not in self.elemental_interactions:
            return 1.0
        
        if defender_element not in self.elemental_interactions[attacker_element]:
            return 1.0
        
        return self.elemental_interactions[attacker_element][defender_element]
    
    def apply_temporary_effect(self, target: Any, effect_type: str, duration: int, 
                             intensity: int = 1, source_element: str = None) -> bool:
        """Applique un effet temporaire à une cible"""
        try:
            if not hasattr(target, 'temporary_effects'):
                target.temporary_effects = []
            
            # Vérifier si l'effet existe déjà
            existing_effect = None
            for effect in target.temporary_effects:
                if effect.effect_type == effect_type:
                    existing_effect = effect
                    break
            
            if existing_effect:
                # Effet cumulatif
                if self.temporary_effects.get(effect_type, {}).get("cumulative", False):
                    old_intensity = existing_effect.intensity
                    existing_effect.intensity += intensity
                    existing_effect.duration = max(existing_effect.duration, duration)
                    print(f"[DEBUG] Effet {effect_type} cumulé sur {target.name}: {old_intensity} → {existing_effect.intensity}")
                    return True
                else:
                    # Remplacer l'effet existant
                    target.temporary_effects.remove(existing_effect)
                    print(f"[DEBUG] Effet {effect_type} existant remplacé sur {target.name}")
            
            # Créer un nouvel effet
            new_effect = TemporaryEffect(
                effect_type=effect_type,
                duration=duration,
                intensity=intensity,
                source_element=source_element
            )
            target.temporary_effects.append(new_effect)
            print(f"[DEBUG] Nouvel effet {effect_type} créé sur {target.name}: intensité={intensity}, durée={duration}")
            return True
            
        except Exception as e:
            print(f"[ERREUR] Erreur dans apply_temporary_effect: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def process_temporary_effects(self, target: Any) -> List[str]:
        """Traite les effets temporaires d'une cible et retourne les logs"""
        logs = []
        if not hasattr(target, 'temporary_effects'):
            return logs
        
        effects_to_remove = []
        
        for effect in target.temporary_effects:
            effect.duration -= 1
            logs.extend(self._apply_effect_turn(target, effect))
            
            if effect.duration <= 0:
                effects_to_remove.append(effect)
        
        # Supprimer les effets expirés
        for effect in effects_to_remove:
            target.temporary_effects.remove(effect)
            logs.append(f"[EFFET] {effect.effect_type} expiré sur {target.name}")
        
        return logs
    
    def _apply_effect_turn(self, target: Any, effect: TemporaryEffect) -> List[str]:
        """Applique les effets d'un tour pour un effet temporaire"""
        logs = []
        effect_config = self.temporary_effects.get(effect.effect_type, {})
        
        if effect.effect_type == "poison":
            # Dégâts basés sur les PV max
            max_hp = target.stats.get("max_hp", 100)
            damage = int(max_hp * effect_config["damage_per_turn"] * effect.intensity)
            current_hp = target.stats.get("hp", 0)
            target.stats["hp"] = max(0, current_hp - damage)
            logs.append(f"[POISON] {target.name} subit {damage} dégâts de poison (HP: {current_hp} → {target.stats['hp']})")
            
        elif effect.effect_type == "burn":
            # Dégâts basés sur les PV actuels
            current_hp = target.stats.get("hp", 0)
            damage = int(current_hp * effect_config["damage_per_turn"] * effect.intensity)
            target.stats["hp"] = max(0, current_hp - damage)
            logs.append(f"[BRÛLURE] {target.name} subit {damage} dégâts de brûlure (HP: {current_hp} → {target.stats['hp']})")
            
        elif effect.effect_type == "corruption":
            # Dégâts basés sur les PV max
            max_hp = target.stats.get("max_hp", 100)
            damage = int(max_hp * effect_config["damage_per_turn"] * effect.intensity)
            current_hp = target.stats.get("hp", 0)
            target.stats["hp"] = max(0, current_hp - damage)
            logs.append(f"[CORRUPTION] {target.name} subit {damage} dégâts de corruption (HP: {current_hp} → {target.stats['hp']})")
            
        elif effect.effect_type == "overload":
            # Dégâts basés sur les PV actuels
            current_hp = target.stats.get("hp", 0)
            damage = int(current_hp * effect_config["damage_per_turn"] * effect.intensity)
            target.stats["hp"] = max(0, current_hp - damage)
            logs.append(f"[SURCHARGE] {target.name} subit {damage} dégâts électriques (HP: {current_hp} → {target.stats['hp']})")
            
        elif effect.effect_type == "annihilation":
            # Dégâts basés sur les PV max
            max_hp = target.stats.get("max_hp", 100)
            damage = int(max_hp * effect_config["damage"])
            current_hp = target.stats.get("hp", 0)
            target.stats["hp"] = max(0, current_hp - damage)
            logs.append(f"[ANNIHILATION] {target.name} subit {damage} dégâts massifs (HP: {current_hp} → {target.stats['hp']})")
            
            # Supprimer les effets positifs
            if hasattr(target, 'temporary_effects'):
                positive_effects = [e for e in target.temporary_effects if e.effect_type in ["shield", "buff"]]
                for pos_effect in positive_effects:
                    target.temporary_effects.remove(pos_effect)
                if positive_effects:
                    logs.append(f"[ANNIHILATION] Effets positifs supprimés sur {target.name}")
        
        elif effect.effect_type == "fragile":
            # Réduction de défense
            current_defense = target.stats.get("defense", 0)
            reduction = int(current_defense * effect_config["defense_reduction"] * effect.intensity)
            target.stats["defense"] = max(0, current_defense - reduction)
            logs.append(f"[FRAGILE] {target.name} perd {reduction} défense ({current_defense} → {target.stats['defense']})")
        
        elif effect.effect_type == "wet":
            # Réduction des dégâts (appliquée lors des attaques)
            logs.append(f"[HUMIDITÉ] {target.name} a ses dégâts réduits de {int(effect_config['damage_reduction'] * 100)}%")
        
        elif effect.effect_type == "stunned":
            # Empêche l'attaque
            logs.append(f"[ÉTOURDISSEMENT] {target.name} ne peut pas attaquer ce tour")
        
        elif effect.effect_type == "shield":
            # Le bouclier n'a pas d'effet par tour, il absorbe les dégâts quand ils arrivent
            # On ne fait que vérifier qu'il est actif
            logs.append(f"[BOUCLIER] {target.name} a un bouclier actif de {effect.intensity} points")
        
        return logs
    
    def handle_card_play(self, card_data: Dict[str, Any], context: EffectContext) -> bool:
        """Gère le jeu d'une carte"""
        try:
            card_type = card_data.get("card_type", "")
            
            # Nettoyer le type de carte (enlever le préfixe CARDTYPE. si présent)
            if card_type.startswith("CARDTYPE."):
                card_type = card_type.replace("CARDTYPE.", "")
            
            if card_type == "SPELL":
                return self._handle_spell_card(card_data, context)
            elif card_type == "UNIT":
                return self._handle_unit_card(card_data, context)
            else:
                if context.engine and hasattr(context.engine, 'log'):
                    context.engine.log.append(f"[MÉCANIQUES] Type de carte non reconnu: {card_type}")
                return False
                
        except Exception as e:
            error_msg = f"[ERREUR] Erreur lors du traitement de la carte: {e}"
            if context.engine and hasattr(context.engine, 'log'):
                context.engine.log.append(error_msg)
            import traceback
            traceback.print_exc()
            return False
    
    def _handle_spell_card(self, card_data: Dict[str, Any], context: EffectContext) -> bool:
        """Gère le jeu d'une carte de sort"""
        effects = card_data.get("effects", [])
        success = True
        
        for effect in effects:
            effect_type = effect.get("type")
            amount = effect.get("amount", 0)
            target_type = effect.get("target", "enemy")
            
            # Déterminer la cible
            targets = self._get_target(context, target_type)
            
            if not targets:
                if context.engine and hasattr(context.engine, 'log'):
                    context.engine.log.append(f"[MÉCANIQUES] Cible non trouvée pour {target_type}")
                continue
            
            # Gérer les cibles multiples
            if isinstance(targets, list):
                for target in targets:
                    if target:
                        success &= self._apply_effect_to_target(target, effect_type, amount, card_data, context)
            else:
                # Cible unique
                success &= self._apply_effect_to_target(targets, effect_type, amount, card_data, context)
        
        return success
    
    def _apply_effect_to_target(self, target: Any, effect_type: str, amount: int, card_data: Dict[str, Any], context: EffectContext) -> bool:
        """Applique un effet à une cible spécifique"""
        try:
            if effect_type == "damage":
                return self._apply_damage(target, amount, card_data.get("element", "NEUTRE"), context)
            elif effect_type == "heal":
                return self._apply_heal(target, amount, context)
            elif effect_type == "shield":
                return self._apply_shield(target, amount, context)
            elif effect_type == "dispel":
                return self._apply_dispel(target, context)
            elif effect_type == "buff":
                return self._apply_buff(target, amount, card_data, context)
            elif effect_type == "debuff":
                return self._apply_debuff(target, amount, card_data, context)
            else:
                if context.engine and hasattr(context.engine, 'log'):
                    context.engine.log.append(f"[ERREUR] Type d'effet non reconnu: {effect_type}")
                return False
                
        except Exception as e:
            error_msg = f"[ERREUR] Erreur dans _apply_effect_to_target: {e}"
            if context.engine and hasattr(context.engine, 'log'):
                context.engine.log.append(error_msg)
            import traceback
            traceback.print_exc()
            return False
    
    def _apply_buff(self, target: Any, amount: int, card_data: Dict[str, Any], context: EffectContext) -> bool:
        """Applique un buff (augmentation de stats)"""
        try:
            stat_type = card_data.get("stat_type", "attack")  # Par défaut, buff d'attaque
            
            if hasattr(target, 'stats'):
                # Unités
                current_value = target.stats.get(stat_type, 0)
                target.stats[stat_type] = current_value + amount
                if context.engine:
                    context.engine.log.append(f"[BUFF] {target.name} gagne +{amount} {stat_type} ({current_value} → {target.stats[stat_type]})")
            elif hasattr(target, 'base_stats'):
                # Héros
                current_value = target.base_stats.get(stat_type, 0)
                target.base_stats[stat_type] = current_value + amount
                if context.engine:
                    context.engine.log.append(f"[BUFF] {target.name} gagne +{amount} {stat_type} ({current_value} → {target.base_stats[stat_type]})")
            
            return True
            
        except Exception as e:
            print(f"[ERREUR] Erreur lors de l'application du buff: {e}")
            return False
    
    def _apply_debuff(self, target: Any, amount: int, card_data: Dict[str, Any], context: EffectContext) -> bool:
        """Applique un debuff (réduction de stats)"""
        try:
            stat_type = card_data.get("stat_type", "attack")  # Par défaut, debuff d'attaque
            
            if hasattr(target, 'stats'):
                # Unités
                current_value = target.stats.get(stat_type, 0)
                target.stats[stat_type] = max(0, current_value - amount)  # Ne pas descendre en dessous de 0
                if context.engine:
                    context.engine.log.append(f"[DEBUFF] {target.name} perd -{amount} {stat_type} ({current_value} → {target.stats[stat_type]})")
            elif hasattr(target, 'base_stats'):
                # Héros
                current_value = target.base_stats.get(stat_type, 0)
                target.base_stats[stat_type] = max(0, current_value - amount)
                if context.engine:
                    context.engine.log.append(f"[DEBUFF] {target.name} perd -{amount} {stat_type} ({current_value} → {target.base_stats[stat_type]})")
            
            return True
            
        except Exception as e:
            print(f"[ERREUR] Erreur lors de l'application du debuff: {e}")
            return False
    
    def _handle_unit_card(self, card_data: Dict[str, Any], context: EffectContext) -> bool:
        """Gère le jeu d'une carte d'unité"""
        # Les unités sont déjà en jeu selon la documentation
        # Cette fonction gère les capacités spéciales des unités
        return True
    
    def _get_target(self, context: EffectContext, target_type: str) -> Any:
        """Détermine la cible selon le type de ciblage"""
        if target_type == "enemy":
            return context.target
        elif target_type == "ally":
            return context.target
        elif target_type == "self":
            return context.caster
        elif target_type == "all_enemies":
            # Retourner tous les ennemis vivants
            if hasattr(context.engine, 'players') and len(context.engine.players) >= 2:
                opponent = context.caster.opponent
                enemies = []
                # Unités ennemies vivantes
                for unit in opponent.units:
                    if hasattr(unit, 'stats') and unit.stats.get('hp', 0) > 0:
                        enemies.append(unit)
                # Héros ennemi activé
                if opponent.hero and getattr(opponent.hero, 'is_active', False):
                    enemies.append(opponent.hero)
                return enemies
        elif target_type == "all_allies":
            # Retourner tous les alliés vivants
            allies = []
            # Unités alliées vivantes
            for unit in context.caster.units:
                if hasattr(unit, 'stats') and unit.stats.get('hp', 0) > 0:
                    allies.append(unit)
            # Héros allié activé
            if context.caster.hero and getattr(context.caster.hero, 'is_active', False):
                allies.append(context.caster.hero)
            return allies
        
        return context.target
    
    def _apply_damage(self, target: Any, amount: int, element: str, context: EffectContext) -> bool:
        """Applique des dégâts avec interactions élémentaires et boucliers"""
        try:
            # Calculer le multiplicateur élémentaire
            target_element = getattr(target, 'element', 'NEUTRE')
            multiplier = self.get_elemental_multiplier(element, target_element)
            
            # Appliquer les dégâts
            final_damage = int(amount * multiplier)
            
            # Vérifier et utiliser les boucliers
            shield_absorbed = 0
            if hasattr(target, 'temporary_effects'):
                shield_effects = [e for e in target.temporary_effects if e.effect_type == "shield"]
                for shield_effect in shield_effects:
                    if shield_effect.intensity > 0:
                        # Le bouclier absorbe les dégâts
                        absorbed = min(shield_effect.intensity, final_damage)
                        shield_effect.intensity -= absorbed
                        final_damage -= absorbed
                        shield_absorbed += absorbed
                        
                        if context.engine:
                            context.engine.log.append(f"[BOUCLIER] {target.name} absorbe {absorbed} dégâts avec son bouclier")
                        
                        # Si le bouclier est épuisé, le supprimer
                        if shield_effect.intensity <= 0:
                            target.temporary_effects.remove(shield_effect)
                            if context.engine:
                                context.engine.log.append(f"[BOUCLIER] Bouclier de {target.name} épuisé")
                        
                        # Si tous les dégâts sont absorbés, arrêter
                        if final_damage <= 0:
                            break
            
            # Appliquer les dégâts restants selon le type d'entité
            if final_damage > 0:
                if hasattr(target, 'stats'):
                    # Unités
                    current_hp = target.stats.get("hp", 0)
                    target.stats["hp"] = max(0, current_hp - final_damage)
                elif hasattr(target, 'base_stats'):
                    # Héros
                    current_hp = target.base_stats.get("hp", 0)
                    target.base_stats["hp"] = max(0, current_hp - final_damage)
                elif hasattr(target, 'hp'):
                    # Entité avec attribut hp direct
                    target.hp = max(0, target.hp - final_damage)
                else:
                    print(f"[ERREUR] Impossible d'appliquer des dégâts à {target.name} - structure inconnue")
                    return False
                
                # Log du dégât
                if context.engine:
                    context.engine.log.append(f"[DÉGÂTS] {target.name} subit {final_damage} dégâts ({element} vs {target_element}, x{multiplier:.2f})")
            else:
                # Tous les dégâts absorbés par le bouclier
                if context.engine:
                    context.engine.log.append(f"[BOUCLIER] {target.name} absorbe tous les dégâts avec son bouclier")
            
            # Vérifier si l'entité est morte
            if self._is_entity_dead(target):
                if context.engine:
                    context.engine.log.append(f"[MORT] {target.name} est mort")
            
            return True
            
        except Exception as e:
            print(f"[ERREUR] Erreur lors de l'application des dégâts: {e}")
            return False
    
    def _is_entity_dead(self, entity: Any) -> bool:
        """Vérifie si une entité est morte"""
        if hasattr(entity, 'stats'):
            return entity.stats.get("hp", 0) <= 0
        elif hasattr(entity, 'base_stats'):
            return entity.base_stats.get("hp", 0) <= 0
        elif hasattr(entity, 'hp'):
            return entity.hp <= 0
        return False
    
    def _apply_heal(self, target: Any, amount: int, context: EffectContext) -> bool:
        """Applique des soins"""
        try:
            # Appliquer les soins selon le type d'entité
            if hasattr(target, 'stats'):
                # Unités
                current_hp = target.stats.get("hp", 0)
                max_hp = target.stats.get("max_hp", 100)
                target.stats["hp"] = min(max_hp, current_hp + amount)
            elif hasattr(target, 'base_stats'):
                # Héros
                current_hp = target.base_stats.get("hp", 0)
                max_hp = target.base_stats.get("max_hp", 100)
                target.base_stats["hp"] = min(max_hp, current_hp + amount)
            elif hasattr(target, 'hp') and hasattr(target, 'max_hp'):
                # Entité avec attributs hp/max_hp directs
                target.hp = min(target.max_hp, target.hp + amount)
            else:
                print(f"[ERREUR] Impossible d'appliquer des soins à {target.name} - structure inconnue")
                return False
            
            if context.engine:
                context.engine.log.append(f"[SOIN] {target.name} soigné de {amount} PV")
            
            return True
            
        except Exception as e:
            print(f"[ERREUR] Erreur lors de l'application des soins: {e}")
            return False
    
    def _apply_shield(self, target: Any, amount: int, context: EffectContext) -> bool:
        """Applique un bouclier"""
        try:
            if context.engine:
                context.engine.log.append(f"[DEBUG] Application du bouclier sur {target.name} - montant: {amount}")
            
            # Vérifier si la cible a déjà des effets temporaires
            if not hasattr(target, 'temporary_effects'):
                target.temporary_effects = []
                if context.engine:
                    context.engine.log.append(f"[DEBUG] Initialisation de temporary_effects pour {target.name}")
            
            # Appliquer l'effet temporaire
            success = self.apply_temporary_effect(target, "shield", 2, amount)
            
            if context.engine:
                if success:
                    context.engine.log.append(f"[BOUCLIER] {target.name} reçoit un bouclier de {amount} points")
                    # Afficher les effets temporaires actuels
                    shield_effects = [e for e in target.temporary_effects if e.effect_type == "shield"]
                    total_shield = sum(e.intensity for e in shield_effects)
                    context.engine.log.append(f"[DEBUG] {target.name} a maintenant {total_shield} points de bouclier au total")
                else:
                    context.engine.log.append(f"[ERREUR] Échec de l'application du bouclier sur {target.name}")
            
            return success
            
        except Exception as e:
            error_msg = f"[ERREUR] Erreur lors de l'application du bouclier: {e}"
            if context.engine:
                context.engine.log.append(error_msg)
            print(error_msg)
            import traceback
            traceback.print_exc()
            return False
    
    def _apply_dispel(self, target: Any, context: EffectContext) -> bool:
        """Supprime les effets négatifs"""
        try:
            if hasattr(target, 'temporary_effects'):
                negative_effects = [e for e in target.temporary_effects 
                                  if e.effect_type in ["poison", "burn", "wet", "freeze", "scald", 
                                                      "steam", "corruption", "overload", "fragile", 
                                                      "stunned", "aspiration"]]
                
                for effect in negative_effects:
                    target.temporary_effects.remove(effect)
                
                if context.engine and negative_effects:
                    context.engine.log.append(f"[DISPEL] {len(negative_effects)} effets négatifs supprimés sur {target.name}")
            
            return True
            
        except Exception as e:
            print(f"[ERREUR] Erreur lors de l'application du dispel: {e}")
            return False

# Instance globale du gestionnaire
card_mechanics_manager = CardMechanicsManager()