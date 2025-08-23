#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Point d'entrée principal pour le multijoueur Steam
"""

import pygame
import sys
import os
from typing import Optional

# Ajouter le répertoire parent au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from UI.steam_lobby_ui import SteamLobbyUI
from UI.steam_game_ui import SteamGameUI

class SteamGameApp:
    """Application principale du jeu multijoueur Steam"""
    
    def __init__(self):
        pygame.init()
        
        # Configuration de l'écran
        self.width = 1200
        self.height = 800
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("JeuDeCarte - Multijoueur Steam")
        
        # État de l'application
        self.current_ui = None
        self.lobby_ui = None
        self.game_ui = None
        self.running = True
        
        # Initialiser l'interface de lobby
        self._initialize_lobby_ui()
    
    def _initialize_lobby_ui(self):
        """Initialiser l'interface de lobby"""
        self.lobby_ui = SteamLobbyUI(self.screen)
        self.lobby_ui.set_game_start_callback(self._on_game_start)
        self.current_ui = self.lobby_ui
        
        print("[STEAM APP] Interface de lobby initialisée")
    
    def _on_game_start(self, lobby_data: dict):
        """Callback: Démarrer une partie"""
        print(f"[STEAM APP] Démarrage de la partie avec le lobby: {lobby_data.get('lobby_id', 'Unknown')}")
        
        # Créer l'interface de jeu
        self.game_ui = SteamGameUI(self.screen, lobby_data)
        self.current_ui = self.game_ui
        
        print("[STEAM APP] Interface de jeu initialisée")
    
    def _handle_events(self):
        """Gérer les événements Pygame"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # Retour au lobby depuis le jeu
                    if self.current_ui == self.game_ui:
                        self._return_to_lobby()
            
            # Transmettre l'événement à l'interface actuelle
            if self.current_ui:
                self.current_ui.handle_event(event)
    
    def _return_to_lobby(self):
        """Retourner au lobby"""
        if self.game_ui:
            self.game_ui.cleanup()
            self.game_ui = None
        
        self.current_ui = self.lobby_ui
        print("[STEAM APP] Retour au lobby")
    
    def _update(self):
        """Mettre à jour l'application"""
        if self.current_ui:
            self.current_ui.update()
    
    def _render(self):
        """Rendu de l'application"""
        if self.current_ui:
            self.current_ui.render()
        
        pygame.display.flip()
    
    def run(self):
        """Boucle principale de l'application"""
        clock = pygame.time.Clock()
        
        print("[STEAM APP] Démarrage de l'application multijoueur Steam")
        
        while self.running:
            # Gérer les événements
            self._handle_events()
            
            # Mettre à jour
            self._update()
            
            # Rendu
            self._render()
            
            # Limiter le framerate
            clock.tick(60)
        
        # Nettoyage
        self._cleanup()
    
    def _cleanup(self):
        """Nettoyer les ressources"""
        print("[STEAM APP] Nettoyage des ressources")
        
        if self.game_ui:
            self.game_ui.cleanup()
        
        if self.lobby_ui:
            self.lobby_ui.cleanup()
        
        pygame.quit()
        sys.exit()

def main():
    """Fonction principale"""
    try:
        app = SteamGameApp()
        app.run()
    except Exception as e:
        print(f"[STEAM APP] Erreur fatale: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 