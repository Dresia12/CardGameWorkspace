# Guide des Types de Ciblage

## **Types de Ciblage Disponibles**

### **1. Cibles Uniques (Ciblage Manuel Requis)**
- `"single_enemy"` - Un seul ennemi
- `"single_ally"` - Un seul allié  
- `"self"` - Le lanceur lui-même

### **2. Cibles Multiples (Utilisation Automatique)**
- `"all_enemies"` - Tous les ennemis
- `"all_allies"` - Tous les alliés
- `"all_units"` - Toutes les unités (alliés + ennemis)

### **3. Cibles Aléatoires (Utilisation Automatique)**
- `"random_enemy"` - Un ennemi aléatoire
- `"random_ally"` - Un allié aléatoire
- `"random_unit"` - Une unité aléatoire

### **4. Cibles en Chaîne (Utilisation Automatique)**
- `"chain_enemies"` - Chaîne d'ennemis (selon bounce_count et priority)
- `"chain_allies"` - Chaîne d'alliés (selon bounce_count et priority)

### **5. Cibles par Position (Utilisation Automatique)**
- `"front_row"` - Première ligne
- `"back_row"` - Ligne arrière

### **6. Cibles Adjacentes (Ciblage Initial + Propagation)**
- `"adjacent_enemies"` - Ciblage initial + propagation aux ennemis adjacents
- `"adjacent_allies"` - Ciblage initial + propagation aux alliés adjacents

## **Logique de Fonctionnement**

### **Capacités Automatiques**
Les capacités suivantes s'utilisent automatiquement sans ciblage manuel :
- Toutes les capacités multiples (`all_*`)
- Toutes les capacités aléatoires (`random_*`)
- Toutes les capacités en chaîne (`chain_*`)
- Toutes les capacités par position (`front_row`, `back_row`)

### **Capacités Adjacentes**
Les capacités `adjacent_*` fonctionnent en deux étapes :
1. **Ciblage initial** : Le joueur sélectionne une cible principale
2. **Propagation automatique** : L'effet se propage aux unités adjacentes
   - 100% des dégâts sur la cible principale
   - 50% des dégâts sur les cibles adjacentes
   - Mêmes effets appliqués à toutes les cibles

### **Capacités à Ciblage Unique**
Les capacités `single_*` et `self` nécessitent un ciblage manuel.

## **Exemples d'Utilisation**

### **Capacité "Danse des Alizés" (all_allies)**
```json
{
  "target_type": "all_allies",
  "crit_boost": 0.2,
  "crit_duration": 1
}
```
**Résultat** : Applique automatiquement +20% crit à tous les alliés

### **Capacité "Attaque en Chaîne" (chain_enemies)**
```json
{
  "target_type": "chain_enemies",
  "bounce_count": 3,
  "priority": "lowest_hp"
}
```
**Résultat** : Touche automatiquement 3 ennemis avec le moins de HP

### **Capacité "Explosion Adjacente" (adjacent_enemies)**
```json
{
  "target_type": "adjacent_enemies",
  "damage": 100
}
```
**Résultat** : 
- Ciblage manuel d'un ennemi
- 100 dégâts sur la cible principale
- 50 dégâts sur les ennemis adjacents

## **Paramètres de Chaînage**

### **bounce_count**
Nombre de rebonds dans la chaîne (ex: 3 = touche 3 cibles)

### **priority**
Priorité de sélection pour les chaînes :
- `"lowest_hp"` - Moins de HP
- `"highest_hp"` - Plus de HP
- `"lowest_defense"` - Moins de défense
- `"highest_defense"` - Plus de défense
- `"random"` - Aléatoire
- `"first"` - Première cible
- `"last"` - Dernière cible
