#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Système de matchmaking en ligne qui communique avec le serveur central
"""

import json
import time
import threading
import requests
from typing import Dict, Optional, Callable
from enum import Enum

class MatchmakingState(Enum):
    """États du matchmaking en ligne"""
    IDLE = "idle"
    SEARCHING = "searching"
    MATCHED = "matched"
    CONNECTING = "connecting"
    READY = "ready"

class OnlineMatchmaking:
    """Système de matchmaking en ligne"""
    
    def __init__(self, server_url: str = "http://localhost:5000"):
        self.server_url = server_url
        self.player_id = None
        self.player_name = None
        self.current_state = MatchmakingState.IDLE
        self.polling_thread = None
        self.is_polling = False
        self.callbacks = {}
        
    def start_matchmaking(self, player_id: str, player_name: str, rank: int = 0, region: str = "unknown") -> bool:
        """Démarrer le matchmaking en ligne"""
        print(f"[ONLINE] Début matchmaking pour {player_name} (ID: {player_id})")
        print(f"[ONLINE] URL serveur: {self.server_url}")
        
        if self.current_state != MatchmakingState.IDLE:
            print("[ONLINE] Matchmaking déjà en cours")
            return False
        
        self.player_id = player_id
        self.player_name = player_name
        
        try:
            print(f"[ONLINE] Tentative de connexion au serveur...")
            # Envoyer la requête au serveur
            response = requests.post(f"{self.server_url}/api/matchmaking/join", json={
                "player_id": player_id,
                "player_name": player_name,
                "rank": rank,
                "region": region
            })
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.current_state = MatchmakingState.SEARCHING
                    print(f"[ONLINE] {player_name} en recherche d'adversaire...")
                    
                    # Démarrer le polling
                    self._start_polling()
                    
                    return True
                else:
                    print(f"[ONLINE] Erreur serveur: {data.get('error', 'Unknown error')}")
                    return False
            else:
                print(f"[ONLINE] Erreur HTTP: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"[ONLINE] Erreur de connexion au serveur: {e}")
            return False
    
    def stop_matchmaking(self) -> bool:
        """Arrêter le matchmaking"""
        if self.current_state == MatchmakingState.IDLE:
            return True
        
        # Arrêter le polling
        self._stop_polling()
        
        if self.player_id:
            try:
                # Notifier le serveur
                response = requests.post(f"{self.server_url}/api/matchmaking/leave", json={
                    "player_id": self.player_id
                })
                
                if response.status_code == 200:
                    print(f"[ONLINE] {self.player_name} a quitté la file d'attente")
                else:
                    print(f"[ONLINE] Erreur lors de la déconnexion: {response.status_code}")
                    
            except requests.exceptions.RequestException as e:
                print(f"[ONLINE] Erreur de connexion: {e}")
        
        self.current_state = MatchmakingState.IDLE
        self.player_id = None
        self.player_name = None
        
        return True
    
    def get_status(self) -> Dict:
        """Obtenir le statut du matchmaking"""
        try:
            response = requests.get(f"{self.server_url}/api/matchmaking/status")
            if response.status_code == 200:
                data = response.json()
                return {
                    "state": self.current_state.value,
                    "player_name": self.player_name,
                    "queue_length": data.get("queue_length", 0),
                    "estimated_wait_time": data.get("estimated_wait_time", 0),
                    "players_in_queue": data.get("players_in_queue", [])
                }
            else:
                return {"error": f"HTTP {response.status_code}"}
                
        except requests.exceptions.RequestException as e:
            return {"error": f"Connexion: {e}"}
    
    def _start_polling(self):
        """Démarrer le polling pour vérifier les matches"""
        if self.is_polling:
            return
        
        self.is_polling = True
        self.polling_thread = threading.Thread(target=self._polling_loop)
        self.polling_thread.daemon = True
        self.polling_thread.start()
    
    def _stop_polling(self):
        """Arrêter le polling"""
        self.is_polling = False
        if self.polling_thread:
            self.polling_thread.join(timeout=1.0)
    
    def _polling_loop(self):
        """Boucle de polling pour vérifier les matches"""
        while self.is_polling and self.current_state == MatchmakingState.SEARCHING:
            try:
                if not self.player_id:
                    break
                
                # Vérifier si un match a été trouvé
                response = requests.post(f"{self.server_url}/api/matchmaking/poll", json={
                    "player_id": self.player_id
                })
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("match_found"):
                        match_info = data.get("match")
                        self._on_match_found(match_info)
                        break
                
                # Attendre avant la prochaine vérification (optimisé)
                time.sleep(3)  # Réduire la fréquence de polling
                
            except requests.exceptions.RequestException as e:
                print(f"[ONLINE] Erreur polling: {e}")
                time.sleep(5)
            except Exception as e:
                print(f"[ONLINE] Erreur inattendue: {e}")
                time.sleep(5)
    
    def _on_match_found(self, match_info: Dict):
        """Appelé quand un match est trouvé"""
        print(f"[ONLINE] Match trouvé: {match_info['player1']['name']} vs {match_info['player2']['name']}")
        
        self.current_state = MatchmakingState.MATCHED
        
        # Déclencher le callback
        if "match_found" in self.callbacks:
            try:
                self.callbacks["match_found"](match_info)
            except Exception as e:
                print(f"[ONLINE] Erreur callback match_found: {e}")
    
    def set_callback(self, event_type: str, callback: Callable):
        """Définir un callback pour un événement"""
        self.callbacks[event_type] = callback
    
    def is_connected(self) -> bool:
        """Vérifier si le serveur est accessible"""
        try:
            response = requests.get(f"{self.server_url}/api/matchmaking/status", timeout=5)
            return response.status_code == 200
        except:
            return False

# Instance globale
online_matchmaking = OnlineMatchmaking()

# Fonctions globales pour compatibilité
def start_online_matchmaking(player_id: str, player_name: str, rank: int = 0, region: str = "unknown") -> bool:
    """Démarrer le matchmaking en ligne (fonction globale)"""
    return online_matchmaking.start_matchmaking(player_id, player_name, rank, region)

def stop_online_matchmaking() -> bool:
    """Arrêter le matchmaking en ligne (fonction globale)"""
    return online_matchmaking.stop_matchmaking()

def get_online_matchmaking_status() -> Dict:
    """Obtenir le statut du matchmaking en ligne (fonction globale)"""
    return online_matchmaking.get_status()

def set_online_matchmaking_callback(event_type: str, callback: Callable):
    """Définir un callback pour le matchmaking en ligne (fonction globale)"""
    online_matchmaking.set_callback(event_type, callback)

def is_server_connected() -> bool:
    """Vérifier si le serveur est accessible (fonction globale)"""
    return online_matchmaking.is_connected()
