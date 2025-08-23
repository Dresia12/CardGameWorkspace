#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Système de matchmaking Steam pour trouver des parties
"""

import json
import time
import threading
import os
from typing import Dict, List, Optional, Callable
from enum import Enum

class LobbyType(Enum):
    """Types de lobby Steam"""
    PRIVATE = 0
    FRIENDS_ONLY = 1
    PUBLIC = 2

class LobbyState(Enum):
    """États d'un lobby"""
    CREATING = "creating"
    WAITING = "waiting"
    READY = "ready"
    IN_GAME = "in_game"
    FINISHED = "finished"

class MatchmakingState(Enum):
    """États du matchmaking"""
    IDLE = "idle"
    SEARCHING = "searching"
    MATCHED = "matched"
    CONNECTING = "connecting"
    READY = "ready"

class SteamLobby:
    """Représente un lobby Steam"""
    
    def __init__(self, lobby_id: str, owner_id: int, lobby_type: LobbyType):
        self.lobby_id = lobby_id
        self.owner_id = owner_id
        self.lobby_type = lobby_type
        self.players = []
        self.max_players = 2
        self.state = LobbyState.CREATING
        self.created_at = time.time()
        self.game_data = {}
        
    def add_player(self, player_id: int, player_name: str):
        """Ajouter un joueur au lobby"""
        if len(self.players) < self.max_players:
            player_info = {
                "id": player_id,
                "name": player_name,
                "joined_at": time.time()
            }
            self.players.append(player_info)
            
            if len(self.players) == self.max_players:
                self.state = LobbyState.READY
            else:
                self.state = LobbyState.WAITING
                
            return True
        return False
    
    def remove_player(self, player_id: int):
        """Retirer un joueur du lobby"""
        self.players = [p for p in self.players if p["id"] != player_id]
        
        if len(self.players) == 0:
            self.state = LobbyState.FINISHED
        elif len(self.players) < self.max_players:
            self.state = LobbyState.WAITING
    
    def to_dict(self) -> Dict:
        """Convertir le lobby en dictionnaire"""
        return {
            "lobby_id": self.lobby_id,
            "owner_id": self.owner_id,
            "lobby_type": self.lobby_type.value,
            "players": self.players,
            "max_players": self.max_players,
            "state": self.state.value,
            "created_at": self.created_at,
            "game_data": self.game_data
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'SteamLobby':
        """Créer un lobby à partir d'un dictionnaire"""
        lobby = cls(data["lobby_id"], data["owner_id"], LobbyType(data["lobby_type"]))
        lobby.players = data["players"]
        lobby.max_players = data["max_players"]
        lobby.state = LobbyState(data["state"])
        lobby.created_at = data["created_at"]
        lobby.game_data = data.get("game_data", {})
        return lobby

class MatchmakingQueue:
    """File d'attente pour le matchmaking automatique"""
    
    def __init__(self):
        self.queue = []  # Liste des joueurs en attente
        self.matched_pairs = []  # Paires de joueurs matchés
        self.lock = threading.Lock()
        self.is_running = False
        self.matchmaking_thread = None
        
    def add_player(self, player_id: int, player_name: str, rank: int = 0) -> bool:
        """Ajouter un joueur à la file d'attente"""
        with self.lock:
            # Vérifier si le joueur n'est pas déjà en queue
            for player in self.queue:
                if player["id"] == player_id:
                    return True  # Déjà en queue
            
            player_info = {
                "id": player_id,
                "name": player_name,
                "rank": rank,
                "joined_at": time.time()
            }
            
            self.queue.append(player_info)
            print(f"[MATCHMAKING] {player_name} ajouté à la file d'attente")
            
            # Essayer de faire un match immédiatement
            self._try_match()
            
            return True
    
    def remove_player(self, player_id: int) -> bool:
        """Retirer un joueur de la file d'attente"""
        with self.lock:
            for i, player in enumerate(self.queue):
                if player["id"] == player_id:
                    removed_player = self.queue.pop(i)
                    print(f"[MATCHMAKING] {removed_player['name']} retiré de la file d'attente")
                    return True
            return False
    
    def _try_match(self):
        """Essayer de faire un match avec les joueurs en queue"""
        if len(self.queue) >= 2:
            # Prendre les 2 premiers joueurs
            player1 = self.queue.pop(0)
            player2 = self.queue.pop(0)
            
            # Créer une paire matchée
            match_pair = {
                "player1": player1,
                "player2": player2,
                "matched_at": time.time(),
                "match_id": f"match_{int(time.time() * 1000)}"
            }
            
            self.matched_pairs.append(match_pair)
            
            print(f"[MATCHMAKING] Match créé: {player1['name']} vs {player2['name']}")
            
            # Déclencher le callback de match
            if hasattr(self, 'match_callback') and self.match_callback:
                self.match_callback(match_pair)
    
    def get_queue_status(self) -> Dict:
        """Obtenir le statut de la file d'attente"""
        with self.lock:
            return {
                "queue_length": len(self.queue),
                "estimated_wait_time": len(self.queue) * 30,  # 30 secondes par joueur en queue
                "players_in_queue": [p["name"] for p in self.queue]
            }
    
    def start(self):
        """Démarrer le système de matchmaking"""
        if self.is_running:
            return
        
        self.is_running = True
        self.matchmaking_thread = threading.Thread(target=self._matchmaking_loop)
        self.matchmaking_thread.daemon = True
        self.matchmaking_thread.start()
        
        print("[MATCHMAKING] Système de matchmaking automatique démarré")
    
    def stop(self):
        """Arrêter le système de matchmaking"""
        self.is_running = False
        if self.matchmaking_thread:
            self.matchmaking_thread.join(timeout=1.0)
        
        print("[MATCHMAKING] Système de matchmaking arrêté")
    
    def _matchmaking_loop(self):
        """Boucle principale du matchmaking"""
        while self.is_running:
            try:
                with self.lock:
                    # Nettoyer les anciens matchs
                    current_time = time.time()
                    self.matched_pairs = [pair for pair in self.matched_pairs 
                                        if current_time - pair["matched_at"] < 60]  # 60 secondes max
                
                time.sleep(1)  # Vérifier toutes les secondes
                
            except Exception as e:
                print(f"[MATCHMAKING] Erreur dans la boucle: {e}")
                time.sleep(5)
    
    def set_match_callback(self, callback: Callable):
        """Définir le callback pour les matches créés"""
        self.match_callback = callback

class SteamMatchmaking:
    """Système de matchmaking Steam"""
    
    def __init__(self):
        self.lobbies = {}  # {lobby_id: SteamLobby}
        self.user_lobbies = {}  # {user_id: lobby_id}
        self.callbacks = {}
        self.search_results = []
        self.lock = threading.Lock()
        
        # Système de matchmaking automatique
        self.matchmaking_queue = MatchmakingQueue()
        self.matchmaking_queue.set_match_callback(self._on_match_created)
        
        # Charger les lobbies existants
        self._load_lobbies()
        
        # Démarrer le matchmaking automatique
        self.matchmaking_queue.start()
    
    def _on_match_created(self, match_pair: Dict):
        """Callback appelé quand un match est créé"""
        print(f"[MATCHMAKING] Match créé automatiquement: {match_pair['match_id']}")
        
        # Créer un lobby pour ce match
        lobby_id = self._create_match_lobby(match_pair)
        
        if lobby_id:
            # Notifier les joueurs
            self._trigger_callback("match_found", {
                "match_id": match_pair["match_id"],
                "lobby_id": lobby_id,
                "player1": match_pair["player1"],
                "player2": match_pair["player2"]
            })
    
    def _create_match_lobby(self, match_pair: Dict) -> Optional[str]:
        """Créer un lobby pour un match automatique"""
        lobby_id = f"match_{int(time.time() * 1000)}"
        
        # Créer le lobby
        lobby = SteamLobby(lobby_id, match_pair["player1"]["id"], LobbyType.PUBLIC)
        lobby.max_players = 2
        lobby.state = LobbyState.READY  # Directement prêt
        
        # Ajouter les joueurs
        lobby.add_player(match_pair["player1"]["id"], match_pair["player1"]["name"])
        lobby.add_player(match_pair["player2"]["id"], match_pair["player2"]["name"])
        
        # Enregistrer le lobby
        self.lobbies[lobby_id] = lobby
        self.user_lobbies[match_pair["player1"]["id"]] = lobby_id
        self.user_lobbies[match_pair["player2"]["id"]] = lobby_id
        
        print(f"[MATCHMAKING] Lobby de match créé: {lobby_id}")
        return lobby_id
    
    def start_matchmaking(self, player_id: int, player_name: str, rank: int = 0) -> bool:
        """Démarrer le matchmaking automatique pour un joueur"""
        return self.matchmaking_queue.add_player(player_id, player_name, rank)
    
    def stop_matchmaking(self, player_id: int) -> bool:
        """Arrêter le matchmaking automatique pour un joueur"""
        return self.matchmaking_queue.remove_player(player_id)
    
    def get_matchmaking_status(self) -> Dict:
        """Obtenir le statut du matchmaking"""
        return self.matchmaking_queue.get_queue_status()
    
    def _load_lobbies(self):
        """Charger les lobbies depuis le fichier de persistance"""
        try:
            if os.path.exists(self.persistence_file):
                with open(self.persistence_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                for lobby_data in data.get("lobbies", []):
                    lobby = SteamLobby.from_dict(lobby_data)
                    self.lobbies[lobby.lobby_id] = lobby
                    
                    # Reconstruire user_lobbies
                    for player in lobby.players:
                        self.user_lobbies[player["id"]] = lobby.lobby_id
                        
                print(f"[MATCHMAKING] {len(self.lobbies)} lobbies chargés depuis le fichier")
        except Exception as e:
            print(f"[MATCHMAKING] Erreur lors du chargement des lobbies: {e}")
    
    def _save_lobbies(self):
        """Sauvegarder les lobbies dans le fichier de persistance"""
        try:
            data = {
                "lobbies": [lobby.to_dict() for lobby in self.lobbies.values()],
                "timestamp": time.time()
            }
            
            with open(self.persistence_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            print(f"[MATCHMAKING] Erreur lors de la sauvegarde des lobbies: {e}")
    
    def _cleanup_old_lobbies(self):
        """Nettoyer les lobbies trop anciens ou vides"""
        current_time = time.time()
        to_remove = []
        
        for lobby_id, lobby in self.lobbies.items():
            # Supprimer les lobbies de plus de 30 minutes
            if current_time - lobby.created_at > 1800:
                to_remove.append(lobby_id)
                print(f"[MATCHMAKING] Lobby ancien supprimé: {lobby_id}")
            # Supprimer les lobbies vides (0 joueurs) ET terminés
            elif len(lobby.players) == 0 and lobby.state == LobbyState.FINISHED:
                to_remove.append(lobby_id)
                print(f"[MATCHMAKING] Lobby vide et terminé supprimé: {lobby_id}")
            # Supprimer les lobbies terminés
            elif lobby.state == LobbyState.FINISHED:
                to_remove.append(lobby_id)
                print(f"[MATCHMAKING] Lobby terminé supprimé: {lobby_id}")
            # Supprimer les lobbies pleins (READY) de plus de 10 minutes
            elif lobby.state == LobbyState.READY and current_time - lobby.created_at > 600:
                to_remove.append(lobby_id)
                print(f"[MATCHMAKING] Lobby plein ancien supprimé: {lobby_id}")
        
        for lobby_id in to_remove:
            del self.lobbies[lobby_id]
        
        if to_remove:
            self._save_lobbies()
    
    def create_lobby(self, lobby_type: LobbyType = LobbyType.PUBLIC, 
                    max_players: int = 2) -> Optional[str]:
        """Créer un nouveau lobby"""
        with self.lock:
            # Nettoyer les anciens lobbies
            self._cleanup_old_lobbies()
            
            lobby_id = f"lobby_{int(time.time() * 1000)}"
            
            # Simuler l'ID du propriétaire (en production, utiliser Steam)
            owner_id = int(time.time()) % 1000000
            
            lobby = SteamLobby(lobby_id, owner_id, lobby_type)
            lobby.max_players = max_players
            lobby.state = LobbyState.WAITING  # Prêt à recevoir des joueurs
            
            self.lobbies[lobby_id] = lobby
            
            print(f"[MATCHMAKING] Lobby créé: {lobby_id}")
            self._trigger_callback("lobby_created", lobby.to_dict())
            
            # Sauvegarder
            self._save_lobbies()
            
            return lobby_id
    
    def join_lobby(self, lobby_id: str, player_id: int, player_name: str) -> bool:
        """Rejoindre un lobby"""
        with self.lock:
            if lobby_id not in self.lobbies:
                print(f"[MATCHMAKING] Lobby non trouvé: {lobby_id}")
                return False
            
            lobby = self.lobbies[lobby_id]
            
            if lobby.state == LobbyState.FINISHED:
                print(f"[MATCHMAKING] Lobby fermé: {lobby_id}")
                return False
            
            if len(lobby.players) >= lobby.max_players:
                print(f"[MATCHMAKING] Lobby plein: {lobby_id}")
                return False
            
            # Vérifier si le joueur n'est pas déjà dans le lobby
            for player in lobby.players:
                if player["id"] == player_id:
                    print(f"[MATCHMAKING] Joueur déjà dans le lobby: {player_name}")
                    return True  # Considérer comme succès
            
            # Ajouter le joueur
            if lobby.add_player(player_id, player_name):
                self.user_lobbies[player_id] = lobby_id
                
                print(f"[MATCHMAKING] Joueur {player_name} rejoint le lobby {lobby_id}")
                self._trigger_callback("player_joined", {
                    "lobby_id": lobby_id,
                    "player": {"id": player_id, "name": player_name}
                })
                
                # Si le lobby est plein, notifier
                if lobby.state == LobbyState.READY:
                    self._trigger_callback("lobby_ready", lobby.to_dict())
                
                # Sauvegarder
                self._save_lobbies()
                
                return True
            
            return False
    
    def leave_lobby(self, player_id: int) -> bool:
        """Quitter un lobby"""
        with self.lock:
            if player_id not in self.user_lobbies:
                return False
            
            lobby_id = self.user_lobbies[player_id]
            
            if lobby_id in self.lobbies:
                lobby = self.lobbies[lobby_id]
                player_name = None
                
                # Trouver le nom du joueur
                for player in lobby.players:
                    if player["id"] == player_id:
                        player_name = player["name"]
                        break
                
                lobby.remove_player(player_id)
                del self.user_lobbies[player_id]
                
                print(f"[MATCHMAKING] Joueur {player_name} quitte le lobby {lobby_id}")
                self._trigger_callback("player_left", {
                    "lobby_id": lobby_id,
                    "player_id": player_id,
                    "player_name": player_name
                })
                
                # Si le lobby est vide, le supprimer
                if lobby.state == LobbyState.FINISHED:
                    del self.lobbies[lobby_id]
                    print(f"[MATCHMAKING] Lobby supprimé: {lobby_id}")
                
                # Sauvegarder
                self._save_lobbies()
                
                return True
            
            return False
    
    def search_lobbies(self, lobby_type: LobbyType = LobbyType.PUBLIC) -> List[Dict]:
        """Rechercher des lobbies disponibles"""
        with self.lock:
            # Nettoyer les anciens lobbies
            self._cleanup_old_lobbies()
            
            available_lobbies = []
            
            for lobby_id, lobby in self.lobbies.items():
                if (lobby.lobby_type == lobby_type and 
                    lobby.state in [LobbyState.WAITING, LobbyState.READY] and
                    len(lobby.players) < lobby.max_players):
                    
                    lobby_info = lobby.to_dict()
                    lobby_info["available_slots"] = lobby.max_players - len(lobby.players)
                    available_lobbies.append(lobby_info)
            
            self.search_results = available_lobbies
            print(f"[MATCHMAKING] {len(available_lobbies)} lobbies trouvés")
            
            return available_lobbies
    
    def get_lobby_info(self, lobby_id: str) -> Optional[Dict]:
        """Obtenir les informations d'un lobby"""
        with self.lock:
            if lobby_id in self.lobbies:
                return self.lobbies[lobby_id].to_dict()
            return None
    
    def get_user_lobby(self, user_id: int) -> Optional[str]:
        """Obtenir le lobby d'un utilisateur"""
        return self.user_lobbies.get(user_id)
    
    def set_lobby_data(self, lobby_id: str, key: str, value: str):
        """Définir des données de lobby"""
        with self.lock:
            if lobby_id in self.lobbies:
                self.lobbies[lobby_id].game_data[key] = value
                self._save_lobbies()
    
    def get_lobby_data(self, lobby_id: str, key: str) -> Optional[str]:
        """Obtenir des données de lobby"""
        if lobby_id in self.lobbies:
            return self.lobbies[lobby_id].game_data.get(key)
        return None
    
    def register_callback(self, event_type: str, callback: Callable):
        """Enregistrer un callback pour un événement"""
        self.callbacks[event_type] = callback
    
    def _trigger_callback(self, event_type: str, data: any = None):
        """Déclencher un callback"""
        if event_type in self.callbacks:
            try:
                self.callbacks[event_type](data)
            except Exception as e:
                print(f"[MATCHMAKING] Erreur callback {event_type}: {e}")

# Instance globale
steam_matchmaking = SteamMatchmaking()

def create_lobby(lobby_type: LobbyType = LobbyType.PUBLIC, 
                max_players: int = 2) -> Optional[str]:
    """Créer un lobby (fonction globale)"""
    return steam_matchmaking.create_lobby(lobby_type, max_players)

def join_lobby(lobby_id: str, player_id: int, player_name: str) -> bool:
    """Rejoindre un lobby (fonction globale)"""
    return steam_matchmaking.join_lobby(lobby_id, player_id, player_name)

def search_lobbies(lobby_type: LobbyType = LobbyType.PUBLIC) -> List[Dict]:
    """Rechercher des lobbies (fonction globale)"""
    return steam_matchmaking.search_lobbies(lobby_type)

def cleanup_all_lobbies():
    """Nettoyer tous les lobbies (fonction globale)"""
    steam_matchmaking._cleanup_old_lobbies()

# Fonctions pour le matchmaking automatique
def start_matchmaking(player_id: int, player_name: str, rank: int = 0) -> bool:
    """Démarrer le matchmaking automatique (fonction globale)"""
    return steam_matchmaking.start_matchmaking(player_id, player_name, rank)

def stop_matchmaking(player_id: int) -> bool:
    """Arrêter le matchmaking automatique (fonction globale)"""
    return steam_matchmaking.stop_matchmaking(player_id)

def get_matchmaking_status() -> Dict:
    """Obtenir le statut du matchmaking (fonction globale)"""
    return steam_matchmaking.get_matchmaking_status() 