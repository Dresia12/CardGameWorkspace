#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import sys
import os
import time
import requests
import threading

project_root = os.path.join(os.path.dirname(__file__))
sys.path.insert(0, project_root)

def test_multiplayer_fix():
    """Test du système multijoueur après corrections"""
    print("=== TEST DU SYSTÈME MULTIJOUEUR APRÈS CORRECTIONS ===")
    
    # Test 1: Vérifier que le serveur répond
    try:
        response = requests.get("http://localhost:5000/api/matchmaking/status")
        if response.status_code == 200:
            print("✓ Serveur accessible")
        else:
            print("✗ Serveur inaccessible")
            return
    except Exception as e:
        print(f"✗ Erreur de connexion au serveur: {e}")
        return
    
    # Test 2: Créer deux joueurs et simuler un match
    print("\n2. Test de création de match:")
    
    # Joueur 1
    player1_data = {
        "player_name": "TestPlayer1",
        "player_id": "player1_test",
        "rank": 0,
        "region": "test"
    }
    
    # Joueur 2  
    player2_data = {
        "player_name": "TestPlayer2", 
        "player_id": "player2_test",
        "rank": 0,
        "region": "test"
    }
    
    # Inscrire les joueurs
    try:
        response1 = requests.post("http://localhost:5000/api/matchmaking/join", json=player1_data)
        response2 = requests.post("http://localhost:5000/api/matchmaking/join", json=player2_data)
        
        if response1.status_code == 200 and response2.status_code == 200:
            print("✓ Joueurs inscrits")
            
            # Attendre un peu pour que le match soit créé
            time.sleep(2)
            
            # Vérifier le statut
            response = requests.get("http://localhost:5000/api/matchmaking/status")
            if response.status_code == 200:
                status = response.json()
                print(f"✓ Statut serveur: {status.get('status', 'unknown')}")
                print(f"✓ Joueurs en queue: {status.get('queue_length', 0)}")
                print(f"✓ Noms en queue: {status.get('players_in_queue', [])}")
                
                # Vérifier s'il y a des matchs actifs
                if 'active_matches' in status:
                    print(f"✓ Matchs actifs: {len(status['active_matches'])}")
                    if status['active_matches']:
                        for match_id, match_info in status['active_matches'].items():
                            print(f"  - Match {match_id}: {match_info.get('player1', {}).get('name', 'Unknown')} vs {match_info.get('player2', {}).get('name', 'Unknown')}")
                    
                    # Tester l'initialisation d'un jeu
                    if status['active_matches']:
                        match_id = list(status['active_matches'].keys())[0]
                        print(f"✓ Test avec match ID: {match_id}")
                        
                        # Test d'initialisation du jeu
                        game_data = {
                            "match_id": match_id,
                            "player_id": "player1_test",
                            "deck": {"name": "Deck Test 1", "hero": "Hero1", "units": [], "cards": []}
                        }
                        
                        response = requests.post("http://localhost:5000/api/game/initialize", json=game_data)
                        if response.status_code == 200:
                            result = response.json()
                            print(f"✓ Initialisation réussie: {result.get('status', 'unknown')}")
                        else:
                            print(f"✗ Erreur initialisation: {response.status_code}")
                            print(f"✗ Réponse: {response.text}")
                else:
                    print("⚠ Aucun match actif trouvé")
                    print(f"⚠ Contenu complet du statut: {status}")
            else:
                print(f"✗ Erreur statut: {response.status_code}")
        else:
            print(f"✗ Erreur inscription: {response1.status_code}, {response2.status_code}")
            
    except Exception as e:
        print(f"✗ Erreur lors du test: {e}")
    
    print("\n=== FIN DU TEST ===")

if __name__ == "__main__":
    test_multiplayer_fix()
