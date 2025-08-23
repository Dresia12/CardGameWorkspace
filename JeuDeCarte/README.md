# JeuDeCarte - Architecture Modulaire

## Structure du Projet

```
JeuDeCarte/
├── main.py                    # Point d'entrée principal
├── Data/                      # Données du jeu
│   ├── heroes.json           # Définitions des héros
│   ├── units.json            # Définitions des unités
│   └── cards.json            # Définitions des cartes
├── Assets/                    # Assets du jeu
│   ├── img/                  # Images
│   │   ├── Hero/            # Images des héros
│   │   ├── Crea/            # Images des créatures/unités
│   │   └── Carte/           # Images des cartes
│   └── Music/               # Sons et musiques
├── Engine/                    # Moteur de jeu
│   └── engine.py            # Logique principale du jeu
├── UI/                       # Interface utilisateur
│   └── game_ui.py           # Interface Pygame
└── Documentation/            # Documentation
    └── Jeu.txt              # Spécifications du jeu
```

## Démarrage

Pour lancer le jeu :

```bash
cd JeuDeCarte
python main.py
```

## Architecture

### Data/
Contient tous les fichiers JSON définissant les entités du jeu :
- **heroes.json** : Héros avec leurs capacités et cooldowns
- **units.json** : Unités avec leurs statistiques et éléments
- **cards.json** : Cartes de sorts avec leurs effets

### Assets/
Contient tous les assets visuels et audio :
- **img/** : Images organisées par type (Hero, Crea, Carte)
- **Music/** : Fichiers audio (.wav, .mp3, .ogg)

### Engine/
Contient la logique métier du jeu :
- **engine.py** : Moteur de combat, gestion des phases, effets temporaires, etc.

### UI/
Contient l'interface utilisateur :
- **game_ui.py** : Interface Pygame avec tous les écrans (Menu, Deck Builder, Combat, etc.)

### Documentation/
Contient la documentation du projet :
- **Jeu.txt** : Spécifications complètes du jeu

## Dépendances

- Python 3.7+
- Pygame

## Développement

L'architecture modulaire permet :
- **Séparation claire** des responsabilités
- **Maintenance facile** du code
- **Évolutivité** pour ajouter de nouveaux modules
- **Tests unitaires** par composant

## Chemins Relatifs

Les chemins dans le code sont configurés pour fonctionner depuis la racine `JeuDeCarte/` :
- UI → Engine : `../Engine/`
- UI → Data : `../Data/`
- UI → Assets : `../Assets/` 