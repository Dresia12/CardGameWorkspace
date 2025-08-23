#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de test pour le système de synchronisation multijoueur
"""

import json
import sys
import os
import time
import requests
import threading

# Ajouter le chemin du projet au sys.path
project_root = os.path.join(os.path.dirname(__file__))
sys.path.insert(0, project_root)

def test_server_sync():
    """Test du serveur de synchronisation"""
    print("=== TEST SERVEUR DE SYNCHRONISATION ===")
    
    server_url = "http://localhost:5000"
    
    # 1. Test de connexion
    print("\n1. Test de connexion au serveur:")
    try:
        response = requests.get(f"{server_url}/api/matchmaking/status", timeout=5)
        if response.status_code == 200:
            print("✓ Serveur accessible")
        else:
            print(f"✗ Erreur serveur: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Impossible de se connecter au serveur: {e}")
        return False
    
    # 2. Test de création d'un match
    print("\n2. Test de création d'un match:")
    match_data = {
        "match_id": "test_match_123",
        "player1": {"id": "player1", "name": "TestPlayer1"},
        "player2": {"id": "player2", "name": "TestPlayer2"},
        "status": "pending"
    }
    
    # 3. Test d'initialisation du jeu
    print("\n3. Test d'initialisation du jeu:")
    deck_data = {
        "name": "Test Deck",
        "hero": {"name": "Test Hero", "element": "Feu"},
        "units": [{"name": "Test Unit", "hp": 100, "attack": 10}],
        "cards": [{"name": "Test Card", "cost": 1, "element": "Feu"}]
    }
    
    try:
        response = requests.post(f"{server_url}/api/game/initialize", json={
            "match_id": "test_match_123",
            "player_id": "player1",
            "deck": deck_data
        }, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("✓ Jeu initialisé pour le joueur 1")
                print(f"   Game started: {data.get('game_started')}")
            else:
                print(f"✗ Erreur initialisation: {data.get('error')}")
        else:
            print(f"✗ Erreur HTTP: {response.status_code}")
    except Exception as e:
        print(f"✗ Erreur initialisation: {e}")
    
    # 4. Test d'initialisation du second joueur
    print("\n4. Test d'initialisation du second joueur:")
    try:
        response = requests.post(f"{server_url}/api/game/initialize", json={
            "match_id": "test_match_123",
            "player_id": "player2",
            "deck": deck_data
        }, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("✓ Jeu initialisé pour le joueur 2")
                print(f"   Game started: {data.get('game_started')}")
            else:
                print(f"✗ Erreur initialisation: {data.get('error')}")
        else:
            print(f"✗ Erreur HTTP: {response.status_code}")
    except Exception as e:
        print(f"✗ Erreur initialisation: {e}")
    
    # 5. Test de soumission d'action
    print("\n5. Test de soumission d'action:")
    action_data = {
        "type": "play_card",
        "data": {
            "card_name": "Test Card",
            "target": "enemy_hero"
        }
    }
    
    try:
        response = requests.post(f"{server_url}/api/game/action", json={
            "match_id": "test_match_123",
            "player_id": "player1",
            "action": action_data
        }, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("✓ Action soumise avec succès")
                print(f"   Next player: {data.get('next_player')}")
            else:
                print(f"✗ Erreur action: {data.get('error')}")
        else:
            print(f"✗ Erreur HTTP: {response.status_code}")
    except Exception as e:
        print(f"✗ Erreur action: {e}")
    
    # 6. Test de récupération de l'état du jeu
    print("\n6. Test de récupération de l'état du jeu:")
    try:
        response = requests.post(f"{server_url}/api/game/state", json={
            "match_id": "test_match_123",
            "player_id": "player2"
        }, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("✓ État du jeu récupéré")
                game_state = data.get("game_state", {})
                print(f"   Status: {game_state.get('status')}")
                print(f"   Current turn: {game_state.get('current_turn')}")
                print(f"   Current player: {game_state.get('current_player')}")
                print(f"   Is my turn: {data.get('is_my_turn')}")
                print(f"   Recent actions: {len(data.get('recent_actions', []))}")
            else:
                print(f"✗ Erreur état: {data.get('error')}")
        else:
            print(f"✗ Erreur HTTP: {response.status_code}")
    except Exception as e:
        print(f"✗ Erreur état: {e}")
    
    print("\n=== FIN DU TEST SERVEUR ===")
    return True

def test_client_sync():
    """Test du client de synchronisation"""
    print("\n=== TEST CLIENT DE SYNCHRONISATION ===")
    
    try:
        from Steam.multiplayer_sync import MultiplayerSync, ActionType
        
        # Créer une instance de synchronisation
        sync = MultiplayerSync()
        
        # Test de connexion
        print("\n1. Test de connexion:")
        if sync.is_connected():
            print("✓ Connecté au serveur")
        else:
            print("✗ Non connecté au serveur")
            return False
        
        # Test d'initialisation
        print("\n2. Test d'initialisation:")
        deck_data = {
            "name": "Test Deck",
            "hero": {"name": "Test Hero", "element": "Feu"},
            "units": [{"name": "Test Unit", "hp": 100, "attack": 10}],
            "cards": [{"name": "Test Card", "cost": 1, "element": "Feu"}]
        }
        
        if sync.initialize_game("test_match_456", "test_player", deck_data):
            print("✓ Jeu initialisé")
        else:
            print("✗ Erreur d'initialisation")
        
        # Test de soumission d'action
        print("\n3. Test de soumission d'action:")
        action_data = {
            "card_name": "Test Card",
            "target": "enemy_hero"
        }
        
        if sync.submit_action(ActionType.PLAY_CARD, action_data):
            print("✓ Action soumise")
        else:
            print("✗ Erreur soumission action")
        
        # Test de mise à jour d'état
        print("\n4. Test de mise à jour d'état:")
        state_data = {
            "hp": 100,
            "mana": 5,
            "deck_size": 25
        }
        
        if sync.update_player_state(state_data):
            print("✓ État mis à jour")
        else:
            print("✗ Erreur mise à jour état")
        
        # Arrêter la synchronisation
        sync.stop_sync()
        
        print("\n=== FIN DU TEST CLIENT ===")
        return True
        
    except Exception as e:
        print(f"✗ Erreur test client: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_full_workflow():
    """Test du workflow complet"""
    print("\n=== TEST WORKFLOW COMPLET ===")
    
    server_url = "http://localhost:5000"
    
    # 1. Créer deux joueurs
    print("\n1. Création des joueurs:")
    for i in range(1, 3):
        try:
            response = requests.post(f"{server_url}/api/matchmaking/join", json={
                "player_id": f"test_player_{i}",
                "player_name": f"TestPlayer{i}",
                "rank": 0,
                "region": "test"
            }, timeout=5)
            
            if response.status_code == 200:
                print(f"✓ Joueur {i} créé")
            else:
                print(f"✗ Erreur création joueur {i}")
        except Exception as e:
            print(f"✗ Erreur création joueur {i}: {e}")
    
    # 2. Attendre qu'un match soit créé
    print("\n2. Attente d'un match:")
    match_found = False
    for i in range(10):  # Attendre 10 secondes
        try:
            response = requests.post(f"{server_url}/api/matchmaking/poll", json={
                "player_id": "test_player_1"
            }, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("match_found"):
                    match_data = data.get("match")
                    print(f"✓ Match trouvé: {match_data.get('match_id')}")
                    match_found = True
                    break
        except Exception as e:
            print(f"✗ Erreur polling: {e}")
        
        time.sleep(1)
    
    if not match_found:
        print("✗ Aucun match trouvé")
        return False
    
    # 3. Initialiser le jeu pour les deux joueurs
    print("\n3. Initialisation du jeu:")
    deck_data = {
        "name": "Test Deck",
        "hero": {"name": "Test Hero", "element": "Feu"},
        "units": [{"name": "Test Unit", "hp": 100, "attack": 10}],
        "cards": [{"name": "Test Card", "cost": 1, "element": "Feu"}]
    }
    
    for i in range(1, 3):
        try:
            response = requests.post(f"{server_url}/api/game/initialize", json={
                "match_id": match_data.get("match_id"),
                "player_id": f"test_player_{i}",
                "deck": deck_data
            }, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    print(f"✓ Joueur {i} initialisé")
                    if data.get("game_started"):
                        print("   → Jeu démarré !")
                else:
                    print(f"✗ Erreur initialisation joueur {i}: {data.get('error')}")
            else:
                print(f"✗ Erreur HTTP joueur {i}: {response.status_code}")
        except Exception as e:
            print(f"✗ Erreur initialisation joueur {i}: {e}")
    
    # 4. Simuler quelques actions
    print("\n4. Simulation d'actions:")
    actions = [
        {"type": "play_card", "data": {"card_name": "Test Card 1", "target": "enemy_hero"}},
        {"type": "use_ability", "data": {"ability_name": "Test Ability", "target": "enemy_unit"}},
        {"type": "end_turn", "data": {}}
    ]
    
    for i, action in enumerate(actions):
        try:
            response = requests.post(f"{server_url}/api/game/action", json={
                "match_id": match_data.get("match_id"),
                "player_id": "test_player_1",
                "action": action
            }, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    print(f"✓ Action {i+1} soumise")
                else:
                    print(f"✗ Erreur action {i+1}: {data.get('error')}")
            else:
                print(f"✗ Erreur HTTP action {i+1}: {response.status_code}")
        except Exception as e:
            print(f"✗ Erreur action {i+1}: {e}")
    
    # 5. Vérifier l'état final
    print("\n5. Vérification de l'état final:")
    try:
        response = requests.post(f"{server_url}/api/game/state", json={
            "match_id": match_data.get("match_id"),
            "player_id": "test_player_2"
        }, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("✓ État final récupéré")
                game_state = data.get("game_state", {})
                print(f"   Status: {game_state.get('status')}")
                print(f"   Current turn: {game_state.get('current_turn')}")
                print(f"   Actions: {len(data.get('recent_actions', []))}")
            else:
                print(f"✗ Erreur état final: {data.get('error')}")
        else:
            print(f"✗ Erreur HTTP état final: {response.status_code}")
    except Exception as e:
        print(f"✗ Erreur état final: {e}")
    
    print("\n=== FIN DU TEST WORKFLOW ===")
    return True

if __name__ == "__main__":
    print("Démarrage des tests de synchronisation multijoueur...")
    
    # Test 1: Serveur de synchronisation
    test_server_sync()
    
    # Test 2: Client de synchronisation
    test_client_sync()
    
    # Test 3: Workflow complet
    test_full_workflow()
    
    print("\nTests terminés!")
