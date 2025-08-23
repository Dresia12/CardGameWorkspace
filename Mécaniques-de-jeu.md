# ⚔️ Mécaniques de jeu

## 🔄 Système de combat

### Tours et initiative
- **Tours alternés** : Vous jouez, puis l'adversaire
- **Initiative** : Détermine qui commence
- **Actions par tour** : Jouer des cartes + utiliser des capacités

### Mana et ressources
- **Mana de base** : 1 par tour
- **Mana maximum** : Augmente chaque tour
- **Coût des cartes** : Mana requis pour jouer

## 🎯 Capacités et ciblage

### Types de ciblage
- **single_enemy** : Un seul ennemi
- **single_ally** : Un seul allié
- **all_enemies** : Tous les ennemis (automatique)
- **all_allies** : Tous les alliés (automatique)
- **adjacent_enemies** : Ennemi + adjacents (ciblage initial requis)
- **adjacent_allies** : Allié + adjacents (ciblage initial requis)

### Utilisation des capacités
1. **Clic sur unité** → Menu des capacités
2. **Sélection capacité** → Mode ciblage
3. **Clic sur cible** → Capacité utilisée

## ⏰ Cooldowns et effets

### Système de cooldown
- **Cooldown** : Nombre de tours avant réutilisation
- **Affichage visuel** : Fond rouge semi-transparent + "CD: X"
- **Capacités disponibles** : Fond gris normal

### Types d'effets
- **Temporaires** : Durent quelques tours
- **Permanents** : Restent jusqu'à la fin du combat
- **Instantanés** : Effet immédiat

### Affichage des effets
- **Buffs** : Stats augmentées (couleur verte)
- **Debuffs** : Stats diminuées (couleur rouge)
- **Overlay** : Informations visuelles sur les unités

## 🎮 Positionnement

### Front Row / Back Row
- **Front Row** : Première ligne, unités en première ligne
- **Back Row** : Deuxième ligne, unités en arrière-plan
- **Capacités de position** : Certaines capacités ciblent spécifiquement front_row ou back_row

### Adjacence
- **Unités adjacentes** : Unités côte à côte
- **Ciblage adjacent** : Effet sur cible principale + propagation aux voisins
- **Réduction d'efficacité** : 50% sur les unités adjacentes

---

*[Retour à l'accueil](Home)*
