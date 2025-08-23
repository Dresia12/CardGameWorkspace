#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import time

BASE_URLS = [
    "http://127.0.0.1:5000",
    "http://localhost:5000",
    "http://127.0.0.1:5001",
    "http://localhost:5001",
]

def try_request(session, method, path, **kwargs):
    last_exc = None
    for base in BASE_URLS:
        url = f"{base}{path}"
        try:
            resp = session.request(method, url, timeout=5, **kwargs)
            print(f"✓ {method.upper()} {url} -> {resp.status_code}")
            return base, resp
        except Exception as e:
            print(f" - Échec {method.upper()} {url}: {e}")
            last_exc = e
    raise last_exc if last_exc else Exception("Aucune URL n'a répondu")

def test_simple():
    """Test simple du serveur"""
    print("=== TEST SIMPLE DU SERVEUR ===")
    
    # Test 1: Connexion basique
    try:
        print("1. Test de connexion...")
        session = requests.Session()
        session.trust_env = False  # éviter l'influence de variables d'environnement/proxy
        base_url, response = try_request(session, "get", "/api/matchmaking/status")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Données: {data}")
        else:
            print(f"✗ Erreur: {response.text}")
    except Exception as e:
        print(f"✗ Erreur de connexion: {e}")
        return
    
    # Test 2: Inscription d'un seul joueur
    try:
        print("\n2. Test d'inscription d'un joueur...")
        player_data = {
            "player_name": "TestPlayer",
            "player_id": "test_player_1",
            "rank": 0,
            "region": "test"
        }
        _, response = try_request(session, "post", "/api/matchmaking/join", json=player_data)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Données: {data}")
        else:
            print(f"✗ Erreur: {response.text}")
    except Exception as e:
        print(f"✗ Erreur d'inscription: {e}")
        return
    
    # Test 3: Vérifier le statut après inscription
    try:
        print("\n3. Vérification du statut...")
        _, response = try_request(session, "get", "/api/matchmaking/status")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Joueurs en queue: {data.get('queue_length', 0)}")
            print(f"✓ Noms: {data.get('players_in_queue', [])}")
            print(f"✓ Matchs actifs: {len(data.get('active_matches', {}))}")
        else:
            print(f"✗ Erreur: {response.text}")
    except Exception as e:
        print(f"✗ Erreur de statut: {e}")
    
    print("\n=== FIN DU TEST SIMPLE ===")

if __name__ == "__main__":
    test_simple()
