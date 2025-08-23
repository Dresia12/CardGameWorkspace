#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module de synchronisation multijoueur pour le combat
"""

import json
import time
import threading
import requests
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum

class ActionType(Enum):
    """Types d'actions possibles dans le combat"""
    PLAY_CARD = "play_card"
    USE_ABILITY = "use_ability"
    END_TURN = "end_turn"
    SURRENDER = "surrender"

@dataclass
class GameAction:
    """Représente une action de jeu"""
    action_type: ActionType
    player_id: str
    data: Dict
    timestamp: float
    action_id: str

class MultiplayerSync:
    """Gestionnaire de synchronisation multijoueur"""
    
    def __init__(self, server_url: str = "http://localhost:5000"):
        self.server_url = server_url
        self.match_id: Optional[str] = None
        self.player_id: Optional[str] = None
        self.opponent_id: Optional[str] = None
        self.is_host: bool = False
        self.game_started: bool = False
        self.current_turn: int = 1
        self.is_my_turn: bool = False
        
        # Callbacks
        self.on_action_received: Optional[Callable[[GameAction], None]] = None
        self.on_turn_changed: Optional[Callable[[bool], None]] = None
        self.on_game_started: Optional[Callable[[], None]] = None
        self.on_game_ended: Optional[Callable[[Dict], None]] = None
        
        # Thread de synchronisation
        self.sync_thread: Optional[threading.Thread] = None
        self.sync_running: bool = False
        self.last_sync_time: float = 0
        self.sync_interval: float = 0.5  # 500ms
        
        # Cache des actions
        self.processed_actions: set = set()
        self.pending_actions: List[GameAction] = []
        
        print(f"[MULTIPLAYER] Initialisé avec serveur: {server_url}")
    
    def initialize_game(self, match_id: str, player_id: str, deck_data: Dict) -> bool:
        """Initialiser le jeu multijoueur"""
        try:
            self.match_id = match_id
            self.player_id = player_id
            
            # Envoyer les données du deck au serveur
            response = requests.post(f"{self.server_url}/api/game/initialize", json={
                "match_id": match_id,
                "player_id": player_id,
                "deck": deck_data
            }, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.game_started = data.get("game_started", False)
                    if self.game_started and self.on_game_started:
                        self.on_game_started()
                    
                    # Démarrer la synchronisation
                    self.start_sync()
                    
                    print(f"[MULTIPLAYER] Jeu initialisé pour {player_id}")
                    return True
                else:
                    print(f"[MULTIPLAYER] Erreur d'initialisation: {data.get('error')}")
                    return False
            else:
                print(f"[MULTIPLAYER] Erreur HTTP: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"[MULTIPLAYER] Erreur d'initialisation: {e}")
            return False
    
    def submit_action(self, action_type: ActionType, data: Dict) -> bool:
        """Soumettre une action au serveur"""
        if not self.match_id or not self.player_id:
            print("[MULTIPLAYER] Jeu non initialisé")
            return False
        
        if not self.is_my_turn:
            print("[MULTIPLAYER] Ce n'est pas votre tour")
            return False
        
        try:
            action = {
                "type": action_type.value,
                "data": data
            }
            
            response = requests.post(f"{self.server_url}/api/game/action", json={
                "match_id": self.match_id,
                "player_id": self.player_id,
                "action": action
            }, timeout=5)
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    print(f"[MULTIPLAYER] Action soumise: {action_type.value}")
                    self.is_my_turn = False
                    if self.on_turn_changed:
                        self.on_turn_changed(False)
                    return True
                else:
                    print(f"[MULTIPLAYER] Erreur action: {result.get('error')}")
                    return False
            else:
                print(f"[MULTIPLAYER] Erreur HTTP: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"[MULTIPLAYER] Erreur soumission action: {e}")
            return False
    
    def update_player_state(self, state: Dict) -> bool:
        """Mettre à jour l'état du joueur"""
        if not self.match_id or not self.player_id:
            return False
        
        try:
            response = requests.post(f"{self.server_url}/api/game/update_state", json={
                "match_id": self.match_id,
                "player_id": self.player_id,
                "state": state
            }, timeout=5)
            
            return response.status_code == 200 and response.json().get("success", False)
            
        except Exception as e:
            print(f"[MULTIPLAYER] Erreur mise à jour état: {e}")
            return False
    
    def get_opponent_state(self) -> Optional[Dict]:
        """Obtenir l'état de l'adversaire"""
        if not self.match_id or not self.player_id:
            return None
        
        try:
            response = requests.post(f"{self.server_url}/api/game/opponent_state", json={
                "match_id": self.match_id,
                "player_id": self.player_id
            }, timeout=5)
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    return result.get("opponent_state")
            
            return None
            
        except Exception as e:
            print(f"[MULTIPLAYER] Erreur récupération état adversaire: {e}")
            return None

    def get_opponent_deck(self) -> Optional[Dict]:
        """Obtenir le deck de l'adversaire si disponible"""
        if not self.match_id or not self.player_id:
            return None
        try:
            response = requests.post(f"{self.server_url}/api/game/opponent_deck", json={
                "match_id": self.match_id,
                "player_id": self.player_id
            }, timeout=5)
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    return result.get("opponent_deck")
            return None
        except Exception as e:
            print(f"[MULTIPLAYER] Erreur récupération deck adversaire: {e}")
            return None
    
    def start_sync(self):
        """Démarrer la synchronisation"""
        if self.sync_running:
            return
        
        self.sync_running = True
        self.sync_thread = threading.Thread(target=self._sync_loop)
        self.sync_thread.daemon = True
        self.sync_thread.start()
        print("[MULTIPLAYER] Synchronisation démarrée")
    
    def stop_sync(self):
        """Arrêter la synchronisation"""
        self.sync_running = False
        if self.sync_thread:
            self.sync_thread.join(timeout=1)
        print("[MULTIPLAYER] Synchronisation arrêtée")
    
    def _sync_loop(self):
        """Boucle de synchronisation"""
        while self.sync_running:
            try:
                self._sync_game_state()
                time.sleep(self.sync_interval)
            except Exception as e:
                print(f"[MULTIPLAYER] Erreur synchronisation: {e}")
                time.sleep(self.sync_interval)
    
    def _sync_game_state(self):
        """Synchroniser l'état du jeu"""
        if not self.match_id or not self.player_id:
            return
        
        try:
            response = requests.post(f"{self.server_url}/api/game/state", json={
                "match_id": self.match_id,
                "player_id": self.player_id
            }, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self._process_game_state(data)
            
        except Exception as e:
            print(f"[MULTIPLAYER] Erreur sync état: {e}")
    
    def _process_game_state(self, data: Dict):
        """Traiter l'état du jeu reçu"""
        game_state = data.get("game_state", {})
        recent_actions = data.get("recent_actions", [])
        is_my_turn = data.get("is_my_turn", False)
        
        # Traiter les nouvelles actions
        for action_data in recent_actions:
            action_id = action_data.get("action_id")
            if action_id not in self.processed_actions:
                self._process_action(action_data)
                self.processed_actions.add(action_id)
        
        # Vérifier les changements de tour
        if is_my_turn != self.is_my_turn:
            self.is_my_turn = is_my_turn
            if self.on_turn_changed:
                self.on_turn_changed(is_my_turn)
        
        # Vérifier si le jeu a démarré
        if game_state.get("game_started") and not self.game_started:
            self.game_started = True
            if self.on_game_started:
                self.on_game_started()

        # Détecter une fin de partie signalée par le serveur
        if game_state.get("status") == "finished":
            # Éviter les callbacks multiples
            if hasattr(self, "_game_ended_emitted") and self._game_ended_emitted:
                return
            self._game_ended_emitted = True
            if self.on_game_ended:
                self.on_game_ended(game_state.get("result", {}))
    
    def _process_action(self, action_data: Dict):
        """Traiter une action reçue"""
        try:
            action = GameAction(
                action_type=ActionType(action_data["action"]["type"]),
                player_id=action_data["player_id"],
                data=action_data["action"]["data"],
                timestamp=action_data["timestamp"],
                action_id=action_data["action_id"]
            )
            
            # Ne pas traiter nos propres actions
            if action.player_id == self.player_id:
                return
            
            print(f"[MULTIPLAYER] Action reçue: {action.action_type.value} de {action.player_id}")
            
            # Appeler le callback
            if self.on_action_received:
                self.on_action_received(action)
                
        except Exception as e:
            print(f"[MULTIPLAYER] Erreur traitement action: {e}")
    
    def end_game(self, result: Dict) -> bool:
        """Terminer le jeu"""
        if not self.match_id or not self.player_id:
            return False
        
        try:
            response = requests.post(f"{self.server_url}/api/game/end", json={
                "match_id": self.match_id,
                "player_id": self.player_id,
                "result": result
            }, timeout=5)
            
            if response.status_code == 200:
                self.stop_sync()
                if self.on_game_ended:
                    self.on_game_ended(result)
                return True
            
            return False
            
        except Exception as e:
            print(f"[MULTIPLAYER] Erreur fin de jeu: {e}")
            return False
    
    def is_connected(self) -> bool:
        """Vérifier la connexion au serveur"""
        try:
            response = requests.get(f"{self.server_url}/api/matchmaking/status", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def get_connection_info(self) -> Dict:
        """Obtenir les informations de connexion"""
        return {
            "server_url": self.server_url,
            "match_id": self.match_id,
            "player_id": self.player_id,
            "game_started": self.game_started,
            "is_my_turn": self.is_my_turn,
            "connected": self.is_connected()
        }
