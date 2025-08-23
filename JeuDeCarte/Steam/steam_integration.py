#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module d'intégration Steam pour le multijoueur P2P
"""

import os
import sys
import json
import time
import threading
from typing import Optional, Dict, List, Callable

# Simulation de Steamworks (pour le développement)
# En production, remplacer par steamworks.Steamworks()
class SteamworksSimulator:
    """Simulateur Steamworks pour le développement"""
    
    def __init__(self):
        self.initialized = False
        self.app_id = 0
        self.user_id = 0
        self.user_name = "Player"
        self.is_online = True
        
    def initialize(self) -> bool:
        """Initialiser Steam"""
        self.initialized = True
        self.app_id = 123456789  # App ID de test
        self.user_id = int(time.time()) % 1000000
        self.user_name = f"Player_{self.user_id}"
        print(f"[STEAM] Initialisé - App ID: {self.app_id}, User: {self.user_name}")
        return True
    
    def is_steam_running(self) -> bool:
        """Vérifier si Steam est en cours d'exécution"""
        return self.is_online
    
    def get_user_id(self) -> int:
        """Obtenir l'ID utilisateur Steam"""
        return self.user_id
    
    def get_user_name(self) -> str:
        """Obtenir le nom d'utilisateur Steam"""
        return self.user_name

class SteamIntegration:
    """Classe principale d'intégration Steam"""
    
    def __init__(self):
        self.steam = None
        self.initialized = False
        self.callbacks = {}
        
    def initialize(self) -> bool:
        """Initialiser l'intégration Steam"""
        try:
            # Utiliser le simulateur en attendant l'approbation Steam
            # TODO: Remplacer par steamworks.Steamworks() une fois approuvé
            self.steam = SteamworksSimulator()
            
            if self.steam.initialize():
                self.initialized = True
                print("[STEAM] Intégration Steam initialisée avec succès")
                return True
            else:
                print("[STEAM] Erreur: Impossible d'initialiser Steam")
                return False
                
        except Exception as e:
            print(f"[STEAM] Erreur d'initialisation: {e}")
            return False
    
    def is_available(self) -> bool:
        """Vérifier si Steam est disponible"""
        if not self.steam:
            return False
        return self.steam.is_steam_running()
    
    def get_user_info(self) -> Dict[str, any]:
        """Obtenir les informations de l'utilisateur"""
        if not self.initialized:
            return {"name": "Unknown", "id": 0}
        
        return {
            "name": self.steam.get_user_name(),
            "id": self.steam.get_user_id()
        }
    
    def register_callback(self, event_type: str, callback: Callable):
        """Enregistrer un callback pour un événement"""
        self.callbacks[event_type] = callback
    
    def trigger_callback(self, event_type: str, data: any = None):
        """Déclencher un callback"""
        if event_type in self.callbacks:
            try:
                self.callbacks[event_type](data)
            except Exception as e:
                print(f"[STEAM] Erreur callback {event_type}: {e}")

# Instance globale
steam_integration = SteamIntegration()

def initialize_steam() -> bool:
    """Initialiser Steam (fonction globale)"""
    return steam_integration.initialize()

def get_steam_user_info() -> Dict[str, any]:
    """Obtenir les informations utilisateur Steam"""
    return steam_integration.get_user_info()

def is_steam_available() -> bool:
    """Vérifier si Steam est disponible"""
    return steam_integration.is_available() 