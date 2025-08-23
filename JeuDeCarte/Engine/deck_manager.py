# deck_manager.py - Gestionnaire de decks pour JeuDeCarte

import json
import os
import shutil
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import hashlib

class DeckValidationError(Exception):
    """Exception levée lors d'une erreur de validation de deck"""
    pass

class Deck:
    """Classe représentant un deck complet"""
    
    def __init__(self, name: str, hero: Dict[str, Any] = None, units: List[Dict[str, Any]] = None, 
                 cards: List[Dict[str, Any]] = None, customizations: Dict[str, Any] = None):
        self.name = name
        self.hero = hero or {}
        self.units = units or []
        self.cards = cards or []
        self.customizations = customizations or {}
        self.created_date = datetime.now().isoformat()
        self.last_modified = datetime.now().isoformat()
        self.version = "1.0"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit le deck en dictionnaire pour la sauvegarde"""
        return {
            "name": self.name,
            "hero": self.hero,
            "units": self.units,
            "cards": self.cards,
            "customizations": self.customizations,
            "created_date": self.created_date,
            "last_modified": self.last_modified,
            "version": self.version
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Deck':
        """Crée un deck à partir d'un dictionnaire"""
        deck = cls(
            name=data.get("name", "Deck sans nom"),
            hero=data.get("hero"),
            units=data.get("units", []),
            cards=data.get("cards", []),
            customizations=data.get("customizations", {})
        )
        deck.created_date = data.get("created_date", datetime.now().isoformat())
        deck.last_modified = data.get("last_modified", datetime.now().isoformat())
        deck.version = data.get("version", "1.0")
        return deck

class DeckManager:
    """Gestionnaire principal des decks"""
    
    def __init__(self, save_directory: str = "JeuDeCarte/Decks"):
        self.save_directory = save_directory
        self.decks_file = os.path.join(save_directory, "decks.json")
        self.backup_directory = os.path.join(save_directory, "backups")
        self.decks: Dict[str, Deck] = {}
        self.current_deck_name: Optional[str] = None
        
        # Créer les dossiers nécessaires
        self._ensure_directories()
        
        # Charger les decks existants
        self.load_all_decks()
    
    def _ensure_directories(self):
        """Crée les dossiers nécessaires s'ils n'existent pas"""
        os.makedirs(self.save_directory, exist_ok=True)
        os.makedirs(self.backup_directory, exist_ok=True)
    
    def load_all_decks(self) -> bool:
        """Charge tous les decks depuis le fichier de sauvegarde"""
        try:
            if not os.path.exists(self.decks_file):
                print(f"[DECK MANAGER] Aucun fichier de decks trouvé, création d'un nouveau")
                self._create_default_deck()
                return True
            
            with open(self.decks_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.decks.clear()
            for deck_data in data.get("decks", []):
                deck = Deck.from_dict(deck_data)
                self.decks[deck.name] = deck
            
            self.current_deck_name = data.get("current_deck")
            
            print(f"[DECK MANAGER] {len(self.decks)} decks chargés")
            return True
            
        except Exception as e:
            print(f"[ERREUR] Impossible de charger les decks: {e}")
            self._create_default_deck()
            return False
    
    def _create_default_deck(self):
        """Crée un deck par défaut si aucun deck n'existe"""
        default_deck = Deck("Deck par défaut")
        self.decks["Deck par défaut"] = default_deck
        self.current_deck_name = "Deck par défaut"
        self.save_all_decks()
    
    def save_all_decks(self) -> bool:
        """Sauvegarde tous les decks"""
        try:
            # Créer une sauvegarde avant d'écraser
            self._create_backup()
            
            data = {
                "decks": [deck.to_dict() for deck in self.decks.values()],
                "current_deck": self.current_deck_name,
                "last_save": datetime.now().isoformat()
            }
            
            with open(self.decks_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"[DECK MANAGER] {len(self.decks)} decks sauvegardés")
            return True
            
        except Exception as e:
            print(f"[ERREUR] Impossible de sauvegarder les decks: {e}")
            return False
    
    def _create_backup(self):
        """Crée une sauvegarde des decks"""
        try:
            if os.path.exists(self.decks_file):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_file = os.path.join(self.backup_directory, f"decks_backup_{timestamp}.json")
                shutil.copy2(self.decks_file, backup_file)
                
                # Garder seulement les 5 dernières sauvegardes
                self._cleanup_old_backups()
                
        except Exception as e:
            print(f"[ERREUR] Impossible de créer la sauvegarde: {e}")
    
    def _cleanup_old_backups(self, keep_count: int = 5):
        """Supprime les anciennes sauvegardes"""
        try:
            backup_files = []
            for filename in os.listdir(self.backup_directory):
                if filename.startswith("decks_backup_") and filename.endswith(".json"):
                    filepath = os.path.join(self.backup_directory, filename)
                    backup_files.append((filepath, os.path.getmtime(filepath)))
            
            # Trier par date de modification (plus récent en premier)
            backup_files.sort(key=lambda x: x[1], reverse=True)
            
            # Supprimer les anciennes sauvegardes
            for filepath, _ in backup_files[keep_count:]:
                os.remove(filepath)
                
        except Exception as e:
            print(f"[ERREUR] Impossible de nettoyer les sauvegardes: {e}")
    
    def create_deck(self, name: str) -> bool:
        """Crée un nouveau deck"""
        try:
            if name in self.decks:
                raise DeckValidationError(f"Un deck nommé '{name}' existe déjà")
            
            new_deck = Deck(name)
            self.decks[name] = new_deck
            self.current_deck_name = name
            
            self.save_all_decks()
            print(f"[DECK MANAGER] Nouveau deck créé: {name}")
            return True
            
        except Exception as e:
            print(f"[ERREUR] Impossible de créer le deck: {e}")
            return False
    
    def delete_deck(self, name: str) -> bool:
        """Supprime un deck"""
        try:
            if name not in self.decks:
                raise DeckValidationError(f"Deck '{name}' introuvable")
            
            if len(self.decks) <= 1:
                raise DeckValidationError("Impossible de supprimer le dernier deck")
            
            del self.decks[name]
            
            # Si le deck supprimé était le deck actuel, changer vers un autre
            if self.current_deck_name == name:
                self.current_deck_name = list(self.decks.keys())[0]
            
            self.save_all_decks()
            print(f"[DECK MANAGER] Deck supprimé: {name}")
            return True
            
        except Exception as e:
            print(f"[ERREUR] Impossible de supprimer le deck: {e}")
            return False
    
    def rename_deck(self, old_name: str, new_name: str) -> bool:
        """Renomme un deck"""
        try:
            if old_name not in self.decks:
                raise DeckValidationError(f"Deck '{old_name}' introuvable")
            
            if new_name in self.decks:
                raise DeckValidationError(f"Un deck nommé '{new_name}' existe déjà")
            
            deck = self.decks.pop(old_name)
            deck.name = new_name
            deck.last_modified = datetime.now().isoformat()
            self.decks[new_name] = deck
            
            # Mettre à jour le deck actuel si nécessaire
            if self.current_deck_name == old_name:
                self.current_deck_name = new_name
            
            self.save_all_decks()
            print(f"[DECK MANAGER] Deck renommé: {old_name} → {new_name}")
            return True
            
        except Exception as e:
            print(f"[ERREUR] Impossible de renommer le deck: {e}")
            return False
    
    def set_current_deck(self, name: str) -> bool:
        """Définit le deck actuel"""
        if name not in self.decks:
            print(f"[ERREUR] Deck '{name}' introuvable")
            return False
        
        self.current_deck_name = name
        self.save_all_decks()
        print(f"[DECK MANAGER] Deck actuel changé vers: {name}")
        return True
    
    def get_current_deck(self) -> Optional[Deck]:
        """Retourne le deck actuel"""
        if self.current_deck_name and self.current_deck_name in self.decks:
            return self.decks[self.current_deck_name]
        return None
    
    def get_deck_names(self) -> List[str]:
        """Retourne la liste des noms de decks"""
        return list(self.decks.keys())
    
    def update_deck(self, name: str, hero: Dict[str, Any] = None, units: List[Dict[str, Any]] = None,
                   cards: List[Dict[str, Any]] = None, customizations: Dict[str, Any] = None) -> bool:
        """Met à jour un deck"""
        try:
            if name not in self.decks:
                raise DeckValidationError(f"Deck '{name}' introuvable")
            
            deck = self.decks[name]
            
            if hero is not None:
                deck.hero = hero
            if units is not None:
                deck.units = units
            if cards is not None:
                deck.cards = cards
            if customizations is not None:
                deck.customizations = customizations
            
            deck.last_modified = datetime.now().isoformat()
            
            # Valider le deck avant de sauvegarder
            self.validate_deck(deck)
            
            self.save_all_decks()
            print(f"[DECK MANAGER] Deck mis à jour: {name}")
            return True
            
        except Exception as e:
            print(f"[ERREUR] Impossible de mettre à jour le deck: {e}")
            return False
    
    def validate_deck(self, deck: Deck) -> bool:
        """Valide un deck selon les règles du jeu"""
        errors = []
        
        # Vérifier le héros
        if not deck.hero:
            errors.append("Le deck doit contenir exactement 1 héros")
        elif isinstance(deck.hero, dict) and len(deck.hero) == 0:
            errors.append("Le deck doit contenir exactement 1 héros")
        
        # Vérifier les unités
        if len(deck.units) > 5:
            errors.append("Le deck ne peut contenir que 5 unités maximum")
        
        # Vérifier les cartes
        if len(deck.cards) != 30:
            errors.append("Le deck doit contenir exactement 30 cartes")
        
        # Vérifier les doublons de cartes
        card_counts = {}
        for card in deck.cards:
            card_name = card.get("name", "Carte sans nom")
            card_counts[card_name] = card_counts.get(card_name, 0) + 1
        
        for card_name, count in card_counts.items():
            if count > 2:
                errors.append(f"La carte '{card_name}' ne peut apparaître que 2 fois maximum")
        
        # Vérifier les doublons d'unités
        unit_names = [unit.get("name", "Unité sans nom") for unit in deck.units]
        if len(unit_names) != len(set(unit_names)):
            errors.append("Les unités doivent être différentes")
        
        if errors:
            raise DeckValidationError("Erreurs de validation:\n" + "\n".join(f"• {error}" for error in errors))
        
        return True
    
    def get_deck_info(self, name: str) -> Dict[str, Any]:
        """Retourne les informations détaillées d'un deck"""
        if name not in self.decks:
            return {}
        
        deck = self.decks[name]
        
        # Compter les cartes par élément
        element_counts = {}
        for card in deck.cards:
            element = card.get("element", "NEUTRE")
            element_counts[element] = element_counts.get(element, 0) + 1
        
        # Compter les cartes par coût
        cost_counts = {}
        for card in deck.cards:
            cost = card.get("cost", 0)
            cost_counts[cost] = cost_counts.get(cost, 0) + 1
        
        return {
            "name": deck.name,
            "hero": deck.hero.get("name", "Aucun héros") if deck.hero else "Aucun héros",
            "units_count": len(deck.units),
            "cards_count": len(deck.cards),
            "element_distribution": element_counts,
            "cost_distribution": cost_counts,
            "created_date": deck.created_date,
            "last_modified": deck.last_modified,
            "is_valid": self._is_deck_valid(deck)
        }
    
    def _is_deck_valid(self, deck: Deck) -> bool:
        """Vérifie si un deck est valide sans lever d'exception"""
        try:
            self.validate_deck(deck)
            return True
        except DeckValidationError:
            return False
    
    def export_deck(self, name: str, filepath: str) -> bool:
        """Exporte un deck vers un fichier"""
        try:
            if name not in self.decks:
                raise DeckValidationError(f"Deck '{name}' introuvable")
            
            deck = self.decks[name]
            export_data = {
                "deck": deck.to_dict(),
                "export_date": datetime.now().isoformat(),
                "version": "1.0"
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            print(f"[DECK MANAGER] Deck exporté: {name} → {filepath}")
            return True
            
        except Exception as e:
            print(f"[ERREUR] Impossible d'exporter le deck: {e}")
            return False
    
    def import_deck(self, filepath: str) -> bool:
        """Importe un deck depuis un fichier"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            deck_data = data.get("deck", {})
            deck = Deck.from_dict(deck_data)
            
            # Valider le deck importé
            self.validate_deck(deck)
            
            # Ajouter le deck (avec suffixe si nom en conflit)
            original_name = deck.name
            counter = 1
            while deck.name in self.decks:
                deck.name = f"{original_name} ({counter})"
                counter += 1
            
            self.decks[deck.name] = deck
            self.save_all_decks()
            
            print(f"[DECK MANAGER] Deck importé: {deck.name}")
            return True
            
        except Exception as e:
            print(f"[ERREUR] Impossible d'importer le deck: {e}")
            return False
    
    def get_deck_statistics(self) -> Dict[str, Any]:
        """Retourne les statistiques globales des decks"""
        stats = {
            "total_decks": len(self.decks),
            "valid_decks": 0,
            "invalid_decks": 0,
            "most_used_heroes": {},
            "most_used_units": {},
            "most_used_cards": {},
            "average_deck_size": 0
        }
        
        hero_counts = {}
        unit_counts = {}
        card_counts = {}
        total_cards = 0
        
        for deck in self.decks.values():
            if self._is_deck_valid(deck):
                stats["valid_decks"] += 1
            else:
                stats["invalid_decks"] += 1
            
            # Compter les héros
            if deck.hero:
                hero_name = deck.hero.get("name", "Héros inconnu")
                hero_counts[hero_name] = hero_counts.get(hero_name, 0) + 1
            
            # Compter les unités
            for unit in deck.units:
                unit_name = unit.get("name", "Unité inconnue")
                unit_counts[unit_name] = unit_counts.get(unit_name, 0) + 1
            
            # Compter les cartes
            for card in deck.cards:
                card_name = card.get("name", "Carte inconnue")
                card_counts[card_name] = card_counts.get(card_name, 0) + 1
            
            total_cards += len(deck.cards)
        
        # Calculer les moyennes et trier
        if self.decks:
            stats["average_deck_size"] = total_cards / len(self.decks)
        
        stats["most_used_heroes"] = dict(sorted(hero_counts.items(), key=lambda x: x[1], reverse=True)[:5])
        stats["most_used_units"] = dict(sorted(unit_counts.items(), key=lambda x: x[1], reverse=True)[:10])
        stats["most_used_cards"] = dict(sorted(card_counts.items(), key=lambda x: x[1], reverse=True)[:10])
        
        return stats

    def create_ai_deck(self) -> Deck:
        """Crée un deck IA pour les combats (alias de create_default_ai_deck)"""
        return self.create_default_ai_deck()
    
    def create_default_ai_deck(self) -> Deck:
        """Crée un deck IA par défaut pour les combats"""
        try:
            # Charger les données de base avec des chemins absolus
            import os
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            heroes_file = os.path.join(base_dir, "Data", "heroes.json")
            units_file = os.path.join(base_dir, "Data", "units.json")
            cards_file = os.path.join(base_dir, "Data", "cards.json")
            
            print(f"[DECK MANAGER] Chargement des fichiers de données:")
            print(f"  - Heroes: {heroes_file}")
            print(f"  - Units: {units_file}")
            print(f"  - Cards: {cards_file}")
            
            with open(heroes_file, 'r', encoding='utf-8') as f:
                heroes_data = json.load(f)
            
            with open(units_file, 'r', encoding='utf-8') as f:
                units_data = json.load(f)
            
            with open(cards_file, 'r', encoding='utf-8') as f:
                cards_data = json.load(f)
            
            # Vérifier que les données sont des listes
            if not isinstance(heroes_data, list):
                print(f"[ERREUR] Les données des héros ne sont pas une liste: {type(heroes_data)}")
                return Deck(name="IA Adversaire")
            
            if not isinstance(units_data, list):
                print(f"[ERREUR] Les données des unités ne sont pas une liste: {type(units_data)}")
                return Deck(name="IA Adversaire")
            
            if not isinstance(cards_data, list):
                print(f"[ERREUR] Les données des cartes ne sont pas une liste: {type(cards_data)}")
                return Deck(name="IA Adversaire")
            
            print(f"[DECK MANAGER] Données chargées: {len(heroes_data)} héros, {len(units_data)} unités, {len(cards_data)} cartes")
            
            # Sélectionner un héros aléatoire
            import random
            
            # Vérifier que les héros sont des dictionnaires valides
            valid_heroes = [hero for hero in heroes_data if isinstance(hero, dict) and 'name' in hero]
            if not valid_heroes:
                print(f"[ERREUR] Aucun héros valide trouvé dans les données")
                return Deck(name="IA Adversaire")
            
            ai_hero = random.choice(valid_heroes)
            
            # Sélectionner 5 unités aléatoires
            valid_units = [unit for unit in units_data if isinstance(unit, dict) and 'name' in unit]
            if len(valid_units) < 5:
                print(f"[ERREUR] Pas assez d'unités valides trouvées ({len(valid_units)}/5)")
                return Deck(name="IA Adversaire")
            
            ai_units = random.sample(valid_units, 5)
            
            # Sélectionner 30 cartes aléatoires en respectant la règle des 2 copies max
            ai_cards = []
            card_counts = {}  # Dictionnaire pour compter les copies de chaque carte
            
            # Créer une liste de toutes les cartes disponibles (avec doublons pour permettre 2 copies)
            available_cards = []
            for card in cards_data:
                # Vérifier que la carte est bien un dictionnaire
                if not isinstance(card, dict):
                    print(f"[ERREUR] Carte invalide (pas un dictionnaire): {card}")
                    continue
                
                # Vérifier que la carte a un nom
                if 'name' not in card:
                    print(f"[ERREUR] Carte sans nom: {card}")
                    continue
                
                # Ajouter chaque carte 2 fois pour permettre 2 copies max
                available_cards.append(card)
                available_cards.append(card)
            
            # Mélanger la liste pour randomiser
            random.shuffle(available_cards)
            
            # Sélectionner les 30 premières cartes
            selected_cards = available_cards[:30]
            
            # Créer le deck final en respectant les doublons
            final_cards = []
            card_counts = {}
            
            for card in selected_cards:
                # Vérifier que la carte est valide
                if not isinstance(card, dict) or 'name' not in card:
                    print(f"[ERREUR] Carte invalide dans la sélection: {card}")
                    continue
                
                card_name = card.get('name', 'Carte inconnue')
                current_count = card_counts.get(card_name, 0)
                
                if current_count < 2:
                    final_cards.append(card)
                    card_counts[card_name] = current_count + 1
                else:
                    # Chercher une carte alternative
                    alternative_found = False
                    for alt_card in available_cards[30:]:  # Utiliser les cartes restantes
                        if not isinstance(alt_card, dict) or 'name' not in alt_card:
                            continue
                        
                        alt_name = alt_card.get('name', 'Carte inconnue')
                        alt_count = card_counts.get(alt_name, 0)
                        
                        if alt_count < 2:
                            final_cards.append(alt_card)
                            card_counts[alt_name] = alt_count + 1
                            alternative_found = True
                            break
                    
                    if not alternative_found:
                        # Si aucune alternative, utiliser la carte originale
                        final_cards.append(card)
                        card_counts[card_name] = current_count + 1
            
            ai_cards = final_cards
            
            # Créer le deck IA
            ai_deck = Deck(
                name="IA Adversaire",
                hero=ai_hero,
                units=ai_units,
                cards=ai_cards
            )
            
            # Vérifier que le deck IA est valide
            try:
                self.validate_deck(ai_deck)
                print(f"[DECK MANAGER] Deck IA créé avec succès: {len(ai_units)} unités, {len(ai_cards)} cartes")
                
                # Log des statistiques du deck
                card_names = []
                for card in ai_cards:
                    if isinstance(card, dict) and 'name' in card:
                        card_names.append(card.get('name', 'Carte inconnue'))
                    else:
                        card_names.append('Carte invalide')
                
                from collections import Counter
                card_counter = Counter(card_names)
                print(f"[DECK MANAGER] Distribution des cartes:")
                for card_name, count in card_counter.most_common(10):
                    print(f"  - {card_name}: {count} copies")
                
            except DeckValidationError as e:
                print(f"[ERREUR] Deck IA invalide: {e}")
                print(f"[DEBUG] Héros: {ai_hero.get('name', 'N/A') if isinstance(ai_hero, dict) and ai_hero else 'None'}")
                print(f"[DEBUG] Unités: {[u.get('name', 'N/A') if isinstance(u, dict) else 'Unité invalide' for u in ai_units]}")
                print(f"[DEBUG] Cartes: {len(ai_cards)} cartes")
                
                # Log détaillé des cartes pour debug
                card_names = []
                for card in ai_cards:
                    if isinstance(card, dict) and 'name' in card:
                        card_names.append(card.get('name', 'Carte inconnue'))
                    else:
                        card_names.append('Carte invalide')
                
                from collections import Counter
                card_counter = Counter(card_names)
                print(f"[DEBUG] Distribution des cartes (pour debug):")
                for card_name, count in card_counter.items():
                    if count > 2:
                        print(f"  ❌ {card_name}: {count} copies (TROP!)")
                    else:
                        print(f"  ✅ {card_name}: {count} copies")
                
                # Retourner un deck minimal valide
                return Deck(name="IA Adversaire")
            
            return ai_deck
            
        except FileNotFoundError as e:
            print(f"[ERREUR] Fichier de données manquant: {e}")
            print(f"[ERREUR] Vérifiez que les fichiers heroes.json, units.json et cards.json existent dans le dossier Data")
            # Retourner un deck minimal en cas d'erreur
            return Deck(name="IA Adversaire")
        except json.JSONDecodeError as e:
            print(f"[ERREUR] Erreur de format JSON dans les fichiers de données: {e}")
            # Retourner un deck minimal en cas d'erreur
            return Deck(name="IA Adversaire")
        except Exception as e:
            print(f"[ERREUR] Impossible de créer le deck IA: {e}")
            # Retourner un deck minimal en cas d'erreur
            return Deck(name="IA Adversaire")

# Instance globale du gestionnaire
import os
# Utiliser un chemin absolu basé sur le répertoire du fichier deck_manager.py
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
decks_dir = os.path.join(project_root, "Decks")
deck_manager = DeckManager(decks_dir)