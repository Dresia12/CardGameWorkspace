# 🎮 Guide Multijoueur Steam - JeuDeCarte

## 📋 Vue d'ensemble

Ce guide explique comment utiliser le système multijoueur Steam P2P intégré dans JeuDeCarte. Le système permet aux joueurs de s'affronter en ligne via Steam sans avoir besoin de serveurs externes.

## 🏗️ Architecture

### Composants principaux

```
Steam/
├── steam_integration.py      # Intégration Steam de base
├── steam_matchmaking.py      # Système de lobby/matchmaking
└── steam_networking.py       # Communication P2P

UI/
├── steam_lobby_ui.py         # Interface de lobby
└── steam_game_ui.py          # Interface de jeu multijoueur

main_steam.py                 # Point d'entrée multijoueur
```

## 🚀 Démarrage rapide

### 1. Lancer le jeu multijoueur

```bash
cd JeuDeCarte
python main_steam.py
```

### 2. Tester le système

```bash
python test_steam_multiplier.py
```

## 🎯 Fonctionnalités

### ✅ Système de Lobby
- **Créer une partie** : Créer un lobby public ou privé
- **Rejoindre une partie** : Rechercher et rejoindre des lobbies existants
- **Gestion des joueurs** : Attendre qu'un adversaire rejoigne
- **Types de lobby** : Public, Privé, Amis uniquement

### ✅ Communication P2P
- **Connexion directe** : Communication entre joueurs sans serveur
- **Synchronisation** : État du jeu synchronisé en temps réel
- **Actions de jeu** : Envoi des actions (cartes, capacités, fin de tour)
- **Chat** : Messages texte entre joueurs

### ✅ Interface utilisateur
- **Menu de lobby** : Interface intuitive pour gérer les parties
- **Salle d'attente** : Attendre qu'un adversaire rejoigne
- **Jeu intégré** : Interface de combat avec informations réseau
- **Indicateurs** : Statut de connexion, rôle (Hôte/Client)

## 🔧 Configuration

### Développement vs Production

#### Mode Développement (Actuel)
```python
# Steam/steam_integration.py
class SteamworksSimulator:
    """Simulateur Steamworks pour le développement"""
    # Utilise des IDs et noms simulés
```

#### Mode Production
```python
# Remplacer par la vraie API Steam
import steamworks
self.steam = steamworks.Steamworks()
```

### Variables d'environnement

```bash
# App ID Steam (à configurer)
STEAM_APP_ID=123456789

# Mode de développement
STEAM_DEV_MODE=true
```

## 📡 Protocole de communication

### Types de messages

```python
class MessageType(Enum):
    GAME_ACTION = "game_action"      # Actions de jeu
    GAME_STATE = "game_state"        # État du jeu
    PLAYER_READY = "player_ready"    # Joueur prêt
    GAME_START = "game_start"        # Début de partie
    GAME_END = "game_end"           # Fin de partie
    PING = "ping"                   # Test de connexion
    PONG = "pong"                   # Réponse ping
    CHAT = "chat"                   # Messages chat
```

### Format des messages

```json
{
    "type": "game_action",
    "data": {
        "action_type": "play_card",
        "card_index": 0,
        "target_info": {
            "type": "enemy_unit",
            "index": 1
        }
    },
    "timestamp": 1640995200.0,
    "sender_id": 12345
}
```

## 🎮 Utilisation

### 1. Créer une partie

1. Lancer `main_steam.py`
2. Cliquer sur "Créer une partie" ou appuyer sur `1`
3. Attendre qu'un adversaire rejoigne
4. La partie démarre automatiquement quand 2 joueurs sont présents

### 2. Rejoindre une partie

1. Lancer `main_steam.py`
2. Cliquer sur "Rejoindre une partie" ou appuyer sur `2`
3. Sélectionner un lobby dans la liste
4. Appuyer sur `Enter` pour rejoindre

### 3. Pendant la partie

- **Actions normales** : Jouer des cartes, utiliser des capacités
- **Synchronisation** : L'état est automatiquement synchronisé
- **Indicateurs** : Voir le statut de connexion en haut à gauche
- **Retour lobby** : Appuyer sur `ESC` pour retourner au lobby

## 🔍 Dépannage

### Problèmes courants

#### Steam non détecté
```
[STEAM] Erreur: Steam non disponible
```
**Solution** : Vérifier que Steam est installé et en cours d'exécution

#### Impossible de créer un lobby
```
[MATCHMAKING] Erreur: Impossible de créer le lobby
```
**Solution** : Vérifier la connexion internet et les permissions Steam

#### Déconnexion pendant la partie
```
[NETWORKING] Timeout de connexion pour le joueur X
```
**Solution** : Vérifier la stabilité de la connexion internet

### Logs de debug

Les logs détaillés sont affichés dans la console :
- `[STEAM]` : Intégration Steam
- `[MATCHMAKING]` : Système de lobby
- `[NETWORKING]` : Communication réseau
- `[STEAM GAME]` : Interface de jeu

## 🛠️ Développement

### Ajouter de nouvelles actions

1. **Définir le type de message**
```python
class MessageType(Enum):
    NEW_ACTION = "new_action"
```

2. **Implémenter l'envoi**
```python
def send_new_action(self, data):
    return self.send_message(player_id, MessageType.NEW_ACTION, data)
```

3. **Implémenter la réception**
```python
def _handle_new_action(self, data):
    # Traiter l'action reçue
    pass
```

### Personnaliser l'interface

Modifier les fichiers dans `UI/` :
- `steam_lobby_ui.py` : Interface de lobby
- `steam_game_ui.py` : Interface de jeu

### Tests

```bash
# Test complet du système
python test_steam_multiplier.py

# Test spécifique
python -c "from Steam.steam_integration import initialize_steam; print(initialize_steam())"
```

## 📚 API Référence

### SteamIntegration

```python
# Initialiser Steam
initialize_steam() -> bool

# Obtenir les infos utilisateur
get_steam_user_info() -> Dict

# Vérifier la disponibilité
is_steam_available() -> bool
```

### SteamMatchmaking

```python
# Créer un lobby
create_lobby(lobby_type, max_players) -> str

# Rejoindre un lobby
join_lobby(lobby_id, player_id, player_name) -> bool

# Rechercher des lobbies
search_lobbies(lobby_type) -> List[Dict]
```

### SteamNetworking

```python
# Démarrer/arrêter
start_networking()
stop_networking()

# Connexion
connect_to_player(player_id, player_name) -> bool

# Envoi de messages
send_game_action(player_id, action) -> bool
broadcast_game_state(state) -> int
```

## 🎯 Prochaines étapes

### Améliorations prévues

1. **Intégration Steam réelle**
   - Remplacer le simulateur par l'API Steamworks
   - Ajouter l'authentification Steam

2. **Fonctionnalités avancées**
   - Chat vocal
   - Spectateurs
   - Replay des parties
   - Classements

3. **Optimisations**
   - Compression des messages
   - Prédiction de latence
   - Synchronisation optimisée

### Déploiement Steam

1. **Créer un compte développeur Steam**
2. **Soumettre l'application**
3. **Configurer l'App ID**
4. **Tester avec des utilisateurs réels**

## 📞 Support

Pour toute question ou problème :
1. Vérifier les logs de debug
2. Consulter ce guide
3. Tester avec `test_steam_multiplier.py`
4. Vérifier la configuration Steam

---

**Note** : Ce système est actuellement en mode développement avec un simulateur Steam. Pour la production, il faudra intégrer la vraie API Steamworks. 