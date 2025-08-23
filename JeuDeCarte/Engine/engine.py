# engine.py – Moteur de jeu pour JeuDeCarte

import json
import sys
import os
import logging
from typing import List, Optional, Dict, Any
import random
import time

# Configuration du logging de debug
def setup_debug_logging():
    """Configure le système de logging de debug pour les effets"""
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Nom du fichier avec timestamp
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    debug_filename = f"logs/effects_debug_{timestamp}.log"
    
    # Configuration du logging de debug
    debug_logger = logging.getLogger('effects_debug')
    debug_logger.setLevel(logging.DEBUG)
    
    # Handler pour fichier
    file_handler = logging.FileHandler(debug_filename, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    
    # Format détaillé
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    
    debug_logger.addHandler(file_handler)
    
    return debug_logger

# Initialiser le logger de debug
debug_logger = setup_debug_logging()

# Import sécurisé des modèles
try:
    from .models import Card, Unit, Hero, Ability
except ImportError:
    # Fallback pour l'import direct
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from models import Card, Unit, Hero, Ability

# Import sécurisé du gestionnaire de mécaniques
try:
    from .card_mechanics_manager import card_mechanics_manager, EffectContext
except ImportError:
    # Fallback si le module n'est pas disponible
    try:
        from card_mechanics_manager import card_mechanics_manager, EffectContext
    except ImportError:
        print("[ERREUR] Impossible d'importer card_mechanics_manager")
        card_mechanics_manager = None
        EffectContext = None

# Import sécurisé du gestionnaire de decks
try:
    from .deck_manager import deck_manager
except ImportError:
    try:
        from deck_manager import deck_manager
    except ImportError:
        print("[ERREUR] Impossible d'importer deck_manager")
        deck_manager = None

# Import sécurisé du gestionnaire de personnalisation
try:
    from .hero_customization_manager import hero_customization_manager
except ImportError:
    try:
        from hero_customization_manager import hero_customization_manager
    except ImportError:
        print("[ERREUR] Impossible d'importer hero_customization_manager")
        hero_customization_manager = None

# Import sécurisé du gestionnaire de base de données d'effets
try:
    from .effects_database_manager import EffectsDatabaseManager
except ImportError:
    try:
        from effects_database_manager import EffectsDatabaseManager
    except ImportError:
        print("[ERREUR] Impossible d'importer effects_database_manager")
        EffectsDatabaseManager = None

# Import sécurisé du gestionnaire de cibles
try:
    from .target_manager import target_manager, TargetType, TargetPriority
except ImportError:
    try:
        from target_manager import target_manager, TargetType, TargetPriority
    except ImportError:
        print("[ERREUR] Impossible d'importer target_manager")
        target_manager = None
        TargetType = None
        TargetPriority = None

# Import sécurisé du système de graines
try:
    from .seed_system import seed_system
except ImportError:
    try:
        from seed_system import seed_system
    except ImportError:
        print("[ERREUR] Impossible d'importer seed_system")
        seed_system = None

# Import sécurisé du système de capacités avancées
try:
    from .advanced_abilities import advanced_abilities
except ImportError:
    try:
        from advanced_abilities import advanced_abilities
    except ImportError:
        print("[ERREUR] Impossible d'importer advanced_abilities")
        advanced_abilities = None

# Import sécurisé du système de pièges
try:
    from .trap_system import trap_system
except ImportError:
    try:
        from trap_system import trap_system
    except ImportError:
        print("[ERREUR] Impossible d'importer trap_system")
        trap_system = None

# Import sécurisé du système de passifs
try:
    from .passive_system import passive_system
except ImportError:
    try:
        from passive_system import passive_system
    except ImportError:
        print("[ERREUR] Impossible d'importer passive_system")
        passive_system = None

# Import sécurisé du système de capacités avancées
try:
    from .advanced_abilities import advanced_abilities
except ImportError:
    try:
        from advanced_abilities import advanced_abilities
    except ImportError:
        print("[ERREUR] Impossible d'importer advanced_abilities")
        advanced_abilities = None

class Player:
    def __init__(self, name: str, deck: List[Card], hero: Hero, units: List[Unit]):
        self.name = name
        self.deck = deck
        self.hand = []
        self.hero = hero
        self.units = units
        self.opponent: Optional['Player'] = None
        self.log: List[str] = []
        
        # Système de mana
        self.mana = 1
        self.max_mana = 1
        self.mana_crystals = 0
        
        # Système de mulligan
        self.mulligan_used = False
        self.mulligan_count = 0  # Nombre de mulligans utilisés
        self.max_mulligans = 1   # Par défaut 1, sera ajusté selon l'ordre de jeu

    def draw_card(self):
        """Pioche une carte du deck"""
        if self.deck and len(self.hand) < 9:  # Pioche conditionnelle : seulement si < 9 cartes
            card = self.deck.pop(0)
            self.hand.append(card)
            # Ne pas afficher les cartes piochées par l'IA
            if self.name != "IA":
                self.log.append(f"[PIOCHE] {card.name} piochée")
            return card
        elif self.deck:
            # Deck non vide mais main pleine
            self.log.append(f"[MAIN PLEINE] Impossible de piocher - main pleine ({len(self.hand)}/9 cartes)")
            return None
        else:
            # Fatigue - dégâts au héros selon la documentation (10% PV max)
            if hasattr(self.hero, 'base_stats'):
                old_hp = self.hero.hp
                max_hp = self.hero.max_hp  # Pour le calcul du pourcentage
                fatigue_damage = max(1, int(max_hp * 0.10))  # 10% PV max, minimum 1 dégât
                self.hero.current_stats['hp'] = max(0, old_hp - fatigue_damage)
                self.log.append(f"[FATIGUE] {self.name} subit {fatigue_damage} dégâts de fatigue (10% PV max) (HP: {old_hp} → {self.hero.hp})")
        return None

    def is_alive(self):
        """Vérifie si le joueur est encore en vie (héros vivant)"""
        return self.hero and self.hero.hp > 0

    def remove_dead_units(self):
        self.units = [u for u in self.units if u.stats.get("hp", 0) > 0]
    
    def get_engine(self):
        """Retourne le moteur de jeu associé à ce joueur"""
    
    def can_mulligan(self):
        """Vérifie si le joueur peut faire un mulligan"""
        return self.mulligan_count < self.max_mulligans
    
    def perform_mulligan(self, cards_to_mulligan):
        """
        Effectue un mulligan en remettant les cartes spécifiées en bas du deck
        et en piochant de nouvelles cartes
        
        Args:
            cards_to_mulligan: Liste des indices des cartes à mulligan
        """
        if not self.can_mulligan():
            self.log.append(f"[MULLIGAN] {self.name} ne peut plus faire de mulligan")
            return False
        
        if not cards_to_mulligan:
            self.log.append(f"[MULLIGAN] {self.name} n'a pas sélectionné de cartes à mulligan")
            return False
        
        # Remettre les cartes sélectionnées en bas du deck
        mulliganed_cards = []
        for index in sorted(cards_to_mulligan, reverse=True):  # Reverse pour éviter les problèmes d'index
            if 0 <= index < len(self.hand):
                card = self.hand.pop(index)
                self.deck.append(card)  # Ajouter en bas du deck
                mulliganed_cards.append(card.name)
        
        # Mélanger le deck après avoir remis les cartes
        import random
        random.shuffle(self.deck)
        
        # Piocher de nouvelles cartes
        new_cards = []
        for _ in range(len(mulliganed_cards)):
            if self.deck:
                card = self.deck.pop(0)
                self.hand.append(card)
                new_cards.append(card.name)
        
        # Incrémenter le compteur de mulligan
        self.mulligan_count += 1
        
        # Logs
        self.log.append(f"[MULLIGAN] {self.name} a mulligané {len(mulliganed_cards)} cartes: {', '.join(mulliganed_cards)}")
        self.log.append(f"[MULLIGAN] {self.name} a pioché {len(new_cards)} nouvelles cartes: {', '.join(new_cards)}")
        self.log.append(f"[MULLIGAN] {self.name} a utilisé {self.mulligan_count}/{self.max_mulligans} mulligans")
        
        return True
    
    def get_engine(self):
        """Retourne le moteur de jeu associé à ce joueur"""
        return getattr(self, 'engine', None)
    
    def play_card(self, card: Card, target=None):
        """Joue une carte de la main en utilisant le gestionnaire de mécaniques"""
        
        if card not in self.hand:
            return False
        
        # Vérifier le coût en mana
        card_cost = getattr(card, 'cost', 0)
        if self.mana < card_cost:
            return False
        
        # Retirer la carte de la main
        self.hand.remove(card)
        
        # Consommer le mana
        self.mana -= card_cost
        
        # Utiliser le gestionnaire de mécaniques
        if card_mechanics_manager is not None and EffectContext is not None:
            try:
                
                # Accès direct au moteur via la référence
                engine = self.get_engine()
                
                # Créer le contexte d'effet
                context = EffectContext(
                    source=card,
                    target=target,
                    caster=self,
                    engine=engine
                )
                
                # Préparer les données de la carte pour le gestionnaire
                card_data = self._prepare_card_data_for_mechanics(card)
                # Utiliser le gestionnaire de mécaniques
                
                try:
                    success = card_mechanics_manager.handle_card_play(card_data, context)
                except Exception as e:
                    self.log.append(f"[ERREUR] Exception lors de l'appel à handle_card_play: {e}")
                    import traceback
                    self.log.append(f"[ERREUR] Traceback: {traceback.format_exc()}")
                    success = False
                
                if success:
                    self.log.append(f"[CARTE] {card.name} jouée avec succès via le gestionnaire de mécaniques")
                    return True
                else:
                    self.log.append(f"[ERREUR] Échec de l'application de {card.name} via le gestionnaire")
                    # Remettre la carte dans la main et rembourser le mana en cas d'échec
                    self.hand.append(card)
                    self.mana += card_cost
                    return False
                    
            except Exception as e:
                self.log.append(f"[ERREUR] Erreur lors du jeu de {card.name}: {e}")
                # Remettre la carte dans la main et rembourser le mana en cas d'erreur
                self.hand.append(card)
                self.mana += card_cost
                return False
        else:
            self.log.append(f"[ERREUR] Gestionnaire de mécaniques non disponible pour {card.name}")
            # Remettre la carte dans la main et rembourser le mana
            self.hand.append(card)
            self.mana += card_cost
            return False
    
    def _prepare_card_data_for_mechanics(self, card: Card) -> dict:
        """Prépare les données de la carte pour le gestionnaire de mécaniques"""
        try:
            # Créer un dictionnaire sécurisé des attributs de la carte
            card_data = {}
            
            # Copier les attributs de base de manière sécurisée
            for attr in ['name', 'cost', 'card_type', 'element', 'description']:
                if hasattr(card, attr):
                    card_data[attr] = getattr(card, attr)
            
            # S'assurer que le type de carte est correct
            if 'card_type' not in card_data:
                card_data['card_type'] = 'CARDTYPE.SPELL'  # Par défaut
            
            if hasattr(card, 'effects') and card.effects:
                card_data['effects'] = card.effects
            else:
                # Créer des effets basés sur les attributs de la carte
                effects = []
                
                # Effet de dégâts
                if hasattr(card, 'damage') and getattr(card, 'damage', 0) > 0:
                    effects.append({
                        "type": "damage",
                        "amount": getattr(card, 'damage', 0),
                        "target": getattr(card, 'target_type', 'enemy')
                    })
                
                # Effet de soins
                if hasattr(card, 'heal') and getattr(card, 'heal', 0) > 0:
                    effects.append({
                        "type": "heal",
                        "amount": getattr(card, 'heal', 0),
                        "target": getattr(card, 'target_type', 'ally')
                    })
                
                # Effet de bouclier
                if hasattr(card, 'shield') and getattr(card, 'shield', 0) > 0:
                    effects.append({
                        "type": "shield",
                        "amount": getattr(card, 'shield', 0),
                        "target": getattr(card, 'target_type', 'ally')
                    })
                
                card_data['effects'] = effects
            
            return card_data
            
        except Exception as e:
            self.log.append(f"[ERREUR] Erreur lors de la préparation des données de carte: {e}")
            # Retourner un dictionnaire minimal en cas d'erreur
            return {
                'name': getattr(card, 'name', 'Carte inconnue'),
                'card_type': 'CARDTYPE.SPELL',
                'effects': []
            }

    def AI_play_turn(self, engine):
        """Logique IA pour jouer automatiquement le tour en utilisant le moteur"""
        self.log.append(f"[IA] {self.name} commence son tour (Mana: {self.mana}/{self.max_mana})")
        
        # Vérifier les ressources disponibles
        actions_performed = 0
        
        # Phase 0: Décider d'activer le héros
        hero_activated = self._AI_activate_hero(engine)
        if hero_activated:
            actions_performed += 1
        
        # Phase 1: Jouer les cartes prioritaires (sorts de dégâts directs)
        spells_played = self._AI_play_spells(engine)
        actions_performed += spells_played
        
        # Phase 2: Déployer des unités
        units_played = self._AI_play_units(engine)
        actions_performed += units_played
        
        # Phase 3: Activer les capacités des unités
        abilities_used = self._AI_use_abilities(engine)
        actions_performed += abilities_used
        
        # Log du résultat du tour
        if actions_performed == 0:
            self.log.append(f"[IA] {self.name} n'a rien à faire et passe son tour")
        else:
            self.log.append(f"[IA] {self.name} a effectué {actions_performed} action(s)")
        
        self.log.append(f"[IA] {self.name} termine son tour")
    
    def _AI_play_spells(self, engine):
        """IA joue les sorts de manière stratégique"""
        
        # Trier les sorts par priorité (dégâts élevés en premier)
        spells = [card for card in self.hand if hasattr(card, 'type') and card.type in ["spell", "CARDTYPE.SPELL"]]
        
        if not spells:
            return 0
        
        spells.sort(key=lambda x: getattr(x, 'damage', 0), reverse=True)
        
        spells_played = 0
        for spell in spells:
            spell_cost = getattr(spell, 'cost', 0)
            spell_damage = getattr(spell, 'damage', 0)
            
            if self.mana < spell_cost:
                continue
                
            # Choisir la meilleure cible
            target = self._AI_choose_spell_target(spell)
            if target:
                target_name = getattr(target, 'name', str(target))
                success = self.play_card(spell, target)
                if success:
                    self.log.append(f"[IA] {self.name} lance {spell.name} sur {target_name}")
                    spells_played += 1
                else:
                    self.log.append(f"[IA] {self.name} échoue à lancer {spell.name}")
            else:
                self.log.append(f"[IA] {self.name} ne trouve pas de cible pour {spell.name}")
        
        return spells_played
    
    def _AI_choose_spell_target(self, spell):
        """IA choisit la meilleure cible pour un sort"""
        damage = getattr(spell, 'damage', 5)
        
        # Vérifier que opponent.units est une liste valide
        if not hasattr(self.opponent, 'units') or not isinstance(self.opponent.units, list):
            return None
        
        # Priorité 1: Unités ennemies avec peu de HP
        enemy_units = [u for u in self.opponent.units if hasattr(u, 'stats') and u.stats.get('hp', 0) > 0]
        if enemy_units:
            # Cibler l'unité la plus faible
            target = min(enemy_units, key=lambda u: u.stats.get('hp', 0))
            if target.stats.get('hp', 0) <= damage:
                return target  # Peut tuer l'unité
        
        # Priorité 2: Héros ennemi si pas d'unités ou si le sort peut faire beaucoup de dégâts
        if damage >= 8 or not enemy_units:
            if hasattr(self.opponent, 'hero') and self.opponent.hero:
                return self.opponent.hero
        
        # Priorité 3: Unités ennemies avec le plus d'attaque
        if enemy_units:
            return max(enemy_units, key=lambda u: u.stats.get('attack', 0))
        
        return None
    
    def _AI_play_units(self, engine):
        """IA déploie des unités stratégiquement"""
        # Vérifier que self.hand est une liste valide
        if not hasattr(self, 'hand') or not isinstance(self.hand, list):
            return 0
        
        units = [card for card in self.hand if hasattr(card, 'type') and card.type in ["unit", "CARDTYPE.UNIT"]]
        
        # Trier par rapport coût/efficacité
        def unit_value(unit):
            if hasattr(unit, 'stats'):
                attack = unit.stats.get('attack', 0)
                hp = unit.stats.get('hp', 0)
            else:
                attack = hp = 0
            cost = getattr(unit, 'cost', 1)
            return (attack + hp) / max(cost, 1)
        
        units.sort(key=unit_value, reverse=True)
        
        units_played = 0
        for unit in units:
            if self.mana < getattr(unit, 'cost', 0) or len(self.units) >= 5:
                continue
            
            success = self.play_card(unit)
            if success:
                unit_name = getattr(unit, 'name', str(unit))
                self.log.append(f"[IA] {self.name} déploie {unit_name}")
                units_played += 1
        
        return units_played
    
    def _AI_use_abilities(self, engine):
        """IA utilise les capacités des unités"""
        
        # Vérifier que self.units est une liste valide
        if not hasattr(self, 'units') or not isinstance(self.units, list):
            return 0
        
        if not self.units:
            return 0
        
        abilities_used = 0
        for unit in self.units:
            if not unit:
                continue
                
            unit_name = getattr(unit, 'name', 'Unité inconnue')
            unit_hp = getattr(unit, 'stats', {}).get('hp', 0)
            
            if unit_hp <= 0:
                continue
            
            if not hasattr(unit, 'abilities') or not unit.abilities:
                continue
            
            # Utiliser la première capacité disponible
            for ability in unit.abilities:
                ability_name = getattr(ability, 'name', 'Capacité inconnue')
                
                # Vérifier le cooldown via le moteur
                cooldown = engine.get_ability_cooldown(unit, ability)
                
                if cooldown > 0:
                    continue
                
                # Choisir une cible pour la capacité
                target = self._AI_choose_ability_target(ability)
                if target:
                    target_name = getattr(target, 'name', str(target))
                    
                    # Utiliser la capacité via le moteur (avec gestion des cooldowns)
                    success = engine.use_ability(unit, ability, target)
                    if success:
                        self.log.append(f"[IA] {unit_name} utilise {ability_name} sur {target_name}")
                        abilities_used += 1
                        break  # Une seule capacité par unité par tour
                    else:
                        pass  # Échec de l'utilisation de la capacité
                else:
                    pass  # Pas de cible trouvée
            else:
                pass  # Pas de capacité disponible
        
        return abilities_used
    
    def _AI_activate_hero(self, engine):
        """IA décide quand activer son héros"""
        
        # Vérifier si le héros est déjà activé
        if hasattr(self, 'hero_activated') and self.hero_activated:
            return False
        
        # Vérifier si le héros existe
        if not self.hero:
            return False
        
        # Vérifier si le héros est vivant
        if not self.is_alive():
            return False
        
        # Récupérer le coût d'activation du héros
        activation_cost = self.hero.get_activation_cost()
        
        # Vérifier si l'IA a assez de mana
        if self.mana < activation_cost:
            return False
        
        # Stratégie d'activation du héros
        should_activate = self._AI_should_activate_hero()
        
        if should_activate:
            # Activer le héros
            self.hero_activated = True
            self.mana -= activation_cost
            self.log.append(f"[IA] {self.name} active son héros pour {activation_cost} mana")
            return True
        else:
            return False
    
    def _AI_should_activate_hero(self):
        """IA décide si elle doit activer son héros maintenant"""
        # Stratégie: activer le héros si les conditions sont critiques
        
        # Condition 1: Peu d'unités vivantes (moins de 2)
        alive_units = [u for u in self.units if u.stats.get('hp', 0) > 0]
        if len(alive_units) < 2:
            return True
        
        # Condition 2: Unités en danger (HP faible)
        weak_units = [u for u in alive_units if u.stats.get('hp', 0) <= 3]
        if len(weak_units) >= 2:
            return True
        
        # Condition 3: Mana suffisant et tour avancé (tour 3+)
        if self.mana >= 2 and hasattr(self, 'engine') and self.engine.turn_count >= 3:
            return True
        
        # Condition 4: Adversaire a beaucoup d'unités (pression)
        if hasattr(self.opponent, 'units'):
            enemy_units = [u for u in self.opponent.units if u.stats.get('hp', 0) > 0]
            if len(enemy_units) >= 4:
                return True
        
        return False
    
    def _AI_choose_ability_target(self, ability):
        """IA choisit la meilleure cible pour une capacité"""
        # Vérifier que opponent.units est une liste valide
        if not hasattr(self.opponent, 'units') or not isinstance(self.opponent.units, list):
            return None
        
        # Logique simple: cibler l'ennemi le plus faible
        enemy_units = [u for u in self.opponent.units if hasattr(u, 'stats') and u.stats.get('hp', 0) > 0]
        if enemy_units:
            return min(enemy_units, key=lambda u: u.stats.get('hp', 0))
        
        # Vérifier que opponent.hero est un objet valide
        if hasattr(self.opponent, 'hero') and self.opponent.hero:
            return self.opponent.hero
        
        return None

class CombatEngine:
    def __init__(self, player1: Player, player2: Player):
        self.players = [player1, player2]
        self.current_player_index = 0  # Commence par le joueur 1
        self.log = []
        self.unit_cooldowns = {}  # {unit_id: [cooldown1, cooldown2, ...]}
        
        # Initialiser les attributs manquants
        self.global_passives = []  # Passifs globaux
        self.triggers = []  # Triggers/événements
        
        # Configuration des joueurs
        player1.opponent = player2
        player2.opponent = player1
        player1.engine = self
        player2.engine = self
        
        # Initialisation du tour
        self.turn_count = 1  # Unifié : utilisation de turn_count partout
        self.log.append(f"[INIT] Combat initialisé - Tour {self.turn_count}")
        
        # Initialiser le gestionnaire de base de données d'effets
        if EffectsDatabaseManager:
            self.effects_manager = EffectsDatabaseManager()
            self.log.append("[INIT] Gestionnaire d'effets initialisé")
        else:
            self.effects_manager = None
            self.log.append("[ERREUR] Gestionnaire d'effets non disponible")

        # Réinitialiser tous les cooldowns au début du combat
        self.reset_all_cooldowns()

    def reset_all_cooldowns(self):
        """Réinitialise tous les cooldowns des unités et héros au début du combat"""
        self.unit_cooldowns.clear()  # Vider le dictionnaire des cooldowns
        
        # Réinitialiser les cooldowns de toutes les unités
        for player in self.players:
            for unit in player.units:
                if hasattr(unit, 'abilities') and unit.abilities:
                    entity_id = id(unit)
                    cooldowns = []
                    for ab in unit.abilities:
                        cooldowns.append(0)  # Toutes les capacités sont prêtes
                        if hasattr(ab, 'current_cooldown'):
                            ab.current_cooldown = 0
                    self.unit_cooldowns[entity_id] = cooldowns
                    self.log.append(f"[COOLDOWN] Réinitialisation des cooldowns pour {unit.name}")
            
            # Réinitialiser le cooldown du héros
            if player.hero and hasattr(player.hero, 'ability') and player.hero.ability:
                if hasattr(player.hero.ability, 'current_cooldown'):
                    player.hero.ability.current_cooldown = 0
                self.log.append(f"[COOLDOWN] Réinitialisation du cooldown du héros {player.hero.name}")
        
        self.log.append("[COOLDOWN] Tous les cooldowns ont été réinitialisés")

    def process_triggers(self, event: str, context: dict):
        """Déclenche tous les triggers correspondant à l'événement donné."""
        for trig in self.triggers:
            if trig.event == event and trig.should_trigger(context):
                # Appliquer l'effet du trigger
                self.apply_effect(context.get('target'), trig.effect, context.get('source'))
                self.log.append(f"[TRIGGER] {trig.event} déclenché sur {getattr(context.get('target'), 'name', 'Cible')}")
        # TODO: Ajouter des triggers par unité/héros si besoin

    def get_elemental_multiplier(self, attacker_element: str, defender_element: str) -> float:
        # Table d'interactions élémentaires complète selon la documentation
        advantage = {
            "Feu": "Terre",
            "Terre": "Air",
            "Air": "Eau", 
            "Eau": "Feu",
            "Foudre": "Eau",
            "Glace": "Air",
            "Lumière": "Ténèbres",
            "Ténèbres": "Lumière",
            "Lumière": "Néant",
            "Arcanique": "Poison"
        }
        
        multiplier = 1.0
        
        # Gestion des éléments spéciaux
        if attacker_element == "Poison":
            if defender_element == "Arcanique":
                multiplier = 0.85  # Poison contre Arcanique : malus de 15%
            else:
                multiplier = 1.15  # Poison contre tous les autres : +15%
        elif attacker_element == "Néant":
            if defender_element == "Lumière":
                multiplier = 0.70  # Néant contre Lumière : malus de 30%
            else:
                multiplier = 1.10  # Néant contre tous les autres : +10%
        else:
            # Gestion des désavantages (malus de 5% selon la doc)
            disadvantage = {v: k for k, v in advantage.items()}
            
            if attacker_element == defender_element:
                multiplier = 1.0
            elif advantage.get(attacker_element) == defender_element:
                multiplier = 1.2  # +20% selon la documentation
            elif disadvantage.get(attacker_element) == defender_element:
                multiplier = 0.95  # -5% selon la documentation
        
        debug_logger.debug(f"[ÉLÉMENTAIRE] Calcul multiplicateur élémentaire")
        debug_logger.debug(f"[ÉLÉMENTAIRE] Attaquant: {attacker_element}")
        debug_logger.debug(f"[ÉLÉMENTAIRE] Défenseur: {defender_element}")
        debug_logger.debug(f"[ÉLÉMENTAIRE] Multiplicateur: {multiplier}")
        
        return multiplier

    def appliquer_effet_carte(self, card, lanceur, cible):
        """Point d'entrée unique pour appliquer l'effet d'une carte, extensible pour de nouveaux types"""
        ctype = getattr(card, 'type', getattr(card, 'card_type', None))
        if ctype is None:
            print(f"Type de carte inconnu pour {card.name}")
            return
        # Exemples de gestion par type (à étendre)
        if ctype == "CARDTYPE.SPELL":
            self.appliquer_effet_spell(card, lanceur, cible)
        elif ctype == "CARDTYPE.EQUIPMENT":
            self.appliquer_effet_equipement(card, lanceur, cible)
        else:
            print(f"Type de carte non géré : {ctype}")
    def appliquer_effet_spell(self, card, lanceur, cible):
        # Logique d'application d'un sort (existant)
        # ...
        pass
    def appliquer_effet_equipement(self, card, lanceur, cible):
        # Logique d'application d'un équipement (à implémenter)
        pass

    def apply_effect(self, target: Any, effect: dict, source: object = None):
        """
        Applique un effet à la cible, y compris les effets conditionnels et combos avancés.
        """
        if not target or not effect:
            debug_logger.debug(f"[EFFET] Tentative d'application d'effet invalide - target: {target}, effect: {effect}")
            return
        
        effect_type = effect.get("effect_type", "unknown")
        value = effect.get("value", 0)
        duration = effect.get("duration", 1)
        element = effect.get("element", "NEUTRE")
        
        debug_logger.debug(f"[EFFET] === DÉBUT APPLICATION EFFET ===")
        debug_logger.debug(f"[EFFET] Type: {effect_type}")
        debug_logger.debug(f"[EFFET] Valeur: {value}")
        debug_logger.debug(f"[EFFET] Durée: {duration}")
        debug_logger.debug(f"[EFFET] Élément: {element}")
        debug_logger.debug(f"[EFFET] Source: {getattr(source, 'name', 'None') if source else 'None'}")
        debug_logger.debug(f"[EFFET] Cible: {getattr(target, 'name', 'Cible')}")
        
        # Application des passifs globaux avant l'effet
        for passive in self.global_passives:
            passive.apply({'target': target, 'effect': effect, 'source': source, 'engine': self})
        
        # Appel de la gestion avancée AVANT l'effet principal
        self.handle_advanced_interactions(target, effect, source)
        
        # Effets principaux (existant)
        if effect_type == "damage":
            if hasattr(target, 'stats'):
                old_hp = target.stats.get('hp', 0)
                target.stats['hp'] = max(0, old_hp - value)
                
                debug_logger.debug(f"[DÉGÂTS] Application des dégâts")
                debug_logger.debug(f"[DÉGÂTS] HP avant: {old_hp}")
                debug_logger.debug(f"[DÉGÂTS] Dégâts infligés: {value}")
                debug_logger.debug(f"[DÉGÂTS] HP après: {target.stats['hp']}")
                
                self.log.append(f"[DÉGÂTS] {getattr(target, 'name', 'Cible')} subit {value} dégâts (HP: {old_hp} → {target.stats['hp']})")
                
                # Nettoyer immédiatement si l'unité meurt
                if target.stats['hp'] <= 0 and hasattr(target, 'name'):
                    debug_logger.debug(f"[MORT] {target.name} est morte")
                    self.log.append(f"[MORT] {target.name} est morte")
                    
                    # Déclencher le passif Ombre Dévorante pour tous les alliés
                    if hasattr(self, 'current_player') and self.current_player:
                        for unit in self.get_allies(target):
                            if hasattr(unit, 'passive_ids') and "1335" in unit.passive_ids:
                                self.apply_ombre_devorante(unit, target)
                    
                    self.cleanup_dead_units()
        elif effect_type in ("burn", "brûlure"):
            if hasattr(target, 'active_effects'):
                target.active_effects.append({"type": "brûlure", "value": value, "duration": duration})
                
                debug_logger.debug(f"[BRÛLURE] Application de l'effet brûlure")
                debug_logger.debug(f"[BRÛLURE] Valeur: {value}")
                debug_logger.debug(f"[BRÛLURE] Durée: {duration}")
                debug_logger.debug(f"[BRÛLURE] Effets actifs après ajout: {len(target.active_effects)}")
                
                self.log.append(f"[BRÛLURE] {getattr(target, 'name', 'Cible')} subit Brûlure {value} ({duration} t)")
        elif effect_type == "poison":
            if hasattr(target, 'active_effects'):
                target.active_effects.append({"type": "poison", "value": value, "duration": duration})
                
                debug_logger.debug(f"[POISON] Application de l'effet poison")
                debug_logger.debug(f"[POISON] Valeur: {value}")
                debug_logger.debug(f"[POISON] Durée: {duration}")
                debug_logger.debug(f"[POISON] Effets actifs après ajout: {len(target.active_effects)}")
                
                self.log.append(f"[POISON] {getattr(target, 'name', 'Cible')} subit Poison {value} ({duration} t)")
        elif effect_type == "shield":
            if hasattr(target, 'stats'):
                old_shield = target.stats.get('shield', 0)
                target.stats['shield'] = old_shield + value
                
                debug_logger.debug(f"[BOUCLIER] Application de l'effet bouclier")
                debug_logger.debug(f"[BOUCLIER] Bouclier avant: {old_shield}")
                debug_logger.debug(f"[BOUCLIER] Bouclier ajouté: {value}")
                debug_logger.debug(f"[BOUCLIER] Bouclier après: {target.stats['shield']}")
                
                self.log.append(f"[BOUCLIER] {getattr(target, 'name', 'Cible')} gagne un bouclier de {value} PV ({duration} t)")
        elif effect_type == "heal":
            if hasattr(target, 'stats'):
                old_hp = target.stats.get('hp', 0)
                target.stats['hp'] = old_hp + value
                
                debug_logger.debug(f"[SOINS] Application de l'effet soin")
                debug_logger.debug(f"[SOINS] HP avant: {old_hp}")
                debug_logger.debug(f"[SOINS] Soins appliqués: {value}")
                debug_logger.debug(f"[SOINS] HP après: {target.stats['hp']}")
                
                self.log.append(f"[SOINS] {getattr(target, 'name', 'Cible')} récupère {value} PV (HP: {old_hp} → {target.stats['hp']})")
        elif effect.get("effect_type") == "buff":
            stat = effect.get("stat", "atk")
            value = effect.get("value", 0)
            duration = effect.get("duration", 1)
            if hasattr(target, 'active_effects'):
                target.active_effects.append({"type": "buff", "stat": stat, "value": value, "duration": duration})
                self.log.append(f"[BUFF] {getattr(target, 'name', 'Cible')} gagne +{value} % {stat.upper()} pour {duration} tours.")
        elif effect.get("effect_type") == "debuff":
            stat = effect.get("stat", "atk")
            value = effect.get("value", 0)
            duration = effect.get("duration", 1)
            if hasattr(target, 'active_effects'):
                target.active_effects.append({"type": "debuff", "stat": stat, "value": value, "duration": duration})
                self.log.append(f"[DEBUFF] {getattr(target, 'name', 'Cible')} subit -{value} % {stat.upper()} pour {duration} tours.")
        elif effect.get("effect_type") == "provoke":
            duration = effect.get("duration", 1)
            if hasattr(target, 'active_effects'):
                target.active_effects.append({"type": "provoke", "duration": duration})
                self.log.append(f"[PROVOCATION] {getattr(target, 'name', 'Cible')} est provoqué pour {duration} tour(s)")
        elif effect.get("effect_type") == "dispel":
            # Retire tous les malus (simplifié)
            if hasattr(target, 'active_effects'):
                before = len(target.active_effects)
                target.active_effects = [e for e in target.active_effects if e["type"] not in ("debuff", "brûlure", "burn", "poison", "freeze", "gelé", "immobilisation", "surcharge", "nihil")]
                after = len(target.active_effects)
                self.log.append(f"[DISPEL] {getattr(target, 'name', 'Cible')} perd {before-after} malus.")
        # NOUVEAUX EFFETS SELON LA DOCUMENTATION
        elif effect.get("effect_type") == "mouillé":
            duration = effect.get("duration", 2)  # 2-3 tours selon la doc
            if hasattr(target, 'active_effects'):
                target.active_effects.append({"type": "mouillé", "duration": duration})
                self.log.append(f"[MOUILLÉ] {getattr(target, 'name', 'Cible')} est mouillé (-20% dégâts) pour {duration} tours")
        elif effect.get("effect_type") == "gel":
            duration = effect.get("duration", 1)  # 1 tour selon la doc
            if hasattr(target, 'active_effects'):
                target.active_effects.append({"type": "gel", "duration": duration})
                self.log.append(f"[GEL] {getattr(target, 'name', 'Cible')} est gelé (ne peut pas agir) pour {duration} tour")
        elif effect.get("effect_type") == "échaudé":
            duration = effect.get("duration", 1)  # 1 tour selon la doc
            if hasattr(target, 'active_effects'):
                target.active_effects.append({"type": "échaudé", "duration": duration})
                self.log.append(f"[ÉCHAUDÉ] {getattr(target, 'name', 'Cible')} est échaudé (-50% soins reçus) pour {duration} tour")
        elif effect.get("effect_type") == "vapeur":
            duration = effect.get("duration", 1)  # 1 tour selon la doc
            if hasattr(target, 'active_effects'):
                target.active_effects.append({"type": "vapeur", "duration": duration})
                self.log.append(f"[VAPEUR] {getattr(target, 'name', 'Cible')} est sous vapeur (-20% précision) pour {duration} tour")
        elif effect.get("effect_type") == "corruption":
            duration = effect.get("duration", 3)  # 3 tours selon la doc
            if hasattr(target, 'active_effects'):
                target.active_effects.append({"type": "corruption", "duration": duration})
                self.log.append(f"[CORRUPTION] {getattr(target, 'name', 'Cible')} est corrompu (-10% toutes stats) pour {duration} tours")
        elif effect.get("effect_type") == "annihilation":
            duration = effect.get("duration", 1)  # 1 tour selon la doc
            if hasattr(target, 'active_effects'):
                target.active_effects.append({"type": "annihilation", "duration": duration})
                self.log.append(f"[ANNIHILATION] {getattr(target, 'name', 'Cible')} subit annihilation (10% PV max + supprime effets positifs)")
        elif effect.get("effect_type") == "surcharge":
            duration = effect.get("duration", 2)  # 2 tours selon la doc
            if hasattr(target, 'active_effects'):
                target.active_effects.append({"type": "surcharge", "duration": duration})
                self.log.append(f"[SURCHARGE] {getattr(target, 'name', 'Cible')} est surchargé (5% PV actuel/tour) pour {duration} tours")
        elif effect.get("effect_type") == "fragilisé":
            duration = effect.get("duration", 1)  # 1-2 tours selon la doc
            if hasattr(target, 'active_effects'):
                target.active_effects.append({"type": "fragilisé", "duration": duration})
                self.log.append(f"[FRAGILISÉ] {getattr(target, 'name', 'Cible')} est fragilisé (-20% défense) pour {duration} tour(s)")
        elif effect.get("effect_type") == "étourdissement":
            duration = effect.get("duration", 1)  # 1 tour selon la doc
            if hasattr(target, 'active_effects'):
                target.active_effects.append({"type": "étourdissement", "duration": duration})
                self.log.append(f"[ÉTOURDISSEMENT] {getattr(target, 'name', 'Cible')} est étourdi (ne peut pas agir + cooldowns non réduits) pour {duration} tour")
        elif effect.get("effect_type") == "aspiration":
            duration = effect.get("duration", 1)  # 1 tour selon la doc
            if hasattr(target, 'active_effects'):
                target.active_effects.append({"type": "aspiration", "duration": duration})
                self.log.append(f"[ASPIRATION] {getattr(target, 'name', 'Cible')} subit aspiration (-1 mana prochain tour) pour {duration} tour")
        # Les effets 'condition' et 'autre' sont logués dans handle_advanced_interactions
        # Ajoutez ici d'autres effets selon les besoins du jeu

    def handle_advanced_interactions(self, target, effect, source):
        """
        Gère les interactions avancées entre statuts et éléments (Mouillé, Échaudé, Gelé, Vapeur, combos, conditions, etc.).
        Cette fonction est appelée à chaque application d'effet et peut être étendue facilement.
        """
        debug_logger.debug(f"[INTERACTION] === DÉBUT INTERACTIONS AVANCÉES ===")
        debug_logger.debug(f"[INTERACTION] Type d'effet: {effect.get('effect_type')}")
        debug_logger.debug(f"[INTERACTION] Élément source: {getattr(source, 'element', 'None') if source else 'None'}")
        debug_logger.debug(f"[INTERACTION] Cible: {getattr(target, 'name', 'Cible')}")
        
        # Exemples d'interactions (à compléter selon les besoins du jeu)
        # 1. Feu sur Mouillé => retire Mouillé, applique Échaudé
        if effect.get("effect_type") in ("damage", "burn", "brûlure") and getattr(source, 'element', None) == "Feu":
            if hasattr(target, 'active_effects') and any(e["type"] == "wet" or e["type"] == "mouillé" for e in target.active_effects):
                debug_logger.debug(f"[INTERACTION] Feu sur Mouillé détecté")
                debug_logger.debug(f"[INTERACTION] Effets avant: {[e['type'] for e in target.active_effects]}")
                
                target.active_effects = [e for e in target.active_effects if e["type"] not in ("wet", "mouillé")]
                target.active_effects.append({"type": "échaudé", "value": 0, "duration": 1})
                
                debug_logger.debug(f"[INTERACTION] Mouillé retiré, Échaudé appliqué")
                debug_logger.debug(f"[INTERACTION] Effets après: {[e['type'] for e in target.active_effects]}")
                
                self.log.append(f"[INTÉRACTION] {getattr(target, 'name', 'Cible')} était Mouillé : Mouillé retiré, Échaudé appliqué (soins -30%, 1 tour)")
        # 2. Feu sur Gelé => retire Gelé, applique Échaudé
        if effect.get("effect_type") in ("damage", "burn", "brûlure") and getattr(source, 'element', None) == "Feu":
            if hasattr(target, 'active_effects') and any(e["type"] == "freeze" or e["type"] == "gelé" for e in target.active_effects):
                target.active_effects = [e for e in target.active_effects if e["type"] not in ("freeze", "gelé")]
                target.active_effects.append({"type": "échaudé", "value": 0, "duration": 1})
                self.log.append(f"[INTÉRACTION] {getattr(target, 'name', 'Cible')} était Gelé : Gelé retiré, Échaudé appliqué (soins -30%, 1 tour)")
        # 3. Eau sur Brûlé => retire Brûlure, soigne 15 PV
        if effect.get("effect_type") in ("heal", "soin") and getattr(source, 'element', None) == "Eau":
            if hasattr(target, 'active_effects') and any(e["type"] == "burn" or e["type"] == "brûlure" for e in target.active_effects):
                target.active_effects = [e for e in target.active_effects if e["type"] not in ("burn", "brûlure")]
                if hasattr(target, 'stats'):
                    old_hp = target.stats.get('hp', 0)
                    target.stats['hp'] = old_hp + 15
                    self.log.append(f"[INTÉRACTION] {getattr(target, 'name', 'Cible')} était Brûlé : Brûlure retirée, +15 PV")
        # 4. Glace sur Mouillé => applique Gelé (ou double Gel)
        if effect.get("effect_type") in ("damage", "freeze", "gel") and getattr(source, 'element', None) == "Glace":
            if hasattr(target, 'active_effects') and any(e["type"] == "wet" or e["type"] == "mouillé" for e in target.active_effects):
                target.active_effects.append({"type": "freeze", "value": 0, "duration": 2})
                self.log.append(f"[INTÉRACTION] {getattr(target, 'name', 'Cible')} était Mouillé : Gelé appliqué (2 tours)")
        # 5. Gestion avancée des effets conditionnels
        if effect.get("effect_type") == "condition":
            desc = effect.get('description', '').lower()
            # si déjà brûlé, +X dégâts
            if "déjà brûl" in desc and "+" in desc and "dégât" in desc:
                import re
                m = re.search(r'\+([0-9]+) dég', desc)
                if m and hasattr(target, 'active_effects') and any(e["type"] in ("brûlure", "burn") for e in target.active_effects):
                    bonus = int(m.group(1))
                    if hasattr(target, 'stats'):
                        old_hp = target.stats.get('hp', 0)
                        target.stats['hp'] = max(0, old_hp - bonus)
                        self.log.append(f"[CONDITION] {getattr(target, 'name', 'Cible')} était déjà Brûlé : +{bonus} dégâts appliqués (HP: {old_hp} → {target.stats['hp']})")
            # si mouillé, soigne X PV et retire mouillé
            elif "si mouill" in desc and "soigne" in desc:
                import re
                m = re.search(r'soigne ([0-9]+) pv', desc)
                if m and hasattr(target, 'active_effects') and any(e["type"] in ("wet", "mouillé") for e in target.active_effects):
                    heal = int(m.group(1))
                    if hasattr(target, 'stats'):
                        old_hp = target.stats.get('hp', 0)
                        target.stats['hp'] = old_hp + heal
                        self.log.append(f"[CONDITION] {getattr(target, 'name', 'Cible')} était Mouillé : +{heal} PV (HP: {old_hp} → {target.stats['hp']})")
                    target.active_effects = [e for e in target.active_effects if e["type"] not in ("wet", "mouillé")]
            # si gelée, retire gel, +X dégâts et -Y% DEF (1 t)
            elif "si gel" in desc and "+" in desc and "dégât" in desc:
                import re
                m = re.search(r'\+([0-9]+) dég', desc)
                if m and hasattr(target, 'active_effects') and any(e["type"] in ("freeze", "gelé") for e in target.active_effects):
                    bonus = int(m.group(1))
                    if hasattr(target, 'stats'):
                        old_hp = target.stats.get('hp', 0)
                        target.stats['hp'] = max(0, old_hp - bonus)
                        self.log.append(f"[CONDITION] {getattr(target, 'name', 'Cible')} était Gelé : +{bonus} dégâts appliqués (HP: {old_hp} → {target.stats['hp']})")
                    target.active_effects = [e for e in target.active_effects if e["type"] not in ("freeze", "gelé")]
            # si la cible meurt, dégâts de zone aux autres ennemis (à simuler dans le moteur de combat complet)
            elif "si la cible meurt" in desc and "dégâts de zone" in desc:
                self.log.append(f"[CONDITION] {getattr(target, 'name', 'Cible')} : effet de zone à appliquer si la cible meurt (à gérer dans le moteur de combat)")
            # si ≥ N cibles sous statut, appliquer un buff (à simuler dans le moteur de combat complet)
            elif "si ≥" in desc or "si >=" in desc:
                self.log.append(f"[CONDITION] {getattr(target, 'name', 'Cible')} : effet de groupe à appliquer (à gérer dans le moteur de combat)")
            else:
                self.log.append(f"[CONDITION] {getattr(target, 'name', 'Cible')} : {effect.get('description')}")
        # 6. Gestion générique des effets 'autre'
        if effect.get("effect_type") == "autre":
            self.log.append(f"[EFFET SPÉCIAL] {getattr(target, 'name', 'Cible')} : {effect.get('description')}")
        # 7. Ajoutez ici d'autres interactions particulières selon les besoins du jeu

    def apply_damage_with_shield(self, target, damage_amount, source_name="Attaque"):
        """Applique des dégâts en tenant compte des boucliers"""
        # Vérifier et utiliser les boucliers
        shield_absorbed = 0
        # 1) Bouclier numérique dans les stats
        try:
            if hasattr(target, 'stats') and isinstance(target.stats, dict):
                stat_shield = target.stats.get('shield', 0)
                if stat_shield and stat_shield > 0:
                    absorbed = min(stat_shield, damage_amount)
                    target.stats['shield'] = max(0, stat_shield - absorbed)
                    damage_amount -= absorbed
                    shield_absorbed += absorbed
                    self.log.append(f"[BOUCLIER] {getattr(target, 'name', 'Cible')} absorbe {absorbed} dégâts (bouclier stats)")
        except Exception:
            pass
        # 2) Effets temporaires de type bouclier (dicts ou objets)
        try:
            if hasattr(target, 'temporary_effects') and target.temporary_effects:
                # Construire une vue uniforme {amount, ref}
                normalized = []
                for eff in list(target.temporary_effects):
                    if isinstance(eff, dict) and eff.get('type') == 'shield':
                        amt = eff.get('amount') or eff.get('value') or 0
                        if amt > 0:
                            normalized.append({'amount': amt, 'ref': eff, 'is_dict': True})
                    else:
                        e_type = getattr(eff, 'effect_type', None)
                        if e_type == 'shield':
                            amt = getattr(eff, 'intensity', 0)
                            if amt > 0:
                                normalized.append({'amount': amt, 'ref': eff, 'is_dict': False})
                for item in normalized:
                    if damage_amount <= 0:
                        break
                    amt = item['amount']
                    absorbed = min(amt, damage_amount)
                    damage_amount -= absorbed
                    shield_absorbed += absorbed
                    # Décrémenter la source
                    if item['is_dict']:
                        item['ref']['amount'] = max(0, amt - absorbed)
                        if item['ref']['amount'] <= 0:
                            try:
                                target.temporary_effects.remove(item['ref'])
                            except Exception:
                                pass
                    else:
                        try:
                            item['ref'].intensity = max(0, amt - absorbed)
                            if item['ref'].intensity <= 0:
                                target.temporary_effects.remove(item['ref'])
                        except Exception:
                            pass
                    self.log.append(f"[BOUCLIER] {getattr(target, 'name', 'Cible')} absorbe {absorbed} dégâts (bouclier effet)")
        except Exception:
            pass
        
        # Appliquer les dégâts restants
        if damage_amount > 0:
            if hasattr(target, 'stats'):
                # Unités
                old_hp = target.stats.get("hp", 0)
                target.stats["hp"] = max(0, old_hp - damage_amount)
                return old_hp, target.stats["hp"], damage_amount
            elif hasattr(target, 'base_stats'):
                # Héros
                old_hp = target.base_stats.get("hp", 0)
                target.base_stats["hp"] = max(0, old_hp - damage_amount)
                return old_hp, target.base_stats["hp"], damage_amount
            elif hasattr(target, 'hp'):
                # Entité avec attribut hp direct
                old_hp = target.hp
                target.hp = max(0, target.hp - damage_amount)
                return old_hp, target.hp, damage_amount
        else:
            # Tous les dégâts absorbés par le bouclier
            self.log.append(f"[BOUCLIER] {target.name} absorbe tous les dégâts avec son bouclier")
            return None, None, 0
        
        return None, None, damage_amount

    def apply_lightning_mark(self, attacker, target):
        """Applique une marque de foudre à la cible (Passif d'Alice - Marque de l'Éclair)"""
        if hasattr(attacker, 'passive_ids') and "1337" in attacker.passive_ids:
            # Initialiser les marques si nécessaire
            if not hasattr(target, 'lightning_marks'):
                target.lightning_marks = 0
            
            # Ajouter une marque
            target.lightning_marks += 1
            self.log.append(f"[MARQUE DE L'ÉCLAIR] {target.name} reçoit une marque de foudre ({target.lightning_marks}/5)")
            
            # Vérifier si l'explosion doit se déclencher
            if target.lightning_marks >= 5:
                # Explosion !
                explosion_damage = 100  # Dégâts fixes de l'explosion
                old_hp = target.hp if hasattr(target, 'hp') else target.stats.get("hp", 0)
                
                # Appliquer les dégâts d'explosion
                if hasattr(target, 'hp'):
                    target.hp = max(0, target.hp - explosion_damage)
                elif hasattr(target, 'stats'):
                    target.stats["hp"] = max(0, target.stats["hp"] - explosion_damage)
                
                # Consommer les marques
                target.lightning_marks = 0
                
                self.log.append(f"[EXPLOSION ÉCLAIR] {target.name} explose ! {explosion_damage} dégâts (HP: {old_hp} → {target.hp if hasattr(target, 'hp') else target.stats.get('hp', 0)})")

    def process_temporary_effects(self, unit: Unit):
        """Traite les effets temporaires d'une unité"""
        # Traiter les effets dans active_effects (format dictionnaire)
        if hasattr(unit, 'active_effects') and unit.active_effects:
            effects_to_remove = []
            
            for effect in unit.active_effects:
                if not isinstance(effect, dict):
                    continue
                    
                old_duration = effect.get("duration", 0)
                effect["duration"] = max(0, old_duration - 1)
                
                # Appliquer l'effet selon son type
                effect_type = effect.get("type", "")
                value = effect.get("value", 0)
                
                if effect_type == "poison":
                    # Dégâts basés sur les PV max (3% * valeur)
                    max_hp = unit.stats.get("max_hp", 100)
                    damage = int(max_hp * 0.03 * value)
                    old_hp = unit.stats["hp"]
                    unit.stats["hp"] = max(0, unit.stats["hp"] - damage)
                    
                    self.log.append(f"[POISON] {unit.name} subit {damage} dégâts de poison (HP: {old_hp} → {unit.stats['hp']})")
                
                elif effect_type == "burn":
                    # Dégâts basés sur les PV actuels (3% * valeur)
                    current_hp = unit.stats.get("hp", 0)
                    damage = int(current_hp * 0.03 * value)
                    old_hp = unit.stats["hp"]
                    unit.stats["hp"] = max(0, unit.stats["hp"] - damage)
                    
                    self.log.append(f"[BRÛLURE] {unit.name} subit {damage} dégâts de brûlure (HP: {old_hp} → {unit.stats['hp']})")
                
                elif effect_type == "freeze":
                    # Effet de gel (stun) - pas de dégâts, juste empêcher l'action
                    self.log.append(f"[GEL] {unit.name} est gelé et ne peut pas agir")
                
                # Marquer pour suppression si durée expirée
                if effect["duration"] <= 0:
                    effects_to_remove.append(effect)
                    self.log.append(f"[EFFET] {effect_type} expiré sur {unit.name}")
            
            # Supprimer les effets expirés
            for effect in effects_to_remove:
                unit.active_effects.remove(effect)
        
        # Traiter les effets dans temporary_effects (format objet)
        if hasattr(unit, 'temporary_effects') and unit.temporary_effects:
            # Utiliser le gestionnaire de mécaniques pour traiter les effets
            if card_mechanics_manager:
                logs = card_mechanics_manager.process_temporary_effects(unit)
                for log in logs:
                    self.log.append(log)
            else:
                # Fallback si le gestionnaire n'est pas disponible
                effects_to_remove = []
                
                for effect in unit.temporary_effects:
                    if not hasattr(effect, 'duration'):
                        continue
                        
                    old_duration = effect.duration
                    effect.duration -= 1
                    
                    # Appliquer l'effet selon son type
                    if hasattr(effect, 'effect_type'):
                        if effect.effect_type == "poison":
                            damage = int(unit.stats.get("hp", 100) * 0.03 * getattr(effect, 'intensity', 1))
                            old_hp = unit.stats["hp"]
                            unit.stats["hp"] = max(0, unit.stats["hp"] - damage)
                            self.log.append(f"[POISON] {unit.name} subit {damage} dégâts de poison")
                        
                        elif effect.effect_type == "burn":
                            damage = int(unit.stats.get("hp", 100) * 0.03 * getattr(effect, 'intensity', 1))
                            old_hp = unit.stats["hp"]
                            unit.stats["hp"] = max(0, unit.stats["hp"] - damage)
                            self.log.append(f"[BRÛLURE] {unit.name} subit {damage} dégâts de brûlure")
                    
                    # Marquer pour suppression si durée expirée
                    if effect.duration <= 0:
                        effects_to_remove.append(effect)
                        self.log.append(f"[EFFET] {getattr(effect, 'effect_type', 'inconnu')} expiré sur {unit.name}")
                
                # Supprimer les effets expirés
                for effect in effects_to_remove:
                    unit.temporary_effects.remove(effect)

    def apply_ability(self, source, target, ability):
        """Applique une capacité d'unité sur une cible en utilisant le système avancé d'effets"""
        if not source or not target or not ability:
            return False
        
        # Vérifier que l'unité est vivante
        if hasattr(source, 'stats') and source.stats.get("hp", 0) <= 0:
            self.log.append(f"[ERREUR] {source.name} est morte et ne peut pas utiliser de capacité")
            return False
        
        # Récupérer les informations de la capacité
        ability_name = getattr(ability, 'name', 'Capacité inconnue')
        ability_description = getattr(ability, 'description', 'Aucune description')
        effect_type = getattr(ability, 'effect_type', 'damage')
        element = getattr(source, 'element', 'NEUTRE')
        
        
        # Créer un effet basé sur le type de capacité
        effect = self.create_effect_from_ability(ability, source, target)
        
        if effect:
            # Utiliser le système avancé d'effets
            success = self.apply_advanced_ability_effect(source, target, effect, ability)
            return success
        else:
            # Fallback vers l'ancien système si pas d'effet créé
            return self.apply_basic_ability(source, target, ability)
    
    def create_effect_from_ability(self, ability, source, target):
        """Crée un effet basé sur les informations de la capacité"""
        # Détecter automatiquement le type d'effet basé sur la description si effect_type n'est pas défini
        effect_type = getattr(ability, 'effect_type', None)
        if effect_type is None:
            # Détection automatique basée sur la description
            description = getattr(ability, 'description', '').lower()
            if any(word in description for word in ['soigne', 'soin', 'régénère', 'guérit', 'heal']):
                effect_type = 'heal'
            elif any(word in description for word in ['inflige', 'dégâts', 'damage', 'attaque']):
                effect_type = 'damage'
            elif any(word in description for word in ['empoisonne', 'poison', 'brûlure', 'gel']):
                effect_type = 'debuff'
            elif any(word in description for word in ['protège', 'bouclier', 'défense']):
                effect_type = 'defense'
            else:
                effect_type = 'damage'  # Par défaut
        
        element = getattr(source, 'element', 'NEUTRE')
        
        # Log pour debug
        self.log.append(f"[DEBUG] Capacité {ability.name}: effect_type détecté = {effect_type}")
        self.log.append(f"[DEBUG] Capacité {ability.name}: description = {getattr(ability, 'description', 'N/A')}")
        
        if effect_type == "damage":
            base_damage = getattr(ability, 'base_damage', 20)
            # Appliquer le multiplicateur élémentaire
            multiplier = self.get_elemental_multiplier(element, getattr(target, 'element', 'NEUTRE'))
            final_damage = int(base_damage * multiplier)
            
            # Détecter si la capacité affecte tous les ennemis
            description = getattr(ability, 'description', '').lower()
            affects_all_enemies = any(phrase in description for phrase in ['tous les ennemis', 'toutes les ennemis', 'all enemies', 'enemies', 'tous les adversaires', 'toutes les adversaires'])
            
            self.log.append(f"[DEBUG] Capacité {ability.name}: affects_all_enemies = {affects_all_enemies}")
            
            return {
                "effect_type": "damage",
                "value": final_damage,
                "element": element,
                "source": source,
                "description": f"{ability.name} inflige {final_damage} dégâts élément {element}",
                "secondary_effects": getattr(ability, 'secondary_effects', []),
                "affects_all_enemies": affects_all_enemies
            }
        
        elif effect_type == "heal":
            # Essayer d'extraire la valeur de soin depuis la description
            heal_amount = getattr(ability, 'heal_amount', None)
            if heal_amount is None:
                description = getattr(ability, 'description', '')
                import re
                # Chercher un nombre suivi de "PV" ou "HP"
                match = re.search(r'(\d+)\s*(?:PV|HP)', description)
                if match:
                    heal_amount = int(match.group(1))
                else:
                    heal_amount = 25  # Valeur par défaut
            
            return {
                "effect_type": "heal",
                "value": heal_amount,
                "element": element,
                "source": source,
                "description": f"{ability.name} soigne {heal_amount} PV",
                "secondary_effects": getattr(ability, 'secondary_effects', [])
            }
        
        elif effect_type == "debuff":
            status_effects = getattr(ability, 'status_effects', [])
            return {
                "effect_type": "debuff",
                "element": element,
                "source": source,
                "description": f"{ability.name} applique des effets de statut",
                "status_effects": status_effects
            }
        
        elif effect_type == "defense":
            defense_effects = getattr(ability, 'defense_effects', [])
            return {
                "effect_type": "defense",
                "element": element,
                "source": source,
                "description": f"{ability.name} applique des effets défensifs",
                "defense_effects": defense_effects
            }
        
        elif effect_type == "special":
            special_effects = getattr(ability, 'special_effects', [])
            return {
                "effect_type": "special",
                "element": element,
                "source": source,
                "description": f"{ability.name} applique des effets spéciaux",
                "special_effects": special_effects
            }
        
        return None
    
    def apply_advanced_ability_effect(self, source, target, effect, ability):
        """Applique un effet de capacité en utilisant le système avancé"""
        try:
            
            # Effet normal sur la cible
                self.apply_effect(target, effect, source)
            
            # Appliquer les effets secondaires
            secondary_effects = effect.get('secondary_effects', [])
            for sec_effect in secondary_effects:
                self.apply_secondary_effect(source, target, sec_effect, effect.get('element', 'NEUTRE'))
            
            # Appliquer les effets de statut si présents
            status_effects = effect.get('status_effects', [])
            for status in status_effects:
                self.apply_status_effect(target, status)
            
            # Appliquer les effets défensifs si présents
            defense_effects = effect.get('defense_effects', [])
            for defense in defense_effects:
                self.apply_defense_effect(target, defense)
            
            # Appliquer les effets spéciaux si présents
            special_effects = effect.get('special_effects', [])
            for special in special_effects:
                self.apply_special_effect(source, target, special)
            
            return True
            
        except Exception as e:
            self.log.append(f"[ERREUR] Erreur lors de l'application de {ability.name}: {e}")
            import traceback
            self.log.append(f"[ERREUR] Traceback: {traceback.format_exc()}")
            return False
    
    def apply_secondary_effect(self, source, target, effect_type, element):
        """Applique un effet secondaire basé sur le type et l'élément"""
        if not hasattr(target, 'active_effects'):
            target.active_effects = []
        
        # Effets basés sur l'élément
        if effect_type == "burn" and element == "Feu":
            # Chance de brûlure
            if random.randint(1, 100) <= 50:  # 50% de chance
                target.active_effects.append({
                    "type": "burn",
                    "value": 5,
                    "duration": 2,
                    "source": source
                })
                self.log.append(f"[EFFET] {target.name} subit Brûlure (2 tours)")
        
        elif effect_type == "freeze" and element == "Glace":
            # Chance de gel
            if random.randint(1, 100) <= 30:  # 30% de chance
                target.active_effects.append({
                    "type": "freeze",
                    "value": 0,
                    "duration": 1,
                    "source": source
                })
                self.log.append(f"[EFFET] {target.name} est Gelé (1 tour)")
        
        elif effect_type == "wet" and element == "Eau":
            # Appliquer mouillé
            target.active_effects.append({
                "type": "wet",
                "value": 0,
                "duration": 2,
                "source": source
            })
            self.log.append(f"[EFFET] {target.name} est Mouillé (2 tours)")
        
        elif effect_type == "poison" and element in ["Poison", "Ténèbres"]:
            # Appliquer poison
            target.active_effects.append({
                "type": "poison",
                "value": 3,
                "duration": 2,
                "source": source
            })
            self.log.append(f"[EFFET] {target.name} est Empoisonné (2 tours)")
        
        elif effect_type == "stun" and element == "Air":
            # Chance d'étourdissement
            if random.randint(1, 100) <= 25:  # 25% de chance
                target.active_effects.append({
                    "type": "stun",
                    "value": 0,
                    "duration": 1,
                    "source": source
                })
                self.log.append(f"[EFFET] {target.name} est Étourdi (1 tour)")
        
        elif effect_type == "overload" and element == "Foudre":
            # Chance de paralysie
            if random.randint(1, 100) <= 20:  # 20% de chance
                target.active_effects.append({
                    "type": "overload",
                    "value": 0,
                    "duration": 1,
                    "source": source
                })
                self.log.append(f"[EFFET] {target.name} est Paralysé (1 tour)")
    
    def apply_status_effect(self, target, status):
        """Applique un effet de statut"""
        if not hasattr(target, 'active_effects'):
            target.active_effects = []
        
        status_type = status.get('type', 'unknown')
        duration = status.get('duration', 1)
        intensity = status.get('intensity', 1)
        
        target.active_effects.append({
            "type": status_type,
            "value": 0,
            "duration": duration,
            "intensity": intensity
        })
        
        self.log.append(f"[STATUT] {target.name} subit {status_type} ({duration} tour(s))")
    
    def apply_defense_effect(self, target, defense):
        """Applique un effet défensif"""
        defense_type = defense.get('type', 'unknown')
        
        if defense_type == "shield":
            amount = defense.get('amount', 30)
            duration = defense.get('duration', 2)
            
            if not hasattr(target, 'active_effects'):
                target.active_effects = []
            
            target.active_effects.append({
                "type": "shield",
                "value": amount,
                "duration": duration
            })
            
            self.log.append(f"[BOUCLIER] {target.name} gagne un bouclier de {amount} PV ({duration} tours)")
        
        elif defense_type == "evasion":
            bonus = defense.get('bonus', 50)
            duration = defense.get('duration', 1)
            
            if not hasattr(target, 'active_effects'):
                target.active_effects = []
            
            target.active_effects.append({
                "type": "evasion_bonus",
                "value": bonus,
                "duration": duration
            })
            
            self.log.append(f"[ESQUIVE] {target.name} gagne +{bonus}% d'esquive ({duration} tour(s))")
    
    def apply_special_effect(self, source, target, special):
        """Applique un effet spécial"""
        special_type = special.get('type', 'unknown')
        
        if special_type == "rage":
            attack_bonus = special.get('attack_bonus', 7)
            max_bonus = special.get('max_bonus', 35)
            
            # Ajouter le bonus d'attaque
            if hasattr(source, 'stats'):
                current_bonus = source.stats.get('rage_bonus', 0)
                new_bonus = min(current_bonus + attack_bonus, max_bonus)
                source.stats['rage_bonus'] = new_bonus
                source.stats['attack'] = source.stats.get('attack', 0) + attack_bonus
                
                self.log.append(f"[RAGE] {source.name} gagne +{attack_bonus} ATK (Total: +{new_bonus})")
        
        elif special_type == "life_drain":
            percentage = special.get('percentage', 50)
            
            # Drain de vie
            if hasattr(target, 'stats'):
                damage = target.stats.get('hp', 0) * percentage // 100
                if hasattr(source, 'stats'):
                    source.stats['hp'] = min(source.stats.get('hp', 0) + damage, source.stats.get('max_hp', 1000))
                    
                    self.log.append(f"[DRAIN] {source.name} draine {damage} PV de {target.name}")
        
        elif special_type == "area_poison":
            duration = special.get('duration', 2)
            targets = special.get('targets', 'all_enemies')
            
            # Empoisonner tous les ennemis
            current_player = self.players[self.current_player_index]
            opponent = current_player.opponent
            
            if targets == "all_enemies":
                for enemy in opponent.units:
                    if enemy.stats.get('hp', 0) > 0:
                        if not hasattr(enemy, 'active_effects'):
                            enemy.active_effects = []
                        
                        enemy.active_effects.append({
                            "type": "poison",
                            "value": 5,
                            "duration": duration
                        })
                
                self.log.append(f"[ZONE] Tous les ennemis sont empoisonnés ({duration} tours)")
    
    def apply_basic_ability(self, source, target, ability):
        """Méthode de fallback pour les capacités basiques"""
        ability_name = getattr(ability, 'name', 'Capacité inconnue')
        ability_description = getattr(ability, 'description', 'Aucune description')
        
        # Appliquer l'effet basé sur la description de la capacité
        if "dégâts" in ability_description.lower() or "inflige" in ability_description.lower():
            # Capacité de dégâts
            if hasattr(target, 'stats'):
                old_hp = target.stats.get('hp', 0)
                damage = 15  # Valeur par défaut
                target.stats['hp'] = max(0, old_hp - damage)
                target_name = getattr(target, 'name', str(target))
                self.log.append(f"[CAPACITÉ] {ability_name} inflige {damage} dégâts à {target_name} (HP: {old_hp} → {target.stats['hp']})")
                
                # Nettoyer immédiatement si la cible meurt
                if target.stats['hp'] <= 0:
                    self.cleanup_dead_units()
                return True
        
        elif "soigne" in ability_description.lower() or "régénération" in ability_description.lower():
            # Capacité de soins
            if hasattr(target, 'stats'):
                old_hp = target.stats.get('hp', 0)
                heal = 20  # Valeur par défaut
                max_hp = target.stats.get('max_hp', old_hp + heal)
                target.stats['hp'] = min(max_hp, old_hp + heal)
                target_name = getattr(target, 'name', str(target))
                self.log.append(f"[CAPACITÉ] {ability_name} soigne {target_name} de {heal} PV (HP: {old_hp} → {target.stats['hp']})")
                return True
        
        return False
    
    def use_ability(self, entity, ability, target):
        """Utilise une capacité d'entité (unité ou héros) sur une cible"""
        if not self.can_use_ability(entity, ability):
            return False
        
        # Vérifier que l'entité appartient au joueur actuel
        current_player = self.players[self.current_player_index]
        if entity not in current_player.units and entity != current_player.hero:
            self.log.append(f"[ERREUR] {entity.name} n'appartient pas au joueur actuel")
            return False
        
        # Vérifier que la cible est valide
        if target is None:
            self.log.append(f"[ERREUR] Cible requise pour la capacité {getattr(ability, 'name', 'inconnue')}")
            return False
        
        # Si la capacité est liée à un ID d'effets, utiliser le système par ID
        if hasattr(ability, 'ability_id'):
            success, _msg = self.use_ability_by_id(entity, getattr(ability, 'ability_id'), target)
            # Le cooldown est déjà appliqué dans use_ability_by_id, pas besoin de le refaire ici
        else:
            # Appliquer la capacité via le système d'objets
            success = self.apply_ability(entity, target, ability)
            
            # Mettre à jour le cooldown seulement pour les capacités sans ID
            if success:
                entity_id = id(entity)
                
                # Pour les unités
                if entity in current_player.units:
                    if entity_id not in self.unit_cooldowns:
                        # Initialiser avec 0 pour les capacités prêtes à utiliser
                        cooldowns = []
                        for ability in entity.abilities:
                            cooldowns.append(0)
                            # Initialiser aussi le current_cooldown de la capacité
                            if hasattr(ability, 'current_cooldown'):
                                ability.current_cooldown = 0
                        self.unit_cooldowns[entity_id] = cooldowns
                    
                    # Trouver l'index de la capacité par nom (plus robuste)
                    try:
                        ability_name = getattr(ability, 'name', '')
                        ability_index = None
                        for i, unit_ability in enumerate(entity.abilities):
                            if getattr(unit_ability, 'name', '') == ability_name:
                                ability_index = i
                                break
                        
                        if ability_index is None:
                            self.log.append(f"[ERREUR] Capacité '{ability_name}' non trouvée dans la liste des capacités de {entity.name}")
                            self.log.append(f"[ERREUR] Capacités disponibles: {[getattr(a, 'name', 'N/A') for a in entity.abilities]}")
                            return False
                        
                        # Déterminer le cooldown à appliquer
                        cooldown = getattr(ability, 'cooldown', 1)
                        self.log.append(f"[COOLDOWN] use_ability - {entity.name} - {ability.name} - Index: {ability_index}, Cooldown de base: {cooldown}")
                        self.log.append(f"[COOLDOWN] use_ability - Cooldowns avant mise à jour: {self.unit_cooldowns[entity_id]}")
                        # CORRECTION : Définir le cooldown à la valeur de base (pas incrémenter)
                        self.unit_cooldowns[entity_id][ability_index] = cooldown
                        self.log.append(f"[COOLDOWN] use_ability - {entity.name} - {ability.name} : cooldown défini à {cooldown}")
                        self.log.append(f"[COOLDOWN] use_ability - Cooldowns après mise à jour: {self.unit_cooldowns[entity_id]}")
                    except Exception as e:
                        self.log.append(f"[ERREUR] Erreur lors de la mise à jour du cooldown pour {entity.name}: {e}")
                        return False
                
                # Pour les héros
                elif entity == current_player.hero:
                    if hasattr(ability, 'cooldown') and hasattr(ability, 'current_cooldown'):
                        # CORRECTION : Définir le cooldown à la valeur de base (pas incrémenter)
                        ability.current_cooldown = ability.cooldown
                        self.log.append(f"[COOLDOWN] use_ability - Héros {entity.name} - {ability.name} : cooldown défini à {ability.cooldown}")
        
        if success:
            ability_name = getattr(ability, 'name', 'Capacité inconnue')
            target_name = getattr(target, 'name', str(target))
            self.log.append(f"[CAPACITÉ] {entity.name} utilise {ability_name} sur {target_name}")
        
        return success
    
    def execute_advanced_ability(self, entity, ability_data, target):
        """
        Exécute une capacité avancée avec des mécaniques complexes
        
        Args:
            entity: L'entité qui utilise la capacité
            ability_data: Données de la capacité depuis effects_database.json
            target: La cible de la capacité
        """
        if not advanced_abilities:
            self.log.append("[ERREUR] Système de capacités avancées non disponible")
            return False
        
        ability_id = ability_data.get("id", "")
        damage_type = ability_data.get("damage_type", "fixed")
        target_type = ability_data.get("target_type", "single_enemy")
        
        # Gérer les différents types de dégâts
        if damage_type == "scaling_attack":
            # Scaling par utilisation
            base_damage = ability_data.get("damage", 1.0)
            scaling_factor = ability_data.get("scaling_per_use", 1.0)
            damage = advanced_abilities.get_scaling_damage(entity.id, ability_id, base_damage, scaling_factor)
            advanced_abilities.increment_ability_usage(entity.id, ability_id)
            
        elif damage_type == "scaling_heal":
            # Scaling de soins par utilisation
            base_heal = ability_data.get("damage", 40)
            scaling_factor = ability_data.get("scaling_per_use", 10)
            heal_amount = advanced_abilities.get_scaling_heal(entity.id, ability_id, base_heal, scaling_factor)
            advanced_abilities.increment_heal_usage(entity.id, ability_id)
            
            # Appliquer les soins
            if target and target.is_alive():
                target.heal(heal_amount)
                self.log.append(f"[SOIN] {entity.name} soigne {target.name} de {heal_amount} PV")
                
                # Appliquer le passif de bouclier de soin si l'entité l'a
                if hasattr(entity, 'passive_ids') and "1309" in entity.passive_ids:
                    shield_amount = int(heal_amount * 0.5)
                    # Ajouter un bouclier temporaire (à implémenter)
                    self.log.append(f"[BOUCLIER] {target.name} reçoit un bouclier de {shield_amount}")
            
            return True
            
        elif damage_type == "multi_attack":
            # Attaques multiples
            attack_count = ability_data.get("attack_count", 1)
            damage_per_attack = ability_data.get("damage", 1.0)
            damage = entity.stats.get("attack", 0) * damage_per_attack * attack_count
            
        elif damage_type == "seed_explosion":
            # Explosion de graines
            if not seed_system:
                self.log.append("[ERREUR] Système de graines non disponible")
                return False
            
            base_damage = ability_data.get("damage", 20)
            seed_count = seed_system.get_seed_count(target.id)
            damage = base_damage * (seed_count / 2)
            
        else:
            # Dégâts normaux
            damage = ability_data.get("damage", 0)
        
        # Gérer les différents types de cibles
        if target_type == "chain_random":
            # Chaîne aléatoire
            chain_chance = ability_data.get("chain_chance", 25)
            max_bounces = ability_data.get("max_bounces", 4)
            targets = advanced_abilities.chain_random_targets(entity, self, [target], chain_chance, max_bounces)
        elif target_type == "random_multiple":
            # Cibles multiples aléatoires
            target_count = ability_data.get("target_count", 2)
            same_target_allowed = ability_data.get("same_target_allowed", False)
            targets = self.get_random_multiple_targets(entity, target_count, same_target_allowed)
        elif target_type == "self_and_allies":
            # Cible soi + alliés
            targets = [entity] + [unit for unit in self.get_all_units() if unit.owner == entity.owner and unit != entity]
        elif target_type == "single_ally":
            # Cible alliée unique
            targets = [target] if target and target.owner == entity.owner else []
        else:
            targets = [target]
        
        # Appliquer les dégâts et effets
        for t in targets:
            if t and t.is_alive():
                # Appliquer les dégâts
                if damage > 0:
                    t.take_damage(damage)
                    self.log.append(f"[DÉGÂTS] {entity.name} inflige {damage} dégâts à {t.name}")
                    
                    # Appliquer le lifesteal si présent
                    if ability_data.get("lifesteal_percent"):
                        lifesteal_amount = int(damage * ability_data["lifesteal_percent"])
                        entity.heal(lifesteal_amount)
                        self.log.append(f"[LIFESTEAL] {entity.name} récupère {lifesteal_amount} PV")
                
                # Appliquer les effets spéciaux
                self.apply_advanced_effects(entity, ability_data, t, damage)
        
        return True
    
    def apply_advanced_effects(self, entity, ability_data, target, damage=0):
        """Applique les effets avancés d'une capacité"""
        
        # Effets de graines
        if ability_data.get("plant_seed"):
            if seed_system:
                seed_damage = ability_data.get("seed_damage", 10)
                seed_duration = ability_data.get("seed_duration", 10)
                seed_system.plant_seed(target.id, seed_damage, seed_duration, entity.id)
                self.log.append(f"[GRAINE] {entity.name} plante une graine sur {target.name}")
        
        if ability_data.get("explode_seeds"):
            if seed_system:
                explosion = seed_system.explode_seeds(target.id)
                if explosion["damage"] > 0:
                    target.take_damage(explosion["damage"])
                    self.log.append(f"[EXPLOSION] {explosion['seeds_exploded']} graines explosent sur {target.name} pour {explosion['damage']} dégâts")
        
        # Effets d'esquive temporaire
        if ability_data.get("dodge_boost"):
            if advanced_abilities:
                dodge_boost = ability_data["dodge_boost"]
                dodge_duration = ability_data.get("dodge_duration", 2)
                advanced_abilities.add_temporary_effect(target.id, "dodge", dodge_boost, dodge_duration)
                self.log.append(f"[ESQUIVE] {target.name} gagne +{dodge_boost*100}% d'esquive pour {dodge_duration} tour(s)")
        
        # Effets de défense temporaire
        if ability_data.get("defense_boost"):
            if advanced_abilities:
                defense_boost = ability_data["defense_boost"]
                defense_duration = ability_data.get("defense_duration", 2)
                advanced_abilities.add_temporary_effect(target.id, "defense", defense_boost, defense_duration)
                self.log.append(f"[DÉFENSE] {target.name} gagne +{defense_boost} de défense pour {defense_duration} tour(s)")
        
        # Effets de silence
        if ability_data.get("silence_duration"):
            if advanced_abilities:
                silence_duration = ability_data["silence_duration"]
                advanced_abilities.add_temporary_effect(target.id, "silence", 1.0, silence_duration)
                self.log.append(f"[SILENCE] {target.name} est silencieux pour {silence_duration} tour(s)")
        
        # Effets d'étourdissement
        if ability_data.get("stun_chance"):
            stun_chance = ability_data["stun_chance"]
            if random.randint(1, 100) <= stun_chance:
                if advanced_abilities:
                    advanced_abilities.add_temporary_effect(target.id, "stun", 1.0, 1)
                    self.log.append(f"[ÉTOURDISSEMENT] {target.name} est étourdi")
        
        # Effets de dégâts de zone (splash)
        if ability_data.get("splash_damage"):
            splash_damage = ability_data["splash_damage"]
            splash_targets = ability_data.get("splash_targets", "adjacent_enemies")
            
            if splash_targets == "adjacent_enemies":
                # Trouver les ennemis adjacents
                adjacent_enemies = self.get_adjacent_enemies(target)
                for enemy in adjacent_enemies:
                    splash_damage_amount = int(damage * splash_damage)
                    enemy.take_damage(splash_damage_amount)
                    self.log.append(f"[SPLASH] {enemy.name} subit {splash_damage_amount} dégâts de zone")
        
        # Passifs temporaires
        if "grant_passive" in ability_data:
            if advanced_abilities:
                passive_id = ability_data["grant_passive"]
                duration = ability_data.get("passive_duration", 1)
                advanced_abilities.add_temporary_passive(target.id, passive_id, duration)
                self.log.append(f"[PASSIF] {entity.name} confère le passif {passive_id} à {target.name} pour {duration} tour(s)")
        
        # Boosts permanents
        if ability_data.get("permanent"):
            if ability_data.get("attack_boost"):
                boost_value = ability_data["attack_boost"]
                entity.stats["attack"] = int(entity.stats.get("attack", 0) * (1 + boost_value))
                self.log.append(f"[BOOST] {entity.name} gagne un boost d'attaque permanent de {boost_value*100}%")
        
        # Effets de contre-attaque
        if ability_data.get("counter_burn"):
            # Ajouter un effet de contre-brûlure
            self.log.append(f"[CONTRE] {entity.name} est protégé par une armure incandescente")
    
    def get_adjacent_enemies(self, target):
        """Retourne les ennemis adjacents à une cible"""
        # Implémentation simplifiée - à adapter selon la logique de positionnement
        all_enemies = [unit for unit in self.get_all_units() if unit.owner != target.owner]
        # Pour l'instant, retourner tous les ennemis (à améliorer)
        return all_enemies
    
    def get_random_multiple_targets(self, caster, target_count, same_target_allowed=False):
        """Obtient plusieurs cibles aléatoires"""
        all_enemies = [unit for unit in self.get_all_units() if unit.owner != caster.owner and unit.stats.get("hp", 0) > 0]
        
        if not all_enemies:
            return []
        
        if same_target_allowed:
            return [random.choice(all_enemies) for _ in range(target_count)]
        else:
            if len(all_enemies) < target_count:
                return all_enemies
            return random.sample(all_enemies, target_count)
    
    def use_multiple_unit_abilities(self, unit, ability_targets):
        """Utilise plusieurs capacités d'une unité en une fois
        
        Args:
            unit: L'unité qui utilise les capacités
            ability_targets: Liste de tuples (ability, target) ou dict {ability: target}
        
        Returns:
            dict: Résultats de chaque capacité utilisée
        """
        results = {}
        
        # Vérifier que l'unité appartient au joueur actuel
        current_player = self.players[self.current_player_index]
        if unit not in current_player.units:
            self.log.append(f"[ERREUR] {unit.name} n'appartient pas au joueur actuel")
            return {"error": "Unité n'appartient pas au joueur actuel"}
        
        # Vérifier que l'unité est vivante
        if unit.stats.get("hp", 0) <= 0:
            self.log.append(f"[ERREUR] {unit.name} est morte et ne peut pas utiliser de capacité")
            return {"error": "Unité morte"}
        
        # Convertir en liste de tuples si c'est un dict
        if isinstance(ability_targets, dict):
            ability_targets = list(ability_targets.items())
        
        # Utiliser chaque capacité
        for ability, target in ability_targets:
            if ability in unit.abilities:
                result = self.use_ability(unit, ability, target)
                results[ability.name] = {
                    "success": result,
                    "target": getattr(target, 'name', str(target))
                }
            else:
                results[ability.name] = {
                    "success": False,
                    "error": "Capacité non trouvée sur l'unité"
                }
        
        return results
    
    def get_available_abilities(self, unit):
        """Retourne les capacités disponibles d'une unité (pas en cooldown)"""
        if not unit or not hasattr(unit, 'abilities'):
            return []
        
        available = []
        unit_id = id(unit)
        
        # Initialiser les cooldowns si nécessaire
        if unit_id not in self.unit_cooldowns:
            # Initialiser avec 0 pour les capacités prêtes à utiliser
            cooldowns = []
            for ability in unit.abilities:
                cooldowns.append(0)
                # Initialiser aussi le current_cooldown de la capacité
                if hasattr(ability, 'current_cooldown'):
                    ability.current_cooldown = 0
            self.unit_cooldowns[unit_id] = cooldowns
        
        # Vérifier chaque capacité
        for i, ability in enumerate(unit.abilities):
            if self.unit_cooldowns[unit_id][i] == 0:
                available.append(ability)
        
        return available
    
    def get_ability_cooldown(self, entity, ability):
        """Retourne le cooldown restant d'une capacité"""
        if not entity or not ability:
            return -1
        
        entity_name = getattr(entity, 'name', 'Entité inconnue')
        ability_name = getattr(ability, 'name', 'Capacité inconnue')
        
        # Vérifier si c'est le héros (priorité sur les unités)
        if hasattr(entity, 'ability') and entity.ability:
            # Pour les héros, retourner directement le current_cooldown de l'ability
            # (pas besoin de comparer les noms car c'est le même objet)
            if hasattr(entity.ability, 'current_cooldown'):
                cooldown_value = entity.ability.current_cooldown
                self.log.append(f"[DEBUG] get_ability_cooldown - Héros {entity.name} - current_cooldown: {cooldown_value}")
                return cooldown_value
            self.log.append(f"[DEBUG] get_ability_cooldown - Héros {entity.name} - pas de current_cooldown")
            return 0
        
        # Vérifier si c'est une unité
        elif hasattr(entity, 'abilities'):
            # Si la capacité possède un ability_id, utiliser le système par ID
            if hasattr(ability, 'ability_id'):
                try:
                    cooldown = self.get_unit_ability_cooldown(entity, getattr(ability, 'ability_id'))
                    self.log.append(f"[COOLDOWN] {entity.name} - {getattr(ability, 'name', 'N/A')} (ID: {ability.ability_id}): cooldown = {cooldown}")
                    return cooldown
                except Exception as e:
                    self.log.append(f"[ERREUR] Erreur dans get_unit_ability_cooldown: {e}")
                    # En cas d'erreur, retourner 0 au lieu de -1
                    return 0
            # Chercher la capacité par nom
            ability_name = getattr(ability, 'name', '')
            ability_found = False
            for unit_ability in entity.abilities:
                if getattr(unit_ability, 'name', '') == ability_name:
                    ability_found = True
                    break
            
            if ability_found:
                entity_id = id(entity)
                
                # Initialiser les cooldowns si l'unité n'est pas encore dans le système
                if entity_id not in self.unit_cooldowns:
                    cooldowns = []
                    for ab in entity.abilities:
                        cooldowns.append(0)
                        # Initialiser aussi le current_cooldown de la capacité
                        if hasattr(ab, 'current_cooldown'):
                            ab.current_cooldown = 0
                    self.unit_cooldowns[entity_id] = cooldowns
                    self.log.append(f"[COOLDOWN] Initialisation des cooldowns pour {entity.name}")
                
                # Trouver l'index par nom
                ability_index = None
                for i, unit_ability in enumerate(entity.abilities):
                    if getattr(unit_ability, 'name', '') == ability_name:
                        ability_index = i
                        break
                
                if ability_index is not None:
                    cooldown_value = self.unit_cooldowns[entity_id][ability_index]
                    # Log pour debug
                    self.log.append(f"[COOLDOWN] {entity.name} - {ability_name}: cooldown = {cooldown_value}")
                    return cooldown_value
        
        # Si on arrive ici, retourner 0 au lieu de -1 pour éviter les faux négatifs
        return 0
    
    def can_use_ability(self, entity, ability):
        """Vérifie si une entité (unité ou héros) peut utiliser une capacité spécifique"""
        if not entity or not ability:
            return False
        
        # Trouver le joueur propriétaire de l'entité
        owner_player = None
        for player in self.players:
            # Vérifier si c'est une unité du joueur
            if entity in player.units:
                owner_player = player
                break
            # Vérifier si c'est le héros du joueur
            elif entity == player.hero:
                owner_player = player
                break
        
        if not owner_player:
            return False
        
        # Vérifier que l'entité appartient au joueur actuel (pour l'utilisation)
        current_player = self.players[self.current_player_index]
        if owner_player != current_player:
            return False
        
        # Vérifier si c'est une unité
        if entity in owner_player.units:
            # Vérifier que l'unité est vivante
            if entity.stats.get("hp", 0) <= 0:
                return False
            
            # Si la capacité possède un ability_id, déléguer au système par ID
            if hasattr(ability, 'ability_id'):
                return self.can_use_ability_by_id(entity, getattr(ability, 'ability_id'))
            
            # Vérifier que la capacité existe sur l'unité (par nom)
            ability_name = getattr(ability, 'name', '')
            ability_found = any(getattr(unit_ability, 'name', '') == ability_name for unit_ability in entity.abilities)
            if not ability_found:
                return False
        
        # Vérifier si c'est le héros
        elif entity == owner_player.hero:
            # Vérifier que le héros est vivant
            if entity.base_stats.get("hp", 0) <= 0:
                return False
            
            # Vérifier que la capacité existe sur le héros (par nom au lieu de l'identité d'objet)
            if not hasattr(entity, 'ability') or not entity.ability:
                return False
            
            hero_ability_name = getattr(entity.ability, 'name', '')
            ability_name = getattr(ability, 'name', '')
            if hero_ability_name != ability_name:
                return False
        
        # Vérifier le cooldown
        cooldown = self.get_ability_cooldown(entity, ability)
        entity_name = getattr(entity, 'name', 'Entité inconnue')
        ability_name = getattr(ability, 'name', 'Capacité inconnue')
        
        # Log détaillé pour debug
        if cooldown > 0:
            self.log.append(f"[DEBUG] {entity_name} ne peut pas utiliser {ability_name} - cooldown: {cooldown}")
        else:
            self.log.append(f"[DEBUG] {entity_name} peut utiliser {ability_name} - cooldown: {cooldown}")
        
        return cooldown == 0
    
    def cleanup_dead_units(self):
        """Nettoie immédiatement les unités mortes de tous les joueurs"""
        for player in self.players:
            original_count = len(player.units)
            player.remove_dead_units()
            removed_count = original_count - len(player.units)
            if removed_count > 0:
                self.log.append(f"[NETTOYAGE] {removed_count} unité(s) morte(s) retirée(s) de {player.name}")

    def next_turn(self):
        try:
            self.log.append(f"[TOUR] Passage au tour suivant - Tour actuel: {self.turn_count}, Joueur actuel: {self.current_player_index}")
        except Exception as e:
            print(f"[ERREUR] Exception dans next_turn() au début: {e}")
            import traceback
            print(f"[ERREUR] Traceback: {traceback.format_exc()}")
            return
        
        try:
            current_player = self.players[self.current_player_index]
            opponent = current_player.opponent
            
            # Initialisation du mana max au premier tour seulement
            if self.current_player_index == 0 and self.turn_count == 1:
                # Premier tour : s'assurer que le mana est initialisé à 1 pour les deux joueurs
                if current_player.max_mana < 1:
                    current_player.max_mana = 1
                    self.log.append(f"[MANA] {current_player.name} mana max initialisé à 1")
                if opponent.max_mana < 1:
                    opponent.max_mana = 1
                    self.log.append(f"[MANA] {opponent.name} mana max initialisé à 1")
            
            # Remplir le mana du joueur actuel
            
            old_mana = current_player.mana
            old_max_mana = current_player.max_mana
            current_player.mana = current_player.max_mana
            
            self.log.append(f"[MANA] {current_player.name} mana rempli ({old_mana} → {current_player.mana}/{current_player.max_mana})")
            if old_mana != current_player.mana:
                self.log.append(f"[MANA] {current_player.name} mana a changé de {old_mana} à {current_player.mana}")
            else:
                self.log.append(f"[MANA] {current_player.name} mana inchangé ({current_player.mana})")
            
            
            # Initialisation du mana pour l'adversaire si nécessaire (seulement au début du jeu)
            if not hasattr(opponent, 'mana') or not hasattr(opponent, 'max_mana'):
                opponent.mana = 1
                opponent.max_mana = 1
            
            # Phase de pioche - SEULEMENT si le joueur a moins de 9 cartes (selon documentation)
            if len(current_player.hand) < 9:
                drawn_card = current_player.draw_card()
                if drawn_card:
                    self.log.append(f"[PIOCHE] {current_player.name} pioche {drawn_card.name}")
                # Note: pas besoin de détruire la carte car draw_card() ne pioche que si < 9 cartes
            
            # Phase principale : chaque unité attaque ou utilise une capacité
            for unit in current_player.units:
                # Initialiser les cooldowns si besoin
                if id(unit) not in self.unit_cooldowns:
                    # Initialiser avec 0 pour les capacités prêtes à utiliser
                    cooldowns = []
                    for ability in unit.abilities:
                        cooldowns.append(0)
                        # Initialiser aussi le current_cooldown de la capacité
                        if hasattr(ability, 'current_cooldown'):
                            ability.current_cooldown = 0
                    self.unit_cooldowns[id(unit)] = cooldowns
                
                # Vérifier si l'unité est étourdie
                if hasattr(unit, 'active_effects') and any(eff["type"] == "stun" and eff["duration"] > 0 for eff in getattr(unit, 'active_effects', [])):
                    self.log.append(f"[STUN] {unit.name} est étourdi et ne peut pas agir ce tour.")
                    continue
                
                # Appliquer les effets temporaires (poison, burn, etc.)
                self.process_temporary_effects(unit)
                
                # Vérifier que l'unité est vivante et peut attaquer
                if unit.stats.get("attack", 0) > 0 and unit.stats.get("hp", 0) > 0:
                    # Filtrer les unités vivantes uniquement
                    targets = [u for u in opponent.units if u.stats.get("hp", 0) > 0]
                    if targets:
                        target = random.choice(targets)
                        # Vérifier que la cible est toujours vivante
                        if target.stats.get("hp", 0) <= 0:
                            continue
                        
                        # Attaque normale
                        multiplier = self.get_elemental_multiplier(unit.element, target.element)
                        base_damage = int(unit.stats["attack"] * multiplier)
                        
                        # Précision puis esquive
                        accuracy = unit.stats.get("accuracy", 99)
                        evasion = target.stats.get("evasion", 0)
                        
                        if random.uniform(0, 100) > accuracy:
                            target_name = getattr(target, 'name', str(target))
                            self.log.append(f"[RATÉ] {unit.name} rate son attaque sur {target_name} ! (Précision: {accuracy}%)")
                        elif random.uniform(0, 100) < evasion:
                            target_name = getattr(target, 'name', str(target))
                            self.log.append(f"[ESQUIVE] {target_name} esquive l'attaque de {unit.name} ! (Esquive: {evasion}%)")
                        else:
                            crit_chance = unit.stats.get("crit_chance", 1)
                            is_crit = random.randint(1, 100) <= crit_chance
                            crit_mult = 1.2 if is_crit else 1.0  # Multiplicateur critique 20% selon la doc
                            final_base_damage = int(base_damage * crit_mult)
                            defense = target.stats.get("defense", 0)
                            reduction = min(defense, 75) / 100.0
                            final_damage = int(final_base_damage * (1 - reduction))
                            old_hp, new_hp, actual_damage = self.apply_damage_with_shield(target, final_damage, f"{unit.name}")
                            target_name = getattr(target, 'name', str(target))
                            target_element = getattr(target, 'element', 'N/A')
                            log_msg = f"[ATTAQUE] {unit.name} ({unit.element}) attaque {target_name} ({target_element}) : ATK={unit.stats['attack']} x{multiplier} DEF={defense} (-{int(reduction*100)}%) => {final_damage} dégâts"
                            if old_hp is not None and new_hp is not None:
                                log_msg += f" | HP: {old_hp} → {new_hp}"
                            if is_crit:
                                log_msg += " [CRITIQUE!]"
                            self.log.append(log_msg)
                            
                            # Nettoyer immédiatement si la cible meurt
                            if target.stats.get("hp", 0) <= 0:
                                self.log.append(f"[MORT] {target_name} est mort")
                                self.cleanup_dead_units()
                    else:
                        # Pas d'unités vivantes, attaquer le héros
                        hero = opponent.hero
                        if hero and hero.stats.get("hp", 0) > 0:
                            # Attaque du héros
                            multiplier = self.get_elemental_multiplier(unit.element, hero.element)
                            base_damage = int(unit.stats["attack"] * multiplier)
                            
                            # Précision puis esquive
                            accuracy = unit.stats.get("accuracy", 99)
                            evasion = hero.current_stats.get("evasion", 0)
                            
                            if random.uniform(0, 100) > accuracy:
                                hero_name = getattr(hero, 'name', str(hero))
                                self.log.append(f"[RATÉ] {unit.name} rate son attaque sur {hero_name} ! (Précision: {accuracy}%)")
                            elif random.uniform(0, 100) < evasion:
                                hero_name = getattr(hero, 'name', str(hero))
                                self.log.append(f"[ESQUIVE] {hero_name} esquive l'attaque de {unit.name} ! (Esquive: {evasion}%)")
                            else:
                                crit_chance = unit.stats.get("crit_chance", 1)
                                is_crit = random.randint(1, 100) <= crit_chance
                                crit_mult = 1.2 if is_crit else 1.0  # Multiplicateur critique 20% selon la doc
                                final_base_damage = int(base_damage * crit_mult)
                                defense = hero.defense
                                reduction = min(defense, 75) / 100.0
                                final_damage = int(final_base_damage * (1 - reduction))
                                old_hp, new_hp, actual_damage = self.apply_damage_with_shield(hero, final_damage, f"{unit.name}")
                                hero_name = getattr(hero, 'name', str(hero))
                                hero_element = getattr(hero, 'element', 'N/A')
                                log_msg = f"[ATTAQUE] {unit.name} ({unit.element}) attaque le héros {hero_name} ({hero_element}) : ATK={unit.stats['attack']} x{multiplier} DEF={defense} (-{int(reduction*100)}%) => {final_damage} dégâts"
                                if old_hp is not None and new_hp is not None:
                                    log_msg += f" | HP: {old_hp} → {new_hp}"
                                if is_crit:
                                    log_msg += " [CRITIQUE!]"
                                self.log.append(log_msg)
                                
                                # Nettoyer immédiatement si le héros meurt
                                if hero.hp <= 0:
                                    self.log.append(f"[MORT] {hero_name} est mort")
                                    self.cleanup_dead_units()

            # Phase de résolution : effets temporaires déjà traités
            
            # NOTE : Le mana n'est pas perdu à la fin du tour, il reste disponible
            # Le mana se remplit au début du tour et reste disponible pendant tout le tour
            # Il n'est consommé que quand le joueur utilise des cartes
            
            # Phase de fin : changer de joueur
            finishing_player = current_player  # Conserver le joueur qui termine son tour
            self.current_player_index = (self.current_player_index + 1) % len(self.players)
            
            # Phase IA automatique si c'est le tour de l'IA (joueur 1)
            if self.current_player_index == 1:  # Tour de l'IA
                current_player = self.players[self.current_player_index]
                current_player.AI_play_turn(self)
            
            # RÉDUCTION DES COOLDOWNS : À la fin de chaque tour complet (quand on revient au joueur 0)
            # CORRECTION : Réduire les cooldowns seulement quand on revient au joueur 0 (fin de tour complet)
            
            # Réduire les cooldowns du joueur qui vient de finir son tour
            try:
                self._reduce_player_cooldowns(finishing_player)
                self.log.append(f"[COOLDOWN] Cooldowns réduits pour {finishing_player.name}")
            except Exception as e:
                self.log.append(f"[ERREUR] Exception dans _reduce_player_cooldowns(): {e}")
                import traceback
                self.log.append(f"[ERREUR] Traceback: {traceback.format_exc()}")
            
            # Incrémenter le tour seulement quand on revient au joueur 0
            if self.current_player_index == 0:
                self.turn_count += 1
                self.log.append(f"[TOUR] Nouveau tour : {self.turn_count}")
                
                # Mettre à jour les systèmes avancés
                self.update_advanced_systems()
                
                # Augmenter le mana max des deux joueurs de 1.0 point par tour complet
                # (sauf au premier tour où le mana est déjà initialisé à 1)
                if self.turn_count > 1:  # Pas au premier tour (déjà initialisé)
                    # Augmenter le mana max du joueur 0
                    player0 = self.players[0]
                    if player0.max_mana < 15:
                        old_max_mana = player0.max_mana
                        player0.max_mana += 1.0
                        self.log.append(f"[MANA] {player0.name} gagne 1 cristal de mana max ({old_max_mana} → {player0.max_mana}/15)")
                    else:
                        self.log.append(f"[MANA] {player0.name} mana max déjà au maximum ({player0.max_mana}/15)")
                    
                    # Augmenter le mana max du joueur 1
                    player1 = self.players[1]
                    if player1.max_mana < 15:
                        old_max_mana = player1.max_mana
                        player1.max_mana += 1.0
                        self.log.append(f"[MANA] {player1.name} gagne 1 cristal de mana max ({old_max_mana} → {player1.max_mana}/15)")
                    else:
                        self.log.append(f"[MANA] {player1.name} mana max déjà au maximum ({player1.max_mana}/15)")
            else:
                self.log.append(f"[TOUR] Phase {self.current_player_index + 1} du tour {self.turn_count}")
            
            # Log de fin de tour
            self.log.append(f"[FIN TOUR] {current_player.name} - Tour {self.turn_count} terminé")
            
            return True
            
        except Exception as e:
            print(f"[ERREUR] Exception dans next_turn() principal: {e}")
            import traceback
            print(f"[ERREUR] Traceback: {traceback.format_exc()}")
            return False

    def is_game_over(self):
        """Vérifie si la partie est terminée et retourne le résultat"""
        # Vérifier les conditions de victoire
        victory_conditions = self.check_victory_conditions()
        
        if not victory_conditions:
            return {"status": "ongoing", "message": "La partie continue"}
        
        # Si plusieurs conditions, prioriser la mort du héros
        hero_death = [cond for cond in victory_conditions if cond["type"] == "hero_death"]
        unit_death_hero_inactive = [cond for cond in victory_conditions if cond["type"] == "unit_death_hero_inactive"]
        fatigue = [cond for cond in victory_conditions if cond["type"] == "fatigue"]
        
        if hero_death:
            # Un héros est mort
            if len(hero_death) == 2:
                return {"status": "draw", "message": "Match nul - tous les héros sont morts"}
            else:
                loser = hero_death[0]["player"]
                winner = next(p for p in self.players if p != loser)
                return {"status": "victory", "winner": winner, "message": f"{winner.name} remporte la victoire !"}
        
        elif unit_death_hero_inactive:
            # Toutes les unités mortes ET héros inactif
            if len(unit_death_hero_inactive) == 2:
                return {"status": "draw", "message": "Match nul - toutes les unités sont mortes et héros inactifs"}
            else:
                loser = unit_death_hero_inactive[0]["player"]
                winner = next(p for p in self.players if p != loser)
                return {"status": "victory", "winner": winner, "message": f"{winner.name} remporte la victoire !"}
        
        elif fatigue:
            # Fatigue (plus de cartes ou tour 50)
            # Vérifier d'abord si c'est le tour 50
            tour_50_fatigue = [cond for cond in fatigue if cond["player"] is None]
            if tour_50_fatigue:
                return {"status": "draw", "message": "Match nul - limite de tours atteinte (50)"}
            
            # Sinon, fatigue normale
            if len(fatigue) == 2:
                return {"status": "draw", "message": "Match nul - fatigue générale"}
            else:
                loser = fatigue[0]["player"]
                winner = next(p for p in self.players if p != loser)
                return {"status": "victory", "winner": winner, "message": f"{winner.name} remporte la victoire !"}
        
        return {"status": "ongoing", "message": "La partie continue"}
    
    def check_victory_conditions(self):
        """Vérifie toutes les conditions de victoire possibles"""
        results = []
        
        # Condition 1: Héros mort (condition principale)
        for player in self.players:
            if not player.hero or not player.is_alive():
                results.append({
                    "type": "hero_death",
                    "player": player,
                    "message": f"{player.name} a perdu - son héros est mort"
                })
        
        # Condition 2: Toutes les unités mortes ET héros inactif (selon documentation)
        for player in self.players:
            # Vérifier si toutes les unités sont mortes
            living_units = [unit for unit in player.units if unit.stats.get("hp", 0) > 0]
            if len(living_units) == 0:
                # Vérifier si le héros est inactif
                if player.hero and not getattr(player.hero, 'is_active', False):
                    results.append({
                        "type": "unit_death_hero_inactive",
                        "player": player,
                        "message": f"{player.name} a perdu - toutes ses unités sont mortes et son héros est inactif"
                    })
        
        # Condition 3: Plus de cartes dans le deck (fatigue)
        for player in self.players:
            if len(player.deck) == 0:
                results.append({
                    "type": "fatigue",
                    "player": player,
                    "message": f"{player.name} a perdu - plus de cartes dans le deck"
                })
        
        # Condition 4: Tour 50 (fatigue générale)
        if self.turn_count >= 50:
            results.append({
                "type": "fatigue",
                "player": None,
                "message": "Match nul - limite de tours atteinte (50)"
            })
        
        return results

    def _initialize_hero_cooldowns(self, player):
        """Initialise les cooldowns du héros du joueur"""
        if player.hero and player.hero.ability:
            ability = player.hero.ability
            if hasattr(ability, 'cooldown') and hasattr(ability, 'current_cooldown'):
                # Les héros commencent aussi avec des cooldowns à 0
                ability.current_cooldown = 0

    def _reduce_player_cooldowns(self, player):
        """Réduit les cooldowns des unités et du héros du joueur à la fin de son tour"""
        player_name = player.name
        self.log.append(f"[COOLDOWN] === RÉDUCTION DES COOLDOWNS pour {player_name} ===")
        
        # Réduire les cooldowns des unités du joueur (nouveau système)
        self.log.append(f"[COOLDOWN] {player_name} a {len(player.units)} unités sur le terrain")
        for unit in player.units:
            self.log.append(f"[COOLDOWN] Vérification des cooldowns pour {unit.name}")
            # Utiliser le nouveau système de cooldown
            self.reduce_ability_cooldowns(unit)
        
        # Réduire les cooldowns du héros du joueur (ancien système maintenu pour compatibilité)
        if player.hero and player.hero.ability:
            ability = player.hero.ability
            if hasattr(ability, 'current_cooldown') and ability.current_cooldown > 0:
                old_cooldown = ability.current_cooldown
                ability.current_cooldown = max(0, ability.current_cooldown - 1)
                new_cooldown = ability.current_cooldown
                if old_cooldown != new_cooldown:
                    ability_name = ability.name
                    self.log.append(f"[COOLDOWN] {player_name} - {player.hero.name} - {ability_name} : cooldown {old_cooldown} → {new_cooldown}")
                    if new_cooldown == 0:
                        self.log.append(f"[COOLDOWN] {player.hero.name} - {ability_name} est maintenant prête à utiliser !")
        
        self.log.append(f"[COOLDOWN] === FIN RÉDUCTION DES COOLDOWNS pour {player_name} ===")

    def get_log(self):
        # Fusionne les logs des joueurs et du moteur
        logs = []
        for p in self.players:
            logs.extend(p.log)
        logs.extend(self.log)
        return logs 

    def validate_deck(self, player):
        """Valide la cohérence du deck selon la documentation"""
        errors = []
        warnings = []
        
        self.log.append(f"[VALIDATION] Validation du deck de {player.name}")
        self.log.append(f"[VALIDATION] Héros: {player.hero}")
        self.log.append(f"[VALIDATION] Unités: {len(player.units) if player.units else 0}")
        self.log.append(f"[VALIDATION] Cartes: {len(player.deck) if player.deck else 0}")
        
        # Validation du héros
        if not player.hero:
            errors.append("Héros manquant (1 héros obligatoire)")
            self.log.append("[VALIDATION] ERREUR: Héros manquant")
        elif not hasattr(player.hero, 'name'):
            errors.append("Héros invalide (nom manquant)")
            self.log.append("[VALIDATION] ERREUR: Héros sans nom")
        else:
            self.log.append(f"[VALIDATION] Héros valide: {player.hero.name}")
        
        # Validation des unités
        if not player.units:
            errors.append("Aucune unité dans le deck (5 unités obligatoires)")
            self.log.append("[VALIDATION] ERREUR: Aucune unité")
        elif len(player.units) != 5:
            errors.append(f"Nombre d'unités incorrect ({len(player.units)}/5 obligatoires)")
            self.log.append(f"[VALIDATION] ERREUR: {len(player.units)} unités au lieu de 5")
        else:
            self.log.append(f"[VALIDATION] Unités valides: {len(player.units)}")
        
        # Vérification des unités uniques (1 exemplaire par unité maximum)
        unit_names = [unit.name for unit in player.units if hasattr(unit, 'name')]
        if len(unit_names) != len(set(unit_names)):
            errors.append("Unités en double détectées (1 exemplaire par unité maximum)")
            self.log.append("[VALIDATION] ERREUR: Unités en double")
        else:
            self.log.append("[VALIDATION] Unités uniques OK")
        
        # Validation des cartes de sorts
        if not player.deck:
            errors.append("Aucune carte de sort dans le deck (30 cartes obligatoires)")
            self.log.append("[VALIDATION] ERREUR: Aucune carte")
        elif len(player.deck) != 30:
            errors.append(f"Nombre de cartes de sorts incorrect ({len(player.deck)}/30 obligatoires)")
            self.log.append(f"[VALIDATION] ERREUR: {len(player.deck)} cartes au lieu de 30")
        else:
            self.log.append(f"[VALIDATION] Cartes valides: {len(player.deck)}")
        
        # Vérification des exemplaires de cartes (max 2 exemplaires identiques)
        card_counts = {}
        for card in player.deck:
            if hasattr(card, 'name'):
                card_counts[card.name] = card_counts.get(card.name, 0) + 1
        
        for card_name, count in card_counts.items():
            if count > 2:
                errors.append(f"Trop d'exemplaires de {card_name} ({count}/2 maximum)")
                self.log.append(f"[VALIDATION] ERREUR: {count} exemplaires de {card_name}")
        
        # Vérification des cartes valides
        for card in player.deck:
            if not hasattr(card, 'name'):
                errors.append("Carte invalide (nom manquant)")
                self.log.append("[VALIDATION] ERREUR: Carte sans nom")
            elif not hasattr(card, 'cost'):
                warnings.append(f"Carte '{card.name}' sans coût en mana")
                self.log.append(f"[VALIDATION] WARNING: {card.name} sans coût")
        
        self.log.append(f"[VALIDATION] Résultat: {len(errors)} erreurs, {len(warnings)} warnings")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    def initialize_game(self):
        """Initialise le jeu avec validation des decks"""
        self.log.append("[INITIALISATION] Validation des decks...")
        
        for i, player in enumerate(self.players):
            validation = self.validate_deck(player)
            if not validation["valid"]:
                self.log.append(f"[ERREUR] Deck du joueur {player.name} invalide:")
                for error in validation["errors"]:
                    self.log.append(f"  - {error}")
                raise ValueError(f"Deck du joueur {player.name} invalide")
            
            if validation["warnings"]:
                self.log.append(f"[ATTENTION] Warnings pour le deck du joueur {player.name}:")
                for warning in validation["warnings"]:
                    self.log.append(f"  - {warning}")
            
            self.log.append(f"[VALIDATION] Deck du joueur {player.name} validé avec succès")
        
        # Initialisation du mana
        for player in self.players:
            player.mana = 1
            player.max_mana = 1
        
        # Initialisation des héros avec leurs données JSON
        for player in self.players:
            self.initialize_hero_from_json(player)
        
        # Initialisation des cooldowns des héros
        for player in self.players:
            if player.hero and player.hero.ability:
                # Initialiser le current_cooldown à 0 au début du combat
                player.hero.ability.current_cooldown = 0
                self.log.append(f"[INITIALISATION] Cooldown initialisé pour {player.hero.name} - {player.hero.ability.name}: 0 (prêt à utiliser)")
        
        # Déploiement automatique des unités sur le champ de bataille
        for player in self.players:
            self.log.append(f"[INITIALISATION] Déploiement des unités pour {player.name} - Unités avant: {len(player.units)}")
            self.deploy_units_from_deck(player)
            self.log.append(f"[INITIALISATION] Déploiement terminé pour {player.name} - Unités après: {len(player.units)}")
        
        # Initialisation des cooldowns des unités
        self.initialize_unit_cooldowns()
        
        # Mélanger les decks avant la pioche initiale
        for player in self.players:
            import random
            random.shuffle(player.deck)
            self.log.append(f"[MÉLANGE] Deck de {player.name} mélangé ({len(player.deck)} cartes)")
        
        # Configurer le nombre de mulligans selon l'ordre de jeu
        # Le joueur qui commence (index 0) a 1 mulligan, l'autre (index 1) a 2 mulligans
        for player in self.players:
            player.mulligan_count = 0  # Initialiser le compteur à 0
        
        self.players[0].max_mulligans = 1  # Premier joueur
        self.players[1].max_mulligans = 2  # Deuxième joueur
        self.log.append(f"[MULLIGAN] {self.players[0].name} a {self.players[0].max_mulligans} mulligan(s)")
        self.log.append(f"[MULLIGAN] {self.players[1].name} a {self.players[1].max_mulligans} mulligan(s)")
        
        # Pioche initiale de 5 cartes (APRÈS la validation)
        for player in self.players:
            for _ in range(5):
                player.draw_card()
            self.log.append(f"[PIOCHE INITIALE] {player.name} a pioché {len(player.hand)} cartes")
        
        self.log.append("[INITIALISATION] Jeu initialisé avec succès")

    def deploy_units_from_deck(self, player: Player):
        """Déploie automatiquement les unités sur le champ de bataille"""
        self.log.append(f"[DÉPLOIEMENT] Déploiement des unités pour {player.name}...")
        
        # Les unités sont déjà dans player.units, il faut juste les initialiser
        if not player.units:
            self.log.append(f"[DÉPLOIEMENT] {player.name} n'a pas d'unités à déployer")
            return
        
        # Initialiser les unités existantes
        deployed_count = 0
        for unit in player.units:
            if deployed_count >= 5:  # Maximum 5 unités sur le champ
                break
            
            # S'assurer que l'unité a des stats valides
            if not hasattr(unit, 'stats') or not unit.stats:
                if hasattr(unit, 'base_stats') and unit.base_stats:
                    unit.stats = unit.base_stats.copy()
                else:
                    unit.stats = {'hp': 100, 'attack': 10, 'defense': 5}
            
            # S'assurer que l'unité a des HP valides
            if unit.stats.get('hp', 0) <= 0:
                if hasattr(unit, 'base_stats') and unit.base_stats:
                    unit.stats['hp'] = unit.base_stats.get('hp', 100)
                else:
                    unit.stats['hp'] = 100
            
            # S'assurer que l'unité a une image_path
            if not hasattr(unit, 'image_path') or not unit.image_path:
                unit.image_path = 'Crea/1.png'  # Image par défaut
            
            # S'assurer que l'unité a un élément
            if not hasattr(unit, 'element') or not unit.element:
                unit.element = 'NEUTRE'
            
            # S'assurer que l'unité a une rareté
            if not hasattr(unit, 'rarity') or not unit.rarity:
                unit.rarity = 'Commun'
            
            # S'assurer que l'unité a une description
            if not hasattr(unit, 'description') or not unit.description:
                unit.description = 'Aucune description'
            
            # S'assurer que l'unité a des stats secondaires
            if not hasattr(unit, 'crit_pct'):
                unit.crit_pct = 3.0
            if not hasattr(unit, 'esquive_pct'):
                unit.esquive_pct = 1.0
            if not hasattr(unit, 'precision_pct'):
                unit.precision_pct = 99.0
            
            # S'assurer que l'unité a des capacités
            if not hasattr(unit, 'abilities') or not unit.abilities:
                unit.abilities = []
            
            deployed_count += 1
            self.log.append(f"[DÉPLOIEMENT] {player.name} déploie {unit.name} sur le champ de bataille (HP: {unit.stats.get('hp', 0)}, ATK: {unit.stats.get('attack', 0)}, DEF: {unit.stats.get('defense', 0)})")
        
        self.log.append(f"[DÉPLOIEMENT] {player.name} a déployé {deployed_count} unités sur le champ de bataille")
        self.log.append(f"[DÉPLOIEMENT] {player.name} a {len(player.deck)} cartes dans son deck")
    def initialize_hero_from_json(self, player: Player):
        """Initialise le héros avec ses données JSON"""
        if not player.hero:
            self.log.append(f"[HÉROS] {player.name} n'a pas de héros")
            return
        
        hero = player.hero
        self.log.append(f"[HÉROS] Initialisation du héros {hero.name} pour {player.name}...")
        
        # S'assurer que le héros a des stats valides depuis les données JSON
        if not hasattr(hero, 'current_stats') or not hero.current_stats:
            # Initialiser les stats depuis base_stats (données JSON)
            if hasattr(hero, 'base_stats') and hero.base_stats:
                hero.current_stats = hero.base_stats.copy()
                self.log.append(f"[HÉROS] Stats initialisées depuis JSON pour {hero.name}: {hero.current_stats}")
            else:
                # Fallback si base_stats n'existe pas
                hero.current_stats = {'hp': 1000, 'attack': 20, 'defense': 15}
                self.log.append(f"[HÉROS] Stats par défaut utilisées pour {hero.name}: {hero.current_stats}")
        
        # S'assurer que le héros a des HP valides
        if hero.current_stats.get('hp', 0) <= 0:
            if hasattr(hero, 'base_stats') and hero.base_stats:
                hero.current_stats['hp'] = hero.base_stats.get('hp', 1000)
            else:
                hero.current_stats['hp'] = 1000
            self.log.append(f"[HÉROS] HP corrigé pour {hero.name}: {hero.current_stats['hp']}")
        
        # S'assurer que le héros a une image_path
        if not hasattr(hero, 'image_path') or not hero.image_path:
            hero.image_path = 'Hero/1.png'  # Image par défaut
            self.log.append(f"[HÉROS] Image par défaut assignée pour {hero.name}: {hero.image_path}")
        
        # S'assurer que le héros a un élément
        if not hasattr(hero, 'element') or not hero.element:
            hero.element = 'NEUTRE'
            self.log.append(f"[HÉROS] Élément par défaut assigné pour {hero.name}: {hero.element}")
        
        # S'assurer que le héros a une rareté
        if not hasattr(hero, 'rarity') or not hero.rarity:
            hero.rarity = 'Commun'
            self.log.append(f"[HÉROS] Rareté par défaut assignée pour {hero.name}: {hero.rarity}")
        
        # S'assurer que le héros a une capacité
        if not hasattr(hero, 'ability') or not hero.ability:
            # Créer une capacité par défaut
            from .models import Ability
            hero.ability = Ability(
                name="Attaque de base",
                description="Attaque de base du héros",
                cooldown=0,
                target_type="single_enemy",
                ability_id="hero_basic"
            )
            self.log.append(f"[HÉROS] Capacité par défaut assignée pour {hero.name}")
        
        # S'assurer que le héros a des stats secondaires
        if not hasattr(hero, 'crit_pct'):
            hero.crit_pct = 5.0
        if not hasattr(hero, 'esquive_pct'):
            hero.esquive_pct = 2.0
        if not hasattr(hero, 'precision_pct'):
            hero.precision_pct = 95.0
        
        self.log.append(f"[HÉROS] {player.name} a le héros {hero.name} (HP: {hero.current_stats.get('hp', 0)}, ATK: {hero.current_stats.get('attack', 0)}, DEF: {hero.current_stats.get('defense', 0)})")



    def get_valid_targets(self, card, player, target_type="any"):
        """
        Retourne la liste des cibles valides pour une carte donnée.
        """
        valid_targets = []
        opponent = player.opponent
        
        # Déterminer le type de ciblage requis
        card_target_type = getattr(card, 'target_type', 'any')
        if target_type != "any":
            card_target_type = target_type
        
        # Cibles ennemies
        if card_target_type in ["enemy", "any"]:
            # Unités ennemies vivantes
            for unit in opponent.units:
                if hasattr(unit, 'stats') and unit.stats.get('hp', 0) > 0:
                    valid_targets.append(unit)
            
            # Héros ennemi (seulement s'il est activé)
            if opponent.hero and getattr(opponent.hero, 'is_active', False):
                valid_targets.append(opponent.hero)
        
        # Cibles alliées
        if card_target_type in ["ally", "any"]:
            # Unités alliées vivantes
            for unit in player.units:
                if hasattr(unit, 'stats') and unit.stats.get('hp', 0) > 0:
                    valid_targets.append(unit)
            
            # Héros allié (seulement s'il est activé)
            if player.hero and getattr(player.hero, 'is_active', False):
                valid_targets.append(player.hero)
        
        # Cible soi-même
        if card_target_type == "self":
            if player.hero and getattr(player.hero, 'is_active', False):
                valid_targets.append(player.hero)
        
        return valid_targets
    
    def validate_target(self, card, target, player):
        """
        Valide si une cible est valide pour une carte selon la documentation.
        """
        if not target:
            return False, "Aucune cible sélectionnée"
        
        # Vérification selon le type de carte
        card_type = getattr(card, 'card_type', 'spell')
        
        if card_type == "spell":
            # Cartes de sorts - ciblage selon l'effet
            effect = getattr(card, 'effect', {})
            target_requirement = effect.get('target', 'enemy')
            
            if target_requirement == "enemy":
                if target.get('type') not in ['enemy_unit', 'enemy_hero']:
                    return False, "Cette carte doit cibler un ennemi"
            elif target_requirement == "ally":
                if target.get('type') not in ['ally_unit', 'ally_hero']:
                    return False, "Cette carte doit cibler un allié"
            elif target_requirement == "self":
                if target.get('type') != 'self':
                    return False, "Cette carte doit cibler vous-même"
        
        elif card_type == "unit":
            # Unités - pas de ciblage nécessaire
            return True, "Cible valide"
        
        # Vérifications supplémentaires selon les effets
        if hasattr(card, 'effect'):
            effect = card.effect
            
            # Vérification des conditions spéciales
            if 'condition' in effect:
                condition = effect['condition']
                
                # Condition de PV minimum
                if 'min_hp' in condition:
                    if target.get('hp', 0) < condition['min_hp']:
                        return False, f"Cible doit avoir au moins {condition['min_hp']} PV"
                
                # Condition d'élément
                if 'element' in condition:
                    if target.get('element') != condition['element']:
                        return False, f"Cible doit être de l'élément {condition['element']}"
                
                # Condition de type
                if 'type' in condition:
                    if target.get('type') != condition['type']:
                        return False, f"Cible doit être de type {condition['type']}"
        
        return True, "Cible valide"
    
    def get_targeting_info(self, card, player):
        """
        Retourne les informations de ciblage pour l'interface graphique.
        """
        # Vérifier si la carte a des effets
        if hasattr(card, 'effects') and card.effects:
            # Prendre le premier effet pour déterminer le type de ciblage
            first_effect = card.effects[0]
            target_type = first_effect.get('target', 'none')
            
            if target_type == "none":
                return {
                    "requires_target": False,
                    "target_type": "none",
                    "description": "Aucun ciblage requis"
                }
            elif target_type == "enemy":
                return {
                    "requires_target": True,
                    "target_type": "enemy",
                    "description": "Ciblez un ennemi",
                    "valid_targets": self.get_valid_targets(card, player, "enemy")
                }
            elif target_type == "ally":
                return {
                    "requires_target": True,
                    "target_type": "ally", 
                    "description": "Ciblez un allié",
                    "valid_targets": self.get_valid_targets(card, player, "ally")
                }
            elif target_type == "self":
                return {
                    "requires_target": True,
                    "target_type": "self",
                    "description": "Ciblez vous-même",
                    "valid_targets": self.get_valid_targets(card, player, "self")
                }
            elif target_type == "all_enemies":
                return {
                    "requires_target": False,  # Pas de ciblage manuel pour les sorts de zone
                    "target_type": "all_enemies",
                    "description": "Affecte tous les ennemis"
                }
            elif target_type == "all_allies":
                return {
                    "requires_target": False,  # Pas de ciblage manuel pour les sorts de zone
                    "target_type": "all_allies",
                    "description": "Affecte tous les alliés"
                }
            elif target_type == "any":
                return {
                    "requires_target": True,
                    "target_type": "any",
                    "description": "Ciblez n'importe quelle cible",
                    "valid_targets": self.get_valid_targets(card, player, "any")
                }
        
        # Fallback pour les cartes sans effets ou avec target_type
        target_type = getattr(card, 'target_type', 'none')
        
        if target_type == "none":
            return {
                "requires_target": False,
                "target_type": "none",
                "description": "Aucun ciblage requis"
            }
        elif target_type == "enemy":
            return {
                "requires_target": True,
                "target_type": "enemy",
                "description": "Ciblez un ennemi",
                "valid_targets": self.get_valid_targets(card, player, "enemy")
            }
        elif target_type == "ally":
            return {
                "requires_target": True,
                "target_type": "ally", 
                "description": "Ciblez un allié",
                "valid_targets": self.get_valid_targets(card, player, "ally")
            }
        elif target_type == "self":
            return {
                "requires_target": True,
                "target_type": "self",
                "description": "Ciblez vous-même",
                "valid_targets": self.get_valid_targets(card, player, "self")
            }
        elif target_type == "any":
            return {
                "requires_target": True,
                "target_type": "any",
                "description": "Ciblez n'importe quelle cible",
                "valid_targets": self.get_valid_targets(card, player, "any")
            }
        
        return {
            "requires_target": False,
            "target_type": "unknown",
            "description": "Type de ciblage inconnu"
        }
    
    def play_card_with_target(self, card_index, target_info, player):
        """
        Joue une carte avec une cible spécifique (pour interface graphique).
        """
        try:
            
            if card_index >= len(player.hand):
                return False, "Index de carte invalide"
            
            card = player.hand[card_index]
            
            # Vérification du mana
            if player.mana < card.cost:
                return False, f"Mana insuffisant ({player.mana}/{card.cost})"
            
            # Vérification de la cible si nécessaire
            targeting_info = self.get_targeting_info(card, player)
            
            if targeting_info["requires_target"]:
                if not target_info:
                    return False, "Cible requise"
                
                is_valid, message = self.validate_target(card, target_info, player)
                if not is_valid:
                    return False, message
                
                target = target_info["target"]  # Correction : "target" au lieu de "object"
            else:
                target = None
            
            # Jouer la carte via la méthode du joueur
            try:
                success = player.play_card(card, target)
            except Exception as e:
                return False, f"Exception dans play_card: {e}"
            
            if success:
                return True, f"Carte {card.name} jouée avec succès"
            else:
                return False, "Erreur lors du jeu de la carte"
                
        except Exception as e:
            return False, f"Exception dans play_card_with_target: {e}"

    def _reduce_all_cooldowns(self):
        """Réduit les cooldowns de toutes les unités de tous les joueurs"""
        self.log.append(f"[COOLDOWN] === RÉDUCTION DES COOLDOWNS GLOBALE ===")
        self.log.append(f"[DEBUG COOLDOWN] _reduce_all_cooldowns() appelé - Tour: {self.turn_count}, Joueur actuel: {self.current_player_index}")
        self.log.append(f"[DEBUG TEST] Test de debug dans _reduce_all_cooldowns() - CODE MODIFIÉ")
        
        # Log des cooldowns avant réduction
        for player in self.players:
            self.log.append(f"[COOLDOWN] {player.name} - Cooldowns avant réduction:")
            for unit in player.units:
                for ability in unit.abilities:
                    cooldown = self.get_ability_cooldown(unit, ability)
                    self.log.append(f"[COOLDOWN]   {unit.name} - {ability.name}: {cooldown}")
        
        for player in self.players:
            self._reduce_player_cooldowns(player)
        
        # Log des cooldowns après réduction
        for player in self.players:
            self.log.append(f"[COOLDOWN] {player.name} - Cooldowns après réduction:")
            for unit in player.units:
                for ability in unit.abilities:
                    cooldown = self.get_ability_cooldown(unit, ability)
                    self.log.append(f"[COOLDOWN]   {unit.name} - {ability.name}: {cooldown}")
        
        self.log.append(f"[COOLDOWN] === FIN RÉDUCTION DES COOLDOWNS GLOBALE ===")
    
    # Méthode supprimée car dupliquée (voir ligne 2712)

    def initialize_unit_cooldowns(self):
        """Initialise les cooldowns de toutes les unités de tous les joueurs"""
        self.log.append(f"[INIT] === INITIALISATION DES COOLDOWNS ===")
        
        for player in self.players:
            self.log.append(f"[INIT] Initialisation des cooldowns pour {player.name}")
            
            # Initialiser les cooldowns des unités
            for unit in player.units:
                entity_id = id(unit)
                if entity_id not in self.unit_cooldowns:
                    cooldowns = []
                    for ability in unit.abilities:
                        cooldowns.append(0)  # Commencer avec 0 (prêt à utiliser)
                    self.unit_cooldowns[entity_id] = cooldowns
                    self.log.append(f"[INIT] {player.name} - {unit.name} : cooldowns initialisés à {cooldowns}")
                else:
                    self.log.append(f"[INIT] {player.name} - {unit.name} : cooldowns déjà existants {self.unit_cooldowns[entity_id]}")
            
            # Initialiser les cooldowns du héros
            if player.hero and player.hero.ability:
                if hasattr(player.hero.ability, 'current_cooldown'):
                    player.hero.ability.current_cooldown = 0
                    self.log.append(f"[INIT] {player.name} - {player.hero.name} : cooldown initialisé à 0")
        
        self.log.append(f"[INIT] === FIN INITIALISATION DES COOLDOWNS ===")
    
    # ===== NOUVELLES MÉTHODES POUR LE SYSTÈME D'EFFETS =====
    
    def use_ability_by_id(self, unit, ability_id: str, target=None):
        """Utilise une capacité par son ID"""
        if not self.effects_manager:
            return False, "Gestionnaire d'effets non disponible"
        
        # Récupérer les informations de la capacité
        ability_data = self.effects_manager.get_ability(ability_id)
        if not ability_data:
            return False, f"Capacité {ability_id} non trouvée"
        
        # Vérifier le cooldown ACTIF (et non la valeur de base)
        active_cooldown = 0
        if hasattr(unit, 'ability_cooldowns'):
            active_cooldown = unit.ability_cooldowns.get(ability_id, 0)
        if active_cooldown > 0:
            return False, f"Capacité en cooldown ({active_cooldown} tours restants)"
        
        # Récupérer le cooldown de base à appliquer APRÈS utilisation
        base_cooldown = self.effects_manager.get_ability_cooldown(
            ability_id, getattr(unit, 'cooldown_modifiers', None)
        )
        
        # Calculer les dégâts
        caster_attack = getattr(unit, 'attack', 0)
        damage_modifiers = 1.0  # TODO: Ajouter les modificateurs de dégâts
        
        damage = self.effects_manager.calculate_ability_damage(ability_id, caster_attack, damage_modifiers)
        
        # Déterminer les cibles
        targets = []
        if target is not None:
            targets = [target]
        else:
            try:
                targets = self.get_available_targets_for_ability(ability_data, unit, self)
            except Exception:
                targets = []
        
        # CORRECTION : Gestion des différents types de ciblage
        target_type = ability_data.get("target_type", "single_enemy")
        
        # Capacités qui s'appliquent à toutes les cibles automatiquement
        auto_apply_types = [
            "all_allies", "all_enemies", "all_units",  # Cibles multiples
            "random_enemy", "random_ally", "random_unit",  # Cibles aléatoires
            "front_row", "back_row",  # Cibles par position
            "chain_enemies", "chain_allies"  # Cibles en chaîne
        ]
        
        if target_type in auto_apply_types:
            # Appliquer les effets à toutes les cibles en une fois
            result = self.effects_manager.apply_ability_effects(ability_id, unit, targets, self)
            if result and getattr(result, 'success', False):
                if getattr(result, 'message', None):
                    self.log.append(f"[EFFETS] {result.message}")
                for effect in getattr(result, 'effects_applied', []) or []:
                    self.log.append(f"[EFFET] {effect} appliqué")
                for chain_effect in getattr(result, 'chain_effects', []) or []:
                    self.log.append(f"[CHAÎNE] {chain_effect} déclenché")
            
            # Appliquer les dégâts sur chaque cible individuellement (si applicable)
            for t in targets:
                if damage > 0:
                    old_hp, new_hp, applied = self.apply_damage_with_shield(t, damage, f"{unit.name}")
                    try:
                        target_name = getattr(t, 'name', 'Cible')
                    except Exception:
                        target_name = 'Cible'
                    if applied and applied > 0:
                        if old_hp is not None and new_hp is not None:
                            self.log.append(f"[CAPACITÉ] {unit.name} utilise {ability_data['name']} sur {target_name} : {applied} dégâts (HP: {old_hp} → {new_hp})")
                        else:
                            self.log.append(f"[CAPACITÉ] {unit.name} utilise {ability_data['name']} sur {target_name} : {applied} dégâts")
                    
                    # Appliquer les marques de foudre (Passif d'Alice)
                    self.apply_lightning_mark(unit, t)
        
        # Capacités adjacentes : ciblage initial + propagation automatique
        elif target_type in ["adjacent_enemies", "adjacent_allies"]:
            # Appliquer sur la cible principale
            primary_target = targets[0] if targets else None
            if primary_target:
                # Appliquer les effets sur la cible principale
                result = self.effects_manager.apply_ability_effects(ability_id, unit, primary_target, self)
                if result and getattr(result, 'success', False):
                    if getattr(result, 'message', None):
                        self.log.append(f"[EFFETS] {result.message}")
                    for effect in getattr(result, 'effects_applied', []) or []:
                        self.log.append(f"[EFFET] {effect} appliqué")
                    for chain_effect in getattr(result, 'chain_effects', []) or []:
                        self.log.append(f"[CHAÎNE] {chain_effect} déclenché")
                
                # Appliquer les dégâts sur la cible principale
                if damage > 0:
                    old_hp, new_hp, applied = self.apply_damage_with_shield(primary_target, damage, f"{unit.name}")
                    try:
                        target_name = getattr(primary_target, 'name', 'Cible')
                    except Exception:
                        target_name = 'Cible'
                    if applied and applied > 0:
                        if old_hp is not None and new_hp is not None:
                            self.log.append(f"[CAPACITÉ] {unit.name} utilise {ability_data['name']} sur {target_name} : {applied} dégâts (HP: {old_hp} → {new_hp})")
                        else:
                            self.log.append(f"[CAPACITÉ] {unit.name} utilise {ability_data['name']} sur {target_name} : {applied} dégâts")
                    
                    # Appliquer les marques de foudre (Passif d'Alice)
                    self.apply_lightning_mark(unit, primary_target)
                
                # PROPAGATION ADJACENTE : Appliquer aux unités adjacentes
                adjacent_targets = self._get_adjacent_targets(primary_target, target_type)
                if adjacent_targets:
                    self.log.append(f"[PROPAGATION] {ability_data['name']} se propage à {len(adjacent_targets)} cibles adjacentes")
                    
                    # Appliquer les effets aux cibles adjacentes (dégâts réduits)
                    adjacent_damage = max(1, int(damage * 0.5))  # 50% des dégâts
                    for adjacent_target in adjacent_targets:
                        # Appliquer les effets (même effets que la cible principale)
                        result = self.effects_manager.apply_ability_effects(ability_id, unit, adjacent_target, self)
                        if result and getattr(result, 'success', False):
                            for effect in getattr(result, 'effects_applied', []) or []:
                                self.log.append(f"[PROPAGATION] {effect} appliqué à {adjacent_target.name}")
                            for chain_effect in getattr(result, 'chain_effects', []) or []:
                                self.log.append(f"[PROPAGATION] {chain_effect} déclenché sur {adjacent_target.name}")
                        
                        # Appliquer les dégâts réduits
                        if adjacent_damage > 0:
                            old_hp, new_hp, applied = self.apply_damage_with_shield(adjacent_target, adjacent_damage, f"{unit.name}")
                            try:
                                target_name = getattr(adjacent_target, 'name', 'Cible')
                            except Exception:
                                target_name = 'Cible'
                            if applied and applied > 0:
                                if old_hp is not None and new_hp is not None:
                                    self.log.append(f"[PROPAGATION] {unit.name} - {ability_data['name']} sur {target_name} : {applied} dégâts (HP: {old_hp} → {new_hp})")
                                else:
                                    self.log.append(f"[PROPAGATION] {unit.name} - {ability_data['name']} sur {target_name} : {applied} dégâts")
                        
                        # Appliquer les marques de foudre (Passif d'Alice)
                        self.apply_lightning_mark(unit, adjacent_target)
                else:
                    self.log.append(f"[PROPAGATION] {ability_data['name']} : aucune cible adjacente trouvée")
        
        # Capacités à ciblage unique classique
        else:
            # Appliquer dégâts et effets sur chaque cible individuellement (comportement normal)
        for t in targets:
            # Appliquer les dégâts si c'est une attaque
            if damage > 0:
                old_hp, new_hp, applied = self.apply_damage_with_shield(t, damage, f"{unit.name}")
                try:
                    target_name = getattr(t, 'name', 'Cible')
                except Exception:
                    target_name = 'Cible'
                if applied and applied > 0:
                    if old_hp is not None and new_hp is not None:
                        self.log.append(f"[CAPACITÉ] {unit.name} utilise {ability_data['name']} sur {target_name} : {applied} dégâts (HP: {old_hp} → {new_hp})")
                    else:
                        self.log.append(f"[CAPACITÉ] {unit.name} utilise {ability_data['name']} sur {target_name} : {applied} dégâts")
                
                # Appliquer les marques de foudre (Passif d'Alice)
                self.apply_lightning_mark(unit, t)
            
            # Appliquer les effets
            result = self.effects_manager.apply_ability_effects(ability_id, unit, t, self)
            if result and getattr(result, 'success', False):
                if getattr(result, 'message', None):
                    self.log.append(f"[EFFETS] {result.message}")
                for effect in getattr(result, 'effects_applied', []) or []:
                    self.log.append(f"[EFFET] {effect} appliqué")
                for chain_effect in getattr(result, 'chain_effects', []) or []:
                    self.log.append(f"[CHAÎNE] {chain_effect} déclenché")
        
        # Appliquer le cooldown
        self._apply_ability_cooldown(unit, ability_id, base_cooldown)
        
        return True, f"Capacité {ability_data['name']} utilisée"
    
    def _apply_ability_cooldown(self, unit, ability_id: str, base_cooldown: int):
        """Applique le cooldown à une capacité"""
        # Initialiser le dictionnaire des cooldowns si nécessaire
        if not hasattr(unit, 'ability_cooldowns'):
            unit.ability_cooldowns = {}
        
        # Appliquer le cooldown
        unit.ability_cooldowns[ability_id] = base_cooldown
        self.log.append(f"[COOLDOWN] {unit.name} - {ability_id}: {base_cooldown} tours")
        
        # Mettre à jour aussi le système de cooldowns du moteur
        entity_id = id(unit)
        if entity_id not in self.unit_cooldowns:
            self.unit_cooldowns[entity_id] = [0] * len(unit.abilities)
        
        # Chercher la capacité par ID dans les capacités de l'unité
        for i, ability in enumerate(unit.abilities):
            if hasattr(ability, 'ability_id') and getattr(ability, 'ability_id') == ability_id:
                if i < len(self.unit_cooldowns[entity_id]):
                    self.unit_cooldowns[entity_id][i] = base_cooldown
                    self.log.append(f"[COOLDOWN] Moteur - {unit.name} - Index {i}: cooldown défini à {base_cooldown}")
                break
        
        # CORRECTION : S'assurer que les deux systèmes sont synchronisés
        # Vérifier si l'unité a des capacités avec des objets Ability
        if hasattr(unit, 'abilities') and unit.abilities:
            for ability in unit.abilities:
                if hasattr(ability, 'ability_id') and getattr(ability, 'ability_id') == ability_id:
                    if hasattr(ability, 'current_cooldown'):
                        ability.current_cooldown = base_cooldown
                        self.log.append(f"[COOLDOWN] Objet Ability - {unit.name} - {ability_id}: cooldown défini à {base_cooldown}")
                break
    
    def process_temporary_effects(self, unit):
        """Traite les effets temporaires d'une unité"""
        if not hasattr(unit, 'temporary_effects'):
            return
        
        effects_to_remove = []
        
        for effect in unit.temporary_effects:
            effect_type = effect.get("type", "")
            duration = effect.get("duration", 0)
            
            # Appliquer les dégâts par tour
            if "damage_per_turn" in effect:
                damage = effect["damage_per_turn"]
                if hasattr(unit, 'hp'):
                    unit.hp = max(0, unit.hp - damage)
                    self.log.append(f"[EFFET] {unit.name} subit {damage} dégâts de {effect_type}")
            
            # Réduire la durée
            effect["duration"] -= 1
            
            # Marquer pour suppression si durée expirée
            if effect["duration"] <= 0:
                effects_to_remove.append(effect)
        
        # Supprimer les effets expirés
        for effect in effects_to_remove:
            unit.temporary_effects.remove(effect)
            self.log.append(f"[EFFET] {effect_type} expiré sur {unit.name}")
    
    def apply_elemental_attack_effects(self, element_name: str, source, target):
        """Applique les effets automatiques d'un élément d'attaque"""
        if not self.effects_manager:
            return []
        
        element_id = self.effects_manager.get_element_id(element_name)
        return self.effects_manager.apply_elemental_attack_effects(element_id, source, target, self)
    
    def get_unit_ability_cooldown(self, unit, ability_id: str) -> int:
        """Récupère le cooldown d'une capacité pour une unité"""
        # Vérifier si l'unité a des cooldowns actifs
        if hasattr(unit, 'ability_cooldowns') and ability_id in unit.ability_cooldowns:
            return unit.ability_cooldowns[ability_id]
        
        # Vérifier aussi dans le système de cooldowns du moteur
        entity_id = id(unit)
        if entity_id in self.unit_cooldowns:
            # Chercher la capacité par ID dans les capacités de l'unité
            for i, ability in enumerate(unit.abilities):
                if hasattr(ability, 'ability_id') and getattr(ability, 'ability_id') == ability_id:
                    if i < len(self.unit_cooldowns[entity_id]):
                        return self.unit_cooldowns[entity_id][i]
        
        # Sinon, s'il n'y a pas d'entrée active, le cooldown courant est 0
        return 0
    
    def can_use_ability_by_id(self, unit, ability_id: str) -> bool:
        """Vérifie si une unité peut utiliser une capacité (par ID)"""
        cooldown = self.get_unit_ability_cooldown(unit, ability_id)
        return cooldown <= 0
    
    def reduce_ability_cooldowns(self, unit):
        """Réduit les cooldowns des capacités d'une unité au début du tour"""
        if not hasattr(unit, 'ability_cooldowns'):
            return
        
        cooldowns_to_remove = []
        for ability_id, cooldown in unit.ability_cooldowns.items():
            if cooldown > 0:
                unit.ability_cooldowns[ability_id] = cooldown - 1
                self.log.append(f"[COOLDOWN] {unit.name} - {ability_id}: {cooldown-1} tours restants")
                
                # Supprimer si cooldown terminé
                if cooldown - 1 <= 0:
                    cooldowns_to_remove.append(ability_id)
        
        # Supprimer les cooldowns terminés
        for ability_id in cooldowns_to_remove:
            del unit.ability_cooldowns[ability_id]
            self.log.append(f"[COOLDOWN] {unit.name} - {ability_id}: Prêt à utiliser")
        
        # Mettre à jour aussi le système de cooldowns du moteur
        entity_id = id(unit)
        if entity_id in self.unit_cooldowns:
            for i, cooldown in enumerate(self.unit_cooldowns[entity_id]):
                if cooldown > 0:
                    self.unit_cooldowns[entity_id][i] = cooldown - 1
                    if cooldown - 1 <= 0:
                        self.log.append(f"[COOLDOWN] Moteur - {unit.name} - Index {i}: Prêt à utiliser")
    
    def select_ability_targets(self, ability_data: Dict[str, Any], caster, battlefield) -> List[Any]:
        """
        Sélectionne les cibles pour une capacité selon son type de cible
        
        Args:
            ability_data: Données de la capacité depuis effects_database.json
            caster: Le lanceur de la capacité
            battlefield: Le champ de bataille actuel
        
        Returns:
            Liste des cibles sélectionnées
        """
        if not target_manager:
            self.log.append("[ERREUR] Gestionnaire de cibles non disponible")
            return []
        
        target_type = ability_data.get("target_type", "single_enemy")
        bounce_count = ability_data.get("bounce_count", 0)
        target_priority = ability_data.get("target_priority", "random")
        
        try:
            targets = target_manager.select_targets(
                target_type=target_type,
                caster=caster,
                battlefield=battlefield,
                priority=target_priority,
                bounce_count=bounce_count
            )
            
            self.log.append(f"[CIBLES] {len(targets)} cible(s) sélectionnée(s) pour {ability_data.get('name', 'Capacité')}")
            return targets
            
        except Exception as e:
            self.log.append(f"[ERREUR] Erreur lors de la sélection de cibles: {e}")
            return []
    
    def validate_ability_targets(self, ability_data: Dict[str, Any], selected_targets: List[Any], 
                               caster, battlefield) -> bool:
        """
        Valide la sélection de cibles pour une capacité
        
        Args:
            ability_data: Données de la capacité
            selected_targets: Cibles sélectionnées
            caster: Le lanceur
            battlefield: Le champ de bataille
        
        Returns:
            True si la sélection est valide
        """
        if not target_manager:
            return False
        
        try:
            return target_manager.validate_target_selection(
                ability=ability_data,
                selected_targets=selected_targets,
                caster=caster,
                battlefield=battlefield
            )
        except Exception as e:
            self.log.append(f"[ERREUR] Erreur lors de la validation des cibles: {e}")
            return False
    
    def get_available_targets_for_ability(self, ability_data: Dict[str, Any], caster, battlefield) -> List[Any]:
        """
        Récupère la liste des cibles disponibles pour une capacité
        
        Args:
            ability_data: Données de la capacité
            caster: Le lanceur
            battlefield: Le champ de bataille
        
        Returns:
            Liste des cibles disponibles
        """
        if not target_manager:
            return []
        
        target_type = ability_data.get("target_type", "single_enemy")
        target_conditions = ability_data.get("target_conditions", ["alive"])
        
        try:
            return target_manager.get_valid_targets(
                target_type=target_type,
                caster=caster,
                battlefield=battlefield,
                target_conditions=target_conditions
            )
        except Exception as e:
            self.log.append(f"[ERREUR] Erreur lors de la récupération des cibles: {e}")
            return []
    
    def update_advanced_systems(self):
        """Met à jour tous les systèmes avancés"""
        
        # Mettre à jour les graines
        if seed_system:
            exploding_seeds = seed_system.update_seeds()
            for explosion in exploding_seeds:
                target_id = explosion["target_id"]
                total_damage = explosion["total_damage"]
                
                # Trouver la cible et lui infliger les dégâts
                for unit in self.get_all_units():
                    if id(unit) == target_id:
                        unit.hp = max(0, unit.hp - total_damage)
                        self.log.append(f"[GRAINES] {unit.name} subit {total_damage} dégâts d'explosion de graines")
                        break
        
        # Mettre à jour les pièges
        if trap_system:
            expired_trap = trap_system.update_traps()
            if expired_trap['expired_trap']:
                target_id = expired_trap['target']
                damage = expired_trap['damage']
                
                # Trouver la cible et lui infliger les dégâts
                for unit in self.get_all_units():
                    if id(unit) == target_id:
                        unit.hp = max(0, unit.hp - damage)
                        self.log.append(f"[PIÈGE] {unit.name} subit {damage} dégâts d'explosion de piège")
                        break
        
        # Mettre à jour les capacités avancées
        if advanced_abilities:
            advanced_abilities.update_temporary_passives()
            advanced_abilities.update_temporary_effects()
        
        # Mettre à jour les passifs spécifiques à la Glace
        self.update_ice_passives()
    
    def update_ice_passives(self):
        """Met à jour les passifs spécifiques à la Glace"""
        # Bénédiction Polaire (1319) - Soigne tous les alliés au début du tour
        for unit in self.get_all_units():
            if hasattr(unit, 'passive_ids') and "1319" in unit.passive_ids:
                if self.current_player == getattr(unit, 'owner', None):
                    allies = self.get_allies(unit)
                    for ally in allies:
                        heal_amount = int(ally.hp * 0.05)
                        ally.hp = min(ally.hp + heal_amount, ally.max_hp)
                        self.log.append(f"[BÉNÉDICTION POLAIRE] {ally.name} soigné de {heal_amount} PV")

    def get_all_units(self):
        """Retourne la liste de toutes les unités vivantes des deux joueurs (héros exclus)."""
        units = []
        for player in getattr(self, 'players', []):
            for unit in getattr(player, 'units', [])[:]:
                # Filtrer les unités mortes si stats/hp disponibles
                try:
                    current_hp = None
                    if hasattr(unit, 'stats') and isinstance(unit.stats, dict):
                        current_hp = unit.stats.get('hp')
                    elif hasattr(unit, 'hp'):
                        current_hp = unit.hp
                    if current_hp is None or current_hp > 0:
                        units.append(unit)
                except Exception:
                    units.append(unit)
        return units

    def get_allies(self, entity):
        """Retourne la liste des alliés d'une entité (héros ou unité)."""
        owner = getattr(entity, 'owner', None)
        if owner is None:
            # Déterminer le propriétaire via présence dans les listes
            for player in getattr(self, 'players', []):
                if entity in getattr(player, 'units', []) or entity == getattr(player, 'hero', None):
                    owner = player
                    break
        if owner is None:
            return []
        return list(getattr(owner, 'units', []))

    def get_enemies(self, entity_or_player):
        """Retourne la liste des ennemis (unités) pour une entité ou un joueur donné."""
        if hasattr(entity_or_player, 'opponent'):
            opponent = entity_or_player.opponent
        else:
            # entity
            owner = getattr(entity_or_player, 'owner', None)
            if owner is None:
                # Déterminer propriétaire
                for player in getattr(self, 'players', []):
                    if entity_or_player in getattr(player, 'units', []) or entity_or_player == getattr(player, 'hero', None):
                        owner = player
                        break
            opponent = getattr(owner, 'opponent', None)
        if opponent is None:
            return []
        return list(getattr(opponent, 'units', []))
    
    def apply_ice_damage_reduction(self, unit, damage):
        """Applique la réduction de dégâts pour les passifs Glace"""
        # Fort des Cimes (1318) - Réduit les dégâts si un ennemi est gelé
        if hasattr(unit, 'passive_ids') and "1318" in unit.passive_ids:
            if self.has_frozen_enemy(getattr(unit, 'owner', None)):
                damage = int(damage * 0.8)  # 20% de réduction
                self.log.append(f"[FORT DES CIMES] {unit.name} réduit les dégâts de 20%")
        
        # Protection Boréale (1321) - Réduit les dégâts pour les alliés Glace
        if hasattr(unit, 'passive_ids') and "1321" in unit.passive_ids:
            if getattr(unit, 'element', None) == "Glace":
                damage = int(damage * 0.8)  # 20% de réduction
                self.log.append(f"[PROTECTION BORÉALE] {unit.name} réduit les dégâts de 20%")
        
        return damage
    
    def has_frozen_enemy(self, player):
        """Vérifie si un ennemi est gelé"""
        enemies = self.get_enemies(player)
        for enemy in enemies:
            if hasattr(enemy, 'active_effects') and "freeze" in enemy.active_effects:
                return True
        return False
    
    def apply_dodge_next_attack(self, unit):
        """Applique l'esquive de la prochaine attaque (Intangibilité 1317)"""
        if hasattr(unit, 'passive_ids') and "1317" in unit.passive_ids:
            unit.dodge_next_attack = True
            self.log.append(f"[INTANGIBILITÉ] {unit.name} peut esquiver la prochaine attaque")
    
    def remove_burn_poison_on_ability_use(self, unit):
        """Retire Brûlure et Poison des alliés (Couronne de Givre 1320)"""
        if hasattr(unit, 'passive_ids') and "1320" in unit.passive_ids:
            allies = self.get_allies(unit)
            for ally in allies:
                if hasattr(ally, 'active_effects'):
                    original_effects = ally.active_effects.copy()
                    ally.active_effects = [e for e in ally.active_effects if e not in ["burn", "poison"]]
                    if len(ally.active_effects) < len(original_effects):
                        self.log.append(f"[COURONNE DE GIVRE] {ally.name} débarrassé de Brûlure et Poison")
    
    def execute_advanced_ability(self, ability_data: Dict[str, Any], caster, targets: List[Any]):
        """Exécute une capacité avec des mécaniques avancées"""
        
        ability_id = ability_data.get("id", "")
        damage_type = ability_data.get("damage_type", "fixed")
        
        # Gestion des dégâts de scaling
        if damage_type == "scaling_attack" and advanced_abilities:
            damage = advanced_abilities.get_scaling_damage(caster, ability_id)
            scaling_per_use = ability_data.get("scaling_per_use", False)
            if scaling_per_use:
                advanced_abilities.increment_ability_usage(caster, ability_id)
        
        # Gestion des dégâts de scaling pour soins
        elif damage_type == "scaling_heal" and advanced_abilities:
            heal_amount = advanced_abilities.get_scaling_heal(caster, ability_id)
            for target in targets:
                if hasattr(target, 'hp') and hasattr(target, 'max_hp'):
                    target.hp = min(target.max_hp, target.hp + heal_amount)
                    self.log.append(f"[SOIN] {target.name} soigné de {heal_amount} PV")
        
        # Gestion des attaques multiples
        elif damage_type == "multi_attack":
            attack_count = ability_data.get("attack_count", 2)
            damage_per_attack = ability_data.get("damage", 1.0)
            
            for target in targets:
                for i in range(attack_count):
                    damage = int(caster.attack * damage_per_attack)
                    target.hp = max(0, target.hp - damage)
                    self.log.append(f"[MULTI-ATTAQUE] {caster.name} attaque {target.name} ({i+1}/{attack_count}): {damage} dégâts")
        
        # Gestion des chaînes aléatoires
        elif ability_data.get("target_type") == "chain_random" and advanced_abilities:
            chain_chance = ability_data.get("chain_chance", 25)
            max_bounces = ability_data.get("max_bounces", 3)
            
            chain_targets = advanced_abilities.chain_random_targets(
                initial_targets=targets,
                chain_chance=chain_chance,
                max_bounces=max_bounces,
                battlefield=self
            )
            
            for target in chain_targets:
                damage = self.calculate_ability_damage(ability_data, caster)
                target.hp = max(0, target.hp - damage)
                self.log.append(f"[CHAÎNE] {caster.name} touche {target.name}: {damage} dégâts")
        
        # Gestion des cibles multiples aléatoires
        elif ability_data.get("target_type") == "random_multiple":
            target_count = ability_data.get("target_count", 2)
            same_target_allowed = ability_data.get("same_target_allowed", False)
            
            random_targets = self.get_random_multiple_targets(targets, target_count, same_target_allowed)
            
            for target in random_targets:
                damage = self.calculate_ability_damage(ability_data, caster)
                target.hp = max(0, target.hp - damage)
                self.log.append(f"[ALÉATOIRE] {caster.name} touche {target.name}: {damage} dégâts")
        
        # Gestion des dégâts de splash
        elif "splash_damage" in ability_data:
            splash_damage = ability_data.get("splash_damage", 0.5)
            splash_targets = ability_data.get("splash_targets", "adjacent_enemies")
            
            for target in targets:
                # Dégâts principaux
                main_damage = self.calculate_ability_damage(ability_data, caster)
                target.hp = max(0, target.hp - main_damage)
                self.log.append(f"[ATTAQUE] {caster.name} attaque {target.name}: {main_damage} dégâts")
                
                # Dégâts de splash
                splash_targets_list = self.get_adjacent_enemies(target)
                for splash_target in splash_targets_list:
                    splash_damage_amount = int(main_damage * splash_damage)
                    splash_target.hp = max(0, splash_target.hp - splash_damage_amount)
                    self.log.append(f"[SPLASH] {splash_target.name} subit {splash_damage_amount} dégâts de splash")
        
        # Gestion des passifs temporaires
        elif "grant_passive" in ability_data:
            passive_id = ability_data.get("grant_passive")
            passive_duration = ability_data.get("passive_duration", 1)
            
            if advanced_abilities:
                for target in targets:
                    advanced_abilities.add_temporary_passive(target, passive_id, passive_duration)
                    self.log.append(f"[PASSIF] {target.name} reçoit le passif {passive_id} pour {passive_duration} tour(s)")
        
        # Gestion des boosts permanents
        elif "attack_boost" in ability_data and ability_data.get("permanent", False):
            boost_amount = ability_data.get("attack_boost", 0.1)
            caster.attack = int(caster.attack * (1 + boost_amount))
            self.log.append(f"[BOOST] {caster.name} gagne +{int(boost_amount * 100)}% d'attaque permanent")
        
        # Gestion des capacités de Murkax (Ténèbres)
        elif ability_id == "6751":  # Griffes de l'Abîme
            for target in targets:
                damage = self.calculate_ability_damage(ability_data, caster)
                target.hp = max(0, target.hp - damage)
                self.log.append(f"[GRIFFES DE L'ABÎME] {caster.name} attaque {target.name}: {damage} dégâts")
                
                # 25% de chance d'appliquer la cécité
                if random.random() < 0.25:
                    self.apply_blind_effect(target)
        
        elif ability_id == "6752":  # Voile d'Éclipsombre
            for target in targets:
                damage = self.calculate_ability_damage(ability_data, caster)
                target.hp = max(0, target.hp - damage)
                self.log.append(f"[VOILE D'ÉCLIPSSOMBRE] {caster.name} attaque {target.name}: {damage} dégâts")
                
                # 30% de chance de réduire la défense
                if random.random() < 0.30:
                    if not hasattr(target, 'temporary_effects'):
                        target.temporary_effects = []
                    
                    defense_reduction = int(target.defense * 0.25)
                    target.temporary_effects.append({
                        "type": "defense_reduction",
                        "duration": 2,
                        "value": defense_reduction
                    })
                    self.log.append(f"[VOILE D'ÉCLIPSSOMBRE] {target.name} perd {defense_reduction} DEF pour 2 tours")
        
        # Gestion des contre-effets
        elif "counter_burn" in ability_data:
            # Logique pour les contre-effets de brûlure
            pass
        
        # Gestion des chances d'étourdissement
        elif "stun_chance" in ability_data:
            stun_chance = ability_data.get("stun_chance", 0)
            for target in targets:
                if random.randint(1, 100) <= stun_chance:
                    if advanced_abilities:
                        advanced_abilities.add_temporary_effect(target, "stunned", 1)
                        self.log.append(f"[ÉTOURDI] {target.name} est étourdi")
        
        # Gestion du lifesteal
        elif "lifesteal_percent" in ability_data:
            lifesteal_percent = ability_data.get("lifesteal_percent", 0.5)
            total_damage = 0
            
            for target in targets:
                damage = self.calculate_ability_damage(ability_data, caster)
                target.hp = max(0, target.hp - damage)
                total_damage += damage
                self.log.append(f"[ATTAQUE] {caster.name} attaque {target.name}: {damage} dégâts")
            
            # Soigner le lanceur
            heal_amount = int(total_damage * lifesteal_percent)
            if hasattr(caster, 'hp') and hasattr(caster, 'max_hp'):
                caster.hp = min(caster.max_hp, caster.hp + heal_amount)
                self.log.append(f"[LIFESTEAL] {caster.name} se soigne de {heal_amount} PV")
        
        # Gestion des effets temporaires (dodge, defense, silence)
        elif any(key in ability_data for key in ["dodge_boost", "defense_boost", "silence_duration"]):
            self.apply_advanced_effects(ability_data, caster, targets)
        
        # === NOUVELLES MÉCANIQUES AIR ===
        
        # Gestion des boosts de critique
        elif "crit_boost" in ability_data:
            crit_boost = ability_data.get("crit_boost", 0.2)
            crit_duration = ability_data.get("crit_duration", 1)
            
            if advanced_abilities:
                for target in targets:
                    advanced_abilities.add_temporary_effect(target, "crit_boost", crit_duration, crit_boost)
                    self.log.append(f"[CRITIQUE] {target.name} gagne +{int(crit_boost * 100)}% de chances de critique pour {crit_duration} tour(s)")
        
        # Gestion des boosts de multiplicateur de critique
        elif "crit_multiplier_boost" in ability_data:
            crit_multiplier_boost = ability_data.get("crit_multiplier_boost", 0.5)
            if hasattr(caster, 'crit_multiplier'):
                caster.crit_multiplier += crit_multiplier_boost
                self.log.append(f"[CRITIQUE] {caster.name} gagne +{int(crit_multiplier_boost * 100)}% de multiplicateur de critique")
        
        # Gestion de la réinitialisation des cooldowns
        elif "reset_all_cooldowns" in ability_data:
            for target in targets:
                if hasattr(target, 'cooldowns'):
                    for ability_id in target.cooldowns:
                        target.cooldowns[ability_id] = 0
                    self.log.append(f"[COOLDOWN] {target.name} a tous ses cooldowns réinitialisés")
        
        # Gestion des dégâts par tour
        elif "damage_per_turn" in ability_data:
            damage_per_turn = ability_data.get("damage_per_turn", 10)
            damage_duration = ability_data.get("damage_duration", 3)
            
            if advanced_abilities:
                for target in targets:
                    advanced_abilities.add_temporary_effect(target, "damage_per_turn", damage_duration, damage_per_turn)
                    self.log.append(f"[DÉGÂTS/TOUR] {target.name} subira {damage_per_turn} dégâts par tour pendant {damage_duration} tours")
        
        # Gestion des debuffs aléatoires
        elif "random_debuff" in ability_data:
            debuff_options = ability_data.get("random_debuff", ["corruption"])
            chosen_debuff = random.choice(debuff_options)
            
            if advanced_abilities:
                for target in targets:
                    advanced_abilities.add_temporary_effect(target, chosen_debuff, 1)
                    self.log.append(f"[DEBUFF] {target.name} reçoit l'effet {chosen_debuff}")
        
        # Gestion de la réduction de dégâts
        elif "damage_reduction" in ability_data:
            damage_reduction = ability_data.get("damage_reduction", 0.2)
            damage_reduction_duration = ability_data.get("damage_reduction_duration", 1)
            
            if advanced_abilities:
                for target in targets:
                    advanced_abilities.add_temporary_effect(target, "damage_reduction", damage_reduction_duration, damage_reduction)
                    self.log.append(f"[RÉDUCTION] {target.name} réduit les dégâts reçus de {int(damage_reduction * 100)}% pour {damage_reduction_duration} tour(s)")
        
        # Gestion des dégâts de critique boostés
        elif "crit_damage_boost" in ability_data:
            crit_damage_boost = ability_data.get("crit_damage_boost", 0.2)
            if hasattr(caster, 'crit_damage_multiplier'):
                caster.crit_damage_multiplier += crit_damage_boost
                self.log.append(f"[CRITIQUE] {caster.name} gagne +{int(crit_damage_boost * 100)}% de dégâts critiques")
        
        # Gestion de l'esquive maximale
        elif "max_dodge" in ability_data:
            max_dodge_duration = ability_data.get("dodge_duration", 1)
            if advanced_abilities:
                for target in targets:
                    advanced_abilities.add_temporary_effect(target, "max_dodge", max_dodge_duration)
                    self.log.append(f"[ESQUIVE] {target.name} a une esquive maximale pour {max_dodge_duration} tour(s)")
        
        # Gestion de la réduction de précision permanente
        elif "precision_reduction" in ability_data and ability_data.get("permanent", False):
            precision_reduction = ability_data.get("precision_reduction", 3)
            for target in targets:
                if hasattr(target, 'precision_pct'):
                    target.precision_pct = max(1, target.precision_pct - precision_reduction)
                    self.log.append(f"[PRÉCISION] {target.name} perd {precision_reduction}% de précision de façon permanente")
        
        # Gestion des critiques maximaux
        elif "max_crit" in ability_data:
            if advanced_abilities:
                for target in targets:
                    advanced_abilities.add_temporary_effect(target, "max_crit", 1)
                    self.log.append(f"[CRITIQUE] {target.name} a 100% de chances de critique")
        
        # Gestion des chances de gel
        elif "freeze_chance" in ability_data:
            freeze_chance = ability_data.get("freeze_chance", 20)
            for target in targets:
                if random.randint(1, 100) <= freeze_chance:
                    if advanced_abilities:
                        advanced_abilities.add_temporary_effect(target, "freeze", 1)
                        self.log.append(f"[GEL] {target.name} est gelé")
        
        # Gestion des bonus de cibles par critique
        elif "crit_bonus_targets" in ability_data:
            max_bonus_targets = ability_data.get("max_bonus_targets", 10)
            # Cette logique sera gérée dans le système de combat principal
            self.log.append(f"[MÉTÉORES] {caster.name} lance une pluie de météores avec bonus de cibles par critique")
        
        # Gestion de toutes les auras
        elif "grant_all_auras" in ability_data:
            aura_duration = ability_data.get("aura_duration", 2)
            if advanced_abilities:
                for target in targets:
                    # Accorder toutes les auras élémentaires (1100-1111)
                    for aura_id in range(1100, 1112):
                        advanced_abilities.add_temporary_passive(target, str(aura_id), aura_duration)
                    self.log.append(f"[AURAS] {target.name} reçoit toutes les auras élémentaires pour {aura_duration} tour(s)")
        
        # Gestion des conditions spéciales
        elif "condition" in ability_data:
            condition = ability_data.get("condition", "")
            if "cards_played_this_turn >= 3" in condition:
                # Vérifier si 3+ cartes ont été jouées ce tour
                cards_played = getattr(caster, 'cards_played_this_turn', 0)
                if cards_played >= 3:
                    # Appliquer le bonus de dégâts
                    damage_boost = ability_data.get("value", 0.5)
                    if hasattr(caster, 'attack'):
                        caster.attack = int(caster.attack * (1 + damage_boost))
                    self.log.append(f"[CONDITION] {caster.name} a joué {cards_played} cartes, bonus de dégâts +{int(damage_boost * 100)}% appliqué")
                else:
                    self.log.append(f"[CONDITION] {caster.name} n'a joué que {cards_played} cartes, condition non remplie")
        
        # Gestion des pièges
        elif "plant_trap" in ability_data and ability_data.get("plant_trap", False):
            if trap_system:
                for target in targets:
                    trap_data = {
                        'trap_damage': ability_data.get('trap_damage', 10),
                        'trap_duration': ability_data.get('trap_duration', 3),
                        'trap_targets_attacker': ability_data.get('trap_targets_attacker', True),
                        'damage': ability_data.get('damage', 0),
                        'planted_by': caster.name
                    }
                    trap_system.plant_trap(id(target), trap_data)
                    self.log.append(f"[PIÈGE] {caster.name} pose un piège sur {target.name} (dégâts: {trap_data['trap_damage']}, durée: {trap_data['trap_duration']} tours)")
            else:
                self.log.append(f"[ERREUR] Système de pièges non disponible pour {caster.name}")
        
        # === NOUVELLES MÉCANIQUES ALICE (FOUDRE) ===
        
        # Gestion des compteurs d'utilisation (Coupe Foudre)
        elif "use_counter" in ability_data and ability_data.get("use_counter", False):
            counter_threshold = ability_data.get("counter_threshold", 3)
            
            # Initialiser le compteur si nécessaire
            if not hasattr(caster, 'ability_usage_counters'):
                caster.ability_usage_counters = {}
            
            ability_id = ability_data.get("id", "")
            if ability_id not in caster.ability_usage_counters:
                caster.ability_usage_counters[ability_id] = 0
            
            # Incrémenter le compteur
            caster.ability_usage_counters[ability_id] += 1
            current_count = caster.ability_usage_counters[ability_id]
            
            self.log.append(f"[COMPTEUR] {caster.name} utilise {ability_data.get('name', 'capacité')} ({current_count}/{counter_threshold})")
            
            # Vérifier si le seuil est atteint
            if current_count >= counter_threshold:
                # Capacité renforcée
                enhanced_damage = ability_data.get("enhanced_damage", 0)
                enhanced_target_type = ability_data.get("enhanced_target_type", "single_enemy")
                
                # Réinitialiser le compteur
                caster.ability_usage_counters[ability_id] = 0
                
                # Appliquer les dégâts renforcés
                if enhanced_target_type == "adjacent_enemies":
                    # Cibler la cible principale et les adjacentes
                    all_targets = [targets[0]] + self.get_adjacent_enemies(targets[0])
                    for target in all_targets:
                        target.hp = max(0, target.hp - enhanced_damage)
                        self.log.append(f"[COUPE FOUDRE ENHANCED] {caster.name} attaque {target.name}: {enhanced_damage} dégâts")
                else:
                    # Cibler seulement la cible principale
                    for target in targets:
                        target.hp = max(0, target.hp - enhanced_damage)
                        self.log.append(f"[COUPE FOUDRE ENHANCED] {caster.name} attaque {target.name}: {enhanced_damage} dégâts")
            else:
                # Capacité normale
                for target in targets:
                    damage = self.calculate_ability_damage(ability_data, caster)
                    target.hp = max(0, target.hp - damage)
                    self.log.append(f"[COUPE FOUDRE] {caster.name} attaque {target.name}: {damage} dégâts")
        
        # Gestion des boosts de précision (Foudre Éclair)
        elif "precision_boost" in ability_data:
            precision_boost = ability_data.get("precision_boost", 10)
            if hasattr(caster, 'precision_pct'):
                caster.precision_pct = min(100, caster.precision_pct + precision_boost)
                self.log.append(f"[PRÉCISION] {caster.name} gagne +{precision_boost}% de précision pour cette attaque")
    
    def apply_advanced_effects(self, ability_data: Dict[str, Any], caster, targets: List[Any]):
        """Applique les effets avancés d'une capacité"""
        
        if not advanced_abilities:
            return
        
        # Effets de dodge
        if "dodge_boost" in ability_data:
            dodge_boost = ability_data.get("dodge_boost", 0.2)
            dodge_duration = ability_data.get("dodge_duration", 2)
            
            for target in targets:
                advanced_abilities.add_temporary_effect(target, "dodge_boost", dodge_duration, dodge_boost)
                self.log.append(f"[DODGE] {target.name} gagne +{int(dodge_boost * 100)}% d'esquive pour {dodge_duration} tour(s)")
        
        # Effets de défense
        elif "defense_boost" in ability_data:
            defense_boost = ability_data.get("defense_boost", 10)
            defense_duration = ability_data.get("defense_duration", 2)
            
            for target in targets:
                advanced_abilities.add_temporary_effect(target, "defense_boost", defense_duration, defense_boost)
                self.log.append(f"[DÉFENSE] {target.name} gagne +{defense_boost} défense pour {defense_duration} tour(s)")
        
        # Effets de silence
        elif "silence_duration" in ability_data:
            silence_duration = ability_data.get("silence_duration", 1)
            
            for target in targets:
                advanced_abilities.add_temporary_effect(target, "silence", silence_duration)
                self.log.append(f"[SILENCE] {target.name} est silencé pour {silence_duration} tour(s)")
    
    def get_random_multiple_targets(self, available_targets: List[Any], target_count: int, same_target_allowed: bool) -> List[Any]:
        """Sélectionne plusieurs cibles aléatoires"""
        if not available_targets:
            return []
        
        if same_target_allowed:
            return random.choices(available_targets, k=target_count)
        else:
            return random.sample(available_targets, min(target_count, len(available_targets)))
    
    def get_adjacent_enemies(self, target) -> List[Any]:
        """Retourne les ennemis adjacents à une cible (simplifié pour l'instant)"""
        # Logique simplifiée : retourner tous les ennemis
        enemies = []
        for unit in self.get_all_units():
            if hasattr(unit, 'team') and unit.team != target.team:
                enemies.append(unit)
        return enemies
    
    def calculate_ability_damage(self, ability_data: Dict[str, Any], caster) -> int:
        """Calcule les dégâts d'une capacité"""
        damage_type = ability_data.get("damage_type", "fixed")
        base_damage = ability_data.get("damage", 0)
        
        if damage_type == "fixed":
            return base_damage
        elif damage_type == "attack":
            return int(caster.attack * base_damage)
        elif damage_type == "attack_plus":
            return int(caster.attack + base_damage)
        elif damage_type == "attack_multiplier":
            return int(caster.attack * base_damage)
        elif damage_type == "hp_percent":
            # Pour les cibles, on utilise une valeur par défaut
            target_max_hp = 1000  # Valeur par défaut
            return int(target_max_hp * base_damage)
        
        return base_damage
    
    def apply_damage_with_ice_reduction(self, target, damage):
        """Applique les dégâts avec les réductions de passifs Glace"""
        # Appliquer les réductions de dégâts Glace
        final_damage = self.apply_ice_damage_reduction(target, damage)
        
        # Appliquer les dégâts
        target.hp = max(0, target.hp - final_damage)
        
        return final_damage
    
    def update_foudre_passives(self):
        """Met à jour les passifs spécifiques à la Foudre"""
        # Survolteur (1324) - Augmente l'ATK quand il applique surcharge
        for unit in self.get_all_units():
            if hasattr(unit, 'passive_ids') and "1324" in unit.passive_ids:
                # Cette logique sera gérée lors de l'application de surcharge
                pass
        
        # Marque de l'Éclair (1337) - Alice
        for unit in self.get_all_units():
            if hasattr(unit, 'passive_ids') and "1337" in unit.passive_ids:
                # Cette logique sera gérée lors des attaques
                pass
    
    def apply_lightning_reflect(self, attacker, target, damage):
        """Applique la réflexion de dégâts Foudre (Conducteur 1322)"""
        if hasattr(target, 'passive_ids') and "1322" in target.passive_ids:
            # Vérifier si l'attaque est de type Foudre
            if hasattr(attacker, 'element') and attacker.element == "Foudre":
                reflected_damage = int(damage * 0.5)  # 50% des dégâts
                attacker.hp = max(0, attacker.hp - reflected_damage)
                self.log.append(f"[CONDUCTEUR] {target.name} renvoie {reflected_damage} dégâts à {attacker.name}")
    
    def apply_status_immunity(self, unit, effect_type):
        """Applique l'immunité aux effets de statut (Cœur Conducteur 1323)"""
        if hasattr(unit, 'passive_ids') and "1323" in unit.passive_ids:
            immunity_chance = 0.4  # 40% de chance
            if random.random() < immunity_chance:
                self.log.append(f"[CŒUR CONDUCTEUR] {unit.name} ignore l'effet {effect_type}")
                return True
        return False
    
    def apply_overload_attack_boost(self, unit):
        """Applique le boost d'attaque permanent (Survolteur 1324)"""
        if hasattr(unit, 'passive_ids') and "1324" in unit.passive_ids:
            boost_amount = 0.1  # +10% ATK
            if not hasattr(unit, 'overload_attack_boosts'):
                unit.overload_attack_boosts = 0
            unit.overload_attack_boosts += 1
            unit.attack = int(unit.base_attack * (1 + unit.overload_attack_boosts * boost_amount))
            self.log.append(f"[SURVOLTEUR] {unit.name} gagne +{int(boost_amount * 100)}% ATK permanent (total: +{int(unit.overload_attack_boosts * boost_amount * 100)}%)")
    
    def apply_electrified_effect(self, target, chance):
        """Applique l'effet Éléctrifié avec une chance donnée"""
        if random.randint(1, 100) <= chance:
            if not hasattr(target, 'active_effects'):
                target.active_effects = []
            target.active_effects.append("electrified")
            self.log.append(f"[ÉLECTRIFIÉ] {target.name} est électrifié (+20% dégâts Foudre pendant 2 tours)")
    
    def apply_lightning_vulnerability(self, target, damage):
        """Applique la vulnérabilité aux dégâts Foudre"""
        if hasattr(target, 'active_effects') and "electrified" in target.active_effects:
            bonus_damage = int(damage * 0.2)  # +20% dégâts Foudre
            return damage + bonus_damage
        return damage
    
    def update_lumiere_passives(self):
        """Met à jour les passifs spécifiques à la Lumière"""
        # Bénédiction Chatoyante (1326) - Soigne les alliés quand Lumicorne est purifiée
        for unit in self.get_all_units():
            if hasattr(unit, 'passive_ids') and "1326" in unit.passive_ids:
                # Cette logique sera gérée lors de la purification
                pass
    
    def apply_radiant_wall(self, unit, effect_type):
        """Applique l'immunité au premier effet négatif (Mur Radieux 1325)"""
        if hasattr(unit, 'passive_ids') and "1325" in unit.passive_ids:
            if not hasattr(unit, 'radiant_wall_used'):
                unit.radiant_wall_used = False
            
            if not unit.radiant_wall_used:
                unit.radiant_wall_used = True
                # Appliquer le boost de défense
                if not hasattr(unit, 'temporary_effects'):
                    unit.temporary_effects = []
                unit.temporary_effects.append({
                    "type": "defense_boost",
                    "duration": 2,
                    "value": int(unit.defense * 0.2)
                })
                self.log.append(f"[MUR RADIEUX] {unit.name} annule l'effet {effect_type} et gagne +20% DEF pour 2 tours")
                return True
        return False
    
    def apply_chatoyant_blessing(self, unit):
        """Applique le soin des alliés (Bénédiction Chatoyante 1326)"""
        if hasattr(unit, 'passive_ids') and "1326" in unit.passive_ids:
            allies = self.get_allies(unit)
            for ally in allies:
                ally.hp = min(ally.hp + 20, ally.max_hp)
            self.log.append(f"[BÉNÉDICTION CHATOYANTE] Tous les alliés soignés de 20 HP")
    
    def apply_renaissance_light(self, unit):
        """Prépare la renaissance (Lueur de Renaissance 1327)"""
        if hasattr(unit, 'passive_ids') and "1327" in unit.passive_ids:
            if not hasattr(unit, 'renaissance_used'):
                unit.renaissance_used = False
            
            if not unit.renaissance_used and unit.hp <= 0:
                unit.renaissance_used = True
                unit.revive_next_turn = True
                unit.revive_hp = 1
                self.log.append(f"[LUEUR DE RENAISSANCE] {unit.name} se prépare à renaître au prochain tour")
    
    def process_renaissance_revive(self):
        """Traite les renaissances au début du tour"""
        for unit in self.get_all_units():
            if hasattr(unit, 'revive_next_turn') and unit.revive_next_turn:
                unit.hp = unit.revive_hp
                unit.revive_next_turn = False
                # Supprimer tous les effets temporaires
                if hasattr(unit, 'temporary_effects'):
                    unit.temporary_effects = []
                if hasattr(unit, 'active_effects'):
                    unit.active_effects = []
                self.log.append(f"[RENAISSANCE] {unit.name} renaît avec {unit.hp} HP")
    
    def apply_vital_radiance(self, unit):
        """Applique le boost d'attaque et soin (Rayonnement Vital 1328)"""
        if hasattr(unit, 'passive_ids') and "1328" in unit.passive_ids:
            # Boost d'attaque permanent
            if not hasattr(unit, 'vital_radiance_boosts'):
                unit.vital_radiance_boosts = 0
            unit.vital_radiance_boosts += 1
            boost_amount = 0.08  # +8% ATK
            unit.attack = int(unit.base_attack * (1 + unit.vital_radiance_boosts * boost_amount))
            
            # Soin
            unit.hp = min(unit.hp + 25, unit.max_hp)
            
            self.log.append(f"[RAYONNEMENT VITAL] {unit.name} gagne +{int(boost_amount * 100)}% ATK permanent (total: +{int(unit.vital_radiance_boosts * boost_amount * 100)}%) et se soigne de 25 HP")
    
    def apply_halo_espoir(self, target):
        """Applique l'immunité à la prochaine altération (Halo Espoir)"""
        if not hasattr(target, 'temporary_effects'):
            target.temporary_effects = []
        
        # Vérifier si une immunité existe déjà (non cumulable)
        for effect in target.temporary_effects:
            if effect.get("type") == "immunity_next_status":
                return  # Déjà immunisé
        
        target.temporary_effects.append({
            "type": "immunity_next_status",
            "duration": 999,  # Jusqu'à la prochaine altération
            "description": "Immunité à la prochaine altération de statut"
        })
        self.log.append(f"[HALO ESPOIR] {target.name} est protégé de la prochaine altération de statut")
    
    def apply_danse_iridescente(self, targets):
        """Applique le soin et la purification complète (Danse Iridescente)"""
        for target in targets:
            # Soin
            target.hp = min(target.hp + 45, target.max_hp)
            
            # Purification complète de tous les effets négatifs
            if hasattr(target, 'temporary_effects'):
                original_count = len(target.temporary_effects)
                target.temporary_effects = [eff for eff in target.temporary_effects 
                                          if eff.get("type") not in ["burn", "poison", "freeze", "wet", "corruption", "fragile", "stunned", "overload"]]
                if len(target.temporary_effects) < original_count:
                    self.log.append(f"[DANSE IRIDESCENTE] {target.name} est purifié de tous ses effets négatifs")
            
            if hasattr(target, 'active_effects'):
                original_count = len(target.active_effects)
                target.active_effects = [eff for eff in target.active_effects 
                                       if eff not in ["burn", "poison", "freeze", "wet", "corruption", "fragile", "stunned", "overload"]]
                if len(target.active_effects) < original_count:
                    self.log.append(f"[DANSE IRIDESCENTE] {target.name} est purifié de tous ses effets actifs négatifs")
    
    def update_poison_passives(self):
        """Met à jour les passifs spécifiques au Poison"""
        # Brume Persistante (1329) - Prolonge la durée des poisons infligés
        # Couverture Moussue (1330) - Réduit les dégâts subis par ennemi empoisonné
        # Venimeux (1331) - Empoisonne l'attaquant
        # Explo-Nez (1332) - Empoisonne tous les ennemis à la mort
        # Communion Fongique (1333) - Réduit la DEF lors d'application de poison
        # Flétrissure Irréversible (1334) - Augmente les dégâts poison par stack
        pass
    
    def apply_brume_persistante(self, unit, poison_effect):
        """Prolonge la durée des poisons infligés (Brume Persistante 1329)"""
        if hasattr(unit, 'passive_ids') and "1329" in unit.passive_ids:
            poison_effect["duration"] += 1
            self.log.append(f"[BRUME PERSISTANTE] {unit.name} prolonge la durée du poison de 1 tour")
    
    def apply_couverture_moussue(self, unit):
        """Calcule la réduction de dégâts (Couverture Moussue 1330)"""
        if hasattr(unit, 'passive_ids') and "1330" in unit.passive_ids:
            poisoned_enemies = 0
            for enemy in self.get_enemies(unit):
                if hasattr(enemy, 'active_effects') and "poison" in enemy.active_effects:
                    poisoned_enemies += 1
            
            if poisoned_enemies > 0:
                reduction = poisoned_enemies * 0.05  # 5% par ennemi empoisonné
                return 1 - reduction  # Multiplicateur de dégâts
        return 1.0
    
    def apply_venimeux(self, unit, attacker):
        """Empoisonne l'attaquant (Venimeux 1331)"""
        if hasattr(unit, 'passive_ids') and "1331" in unit.passive_ids:
            if not hasattr(attacker, 'active_effects'):
                attacker.active_effects = []
            
            attacker.active_effects.append("poison")
            self.log.append(f"[VENIMEUX] {attacker.name} est empoisonné par {unit.name}")
    
    def apply_explo_nez(self, unit):
        """Empoisonne tous les ennemis à la mort (Explo-Nez 1332)"""
        if hasattr(unit, 'passive_ids') and "1332" in unit.passive_ids:
            enemies = self.get_enemies(unit)
            for enemy in enemies:
                if not hasattr(enemy, 'active_effects'):
                    enemy.active_effects = []
                enemy.active_effects.append("poison")
            self.log.append(f"[EXPLO-NEZ] {unit.name} empoisonne tous les ennemis à sa mort")
    
    def apply_communion_fongique(self, unit, target):
        """Applique la réduction de DEF (Communion Fongique 1333)"""
        if hasattr(unit, 'passive_ids') and "1333" in unit.passive_ids:
            if random.random() < 0.4:  # 40% de chance
                if not hasattr(target, 'temporary_effects'):
                    target.temporary_effects = []
                
                target.temporary_effects.append({
                    "type": "defense_reduction",
                    "duration": 2,
                    "value": int(target.defense * 0.2)
                })
                self.log.append(f"[COMMUNION FONGIQUE] {target.name} perd 20% DEF pour 2 tours")
    
    def apply_fletrissure_irreversible(self, unit, target, poison_stacks):
        """Calcule les dégâts poison augmentés (Flétrissure Irréversible 1334)"""
        if hasattr(unit, 'passive_ids') and "1334" in unit.passive_ids:
            # Compter les stacks de poison que cette unité a contribué
            if not hasattr(unit, 'poison_stacks_contributed'):
                unit.poison_stacks_contributed = {}
            
            if target.name not in unit.poison_stacks_contributed:
                unit.poison_stacks_contributed[target.name] = 0
            
            unit.poison_stacks_contributed[target.name] += 1
            stacks = unit.poison_stacks_contributed[target.name]
            
            # Augmenter les dégâts poison de 1% PV max par stack
            bonus_damage = int(target.max_hp * 0.01 * stacks)
            return bonus_damage
        return 0
    
    def apply_beurk_effect(self, target):
        """Applique l'effet Beurk (augmente les dégâts poison subis)"""
        if not hasattr(target, 'temporary_effects'):
            target.temporary_effects = []
        
        target.temporary_effects.append({
            "type": "poison_vulnerability",
            "duration": 1,
            "value": 0.1  # +10% dégâts poison
        })
        self.log.append(f"[BEURK] {target.name} subit +10% dégâts poison pendant 1 tour")
    
    def apply_enhanced_poison(self, target):
        """Applique un poison avec valeur 3 (Toxine Mortelle)"""
        if not hasattr(target, 'active_effects'):
            target.active_effects = []
        
        target.active_effects.append({
            "type": "poison",
            "value": 3,
            "duration": 1
        })
        self.log.append(f"[TOXINE MORTELLE] {target.name} subit un poison renforcé (valeur 3)")
    
    def apply_ombre_devorante(self, unit, killed_enemy):
        """Applique le bonus de dégâts Ténèbres (Ombre Dévorante 1335)"""
        if hasattr(unit, 'passive_ids') and "1335" in unit.passive_ids:
            if not hasattr(unit, 'temporary_effects'):
                unit.temporary_effects = []
            
            # Ajouter un bonus de dégâts Ténèbres de 15% pour 3 tours
            unit.temporary_effects.append({
                "type": "darkness_damage_boost",
                "duration": 3,
                "value": 0.15  # +15% dégâts Ténèbres
            })
            self.log.append(f"[OMBRE DÉVORANTE] {unit.name} gagne +15% dégâts Ténèbres pour 3 tours")
    
    def apply_blind_effect(self, target):
        """Applique l'effet de cécité (précision -25%)"""
        if not hasattr(target, 'temporary_effects'):
            target.temporary_effects = []
        
        target.temporary_effects.append({
            "type": "precision_reduction",
            "duration": 1,
            "value": 25  # -25% précision
        })
        self.log.append(f"[CÉCITÉ] {target.name} perd 25% de précision pendant 1 tour")

    # ========================================
    # MÉTHODES DE PHASES DE COMBAT MANQUANTES
    # ========================================

    def execute_draw_phase(self, player):
        """Exécute la phase de pioche pour un joueur"""
        self.log.append(f"[PHASE PIOCHE] Début de la phase de pioche pour {player.name}")
        
        # Piocher une carte
        if len(player.deck) > 0:
            drawn_card = player.deck.pop(0)
            player.hand.append(drawn_card)
            self.log.append(f"[PIOCHE] {player.name} pioche {drawn_card.name}")
        else:
            self.log.append(f"[PIOCHE] {player.name} ne peut plus piocher (deck vide)")
        
        # Vérifier la limite de cartes en main (max 10)
        if len(player.hand) > 10:
            discarded = player.hand.pop()
            self.log.append(f"[LIMITE MAIN] {player.name} défausse {discarded.name} (limite de 10 cartes)")
        
        self.log.append(f"[PHASE PIOCHE] Fin de la phase de pioche pour {player.name}")

    def execute_mana_phase(self, player):
        """Exécute la phase de mana pour un joueur"""
        self.log.append(f"[PHASE MANA] Début de la phase de mana pour {player.name}")
        
        # Augmenter le mana maximum
        player.max_mana = min(player.max_mana + 1, 10)
        
        # Restaurer le mana actuel
        player.mana = player.max_mana
        
        self.log.append(f"[MANA] {player.name} a maintenant {player.mana}/{player.max_mana} mana")
        self.log.append(f"[PHASE MANA] Fin de la phase de mana pour {player.name}")

    def execute_combat_phase(self, player):
        """Exécute la phase de combat pour un joueur"""
        self.log.append(f"[PHASE COMBAT] Début de la phase de combat pour {player.name}")
        
        # Ici on pourrait ajouter la logique de combat automatique
        # Pour l'instant, on laisse le joueur faire ses actions manuellement
        self.log.append(f"[PHASE COMBAT] Phase de combat en attente d'actions pour {player.name}")

    def execute_end_phase(self, player):
        """Exécute la phase de fin de tour pour un joueur"""
        self.log.append(f"[PHASE FIN] Début de la phase de fin de tour pour {player.name}")
        
        # Mettre à jour les systèmes avancés
        self.update_advanced_systems()
        
        # Nettoyer les unités mortes
        self.cleanup_dead_units()
        
        # Mettre à jour les cooldowns
        self.update_cooldowns(player)
        
        self.log.append(f"[PHASE FIN] Fin de la phase de fin de tour pour {player.name}")

    def execute_complete_turn(self, player):
        """Exécute un tour complet pour un joueur"""
        self.log.append(f"[TOUR COMPLET] Début du tour complet pour {player.name}")
        
        # Phase de pioche
        self.execute_draw_phase(player)
        
        # Phase de mana
        self.execute_mana_phase(player)
        
        # Phase de combat (attente d'actions)
        self.execute_combat_phase(player)
        
        # Phase de fin de tour
        self.execute_end_phase(player)
        
        self.log.append(f"[TOUR COMPLET] Fin du tour complet pour {player.name}")

    def _get_adjacent_targets(self, primary_target, target_type):
        """Récupère les cibles adjacentes à la cible principale"""
        adjacent_targets = []
        
        try:
            # Déterminer le type de cibles adjacentes
            is_enemy = target_type == "adjacent_enemies"
            
            # Obtenir toutes les unités du même type que la cible principale
            if is_enemy:
                # Pour adjacent_enemies, chercher parmi les ennemis
                potential_targets = []
                for unit in self.get_all_units():
                    if unit.owner != primary_target.owner:
                        potential_targets.append(unit)
            else:
                # Pour adjacent_allies, chercher parmi les alliés
                potential_targets = []
                for unit in self.get_all_units():
                    if unit.owner == primary_target.owner:
                        potential_targets.append(unit)
            
            if primary_target not in potential_targets:
                return adjacent_targets
            
            primary_index = potential_targets.index(primary_target)
            
            # Vérifier les unités adjacentes (gauche et droite)
            for offset in [-1, 1]:
                adjacent_index = primary_index + offset
                if 0 <= adjacent_index < len(potential_targets):
                    adjacent_unit = potential_targets[adjacent_index]
                    
                    # Vérifier que l'unité est vivante
                    if hasattr(adjacent_unit, 'hp') and adjacent_unit.hp > 0:
                        adjacent_targets.append(adjacent_unit)
            
            # Log pour debug
            if adjacent_targets:
                target_names = [t.name for t in adjacent_targets]
                self.log.append(f"[ADJACENT] Cibles adjacentes trouvées pour {primary_target.name}: {', '.join(target_names)}")
            else:
                self.log.append(f"[ADJACENT] Aucune cible adjacente trouvée pour {primary_target.name}")
            
        except Exception as e:
            self.log.append(f"[ERREUR] Erreur lors de la récupération des cibles adjacentes: {e}")
        
        return adjacent_targets

    def update_cooldowns(self, player):
        """Met à jour les cooldowns pour un joueur"""
        # Réduire les cooldowns des unités
        for unit in player.units:
            if hasattr(unit, 'cooldowns'):
                for i, cooldown in enumerate(unit.cooldowns):
                    if cooldown > 0:
                        unit.cooldowns[i] -= 1
        
        # Réduire le cooldown du héros
        if player.hero and hasattr(player.hero, 'ability_cooldown'):
            if player.hero.ability_cooldown > 0:
                player.hero.ability_cooldown -= 1