#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Serveur de matchmaking central pour le jeu multijoueur
"""

import json
import time
import threading
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid

app = Flask(__name__)
CORS(app)  # Permettre les requêtes cross-origin

class MatchmakingServer:
    """Serveur de matchmaking central"""
    
    def __init__(self, db_path: str = "matchmaking.db"):
        self.db_path = db_path
        self.active_players = {}  # {player_id: player_info}
        self.matches = {}  # {match_id: match_info}
        self.match_claimed = {}  # {match_id: set(player_ids)} - pour tracker qui a récupéré le match
        # Utiliser un verrou réentrant pour éviter les deadlocks lorsque
        # des méthodes appelées sous lock ré-acquièrent le même lock
        self.lock = threading.RLock()
        
        # Nouvelles structures pour la synchronisation de combat
        self.active_games = {}  # {match_id: game_state}
        self.game_actions = {}  # {match_id: [action1, action2, ...]}
        self.player_states = {}  # {match_id: {player_id: state}}
        self.action_locks = {}  # {match_id: threading.Lock()}
        
        # Initialiser la base de données
        self._init_database()
        
        # Démarrer le thread de nettoyage
        self.cleanup_thread = threading.Thread(target=self._cleanup_loop)
        self.cleanup_thread.daemon = True
        self.cleanup_thread.start()
    
    def _init_database(self):
        """Initialiser la base de données"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS players (
                    player_id TEXT PRIMARY KEY,
                    player_name TEXT NOT NULL,
                    rank INTEGER DEFAULT 0,
                    region TEXT DEFAULT 'unknown',
                    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS matches (
                    match_id TEXT PRIMARY KEY,
                    player1_id TEXT NOT NULL,
                    player2_id TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'pending',
                    lobby_id TEXT
                )
            """)
            
            conn.commit()
    
    def add_player(self, player_id: str, player_name: str, rank: int = 0, region: str = "unknown") -> bool:
        """Ajouter un joueur à la file d'attente"""
        with self.lock:
            # Vérifier si le joueur n'est pas déjà en queue
            if player_id in self.active_players:
                self.active_players[player_id]["last_seen"] = time.time()
                return True
            
            player_info = {
                "id": player_id,
                "name": player_name,
                "rank": rank,
                "region": region,
                "joined_at": time.time(),
                "last_seen": time.time()
            }
            
            self.active_players[player_id] = player_info
            
            # Sauvegarder en base
            self._save_player(player_info)
            
            print(f"[SERVER] {player_name} ajouté à la file d'attente (total: {len(self.active_players)})")
            
            # Si on a 2 vrais joueurs, faire un match immédiatement
            if len(self.active_players) >= 2:
                match_result = self._try_match()
                if match_result:
                    print(f"[SERVER] Match créé immédiatement pour {player_name}")
                else:
                    print(f"[SERVER] En attente d'un adversaire pour {player_name}")
            else:
                print(f"[SERVER] {player_name} en attente d'un adversaire...")
            
            return True
    
    def remove_player(self, player_id: str) -> bool:
        """Retirer un joueur de la file d'attente"""
        with self.lock:
            if player_id in self.active_players:
                player_name = self.active_players[player_id]["name"]
                del self.active_players[player_id]
                
                # Marquer comme inactif en base
                self._deactivate_player(player_id)
                
                print(f"[SERVER] {player_name} retiré de la file d'attente")
                return True
            return False
    
    def _try_match(self) -> Optional[Dict]:
        """Essayer de faire un match avec les joueurs en queue"""
        if len(self.active_players) >= 2:
            # Prendre les 2 premiers joueurs (FIFO)
            players = list(self.active_players.values())
            player1 = players[0]
            player2 = players[1]
            
            # Vérifier que les joueurs sont toujours actifs
            if player1["id"] not in self.active_players or player2["id"] not in self.active_players:
                print(f"[SERVER] Un des joueurs n'est plus disponible pour le match")
                return None
            
            # Créer le match
            match_id = str(uuid.uuid4())
            match_info = {
                "match_id": match_id,
                "player1": player1,
                "player2": player2,
                "created_at": time.time(),
                "status": "pending"
            }
            
            # Retirer les joueurs de la queue
            del self.active_players[player1["id"]]
            del self.active_players[player2["id"]]
            
            # Sauvegarder le match
            self.matches[match_id] = match_info
            self.match_claimed[match_id] = set()  # Aucun joueur n'a encore récupéré le match
            
            # Initialiser les structures de synchronisation pour ce match
            self.active_games[match_id] = {
                "status": "initializing",
                "current_turn": 1,
                "current_player": player1["id"],
                "game_started": False,
                "last_action_time": time.time()
            }
            self.game_actions[match_id] = []
            self.player_states[match_id] = {
                player1["id"]: {"ready": False, "deck": None, "last_seen": time.time()},
                player2["id"]: {"ready": False, "deck": None, "last_seen": time.time()}
            }
            self.action_locks[match_id] = threading.Lock()
            
            self._save_match(match_info)
            
            print(f"[SERVER] Match créé: {player1['name']} vs {player2['name']} (ID: {match_id})")
            
            return match_info
        
        return None

    # === NOUVELLES MÉTHODES POUR LA SYNCHRONISATION DE COMBAT ===
    
    def initialize_game(self, match_id: str, player_id: str, deck_data: Dict) -> Dict:
        """Initialiser le jeu pour un joueur"""
        with self.action_locks.get(match_id, threading.Lock()):
            if match_id not in self.active_games:
                return {"error": "Match introuvable"}
            
            # Convertir player_id en int pour correspondre au format stocké
            try:
                player_id_int = int(player_id)
            except ValueError:
                return {"error": "ID de joueur invalide"}
            
            if player_id_int not in self.player_states[match_id]:
                return {"error": "Joueur non autorisé"}
            
            # Marquer le joueur comme prêt
            self.player_states[match_id][player_id_int]["ready"] = True
            self.player_states[match_id][player_id_int]["deck"] = deck_data
            self.player_states[match_id][player_id_int]["last_seen"] = time.time()
            
            print(f"[GAME] Joueur {player_id_int} prêt pour le match {match_id}")
            
            # Vérifier si les deux joueurs sont prêts
            both_ready = all(state["ready"] for state in self.player_states[match_id].values())
            
            if both_ready:
                self.active_games[match_id]["status"] = "active"
                self.active_games[match_id]["game_started"] = True
                self.active_games[match_id]["last_action_time"] = time.time()
                print(f"[GAME] Match {match_id} démarré !")
            
            return {
                "success": True,
                "game_started": both_ready,
                "game_state": self.active_games[match_id]
            }
    
    def submit_action(self, match_id: str, player_id: str, action: Dict) -> Dict:
        """Soumettre une action de combat"""
        with self.action_locks.get(match_id, threading.Lock()):
            if match_id not in self.active_games:
                return {"error": "Match introuvable"}
            
            if self.active_games[match_id]["status"] != "active":
                return {"error": "Jeu non actif"}
            
            # Convertir player_id en int
            try:
                player_id_int = int(player_id)
            except ValueError:
                return {"error": "ID de joueur invalide"}
            
            # Vérifier que c'est le tour du joueur
            if self.active_games[match_id]["current_player"] != player_id_int:
                return {"error": "Ce n'est pas votre tour"}
            
            # Ajouter l'action à la liste
            action_with_metadata = {
                "action": action,
                "player_id": player_id_int,
                "timestamp": time.time(),
                "action_id": str(uuid.uuid4())
            }
            
            self.game_actions[match_id].append(action_with_metadata)
            self.active_games[match_id]["last_action_time"] = time.time()
            
            # Changer de joueur
            players = list(self.player_states[match_id].keys())
            current_index = players.index(player_id_int)
            next_index = (current_index + 1) % len(players)
            self.active_games[match_id]["current_player"] = players[next_index]
            self.active_games[match_id]["current_turn"] += 1
            
            print(f"[GAME] Action soumise par {player_id_int} dans le match {match_id}")
            
            return {
                "success": True,
                "action_id": action_with_metadata["action_id"],
                "next_player": self.active_games[match_id]["current_player"]
            }
    
    def get_game_state(self, match_id: str, player_id: str) -> Dict:
        """Obtenir l'état actuel du jeu"""
        with self.action_locks.get(match_id, threading.Lock()):
            if match_id not in self.active_games:
                return {"error": "Match introuvable"}
            
            # Convertir player_id en int
            try:
                player_id_int = int(player_id)
            except ValueError:
                return {"error": "ID de joueur invalide"}
            
            if player_id_int not in self.player_states[match_id]:
                return {"error": "Joueur non autorisé"}
            
            # Mettre à jour le timestamp de dernière vue
            self.player_states[match_id][player_id_int]["last_seen"] = time.time()
            
            # Obtenir les actions depuis la dernière fois
            # (pour l'instant, on renvoie toutes les actions)
            recent_actions = self.game_actions[match_id]
            
            return {
                "success": True,
                "game_state": self.active_games[match_id],
                "recent_actions": recent_actions,
                "is_my_turn": self.active_games[match_id]["current_player"] == player_id_int
            }
    
    def update_player_state(self, match_id: str, player_id: str, state: Dict) -> Dict:
        """Mettre à jour l'état d'un joueur (vies, mana, etc.)"""
        with self.action_locks.get(match_id, threading.Lock()):
            if match_id not in self.active_games:
                return {"error": "Match introuvable"}
            
            # Convertir player_id en int
            try:
                player_id_int = int(player_id)
            except ValueError:
                return {"error": "ID de joueur invalide"}
            
            if player_id_int not in self.player_states[match_id]:
                return {"error": "Joueur non autorisé"}
            
            # Mettre à jour l'état du joueur
            self.player_states[match_id][player_id_int].update(state)
            self.player_states[match_id][player_id_int]["last_seen"] = time.time()
            
            return {"success": True}
    
    def get_opponent_state(self, match_id: str, player_id: str) -> Dict:
        """Obtenir l'état de l'adversaire"""
        with self.action_locks.get(match_id, threading.Lock()):
            if match_id not in self.active_games:
                return {"error": "Match introuvable"}
            
            # Convertir player_id en int
            try:
                player_id_int = int(player_id)
            except ValueError:
                return {"error": "ID de joueur invalide"}
            
            if player_id_int not in self.player_states[match_id]:
                return {"error": "Joueur non autorisé"}
            
            # Trouver l'adversaire
            opponent_id = None
            for pid in self.player_states[match_id].keys():
                if pid != player_id_int:
                    opponent_id = pid
                    break
            
            if not opponent_id:
                return {"error": "Adversaire introuvable"}
            
            opponent_state = self.player_states[match_id][opponent_id].copy()
            # Ne pas renvoyer les informations sensibles comme le deck
            if "deck" in opponent_state:
                del opponent_state["deck"]
            
            return {
                "success": True,
                "opponent_state": opponent_state
            }

    def get_opponent_deck(self, match_id: str, player_id: str) -> Dict:
        """Obtenir le deck de l'adversaire (autorisé uniquement si les deux joueurs sont prêts)."""
        with self.action_locks.get(match_id, threading.Lock()):
            if match_id not in self.active_games:
                return {"error": "Match introuvable"}
            # Convertir l'ID
            try:
                player_id_int = int(player_id)
            except ValueError:
                return {"error": "ID de joueur invalide"}
            if player_id_int not in self.player_states[match_id]:
                return {"error": "Joueur non autorisé"}
            # Vérifier que les deux joueurs sont prêts et que les decks existent
            both_ready = all(state.get("ready") and state.get("deck") is not None for state in self.player_states[match_id].values())
            if not both_ready:
                return {"error": "Deck indisponible"}
            # Trouver l'adversaire
            opponent_id = None
            for pid in self.player_states[match_id].keys():
                if pid != player_id_int:
                    opponent_id = pid
                    break
            if opponent_id is None:
                return {"error": "Adversaire introuvable"}
            opponent_deck = self.player_states[match_id][opponent_id].get("deck")
            if not opponent_deck:
                return {"error": "Deck indisponible"}
            return {"success": True, "opponent_deck": opponent_deck}
    
    def end_game(self, match_id: str, player_id: str, result: Dict) -> Dict:
        """Terminer le jeu"""
        with self.action_locks.get(match_id, threading.Lock()):
            if match_id not in self.active_games:
                return {"error": "Match introuvable"}
            
            self.active_games[match_id]["status"] = "finished"
            self.active_games[match_id]["result"] = result
            self.active_games[match_id]["ended_by"] = player_id
            self.active_games[match_id]["end_time"] = time.time()
            
            print(f"[GAME] Match {match_id} terminé par {player_id}")
            
            return {"success": True}
    
    def cleanup_game(self, match_id: str):
        """Nettoyer les données d'un jeu terminé"""
        with self.lock:
            if match_id in self.active_games:
                del self.active_games[match_id]
            if match_id in self.game_actions:
                del self.game_actions[match_id]
            if match_id in self.player_states:
                del self.player_states[match_id]
            if match_id in self.action_locks:
                del self.action_locks[match_id]
            print(f"[GAME] Données du match {match_id} nettoyées")
    
    def get_queue_status(self) -> Dict:
        """Obtenir le statut de la file d'attente"""
        with self.lock:
            return {
                "queue_length": len(self.active_players),
                "estimated_wait_time": len(self.active_players) * 30,  # 30s par joueur
                "players_in_queue": [p["name"] for p in self.active_players.values()],
                "server_time": time.time()
            }
    
    def _save_player(self, player_info: Dict):
        """Sauvegarder un joueur en base"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO players 
                (player_id, player_name, rank, region, joined_at, last_seen, is_active)
                VALUES (?, ?, ?, ?, ?, ?, 1)
            """, (
                player_info["id"],
                player_info["name"],
                player_info["rank"],
                player_info["region"],
                datetime.fromtimestamp(player_info["joined_at"]),
                datetime.fromtimestamp(player_info["last_seen"])
            ))
            conn.commit()
    
    def _deactivate_player(self, player_id: str):
        """Marquer un joueur comme inactif"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE players SET is_active = 0, last_seen = CURRENT_TIMESTAMP
                WHERE player_id = ?
            """, (player_id,))
            conn.commit()
    
    def _save_match(self, match_info: Dict):
        """Sauvegarder un match en base"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO matches (match_id, player1_id, player2_id, created_at, status)
                VALUES (?, ?, ?, ?, ?)
            """, (
                match_info["match_id"],
                match_info["player1"]["id"],
                match_info["player2"]["id"],
                datetime.fromtimestamp(match_info["created_at"]),
                match_info["status"]
            ))
            conn.commit()
    
    def _cleanup_loop(self):
        """Boucle de nettoyage des joueurs inactifs"""
        while True:
            try:
                current_time = time.time()
                with self.lock:
                    # Retirer les joueurs inactifs (> 5 minutes)
                    inactive_players = []
                    for player_id, player_info in self.active_players.items():
                        if current_time - player_info["last_seen"] > 300:  # 5 minutes
                            inactive_players.append(player_id)
                    
                    for player_id in inactive_players:
                        self.remove_player(player_id)
                    
                    # Nettoyer les jeux inactifs (> 10 minutes)
                    inactive_games = []
                    for match_id, game_state in self.active_games.items():
                        if current_time - game_state.get("last_action_time", 0) > 600:  # 10 minutes
                            inactive_games.append(match_id)
                    
                    for match_id in inactive_games:
                        self.cleanup_game(match_id)
                
                time.sleep(60)  # Vérifier toutes les minutes
                
            except Exception as e:
                print(f"[SERVER] Erreur cleanup: {e}")
                time.sleep(60)

# Instance globale du serveur
matchmaking_server = MatchmakingServer()

# Route de test simple
@app.route('/', methods=['GET'])
def test_route():
    """Route de test simple"""
    return jsonify({"status": "ok", "message": "Serveur de matchmaking opérationnel"})

# Routes API existantes
@app.route('/api/matchmaking/join', methods=['POST'])
def join_matchmaking():
    """Rejoindre la file d'attente"""
    data = request.get_json()
    player_id = data.get('player_id')
    player_name = data.get('player_name')
    rank = data.get('rank', 0)
    region = data.get('region', 'unknown')
    
    if not player_id or not player_name:
        return jsonify({"error": "player_id et player_name requis"}), 400
    
    success = matchmaking_server.add_player(player_id, player_name, rank, region)
    
    return jsonify({
        "success": success,
        "queue_status": matchmaking_server.get_queue_status()
    })

@app.route('/api/matchmaking/leave', methods=['POST'])
def leave_matchmaking():
    """Quitter la file d'attente"""
    data = request.get_json()
    player_id = data.get('player_id')
    
    if not player_id:
        return jsonify({"error": "player_id requis"}), 400
    
    success = matchmaking_server.remove_player(player_id)
    
    return jsonify({"success": success})

@app.route('/api/matchmaking/status', methods=['GET'])
def get_status():
    """Obtenir le statut de la file d'attente et des matchs actifs"""
    with matchmaking_server.lock:
        status = matchmaking_server.get_queue_status()
        status.update({
            "active_matches": matchmaking_server.matches,
            "active_games": matchmaking_server.active_games
        })
    return jsonify(status)

@app.route('/api/matchmaking/poll', methods=['POST'])
def poll_for_match():
    """Vérifier si un match a été trouvé"""
    data = request.get_json()
    player_id = data.get('player_id')
    
    if not player_id:
        return jsonify({"error": "player_id requis"}), 400
    
    # Chercher un match pour ce joueur
    with matchmaking_server.lock:
        for match_id, match_info in matchmaking_server.matches.items():
            if (match_info["player1"]["id"] == player_id or 
                match_info["player2"]["id"] == player_id):
                
                # Marquer que ce joueur a récupéré le match
                if match_id not in matchmaking_server.match_claimed:
                    matchmaking_server.match_claimed[match_id] = set()
                
                matchmaking_server.match_claimed[match_id].add(player_id)
                
                # Si les deux joueurs ont récupéré le match, le supprimer
                if len(matchmaking_server.match_claimed[match_id]) >= 2:
                    print(f"[SERVER] Match {match_id} récupéré par les deux joueurs, suppression...")
                    del matchmaking_server.matches[match_id]
                    del matchmaking_server.match_claimed[match_id]
                else:
                    print(f"[SERVER] Match {match_id} récupéré par {player_id} ({len(matchmaking_server.match_claimed[match_id])}/2)")
                
                return jsonify({
                    "match_found": True,
                    "match": match_info
                })
    
    return jsonify({"match_found": False})

# === NOUVELLES ROUTES POUR LA SYNCHRONISATION DE COMBAT ===

@app.route('/api/game/initialize', methods=['POST'])
def initialize_game():
    """Initialiser le jeu pour un joueur"""
    data = request.get_json()
    match_id = data.get('match_id')
    player_id = data.get('player_id')
    deck_data = data.get('deck')
    
    if not match_id or not player_id or not deck_data:
        return jsonify({"error": "match_id, player_id et deck requis"}), 400
    
    result = matchmaking_server.initialize_game(match_id, player_id, deck_data)
    return jsonify(result)

@app.route('/api/game/action', methods=['POST'])
def submit_action():
    """Soumettre une action de combat"""
    data = request.get_json()
    match_id = data.get('match_id')
    player_id = data.get('player_id')
    action = data.get('action')
    
    if not match_id or not player_id or not action:
        return jsonify({"error": "match_id, player_id et action requis"}), 400
    
    result = matchmaking_server.submit_action(match_id, player_id, action)
    return jsonify(result)

@app.route('/api/game/state', methods=['POST'])
def get_game_state():
    """Obtenir l'état actuel du jeu"""
    data = request.get_json()
    match_id = data.get('match_id')
    player_id = data.get('player_id')
    
    if not match_id or not player_id:
        return jsonify({"error": "match_id et player_id requis"}), 400
    
    result = matchmaking_server.get_game_state(match_id, player_id)
    return jsonify(result)

@app.route('/api/game/update_state', methods=['POST'])
def update_player_state():
    """Mettre à jour l'état d'un joueur"""
    data = request.get_json()
    match_id = data.get('match_id')
    player_id = data.get('player_id')
    state = data.get('state', {})
    
    if not match_id or not player_id:
        return jsonify({"error": "match_id et player_id requis"}), 400
    
    result = matchmaking_server.update_player_state(match_id, player_id, state)
    return jsonify(result)

@app.route('/api/game/opponent_state', methods=['POST'])
def get_opponent_state():
    """Obtenir l'état de l'adversaire"""
    data = request.get_json()
    match_id = data.get('match_id')
    player_id = data.get('player_id')
    
    if not match_id or not player_id:
        return jsonify({"error": "match_id et player_id requis"}), 400
    
    result = matchmaking_server.get_opponent_state(match_id, player_id)
    return jsonify(result)

@app.route('/api/game/opponent_deck', methods=['POST'])
def get_opponent_deck():
    """Obtenir le deck de l'adversaire (si prêt)"""
    data = request.get_json()
    match_id = data.get('match_id')
    player_id = data.get('player_id')
    if not match_id or not player_id:
        return jsonify({"error": "match_id et player_id requis"}), 400
    result = matchmaking_server.get_opponent_deck(match_id, player_id)
    return jsonify(result)

@app.route('/api/game/end', methods=['POST'])
def end_game():
    """Terminer le jeu"""
    data = request.get_json()
    match_id = data.get('match_id')
    player_id = data.get('player_id')
    result = data.get('result', {})
    
    if not match_id or not player_id:
        return jsonify({"error": "match_id et player_id requis"}), 400
    
    result = matchmaking_server.end_game(match_id, player_id, result)
    return jsonify(result)

if __name__ == '__main__':
    print("[SERVER] Démarrage du serveur de matchmaking avec synchronisation de combat...")
    try:
        app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
    except Exception as e:
        print(f"[SERVER] Erreur au démarrage: {e}")
        # Essayer le port 5001
        try:
            print("[SERVER] Tentative avec le port 5001...")
            app.run(host='0.0.0.0', port=5001, debug=False, threaded=True)
        except Exception as e2:
            print(f"[SERVER] Erreur avec le port 5001: {e2}")
