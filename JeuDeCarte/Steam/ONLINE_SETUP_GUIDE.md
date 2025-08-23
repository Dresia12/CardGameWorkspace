# 🌐 Guide de Mise en Place du Matchmaking en Ligne

## 📋 Prérequis

### **1. Serveur (VPS/Cloud)**
- **OS** : Linux (Ubuntu 20.04+ recommandé)
- **RAM** : 1GB minimum, 2GB recommandé
- **CPU** : 1 vCore minimum
- **Stockage** : 10GB minimum
- **Réseau** : IP publique avec port 5000 ouvert

### **2. Dépendances Système**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-venv nginx

# CentOS/RHEL
sudo yum install python3 python3-pip nginx
```

## 🚀 Installation du Serveur

### **1. Préparer l'Environnement**
```bash
# Créer un utilisateur pour le service
sudo useradd -m -s /bin/bash matchmaking
sudo su - matchmaking

# Créer le répertoire de l'application
mkdir -p ~/matchmaking-server
cd ~/matchmaking-server

# Créer un environnement virtuel
python3 -m venv venv
source venv/bin/activate
```

### **2. Installer les Dépendances**
```bash
# Copier le fichier requirements.txt
pip install -r requirements.txt
```

### **3. Configurer le Service Systemd**
```bash
# Créer le fichier de service
sudo nano /etc/systemd/system/matchmaking.service
```

Contenu du fichier :
```ini
[Unit]
Description=Matchmaking Server
After=network.target

[Service]
Type=simple
User=matchmaking
WorkingDirectory=/home/matchmaking/matchmaking-server
Environment=PATH=/home/matchmaking/matchmaking-server/venv/bin
ExecStart=/home/matchmaking/matchmaking-server/venv/bin/python matchmaking_server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### **4. Démarrer le Service**
```bash
sudo systemctl daemon-reload
sudo systemctl enable matchmaking
sudo systemctl start matchmaking
sudo systemctl status matchmaking
```

### **5. Configurer Nginx (Optionnel)**
```bash
sudo nano /etc/nginx/sites-available/matchmaking
```

Contenu :
```nginx
server {
    listen 80;
    server_name votre-domaine.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/matchmaking /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## 🔧 Configuration du Client

### **1. Modifier l'URL du Serveur**
Dans `online_matchmaking.py`, changer l'URL par défaut :
```python
def __init__(self, server_url: str = "http://votre-serveur.com"):
```

### **2. Intégrer dans le Jeu**
Modifier `steam_matchmaking_ui.py` pour utiliser le système en ligne :
```python
# Remplacer les imports
from Steam.online_matchmaking import (
    start_online_matchmaking, 
    stop_online_matchmaking, 
    get_online_matchmaking_status,
    set_online_matchmaking_callback
)
```

## 🧪 Tests

### **1. Test du Serveur**
```bash
# Vérifier que le serveur répond
curl http://localhost:5000/api/matchmaking/status

# Tester l'ajout d'un joueur
curl -X POST http://localhost:5000/api/matchmaking/join \
  -H "Content-Type: application/json" \
  -d '{"player_id":"test1","player_name":"TestPlayer"}'
```

### **2. Test du Client**
```bash
cd JeuDeCarte/Steam
python test_online_matchmaking.py
```

## 🔒 Sécurité

### **1. Firewall**
```bash
# Autoriser uniquement le port 5000
sudo ufw allow 5000/tcp
sudo ufw enable
```

### **2. SSL/TLS (Recommandé)**
```bash
# Installer Certbot
sudo apt install certbot python3-certbot-nginx

# Obtenir un certificat
sudo certbot --nginx -d votre-domaine.com
```

### **3. Rate Limiting**
Ajouter dans `matchmaking_server.py` :
```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)
```

## 📊 Monitoring

### **1. Logs**
```bash
# Voir les logs du service
sudo journalctl -u matchmaking -f

# Voir les logs nginx
sudo tail -f /var/log/nginx/access.log
```

### **2. Métriques**
Ajouter des endpoints de monitoring :
```python
@app.route('/health')
def health_check():
    return jsonify({"status": "healthy", "timestamp": time.time()})

@app.route('/metrics')
def metrics():
    return jsonify({
        "active_players": len(matchmaking_server.active_players),
        "total_matches": len(matchmaking_server.matches),
        "uptime": time.time() - start_time
    })
```

## 🚀 Déploiement en Production

### **1. Variables d'Environnement**
```bash
# Créer un fichier .env
export MATCHMAKING_SERVER_URL="https://votre-serveur.com"
export DATABASE_PATH="/var/lib/matchmaking/matchmaking.db"
export LOG_LEVEL="INFO"
```

### **2. Sauvegarde**
```bash
# Script de sauvegarde automatique
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
cp /home/matchmaking/matchmaking-server/matchmaking.db /backup/matchmaking_$DATE.db
```

### **3. Scaling**
Pour gérer plus de joueurs :
- Augmenter les ressources serveur
- Utiliser un load balancer
- Implémenter une base de données distribuée (Redis/PostgreSQL)

## 🔧 Dépannage

### **Problèmes Courants**

1. **Serveur ne démarre pas**
   ```bash
   sudo systemctl status matchmaking
   sudo journalctl -u matchmaking -n 50
   ```

2. **Connexion refusée**
   ```bash
   # Vérifier le firewall
   sudo ufw status
   
   # Vérifier que le port est ouvert
   netstat -tlnp | grep 5000
   ```

3. **Base de données corrompue**
   ```bash
   # Arrêter le service
   sudo systemctl stop matchmaking
   
   # Sauvegarder et recréer
   cp matchmaking.db matchmaking.db.backup
   rm matchmaking.db
   
   # Redémarrer
   sudo systemctl start matchmaking
   ```

## 📈 Optimisations

### **1. Performance**
- Utiliser Redis pour le cache
- Implémenter la compression gzip
- Optimiser les requêtes SQL

### **2. Fiabilité**
- Monitoring automatique
- Redémarrage automatique
- Sauvegarde automatique

### **3. Sécurité**
- Authentification API
- Validation des données
- Protection DDoS
