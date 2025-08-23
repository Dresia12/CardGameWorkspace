# 🎨 Interface de combat

## 🖼️ Overlays des unités

### Affichage normal
- **HP** : Points de vie actuels/maximum
- **Attaque** : Dégâts de base
- **Défense** : Protection contre les dégâts
- **Position** : Front row / Back row

### Avec buffs temporaires
- **Stats augmentées** : Affichées en vert
- **Durée** : Nombre de tours restants
- **Icônes** : Indicateurs visuels des effets

### Avec debuffs
- **Stats diminuées** : Affichées en rouge
- **Effets négatifs** : Poison, ralentissement, etc.
- **Durée** : Nombre de tours restants

### Avec cooldowns de capacités
- **Capacités disponibles** : Affichage normal
- **Capacités en cooldown** : Fond rouge semi-transparent
- **Indicateur CD** : "CD: X" à droite de la capacité

## 🎮 Menus de capacités

### Capacités disponibles
- **Fond gris** : Normal
- **Texte blanc** : Lisible
- **Clic actif** : Capacité utilisable

### Capacités en cooldown
- **Fond rouge semi-transparent** : 40% d'opacité
- **Texte gris foncé** : Indisponible
- **"CD: X"** : Cooldown restant

### Comportement du menu
- **Rafraîchissement automatique** : Après utilisation d'une capacité
- **Affichage persistant** : Menu reste ouvert
- **Mise à jour visuelle** : Cooldowns mis à jour en temps réel

## 🎯 Système de ciblage

### Cibles valides
- **Surbrillance** : Cibles sélectionnables
- **Couleur** : Indication visuelle
- **Feedback** : Confirmation de sélection

### Cibles invalides
- **Grisées** : Non sélectionnables
- **Raison** : Morte, hors de portée, etc.

### Ciblage adjacent
- **Cible principale** : Sélection manuelle
- **Propagation** : Effet automatique sur les voisins
- **Réduction** : 50% d'efficacité sur les adjacents

### Types de ciblage visuel
- **Single** : Une seule cible surlignée
- **Multiple** : Plusieurs cibles surlignées
- **Adjacent** : Cible principale + voisins
- **Automatique** : Pas de surbrillance (utilisation immédiate)

## 🎨 Éléments visuels

### Couleurs et significations
- **Vert** : Buffs, effets positifs
- **Rouge** : Debuffs, effets négatifs, cooldowns
- **Gris** : Normal, neutre
- **Blanc** : Texte lisible
- **Gris foncé** : Texte indisponible

### Effets visuels
- **Semi-transparence** : 40% d'opacité pour les cooldowns
- **Surbrillance** : Cibles sélectionnables
- **Animation** : Effets de combat
- **Feedback** : Confirmation des actions

### Interface responsive
- **Adaptation** : Interface s'adapte au contenu
- **Positionnement** : Menus positionnés intelligemment
- **Accessibilité** : Interface claire et intuitive

---

*[Retour à l'accueil](Home)*
