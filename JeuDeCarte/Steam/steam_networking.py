#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Système de networking P2P Steam pour la communication entre joueurs
"""

import json
import time
import threading
import queue
from typing import Dict, List, Optional, Callable, Any
from enum import Enum

class MessageType(Enum):
    """Types de messages réseau"""
    GAME_ACTION = "game_action"
    GAME_STATE = "game_state"
    PLAYER_READY = "player_ready"
    GAME_START = "game_start"
    GAME_END = "game_end"
    PING = "ping"
    PONG = "pong"
    CHAT = "chat"

class SteamNetworking:
    """Système de networking P2P Steam"""
    
    def __init__(self):
        self.connections = {}  # {player_id: connection_info}
        self.message_queue = queue.Queue()
        self.callbacks = {}
        self.is_running = False
        self.network_thread = None
        self.last_ping = {}
        self.connection_timeouts = {}
        
    def start(self):
        """Démarrer le système de networking"""
        if self.is_running:
            return
        
        self.is_running = True
        self.network_thread = threading.Thread(target=self._network_loop)
        self.network_thread.daemon = True
        self.network_thread.start()
        
        print("[NETWORKING] Système de networking démarré")
    
    def stop(self):
        """Arrêter le système de networking"""
        self.is_running = False
        if self.network_thread:
            self.network_thread.join(timeout=1.0)
        
        print("[NETWORKING] Système de networking arrêté")
    
    def connect_to_player(self, player_id: int, player_name: str) -> bool:
        """Se connecter à un autre joueur"""
        if player_id in self.connections:
            print(f"[NETWORKING] Déjà connecté à {player_name}")
            return True
        
        # Simuler une connexion P2P
        connection_info = {
            "player_id": player_id,
            "player_name": player_name,
            "connected_at": time.time(),
            "last_message": time.time(),
            "is_connected": True
        }
        
        self.connections[player_id] = connection_info
        self.last_ping[player_id] = time.time()
        
        print(f"[NETWORKING] Connecté à {player_name} (ID: {player_id})")
        self._trigger_callback("player_connected", connection_info)
        
        return True
    
    def disconnect_from_player(self, player_id: int):
        """Se déconnecter d'un joueur"""
        if player_id in self.connections:
            player_name = self.connections[player_id]["player_name"]
            del self.connections[player_id]
            
            if player_id in self.last_ping:
                del self.last_ping[player_id]
            
            print(f"[NETWORKING] Déconnecté de {player_name}")
            self._trigger_callback("player_disconnected", {
                "player_id": player_id,
                "player_name": player_name
            })
    
    def send_message(self, player_id: int, message_type: MessageType, data: Any = None) -> bool:
        """Envoyer un message à un joueur"""
        if player_id not in self.connections:
            print(f"[NETWORKING] Pas connecté au joueur {player_id}")
            return False
        
        message = {
            "type": message_type.value,
            "data": data,
            "timestamp": time.time(),
            "sender_id": self._get_local_player_id()
        }
        
        # Simuler l'envoi de message
        self._simulate_message_send(player_id, message)
        
        return True
    
    def broadcast_message(self, message_type: MessageType, data: Any = None) -> int:
        """Envoyer un message à tous les joueurs connectés"""
        sent_count = 0
        
        for player_id in list(self.connections.keys()):
            if self.send_message(player_id, message_type, data):
                sent_count += 1
        
        return sent_count
    
    def send_game_action(self, player_id: int, action: Dict) -> bool:
        """Envoyer une action de jeu"""
        return self.send_message(player_id, MessageType.GAME_ACTION, action)
    
    def send_game_state(self, player_id: int, game_state: Dict) -> bool:
        """Envoyer l'état du jeu"""
        return self.send_message(player_id, MessageType.GAME_STATE, game_state)
    
    def send_chat_message(self, player_id: int, message: str) -> bool:
        """Envoyer un message de chat"""
        return self.send_message(player_id, MessageType.CHAT, {
            "message": message,
            "timestamp": time.time()
        })
    
    def get_connected_players(self) -> List[Dict]:
        """Obtenir la liste des joueurs connectés"""
        return list(self.connections.values())
    
    def is_connected_to(self, player_id: int) -> bool:
        """Vérifier si connecté à un joueur"""
        return player_id in self.connections
    
    def register_callback(self, event_type: str, callback: Callable):
        """Enregistrer un callback pour un événement"""
        self.callbacks[event_type] = callback
    
    def _network_loop(self):
        """Boucle principale du networking"""
        while self.is_running:
            try:
                # Traiter les messages en attente
                self._process_message_queue()
                
                # Envoyer des pings pour maintenir les connexions
                self._send_pings()
                
                # Vérifier les timeouts de connexion
                self._check_connection_timeouts()
                
                time.sleep(0.1)  # 10 FPS pour le networking
                
            except Exception as e:
                print(f"[NETWORKING] Erreur dans la boucle réseau: {e}")
    
    def _process_message_queue(self):
        """Traiter la queue de messages"""
        try:
            while not self.message_queue.empty():
                message_data = self.message_queue.get_nowait()
                self._handle_message(message_data)
        except queue.Empty:
            pass
    
    def _handle_message(self, message_data: Dict):
        """Traiter un message reçu"""
        try:
            message_type = message_data.get("type")
            sender_id = message_data.get("sender_id")
            data = message_data.get("data")
            timestamp = message_data.get("timestamp", time.time())
            
            # Mettre à jour le timestamp de dernière activité
            if sender_id in self.connections:
                self.connections[sender_id]["last_message"] = timestamp
            
            # Traiter selon le type de message
            if message_type == MessageType.PING.value:
                self._handle_ping(sender_id)
            elif message_type == MessageType.PONG.value:
                self._handle_pong(sender_id)
            elif message_type == MessageType.GAME_ACTION.value:
                self._trigger_callback("game_action_received", {
                    "sender_id": sender_id,
                    "action": data
                })
            elif message_type == MessageType.GAME_STATE.value:
                self._trigger_callback("game_state_received", {
                    "sender_id": sender_id,
                    "state": data
                })
            elif message_type == MessageType.CHAT.value:
                self._trigger_callback("chat_message_received", {
                    "sender_id": sender_id,
                    "message": data
                })
            else:
                print(f"[NETWORKING] Type de message inconnu: {message_type}")
                
        except Exception as e:
            print(f"[NETWORKING] Erreur traitement message: {e}")
    
    def _handle_ping(self, sender_id: int):
        """Traiter un ping"""
        # Répondre avec un pong
        self.send_message(sender_id, MessageType.PONG)
    
    def _handle_pong(self, sender_id: int):
        """Traiter un pong"""
        # Mettre à jour le timestamp de ping
        if sender_id in self.last_ping:
            self.last_ping[sender_id] = time.time()
    
    def _send_pings(self):
        """Envoyer des pings aux joueurs connectés"""
        current_time = time.time()
        
        for player_id in list(self.connections.keys()):
            if current_time - self.last_ping.get(player_id, 0) > 5.0:  # Ping toutes les 5 secondes
                self.send_message(player_id, MessageType.PING)
                self.last_ping[player_id] = current_time
    
    def _check_connection_timeouts(self):
        """Vérifier les timeouts de connexion"""
        current_time = time.time()
        timeout_duration = 30.0  # 30 secondes de timeout
        
        for player_id in list(self.connections.keys()):
            last_message = self.connections[player_id]["last_message"]
            if current_time - last_message > timeout_duration:
                print(f"[NETWORKING] Timeout de connexion pour le joueur {player_id}")
                self.disconnect_from_player(player_id)
    
    def _simulate_message_send(self, player_id: int, message: Dict):
        """Simuler l'envoi d'un message (pour le développement)"""
        # En production, utiliser Steam P2P
        # self.steam.networking.send_p2p_packet(player_id, json.dumps(message))
        
        # Pour le développement, simuler la réception
        time.sleep(0.01)  # Simuler la latence réseau
        
        # Ajouter le message à la queue de réception
        self.message_queue.put(message)
    
    def _get_local_player_id(self) -> int:
        """Obtenir l'ID du joueur local"""
        # En production, utiliser Steam
        # return self.steam.get_user_id()
        return 12345  # ID de test
    
    def _trigger_callback(self, event_type: str, data: Any = None):
        """Déclencher un callback"""
        if event_type in self.callbacks:
            try:
                self.callbacks[event_type](data)
            except Exception as e:
                print(f"[NETWORKING] Erreur callback {event_type}: {e}")

# Instance globale
steam_networking = SteamNetworking()

def start_networking():
    """Démarrer le networking (fonction globale)"""
    steam_networking.start()

def stop_networking():
    """Arrêter le networking (fonction globale)"""
    steam_networking.stop()

def connect_to_player(player_id: int, player_name: str) -> bool:
    """Se connecter à un joueur (fonction globale)"""
    return steam_networking.connect_to_player(player_id, player_name)

def send_game_action(player_id: int, action: Dict) -> bool:
    """Envoyer une action de jeu (fonction globale)"""
    return steam_networking.send_game_action(player_id, action)

def broadcast_game_state(game_state: Dict) -> int:
    """Diffuser l'état du jeu (fonction globale)"""
    return steam_networking.broadcast_message(MessageType.GAME_STATE, game_state) 