# Guide de Résolution des Problèmes d'Images - JeuDeCarte

## 🖼️ Problème Identifié

Les images des héros et unités ne se chargent pas correctement dans l'interface du jeu.

## 🔍 Diagnostic

### Causes Possibles

1. **Incohérence des chemins** : Les données JSON utilisent des chemins avec extensions (`.png`) mais le gestionnaire d'assets charge les images sans extensions
2. **Images manquantes** : Certains fichiers d'images référencés dans les JSON n'existent pas
3. **Structure de dossiers incorrecte** : Les dossiers d'images ne sont pas organisés comme attendu
4. **Extensions de fichiers** : Mismatch entre les extensions dans les JSON et les fichiers réels

## 🛠️ Solutions Implémentées

### 1. Amélioration du Gestionnaire d'Assets

**Fichier modifié** : `UI/game_ui.py`

**Améliorations apportées** :
- **Gestion flexible des extensions** : Le gestionnaire accepte maintenant les chemins avec et sans extensions
- **Images par défaut** : Création automatique d'images par défaut quand une image est manquante
- **Logs de debug** : Messages détaillés pour identifier les problèmes
- **Fallback intelligent** : Tentative de chargement avec différentes variations du nom de fichier

### 2. Scripts de Diagnostic

**Nouveaux fichiers créés** :

#### `check_image_structure.py`
```bash
python check_image_structure.py
```
- Vérifie la structure des dossiers d'images
- Compte les images dans chaque dossier
- Identifie les images manquantes
- Suggère des corrections

#### `test_images.py`
```bash
python test_images.py
```
- Teste le chargement des images via le gestionnaire d'assets
- Vérifie les références dans les fichiers JSON
- Teste des images spécifiques

#### `generate_default_images.py`
```bash
python generate_default_images.py
```
- Identifie automatiquement les images manquantes
- Crée des images par défaut colorées selon le type d'entité
- Demande confirmation avant création

## 📋 Étapes de Résolution

### Étape 1 : Diagnostic
```bash
cd JeuDeCarte
python check_image_structure.py
```

### Étape 2 : Test du Gestionnaire
```bash
python test_images.py
```

### Étape 3 : Création d'Images par Défaut (si nécessaire)
```bash
python generate_default_images.py
```

### Étape 4 : Test du Jeu
```bash
python main.py
```

## 🎨 Types d'Images par Défaut

Le système crée automatiquement des images par défaut avec des couleurs spécifiques :

- **Héros** : Fond marron avec texte doré
- **Unités** : Fond vert avec texte vert clair  
- **Cartes** : Fond bleu nuit avec texte bleu clair
- **Autres** : Fond gris avec texte gris clair

## 📁 Structure Attendue

```
JeuDeCarte/
├── Assets/
│   └── img/
│       ├── Hero/          # Images des héros (1.png, 2.png, etc.)
│       ├── Crea/          # Images des unités (1.png, 2.png, etc.)
│       ├── Carte/         # Images des cartes (DosCarte1.png, etc.)
│       └── Symbols/       # Symboles élémentaires (feu.png, eau.png, etc.)
├── Data/
│   ├── heroes.json        # Références: "image_path": "Hero/1.png"
│   ├── units.json         # Références: "image_path": "Crea/1.png"
│   └── cards.json         # Références: "image_path": "Carte/DosCarte1.png"
```

## 🔧 Corrections Manuelles

### Si les images existent mais ne se chargent pas :

1. **Vérifier les extensions** :
   - Les JSON utilisent `.png` mais les fichiers sont `.jpg` (ou vice versa)
   - Solution : Renommer les fichiers ou modifier les JSON

2. **Vérifier les noms de fichiers** :
   - Les JSON référencent `Hero/1.png` mais le fichier s'appelle `Hero/hero1.png`
   - Solution : Renommer les fichiers ou modifier les JSON

3. **Vérifier la structure** :
   - Les images sont dans `Assets/images/` au lieu de `Assets/img/`
   - Solution : Déplacer les dossiers ou modifier le code

### Si les images n'existent pas :

1. **Utiliser le générateur automatique** :
   ```bash
   python generate_default_images.py
   ```

2. **Créer manuellement** :
   - Créer les dossiers manquants
   - Ajouter des images PNG de 200x288 pixels
   - Respecter la nomenclature des JSON

## 🐛 Logs de Debug

Le système génère maintenant des logs détaillés :

```
[ASSETS] Image chargée : Hero/1.png -> (200, 288)
[DEBUG] Image héros affichée : Hero/1.png -> (200, 288)
[ASSETS] Image non trouvée : Hero/999.png, création d'une image par défaut
```

## ✅ Vérification

Après application des corrections, vous devriez voir :

1. **Dans le deck builder** : Toutes les images des héros et unités s'affichent
2. **Dans les logs** : Messages de succès pour le chargement des images
3. **Pas d'erreurs** : Aucun message d'erreur lié aux images

## 🆘 Support

Si les problèmes persistent :

1. **Vérifiez les permissions** : Le jeu doit pouvoir lire les dossiers d'images
2. **Vérifiez l'espace disque** : Assurez-vous d'avoir assez d'espace pour les images
3. **Vérifiez les dépendances** : `Pillow` est nécessaire pour le générateur d'images
4. **Consultez les logs** : Les messages d'erreur donnent des indices sur le problème

## 📝 Notes Techniques

- **Format d'images** : PNG recommandé pour la transparence
- **Taille standard** : 200x288 pixels selon la documentation
- **Compression** : Éviter les images trop lourdes pour les performances
- **Nommage** : Utiliser des noms simples sans espaces ni caractères spéciaux