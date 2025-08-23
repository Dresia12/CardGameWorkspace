#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JeuDeCarte - Point d'entrée principal
Lance l'interface utilisateur du jeu de cartes
"""

import sys
import os

# Ajouter le dossier UI au path pour les imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'UI'))

try:
    from game_ui import GameUI
    
    def main():
        """Fonction principale du jeu"""
        print("[MAIN] Démarrage du JeuDeCarte...")
        print("[MAIN] Import de GameUI réussi")
        
        # Créer et lancer l'interface utilisateur
        print("[MAIN] Création de l'instance GameUI...")
        game = GameUI()
        print("[MAIN] Instance GameUI créée avec succès")
        print("[MAIN] Lancement de game.run()...")
        game.run()
        print("[MAIN] game.run() terminé")
        
    if __name__ == "__main__":
        main()
        
except ImportError as e:
    print(f"[ERREUR] Impossible d'importer game_ui : {e}")
    print("[ERREUR] Vérifiez que le fichier UI/game_ui.py existe")
except Exception as e:
    print(f"[ERREUR] Erreur lors du démarrage : {e}") 