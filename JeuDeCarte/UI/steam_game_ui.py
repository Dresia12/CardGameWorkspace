#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interface de jeu multijoueur Steam — version corrigée
- Supprime la double création/assignation des decks (source unique : CombatEngine)
- Initialise self.game_ended dans __init__
- Corrige les conversions str/int dans _sync_game_state
- Sécurise l'ordre d'initialisation et le mapping joueur/opposant
- Nettoie quelques vérifs et logs
"""

import pygame
import sys
import json
import time
from typing import Dict, List, Optional, Callable

# Import des modules Steam
sys.path.append('..')
from Steam.steam_networking import (
    steam_networking, send_game_action, broadcast_game_state,
    MessageType
)
from Steam.steam_integration import get_steam_user_info

# Import du moteur de jeu existant
from Engine.engine import CombatEngine, Player
from Engine.models import Hero, Unit, Card, Ability
from UI.game_ui import CombatScreen


class SteamGameUI:
    """Interface de jeu multijoueur Steam"""

    def __init__(self, game_ui, lobby_data: Dict):
        """
        Initialise SteamGameUI avec un GameUI existant
        
        Args:
            game_ui: Instance de GameUI existante (pour éviter les conflits)
            lobby_data: Données du lobby multijoueur
        """
        self.game_ui = game_ui
        self.screen = game_ui.screen
        self.width, self.height = self.screen.get_size()
        self.lobby_data = lobby_data
        self.user_info = get_steam_user_info()

        # État du jeu
        self.game_engine: Optional[CombatEngine] = None
        self.combat_screen: Optional[CombatScreen] = None
        self.is_host = False
        self.opponent_id: Optional[str] = None
        self.game_state: Dict = {}
        self.last_sync_time = 0.0
        self.sync_interval = 1.0  # Synchronisation toutes les 1 secondes
        self.game_ended = False
        
        # Système de séquence réseau pour éviter les désynchronisations
        self.net_seq = 0
        self.last_net_seq_received = -1
        
        # État de l'écran de fin de match
        self.show_match_end_screen = False
        self.match_end_result = ""

        # Interface
        self.font_medium = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)

        # Couleurs
        self.colors = {
            "background": (30, 30, 30),
            "panel": (50, 50, 50),
            "text": (255, 255, 255),
            "text_secondary": (200, 200, 200),
            "success": (0, 200, 0),
            "error": (200, 0, 0),
            "warning": (255, 200, 0),
        }

        # Callbacks réseau
        self._setup_network_callbacks()

        # Initialiser le jeu
        self._initialize_game()

    def _setup_network_callbacks(self):
        """Configurer les callbacks réseau"""
        steam_networking.register_callback(
            "game_action_received", self._on_game_action_received
        )
        steam_networking.register_callback(
            "game_state_received", self._on_game_state_received
        )
        steam_networking.register_callback(
            "player_disconnected", self._on_player_disconnected
        )

    def _initialize_game(self):
        """Initialiser le jeu multijoueur"""
        print(f"[STEAM GAME INIT] Début initialisation avec lobby_data: {self.lobby_data}")

        # Déterminer qui est l'hôte
        player1 = self.lobby_data.get("player1", {})
        player2 = self.lobby_data.get("player2", {})

        if player1 and player2:
            # Hypothèse : player1 est l'hôte dans le lobby. Vérifier contre l'ID local.
            self.is_host = (player1.get("id") == self.user_info.get("id"))
            self.opponent_id = player2.get("id") if self.is_host else player1.get("id")
            print(f"[STEAM GAME] {'Hôte' if self.is_host else 'Client'} - Opposant: {self.opponent_id}")
        else:
            print("[STEAM GAME INIT] ERREUR: Données de joueurs manquantes")
            print(f"[STEAM GAME INIT] player1: {player1}")
            print(f"[STEAM GAME INIT] player2: {player2}")
            return

        # Créer le moteur de jeu
        print("[STEAM GAME INIT] Création du moteur de jeu...")
        if self._create_game_engine():
            print("[STEAM GAME INIT] Moteur de jeu créé avec succès")
            if self.game_engine:
                # Créer et attacher l'interface de combat AU MOTEUR EXISTANT
                try:
                    print("[STEAM GAME INIT] Création du CombatScreen...")
                    
                    # Utiliser le GameUI existant passé en paramètre
                    print(f"[STEAM GAME INIT] Utilisation du GameUI existant: {type(self.game_ui)}")
                    
                    # Créer le CombatScreen avec le GameUI existant
                    self.combat_screen = CombatScreen(self.game_ui)
                    if not self.screen:
                        print("[STEAM GAME INIT] ERREUR: Écran non disponible")
                        return
                    self.combat_screen.screen = self.screen

                    # Activer le mode réseau pour le CombatScreen
                    self.combat_screen.set_network_mode(True)
                    print("[STEAM GAME INIT] Mode réseau activé pour CombatScreen")

                    # Lier directement le moteur existant : source unique de vérité
                    self.combat_screen.combat_engine = self.game_engine

                    # Configurer les références player/opponent pour l'UI
                    if self.is_host:
                        self.combat_screen.player = self.game_engine.players[0]
                        self.combat_screen.opponent = self.game_engine.players[1]
                    else:
                        self.combat_screen.player = self.game_engine.players[1]
                        self.combat_screen.opponent = self.game_engine.players[0]

                    print("[STEAM GAME INIT] CombatScreen prêt (lié au moteur)")
                except Exception as e:
                    print(f"[STEAM GAME INIT] Erreur création interface: {e}")
                    import traceback
                    traceback.print_exc()
            else:
                print("[STEAM GAME] Erreur: Moteur de jeu non créé")
        else:
            print("[STEAM GAME] Erreur: Impossible d'initialiser le moteur de jeu")

        print("[STEAM GAME INIT] === FIN INITIALISATION ===")
        print(f"[STEAM GAME INIT] game_engine: {'OK' if self.game_engine else 'ERREUR'}")
        print(f"[STEAM GAME INIT] combat_screen: {'OK' if self.combat_screen else 'ERREUR'}")
        print(f"[STEAM GAME INIT] screen: {'OK' if self.screen else 'ERREUR'}")

    def _create_game_engine(self) -> bool:
        """Créer le moteur de jeu"""
        try:
            # Créer les deux joueurs (multijoueur => pas d'IA ici)
            p1 = self._create_player("Joueur 1", is_ai=False, player_id=1)
            p2 = self._create_player("Joueur 2", is_ai=False, player_id=2)

            if p1 and p2:
                try:
                    self.game_engine = CombatEngine(p1, p2)
                    self.game_engine.initialize_game()
                    print("[STEAM GAME] Moteur de jeu initialisé avec succès")
                    print(
                        f"[STEAM GAME] J1: {len(p1.deck)} cartes, {len(p1.units)} unités — J2: {len(p2.deck)} cartes, {len(p2.units)} unités"
                    )
                    return True
                except Exception as e:
                    print(f"[STEAM GAME] Erreur initialisation CombatEngine: {e}")
                    return False
            else:
                print("[STEAM GAME] Erreur: Impossible de créer les joueurs (deck manquant ?)")
                return False
        except Exception as e:
            print(f"[STEAM GAME] Erreur initialisation moteur: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _create_player(self, name: str, is_ai: bool = False, player_id: int = 1) -> Optional[Player]:
        """Créer un joueur avec son deck sauvegardé (multijoueur : exige un deck valide)."""
        try:
            from Engine.deck_manager import deck_manager

            # Initialiser le deck manager si nécessaire
            if not getattr(deck_manager, "decks", None):
                print(f"[STEAM GAME] Initialisation du deck manager pour {name}...")
                try:
                    deck_manager.load_decks()
                    print(
                        f"[STEAM GAME] Deck manager initialisé avec {len(deck_manager.decks)} decks"
                    )
                except Exception as e:
                    print(f"[STEAM GAME] Erreur initialisation deck manager: {e}")
                    return None  # multijoueur: pas de fallback automatique

            current_deck = deck_manager.get_current_deck()
            if not current_deck:
                print(
                    f"[STEAM GAME] ERREUR: Aucun deck actuel disponible pour {name} (multijoueur)"
                )
                return None

            print(f"[STEAM GAME] Utilisation du deck actuel pour {name}: {current_deck.name}")

            # Conversion Héros
            try:
                if isinstance(current_deck.hero, dict):
                    hero_data = current_deck.hero
                    hero = Hero(
                        name=hero_data.get("name", "Héros par défaut"),
                        element=hero_data.get("element", "Neutre"),
                        base_stats=hero_data.get(
                            "stats", {"hp": 100, "attack": 20, "defense": 15}
                        ),
                    )
                else:
                    hero = current_deck.hero
            except Exception as e:
                print(f"[STEAM GAME] Erreur conversion héros: {e}")
                hero = Hero(
                    name="Héros par défaut",
                    element="Neutre",
                    base_stats={"hp": 100, "attack": 20, "defense": 15},
                )

            # Conversion Unités
            units: List[Unit] = []
            try:
                for unit_data in current_deck.units:
                    if isinstance(unit_data, dict):
                        abilities: List[Ability] = []
                        for ability_data in unit_data.get("abilities", []):
                            abilities.append(
                                Ability(
                                    name=ability_data.get("name", "Capacité"),
                                    description=ability_data.get("description", ""),
                                    cooldown=ability_data.get("cooldown", 0),
                                )
                            )
                        unit = Unit(
                            name=unit_data.get("name", "Unité"),
                            element=unit_data.get("element", "Neutre"),
                            stats={
                                "hp": unit_data.get("hp", 100),
                                "max_hp": unit_data.get("hp", 100),
                                "attack": unit_data.get("attack", 10),
                                "defense": unit_data.get("defense", 5),
                            },
                            abilities=abilities,
                        )
                        units.append(unit)
                    else:
                        units.append(unit_data)
            except Exception as e:
                print(f"[STEAM GAME] Erreur conversion unités: {e}")
                for i in range(5):
                    units.append(
                        Unit(
                            name=f"Unité par défaut {i+1}",
                            element="Neutre",
                            stats={"hp": 100, "max_hp": 100, "attack": 10, "defense": 5},
                            abilities=[],
                        )
                    )

            # Conversion Cartes
            cards: List[Card] = []
            try:
                for card_data in current_deck.cards:
                    if isinstance(card_data, dict):
                        cards.append(
                            Card(
                                name=card_data.get("name", "Carte"),
                                cost=card_data.get("cost", 1),
                                element=card_data.get("element", "Neutre"),
                                card_type=card_data.get("card_type", "sort"),
                                effect=card_data.get("effect", ""),
                                target_type=card_data.get("target_type", "any"),
                                effects=card_data.get("effects", []),
                            )
                        )
                    else:
                        cards.append(card_data)
            except Exception as e:
                print(f"[STEAM GAME] Erreur conversion cartes: {e}")
                for i in range(30):
                    cards.append(
                        Card(
                            name=f"Carte par défaut {i+1}",
                            cost=1,
                            element="Neutre",
                            card_type="sort",
                            effect="",
                            target_type="any",
                            effects=[],
                        )
                    )

            # Validation minimale
            if len(units) != 5:
                print(f"[STEAM GAME] AVERTISSEMENT: {len(units)} unités au lieu de 5")
            if len(cards) != 30:
                print(f"[STEAM GAME] AVERTISSEMENT: {len(cards)} cartes au lieu de 30")
            if not hero:
                print("[STEAM GAME] AVERTISSEMENT: Pas de héros")

            return Player(name, cards, hero, units)
        except Exception as e:
            print(f"[STEAM GAME] Erreur création joueur {name}: {e}")
            return None

    # === Callbacks réseau ===
    def _on_game_action_received(self, data: Dict):
        try:
            action = data.get("action", {})
            sender_id = data.get("sender_id")
            print(f"[STEAM GAME] Action reçue de {sender_id}: {action}")
            self._apply_remote_action(action)
        except Exception as e:
            print(f"[STEAM GAME] Erreur traitement action: {e}")

    def _on_game_state_received(self, data: Dict):
        try:
            # Vérifier la séquence réseau pour éviter les paquets en retard/doublons
            seq = data.get("seq", -1)
            if seq <= self.last_net_seq_received:
                print(f"[STEAM GAME] Paquet ignoré (seq {seq} <= {self.last_net_seq_received})")
                return  # Ignorer paquets en retard/doublons
            
            self.last_net_seq_received = seq
            state = data.get("state", {})
            sender_id = data.get("sender_id")
            print(f"[STEAM GAME] État reçu de {sender_id} (seq: {seq})")
            self._sync_game_state(state)
        except Exception as e:
            print(f"[STEAM GAME] Erreur synchronisation état: {e}")

    def _on_player_disconnected(self, data: Dict):
        player_id = data.get("player_id")
        player_name = data.get("player_name", "Unknown")
        print(f"[STEAM GAME] Joueur déconnecté: {player_name} ({player_id})")
        self._show_disconnect_message(player_name)

    # === Application/synchro d'actions/état ===
    def _apply_remote_action(self, action: Dict):
        if not self.game_engine:
            return

        if self.combat_screen and hasattr(self.combat_screen, "receive_network_action"):
            self.combat_screen.receive_network_action(action)
            print(f"[STEAM GAME] Action transmise au CombatScreen: {action.get('type')}")
        else:
            print(
                f"[STEAM GAME] CombatScreen non disponible pour traiter l'action: {action.get('type')}"
            )

        action_type = action.get("type")
        if action_type == "play_card":
            card_index = action.get("card_index")
            target_info = action.get("target_info")
            if (
                self.game_engine.players[1]
                == self.game_engine.players[self.game_engine.current_player_index]
            ):
                success = self.game_engine.play_card_with_target(
                    card_index, target_info, self.game_engine.players[1]
                )
                if success:
                    print(f"[STEAM GAME] Carte jouée par l'adversaire: {card_index}")
        elif action_type == "use_ability":
            # Implémentation selon votre système
            pass
        elif action_type == "end_turn":
            if (
                self.game_engine.players[1]
                == self.game_engine.players[self.game_engine.current_player_index]
            ):
                self.game_engine.next_turn()
                print("[STEAM GAME] Tour terminé par l'adversaire")

    def _sync_game_state(self, state: Dict):
        if not self.game_engine:
            return

        # Unités
        units_state = state.get("units", {})
        for player_index_str, player_units in units_state.items():
            try:
                player_index = int(player_index_str)
                if 0 <= player_index < len(self.game_engine.players):
                    player = self.game_engine.players[player_index]
                    for unit_index_str, unit_state in player_units.items():
                        try:
                            unit_index = int(unit_index_str)
                            if 0 <= unit_index < len(player.units):
                                unit = player.units[unit_index]
                                unit.stats["hp"] = unit_state.get("hp", unit.stats.get("hp", 0))
                                if "max_hp" in unit_state:
                                    unit.stats["max_hp"] = unit_state.get(
                                        "max_hp", unit.stats.get("max_hp", unit.stats.get("hp", 0))
                                    )
                        except (ValueError, TypeError) as e:
                            print(f"[STEAM GAME] Erreur conversion unit_index: {e}")
            except (ValueError, TypeError) as e:
                print(f"[STEAM GAME] Erreur conversion player_index: {e}")

        # Mains (seulement la taille)
        hands_state = state.get("hands", {})
        for player_index_str, hand_size in hands_state.items():
            try:
                player_index = int(player_index_str)
                if 0 <= player_index < len(self.game_engine.players):
                    player = self.game_engine.players[player_index]
                    # Option: exposer une propriété 'reported_hand_size' côté UI
                    setattr(player, "reported_hand_size", int(hand_size))
            except (ValueError, TypeError) as e:
                print(f"[STEAM GAME] Erreur synchro main: {e}")

        # Tour courant
        current_turn = state.get("current_turn")
        if isinstance(current_turn, int):
            self.game_engine.current_player_index = current_turn

        # Compteur de tour (si transmis)
        if isinstance(state.get("turn_count"), int):
            self.game_engine.turn_count = state["turn_count"]

        print("[STEAM GAME] État synchronisé")

    # === Envoi réseau ===
    def _send_game_action(self, action: Dict):
        if self.opponent_id:
            success = send_game_action(self.opponent_id, action)
            if success:
                print(f"[STEAM GAME] Action envoyée: {action.get('type')}")
            else:
                print(f"[STEAM GAME] Erreur envoi action: {action.get('type')}")

    def _broadcast_game_state(self):
        if not self.game_engine:
            return
        current_time = time.time()
        if current_time - self.last_sync_time < self.sync_interval:
            return

        # Incrémenter la séquence réseau
        self.net_seq += 1
        
        state = {
            "units": {},
            "hands": {},
            "current_turn": self.game_engine.current_player_index,
            "turn_count": self.game_engine.turn_count,
        }

        # Unités
        for i, player in enumerate(self.game_engine.players):
            state["units"][str(i)] = {}
            for j, unit in enumerate(player.units):
                u_hp = unit.stats.get("hp", 0)
                u_mhp = unit.stats.get("max_hp", u_hp)
                state["units"][str(i)][str(j)] = {"hp": u_hp, "max_hp": u_mhp}

        # Mains (taille uniquement)
        for i, player in enumerate(self.game_engine.players):
            state["hands"][str(i)] = len(getattr(player, "hand", []))

        # Créer le payload avec séquence
        payload = {
            "type": "game_state",
            "seq": self.net_seq,
            "state": state
        }
        
        sent_count = broadcast_game_state(payload)
        if sent_count > 0:
            self.last_sync_time = current_time
            print(f"[STEAM GAME] État envoyé (seq: {self.net_seq})")

    # === Rendu/UI ===
    def _show_disconnect_message(self, player_name: str):
        print(f"[STEAM GAME] {player_name} s'est déconnecté")

    def handle_event(self, event: pygame.event.Event):
        if self.show_match_end_screen:
            self._handle_match_end_event(event)
        elif self.combat_screen:
            # Utiliser le système d'événements du CombatScreen existant
            self.combat_screen.handle_event(event)
            if hasattr(self.combat_screen, "last_action") and self.combat_screen.last_action:
                action = self.combat_screen.last_action
                print(f"[STEAM GAME] Action interceptée: {action}")
                self._send_game_action(action)
                self.combat_screen.last_action = None

    def update(self):
        if self.combat_screen:
            self.combat_screen.update()
        self._broadcast_game_state()

        if self.game_engine and not self.game_ended:
            game_result = self.game_engine.is_game_over()
            if isinstance(game_result, dict) and game_result.get("status") != "ongoing":
                self.game_ended = True
                self._handle_game_end(game_result)

    def render(self):
        try:
            if self.show_match_end_screen:
                self._render_match_end_screen()
            elif self.combat_screen:
                # Utiliser le système de rendu du GameUI existant
                self.combat_screen.draw(self.screen)
                self._render_network_info()
            else:
                self._render_loading_screen()
        except Exception as e:
            print(f"[STEAM GAME] Erreur rendu: {e}")
            self._render_error_screen()

    def draw(self, screen: pygame.Surface):
        self.screen = screen
        self.render()

    def _render_network_info(self):
        connection_status = "Connecté" if self.opponent_id else "Déconnecté"
        status_color = self.colors["success"] if self.opponent_id else self.colors["error"]
        status_text = self.font_small.render(f"Réseau: {connection_status}", True, status_color)
        self.screen.blit(status_text, (10, 10))

        lobby_info = f"Lobby: {str(self.lobby_data.get('lobby_id', 'Unknown'))[:8]}"
        lobby_text = self.font_small.render(lobby_info, True, self.colors["text_secondary"])
        self.screen.blit(lobby_text, (10, 30))

        role_text = "Hôte" if self.is_host else "Client"
        role_surface = self.font_small.render(f"Rôle: {role_text}", True, self.colors["text_secondary"])
        self.screen.blit(role_surface, (10, 50))

    def _render_loading_screen(self):
        self.screen.fill(self.colors["background"])
        title = self.font_medium.render(
            "Chargement du jeu multijoueur...", True, self.colors["text"]
        )
        title_rect = title.get_rect(center=(self.width // 2, self.height // 2))
        self.screen.blit(title, title_rect)

    def _render_error_screen(self):
        self.screen.fill(self.colors["background"])
        title = self.font_medium.render("Erreur de rendu", True, self.colors["error"])
        title_rect = title.get_rect(center=(self.width // 2, self.height // 2 - 50))
        self.screen.blit(title, title_rect)
        subtitle = self.font_small.render(
            "Le jeu multijoueur a rencontré un problème", True, self.colors["text_secondary"]
        )
        subtitle_rect = subtitle.get_rect(center=(self.width // 2, self.height // 2))
        self.screen.blit(subtitle, subtitle_rect)
    
    def _render_match_end_screen(self):
        """Rendu de l'écran de fin de match"""
        self.screen.fill(self.colors["background"])
        
        # Titre du résultat
        title = self.font_medium.render(self.match_end_result, True, self.colors["text"])
        title_rect = title.get_rect(center=(self.width // 2, self.height // 2 - 100))
        self.screen.blit(title, title_rect)
        
        # Bouton "Retour au lobby"
        button_rect = pygame.Rect(self.width // 2 - 100, self.height // 2, 200, 50)
        pygame.draw.rect(self.screen, self.colors["panel"], button_rect)
        pygame.draw.rect(self.screen, self.colors["text"], button_rect, 2)
        
        button_text = self.font_small.render("Retour au lobby", True, self.colors["text"])
        button_text_rect = button_text.get_rect(center=button_rect.center)
        self.screen.blit(button_text, button_text_rect)
        
        # Stocker la position du bouton pour la gestion des clics
        self.return_button_rect = button_rect
    
    def _handle_match_end_event(self, event: pygame.event.Event):
        """Gérer les événements de l'écran de fin de match"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Clic gauche
                mouse_pos = pygame.mouse.get_pos()
                if hasattr(self, 'return_button_rect') and self.return_button_rect.collidepoint(mouse_pos):
                    print("[STEAM GAME] Retour au lobby demandé")
                    self._return_to_lobby()
    
    def _return_to_lobby(self):
        """Retourner au lobby et réinitialiser l'UI"""
        print("[STEAM GAME] Retour au lobby...")
        
        # Nettoyer les ressources
        self.cleanup()
        
        # Réinitialiser l'état
        self.game_engine = None
        self.combat_screen = None
        self.game_ended = False
        self.show_match_end_screen = False
        self.match_end_result = ""
        self.net_seq = 0
        self.last_net_seq_received = -1
        
        # TODO: Retourner au menu principal ou au lobby
        # Pour l'instant, on affiche un message
        print("[STEAM GAME] Retour au menu principal...")
        # Note: Il faudrait implémenter un callback pour retourner au menu principal

    def _handle_game_end(self, result: Dict):
        status = result.get("status")
        message = result.get("message", "")
        print(f"[STEAM GAME] Partie terminée: {status} - {message}")
        
        # Déterminer le résultat pour l'affichage
        if status == "victory":
            self.match_end_result = "Victoire !"
        elif status == "defeat":
            self.match_end_result = "Défaite !"
        elif status == "draw":
            self.match_end_result = "Match nul !"
        else:
            self.match_end_result = f"Match terminé - {message}"
        
        # Afficher l'écran de fin de match
        self.show_match_end_screen = True

    def cleanup(self):
        if self.combat_screen and hasattr(self.combat_screen, "cleanup"):
            self.combat_screen.cleanup()
