#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import socket
import time

def test_connection():
    """Test de connexion très simple"""
    print("=== TEST DE CONNEXION DEBUG ===")
    
    # Test 1: Vérifier si le port est ouvert
    print("1. Test du port 5000...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(('127.0.0.1', 5000))
        sock.close()
        
        if result == 0:
            print("✓ Port 5000 est ouvert")
        else:
            print(f"✗ Port 5000 fermé (code: {result})")
            return
    except Exception as e:
        print(f"✗ Erreur test port: {e}")
        return
    
    # Test 2: Test HTTP simple
    print("\n2. Test HTTP simple...")
    try:
        response = requests.get("http://127.0.0.1:5000/", timeout=3)
        print(f"✓ Réponse: {response.status_code}")
        print(f"✓ Contenu: {response.text}")
    except requests.exceptions.Timeout:
        print("✗ Timeout - le serveur ne répond pas")
    except requests.exceptions.ConnectionError as e:
        print(f"✗ Erreur de connexion: {e}")
    except Exception as e:
        print(f"✗ Erreur: {e}")
    
    # Test 3: Test avec curl-like
    print("\n3. Test avec socket direct...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        sock.connect(('127.0.0.1', 5000))
        
        # Envoyer une requête HTTP simple
        request = "GET / HTTP/1.1\r\nHost: 127.0.0.1:5000\r\n\r\n"
        sock.send(request.encode())
        
        # Lire la réponse
        response = sock.recv(1024).decode()
        print(f"✓ Réponse brute: {response[:200]}...")
        
        sock.close()
    except Exception as e:
        print(f"✗ Erreur socket: {e}")

if __name__ == "__main__":
    test_connection()
