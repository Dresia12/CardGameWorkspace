#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import sys
import os
import time
import requests

# Ajouter le chemin du projet au sys.path
project_root = os.path.join(os.path.dirname(__file__))
sys.path.insert(0, project_root)

def test_matchmaking_server():
    """Test du serveur de matchmaking"""
    print("=== TEST SERVEUR MATCHMAKING ===")
    
    server_url = "http://localhost:5000"
    
    # 1. Test de connexion
    print("\n1. Test de connexion au serveur:")
    try:
        response = requests.get(f"{server_url}/api/matchmaking/status", timeout=5)
        if response.status_code == 200:
            print("✓ Serveur accessible")
            status = response.json()
            print(f"   Statut: {status}")
        else:
            print(f"✗ Erreur serveur: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Impossible de se connecter au serveur: {e}")
        return False
    
    # 2. Test d'ajout de joueur 1
    print("\n2. Test d'ajout du joueur 1:")
    player1_data = {
        "player_id": "test_player_1",
        "player_name": "TestPlayer1",
        "rank": 0,
        "region": "test"
    }
    
    try:
        response = requests.post(f"{server_url}/api/matchmaking/join", json=player1_data)
        if response.status_code == 200:
            data = response.json()
            print("✓ Joueur 1 ajouté")
            print(f"   Réponse: {data}")
        else:
            print(f"✗ Erreur ajout joueur 1: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Erreur ajout joueur 1: {e}")
        return False
    
    # 3. Test d'ajout de joueur 2 (devrait créer un match)
    print("\n3. Test d'ajout du joueur 2:")
    player2_data = {
        "player_id": "test_player_2",
        "player_name": "TestPlayer2",
        "rank": 0,
        "region": "test"
    }
    
    try:
        response = requests.post(f"{server_url}/api/matchmaking/join", json=player2_data)
        if response.status_code == 200:
            data = response.json()
            print("✓ Joueur 2 ajouté")
            print(f"   Réponse: {data}")
        else:
            print(f"✗ Erreur ajout joueur 2: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Erreur ajout joueur 2: {e}")
        return False
    
    # 4. Test de polling pour le joueur 1
    print("\n4. Test de polling pour le joueur 1:")
    for i in range(5):  # Tester pendant 5 secondes
        try:
            response = requests.post(f"{server_url}/api/matchmaking/poll", json={
                "player_id": "test_player_1"
            })
            if response.status_code == 200:
                data = response.json()
                print(f"   Poll {i+1}: {data}")
                if data.get("match_found"):
                    print("✓ Match trouvé pour le joueur 1!")
                    match_info = data.get("match")
                    print(f"   Match info: {match_info}")
                    break
            else:
                print(f"   Erreur poll: {response.status_code}")
        except Exception as e:
            print(f"   Erreur poll: {e}")
        
        time.sleep(1)
    
    # 5. Test de polling pour le joueur 2
    print("\n5. Test de polling pour le joueur 2:")
    for i in range(5):  # Tester pendant 5 secondes
        try:
            response = requests.post(f"{server_url}/api/matchmaking/poll", json={
                "player_id": "test_player_2"
            })
            if response.status_code == 200:
                data = response.json()
                print(f"   Poll {i+1}: {data}")
                if data.get("match_found"):
                    print("✓ Match trouvé pour le joueur 2!")
                    match_info = data.get("match")
                    print(f"   Match info: {match_info}")
                    break
            else:
                print(f"   Erreur poll: {response.status_code}")
        except Exception as e:
            print(f"   Erreur poll: {e}")
        
        time.sleep(1)
    
    # 6. Nettoyage - retirer les joueurs
    print("\n6. Nettoyage:")
    for player_id in ["test_player_1", "test_player_2"]:
        try:
            response = requests.post(f"{server_url}/api/matchmaking/leave", json={
                "player_id": player_id
            })
            if response.status_code == 200:
                print(f"✓ Joueur {player_id} retiré")
            else:
                print(f"✗ Erreur retrait {player_id}: {response.status_code}")
        except Exception as e:
            print(f"✗ Erreur retrait {player_id}: {e}")
    
    print("\n=== FIN DU TEST ===")
    return True

def test_online_matchmaking():
    """Test du système de matchmaking en ligne"""
    print("\n=== TEST ONLINE MATCHMAKING ===")
    
    try:
        from Steam.online_matchmaking import OnlineMatchmaking
        
        # Créer une instance de test
        matchmaking = OnlineMatchmaking()
        
        # Test de connexion
        print("\n1. Test de connexion:")
        if matchmaking.is_connected():
            print("✓ Serveur accessible")
        else:
            print("✗ Serveur non accessible")
            return False
        
        # Test de callback
        print("\n2. Test de callback:")
        callback_called = False
        callback_data = None
        
        def test_callback(match_data):
            nonlocal callback_called, callback_data
            callback_called = True
            callback_data = match_data
            print(f"✓ Callback appelé avec: {match_data}")
        
        matchmaking.set_callback("match_found", test_callback)
        print("✓ Callback configuré")
        
        # Test de démarrage du matchmaking
        print("\n3. Test de démarrage du matchmaking:")
        if matchmaking.start_matchmaking("test_id", "TestPlayer"):
            print("✓ Matchmaking démarré")
            
            # Attendre un peu pour voir si un match est trouvé
            print("\n4. Attente de match (10 secondes):")
            for i in range(10):
                print(f"   Attente {i+1}/10...")
                time.sleep(1)
                if callback_called:
                    print("✓ Match trouvé via callback!")
                    break
            else:
                print("✗ Aucun match trouvé dans les 10 secondes")
        else:
            print("✗ Impossible de démarrer le matchmaking")
            return False
        
        # Arrêter le matchmaking
        print("\n5. Arrêt du matchmaking:")
        if matchmaking.stop_matchmaking():
            print("✓ Matchmaking arrêté")
        else:
            print("✗ Erreur lors de l'arrêt")
        
    except Exception as e:
        print(f"✗ Erreur test online matchmaking: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n=== FIN DU TEST ONLINE MATCHMAKING ===")
    return True

if __name__ == "__main__":
    print("Démarrage des tests de matchmaking...")
    
    # Test 1: Serveur de matchmaking
    test_matchmaking_server()
    
    # Test 2: Système de matchmaking en ligne
    test_online_matchmaking()
    
    print("\nTests terminés!")
