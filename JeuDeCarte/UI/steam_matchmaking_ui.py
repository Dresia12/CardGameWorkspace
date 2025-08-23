#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Interface utilisateur pour le matchmaking automatique Steam
"""

import pygame
import sys
import time
import threading
from typing import Optional, Callable

# Import des modules Steam
sys.path.append('..')
from Steam.steam_integration import initialize_steam, get_steam_user_info, is_steam_available
from Steam.online_matchmaking import start_online_matchmaking, stop_online_matchmaking, get_online_matchmaking_status, set_online_matchmaking_callback
from Steam.steam_networking import start_networking, stop_networking

class SteamMatchmakingUI:
    """Interface utilisateur pour le matchmaking automatique"""
    
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.width, self.height = screen.get_size()
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)
        
        # État du matchmaking
        self.is_searching = False
        self.search_start_time = 0
        self.user_info = None
        self.matchmaking_status = {}
        self.on_match_found = None
        
        # Couleurs
        self.colors = {
            "background": (30, 30, 30),
            "panel": (50, 50, 50),
            "button": (70, 70, 70),
            "button_hover": (90, 90, 90),
            "button_active": (0, 150, 255),
            "text": (255, 255, 255),
            "text_secondary": (200, 200, 200),
            "accent": (0, 150, 255),
            "success": (0, 200, 0),
            "error": (200, 0, 0),
            "warning": (255, 200, 0)
        }
        
        # Boutons
        self.buttons = []
        self._setup_buttons()
        
        # Initialiser Steam
        self._initialize_steam()
        
        # Configurer le callback pour les matches trouvés
        set_online_matchmaking_callback("match_found", self._on_match_found)
        
        # Thread de mise à jour du statut
        self.status_thread = None
        self.status_thread_running = False
        
    def _initialize_steam(self):
        """Initialiser Steam"""
        if initialize_steam():
            self.user_info = get_steam_user_info()
            start_networking()
            print(f"[MATCHMAKING UI] Steam initialisé pour {self.user_info['name']}")
        else:
            # Créer un utilisateur par défaut pour le test local
            import uuid
            self.user_info = {
                "id": str(uuid.uuid4()),
                "name": f"Joueur_{uuid.uuid4().hex[:8]}"
            }
            print(f"[MATCHMAKING UI] Utilisateur par défaut créé: {self.user_info['name']}")
    
    def _setup_buttons(self):
        """Configurer les boutons"""
        button_width = 300
        button_height = 60
        center_x = self.width // 2
        start_y = 400
        
        # Bouton Rechercher un match
        self.search_button = {
            "rect": pygame.Rect(center_x - button_width // 2, start_y, button_width, button_height),
            "text": "RECHERCHER UN MATCH",
            "action": self._toggle_search,
            "color": self.colors["button"],
            "text_color": self.colors["text"]
        }
        
        # Bouton Annuler
        self.cancel_button = {
            "rect": pygame.Rect(center_x - button_width // 2, start_y + 80, button_width, button_height),
            "text": "ANNULER",
            "action": self._cancel_search,
            "color": self.colors["error"],
            "text_color": self.colors["text"]
        }
        
        # Bouton Retour
        self.back_button = {
            "rect": pygame.Rect(center_x - button_width // 2, start_y + 160, button_width, button_height),
            "text": "RETOUR",
            "action": self._go_back,
            "color": self.colors["button"],
            "text_color": self.colors["text"]
        }
        
        self.buttons = [self.search_button, self.cancel_button, self.back_button]
    
    def set_match_found_callback(self, callback: Callable):
        """Définir le callback quand un match est trouvé"""
        self.on_match_found = callback
    
    def _toggle_search(self):
        """Basculer la recherche de match"""
        if not self.is_searching:
            self._start_search()
        else:
            self._stop_search()
    
    def _start_search(self):
        """Démarrer la recherche de match"""
        if not self.user_info:
            print("[MATCHMAKING UI] Erreur: Utilisateur non connecté")
            return
        
        # Utiliser le matchmaking en ligne
        if start_online_matchmaking(self.user_info["id"], self.user_info["name"]):
            self.is_searching = True
            self.search_start_time = time.time()
            self.search_button["text"] = "RECHERCHE EN COURS..."
            self.search_button["color"] = self.colors["button_active"]
            
            # Démarrer le thread de mise à jour du statut
            self._start_status_thread()
            
            print(f"[MATCHMAKING UI] Recherche de match en ligne démarrée pour {self.user_info['name']}")
        else:
            print("[MATCHMAKING UI] Erreur: Impossible de démarrer la recherche en ligne")
    
    def _stop_search(self):
        """Arrêter la recherche de match"""
        if not self.user_info:
            return
        
        if stop_online_matchmaking():
            self.is_searching = False
            self.search_button["text"] = "RECHERCHER UN MATCH"
            self.search_button["color"] = self.colors["button"]
            
            # Arrêter le thread de mise à jour du statut
            self._stop_status_thread()
            
            print(f"[MATCHMAKING UI] Recherche de match en ligne arrêtée pour {self.user_info['name']}")
        else:
            print("[MATCHMAKING UI] Erreur: Impossible d'arrêter la recherche en ligne")
    
    def _cancel_search(self):
        """Annuler la recherche et retourner au menu précédent"""
        self._stop_search()
        self._go_back()
    
    def _go_back(self):
        """Retourner au menu précédent"""
        if self.is_searching:
            self._stop_search()
        
        # Le callback sera géré par l'interface parent
        if hasattr(self, 'on_back') and self.on_back:
            self.on_back()
    
    def _start_status_thread(self):
        """Démarrer le thread de mise à jour du statut"""
        if self.status_thread_running:
            return
        
        self.status_thread_running = True
        self.status_thread = threading.Thread(target=self._status_update_loop)
        self.status_thread.daemon = True
        self.status_thread.start()
    
    def _stop_status_thread(self):
        """Arrêter le thread de mise à jour du statut"""
        self.status_thread_running = False
        if self.status_thread:
            self.status_thread.join(timeout=1.0)
    
    def _status_update_loop(self):
        """Boucle de mise à jour du statut"""
        while self.status_thread_running:
            try:
                self.matchmaking_status = get_online_matchmaking_status()
                time.sleep(1)  # Mettre à jour toutes les secondes
            except Exception as e:
                print(f"[MATCHMAKING UI] Erreur mise à jour statut: {e}")
                time.sleep(5)
    
    def handle_event(self, event: pygame.event.Event):
        """Gérer les événements Pygame"""
        if event.type == pygame.KEYDOWN:
            self._handle_keydown(event.key)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self._handle_mouse_click(event.pos)
    
    def _handle_keydown(self, key: int):
        """Gérer les touches pressées"""
        if key == pygame.K_ESCAPE:
            self._go_back()
        elif key == pygame.K_SPACE:
            self._toggle_search()
    
    def _handle_mouse_click(self, pos: tuple):
        """Gérer les clics de souris"""
        x, y = pos
        
        for button in self.buttons:
            if button["rect"].collidepoint(x, y):
                button["action"]()
                return
    
    def update(self):
        """Mettre à jour l'interface"""
        # Le polling se fait dans OnlineMatchmaking
        # Le callback _on_match_found sera appelé automatiquement
        pass
    
    def _on_match_found(self, match_data=None):
        """Appelé quand un match est trouvé"""
        print(f"[MATCHMAKING UI] Match trouvé ! Données: {match_data}")
        
        # Arrêter la recherche
        self.is_searching = False
        self.search_button["text"] = "RECHERCHER UN MATCH"
        self.search_button["color"] = self.colors["button"]
        
        print(f"[MATCHMAKING UI] on_match_found callback: {self.on_match_found}")
        if self.on_match_found and match_data:
            try:
                # Utiliser les vraies données du match du serveur
                print(f"[MATCHMAKING UI] Appel du callback avec: {match_data}")
                self.on_match_found(match_data)
                print("[MATCHMAKING UI] Callback exécuté avec succès")
            except Exception as e:
                print(f"[MATCHMAKING UI] Erreur lors de l'exécution du callback: {e}")
                import traceback
                traceback.print_exc()
        else:
            print(f"[MATCHMAKING UI] Erreur: on_match_found={self.on_match_found}, match_data={match_data}")
    
    def render(self):
        """Rendu de l'interface"""
        # Fond
        self.screen.fill(self.colors["background"])
        
        # Titre
        title = self.font_large.render("MATCHMAKING AUTOMATIQUE", True, self.colors["text"])
        title_rect = title.get_rect(center=(self.width // 2, 100))
        self.screen.blit(title, title_rect)
        
        # Sous-titre
        subtitle = self.font_medium.render("Trouvez un adversaire en ligne", True, self.colors["text_secondary"])
        subtitle_rect = subtitle.get_rect(center=(self.width // 2, 150))
        self.screen.blit(subtitle, subtitle_rect)
        
        # Informations utilisateur
        if self.user_info:
            user_text = f"Connecté en tant que: {self.user_info['name']}"
            user_surface = self.font_small.render(user_text, True, self.colors["text_secondary"])
            user_rect = user_surface.get_rect(center=(self.width // 2, 200))
            self.screen.blit(user_surface, user_rect)
        
        # Statut de recherche
        if self.is_searching:
            self._render_search_status()
        else:
            self._render_idle_status()
        
        # Boutons
        self._render_buttons()
    
    def draw(self, screen: pygame.Surface):
        """Méthode draw pour compatibilité avec le système d'écrans"""
        self.screen = screen  # Mettre à jour la référence de l'écran
        self.render()
    
    def _render_search_status(self):
        """Rendu du statut de recherche"""
        # Temps de recherche
        search_time = int(time.time() - self.search_start_time)
        time_text = f"Recherche en cours... ({search_time}s)"
        time_surface = self.font_medium.render(time_text, True, self.colors["accent"])
        time_rect = time_surface.get_rect(center=(self.width // 2, 300))
        self.screen.blit(time_surface, time_rect)
        
        # Animation de chargement
        dots = "." * ((search_time // 2) % 4)
        loading_text = f"Recherche d'adversaire{dots}"
        loading_surface = self.font_small.render(loading_text, True, self.colors["text_secondary"])
        loading_rect = loading_surface.get_rect(center=(self.width // 2, 330))
        self.screen.blit(loading_surface, loading_rect)
        
        # Statut de la file d'attente
        if self.matchmaking_status:
            queue_length = self.matchmaking_status.get("queue_length", 0)
            wait_time = self.matchmaking_status.get("estimated_wait_time", 0)
            
            queue_text = f"Joueurs en attente: {queue_length}"
            queue_surface = self.font_small.render(queue_text, True, self.colors["text_secondary"])
            queue_rect = queue_surface.get_rect(center=(self.width // 2, 360))
            self.screen.blit(queue_surface, queue_rect)
            
            if wait_time > 0:
                wait_text = f"Temps d'attente estimé: {wait_time}s"
                wait_surface = self.font_small.render(wait_text, True, self.colors["warning"])
                wait_rect = wait_surface.get_rect(center=(self.width // 2, 380))
                self.screen.blit(wait_surface, wait_rect)
    
    def _render_idle_status(self):
        """Rendu du statut inactif"""
        status_text = "Appuyez sur ESPACE ou cliquez sur 'RECHERCHER UN MATCH' pour commencer"
        status_surface = self.font_medium.render(status_text, True, self.colors["text_secondary"])
        status_rect = status_surface.get_rect(center=(self.width // 2, 300))
        self.screen.blit(status_surface, status_rect)
    
    def _render_buttons(self):
        """Rendu des boutons"""
        mouse_pos = pygame.mouse.get_pos()
        
        for button in self.buttons:
            # Couleur selon l'état
            color = button["color"]
            if button["rect"].collidepoint(mouse_pos):
                color = self.colors["button_hover"]
            
            # Dessiner le bouton
            pygame.draw.rect(self.screen, color, button["rect"])
            pygame.draw.rect(self.screen, self.colors["text"], button["rect"], 2)
            
            # Texte du bouton
            text_surface = self.font_medium.render(button["text"], True, button["text_color"])
            text_rect = text_surface.get_rect(center=button["rect"].center)
            self.screen.blit(text_surface, text_rect)
    
    def cleanup(self):
        """Nettoyer les ressources"""
        print("[MATCHMAKING UI] Nettoyage des ressources")
        
        if self.is_searching:
            self._stop_search()
        
        self._stop_status_thread()
