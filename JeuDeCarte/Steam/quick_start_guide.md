# 🚀 Guide de Démarrage Rapide - Multijoueur Temporaire

## 📋 **Option 1 : Test Local (Recommandé)**

### **Étape 1 : Installer les Dépendances**
```bash
cd JeuDeCarte/Steam
pip install flask flask-cors requests
```

### **Étape 2 : Démarrer le Serveur Local**
```bash
# Terminal 1 - Serveur de matchmaking
python matchmaking_server.py
```

### **Étape 3 : Tester le Système**
```bash
# Terminal 2 - Test du client
python test_online_matchmaking.py
```

### **Étape 4 : Lancer le Jeu**
```bash
# Terminal 3 - Jeu principal
python main.py
```

## 🌐 **Option 2 : Déploiement Rapide (15 minutes)**

### **Avec Render (Gratuit)**
1. Créer un compte sur [render.com](https://render.com)
2. Connecter votre repo GitHub
3. Créer un "Web Service"
4. Pointer vers le dossier `JeuDeCarte/Steam`
5. Déployer automatiquement

### **Configuration du Client**
Modifier `online_matchmaking.py` :
```python
def __init__(self, server_url: str = "https://votre-app.onrender.com"):
```

## 🎮 **Option 3 : Test avec Amis**

### **Configuration Réseau Local**
1. **Machine 1 (Serveur)** :
   ```bash
   python matchmaking_server.py
   # Noter l'IP locale (ex: 192.168.1.100)
   ```

2. **Machine 2 (Client)** :
   ```bash
   # Modifier l'URL dans online_matchmaking.py
   server_url = "http://192.168.1.100:5000"
   ```

3. **Tester** :
   ```bash
   python test_online_matchmaking.py
   ```

## 🔧 **Configuration Rapide du Jeu**

### **Modifier l'UI de Matchmaking**
Dans `steam_matchmaking_ui.py`, remplacer les imports :
```python
# Remplacer
from Steam.steam_real_matchmaking import start_steam_matchmaking

# Par
from Steam.online_matchmaking import start_online_matchmaking
```

### **Tester le Bouton VS**
1. Lancer le jeu
2. Aller dans "JOUER"
3. Cliquer sur "VS JOUEUR"
4. Vérifier que le matchmaking démarre

## 📊 **Tests Recommandés**

### **Test 1 : Fonctionnalité de Base**
```bash
# Vérifier que le serveur répond
curl http://localhost:5000/api/matchmaking/status
```

### **Test 2 : Matchmaking Simple**
```bash
# Ajouter un joueur
curl -X POST http://localhost:5000/api/matchmaking/join \
  -H "Content-Type: application/json" \
  -d '{"player_id":"test1","player_name":"Player1"}'
```

### **Test 3 : Match Complet**
```bash
# Ajouter un deuxième joueur (déclenche le match)
curl -X POST http://localhost:5000/api/matchmaking/join \
  -H "Content-Type: application/json" \
  -d '{"player_id":"test2","player_name":"Player2"}'
```

## 🎯 **Avantages de cette Approche**

✅ **Test immédiat** : Fonctionne dès maintenant
✅ **Pas de coût** : Gratuit pour les tests
✅ **Vrai multijoueur** : Communication réseau réelle
✅ **Migration facile** : Basculer vers Steam plus tard
✅ **Test avec amis** : Possibilité de tester en réseau local

## 🔄 **Migration Future vers Steam**

Une fois Steam approuvé :
1. Remplacer `SteamworksSimulator` par `steamworks.Steamworks()`
2. Configurer l'App ID
3. Tester avec la vraie API Steam
4. Déployer sur Steam

## 🚨 **Points d'Attention**

⚠️ **Serveur local** : Fonctionne uniquement sur votre réseau
⚠️ **Pas de P2P** : Communication via serveur central
⚠️ **Limitations** : Pas de fonctionnalités Steam avancées

## 💡 **Recommandation Finale**

**Commencez par l'Option 1 (Test Local)** :
1. Testez rapidement le système
2. Validez que tout fonctionne
3. Testez avec des amis en réseau local
4. Migrez vers Steam une fois approuvé

**Voulez-vous que je vous aide à configurer le test local ?**
