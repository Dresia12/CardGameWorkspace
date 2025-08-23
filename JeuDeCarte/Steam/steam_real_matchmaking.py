#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Système de matchmaking utilisant les vraies APIs Steam
"""

import time
import threading
from typing import Dict, Optional, Callable
from enum import Enum

try:
    import steamworks
except ImportError:
    print("[STEAM] steamworks-py non installé. Installer avec: pip install steamworks-py")
    steamworks = None

class SteamMatchmakingState(Enum):
    """États du matchmaking Steam"""
    IDLE = "idle"
    SEARCHING = "searching"
    MATCHED = "matched"
    CONNECTING = "connecting"
    READY = "ready"

class SteamRealMatchmaking:
    """Système de matchmaking Steam réel"""
    
    def __init__(self, app_id: int):
        self.app_id = app_id
        self.steam = None
        self.current_state = SteamMatchmakingState.IDLE
        self.search_handle = None
        self.callbacks = {}
        self.is_initialized = False
        
    def initialize(self) -> bool:
        """Initialiser Steam"""
        if not steamworks:
            print("[STEAM] steamworks-py non disponible")
            return False
            
        try:
            self.steam = steamworks.Steamworks()
            if self.steam.initialize():
                self.is_initialized = True
                print(f"[STEAM] Initialisé avec App ID: {self.app_id}")
                return True
            else:
                print("[STEAM] Échec de l'initialisation")
                return False
        except Exception as e:
            print(f"[STEAM] Erreur d'initialisation: {e}")
            return False
    
    def start_matchmaking(self, max_players: int = 2) -> bool:
        """Démarrer le matchmaking Steam"""
        if not self.is_initialized:
            print("[STEAM] Steam non initialisé")
            return False
            
        if self.current_state != SteamMatchmakingState.IDLE:
            print("[STEAM] Matchmaking déjà en cours")
            return False
        
        try:
            # Créer une recherche de lobby
            self.search_handle = self.steam.matchmaking.create_lobby_search()
            
            # Configurer les critères de recherche
            self.steam.matchmaking.add_near_filter()
            self.steam.matchmaking.add_slots_available_filter(max_players)
            
            # Démarrer la recherche
            self.steam.matchmaking.search_for_lobby()
            
            self.current_state = SteamMatchmakingState.SEARCHING
            print("[STEAM] Recherche de lobby démarrée")
            
            # Démarrer le thread de monitoring
            self._start_monitoring()
            
            return True
            
        except Exception as e:
            print(f"[STEAM] Erreur démarrage matchmaking: {e}")
            return False
    
    def stop_matchmaking(self) -> bool:
        """Arrêter le matchmaking"""
        if self.current_state == SteamMatchmakingState.IDLE:
            return True
        
        try:
            if self.search_handle:
                self.steam.matchmaking.cancel_lobby_search(self.search_handle)
                self.search_handle = None
            
            self.current_state = SteamMatchmakingState.IDLE
            print("[STEAM] Matchmaking arrêté")
            return True
            
        except Exception as e:
            print(f"[STEAM] Erreur arrêt matchmaking: {e}")
            return False
    
    def create_lobby(self, max_players: int = 2, lobby_type: str = "public") -> bool:
        """Créer un lobby Steam"""
        if not self.is_initialized:
            return False
            
        try:
            # Créer un lobby
            lobby_id = self.steam.matchmaking.create_lobby(
                lobby_type="public" if lobby_type == "public" else "private",
                max_players=max_players
            )
            
            print(f"[STEAM] Lobby créé: {lobby_id}")
            
            # Déclencher le callback
            if "lobby_created" in self.callbacks:
                self.callbacks["lobby_created"]({"lobby_id": lobby_id})
            
            return True
            
        except Exception as e:
            print(f"[STEAM] Erreur création lobby: {e}")
            return False
    
    def join_lobby(self, lobby_id: str) -> bool:
        """Rejoindre un lobby"""
        if not self.is_initialized:
            return False
            
        try:
            self.steam.matchmaking.join_lobby(lobby_id)
            print(f"[STEAM] Rejoint le lobby: {lobby_id}")
            
            # Déclencher le callback
            if "lobby_joined" in self.callbacks:
                self.callbacks["lobby_joined"]({"lobby_id": lobby_id})
            
            return True
            
        except Exception as e:
            print(f"[STEAM] Erreur rejoindre lobby: {e}")
            return False
    
    def get_lobby_members(self, lobby_id: str) -> list:
        """Obtenir les membres d'un lobby"""
        if not self.is_initialized:
            return []
            
        try:
            members = self.steam.matchmaking.get_lobby_member_count(lobby_id)
            member_list = []
            
            for i in range(members):
                steam_id = self.steam.matchmaking.get_lobby_member_by_index(lobby_id, i)
                name = self.steam.friends.get_friend_persona_name(steam_id)
                member_list.append({
                    "steam_id": steam_id,
                    "name": name
                })
            
            return member_list
            
        except Exception as e:
            print(f"[STEAM] Erreur récupération membres: {e}")
            return []
    
    def _start_monitoring(self):
        """Démarrer le monitoring des événements Steam"""
        def monitor_loop():
            while self.current_state == SteamMatchmakingState.SEARCHING:
                try:
                    # Vérifier les événements Steam
                    self.steam.run_callbacks()
                    
                    # Vérifier si un lobby a été trouvé
                    if self.search_handle:
                        lobby_id = self.steam.matchmaking.get_lobby_from_search(self.search_handle)
                        if lobby_id:
                            self._on_lobby_found(lobby_id)
                            break
                    
                    time.sleep(0.1)  # 100ms
                    
                except Exception as e:
                    print(f"[STEAM] Erreur monitoring: {e}")
                    time.sleep(1)
        
        monitor_thread = threading.Thread(target=monitor_loop)
        monitor_thread.daemon = True
        monitor_thread.start()
    
    def _on_lobby_found(self, lobby_id: str):
        """Appelé quand un lobby est trouvé"""
        print(f"[STEAM] Lobby trouvé: {lobby_id}")
        
        self.current_state = SteamMatchmakingState.MATCHED
        
        # Déclencher le callback
        if "match_found" in self.callbacks:
            lobby_info = {
                "lobby_id": lobby_id,
                "members": self.get_lobby_members(lobby_id)
            }
            self.callbacks["match_found"](lobby_info)
    
    def set_callback(self, event_type: str, callback: Callable):
        """Définir un callback pour un événement"""
        self.callbacks[event_type] = callback
    
    def get_status(self) -> Dict:
        """Obtenir le statut du matchmaking"""
        return {
            "state": self.current_state.value,
            "initialized": self.is_initialized,
            "search_handle": self.search_handle is not None
        }

# Instance globale (à configurer avec votre App ID)
# REMPLACER 123456789 par votre vrai App ID Steam
steam_real_matchmaking = SteamRealMatchmaking(app_id=123456789)  # TODO: Remplacer par votre App ID

# Fonctions globales
def initialize_steam_real(app_id: int) -> bool:
    """Initialiser le matchmaking Steam réel"""
    global steam_real_matchmaking
    steam_real_matchmaking = SteamRealMatchmaking(app_id)
    return steam_real_matchmaking.initialize()

def start_steam_matchmaking(max_players: int = 2) -> bool:
    """Démarrer le matchmaking Steam"""
    return steam_real_matchmaking.start_matchmaking(max_players)

def stop_steam_matchmaking() -> bool:
    """Arrêter le matchmaking Steam"""
    return steam_real_matchmaking.stop_matchmaking()

def create_steam_lobby(max_players: int = 2, lobby_type: str = "public") -> bool:
    """Créer un lobby Steam"""
    return steam_real_matchmaking.create_lobby(max_players, lobby_type)

def join_steam_lobby(lobby_id: str) -> bool:
    """Rejoindre un lobby Steam"""
    return steam_real_matchmaking.join_lobby(lobby_id)

def set_steam_callback(event_type: str, callback: Callable):
    """Définir un callback Steam"""
    steam_real_matchmaking.set_callback(event_type, callback)

def get_steam_status() -> Dict:
    """Obtenir le statut Steam"""
    return steam_real_matchmaking.get_status()
