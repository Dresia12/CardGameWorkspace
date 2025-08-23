#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Interface utilisateur pour le lobby Steam
"""

import pygame
import sys
import time
from typing import List, Dict, Optional, Callable

# Import des modules Steam
sys.path.append('..')
from Steam.steam_integration import initialize_steam, get_steam_user_info, is_steam_available
from Steam.steam_matchmaking import create_lobby, join_lobby, search_lobbies, LobbyType
from Steam.steam_networking import start_networking, stop_networking, connect_to_player

class SteamLobbyUI:
    """Interface utilisateur pour le lobby Steam"""
    
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.width, self.height = screen.get_size()
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)
        
        # État de l'interface
        self.current_screen = "main_menu"  # main_menu, lobby_list, lobby_room
        self.selected_lobby_index = 0
        self.lobby_list = []
        self.current_lobby = None
        self.user_info = None
        
        # Couleurs
        self.colors = {
            "background": (30, 30, 30),
            "panel": (50, 50, 50),
            "button": (70, 70, 70),
            "button_hover": (90, 90, 90),
            "text": (255, 255, 255),
            "text_secondary": (200, 200, 200),
            "accent": (0, 150, 255),
            "success": (0, 200, 0),
            "error": (200, 0, 0)
        }
        
        # Initialiser Steam
        self._initialize_steam()
        
        # Callbacks
        self.on_game_start = None
        
    def _initialize_steam(self):
        """Initialiser Steam"""
        if initialize_steam():
            self.user_info = get_steam_user_info()
            start_networking()
            print(f"[LOBBY] Steam initialisé pour {self.user_info['name']}")
        else:
            print("[LOBBY] Erreur: Steam non disponible")
    
    def set_game_start_callback(self, callback: Callable):
        """Définir le callback pour démarrer une partie"""
        self.on_game_start = callback
    
    def handle_event(self, event: pygame.event.Event):
        """Gérer les événements Pygame"""
        if event.type == pygame.KEYDOWN:
            self._handle_keydown(event.key)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self._handle_mouse_click(event.pos)
    
    def _handle_keydown(self, key: int):
        """Gérer les touches pressées"""
        if self.current_screen == "main_menu":
            if key == pygame.K_1:
                self._create_lobby()
            elif key == pygame.K_2:
                self._search_lobbies()
        elif self.current_screen == "lobby_list":
            if key == pygame.K_UP:
                self.selected_lobby_index = max(0, self.selected_lobby_index - 1)
            elif key == pygame.K_DOWN:
                self.selected_lobby_index = min(len(self.lobby_list) - 1, self.selected_lobby_index + 1)
            elif key == pygame.K_RETURN:
                self._join_selected_lobby()
            elif key == pygame.K_ESCAPE:
                self.current_screen = "main_menu"
        elif self.current_screen == "lobby_room":
            if key == pygame.K_ESCAPE:
                self._leave_lobby()
    
    def _handle_mouse_click(self, pos: tuple):
        """Gérer les clics de souris"""
        x, y = pos
        
        if self.current_screen == "main_menu":
            # Bouton Créer une partie
            if 100 <= x <= 400 and 200 <= y <= 250:
                self._create_lobby()
            # Bouton Rejoindre une partie
            elif 100 <= x <= 400 and 300 <= y <= 350:
                self._search_lobbies()
        
        elif self.current_screen == "lobby_list":
            # Zone de sélection des lobbies
            if 50 <= x <= 750 and 150 <= y <= 500:
                lobby_index = (y - 150) // 50
                if 0 <= lobby_index < len(self.lobby_list):
                    self.selected_lobby_index = lobby_index
                    if pygame.mouse.get_pressed()[0]:  # Clic gauche
                        self._join_selected_lobby()
            # Bouton Retour
            elif 100 <= x <= 200 and 550 <= y <= 580:
                self.current_screen = "main_menu"
    
    def _create_lobby(self):
        """Créer un nouveau lobby"""
        if not self.user_info:
            print("[LOBBY] Erreur: Utilisateur non connecté")
            return
        
        lobby_id = create_lobby(LobbyType.PUBLIC, 2)
        if lobby_id:
            # Ajouter le créateur au lobby
            if join_lobby(lobby_id, self.user_info["id"], self.user_info["name"]):
                # Recharger les informations du lobby depuis le système
                import Steam.steam_matchmaking as steam_mm
                steam_mm.steam_matchmaking._load_lobbies()
                lobbies = steam_mm.search_lobbies(LobbyType.PUBLIC)
                
                # Trouver le lobby créé
                for lobby in lobbies:
                    if lobby.get("lobby_id") == lobby_id:
                        self.current_lobby = lobby
                        break
                else:
                    # Fallback si le lobby n'est pas trouvé
                    self.current_lobby = {
                        "lobby_id": lobby_id,
                        "owner_id": self.user_info["id"],
                        "players": [self.user_info],
                        "state": "waiting"
                    }
                
                self.current_screen = "lobby_room"
                print(f"[LOBBY] Lobby créé et rejoint: {lobby_id}")
            else:
                print("[LOBBY] Erreur: Impossible de rejoindre le lobby créé")
        else:
            print("[LOBBY] Erreur: Impossible de créer le lobby")
    
    def _search_lobbies(self):
        """Rechercher des lobbies disponibles"""
        # Forcer le rechargement depuis le fichier
        import Steam.steam_matchmaking as steam_mm
        steam_mm.steam_matchmaking._load_lobbies()
        
        # Attendre un peu pour s'assurer que le fichier est bien lu
        import time
        time.sleep(0.1)
        
        self.lobby_list = search_lobbies(LobbyType.PUBLIC)
        self.selected_lobby_index = 0
        self.current_screen = "lobby_list"
        print(f"[LOBBY] {len(self.lobby_list)} lobbies trouvés")
    
    def _join_selected_lobby(self):
        """Rejoindre le lobby sélectionné"""
        if not self.lobby_list or self.selected_lobby_index >= len(self.lobby_list):
            return
        
        lobby = self.lobby_list[self.selected_lobby_index]
        lobby_id = lobby["lobby_id"]
        
        if join_lobby(lobby_id, self.user_info["id"], self.user_info["name"]):
            self.current_lobby = lobby
            self.current_screen = "lobby_room"
            
            # Se connecter au propriétaire du lobby
            owner_id = lobby["owner_id"]
            owner_name = next((p["name"] for p in lobby["players"] if p["id"] == owner_id), "Unknown")
            connect_to_player(owner_id, owner_name)
            
            print(f"[LOBBY] Rejoint le lobby: {lobby_id}")
        else:
            print(f"[LOBBY] Erreur: Impossible de rejoindre le lobby {lobby_id}")
    
    def _leave_lobby(self):
        """Quitter le lobby actuel"""
        if self.current_lobby:
            # En production, utiliser steam_matchmaking.leave_lobby()
            print(f"[LOBBY] Quitté le lobby: {self.current_lobby['lobby_id']}")
        
        self.current_lobby = None
        self.current_screen = "main_menu"
    
    def update(self):
        """Mettre à jour l'interface"""
        # Mettre à jour la liste des lobbies si nécessaire
        if self.current_screen == "lobby_list":
            # Forcer le rechargement depuis le fichier
            import Steam.steam_matchmaking as steam_mm
            steam_mm.steam_matchmaking._load_lobbies()
            self.lobby_list = search_lobbies(LobbyType.PUBLIC)
        
        # Mettre à jour les informations du lobby actuel
        if self.current_screen == "lobby_room" and self.current_lobby:
            # Recharger les informations du lobby depuis le fichier
            import Steam.steam_matchmaking as steam_mm
            steam_mm.steam_matchmaking._load_lobbies()
            
            # Chercher le lobby actuel dans la liste mise à jour
            lobby_id = self.current_lobby.get("lobby_id")
            if lobby_id:
                # Obtenir les informations fraîches du lobby
                lobby_info = steam_mm.steam_matchmaking.get_lobby_info(lobby_id)
                if lobby_info:
                    self.current_lobby = lobby_info
                    print(f"[LOBBY UI] Mise à jour lobby: {len(lobby_info.get('players', []))}/{lobby_info.get('max_players', 2)} joueurs")
                else:
                    # Le lobby n'existe plus
                    print(f"[LOBBY UI] Lobby {lobby_id} n'existe plus")
                    self.current_screen = "main_menu"
                    return
            
            # Vérifier si le lobby est prêt
            if len(self.current_lobby.get("players", [])) == 2:
                # Démarrer la partie
                if self.on_game_start:
                    self.on_game_start(self.current_lobby)
            
            # Attendre un peu pour la synchronisation
            import time
            time.sleep(0.1)
    
    def render(self):
        """Rendu de l'interface"""
        self.screen.fill(self.colors["background"])
        
        if self.current_screen == "main_menu":
            self._render_main_menu()
        elif self.current_screen == "lobby_list":
            self._render_lobby_list()
        elif self.current_screen == "lobby_room":
            self._render_lobby_room()
    
    def _render_main_menu(self):
        """Rendu du menu principal"""
        # Titre
        title = self.font_large.render("JeuDeCarte - Multijoueur Steam", True, self.colors["text"])
        title_rect = title.get_rect(center=(self.width // 2, 100))
        self.screen.blit(title, title_rect)
        
        # Informations utilisateur
        if self.user_info:
            user_text = self.font_medium.render(f"Connecté en tant que: {self.user_info['name']}", 
                                              True, self.colors["text_secondary"])
            user_rect = user_text.get_rect(center=(self.width // 2, 150))
            self.screen.blit(user_text, user_rect)
        
        # Boutons
        buttons = [
            ("1. Créer une partie", (100, 200, 300, 50)),
            ("2. Rejoindre une partie", (100, 300, 300, 50)),
            ("ESC. Quitter", (100, 400, 300, 50))
        ]
        
        for text, rect in buttons:
            color = self.colors["button"]
            if self._is_mouse_over(rect):
                color = self.colors["button_hover"]
            
            pygame.draw.rect(self.screen, color, rect)
            pygame.draw.rect(self.screen, self.colors["text"], rect, 2)
            
            button_text = self.font_medium.render(text, True, self.colors["text"])
            button_rect = button_text.get_rect(center=(rect[0] + rect[2] // 2, rect[1] + rect[3] // 2))
            self.screen.blit(button_text, button_rect)
    
    def _render_lobby_list(self):
        """Rendu de la liste des lobbies"""
        # Titre
        title = self.font_large.render("Lobbies Disponibles", True, self.colors["text"])
        title_rect = title.get_rect(center=(self.width // 2, 50))
        self.screen.blit(title, title_rect)
        
        # Liste des lobbies
        if not self.lobby_list:
            no_lobby_text = self.font_medium.render("Aucun lobby disponible", True, self.colors["text_secondary"])
            no_lobby_rect = no_lobby_text.get_rect(center=(self.width // 2, 200))
            self.screen.blit(no_lobby_text, no_lobby_rect)
        else:
            for i, lobby in enumerate(self.lobby_list):
                y_pos = 150 + i * 50
                color = self.colors["accent"] if i == self.selected_lobby_index else self.colors["panel"]
                
                # Rectangle de sélection
                pygame.draw.rect(self.screen, color, (50, y_pos, 700, 40))
                pygame.draw.rect(self.screen, self.colors["text"], (50, y_pos, 700, 40), 2)
                
                # Informations du lobby
                lobby_text = f"Lobby {lobby['lobby_id'][:8]} - Joueurs: {len(lobby['players'])}/{lobby['max_players']}"
                text_surface = self.font_small.render(lobby_text, True, self.colors["text"])
                self.screen.blit(text_surface, (60, y_pos + 10))
        
        # Instructions
        instructions = [
            "↑↓: Sélectionner | ENTER: Rejoindre | ESC: Retour",
            f"Lobbies trouvés: {len(self.lobby_list)}"
        ]
        
        for i, instruction in enumerate(instructions):
            inst_text = self.font_small.render(instruction, True, self.colors["text_secondary"])
            inst_rect = inst_text.get_rect(center=(self.width // 2, 550 + i * 30))
            self.screen.blit(inst_text, inst_rect)
    
    def _render_lobby_room(self):
        """Rendu de la salle de lobby"""
        if not self.current_lobby:
            return
        
        # Titre
        title = self.font_large.render("Salle de Lobby", True, self.colors["text"])
        title_rect = title.get_rect(center=(self.width // 2, 50))
        self.screen.blit(title, title_rect)
        
        # Informations du lobby
        lobby_info = f"Lobby: {self.current_lobby['lobby_id'][:8]}"
        info_text = self.font_medium.render(lobby_info, True, self.colors["text_secondary"])
        info_rect = info_text.get_rect(center=(self.width // 2, 100))
        self.screen.blit(info_text, info_rect)
        
        # Liste des joueurs
        players = self.current_lobby.get("players", [])
        player_title = self.font_medium.render("Joueurs:", True, self.colors["text"])
        self.screen.blit(player_title, (100, 150))
        
        for i, player in enumerate(players):
            player_text = f"{i+1}. {player['name']}"
            color = self.colors["success"] if player["id"] == self.user_info["id"] else self.colors["text"]
            player_surface = self.font_medium.render(player_text, True, color)
            self.screen.blit(player_surface, (120, 200 + i * 40))
        
        # Statut
        if len(players) == 2:
            status_text = "Prêt à démarrer !"
            status_color = self.colors["success"]
        else:
            status_text = "En attente d'un autre joueur..."
            status_color = self.colors["text_secondary"]
        
        status_surface = self.font_medium.render(status_text, True, status_color)
        status_rect = status_surface.get_rect(center=(self.width // 2, 350))
        self.screen.blit(status_surface, status_rect)
        
        # Instructions
        instructions = [
            "ESC: Quitter le lobby",
            f"Joueurs: {len(players)}/2"
        ]
        
        for i, instruction in enumerate(instructions):
            inst_text = self.font_small.render(instruction, True, self.colors["text_secondary"])
            inst_rect = inst_text.get_rect(center=(self.width // 2, 450 + i * 30))
            self.screen.blit(inst_text, inst_rect)
    
    def _is_mouse_over(self, rect: tuple) -> bool:
        """Vérifier si la souris est sur un rectangle"""
        x, y = pygame.mouse.get_pos()
        return rect[0] <= x <= rect[0] + rect[2] and rect[1] <= y <= rect[1] + rect[3]
    
    def cleanup(self):
        """Nettoyer les ressources"""
        stop_networking() 