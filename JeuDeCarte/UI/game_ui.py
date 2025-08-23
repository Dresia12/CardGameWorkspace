import pygame
import sys
import os
import logging
import time
import json
from typing import Optional, List, Tuple, Dict, Any

# Configuration du logging
def setup_logging():
    """Configure le système de logging"""
    # Créer le dossier logs s'il n'existe pas
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Nom du fichier avec timestamp
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    log_filename = f"logs/combat_debug_{timestamp}.log"
    
    # Configuration du logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename, encoding='utf-8'),
            logging.StreamHandler()  # Garde aussi l'affichage console
        ]
    )
    
    return logging.getLogger(__name__)

# Initialiser le logger
logger = setup_logging()

# Imports des gestionnaires
import os

# Ajouter le chemin du projet au sys.path
project_root = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, project_root)

from Engine.deck_manager import deck_manager
from Engine.hero_customization_manager import hero_customization_manager
from Engine.models import Ability, Card, Hero, Unit
from Engine.effects_database_manager import EffectsDatabaseManager

# Import du système de matchmaking Steam
from UI.steam_matchmaking_ui import SteamMatchmakingUI

# Enum pour les types d'actions multijoueur
class ActionType:
    PLAY_CARD = "play_card"
    USE_ABILITY = "use_ability"
    END_TURN = "end_turn"

# Configuration de l'écran
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
FPS = 60

# Couleurs
COLORS = {
    'deep_black': (10, 10, 20),
    'black': (0, 0, 0),
    'white': (255, 255, 255),
    'gold': (255, 215, 0),
    'light_gold': (255, 235, 100),
    'yellow': (255, 255, 0),
    'silver': (192, 192, 192),
    'gray': (128, 128, 128),
    'dark_gray': (64, 64, 64),
    'royal_blue': (65, 105, 225),
    'light_blue': (173, 216, 230),
    'crimson': (220, 20, 60),
    'ruby_red': (155, 17, 30),
    'orange': (255, 165, 0),
    'deep_blue': (25, 25, 112),
    'green': (0, 255, 0),
    'blue': (0, 0, 255),
    'purple': (128, 0, 128),
    'red': (255, 0, 0),
    'cyan': (0, 255, 255)
}

class GameUI:
    """Interface principale du jeu"""
    
    def __init__(self):
        print(f"[DEBUG GAMEUI] Initialisation de GameUI")
        pygame.init()
        print(f"[DEBUG GAMEUI] Pygame initialisé")
        
        # Initialiser le mixer pour l'audio
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            print("[AUDIO] Mixer pygame initialisé avec succès")
        except Exception as e:
            print(f"[ERREUR] Impossible d'initialiser le mixer : {e}")
        
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Jeu de Cartes")
        self.clock = pygame.time.Clock()
        self.running = True
        self.fullscreen = False
        self.current_screen = "main_menu"
        self.previous_screen = None
        print(f"[DEBUG GAMEUI] Écran initialisé, current_screen: {self.current_screen}")
        
        # Polices
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)
        
        # Gestionnaire d'assets
        self.asset_manager = AssetManager()
        self.asset_manager.load_assets()
        
        # Écrans
        print(f"[DEBUG GAMEUI] Création des écrans...")
        self.screens = {
            "main_menu": MainMenuScreen(self),
            "pre_combat": PreCombatScreen(self),
            "deck_builder": DeckBuilderScreen(self),
            "combat": CombatScreen(self),
            "hero_customization": HeroCustomizationScreen(self),
            "matchmaking": MatchmakingScreen(self)
        }
        print(f"[DEBUG GAMEUI] Écrans créés: {list(self.screens.keys())}")
        
        # Audio
        self.audio_available = pygame.mixer.get_init() is not None
        if self.audio_available:
            self.play_background_music()
    
    def run(self):
        """Boucle principale du jeu"""
        print(f"[DEBUG RUN] Début de la boucle principale")
        print(f"[DEBUG RUN] Écran actuel: {self.current_screen}")
        print(f"[DEBUG RUN] Écrans disponibles: {list(self.screens.keys())}")
        
        try:
            while self.running:
                print(f"[DEBUG] Boucle principale - Frame, self.running = {self.running}")
                # Gestion des événements
                for event in pygame.event.get():
                    self.handle_event(event)
                
                print(f"[DEBUG] Après gestion des événements, self.running = {self.running}")
                
                # Dessiner le background dynamique en premier
                print(f"[DEBUG] Écran actuel: {self.current_screen}")
                self.draw_background(self.screen)
                
                # Mise à jour de l'écran actuel
                current_screen = self.screens.get(self.current_screen)
                if current_screen:
                    current_screen.update()
                    current_screen.draw(self.screen)
                else:
                    print(f"[DEBUG RUN] Écran actuel non trouvé: {self.current_screen}")
                
                # Mise à jour de l'affichage
                pygame.display.flip()
                self.clock.tick(FPS)
        except Exception as e:
            print(f"[DEBUG] Erreur dans la boucle principale: {e}")
            import traceback
            traceback.print_exc()
        
        print(f"[DEBUG RUN] Fin de la boucle principale")
        pygame.quit()
        sys.exit()
    
    def play_background_music(self, music_type="main"):
        """Joue la musique de fond
        
        Args:
            music_type (str): Type de musique à jouer
                - "main": MusicBoard.wav (musique principale)
                - "combat": MusicBoardHarp_V1.wav (musique de combat)
        """
        if not self.audio_available:
            print("[AUDIO] Audio non disponible")
            return
            
        try:
            project_root = os.path.join(os.path.dirname(__file__), '..')
            print(f"[AUDIO] Project root: {project_root}")
            
            if music_type == "combat":
                music_path = os.path.join(project_root, 'Assets', 'Music', 'MusicBoardHarp_V1.wav')
                music_name = "MusicBoardHarp_V1.wav"
            else:
                music_path = os.path.join(project_root, 'Assets', 'Music', 'MusicBoard.wav')
                music_name = "MusicBoard.wav"
            
            print(f"[AUDIO] Chemin musique: {music_path}")
            print(f"[AUDIO] Fichier existe: {os.path.exists(music_path)}")
            
            if os.path.exists(music_path):
                pygame.mixer.music.load(music_path)
                pygame.mixer.music.set_volume(0.5)  # Volume à 50%
                pygame.mixer.music.play(-1)
                print(f"[AUDIO] Musique de fond lancée : {music_name} (volume: 50%)")
            else:
                print(f"[ERREUR] Fichier musique introuvable : {music_path}")
                
        except Exception as e:
            print(f"[ERREUR] Impossible de jouer la musique de fond : {e}")
            import traceback
            traceback.print_exc()
    
    def handle_event(self, event):
        """Gestion des événements globaux"""
        if event.type == pygame.QUIT:
            self.running = False
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.handle_escape()
            elif event.key == pygame.K_F11:
                self.toggle_fullscreen()
        
        # Transmettre l'événement à l'écran actuel
        current_screen = self.screens.get(self.current_screen)
        if current_screen:
            print(f"[DEBUG EVENT] Événement transmis à l'écran: {self.current_screen}")
            current_screen.handle_event(event)
        else:
            print(f"[DEBUG EVENT] Écran actuel non trouvé: {self.current_screen}")
    
    def handle_escape(self):
        """Gestion de la touche Échap"""
        if self.current_screen == "main_menu":
            self.running = False
        else:
            self.change_screen("main_menu")
    
    def toggle_fullscreen(self):
        """Bascule entre plein écran et fenêtré"""
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    
    def change_screen(self, screen_name: str):
        """Change d'écran"""
        print(f"[DEBUG SCREEN] change_screen() appelé avec: {screen_name}")
        print(f"[DEBUG SCREEN] Écrans disponibles: {list(self.screens.keys())}")
        
        if screen_name in self.screens:
            print(f"[UI] Changement d'écran : {self.current_screen} → {screen_name}")
            
            # Gestion de la musique selon l'écran
            if self.current_screen == "combat" and screen_name != "combat":
                # Quitter le combat : remettre la musique principale
                self.play_background_music("main")
            elif screen_name == "combat" and self.current_screen != "combat":
                # Entrer en combat : musique de combat (gérée dans start_combat)
                pass
            
            # Mémoriser l'écran précédent pour gestion du retour
            self.previous_screen = self.current_screen
            self.current_screen = screen_name
            print(f"[DEBUG SCREEN] Écran actuel mis à jour: {self.current_screen}")
        else:
            print(f"[DEBUG SCREEN] Écran '{screen_name}' non trouvé!")

    def get_current_hero_element(self):
        """Détermine l'élément du héros actuel pour le background"""
        # Priorité 1: Héros en combat
        try:
            if hasattr(self, 'screens') and 'combat' in self.screens:
                combat_screen = self.screens['combat']
                if hasattr(combat_screen, 'player_hero') and combat_screen.player_hero:
                    if hasattr(combat_screen.player_hero, 'element'):
                        return combat_screen.player_hero.element
        except Exception as e:
            pass
        
        # Priorité 2: Héros sélectionné dans DeckBuilderScreen
        try:
            if hasattr(self, 'screens') and 'deck_builder' in self.screens:
                deck_builder = self.screens['deck_builder']
                if hasattr(deck_builder, 'selected_hero') and deck_builder.selected_hero:
                    if hasattr(deck_builder.selected_hero, 'element'):
                        return deck_builder.selected_hero.element
        except Exception as e:
            pass
        
        # Priorité 3: Héros du deck sauvegardé via le deck manager
        try:
            from Engine.deck_manager import deck_manager
            current_deck = deck_manager.get_current_deck()
            if current_deck and current_deck.hero:
                if hasattr(current_deck.hero, 'element'):
                    return current_deck.hero.element
                elif isinstance(current_deck.hero, dict) and 'element' in current_deck.hero:
                    return current_deck.hero['element']
        except Exception as e:
            pass
        
        # Fallback: élément neutre
        return "Neutre"

    def draw_background(self, screen):
        """Dessine le background dynamique basé sur l'élément du héros"""
        current_element = None
        
        try:
            current_element = self.get_current_hero_element()
            print(f"[DEBUG] Élément détecté: {current_element}")
            
            # Mapper les éléments aux noms de fichiers
            element_to_file = {
                "Feu": "Feu.png",
                "Eau": "Eau.png", 
                "Terre": "Terre.png",
                "Air": "Air.png",
                "Foudre": "Foudre.png",
                "Glace": "Glace.png",
                "Lumiere": "Lumiere.png",
                "Tenebres": "Tenebres.png",
                "Arcanique": "Arcanique.png",
                "Poison": "Poison.png",
                "Neant": "Neant.png",
                "Neutre": "Neutre.png"
            }
            
            background_file = element_to_file.get(current_element, "Neutre.png")
            print(f"[DEBUG] Fichier background: {background_file}")
            
            # Charger et afficher le background
            try:
                background_path = os.path.join(os.path.dirname(__file__), '..', 'Assets', 'img', 'Fond', background_file)
                print(f"[DEBUG] Chemin background: {background_path}")
                print(f"[DEBUG] Fichier existe: {os.path.exists(background_path)}")
                
                if os.path.exists(background_path):
                    background_image = pygame.image.load(background_path)
                    background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
                    screen.blit(background_image, (0, 0))
                    print(f"[DEBUG] Background affiché avec succès")
                else:
                    # Fallback: fond noir
                    screen.fill((0, 0, 0))
                    print(f"[DEBUG] Fichier background introuvable")
            except Exception as e:
                # Fallback: fond noir
                screen.fill((0, 0, 0))
                print(f"[DEBUG] Erreur lors du chargement: {e}")
                
        except Exception as e:
            # Fallback: fond noir
            screen.fill((0, 0, 0))
            print(f"[DEBUG] Erreur générale: {e}")
    
    def clear_screen_for_ui(self, screen):
        """Nettoie l'écran avec un overlay semi-transparent pour l'UI"""
        # Au lieu d'un overlay sur tout l'écran, on ne fait rien
        # Les écrans individuels devront gérer leur propre nettoyage
        pass

class AssetManager:
    """Gestionnaire d'assets (images, sons, fonts)"""
    
    IMAGE_SIZES = {
        'Hero': (200, 288),
        'Crea': (200, 288),
        'Carte': (200, 288),
        'Symbols': (34, 34),
        'Icons': (32, 32),
        'UI': (64, 64),
        'Backgrounds': (1920, 1080),
        'default': (200, 288)
    }
    
    def __init__(self):
        self.images = {}
        self.sounds = {}
        self.fonts = {}
        self.scaled_images_cache = {}
    
    def load_assets(self):
        """Charge tous les assets"""
        self.load_images()
        self.load_sounds()
        self.load_fonts()
    
    def load_images(self):
        """Charge les images"""
        try:
            project_root = os.path.join(os.path.dirname(__file__), '..')
            assets_path = os.path.join(project_root, 'Assets', 'img')
            
            print(f"[ASSETS] Recherche d'images dans : {assets_path}")
            
            for root, dirs, files in os.walk(assets_path):
                for file in files:
                    if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                        img_path = os.path.join(root, file)
                        # Obtenir le chemin relatif depuis le dossier img
                        rel_path = os.path.relpath(img_path, assets_path)
                        # Normaliser les séparateurs de chemin
                        img_name = rel_path.replace('\\', '/').replace('/', '/')
                        # Supprimer l'extension pour la clé de base
                        img_name_no_ext = os.path.splitext(img_name)[0]
                        
                        try:
                            # Charger l'image sans convert_alpha() d'abord
                            image = pygame.image.load(img_path)
                            
                            # Essayer de convertir seulement si pygame.display est initialisé
                            try:
                                image = image.convert_alpha()
                            except pygame.error:
                                # Si pygame.display n'est pas initialisé, on garde l'image sans conversion
                                print(f"[ASSETS] Image chargée sans conversion alpha: {img_name}")
                            
                            # Stocker l'image avec et sans extension pour la compatibilité
                            self.images[img_name_no_ext] = image
                            self.images[img_name] = image  # Avec extension
                            print(f"[ASSETS] Image chargée : {img_name} -> {image.get_size()}")
                        except Exception as e:
                            print(f"[ERREUR] Impossible de charger l'image {img_path}: {e}")
                                
        except Exception as e:
            print(f"[ERREUR] Impossible de charger les images: {e}")
    
    def get_image(self, name: str) -> Optional[pygame.Surface]:
        """Récupère une image avec gestion des chemins"""
        # Essayer d'abord le nom exact
        if name in self.images:
            return self.images[name]
        
        # Essayer sans extension si le nom en a une
        if name.endswith(('.png', '.jpg', '.jpeg')):
            name_no_ext = os.path.splitext(name)[0]
            if name_no_ext in self.images:
                return self.images[name_no_ext]
        
        # Essayer avec extension si le nom n'en a pas
        for ext in ['.png', '.jpg', '.jpeg']:
            name_with_ext = name + ext
            if name_with_ext in self.images:
                return self.images[name_with_ext]
        
        # Si aucune image trouvée, créer une image par défaut
        print(f"[ASSETS] Image non trouvée : {name}, création d'une image par défaut")
        return self._create_default_image(name)
    
    def _create_default_image(self, name: str) -> pygame.Surface:
        """Crée une image par défaut quand l'image n'est pas trouvée"""
        # Créer une surface de 200x288 pixels (taille standard selon la documentation)
        surface = pygame.Surface((200, 288))
        
        # Couleur de fond selon le type
        if 'Hero' in name:
            bg_color = (100, 50, 50)  # Rouge foncé pour les héros
            text_color = (255, 200, 200)
        elif 'Crea' in name:
            bg_color = (50, 100, 50)  # Vert foncé pour les créatures
            text_color = (200, 255, 200)
        elif 'Carte' in name:
            bg_color = (50, 50, 100)  # Bleu foncé pour les cartes
            text_color = (200, 200, 255)
        else:
            bg_color = (80, 80, 80)   # Gris par défaut
            text_color = (200, 200, 200)
        
        # Remplir le fond
        surface.fill(bg_color)
        
        # Ajouter un texte pour indiquer que l'image est manquante
        try:
            font = pygame.font.Font(None, 24)
            text = font.render("Image manquante", True, text_color)
            text_rect = text.get_rect(center=(100, 144))
            surface.blit(text, text_rect)
            
            # Ajouter le nom de l'image
            name_text = font.render(name, True, text_color)
            name_rect = name_text.get_rect(center=(100, 170))
            surface.blit(name_text, name_rect)
        except:
            pass  # Si la police n'est pas disponible, on garde juste le fond
        
        # Stocker l'image pour éviter de la recréer
        self.images[name] = surface
        return surface
    
    def load_sounds(self):
        """Charge les sons"""
        pass
    
    def load_fonts(self):
        """Charge les polices"""
        pass
    
    def get_sound(self, name: str) -> Optional[pygame.mixer.Sound]:
        """Récupère un son"""
        return self.sounds.get(name)

class Screen:
    """Classe de base pour tous les écrans"""
    
    def __init__(self, game_ui: GameUI):
        self.game_ui = game_ui
        self.buttons = []
    
    def update(self):
        """Mise à jour de l'écran"""
        pass
    
    def draw(self, screen: pygame.Surface):
        """Dessin de l'écran"""
        pass
    
    def handle_event(self, event):
        """Gestion des événements de l'écran"""
        pass

class Button:
    """Bouton cliquable"""
    
    def __init__(self, x: int, y: int, width: int, height: int, text: str, 
                 color: Tuple[int, int, int], text_color: Tuple[int, int, int], action, 
                 tooltip: str = None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.text_color = text_color
        self.action = action
        self.hover = False
        self.tooltip = tooltip
        
    def draw(self, screen: pygame.Surface):
        """Dessine le bouton"""
        color = self.color if not self.hover else tuple(min(255, c + 30) for c in self.color)
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, COLORS['white'], self.rect, 2)
        
        font = pygame.font.Font(None, self._calculate_optimal_font_size())
        text_surface = font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
    
    def _calculate_optimal_font_size(self) -> int:
        """Calcule la taille de police optimale"""
        font_size = 24
        while font_size > 12:
            font = pygame.font.Font(None, font_size)
            text_surface = font.render(self.text, True, self.text_color)
            if text_surface.get_width() <= self.rect.width - 20:
                return font_size
            font_size -= 2
        return 12
    
    def is_clicked(self, pos: Tuple[int, int]) -> bool:
        """Vérifie si le bouton est cliqué"""
        return self.rect.collidepoint(pos)
    
    def update_hover(self, pos: Tuple[int, int]):
        """Met à jour l'état de hover"""
        self.hover = self.rect.collidepoint(pos)
    
    def draw_tooltip(self, screen: pygame.Surface, mouse_pos: Tuple[int, int]):
        """Dessine le tooltip si le bouton est survolé"""
        if self.hover and self.tooltip:
            # Calculer la position du tooltip (au-dessus du bouton)
            tooltip_x = mouse_pos[0]
            tooltip_y = self.rect.top - 10
            
            # Créer le texte du tooltip
            font = pygame.font.Font(None, 20)
            lines = self.tooltip.split('\n')
            
            # Calculer la taille du tooltip
            max_width = 0
            total_height = 0
            line_surfaces = []
            
            for line in lines:
                line_surface = font.render(line, True, COLORS['white'])
                line_surfaces.append(line_surface)
                max_width = max(max_width, line_surface.get_width())
                total_height += line_surface.get_height() + 2
            
            # Ajuster la position pour que le tooltip reste dans l'écran
            if tooltip_x + max_width > SCREEN_WIDTH:
                tooltip_x = SCREEN_WIDTH - max_width - 10
            if tooltip_y - total_height < 0:
                tooltip_y = self.rect.bottom + 10
            
            # Dessiner le fond du tooltip
            tooltip_rect = pygame.Rect(tooltip_x - 5, tooltip_y - total_height - 5, 
                                     max_width + 10, total_height + 10)
            pygame.draw.rect(screen, (*COLORS['deep_black'], 230), tooltip_rect, border_radius=5)
            pygame.draw.rect(screen, COLORS['gold'], tooltip_rect, 2, border_radius=5)
            
            # Dessiner le texte du tooltip
            current_y = tooltip_y - total_height
            for line_surface in line_surfaces:
                screen.blit(line_surface, (tooltip_x, current_y))
                current_y += line_surface.get_height() + 2

class DropdownMenu:
    """Menu déroulant"""
    
    def __init__(self, x: int, y: int, width: int, height: int, options: List[str], 
                 default_option: str = "all", font_size: int = 24):
        self.rect = pygame.Rect(x, y, width, height)
        self.options = options
        self.selected_option = default_option
        self.is_open = False
        self.font_size = font_size
        
    def draw(self, screen: pygame.Surface):
        """Dessine le menu déroulant"""
        # Fond principal
        pygame.draw.rect(screen, COLORS['dark_gray'], self.rect)
        pygame.draw.rect(screen, COLORS['white'], self.rect, 2)
        
        # Texte sélectionné
        font = pygame.font.Font(None, self.font_size)
        text_surface = font.render(self.selected_option, True, COLORS['white'])
        text_rect = text_surface.get_rect(midleft=(self.rect.x + 10, self.rect.centery))
        screen.blit(text_surface, text_rect)
        
        # Flèche
        arrow_points = [
            (self.rect.right - 20, self.rect.centery - 5),
            (self.rect.right - 20, self.rect.centery + 5),
            (self.rect.right - 10, self.rect.centery)
        ]
        pygame.draw.polygon(screen, COLORS['white'], arrow_points)
        
        # Options si ouvert
        if self.is_open:
            for i, option in enumerate(self.options):
                option_rect = pygame.Rect(self.rect.x, self.rect.bottom + i * 30, self.rect.width, 30)
                pygame.draw.rect(screen, COLORS['dark_gray'], option_rect)
                pygame.draw.rect(screen, COLORS['white'], option_rect, 1)
                
                option_surface = font.render(option, True, COLORS['white'])
                option_text_rect = option_surface.get_rect(midleft=(option_rect.x + 10, option_rect.centery))
                screen.blit(option_surface, option_text_rect)
    
    def handle_click(self, pos: Tuple[int, int]) -> Optional[str]:
        """Gère les clics sur le menu"""
        if self.rect.collidepoint(pos):
            self.is_open = not self.is_open
            return None
        
        if self.is_open:
            for i, option in enumerate(self.options):
                option_rect = pygame.Rect(self.rect.x, self.rect.bottom + i * 30, self.rect.width, 30)
                if option_rect.collidepoint(pos):
                    self.selected_option = option
                    self.is_open = False
                    return option
        
        self.is_open = False
        return None
    
    def close(self):
        """Ferme le menu"""
        self.is_open = False

class MainMenuScreen(Screen):
    """Écran du menu principal"""
    
    def __init__(self, game_ui: GameUI):
        super().__init__(game_ui)
        self.setup_buttons()
    
    def setup_buttons(self):
        """Configure les boutons du menu principal"""
        button_width = 300
        button_height = 60
        start_y = 400
        
        # Bouton Jouer
        self.buttons.append(Button(
            SCREEN_WIDTH // 2 - button_width // 2,
            start_y,
            button_width,
            button_height,
            "JOUER",
            COLORS['gold'],
            COLORS['deep_black'],
            lambda: self.game_ui.change_screen("pre_combat")
        ))
        
        # Bouton DECK
        self.buttons.append(Button(
            SCREEN_WIDTH // 2 - button_width // 2,
            start_y + 80,
            button_width,
            button_height,
            "DECK",
            COLORS['royal_blue'],
            COLORS['white'],
            lambda: self.game_ui.change_screen("deck_builder")
        ))
        
        # Bouton BOUTIQUE
        self.buttons.append(Button(
            SCREEN_WIDTH // 2 - button_width // 2,
            start_y + 160,
            button_width,
            button_height,
            "BOUTIQUE",
            COLORS['ruby_red'],
            COLORS['white'],
            lambda: print("BOUTIQUE - À implémenter")
        ))
        
        # Bouton OPTIONS
        self.buttons.append(Button(
            SCREEN_WIDTH // 2 - button_width // 2,
            start_y + 240,
            button_width,
            button_height,
            "OPTIONS",
            COLORS['silver'],
            COLORS['deep_black'],
            lambda: print("OPTIONS - À implémenter")
        ))
        
        # Bouton QUITTER
        self.buttons.append(Button(
            SCREEN_WIDTH // 2 - button_width // 2,
            start_y + 320,
            button_width,
            button_height,
            "QUITTER",
            COLORS['crimson'],
            COLORS['white'],
            lambda: setattr(self.game_ui, 'running', False)
        ))
    
    def draw(self, screen: pygame.Surface):
        """Dessin du menu principal"""
        # Le background est déjà dessiné par GameUI.draw_background()
        
        # Titre
        title = self.game_ui.font_large.render("JEU DE CARTES", True, COLORS['gold'])
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 200))
        screen.blit(title, title_rect)
        
        # Sous-titre
        subtitle = self.game_ui.font_medium.render("Aventure Fantasy", True, COLORS['white'])
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, 250))
        screen.blit(subtitle, subtitle_rect)
        
        # Boutons
        for button in self.buttons:
            button.draw(screen)
    
    def handle_event(self, event):
        """Gestion des événements du menu principal"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            for button in self.buttons:
                if button.is_clicked(mouse_pos):
                    button.action()
                    return


class MatchmakingScreen(Screen):
    """Écran de matchmaking multijoueur"""
    
    def __init__(self, game_ui: GameUI):
        super().__init__(game_ui)
        print(f"[DEBUG MATCHMAKING] MatchmakingScreen initialisé")
        
        # Créer l'interface de matchmaking Steam
        self.steam_matchmaking_ui = SteamMatchmakingUI(self.game_ui.screen)
        
        # Configurer le callback pour quand un match est trouvé
        print(f"[DEBUG MATCHMAKING] Configuration du callback _on_match_found")
        self.steam_matchmaking_ui.set_match_found_callback(self._on_match_found)
        print(f"[DEBUG MATCHMAKING] Callback configuré: {self.steam_matchmaking_ui.on_match_found}")
        
        print(f"[DEBUG MATCHMAKING] SteamMatchmakingUI initialisé")
    
    def _on_match_found(self, match_data):
        """Callback appelé quand un match est trouvé"""
        print(f"[DEBUG MATCHMAKING] Match trouvé ! Données: {match_data}")
        try:
            # Démarrer le VRAI combat multijoueur local
            print("[DEBUG MATCHMAKING] Démarrage du combat multijoueur local...")
            # Récupérer le deck du joueur depuis l'écran pré-combat
            pre_combat_screen = self.game_ui.screens.get("pre_combat")
            if pre_combat_screen and hasattr(pre_combat_screen, 'current_deck') and pre_combat_screen.current_deck:
                player_deck = pre_combat_screen.current_deck
                print(f"[DEBUG MATCHMAKING] Deck joueur trouvé: {player_deck.name if hasattr(player_deck, 'name') else 'Deck sans nom'}")
                # Déterminer si on est le joueur 1 ou 2 (basé sur l'ID du client actuel)
                current_player_id = self.steam_matchmaking_ui.user_info["id"]
                is_player1 = match_data.get('player1', {}).get('id') == current_player_id
                print(f"[DEBUG MATCHMAKING] Rôle: {'Joueur 1 (Hôte)' if is_player1 else 'Joueur 2 (Client)'}")
                # Démarrer le combat multijoueur avec synchronisation (sans changer d'écran tout de suite)
                combat_screen = self.game_ui.screens.get("combat")
                if combat_screen:
                    print("[DEBUG MATCHMAKING] Démarrage du combat multijoueur...")
                    combat_screen.set_multiplayer_mode(True, is_player1, match_data)
                    combat_screen.start_multiplayer_combat(player_deck, match_data)
                    print("[DEBUG MATCHMAKING] Attente que les deux joueurs soient prêts...")
                else:
                    print("[DEBUG MATCHMAKING] Erreur: Écran de combat non trouvé")
                    self.game_ui.change_screen("pre_combat")
            else:
                print("[DEBUG MATCHMAKING] Erreur: Deck du joueur non trouvé")
                self.game_ui.change_screen("pre_combat")
        except Exception as e:
            print(f"[DEBUG MATCHMAKING] Erreur lors du lancement du combat multijoueur: {e}")
            import traceback
            traceback.print_exc()
            self.game_ui.change_screen("pre_combat")
    
    def update(self):
        """Mise à jour de l'écran de matchmaking"""
        self.steam_matchmaking_ui.update()
    
    def draw(self, screen: pygame.Surface):
        """Dessin de l'écran de matchmaking"""
        self.steam_matchmaking_ui.draw(screen)
    
    def handle_event(self, event):
        """Gestion des événements de l'écran de matchmaking"""
        # Gérer le retour vers l'écran précédent
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.game_ui.change_screen("pre_combat")
            return
        
        # Configurer le callback de retour pour SteamMatchmakingUI
        self.steam_matchmaking_ui.on_back = lambda: self.game_ui.change_screen("pre_combat")
        
        # Passer l'événement à SteamMatchmakingUI
        self.steam_matchmaking_ui.handle_event(event)


class PreCombatScreen(Screen):
    """Écran de sélection avant combat"""
    
    def __init__(self, game_ui: GameUI):
        super().__init__(game_ui)
        print(f"[DEBUG PRE-COMBAT] PreCombatScreen initialisé")
        # Initialiser les variables de deck avant setup_buttons
        self.deck_valid = False
        self.deck_error = "Chargement..."
        self.current_deck = None
        self.load_deck_info()
        self.setup_buttons()
        print(f"[DEBUG PRE-COMBAT] PreCombatScreen setup terminé")
    
    def update(self):
        """Mise à jour de l'écran pre-combat"""
        # Recharger les informations du deck à chaque frame pour s'assurer qu'elles sont à jour
        self.load_deck_info()
    
    def setup_buttons(self):
        """Configure les boutons de l'écran pre-combat"""
        button_width = 300
        button_height = 60
        start_y = 400
        
        # Mettre à jour les boutons en fonction de la validité du deck
        self.buttons = [
            Button(
                SCREEN_WIDTH // 2 - button_width // 2,
                start_y,
                button_width,
                button_height,
                "COMBAT IA",
                COLORS['gold'],
                COLORS['deep_black'],
                self.start_ai_combat,
                "Lance un combat contre l'IA"
            ),
            Button(
                SCREEN_WIDTH // 2 - button_width // 2,
                start_y + 80,
                button_width,
                button_height,
                "VERSUS",
                COLORS['red'] if self.deck_valid else COLORS['gray'],  # Grisé si deck invalide
                COLORS['white'],
                self.start_matchmaking if self.deck_valid else self._show_deck_error,  # Callback différent si invalide
                "Lance un combat multijoueur" if self.deck_valid else "Deck invalide - Créez un deck valide d'abord"
            ),
            Button(
                SCREEN_WIDTH // 2 - button_width // 2,
                start_y + 160,
                button_width,
                button_height,
                "RETOUR",
                COLORS['gray'],
                COLORS['white'],
                lambda: self.game_ui.change_screen("main_menu"),
                "Retourne au menu principal"
            )
        ]
        
        # Bouton pour aller au Deck Builder si pas de deck
        self.deck_builder_button = Button(
            SCREEN_WIDTH // 2 - button_width // 2,
            start_y + 240,
            button_width,
            button_height,
            "CRÉER UN DECK",
            COLORS['blue'],
            COLORS['white'],
            lambda: self.game_ui.change_screen("deck_builder"),
            "Aller au Deck Builder pour créer un deck"
        )
    
    def load_deck_info(self):
        """Charge les informations du deck actuel"""
        try:
            print("[DEBUG] Import de deck_manager...")
            from Engine.deck_manager import deck_manager
            print("[DEBUG] deck_manager importé avec succès")
            
            # Utiliser l'instance globale du deck_manager
            print("[DEBUG] Appel de deck_manager.get_current_deck()...")
            self.current_deck = deck_manager.get_current_deck()
            print(f"[DEBUG] get_current_deck() retourne: {self.current_deck}")
            if self.current_deck:
                print(f"[DEBUG] Type de current_deck: {type(self.current_deck)}")
                print(f"[DEBUG] current_deck.name: {getattr(self.current_deck, 'name', 'PAS D\'ATTRIBUT NAME')}")
            
            if self.current_deck:
                self.deck_valid = self.validate_deck(self.current_deck)
                if self.deck_valid:
                    print(f"[DECK] Deck chargé: {self.current_deck.name}")
                else:
                    print(f"[DECK] Deck invalide: {self.deck_error}")
            else:
                self.deck_valid = False
                self.deck_error = "Aucun deck sauvegardé. Créez un deck dans le Deck Builder."
                print("[DECK] Aucun deck trouvé")
                
        except ImportError as e:
            self.deck_valid = False
            self.deck_error = "Erreur d'import du DeckManager"
            print(f"[ERREUR] Import DeckManager: {e}")
        except Exception as e:
            self.deck_valid = False
            self.deck_error = f"Erreur de chargement: {str(e)}"
            print(f"[ERREUR] load_deck_info: {e}")
    
    def validate_deck(self, deck):
        """Valide que le deck est complet et valide"""
        try:
            # Vérifier qu'il y a un héros
            if not deck.hero:
                self.deck_error = "Aucun héros sélectionné"
                return False
            
            # Vérifier qu'il y a exactement 5 unités
            if not deck.units or len(deck.units) != 5:
                self.deck_error = f"Le deck doit contenir exactement 5 unités (actuellement: {len(deck.units) if deck.units else 0})"
                return False
            
            # Vérifier qu'il y a exactement 30 cartes
            if not deck.cards or len(deck.cards) != 30:
                self.deck_error = f"Le deck doit contenir exactement 30 cartes (actuellement: {len(deck.cards) if deck.cards else 0})"
                return False
            
            # Vérifier qu'il n'y a pas plus de 2 exemplaires de la même carte
            card_counts = {}
            for card in deck.cards:
                # Les cartes sont des dictionnaires JSON, pas des objets Card
                card_name = card.get('name', 'Carte inconnue') if isinstance(card, dict) else getattr(card, 'name', 'Carte inconnue')
                card_counts[card_name] = card_counts.get(card_name, 0) + 1
                if card_counts[card_name] > 2:
                    self.deck_error = f"Trop d'exemplaires de la carte '{card_name}' (maximum 2)"
                    return False
            
            return True
            
        except Exception as e:
            self.deck_error = f"Erreur de validation: {str(e)}"
            return False
    
    def start_ai_combat(self):
        """Lance un combat contre l'IA"""
        print(f"[DEBUG AI COMBAT] start_ai_combat() appelé")
        print(f"[DEBUG AI COMBAT] self.deck_valid: {self.deck_valid}")
        print(f"[DEBUG AI COMBAT] self.current_deck existe: {hasattr(self, 'current_deck')}")
        
        if not self.deck_valid:
            print(f"[DEBUG AI COMBAT] Deck non valide, arrêt")
            return  # Le deck n'est pas valide
        
        if not hasattr(self, 'current_deck') or not self.current_deck:
            print(f"[DEBUG AI COMBAT] Pas de deck actuel, arrêt")
            return
        
        print(f"[DEBUG AI COMBAT] Deck valide, lancement du combat")
        print(f"[DEBUG AI COMBAT] current_deck.hero: {self.current_deck.hero}")
        print(f"[DEBUG AI COMBAT] current_deck.units: {len(self.current_deck.units) if self.current_deck.units else 0}")
        print(f"[DEBUG AI COMBAT] current_deck.cards: {len(self.current_deck.cards) if self.current_deck.cards else 0}")
        
        # Lancer le combat
        combat_screen = self.game_ui.screens["combat"]
        print(f"[DEBUG AI COMBAT] Combat screen récupéré: {combat_screen}")
        
        # Ajouter aux logs de combat
        combat_screen.combat_log.append("[DEBUG] start_ai_combat() appelé")
        combat_screen.combat_log.append("[DEBUG] Deck valide, lancement du combat")
        
        combat_screen.start_combat(self.current_deck)
        self.game_ui.change_screen("combat")
        print(f"[DEBUG AI COMBAT] Changement d'écran effectué")
    
    def start_matchmaking(self):
        """Lance le matchmaking multijoueur"""
        print("[DEBUG MATCHMAKING] start_matchmaking() appelé")
        
        if not self.deck_valid:
            print("[DEBUG MATCHMAKING] Deck non valide, arrêt")
            return  # Le deck n'est pas valide
        
        if not hasattr(self, 'current_deck') or not self.current_deck:
            print("[DEBUG MATCHMAKING] Pas de deck actuel, arrêt")
            return
        
        print("[DEBUG MATCHMAKING] Deck valide, lancement du matchmaking")
        
        # Changer vers l'écran de matchmaking
        self.game_ui.change_screen("matchmaking")
        print("[DEBUG MATCHMAKING] Changement vers l'écran matchmaking effectué")
    
    def _show_deck_error(self):
        """Affiche un message d'erreur pour le deck invalide"""
        print(f"[DEBUG] Tentative de lancement VERSUS avec deck invalide: {self.deck_error}")
        # En production, afficher une popup ou un message à l'écran
        # Pour l'instant, juste un log
    
    def draw(self, screen: pygame.Surface):
        """Dessin de l'écran pre-combat"""
        # Le background est déjà dessiné par GameUI.draw_background()
        # Pas besoin de screen.fill() qui recouvrirait le background
        
        # Titre
        title = self.game_ui.font_large.render("PRÉPARATION DU COMBAT", True, COLORS['gold'])
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 150))
        screen.blit(title, title_rect)
        
        # Informations sur le deck
        self.draw_deck_info(screen)
        
        # Boutons
        for button in self.buttons:
            button.draw(screen)
        
        # Afficher le bouton Deck Builder si pas de deck valide
        if not self.deck_valid:
            self.deck_builder_button.draw(screen)
        
        # Tooltips
        self.draw_tooltips(screen)
    
    def draw_deck_info(self, screen):
        """Dessine les informations sur le deck"""
        info_y = 250
        info_spacing = 30
        
        if self.deck_valid and self.current_deck:
            # Deck valide
            status_text = "✓ DECK VALIDE"
            status_color = COLORS['green']
            
            # Informations du deck
            hero_name = self.current_deck.hero.get('name', 'Héros inconnu') if isinstance(self.current_deck.hero, dict) else getattr(self.current_deck.hero, 'name', 'Héros inconnu')
            hero_text = f"Héros: {hero_name}"
            units_text = f"Unités: {len(self.current_deck.units)}/5"
            cards_text = f"Cartes: {len(self.current_deck.cards)}/30"
            
            # Afficher les informations
            status_surface = self.game_ui.font_medium.render(status_text, True, status_color)
            status_rect = status_surface.get_rect(center=(SCREEN_WIDTH // 2, info_y))
            screen.blit(status_surface, status_rect)
            
            hero_surface = self.game_ui.font_small.render(hero_text, True, COLORS['white'])
            hero_rect = hero_surface.get_rect(center=(SCREEN_WIDTH // 2, info_y + info_spacing))
            screen.blit(hero_surface, hero_rect)
            
            units_surface = self.game_ui.font_small.render(units_text, True, COLORS['white'])
            units_rect = units_surface.get_rect(center=(SCREEN_WIDTH // 2, info_y + 2 * info_spacing))
            screen.blit(units_surface, units_rect)
            
            cards_surface = self.game_ui.font_small.render(cards_text, True, COLORS['white'])
            cards_rect = cards_surface.get_rect(center=(SCREEN_WIDTH // 2, info_y + 3 * info_spacing))
            screen.blit(cards_surface, cards_rect)
            
        else:
            # Deck invalide
            status_text = "✗ DECK INVALIDE"
            status_color = COLORS['red']
            
            error_text = self.deck_error if hasattr(self, 'deck_error') else "Erreur inconnue"
            
            # Afficher l'erreur
            status_surface = self.game_ui.font_medium.render(status_text, True, status_color)
            status_rect = status_surface.get_rect(center=(SCREEN_WIDTH // 2, info_y))
            screen.blit(status_surface, status_rect)
            
            error_surface = self.game_ui.font_small.render(error_text, True, COLORS['red'])
            error_rect = error_surface.get_rect(center=(SCREEN_WIDTH // 2, info_y + info_spacing))
            screen.blit(error_surface, error_rect)
            
            # Désactiver le bouton de combat
            for button in self.buttons:
                if "COMBAT IA" in button.text:
                    button.color = COLORS['gray']
                    button.text_color = COLORS['dark_gray']
    
    def draw_tooltips(self, screen):
        """Dessine les tooltips"""
        mouse_pos = pygame.mouse.get_pos()
        
        # Tooltips pour les boutons principaux
        for button in self.buttons:
            button.update_hover(mouse_pos)
            if button.hover and button.tooltip:
                button.draw_tooltip(screen, mouse_pos)
        
        # Tooltip pour le bouton Deck Builder si affiché
        if not self.deck_valid:
            self.deck_builder_button.update_hover(mouse_pos)
            if self.deck_builder_button.hover and self.deck_builder_button.tooltip:
                self.deck_builder_button.draw_tooltip(screen, mouse_pos)
    
    def handle_event(self, event):
        """Gestion des événements de l'écran pre-combat"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            print(f"[DEBUG PRE-COMBAT] Clic détecté à la position: {mouse_pos}")
            
            # Vérifier les boutons principaux
            for i, button in enumerate(self.buttons):
                if button.is_clicked(mouse_pos):
                    print(f"[DEBUG PRE-COMBAT] Bouton {i} cliqué: {button.text}")
                    button.action()
                    print(f"[DEBUG PRE-COMBAT] Action du bouton {i} exécutée")
                    return
            
            # Vérifier le bouton Deck Builder si affiché
            if not self.deck_valid and self.deck_builder_button.is_clicked(mouse_pos):
                print(f"[DEBUG PRE-COMBAT] Bouton Deck Builder cliqué")
                self.deck_builder_button.action()
                return
import pygame
import sys
import os
import logging
import time
import pygame
import sys
import os
import logging
import time
import json
from typing import Optional, List, Tuple, Dict, Any

# Configuration du logging
def setup_logging():
    """Configure le système de logging"""
    # Créer le dossier logs s'il n'existe pas
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Nom du fichier avec timestamp
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    log_filename = f"logs/combat_debug_{timestamp}.log"
    
    # Configuration du logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename, encoding='utf-8'),
            logging.StreamHandler()  # Garde aussi l'affichage console
        ]
    )
    
    return logging.getLogger(__name__)

# Initialiser le logger
logger = setup_logging()

# Imports des gestionnaires
import os

# Ajouter le chemin du projet au sys.path
project_root = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, project_root)

from Engine.deck_manager import deck_manager
from Engine.hero_customization_manager import hero_customization_manager
from Engine.models import Ability, Card, Hero, Unit
from Engine.effects_database_manager import EffectsDatabaseManager

# Import du système de matchmaking Steam
from UI.steam_matchmaking_ui import SteamMatchmakingUI

# Enum pour les types d'actions multijoueur
class ActionType:
    PLAY_CARD = "play_card"
    USE_ABILITY = "use_ability"
    END_TURN = "end_turn"

# Configuration de l'écran
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
FPS = 60

# Couleurs
COLORS = {
    'deep_black': (10, 10, 20),
    'black': (0, 0, 0),
    'white': (255, 255, 255),
    'gold': (255, 215, 0),
    'light_gold': (255, 235, 100),
    'yellow': (255, 255, 0),
    'silver': (192, 192, 192),
    'gray': (128, 128, 128),
    'dark_gray': (64, 64, 64),
    'royal_blue': (65, 105, 225),
    'light_blue': (173, 216, 230),
    'crimson': (220, 20, 60),
    'ruby_red': (155, 17, 30),
    'orange': (255, 165, 0),
    'deep_blue': (25, 25, 112),
    'green': (0, 255, 0),
    'blue': (0, 0, 255),
    'purple': (128, 0, 128),
    'red': (255, 0, 0),
    'cyan': (0, 255, 255)
}

class GameUI:
    """Interface principale du jeu"""
    
    def __init__(self):
        print(f"[DEBUG GAMEUI] Initialisation de GameUI")
        pygame.init()
        print(f"[DEBUG GAMEUI] Pygame initialisé")
        
        # Initialiser le mixer pour l'audio
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            print("[AUDIO] Mixer pygame initialisé avec succès")
        except Exception as e:
            print(f"[ERREUR] Impossible d'initialiser le mixer : {e}")
        
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Jeu de Cartes")
        self.clock = pygame.time.Clock()
        self.running = True
        self.fullscreen = False
        self.current_screen = "main_menu"
        self.previous_screen = None
        print(f"[DEBUG GAMEUI] Écran initialisé, current_screen: {self.current_screen}")
        
        # Polices
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)
        
        # Gestionnaire d'assets
        self.asset_manager = AssetManager()
        self.asset_manager.load_assets()
        
        # Écrans
        print(f"[DEBUG GAMEUI] Création des écrans...")
        self.screens = {
            "main_menu": MainMenuScreen(self),
            "pre_combat": PreCombatScreen(self),
            "deck_builder": DeckBuilderScreen(self),
            "combat": CombatScreen(self),
            "hero_customization": HeroCustomizationScreen(self),
            "matchmaking": MatchmakingScreen(self)
        }
        print(f"[DEBUG GAMEUI] Écrans créés: {list(self.screens.keys())}")
        
        # Audio
        self.audio_available = pygame.mixer.get_init() is not None
        if self.audio_available:
            self.play_background_music()
    
    def run(self):
        """Boucle principale du jeu"""
        print(f"[DEBUG RUN] Début de la boucle principale")
        print(f"[DEBUG RUN] Écran actuel: {self.current_screen}")
        print(f"[DEBUG RUN] Écrans disponibles: {list(self.screens.keys())}")
        
        try:
            while self.running:
                print(f"[DEBUG] Boucle principale - Frame, self.running = {self.running}")
                # Gestion des événements
                for event in pygame.event.get():
                    self.handle_event(event)
                
                print(f"[DEBUG] Après gestion des événements, self.running = {self.running}")
                
                # Dessiner le background dynamique en premier
                print(f"[DEBUG] Écran actuel: {self.current_screen}")
                self.draw_background(self.screen)
                
                # Mise à jour de l'écran actuel
                current_screen = self.screens.get(self.current_screen)
                if current_screen:
                    current_screen.update()
                    current_screen.draw(self.screen)
                else:
                    print(f"[DEBUG RUN] Écran actuel non trouvé: {self.current_screen}")
                
                # Mise à jour de l'affichage
                pygame.display.flip()
                self.clock.tick(FPS)
        except Exception as e:
            print(f"[DEBUG] Erreur dans la boucle principale: {e}")
            import traceback
            traceback.print_exc()
        
        print(f"[DEBUG RUN] Fin de la boucle principale")
        pygame.quit()
        sys.exit()
    
    def play_background_music(self, music_type="main"):
        """Joue la musique de fond
        
        Args:
            music_type (str): Type de musique à jouer
                - "main": MusicBoard.wav (musique principale)
                - "combat": MusicBoardHarp_V1.wav (musique de combat)
        """
        if not self.audio_available:
            print("[AUDIO] Audio non disponible")
            return
            
        try:
            project_root = os.path.join(os.path.dirname(__file__), '..')
            print(f"[AUDIO] Project root: {project_root}")
            
            if music_type == "combat":
                music_path = os.path.join(project_root, 'Assets', 'Music', 'MusicBoardHarp_V1.wav')
                music_name = "MusicBoardHarp_V1.wav"
            else:
                music_path = os.path.join(project_root, 'Assets', 'Music', 'MusicBoard.wav')
                music_name = "MusicBoard.wav"
            
            print(f"[AUDIO] Chemin musique: {music_path}")
            print(f"[AUDIO] Fichier existe: {os.path.exists(music_path)}")
            
            if os.path.exists(music_path):
                pygame.mixer.music.load(music_path)
                pygame.mixer.music.set_volume(0.5)  # Volume à 50%
                pygame.mixer.music.play(-1)
                print(f"[AUDIO] Musique de fond lancée : {music_name} (volume: 50%)")
            else:
                print(f"[ERREUR] Fichier musique introuvable : {music_path}")
                
        except Exception as e:
            print(f"[ERREUR] Impossible de jouer la musique de fond : {e}")
            import traceback
            traceback.print_exc()
    
    def handle_event(self, event):
        """Gestion des événements globaux"""
        if event.type == pygame.QUIT:
            self.running = False
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.handle_escape()
            elif event.key == pygame.K_F11:
                self.toggle_fullscreen()
        
        # Transmettre l'événement à l'écran actuel
        current_screen = self.screens.get(self.current_screen)
        if current_screen:
            print(f"[DEBUG EVENT] Événement transmis à l'écran: {self.current_screen}")
            current_screen.handle_event(event)
        else:
            print(f"[DEBUG EVENT] Écran actuel non trouvé: {self.current_screen}")
    
    def handle_escape(self):
        """Gestion de la touche Échap"""
        if self.current_screen == "main_menu":
            self.running = False
        else:
            self.change_screen("main_menu")
    
    def toggle_fullscreen(self):
        """Bascule entre plein écran et fenêtré"""
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    
    def change_screen(self, screen_name: str):
        """Change d'écran"""
        print(f"[DEBUG SCREEN] change_screen() appelé avec: {screen_name}")
        print(f"[DEBUG SCREEN] Écrans disponibles: {list(self.screens.keys())}")
        
        if screen_name in self.screens:
            print(f"[UI] Changement d'écran : {self.current_screen} → {screen_name}")
            
            # Gestion de la musique selon l'écran
            if self.current_screen == "combat" and screen_name != "combat":
                # Quitter le combat : remettre la musique principale
                self.play_background_music("main")
            elif screen_name == "combat" and self.current_screen != "combat":
                # Entrer en combat : musique de combat (gérée dans start_combat)
                pass
            
            # Mémoriser l'écran précédent pour gestion du retour
            self.previous_screen = self.current_screen
            self.current_screen = screen_name
            print(f"[DEBUG SCREEN] Écran actuel mis à jour: {self.current_screen}")
        else:
            print(f"[DEBUG SCREEN] Écran '{screen_name}' non trouvé!")

    def get_current_hero_element(self):
        """Détermine l'élément du héros actuel pour le background"""
        # Priorité 1: Héros en combat
        try:
            if hasattr(self, 'screens') and 'combat' in self.screens:
                combat_screen = self.screens['combat']
                if hasattr(combat_screen, 'player_hero') and combat_screen.player_hero:
                    if hasattr(combat_screen.player_hero, 'element'):
                        return combat_screen.player_hero.element
        except Exception as e:
            pass
        
        # Priorité 2: Héros sélectionné dans DeckBuilderScreen
        try:
            if hasattr(self, 'screens') and 'deck_builder' in self.screens:
                deck_builder = self.screens['deck_builder']
                if hasattr(deck_builder, 'selected_hero') and deck_builder.selected_hero:
                    if hasattr(deck_builder.selected_hero, 'element'):
                        return deck_builder.selected_hero.element
        except Exception as e:
            pass
        
        # Priorité 3: Héros du deck sauvegardé via le deck manager
        try:
            from Engine.deck_manager import deck_manager
            current_deck = deck_manager.get_current_deck()
            if current_deck and current_deck.hero:
                if hasattr(current_deck.hero, 'element'):
                    return current_deck.hero.element
                elif isinstance(current_deck.hero, dict) and 'element' in current_deck.hero:
                    return current_deck.hero['element']
        except Exception as e:
            pass
        
        # Fallback: élément neutre
        return "Neutre"

    def draw_background(self, screen):
        """Dessine le background dynamique basé sur l'élément du héros"""
        current_element = None
        
        try:
            current_element = self.get_current_hero_element()
            print(f"[DEBUG] Élément détecté: {current_element}")
            
            # Mapper les éléments aux noms de fichiers
            element_to_file = {
                "Feu": "Feu.png",
                "Eau": "Eau.png", 
                "Terre": "Terre.png",
                "Air": "Air.png",
                "Foudre": "Foudre.png",
                "Glace": "Glace.png",
                "Lumiere": "Lumiere.png",
                "Tenebres": "Tenebres.png",
                "Arcanique": "Arcanique.png",
                "Poison": "Poison.png",
                "Neant": "Neant.png",
                "Neutre": "Neutre.png"
            }
            
            background_file = element_to_file.get(current_element, "Neutre.png")
            print(f"[DEBUG] Fichier background: {background_file}")
            
            # Charger et afficher le background
            try:
                background_path = os.path.join(os.path.dirname(__file__), '..', 'Assets', 'img', 'Fond', background_file)
                print(f"[DEBUG] Chemin background: {background_path}")
                print(f"[DEBUG] Fichier existe: {os.path.exists(background_path)}")
                
                if os.path.exists(background_path):
                    background_image = pygame.image.load(background_path)
                    background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
                    screen.blit(background_image, (0, 0))
                    print(f"[DEBUG] Background affiché avec succès")
                else:
                    # Fallback: fond noir
                    screen.fill((0, 0, 0))
                    print(f"[DEBUG] Fichier background introuvable")
            except Exception as e:
                # Fallback: fond noir
                screen.fill((0, 0, 0))
                print(f"[DEBUG] Erreur lors du chargement: {e}")
                
        except Exception as e:
            # Fallback: fond noir
            screen.fill((0, 0, 0))
            print(f"[DEBUG] Erreur générale: {e}")
    
    def clear_screen_for_ui(self, screen):
        """Nettoie l'écran avec un overlay semi-transparent pour l'UI"""
        # Au lieu d'un overlay sur tout l'écran, on ne fait rien
        # Les écrans individuels devront gérer leur propre nettoyage
        pass

class AssetManager:
    """Gestionnaire d'assets (images, sons, fonts)"""
    
    IMAGE_SIZES = {
        'Hero': (200, 288),
        'Crea': (200, 288),
        'Carte': (200, 288),
        'Symbols': (34, 34),
        'Icons': (32, 32),
        'UI': (64, 64),
        'Backgrounds': (1920, 1080),
        'default': (200, 288)
    }
    
    def __init__(self):
        self.images = {}
        self.sounds = {}
        self.fonts = {}
        self.scaled_images_cache = {}
    
    def load_assets(self):
        """Charge tous les assets"""
        self.load_images()
        self.load_sounds()
        self.load_fonts()
    
    def load_images(self):
        """Charge les images"""
        try:
            project_root = os.path.join(os.path.dirname(__file__), '..')
            assets_path = os.path.join(project_root, 'Assets', 'img')
            
            print(f"[ASSETS] Recherche d'images dans : {assets_path}")
            
            for root, dirs, files in os.walk(assets_path):
                for file in files:
                    if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                        img_path = os.path.join(root, file)
                        # Obtenir le chemin relatif depuis le dossier img
                        rel_path = os.path.relpath(img_path, assets_path)
                        # Normaliser les séparateurs de chemin
                        img_name = rel_path.replace('\\', '/').replace('/', '/')
                        # Supprimer l'extension pour la clé de base
                        img_name_no_ext = os.path.splitext(img_name)[0]
                        
                        try:
                            # Charger l'image sans convert_alpha() d'abord
                            image = pygame.image.load(img_path)
                            
                            # Essayer de convertir seulement si pygame.display est initialisé
                            try:
                                image = image.convert_alpha()
                            except pygame.error:
                                # Si pygame.display n'est pas initialisé, on garde l'image sans conversion
                                print(f"[ASSETS] Image chargée sans conversion alpha: {img_name}")
                            
                            # Stocker l'image avec et sans extension pour la compatibilité
                            self.images[img_name_no_ext] = image
                            self.images[img_name] = image  # Avec extension
                            print(f"[ASSETS] Image chargée : {img_name} -> {image.get_size()}")
                        except Exception as e:
                            print(f"[ERREUR] Impossible de charger l'image {img_path}: {e}")
                                
        except Exception as e:
            print(f"[ERREUR] Impossible de charger les images: {e}")
    
    def get_image(self, name: str) -> Optional[pygame.Surface]:
        """Récupère une image avec gestion des chemins"""
        # Essayer d'abord le nom exact
        if name in self.images:
            return self.images[name]
        
        # Essayer sans extension si le nom en a une
        if name.endswith(('.png', '.jpg', '.jpeg')):
            name_no_ext = os.path.splitext(name)[0]
            if name_no_ext in self.images:
                return self.images[name_no_ext]
        
        # Essayer avec extension si le nom n'en a pas
        for ext in ['.png', '.jpg', '.jpeg']:
            name_with_ext = name + ext
            if name_with_ext in self.images:
                return self.images[name_with_ext]
        
        # Si aucune image trouvée, créer une image par défaut
        print(f"[ASSETS] Image non trouvée : {name}, création d'une image par défaut")
        return self._create_default_image(name)
    
    def _create_default_image(self, name: str) -> pygame.Surface:
        """Crée une image par défaut quand l'image n'est pas trouvée"""
        # Créer une surface de 200x288 pixels (taille standard selon la documentation)
        surface = pygame.Surface((200, 288))
        
        # Couleur de fond selon le type
        if 'Hero' in name:
            bg_color = (100, 50, 50)  # Rouge foncé pour les héros
            text_color = (255, 200, 200)
        elif 'Crea' in name:
            bg_color = (50, 100, 50)  # Vert foncé pour les créatures
            text_color = (200, 255, 200)
        elif 'Carte' in name:
            bg_color = (50, 50, 100)  # Bleu foncé pour les cartes
            text_color = (200, 200, 255)
        else:
            bg_color = (80, 80, 80)   # Gris par défaut
            text_color = (200, 200, 200)
        
        # Remplir le fond
        surface.fill(bg_color)
        
        # Ajouter un texte pour indiquer que l'image est manquante
        try:
            font = pygame.font.Font(None, 24)
            text = font.render("Image manquante", True, text_color)
            text_rect = text.get_rect(center=(100, 144))
            surface.blit(text, text_rect)
            
            # Ajouter le nom de l'image
            name_text = font.render(name, True, text_color)
            name_rect = name_text.get_rect(center=(100, 170))
            surface.blit(name_text, name_rect)
        except:
            pass  # Si la police n'est pas disponible, on garde juste le fond
        
        # Stocker l'image pour éviter de la recréer
        self.images[name] = surface
        return surface
    
    def load_sounds(self):
        """Charge les sons"""
        pass
    
    def load_fonts(self):
        """Charge les polices"""
        pass
    
    def get_sound(self, name: str) -> Optional[pygame.mixer.Sound]:
        """Récupère un son"""
        return self.sounds.get(name)

class Screen:
    """Classe de base pour tous les écrans"""
    
    def __init__(self, game_ui: GameUI):
        self.game_ui = game_ui
        self.buttons = []
    
    def update(self):
        """Mise à jour de l'écran"""
        pass
    
    def draw(self, screen: pygame.Surface):
        """Dessin de l'écran"""
        pass
    
    def handle_event(self, event):
        """Gestion des événements de l'écran"""
        pass

class Button:
    """Bouton cliquable"""
    
    def __init__(self, x: int, y: int, width: int, height: int, text: str, 
                 color: Tuple[int, int, int], text_color: Tuple[int, int, int], action, 
                 tooltip: str = None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.text_color = text_color
        self.action = action
        self.hover = False
        self.tooltip = tooltip
        
    def draw(self, screen: pygame.Surface):
        """Dessine le bouton"""
        color = self.color if not self.hover else tuple(min(255, c + 30) for c in self.color)
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, COLORS['white'], self.rect, 2)
        
        font = pygame.font.Font(None, self._calculate_optimal_font_size())
        text_surface = font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
    
    def _calculate_optimal_font_size(self) -> int:
        """Calcule la taille de police optimale"""
        font_size = 24
        while font_size > 12:
            font = pygame.font.Font(None, font_size)
            text_surface = font.render(self.text, True, self.text_color)
            if text_surface.get_width() <= self.rect.width - 20:
                return font_size
            font_size -= 2
        return 12
    
    def is_clicked(self, pos: Tuple[int, int]) -> bool:
        """Vérifie si le bouton est cliqué"""
        return self.rect.collidepoint(pos)
    
    def update_hover(self, pos: Tuple[int, int]):
        """Met à jour l'état de hover"""
        self.hover = self.rect.collidepoint(pos)
    
    def draw_tooltip(self, screen: pygame.Surface, mouse_pos: Tuple[int, int]):
        """Dessine le tooltip si le bouton est survolé"""
        if self.hover and self.tooltip:
            # Calculer la position du tooltip (au-dessus du bouton)
            tooltip_x = mouse_pos[0]
            tooltip_y = self.rect.top - 10
            
            # Créer le texte du tooltip
            font = pygame.font.Font(None, 20)
            lines = self.tooltip.split('\n')
            
            # Calculer la taille du tooltip
            max_width = 0
            total_height = 0
            line_surfaces = []
            
            for line in lines:
                line_surface = font.render(line, True, COLORS['white'])
                line_surfaces.append(line_surface)
                max_width = max(max_width, line_surface.get_width())
                total_height += line_surface.get_height() + 2
            
            # Ajuster la position pour que le tooltip reste dans l'écran
            if tooltip_x + max_width > SCREEN_WIDTH:
                tooltip_x = SCREEN_WIDTH - max_width - 10
            if tooltip_y - total_height < 0:
                tooltip_y = self.rect.bottom + 10
            
            # Dessiner le fond du tooltip
            tooltip_rect = pygame.Rect(tooltip_x - 5, tooltip_y - total_height - 5, 
                                     max_width + 10, total_height + 10)
            pygame.draw.rect(screen, (*COLORS['deep_black'], 230), tooltip_rect, border_radius=5)
            pygame.draw.rect(screen, COLORS['gold'], tooltip_rect, 2, border_radius=5)
            
            # Dessiner le texte du tooltip
            current_y = tooltip_y - total_height
            for line_surface in line_surfaces:
                screen.blit(line_surface, (tooltip_x, current_y))
                current_y += line_surface.get_height() + 2

class DropdownMenu:
    """Menu déroulant"""
    
    def __init__(self, x: int, y: int, width: int, height: int, options: List[str], 
                 default_option: str = "all", font_size: int = 24):
        self.rect = pygame.Rect(x, y, width, height)
        self.options = options
        self.selected_option = default_option
        self.is_open = False
        self.font_size = font_size
        
    def draw(self, screen: pygame.Surface):
        """Dessine le menu déroulant"""
        # Fond principal
        pygame.draw.rect(screen, COLORS['dark_gray'], self.rect)
        pygame.draw.rect(screen, COLORS['white'], self.rect, 2)
        
        # Texte sélectionné
        font = pygame.font.Font(None, self.font_size)
        text_surface = font.render(self.selected_option, True, COLORS['white'])
        text_rect = text_surface.get_rect(midleft=(self.rect.x + 10, self.rect.centery))
        screen.blit(text_surface, text_rect)
        
        # Flèche
        arrow_points = [
            (self.rect.right - 20, self.rect.centery - 5),
            (self.rect.right - 20, self.rect.centery + 5),
            (self.rect.right - 10, self.rect.centery)
        ]
        pygame.draw.polygon(screen, COLORS['white'], arrow_points)
        
        # Options si ouvert
        if self.is_open:
            for i, option in enumerate(self.options):
                option_rect = pygame.Rect(self.rect.x, self.rect.bottom + i * 30, self.rect.width, 30)
                pygame.draw.rect(screen, COLORS['dark_gray'], option_rect)
                pygame.draw.rect(screen, COLORS['white'], option_rect, 1)
                
                option_surface = font.render(option, True, COLORS['white'])
                option_text_rect = option_surface.get_rect(midleft=(option_rect.x + 10, option_rect.centery))
                screen.blit(option_surface, option_text_rect)
    
    def handle_click(self, pos: Tuple[int, int]) -> Optional[str]:
        """Gère les clics sur le menu"""
        if self.rect.collidepoint(pos):
            self.is_open = not self.is_open
            return None
        
        if self.is_open:
            for i, option in enumerate(self.options):
                option_rect = pygame.Rect(self.rect.x, self.rect.bottom + i * 30, self.rect.width, 30)
                if option_rect.collidepoint(pos):
                    self.selected_option = option
                    self.is_open = False
                    return option
        
        self.is_open = False
        return None
    
    def close(self):
        """Ferme le menu"""
        self.is_open = False

class MainMenuScreen(Screen):
    """Écran du menu principal"""
    
    def __init__(self, game_ui: GameUI):
        super().__init__(game_ui)
        self.setup_buttons()
    
    def setup_buttons(self):
        """Configure les boutons du menu principal"""
        button_width = 300
        button_height = 60
        start_y = 400
        
        # Bouton Jouer
        self.buttons.append(Button(
            SCREEN_WIDTH // 2 - button_width // 2,
            start_y,
            button_width,
            button_height,
            "JOUER",
            COLORS['gold'],
            COLORS['deep_black'],
            lambda: self.game_ui.change_screen("pre_combat")
        ))
        
        # Bouton DECK
        self.buttons.append(Button(
            SCREEN_WIDTH // 2 - button_width // 2,
            start_y + 80,
            button_width,
            button_height,
            "DECK",
            COLORS['royal_blue'],
            COLORS['white'],
            lambda: self.game_ui.change_screen("deck_builder")
        ))
        
        # Bouton BOUTIQUE
        self.buttons.append(Button(
            SCREEN_WIDTH // 2 - button_width // 2,
            start_y + 160,
            button_width,
            button_height,
            "BOUTIQUE",
            COLORS['ruby_red'],
            COLORS['white'],
            lambda: print("BOUTIQUE - À implémenter")
        ))
        
        # Bouton OPTIONS
        self.buttons.append(Button(
            SCREEN_WIDTH // 2 - button_width // 2,
            start_y + 240,
            button_width,
            button_height,
            "OPTIONS",
            COLORS['silver'],
            COLORS['deep_black'],
            lambda: print("OPTIONS - À implémenter")
        ))
        
        # Bouton QUITTER
        self.buttons.append(Button(
            SCREEN_WIDTH // 2 - button_width // 2,
            start_y + 320,
            button_width,
            button_height,
            "QUITTER",
            COLORS['crimson'],
            COLORS['white'],
            lambda: setattr(self.game_ui, 'running', False)
        ))
    
    def draw(self, screen: pygame.Surface):
        """Dessin du menu principal"""
        # Le background est déjà dessiné par GameUI.draw_background()
        
        # Titre
        title = self.game_ui.font_large.render("JEU DE CARTES", True, COLORS['gold'])
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 200))
        screen.blit(title, title_rect)
        
        # Sous-titre
        subtitle = self.game_ui.font_medium.render("Aventure Fantasy", True, COLORS['white'])
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, 250))
        screen.blit(subtitle, subtitle_rect)
        
        # Boutons
        for button in self.buttons:
            button.draw(screen)
    
    def handle_event(self, event):
        """Gestion des événements du menu principal"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            for button in self.buttons:
                if button.is_clicked(mouse_pos):
                    button.action()
                    return


class MatchmakingScreen(Screen):
    """Écran de matchmaking multijoueur"""
    
    def __init__(self, game_ui: GameUI):
        super().__init__(game_ui)
        print(f"[DEBUG MATCHMAKING] MatchmakingScreen initialisé")
        
        # Créer l'interface de matchmaking Steam
        self.steam_matchmaking_ui = SteamMatchmakingUI(self.game_ui.screen)
        
        # Configurer le callback pour quand un match est trouvé
        print(f"[DEBUG MATCHMAKING] Configuration du callback _on_match_found")
        self.steam_matchmaking_ui.set_match_found_callback(self._on_match_found)
        print(f"[DEBUG MATCHMAKING] Callback configuré: {self.steam_matchmaking_ui.on_match_found}")
        
        print(f"[DEBUG MATCHMAKING] SteamMatchmakingUI initialisé")
    
    def _on_match_found(self, match_data):
        """Callback appelé quand un match est trouvé"""
        print(f"[DEBUG MATCHMAKING] Match trouvé ! Données: {match_data}")
        try:
            # Démarrer le VRAI combat multijoueur local
            print("[DEBUG MATCHMAKING] Démarrage du combat multijoueur local...")
            # Récupérer le deck du joueur depuis l'écran pré-combat
            pre_combat_screen = self.game_ui.screens.get("pre_combat")
            if pre_combat_screen and hasattr(pre_combat_screen, 'current_deck') and pre_combat_screen.current_deck:
                player_deck = pre_combat_screen.current_deck
                print(f"[DEBUG MATCHMAKING] Deck joueur trouvé: {player_deck.name if hasattr(player_deck, 'name') else 'Deck sans nom'}")
                # Déterminer si on est le joueur 1 ou 2 (basé sur l'ID du client actuel)
                current_player_id = self.steam_matchmaking_ui.user_info["id"]
                is_player1 = match_data.get('player1', {}).get('id') == current_player_id
                print(f"[DEBUG MATCHMAKING] Rôle: {'Joueur 1 (Hôte)' if is_player1 else 'Joueur 2 (Client)'}")
                # Démarrer le combat multijoueur avec synchronisation (sans changer d'écran tout de suite)
                combat_screen = self.game_ui.screens.get("combat")
                if combat_screen:
                    print("[DEBUG MATCHMAKING] Démarrage du combat multijoueur...")
                    combat_screen.set_multiplayer_mode(True, is_player1, match_data)
                    combat_screen.start_multiplayer_combat(player_deck, match_data)
                    print("[DEBUG MATCHMAKING] Attente que les deux joueurs soient prêts...")
                else:
                    print("[DEBUG MATCHMAKING] Erreur: Écran de combat non trouvé")
                    self.game_ui.change_screen("pre_combat")
            else:
                print("[DEBUG MATCHMAKING] Erreur: Deck du joueur non trouvé")
                self.game_ui.change_screen("pre_combat")
        except Exception as e:
            print(f"[DEBUG MATCHMAKING] Erreur lors du lancement du combat multijoueur: {e}")
            import traceback
            traceback.print_exc()
            self.game_ui.change_screen("pre_combat")
    
    def update(self):
        """Mise à jour de l'écran de matchmaking"""
        self.steam_matchmaking_ui.update()
    
    def draw(self, screen: pygame.Surface):
        """Dessin de l'écran de matchmaking"""
        self.steam_matchmaking_ui.draw(screen)
    
    def handle_event(self, event):
        """Gestion des événements de l'écran de matchmaking"""
        # Gérer le retour vers l'écran précédent
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.game_ui.change_screen("pre_combat")
            return
        
        # Configurer le callback de retour pour SteamMatchmakingUI
        self.steam_matchmaking_ui.on_back = lambda: self.game_ui.change_screen("pre_combat")
        
        # Passer l'événement à SteamMatchmakingUI
        self.steam_matchmaking_ui.handle_event(event)


class PreCombatScreen(Screen):
    """Écran de sélection avant combat"""
    
    def __init__(self, game_ui: GameUI):
        super().__init__(game_ui)
        print(f"[DEBUG PRE-COMBAT] PreCombatScreen initialisé")
        # Initialiser les variables de deck avant setup_buttons
        self.deck_valid = False
        self.deck_error = "Chargement..."
        self.current_deck = None
        self.load_deck_info()
        self.setup_buttons()
        print(f"[DEBUG PRE-COMBAT] PreCombatScreen setup terminé")
    
    def update(self):
        """Mise à jour de l'écran pre-combat"""
        # Recharger les informations du deck à chaque frame pour s'assurer qu'elles sont à jour
        self.load_deck_info()
    
    def setup_buttons(self):
        """Configure les boutons de l'écran pre-combat"""
        button_width = 300
        button_height = 60
        start_y = 400
        
        # Mettre à jour les boutons en fonction de la validité du deck
        self.buttons = [
            Button(
                SCREEN_WIDTH // 2 - button_width // 2,
                start_y,
                button_width,
                button_height,
                "COMBAT IA",
                COLORS['gold'],
                COLORS['deep_black'],
                self.start_ai_combat,
                "Lance un combat contre l'IA"
            ),
            Button(
                SCREEN_WIDTH // 2 - button_width // 2,
                start_y + 80,
                button_width,
                button_height,
                "VERSUS",
                COLORS['red'] if self.deck_valid else COLORS['gray'],  # Grisé si deck invalide
                COLORS['white'],
                self.start_matchmaking if self.deck_valid else self._show_deck_error,  # Callback différent si invalide
                "Lance un combat multijoueur" if self.deck_valid else "Deck invalide - Créez un deck valide d'abord"
            ),
            Button(
                SCREEN_WIDTH // 2 - button_width // 2,
                start_y + 160,
                button_width,
                button_height,
                "RETOUR",
                COLORS['gray'],
                COLORS['white'],
                lambda: self.game_ui.change_screen("main_menu"),
                "Retourne au menu principal"
            )
        ]
        
        # Bouton pour aller au Deck Builder si pas de deck
        self.deck_builder_button = Button(
            SCREEN_WIDTH // 2 - button_width // 2,
            start_y + 240,
            button_width,
            button_height,
            "CRÉER UN DECK",
            COLORS['blue'],
            COLORS['white'],
            lambda: self.game_ui.change_screen("deck_builder"),
            "Aller au Deck Builder pour créer un deck"
        )
    
    def load_deck_info(self):
        """Charge les informations du deck actuel"""
        try:
            print("[DEBUG] Import de deck_manager...")
            from Engine.deck_manager import deck_manager
            print("[DEBUG] deck_manager importé avec succès")
            
            # Utiliser l'instance globale du deck_manager
            print("[DEBUG] Appel de deck_manager.get_current_deck()...")
            self.current_deck = deck_manager.get_current_deck()
            print(f"[DEBUG] get_current_deck() retourne: {self.current_deck}")
            if self.current_deck:
                print(f"[DEBUG] Type de current_deck: {type(self.current_deck)}")
                print(f"[DEBUG] current_deck.name: {getattr(self.current_deck, 'name', 'PAS D\'ATTRIBUT NAME')}")
            
            if self.current_deck:
                self.deck_valid = self.validate_deck(self.current_deck)
                if self.deck_valid:
                    print(f"[DECK] Deck chargé: {self.current_deck.name}")
                else:
                    print(f"[DECK] Deck invalide: {self.deck_error}")
            else:
                self.deck_valid = False
                self.deck_error = "Aucun deck sauvegardé. Créez un deck dans le Deck Builder."
                print("[DECK] Aucun deck trouvé")
                
        except ImportError as e:
            self.deck_valid = False
            self.deck_error = "Erreur d'import du DeckManager"
            print(f"[ERREUR] Import DeckManager: {e}")
        except Exception as e:
            self.deck_valid = False
            self.deck_error = f"Erreur de chargement: {str(e)}"
            print(f"[ERREUR] load_deck_info: {e}")
    
    def validate_deck(self, deck):
        """Valide que le deck est complet et valide"""
        try:
            # Vérifier qu'il y a un héros
            if not deck.hero:
                self.deck_error = "Aucun héros sélectionné"
                return False
            
            # Vérifier qu'il y a exactement 5 unités
            if not deck.units or len(deck.units) != 5:
                self.deck_error = f"Le deck doit contenir exactement 5 unités (actuellement: {len(deck.units) if deck.units else 0})"
                return False
            
            # Vérifier qu'il y a exactement 30 cartes
            if not deck.cards or len(deck.cards) != 30:
                self.deck_error = f"Le deck doit contenir exactement 30 cartes (actuellement: {len(deck.cards) if deck.cards else 0})"
                return False
            
            # Vérifier qu'il n'y a pas plus de 2 exemplaires de la même carte
            card_counts = {}
            for card in deck.cards:
                # Les cartes sont des dictionnaires JSON, pas des objets Card
                card_name = card.get('name', 'Carte inconnue') if isinstance(card, dict) else getattr(card, 'name', 'Carte inconnue')
                card_counts[card_name] = card_counts.get(card_name, 0) + 1
                if card_counts[card_name] > 2:
                    self.deck_error = f"Trop d'exemplaires de la carte '{card_name}' (maximum 2)"
                    return False
            
            return True
            
        except Exception as e:
            self.deck_error = f"Erreur de validation: {str(e)}"
            return False
    
    def start_ai_combat(self):
        """Lance un combat contre l'IA"""
        print(f"[DEBUG AI COMBAT] start_ai_combat() appelé")
        print(f"[DEBUG AI COMBAT] self.deck_valid: {self.deck_valid}")
        print(f"[DEBUG AI COMBAT] self.current_deck existe: {hasattr(self, 'current_deck')}")
        
        if not self.deck_valid:
            print(f"[DEBUG AI COMBAT] Deck non valide, arrêt")
            return  # Le deck n'est pas valide
        
        if not hasattr(self, 'current_deck') or not self.current_deck:
            print(f"[DEBUG AI COMBAT] Pas de deck actuel, arrêt")
            return
        
        print(f"[DEBUG AI COMBAT] Deck valide, lancement du combat")
        print(f"[DEBUG AI COMBAT] current_deck.hero: {self.current_deck.hero}")
        print(f"[DEBUG AI COMBAT] current_deck.units: {len(self.current_deck.units) if self.current_deck.units else 0}")
        print(f"[DEBUG AI COMBAT] current_deck.cards: {len(self.current_deck.cards) if self.current_deck.cards else 0}")
        
        # Lancer le combat
        combat_screen = self.game_ui.screens["combat"]
        print(f"[DEBUG AI COMBAT] Combat screen récupéré: {combat_screen}")
        
        # Ajouter aux logs de combat
        combat_screen.combat_log.append("[DEBUG] start_ai_combat() appelé")
        combat_screen.combat_log.append("[DEBUG] Deck valide, lancement du combat")
        
        combat_screen.start_combat(self.current_deck)
        self.game_ui.change_screen("combat")
        print(f"[DEBUG AI COMBAT] Changement d'écran effectué")
    
    def start_matchmaking(self):
        """Lance le matchmaking multijoueur"""
        print("[DEBUG MATCHMAKING] start_matchmaking() appelé")
        
        if not self.deck_valid:
            print("[DEBUG MATCHMAKING] Deck non valide, arrêt")
            return  # Le deck n'est pas valide
        
        if not hasattr(self, 'current_deck') or not self.current_deck:
            print("[DEBUG MATCHMAKING] Pas de deck actuel, arrêt")
            return
        
        print("[DEBUG MATCHMAKING] Deck valide, lancement du matchmaking")
        
        # Changer vers l'écran de matchmaking
        self.game_ui.change_screen("matchmaking")
        print("[DEBUG MATCHMAKING] Changement vers l'écran matchmaking effectué")
    
    def _show_deck_error(self):
        """Affiche un message d'erreur pour le deck invalide"""
        print(f"[DEBUG] Tentative de lancement VERSUS avec deck invalide: {self.deck_error}")
        # En production, afficher une popup ou un message à l'écran
        # Pour l'instant, juste un log
    
    def draw(self, screen: pygame.Surface):
        """Dessin de l'écran pre-combat"""
        # Le background est déjà dessiné par GameUI.draw_background()
        # Pas besoin de screen.fill() qui recouvrirait le background
        
        # Titre
        title = self.game_ui.font_large.render("PRÉPARATION DU COMBAT", True, COLORS['gold'])
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 150))
        screen.blit(title, title_rect)
        
        # Informations sur le deck
        self.draw_deck_info(screen)
        
        # Boutons
        for button in self.buttons:
            button.draw(screen)
        
        # Afficher le bouton Deck Builder si pas de deck valide
        if not self.deck_valid:
            self.deck_builder_button.draw(screen)
        
        # Tooltips
        self.draw_tooltips(screen)
    
    def draw_deck_info(self, screen):
        """Dessine les informations sur le deck"""
        info_y = 250
        info_spacing = 30
        
        if self.deck_valid and self.current_deck:
            # Deck valide
            status_text = "✓ DECK VALIDE"
            status_color = COLORS['green']
            
            # Informations du deck
            hero_name = self.current_deck.hero.get('name', 'Héros inconnu') if isinstance(self.current_deck.hero, dict) else getattr(self.current_deck.hero, 'name', 'Héros inconnu')
            hero_text = f"Héros: {hero_name}"
            units_text = f"Unités: {len(self.current_deck.units)}/5"
            cards_text = f"Cartes: {len(self.current_deck.cards)}/30"
            
            # Afficher les informations
            status_surface = self.game_ui.font_medium.render(status_text, True, status_color)
            status_rect = status_surface.get_rect(center=(SCREEN_WIDTH // 2, info_y))
            screen.blit(status_surface, status_rect)
            
            hero_surface = self.game_ui.font_small.render(hero_text, True, COLORS['white'])
            hero_rect = hero_surface.get_rect(center=(SCREEN_WIDTH // 2, info_y + info_spacing))
            screen.blit(hero_surface, hero_rect)
            
            units_surface = self.game_ui.font_small.render(units_text, True, COLORS['white'])
            units_rect = units_surface.get_rect(center=(SCREEN_WIDTH // 2, info_y + 2 * info_spacing))
            screen.blit(units_surface, units_rect)
            
            cards_surface = self.game_ui.font_small.render(cards_text, True, COLORS['white'])
            cards_rect = cards_surface.get_rect(center=(SCREEN_WIDTH // 2, info_y + 3 * info_spacing))
            screen.blit(cards_surface, cards_rect)
            
        else:
            # Deck invalide
            status_text = "✗ DECK INVALIDE"
            status_color = COLORS['red']
            
            error_text = self.deck_error if hasattr(self, 'deck_error') else "Erreur inconnue"
            
            # Afficher l'erreur
            status_surface = self.game_ui.font_medium.render(status_text, True, status_color)
            status_rect = status_surface.get_rect(center=(SCREEN_WIDTH // 2, info_y))
            screen.blit(status_surface, status_rect)
            
            error_surface = self.game_ui.font_small.render(error_text, True, COLORS['red'])
            error_rect = error_surface.get_rect(center=(SCREEN_WIDTH // 2, info_y + info_spacing))
            screen.blit(error_surface, error_rect)
            
            # Désactiver le bouton de combat
            for button in self.buttons:
                if "COMBAT IA" in button.text:
                    button.color = COLORS['gray']
                    button.text_color = COLORS['dark_gray']
    
    def draw_tooltips(self, screen):
        """Dessine les tooltips"""
        mouse_pos = pygame.mouse.get_pos()
        
        # Tooltips pour les boutons principaux
        for button in self.buttons:
            button.update_hover(mouse_pos)
            if button.hover and button.tooltip:
                button.draw_tooltip(screen, mouse_pos)
        
        # Tooltip pour le bouton Deck Builder si affiché
        if not self.deck_valid:
            self.deck_builder_button.update_hover(mouse_pos)
            if self.deck_builder_button.hover and self.deck_builder_button.tooltip:
                self.deck_builder_button.draw_tooltip(screen, mouse_pos)
    
    def handle_event(self, event):
        """Gestion des événements de l'écran pre-combat"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            print(f"[DEBUG PRE-COMBAT] Clic détecté à la position: {mouse_pos}")
            
            # Vérifier les boutons principaux
            for i, button in enumerate(self.buttons):
                if button.is_clicked(mouse_pos):
                    print(f"[DEBUG PRE-COMBAT] Bouton {i} cliqué: {button.text}")
                    button.action()
                    print(f"[DEBUG PRE-COMBAT] Action du bouton {i} exécutée")
                    return
            
            # Vérifier le bouton Deck Builder si affiché
            if not self.deck_valid and self.deck_builder_button.is_clicked(mouse_pos):
                print(f"[DEBUG PRE-COMBAT] Bouton Deck Builder cliqué")
                self.deck_builder_button.action()
                return
import pygame
import sys
import os
import logging
import time
class CombatScreen(Screen):
    """Écran de combat complet"""
    
    def __init__(self, game_ui: GameUI):
        super().__init__(game_ui)
        self.combat_engine = None
        self.player = None
        self.opponent = None
        self.current_phase = "actions"  # pioche, mana, actions, combat, fin_tour
        self.selected_card = None
        self.selected_target = None
        self.hovered_card = None
        self.hovered_entity = None
        self.combat_log = []
        self.animation_timer = 0
        
        # Popup d'abandon (affichée côté adversaire lorsqu'il abandonne)
        self.surrender_popup_visible = False
        self.surrender_popup_rect = None
        self.surrender_ok_button = None
        
        # Variables pour l'overlay de clic droit
        self.right_click_overlay = None
        self.right_click_overlay_type = None
        self.right_click_overlay_alpha = 255
        self.right_click_overlay_unit = None  # Pour stocker l'unité de l'overlay
        
        # Menu des capacités
        self.ability_menu = None
        self.ability_menu_unit = None
        self.ability_menu_rect = None
        
        # === NOUVELLES VARIABLES POUR LE SYSTÈME DE CIBLAGE ===
        self.targeting_mode = False
        self.targeting_card = None
        self.valid_targets = []
        self.highlighted_targets = []
        self.targeting_info = None
        
        # === NOUVELLES VARIABLES POUR LES CAPACITÉS ===
        self.ability_mode = False
        self.selected_ability = None
        self.ability_source = None
        self.ability_targets = []
        
        # === NOUVELLES VARIABLES POUR LES EFFETS VISUELS ===
        self.visual_effects = []  # Liste des effets visuels actifs
        self.damage_numbers = []  # Liste des nombres de dégâts à afficher
        self.heal_numbers = []    # Liste des nombres de soins à afficher
        self.effect_indicators = []  # Indicateurs d'effets temporaires
        
        # === NOUVELLES VARIABLES POUR LA GESTION DES TOURS ===
        self.show_logs = False
        self.auto_play_ai = True
        
        # === VARIABLES POUR LE TIMER DE TOUR ===
        self.turn_timer = 45  # 45 secondes par tour
        self.turn_start_time = None
        self.turn_auto_end = False
        print(f"[TIMER] Timer initialisé - turn_timer: {self.turn_timer}s, turn_start_time: {self.turn_start_time}")
        
        # Variables du mulligan
        self.mulligan_mode = False
        self.mulligan_selected_cards = []
        self.mulligan_completed = False
        self.mulligan_timer = 10  # 10 secondes pour le mulligan
        self.mulligan_start_time = None
        self.player_ready = False
        self.opponent_ready = False
        self.mulligan_fade_out = False
        self.mulligan_fade_alpha = 204
        
        # Variables pour le timer de début de combat
        self.combat_start_countdown = False
        self.combat_start_timer = 3  # 3 secondes
        self.combat_start_start_time = None
        
        # Cache pour les polices
        self._font_cache = {}
        
        # Variables de timeout IA
        self.ai_turn_timeout = 2.5  # 2.5 secondes pour le tour de l'IA
        self.ai_turn_start_time = None
        self.ai_turn_auto_end = False
        
        self.setup_buttons()
        self.setup_combat_areas()
        
        # Mode réseau pour le multijoueur
        self.network_mode = False
    
    def set_network_mode(self, is_network_mode: bool):
        """Active le mode réseau pour le multijoueur"""
        self.network_mode = is_network_mode
        print(f"[COMBAT SCREEN] Mode réseau {'activé' if is_network_mode else 'désactivé'}")
    
    def set_multiplayer_mode(self, is_multiplayer: bool, is_host: bool, match_data: dict):
        """Configure le mode multijoueur local"""
        self.network_mode = is_multiplayer
        self.is_host = is_host
        self.match_data = match_data
        print(f"[COMBAT SCREEN] Mode multijoueur local {'activé' if is_multiplayer else 'désactivé'}")
        print(f"[COMBAT SCREEN] Rôle: {'Hôte' if is_host else 'Client'}")
        print(f"[COMBAT SCREEN] Match ID: {match_data.get('match_id', 'Unknown')}")
    
    def update(self):
        """Mise à jour de l'écran de combat"""
        # Mettre à jour les logs de debug du moteur
        if self.combat_engine and hasattr(self.combat_engine, 'log'):
            for log_entry in self.combat_engine.log:
                if (log_entry.startswith("[DEBUG]") or log_entry.startswith("[MANA]") or log_entry.startswith("[TOUR]")) and log_entry not in self.combat_log:
                    self.combat_log.append(log_entry)
        
        # Mise à jour de l'overlay de clic droit
        self.update_right_click_overlay()
        
        # Mise à jour des effets visuels
        self.update_visual_effects()
        
        # Vérifier le timer du mulligan
        self.check_mulligan_timer()
        
        # Vérifier le compte à rebours de début de combat
        self.check_combat_countdown()
        
        # Vérifier le timer du tour
        if self.turn_start_time is not None:
            remaining = self.get_remaining_time()
            if remaining % 10 == 0 and remaining > 0:  # Log toutes les 10 secondes
                print(f"[TIMER UPDATE] Temps restant: {remaining}s")
        self.check_turn_timer()
        
        # === MODE RÉSEAU ===
        if self.network_mode:
            # En mode multijoueur, désactiver l'IA automatique
            self.auto_play_ai = False
            
            # Vérifier si c'est notre tour
            if self.combat_engine and self.combat_engine.current_player_index == 0:  # Notre tour
                # Logique pour notre tour en multijoueur
                pass
            else:
                # Tour de l'adversaire - attendre les actions réseau
                pass
        else:
            # Mode IA normal
            # Vérifier le timeout de l'IA
            self.check_ai_turn_timeout()
        
        # Debug: vérifier si update() est appelé régulièrement
        if not hasattr(self, '_update_counter'):
            self._update_counter = 0
        self._update_counter += 1
        if self._update_counter % 60 == 0:  # Log toutes les 60 frames (environ 1 seconde)
            logger.debug(f"[DEBUG UPDATE] update() appelé {self._update_counter} fois")
        
        # Vérifier si la partie est terminée
        if self.combat_engine:
            game_result = self.combat_engine.is_game_over()
            if game_result["status"] != "ongoing":
                print(f"[FIN DE PARTIE] {game_result['message']}")
                self.combat_log.append(f"=== {game_result['message']} ===")
                # TODO: Afficher un écran de fin de partie
                # Pour l'instant, retourner au menu après 3 secondes
                import threading
                import time
                def return_to_menu():
                    time.sleep(3)
                    self.game_ui.change_screen("main_menu")
                threading.Thread(target=return_to_menu, daemon=True).start()
        
    def setup_buttons(self):
        """Configure les boutons de l'interface de combat"""
        button_width = 150
        button_height = 40
        button_spacing = 10
        
        # Boutons en bas de l'écran
        bottom_y = SCREEN_HEIGHT - button_height - 20
        right_x = SCREEN_WIDTH - button_width - 20
        
        # Disposition demandée : ABANDON au-dessus de LOGS (côté droit)
        self.buttons = [
            Button(20, bottom_y, button_width, button_height, "FIN DE TOUR", 
                   COLORS['crimson'], COLORS['white'], self.end_turn, "Termine le tour actuel"),
            Button(20 + button_width + button_spacing, bottom_y, button_width, button_height, "ACTIVER HÉROS", 
                   COLORS['gold'], COLORS['deep_black'], self.activate_hero, "Active le héros (coût spécial)"),
            Button(right_x, bottom_y - (button_height + button_spacing), button_width, button_height, "ABANDON", 
                   COLORS['gray'], COLORS['white'], self.surrender, "Abandonne la partie"),
            Button(right_x, bottom_y, button_width, button_height, "LOGS", 
                   COLORS['blue'], COLORS['white'], self.toggle_logs, "Affiche/masque les logs de combat")
        ]
        
        # Boutons de mulligan (initialement cachés)
        self.mulligan_buttons = [
            Button(SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 + 100, 120, 40, "MULLIGAN", 
                   COLORS['orange'], COLORS['white'], self.start_mulligan, "Démarre le mulligan"),
            Button(SCREEN_WIDTH // 2 - 60, SCREEN_HEIGHT // 2 + 100, 120, 40, "CONFIRMER", 
                   COLORS['green'], COLORS['white'], self.confirm_mulligan, "Confirme le mulligan"),
            Button(SCREEN_WIDTH // 2 + 80, SCREEN_HEIGHT // 2 + 100, 120, 40, "PASSER", 
                   COLORS['gray'], COLORS['white'], self.skip_mulligan, "Passe le mulligan"),
            Button(SCREEN_WIDTH // 2 + 200, SCREEN_HEIGHT // 2 + 100, 120, 40, "PRÊT", 
                   COLORS['blue'], COLORS['white'], self.set_player_ready, "Se mettre prêt")
        ]
    
    def update_button_positions(self):
        """Met à jour les positions des boutons après la configuration des zones de combat"""
        if hasattr(self, 'opponent_hero_rect') and hasattr(self, 'player_hero_rect') and self.buttons:
            button_width = 150
            button_height = 40
            
            # Bouton "FIN DE TOUR" sous le héros adverse (aligné à droite)
            opponent_hero_bottom = self.opponent_hero_rect.bottom + 20
            self.buttons[0].rect.x = SCREEN_WIDTH - 175  # 225 - 50 (largeur bouton = 150, héros = 200, donc 200-150=50)
            self.buttons[0].rect.y = opponent_hero_bottom
            
            # Bouton "ACTIVER HÉROS" sous le héros du joueur (gauche)
            player_hero_bottom = self.player_hero_rect.bottom + 20
            self.buttons[1].rect.x = 25
            self.buttons[1].rect.y = player_hero_bottom
    
    def setup_combat_areas(self):
        """Configure les zones de combat"""
        # Zone centrale pour les unités - AGRANDIE ET CENTRÉE
        battlefield_width = SCREEN_WIDTH - 500
        battlefield_height = 700  # 600 + 100px supplémentaires
        battlefield_x = (SCREEN_WIDTH - battlefield_width) // 2  # Centrage horizontal
        battlefield_y = (SCREEN_HEIGHT - battlefield_height) // 2  # Centrage vertical
        self.battlefield_rect = pygame.Rect(battlefield_x, battlefield_y, battlefield_width, battlefield_height)
        
        # Zones pour les héros (côtés gauche et droit) - centrés verticalement
        hero_width = 200
        hero_height = 288
        hero_y = (SCREEN_HEIGHT - hero_height) // 2  # Centrage vertical
        self.player_hero_rect = pygame.Rect(25, hero_y, hero_width, hero_height)
        self.opponent_hero_rect = pygame.Rect(SCREEN_WIDTH - 225, hero_y, hero_width, hero_height)
        
        # Zones pour les mains
        self.player_hand_rect = pygame.Rect(50, SCREEN_HEIGHT - 150, SCREEN_WIDTH - 100, 120)
        self.opponent_hand_rect = pygame.Rect(50, 30, SCREEN_WIDTH - 100, 120)
        
        # Zone d'information (mana, tour, etc.)
        self.info_rect = pygame.Rect(SCREEN_WIDTH - 200, 50, 180, 120)
        
        # Mettre à jour les positions des boutons après avoir configuré les zones
        self.update_button_positions()
    

    
    def set_network_mode(self, is_network_mode: bool):
        """Active le mode réseau pour le multijoueur"""
        self.network_mode = is_network_mode
        print(f"[COMBAT SCREEN] Mode réseau {'activé' if is_network_mode else 'désactivé'}")
    
    def start_combat(self, player_deck, opponent_deck=None):
        """Démarre un combat avec les decks fournis"""
        self.combat_log.append("[DEBUG] start_combat() appelé")
        self.combat_log.append(f"[DEBUG] player_deck: {player_deck}")
        
        from Engine.engine import CombatEngine, Player
        from Engine.deck_manager import DeckManager
        from Engine.models import Card, Hero, Unit
        
        self.combat_log.append("[DEBUG] Imports réussis")
        
        # Fonction pour remplir le mana du joueur au début de son tour
        def fill_player_mana():
            if self.player and self.combat_engine:
                old_mana = self.player.mana
                self.player.mana = self.player.max_mana
                self.combat_log.append(f"[MANA] {self.player.name} mana rempli ({old_mana} → {self.player.mana}/{self.player.max_mana})")
                print(f"[MANA] {self.player.name} mana rempli ({old_mana} → {self.player.mana}/{self.player.max_mana})")
        
        # Remplir le mana du joueur au début du combat
        fill_player_mana()
        
        # Créer l'adversaire (IA par défaut)
        if opponent_deck is None:
            self.combat_log.append("[DEBUG] Création du deck IA...")
            # Créer un deck IA par défaut
            deck_manager = DeckManager()
            opponent_deck = deck_manager.create_default_ai_deck()
            self.combat_log.append(f"[DEBUG] Deck IA créé: {opponent_deck}")
            
            # Vérifier que le deck IA est valide
            if not opponent_deck or not opponent_deck.hero or not opponent_deck.units or not opponent_deck.cards:
                print("[ERREUR] Deck IA invalide, impossible de lancer le combat")
                return
            
            # Vérifier que le deck IA respecte les règles
            try:
                from Engine.deck_manager import deck_manager
                deck_manager.validate_deck(opponent_deck)
                print(f"[COMBAT] Deck IA validé: {len(opponent_deck.units)} unités, {len(opponent_deck.cards)} cartes")
            except Exception as e:
                print(f"[ERREUR] Deck IA ne respecte pas les règles: {e}")
                return
        
        def convert_cards(cards_data):
            """Convertit les données JSON des cartes en objets Card"""
            cards = []
            for card_data in cards_data:
                # Utiliser 'card_type' au lieu de 'type' pour correspondre au JSON
                card_type = card_data.get('card_type', card_data.get('type', 'SPELL'))
                # Nettoyer le card_type si nécessaire (enlever 'CARDTYPE.' si présent)
                if card_type.startswith('CARDTYPE.'):
                    card_type = card_type.replace('CARDTYPE.', '')
                
                card = Card(
                    name=card_data.get('name', 'Carte inconnue'),
                    cost=card_data.get('cost', 0),
                    element=card_data.get('element', ''),
                    card_type=card_type,
                    effect=card_data.get('description', ''),
                    target_type=card_data.get('target_type', 'any'),
                    effects=card_data.get('effects', [])  # Ajouter les effets du JSON
                )
                # Ajouter l'image_path
                card.image_path = card_data.get('image_path', 'Card/1.png')
                cards.append(card)
            return cards
        
        def convert_hero(hero_data, deck_customizations=None, is_enemy=False):
            """Convertit les données JSON du héros en objet Hero avec personnalisations"""
            if not hero_data:
                return None
            
            # Récupérer les stats de base
            base_stats = hero_data.get('base_stats', {}).copy()
            logger.debug(f"[CONVERSION] Données JSON pour héros {hero_data.get('name', 'Héros inconnu')}: {hero_data}")
            logger.debug(f"[CONVERSION] base_stats extrait pour héros: {base_stats}")
            
            # Initialiser les valeurs par défaut pour les capacités
            ability_name = hero_data.get('ability_name', '')
            ability_description = hero_data.get('ability_description', '')
            ability_cooldown = hero_data.get('ability_cooldown', 0)
            
            # Appliquer les personnalisations si disponibles
            if deck_customizations and hasattr(deck_customizations, 'customizations'):
                hero_name = hero_data.get('name', '')
                if hero_name in deck_customizations.customizations:
                    customization = deck_customizations.customizations[hero_name]
                    
                    # Appliquer les bonus de stats
                    if 'hp_bonus' in customization:
                        base_stats['hp'] = base_stats.get('hp', 0) + customization['hp_bonus']
                    if 'attack_bonus' in customization:
                        base_stats['attack'] = base_stats.get('attack', 0) + customization['attack_bonus']
                    if 'defense_bonus' in customization:
                        base_stats['defense'] = base_stats.get('defense', 0) + customization['defense_bonus']
                    
                    # Appliquer les modifications de capacité
                    if 'use_hero_ability' in customization:
                        if customization['use_hero_ability']:
                            # Utiliser la capacité du héros (garder les valeurs par défaut)
                            pass
                        else:
                            # Utiliser la capacité passive
                            ability_name = "Passif"
                            ability_description = hero_data.get('passive', 'Aucun passif')
                            ability_cooldown = 0
                    
                    # Si le passif est activé
                    if 'passive_active' in customization and customization['passive_active']:
                        # Ajouter les effets du passif aux stats
                        passive = hero_data.get('passive', '')
                        if '+10 % dégâts' in passive:
                            # Bonus de dégâts pour les alliés (géré par le moteur)
                            pass
                        elif '-10 % dégâts subit' in passive:
                            # Réduction des dégâts subis (géré par le moteur)
                            pass
                        elif '+5 DEF' in passive:
                            base_stats['defense'] = base_stats.get('defense', 0) + 5
                        elif '+2 coût' in passive:
                            # Le coût d'activation sera géré par get_activation_cost()
                            pass
            
            # Créer l'objet Hero
            hero = Hero(
                name=hero_data.get('name', 'Héros inconnu'),
                element=hero_data.get('element', ''),
                base_stats=base_stats,
                ability_name=ability_name,
                ability_description=ability_description,
                ability_cooldown=ability_cooldown
            )
            
            # Transférer toutes les données JSON vers l'objet Hero
            hero.image_path = hero_data.get('image_path', 'Hero/1.png')
            hero.rarity = hero_data.get('rarity', 'Commun')
            hero.is_enemy = is_enemy
            
            # Transférer les stats secondaires
            hero.crit_pct = hero_data.get('crit_pct', 5.0)
            hero.esquive_pct = hero_data.get('esquive_pct', 2.0)
            hero.precision_pct = hero_data.get('precision_pct', 95.0)
            
            # S'assurer que les stats sont correctement initialisées
            if base_stats:
                hero.base_stats = base_stats.copy()
                hero.current_stats = base_stats.copy()
                logger.debug(f"[CONVERSION] Stats héros initialisées depuis JSON: {hero.current_stats}")
            else:
                hero.current_stats = {'hp': 1000, 'attack': 20, 'defense': 15}
                logger.debug(f"[CONVERSION] Stats héros par défaut utilisées: {hero.current_stats}")
            
            # Transférer le passif et la description
            hero.passive = hero_data.get('passive', '')
            hero.description = hero_data.get('description', '')
            
            # Stocker les informations du passif si disponibles
            if deck_customizations and hasattr(deck_customizations, 'customizations'):
                hero_name = hero_data.get('name', '')
                if hero_name in deck_customizations.customizations:
                    customization = deck_customizations.customizations[hero_name]
                    if 'passive_active' in customization:
                        hero._passive_active = customization['passive_active']
                        hero._passive_description = hero_data.get('passive', '')
            
            logger.debug(f"[CONVERSION] Héros {hero.name} converti - HP: {hero.current_stats.get('hp', 0)}, ATK: {hero.current_stats.get('attack', 0)}, DEF: {hero.current_stats.get('defense', 0)}, Image: {hero.image_path}")
            
            return hero
        
        def convert_units(units_data, is_enemy=False):
            """Convertit les données JSON des unités en objets Unit"""
            units = []
            # Gestionnaire pour récupérer les noms/desc/cooldowns des capacités par ID
            try:
                effects_mgr = EffectsDatabaseManager()
                logger.debug("[CONVERSION] EffectsDatabaseManager initialisé avec succès")
            except Exception as e:
                effects_mgr = None
                logger.error(f"[CONVERSION] Erreur lors de l'initialisation d'EffectsDatabaseManager: {e}")
                print(f"[ERREUR] EffectsDatabaseManager non disponible: {e}")
            for unit_data in units_data:
                # Créer l'unité avec les données JSON
                # Extraire les stats directement de l'objet unité (pas de base_stats)
                unit_stats = {
                    'hp': unit_data.get('hp', 100),
                    'attack': unit_data.get('attack', 10),
                    'defense': unit_data.get('defense', 5)
                }
                logger.debug(f"[CONVERSION] Données JSON pour {unit_data.get('name', 'Unité inconnue')}: {unit_data}")
                logger.debug(f"[CONVERSION] Stats extraites: {unit_stats}")
                
                # Construire la liste d'Ability à partir de ability_ids (prioritaire)
                abilities = []
                unit_name = unit_data.get('name', 'Unité inconnue')
                logger.debug(f"[CONVERSION] Chargement des capacités pour {unit_name}")
                
                for ability_id in unit_data.get('ability_ids', []):
                    logger.debug(f"[CONVERSION] Traitement de l'ability_id {ability_id} pour {unit_name}")
                    
                    ability_name = f"Capacité {ability_id}"
                    ability_desc = ""
                    ability_cd = 0
                    
                    if effects_mgr:
                        data = effects_mgr.get_ability(str(ability_id))
                        if data:
                            ability_name = data.get('name', ability_name)
                            ability_desc = data.get('description', '')
                            ability_cd = data.get('base_cooldown', 0)
                            # Stocker l'élément pour l'overlay
                            ability_element = data.get('element', '1')
                            logger.debug(f"[CONVERSION] Capacité {ability_id} chargée: {ability_name}")
                        else:
                            logger.warning(f"[CONVERSION] Aucune donnée trouvée pour l'ability_id {ability_id}")
                            ability_element = '1'  # Élément par défaut
                    else:
                        logger.warning(f"[CONVERSION] EffectsDatabaseManager non disponible pour {ability_id}")
                        ability_element = '1'  # Élément par défaut
                    
                    # Récupérer le target_type depuis les données JSON
                    ability_target_type = data.get('target_type', 'single_enemy')
                    
                    ability_obj = Ability(ability_name, ability_desc, ability_cd, ability_target_type, str(ability_id))
                    # Stocker l'élément pour l'overlay
                    setattr(ability_obj, 'element', ability_element)
                    abilities.append(ability_obj)
                    
                    logger.debug(f"[CONVERSION] Objet Ability créé pour {unit_name}: {ability_name} (ID: {ability_id})")
                # Support optionnel d'un bloc JSON 'abilities' déjà détaillé
                if not abilities:
                    for ability_data in unit_data.get('abilities', []):
                        if isinstance(ability_data, dict):
                            ability = Ability(
                                name=ability_data.get('name', 'Capacité inconnue'),
                                description=ability_data.get('description', ''),
                                cooldown=ability_data.get('cooldown', 0),
                                target_type=ability_data.get('target_type', 'single_enemy'),
                                ability_id=ability_data.get('ability_id', '')
                            )
                            abilities.append(ability)
                
                unit = Unit(
                    name=unit_data.get('name', 'Unité inconnue'),
                    element=unit_data.get('element', ''),
                    stats=unit_stats,
                    abilities=abilities
                )
                
                # Transférer toutes les données JSON vers l'objet Unit
                unit.image_path = unit_data.get('image_path', 'Crea/1.png')
                unit.rarity = unit_data.get('rarity', 'Commun')
                unit.description = unit_data.get('description', 'Aucune description')
                # Ne pas assigner de cooldown directement à l'unité - utiliser le système du moteur
                # unit.cooldown = unit_data.get('cooldown', 0)  # SUPPRIMÉ
                unit.is_enemy = is_enemy
                
                # Préserver les IDs des capacités et passifs pour l'overlay
                unit.ability_ids = unit_data.get('ability_ids', [])
                unit.passive_ids = unit_data.get('passive_ids', [])
                
                # Transférer les stats secondaires
                unit.crit_pct = unit_data.get('crit_pct', 3.0)
                unit.esquive_pct = unit_data.get('esquive_pct', 1.0)
                unit.precision_pct = unit_data.get('precision_pct', 99.0)
                
                # S'assurer que les stats sont correctement initialisées
                unit.base_stats = unit_stats.copy()
                unit.stats = unit_stats.copy()
                logger.debug(f"[CONVERSION] Stats initialisées depuis JSON: {unit.stats}")
                
                logger.debug(f"[CONVERSION] Unité {unit.name} convertie - HP: {unit.stats.get('hp', 0)}, ATK: {unit.stats.get('attack', 0)}, DEF: {unit.stats.get('defense', 0)}, Image: {unit.image_path}")
                logger.debug(f"[CONVERSION] Unité {unit.name} - base_stats: {unit.base_stats}")
                logger.debug(f"[CONVERSION] Unité {unit.name} - stats: {unit.stats}")
                
                units.append(unit)
            return units
        
        # Convertir les données du joueur
        self.combat_log.append("[DEBUG] Conversion des données du joueur...")
        self.combat_log.append(f"[DEBUG] player_deck.units: {player_deck.units}")
        player_cards = convert_cards(player_deck.cards)
        player_hero = convert_hero(player_deck.hero, player_deck, is_enemy=False)
        player_units = convert_units(player_deck.units, is_enemy=False)
        self.combat_log.append(f"[DEBUG] Joueur converti - Cartes: {len(player_cards)}, Héros: {player_hero}, Unités: {len(player_units)}")
        for i, unit in enumerate(player_units):
            self.combat_log.append(f"[DEBUG] Unité joueur {i}: {unit.name} (HP: {unit.stats.get('hp', 0)})")
        
        # Convertir les données de l'IA
        self.combat_log.append("[DEBUG] Conversion des données de l'IA...")
        self.combat_log.append(f"[DEBUG] opponent_deck.units: {opponent_deck.units}")
        opponent_cards = convert_cards(opponent_deck.cards)
        opponent_hero = convert_hero(opponent_deck.hero, is_enemy=True)
        opponent_units = convert_units(opponent_deck.units, is_enemy=True)
        self.combat_log.append(f"[DEBUG] IA convertie - Cartes: {len(opponent_cards)}, Héros: {opponent_hero}, Unités: {len(opponent_units)}")
        for i, unit in enumerate(opponent_units):
            self.combat_log.append(f"[DEBUG] Unité IA {i}: {unit.name} (HP: {unit.stats.get('hp', 0)})")
        
        # Créer les joueurs
        self.combat_log.append("[DEBUG] Création des joueurs...")
        self.combat_log.append(f"[DEBUG] Cartes du joueur avant création: {len(player_cards)}")
        self.combat_log.append(f"[DEBUG] Cartes de l'IA avant création: {len(opponent_cards)}")
        self.combat_log.append(f"[DEBUG] Unités du joueur avant création: {len(player_units)}")
        for i, unit in enumerate(player_units):
            self.combat_log.append(f"[DEBUG] Unité joueur {i}: {unit.name} (is_enemy: {getattr(unit, 'is_enemy', 'N/A')})")
        self.combat_log.append(f"[DEBUG] Unités de l'IA avant création: {len(opponent_units)}")
        for i, unit in enumerate(opponent_units):
            self.combat_log.append(f"[DEBUG] Unité IA {i}: {unit.name} (is_enemy: {getattr(unit, 'is_enemy', 'N/A')})")
        
        self.player = Player("Joueur", player_cards, player_hero, player_units)
        self.opponent = Player("IA", opponent_cards, opponent_hero, opponent_units)
        
        # Assigner l'attribut owner aux unités et héros pour le système de cibles
        for unit in player_units:
            unit.owner = self.player
        for unit in opponent_units:
            unit.owner = self.opponent
        
        # Assigner l'attribut owner aux héros
        if player_hero:
            player_hero.owner = self.player
        if opponent_hero:
            opponent_hero.owner = self.opponent
        
        self.combat_log.append(f"[DEBUG] Cartes du joueur après création: {len(self.player.deck)}")
        self.combat_log.append(f"[DEBUG] Cartes de l'IA après création: {len(self.opponent.deck)}")
        self.combat_log.append(f"[DEBUG] Unités du joueur après création: {len(self.player.units)}")
        for i, unit in enumerate(self.player.units):
            self.combat_log.append(f"[DEBUG] Unité joueur finale {i}: {unit.name} (is_enemy: {getattr(unit, 'is_enemy', 'N/A')})")
        self.combat_log.append(f"[DEBUG] Unités de l'IA après création: {len(self.opponent.units)}")
        for i, unit in enumerate(self.opponent.units):
            self.combat_log.append(f"[DEBUG] Unité IA finale {i}: {unit.name} (is_enemy: {getattr(unit, 'is_enemy', 'N/A')})")
        self.combat_log.append("[DEBUG] Joueurs créés avec succès")
        
        # Créer le moteur de combat avec les joueurs
        self.combat_log.append("[DEBUG] Création du moteur de combat...")
        self.combat_engine = CombatEngine(self.player, self.opponent)
        self.combat_log.append("[DEBUG] Moteur de combat créé")
        
        # Lancer la musique de combat
        self.combat_log.append("[DEBUG] Lancement de la musique de combat...")
        self.game_ui.play_background_music("combat")
        self.combat_log.append("[DEBUG] Musique lancée")
        
        # Initialiser le combat
        self.combat_log.append("[DEBUG] Initialisation du moteur de combat...")
        try:
            # Validation des decks AVANT l'initialisation (pour éviter la pioche initiale)
            self.combat_log.append("[DEBUG] Validation des decks...")
            for i, player in enumerate(self.combat_engine.players):
                validation = self.combat_engine.validate_deck(player)
                self.combat_log.append(f"[VALIDATION] Validation du deck de {player.name}")
                self.combat_log.append(f"[VALIDATION] Héros: {player.hero}")
                self.combat_log.append(f"[VALIDATION] Unités: {len(player.units) if player.units else 0}")
                self.combat_log.append(f"[VALIDATION] Cartes: {len(player.deck) if player.deck else 0}")
                
                if not validation["valid"]:
                    self.combat_log.append(f"[VALIDATION] ERREUR: Deck invalide")
                    for error in validation["errors"]:
                        self.combat_log.append(f"[VALIDATION] ERREUR: {error}")
                    # Lever l'erreur ici pour arrêter l'initialisation
                    raise ValueError(f"Deck du joueur {player.name} invalide")
                else:
                    self.combat_log.append(f"[VALIDATION] Deck valide")
            
            # Si on arrive ici, tous les decks sont valides
            self.combat_log.append("[DEBUG] Tous les decks sont valides, initialisation...")
            self.combat_engine.initialize_game()
            self.combat_log.append("[DEBUG] Moteur de combat initialisé avec succès")
            
            # Vérifier les stats après initialisation
            logger.debug(f"[POST-INIT] Vérification des stats après initialisation du moteur:")
            for unit in self.player.units:
                logger.debug(f"[POST-INIT] Unité {unit.name} - HP: {unit.hp}, ATK: {unit.attack}, DEF: {unit.defense}")
                logger.debug(f"[POST-INIT] Unité {unit.name} - base_stats: {unit.base_stats}")
                logger.debug(f"[POST-INIT] Unité {unit.name} - stats: {unit.stats}")
            
            self.current_phase = "pioche"
            self.combat_log = []
            
            # Ajouter message de début
            self.combat_log.append("=== DÉBUT DU COMBAT ===")
            self.combat_log.append(f"{self.player.name} vs {self.opponent.name}")
            self.combat_log.append("[DEBUG] Combat initialisé avec succès")
            self.combat_log.append("[DEBUG] Lancement de la phase de mulligan...")
            
            # Ajouter les logs de debug du moteur à l'interface
            if hasattr(self.combat_engine, 'log'):
                for log_entry in self.combat_engine.log:
                    if (log_entry.startswith("[DEBUG]") or log_entry.startswith("[MANA]") or 
                        log_entry.startswith("[TOUR]") or log_entry.startswith("[VALIDATION]")):
                        self.combat_log.append(log_entry)
            
            print(f"[COMBAT] Combat initialisé avec succès")
            self.combat_log.append("[DEBUG] Combat initialisé avec succès")
            
            # Vérifier si c'est le tour de l'IA au début et démarrer le timer si nécessaire
            if self.combat_engine.current_player_index == 1:
                print("[COMBAT] Tour de l'IA détecté au début, démarrage du timer de timeout")
                self.start_ai_turn_timer()
            
            # Lancer automatiquement la phase de mulligan
            self.combat_log.append("[DEBUG] Lancement de la phase de mulligan...")
            print(f"[COMBAT] Combat initialisé, lancement de la phase de mulligan")
            print(f"[DEBUG COMBAT] Avant start_mulligan() - self.player: {self.player}")
            self.start_mulligan()
            print(f"[DEBUG COMBAT] Après start_mulligan() - mulligan_mode: {self.mulligan_mode}")
            self.combat_log.append(f"[DEBUG] Après start_mulligan() - mulligan_mode: {self.mulligan_mode}")
            
        except ValueError as e:
            print(f"[ERREUR] Impossible d'initialiser le combat: {e}")
            self.combat_log.append(f"[ERREUR] Impossible d'initialiser le combat: {e}")
            # Retourner au menu principal en cas d'erreur
            self.game_ui.change_screen("main_menu")
            return
        except Exception as e:
            print(f"[ERREUR] Erreur inattendue lors de l'initialisation: {e}")
            self.combat_log.append(f"[ERREUR] Erreur inattendue lors de l'initialisation: {e}")
            # Retourner au menu principal en cas d'erreur
            self.game_ui.change_screen("main_menu")
            return
    
    def start_multiplayer_combat(self, player_deck, match_data):
        """Démarre un combat multijoueur avec synchronisation"""
        self.combat_log.append("[DEBUG] start_multiplayer_combat() appelé")
        self.combat_log.append(f"[DEBUG] player_deck: {player_deck}")
        self.combat_log.append(f"[DEBUG] match_data: {match_data}")
        # Stocker le deck en attente pour démarrer quand les deux joueurs seront prêts
        self._pending_player_deck = player_deck
        self._pending_match_data = match_data
        
        try:
            # Importer le module de synchronisation multijoueur
            from Steam.multiplayer_sync import MultiplayerSync, ActionType
            
            # Initialiser la synchronisation multijoueur
            self.multiplayer_sync = MultiplayerSync()
            
            # Configurer les callbacks
            self.multiplayer_sync.on_action_received = self._handle_opponent_action
            self.multiplayer_sync.on_turn_changed = self._handle_turn_change
            self.multiplayer_sync.on_game_started = self._handle_game_started
            self.multiplayer_sync.on_game_ended = self._handle_game_ended
            
            # Initialiser le jeu avec le serveur
            match_id = match_data.get('match_id')
            # Utiliser l'ID du joueur depuis les données du match
            current_player_id = match_data.get('player1', {}).get('id')
            if not self.is_host:  # Si on n'est pas l'hôte, on est le joueur 2
                current_player_id = match_data.get('player2', {}).get('id')
            player_id = str(current_player_id)
            
            # Convertir le deck en format JSON pour l'envoi
            deck_data = {
                "name": player_deck.name,
                "hero": player_deck.hero,
                "units": player_deck.units,
                "cards": player_deck.cards
            }
            
            if self.multiplayer_sync.initialize_game(match_id, player_id, deck_data):
                print(f"[MULTIPLAYER] Jeu initialisé avec succès")
                self.combat_log.append("[MULTIPLAYER] Jeu initialisé avec succès")
                
                # CONFIGURER LE MODE MULTIJOUEUR MAIS NE PAS LANCER LE COMBAT TANT QUE LES 2 NE SONT PAS PRÊTS
                self.network_mode = True
                self.multiplayer_match_data = match_data
                self.is_host = match_data.get('player1', {}).get('id') == current_player_id
                print(f"[MULTIPLAYER] Mode multijoueur configuré - Host: {self.is_host}")
                self.combat_log.append(f"[MULTIPLAYER] Mode multijoueur configuré - Host: {self.is_host}")
                # Le combat démarrera dans _handle_game_started
            else:
                print(f"[MULTIPLAYER] Erreur d'initialisation du jeu")
                self.combat_log.append("[MULTIPLAYER] Erreur d'initialisation du jeu")
                self.game_ui.change_screen("pre_combat")
                
        except Exception as e:
            print(f"[MULTIPLAYER] Erreur lors du démarrage du combat multijoueur: {e}")
            self.combat_log.append(f"[MULTIPLAYER] Erreur: {e}")
            import traceback
            traceback.print_exc()
            self.game_ui.change_screen("pre_combat")
    
    def _handle_opponent_action(self, action):
        """Gère une action reçue de l'adversaire"""
        print(f"[MULTIPLAYER] Action reçue: {action.action_type.value}")
        self.combat_log.append(f"[MULTIPLAYER] Action reçue: {action.action_type.value}")
        
        # Traiter l'action selon son type
        if action.action_type == ActionType.PLAY_CARD:
            self._handle_opponent_card_play(action.data)
        elif action.action_type == ActionType.USE_ABILITY:
            self._handle_opponent_ability_use(action.data)
        elif action.action_type == ActionType.END_TURN:
            self._handle_opponent_end_turn()
    
    def _handle_opponent_card_play(self, data):
        """Gère le jeu d'une carte par l'adversaire"""
        card_name = data.get('card_name')
        target = data.get('target')
        print(f"[MULTIPLAYER] Adversaire joue {card_name} sur {target}")
        self.combat_log.append(f"[MULTIPLAYER] Adversaire joue {card_name}")
        
        # TODO: Implémenter la logique pour appliquer l'action de l'adversaire
    
    def _handle_opponent_ability_use(self, data):
        """Gère l'utilisation d'une capacité par l'adversaire"""
        ability_name = data.get('ability_name')
        target = data.get('target')
        print(f"[MULTIPLAYER] Adversaire utilise {ability_name} sur {target}")
        self.combat_log.append(f"[MULTIPLAYER] Adversaire utilise {ability_name}")
        
        # TODO: Implémenter la logique pour appliquer l'action de l'adversaire
    
    def _handle_opponent_end_turn(self):
        """Gère la fin de tour de l'adversaire"""
        print(f"[MULTIPLAYER] Adversaire termine son tour")
        self.combat_log.append("[MULTIPLAYER] Adversaire termine son tour")
        
        # TODO: Implémenter la logique pour passer au tour suivant
    
    def _handle_turn_change(self, is_my_turn):
        """Gère le changement de tour"""
        print(f"[MULTIPLAYER] Changement de tour: {'Mon tour' if is_my_turn else 'Tour adversaire'}")
        self.combat_log.append(f"[MULTIPLAYER] {'Mon tour' if is_my_turn else 'Tour adversaire'}")
        
        if is_my_turn:
            # C'est notre tour, activer les contrôles
            self.player_turn_active = True
        else:
            # C'est le tour de l'adversaire, désactiver les contrôles
            self.player_turn_active = False
    
    def _handle_game_started(self):
        """Gère le démarrage du jeu"""
        print(f"[MULTIPLAYER] Jeu démarré")
        self.combat_log.append("[MULTIPLAYER] Jeu démarré")
        # Lancer réellement le combat une fois que le serveur indique que les deux joueurs sont prêts
        try:
            # Récupérer le deck adverse depuis le serveur
            opponent_deck_data = None
            if hasattr(self, 'multiplayer_sync') and self.multiplayer_sync:
                opponent_deck_data = self.multiplayer_sync.get_opponent_deck()
            if not opponent_deck_data:
                print("[MULTIPLAYER] Deck adverse indisponible, fallback AI deck")
                from Engine.deck_manager import deck_manager
                temp_opponent_deck = deck_manager.create_ai_deck()
            else:
                # Construire un Deck à partir du dict
                from Engine.deck_manager import Deck
                temp_opponent_deck = Deck.from_dict(opponent_deck_data)
            # Basculer sur l'écran de combat et démarrer
            if self._pending_player_deck:
                self.game_ui.change_screen("combat")
                self.start_combat(self._pending_player_deck, temp_opponent_deck)
                print(f"[MULTIPLAYER] Combat multijoueur démarré (synchro OK)")
                self.combat_log.append("[MULTIPLAYER] Combat multijoueur démarré (synchro OK)")
        except Exception as e:
            print(f"[MULTIPLAYER] Erreur au démarrage effectif du combat: {e}")
            self.combat_log.append(f"[MULTIPLAYER] Erreur au démarrage effectif du combat: {e}")
    
    def _handle_game_ended(self, result):
        """Gère la fin du jeu"""
        print(f"[MULTIPLAYER] Jeu terminé: {result}")
        self.combat_log.append(f"[MULTIPLAYER] Jeu terminé: {result}")
        
        # Arrêter la synchronisation
        if hasattr(self, 'multiplayer_sync'):
            self.multiplayer_sync.stop_sync()
        
        # Si l'adversaire a abandonné, afficher une popup et rester dans l'écran
        reason = (result or {}).get("reason")
        if reason == "surrender":
            self.show_surrender_popup()
    
    # === NOUVELLES MÉTHODES POUR LE SYSTÈME DE CIBLAGE ===
    
    def start_targeting(self, card):
        """Démarre le mode de ciblage pour une carte"""
        if not self.combat_engine or not self.player:
            return
        
        self.targeting_mode = True
        self.targeting_card = card
        self.targeting_info = self.combat_engine.get_targeting_info(card, self.player)
        self.valid_targets = self.combat_engine.get_valid_targets(card, self.player)
        self.highlighted_targets = []
        
        print(f"[CIBLAGE] Mode ciblage activé pour {card.name}")
    
    def cancel_targeting(self):
        """Annule le mode de ciblage"""
        self.targeting_mode = False
        self.targeting_card = None
        self.valid_targets = []
        self.highlighted_targets = []
        self.targeting_info = None
        print("[CIBLAGE] Mode ciblage annulé")
    
    def select_target(self, target):
        """Sélectionne une cible et joue la carte"""
        print(f"[DEBUG] select_target appelé avec target: {target}")
        self.combat_log.append(f"[DEBUG] select_target appelé avec target: {target}")
        
        if not self.targeting_mode or not self.targeting_card:
            print(f"[DEBUG] Mode ciblage invalide: targeting_mode={self.targeting_mode}, targeting_card={self.targeting_card}")
            self.combat_log.append(f"[DEBUG] Mode ciblage invalide")
            return
        
        # Vérifier que la cible est valide
        if hasattr(self, 'valid_targets') and target not in self.valid_targets:
            print(f"[CIBLAGE] Cible invalide: {target}")
            self.combat_log.append(f"[CIBLAGE] Cible invalide: {target}")
            return
        
        # Jouer la carte avec la cible
        try:
            print(f"[DEBUG] Début du traitement de la carte {self.targeting_card.name}")
            self.combat_log.append(f"[DEBUG] Début du traitement de la carte {self.targeting_card.name}")
            
            # Trouver l'index de la carte dans la main
            card_index = None
            for i, card in enumerate(self.player.hand):
                if card == self.targeting_card:
                    card_index = i
                    break
            
            print(f"[DEBUG] Index de carte trouvé: {card_index}")
            self.combat_log.append(f"[DEBUG] Index de carte trouvé: {card_index}")
            
            if card_index is not None:
                # Créer les informations de ciblage
                target_info = {
                    'target': target,
                    'target_type': self.targeting_info.get('target_type', 'any')
                }
                
                print(f"[DEBUG] Target info créé: {target_info}")
                self.combat_log.append(f"[DEBUG] Target info créé")
                
                # Jouer la carte via le moteur
                success, message = self.combat_engine.play_card_with_target(card_index, target_info, self.player)
                
                if success:
                    print(f"[CIBLAGE] Carte {self.targeting_card.name} jouée sur {target}")
                    # Ajouter effet visuel
                    self.add_visual_effect("card_played", target)
                    # Ajouter le message au log de combat
                    self.combat_log.append(f"[CARTE] {self.targeting_card.name} jouée sur {target.name}")
                else:
                    print(f"[CIBLAGE] Échec de l'utilisation de {self.targeting_card.name}: {message}")
                    # Ajouter le message d'erreur au log de combat
                    self.combat_log.append(f"[ERREUR] {message}")
            else:
                self.combat_log.append(f"[ERREUR] Index de carte non trouvé!")
            
        except Exception as e:
            print(f"[ERREUR] Erreur lors de l'utilisation de la carte: {e}")
            self.combat_log.append(f"[ERREUR] Erreur lors de l'utilisation de la carte: {e}")
        
        # Sortir du mode ciblage
        self.cancel_targeting()
    
    # === NOUVELLES MÉTHODES POUR LES CAPACITÉS ===
    
    def start_ability_targeting(self, ability, source):
        """Démarre le mode de ciblage pour une capacité"""
        logger.debug(f"[DEBUG] start_ability_targeting appelé avec ability: {ability}, source: {source}")
        
        if not self.combat_engine:
            logger.debug(f"[DEBUG] Combat engine non disponible")
            return
        
        logger.debug(f"[DEBUG] Initialisation du mode ciblage")
        self.ability_mode = True
        self.selected_ability = ability
        self.ability_source = source
        
        # Obtenir les cibles valides pour cette capacité
        self.ability_targets = []
        logger.debug(f"[DEBUG] target_type de la capacité: {getattr(ability, 'target_type', 'Non défini')}")
        
        # CORRECTION : Utiliser le système de ciblage du combat engine
        try:
            # Convertir l'objet Ability en dictionnaire pour get_available_targets_for_ability
            original_target_type = getattr(ability, 'target_type', 'single_enemy')
            
            # CORRECTION : Pour les capacités adjacentes, utiliser le ciblage single_* pour l'UI
            if original_target_type in ["adjacent_enemies", "adjacent_allies"]:
                # Convertir en type de ciblage unique pour l'interface
                if original_target_type == "adjacent_enemies":
                    ui_target_type = "single_enemy"
                else:  # adjacent_allies
                    ui_target_type = "single_ally"
                
                ability_data = {
                    'target_type': ui_target_type,
                    'target_conditions': getattr(ability, 'target_conditions', ['alive'])
                }
                logger.debug(f"[DEBUG] Capacité {original_target_type} convertie en {ui_target_type} pour l'UI")
            else:
                ability_data = {
                    'target_type': original_target_type,
                    'target_conditions': getattr(ability, 'target_conditions', ['alive'])
                }
            
            # Obtenir les cibles via le combat engine
            self.ability_targets = self.combat_engine.get_available_targets_for_ability(ability_data, source, self.combat_engine)
            logger.debug(f"[DEBUG] Cibles obtenues via combat engine: {len(self.ability_targets)}")
            
        except Exception as e:
            logger.error(f"[ERREUR] Erreur lors de la récupération des cibles: {e}")
            # Fallback vers l'ancien système
            if hasattr(ability, 'target_type'):
                if ability.target_type == "enemy":
                    logger.debug(f"[DEBUG] Cible ennemie - opponent.units: {len(self.opponent.units)}, opponent.hero: {self.opponent.hero}")
                    self.ability_targets = self.opponent.units + [self.opponent.hero]
                elif ability.target_type == "ally":
                    logger.debug(f"[DEBUG] Cible alliée - player.units: {len(self.player.units)}, player.hero: {self.player.hero}")
                    self.ability_targets = self.player.units + [self.player.hero]
                elif ability.target_type == "self":
                    logger.debug(f"[DEBUG] Cible soi-même - source: {source}")
                    self.ability_targets = [source]
                else:  # any
                    logger.debug(f"[DEBUG] Cible quelconque - player.units: {len(self.player.units)}, opponent.units: {len(self.opponent.units)}")
                    self.ability_targets = self.player.units + [self.player.hero] + self.opponent.units + [self.opponent.hero]
            else:
                logger.debug(f"[DEBUG] Pas de target_type défini, utilisation par défaut 'any'")
                self.ability_targets = self.player.units + [self.player.hero] + self.opponent.units + [self.opponent.hero]
        
        logger.debug(f"[DEBUG] Cibles avant filtrage: {len(self.ability_targets)}")
        for target in self.ability_targets:
            logger.debug(f"[DEBUG] - {target.name if hasattr(target, 'name') else 'Cible'}")
        
        # Filtrer les cibles vivantes
        filtered_targets = []
        logger.debug(f"[DEBUG] Filtrage des cibles vivantes...")
        for target in self.ability_targets:
            logger.debug(f"[DEBUG] Vérification de {target.name if hasattr(target, 'name') else 'Cible'}")
            
            if hasattr(target, 'stats') and target.stats.get('hp', 0) > 0:
                logger.debug(f"[DEBUG] - Cible vivante (stats): HP={target.stats.get('hp', 0)}")
                filtered_targets.append(target)
            elif hasattr(target, 'current_stats') and target.current_stats.get('hp', 0) > 0:
                logger.debug(f"[DEBUG] - Cible vivante (current_stats): HP={target.current_stats.get('hp', 0)}")
                filtered_targets.append(target)
            elif hasattr(target, 'hp') and target.hp > 0:
                logger.debug(f"[DEBUG] - Cible vivante (hp): HP={target.hp}")
                filtered_targets.append(target)
            else:
                logger.debug(f"[DEBUG] - Cible morte ou invalide")
        
        self.ability_targets = filtered_targets
        logger.debug(f"[DEBUG] Cibles après filtrage: {len(self.ability_targets)}")
        
        logger.debug(f"[CAPACITÉ] Mode ciblage activé pour {ability.name}")
        logger.debug(f"[CAPACITÉ] Cibles disponibles: {len(self.ability_targets)}")
        for target in self.ability_targets:
            logger.debug(f"[CAPACITÉ] - {target.name if hasattr(target, 'name') else 'Cible'}")
        
        # CORRECTION : Pour les capacités automatiques, utiliser sans demander de ciblage
        target_type = getattr(ability, 'target_type', 'single_enemy')
        
        # Capacités qui s'utilisent automatiquement
        auto_use_types = [
            "all_allies", "all_enemies", "all_units",  # Cibles multiples
            "random_enemy", "random_ally", "random_unit",  # Cibles aléatoires
            "front_row", "back_row",  # Cibles par position
            "chain_enemies", "chain_allies"  # Cibles en chaîne
        ]
        
        if target_type in auto_use_types:
            logger.debug(f"[CAPACITÉ] Capacité {target_type} détectée, utilisation automatique")
            # Utiliser la capacité automatiquement sur toutes les cibles
            self.use_ability_on_target(None)  # None car on utilise toutes les cibles
        
        # Capacités adjacentes : demander une cible initiale, puis propagation automatique
        elif target_type in ["adjacent_enemies", "adjacent_allies"]:
            logger.debug(f"[CAPACITÉ] Capacité {target_type} détectée, ciblage initial requis")
            # Le mode ciblage reste actif pour que le joueur sélectionne la cible principale
    
    def cancel_ability_targeting(self):
        """Annule le mode de ciblage des capacités"""
        self.ability_mode = False
        self.selected_ability = None
        self.ability_source = None
        self.ability_targets = []
        logger.debug("[CAPACITÉ] Mode ciblage annulé")
    
    def use_ability_on_target(self, target):
        """Utilise une capacité sur une cible"""
        if not self.ability_mode or not self.selected_ability or not self.ability_source:
            return
        
        # Vérifier que la capacité peut être utilisée
        if not self.combat_engine.can_use_ability(self.ability_source, self.selected_ability):
            logger.debug(f"[CAPACITÉ] Capacité {self.selected_ability.name} ne peut pas être utilisée")
            return
        
        try:
            # CORRECTION : Gestion des différents types de ciblage
            target_type = getattr(self.selected_ability, 'target_type', 'single_enemy')
            
            # Capacités qui s'utilisent automatiquement sur toutes les cibles
            auto_use_types = [
                "all_allies", "all_enemies", "all_units",  # Cibles multiples
                "random_enemy", "random_ally", "random_unit",  # Cibles aléatoires
                "front_row", "back_row",  # Cibles par position
                "chain_enemies", "chain_allies"  # Cibles en chaîne
            ]
            
            if target_type in auto_use_types:
                # Utiliser la capacité sur toutes les cibles automatiquement
                # Pour les capacités avec ability_id, utiliser use_ability_by_id directement
                if hasattr(self.selected_ability, 'ability_id') and self.selected_ability.ability_id:
                    success, message = self.combat_engine.use_ability_by_id(self.ability_source, self.selected_ability.ability_id, None)
                    if success:
                        logger.debug(f"[CAPACITÉ] Capacité {self.selected_ability.name} utilisée sur {len(self.ability_targets)} cibles ({target_type})")
                        # Ajouter effet visuel sur toutes les cibles
                        for t in self.ability_targets:
                            self.add_visual_effect("ability_used", t)
                    else:
                        logger.debug(f"[CAPACITÉ] Échec de l'utilisation de {self.selected_ability.name}: {message}")
                else:
                    # Fallback pour les capacités sans ID
                    success = self.combat_engine.use_ability(self.ability_source, self.selected_ability, self.ability_targets)
                    if success:
                        logger.debug(f"[CAPACITÉ] Capacité {self.selected_ability.name} utilisée sur {len(self.ability_targets)} cibles ({target_type})")
                        # Ajouter effet visuel sur toutes les cibles
                        for t in self.ability_targets:
                            self.add_visual_effect("ability_used", t)
                    else:
                        logger.debug(f"[CAPACITÉ] Échec de l'utilisation de {self.selected_ability.name}")
            
            # Capacités adjacentes : ciblage initial + propagation automatique
            elif target_type in ["adjacent_enemies", "adjacent_allies"]:
                # Vérifier que la cible est valide
                if target is None or target not in self.ability_targets:
                    logger.debug(f"[CAPACITÉ] Cible invalide pour capacité adjacente: {target}")
                    return
                
                # Utiliser la capacité sur la cible sélectionnée (la propagation se fait dans le moteur)
                if hasattr(self.selected_ability, 'ability_id') and self.selected_ability.ability_id:
                    success, message = self.combat_engine.use_ability_by_id(self.ability_source, self.selected_ability.ability_id, target)
                    if success:
                        logger.debug(f"[CAPACITÉ] Capacité {self.selected_ability.name} utilisée sur {target} avec propagation adjacente")
                        # Ajouter effet visuel sur la cible principale
                        self.add_visual_effect("ability_used", target)
                    else:
                        logger.debug(f"[CAPACITÉ] Échec de l'utilisation de {self.selected_ability.name}: {message}")
                else:
                    # Fallback pour les capacités sans ID
                    success = self.combat_engine.use_ability(self.ability_source, self.selected_ability, target)
                    if success:
                        logger.debug(f"[CAPACITÉ] Capacité {self.selected_ability.name} utilisée sur {target} avec propagation adjacente")
                        # Ajouter effet visuel sur la cible principale
                        self.add_visual_effect("ability_used", target)
                    else:
                        logger.debug(f"[CAPACITÉ] Échec de l'utilisation de {self.selected_ability.name}")
            
            # Capacités à ciblage unique classique
            else:
                # Vérifier que la cible est valide
                if target is None or target not in self.ability_targets:
                    logger.debug(f"[CAPACITÉ] Cible invalide: {target}")
                    return
                
                # Utiliser la capacité sur la cible sélectionnée
                if hasattr(self.selected_ability, 'ability_id') and self.selected_ability.ability_id:
                    success, message = self.combat_engine.use_ability_by_id(self.ability_source, self.selected_ability.ability_id, target)
                    if success:
                        logger.debug(f"[CAPACITÉ] Capacité {self.selected_ability.name} utilisée sur {target}")
                        # Ajouter effet visuel
                        self.add_visual_effect("ability_used", target)
                    else:
                        logger.debug(f"[CAPACITÉ] Échec de l'utilisation de {self.selected_ability.name}: {message}")
                else:
                    # Fallback pour les capacités sans ID
                    success = self.combat_engine.use_ability(self.ability_source, self.selected_ability, target)
                    if success:
                        logger.debug(f"[CAPACITÉ] Capacité {self.selected_ability.name} utilisée sur {target}")
                        # Ajouter effet visuel
                        self.add_visual_effect("ability_used", target)
                    else:
                        logger.debug(f"[CAPACITÉ] Échec de l'utilisation de {self.selected_ability.name}")
            
        except Exception as e:
            logger.error(f"[ERREUR] Erreur lors de l'utilisation de la capacité: {e}")
        
        # Sortir du mode ciblage
        self.cancel_ability_targeting()
        
        # CORRECTION : Rafraîchir le menu des capacités pour mettre à jour l'affichage
        # des cooldowns après utilisation d'une capacité
        if self.ability_menu is not None and self.ability_menu_unit is not None:
            # Recréer le menu avec les capacités mises à jour
            if hasattr(self.ability_menu_unit, 'abilities'):
                # Pour les unités
                self.create_ability_menu(self.ability_menu_unit, self.ability_menu_unit.abilities)
            elif hasattr(self.ability_menu_unit, 'ability') and self.ability_menu_unit.ability:
                # Pour les héros
                self.create_ability_menu(self.ability_menu_unit, [self.ability_menu_unit.ability])
    
    # === NOUVELLES MÉTHODES POUR LES EFFETS VISUELS ===
    
    def add_visual_effect(self, effect_type, target, duration=60):
        """Ajoute un effet visuel"""
        effect = {
            'type': effect_type,
            'target': target,
            'duration': duration,
            'timer': duration
        }
        self.visual_effects.append(effect)
    
    def add_damage_number(self, target, amount, is_critical=False):
        """Ajoute un nombre de dégâts à afficher"""
        damage_effect = {
            'type': 'damage',
            'target': target,
            'amount': amount,
            'critical': is_critical,
            'timer': 60,
            'y_offset': 0
        }
        self.damage_numbers.append(damage_effect)
    
    def add_heal_number(self, target, amount):
        """Ajoute un nombre de soins à afficher"""
        heal_effect = {
            'type': 'heal',
            'target': target,
            'amount': amount,
            'timer': 60,
            'y_offset': 0
        }
        self.heal_numbers.append(heal_effect)
    
    def add_effect_indicator(self, target, effect_type, duration):
        """Ajoute un indicateur d'effet temporaire"""
        indicator = {
            'type': effect_type,
            'target': target,
            'duration': duration,
            'timer': duration * 60,  # 60 FPS
            'alpha': 255
        }
        self.effect_indicators.append(indicator)
    
    def update_visual_effects(self):
        """Met à jour tous les effets visuels"""
        # Mettre à jour les effets visuels
        self.visual_effects = [effect for effect in self.visual_effects if effect['timer'] > 0]
        for effect in self.visual_effects:
            effect['timer'] -= 1
        
        # Mettre à jour les nombres de dégâts
        self.damage_numbers = [effect for effect in self.damage_numbers if effect['timer'] > 0]
        for effect in self.damage_numbers:
            effect['timer'] -= 1
            effect['y_offset'] -= 1  # Monter vers le haut
        
        # Mettre à jour les nombres de soins
        self.heal_numbers = [effect for effect in self.heal_numbers if effect['timer'] > 0]
        for effect in self.heal_numbers:
            effect['timer'] -= 1
            effect['y_offset'] -= 1  # Monter vers le haut
        
        # Mettre à jour les indicateurs d'effets
        self.effect_indicators = [indicator for indicator in self.effect_indicators if indicator['timer'] > 0]
        for indicator in self.effect_indicators:
            indicator['timer'] -= 1
            if indicator['timer'] < 30:  # Fade out
                indicator['alpha'] = max(0, indicator['alpha'] - 8)
    
    # === NOUVELLES MÉTHODES POUR LA GESTION DES TOURS ===
    

    
    def execute_draw_phase(self):
        """Exécute la phase de pioche"""
        if not self.combat_engine or not self.player:
            return
        
        # Pioche conditionnelle : seulement si moins de 9 cartes (selon documentation)
        if len(self.player.hand) < 9:
            drawn_card = self.player.draw_card()
            if drawn_card:
                print(f"[PHASE PIOCHE] {drawn_card.name} piochée")
                self.add_visual_effect("card_drawn", self.player)
        else:
            print(f"[PHASE PIOCHE] Main pleine ({len(self.player.hand)}/9 cartes) - pas de pioche")
    
    def execute_mana_phase(self):
        """Exécute la phase de mana"""
        if not self.combat_engine or not self.player:
            return
        
        # Le mana max est géré par le moteur, on ne fait que remplir le mana actuel
        self.player.mana = self.player.max_mana
        print(f"[PHASE MANA] Mana: {self.player.mana}/{self.player.max_mana}")
        self.add_visual_effect("mana_gained", self.player)
    
    def execute_actions_phase(self):
        """Exécute la phase d'actions (mode interactif)"""
        print("[PHASE ACTIONS] Mode interactif - le joueur peut agir")
        # Cette phase reste interactive pour le joueur
        # Le joueur doit cliquer sur "FIN DE TOUR" pour passer à la phase suivante
    
    def execute_combat_phase(self):
        """Exécute la phase de combat"""
        if not self.combat_engine:
            return
        
        print("[PHASE COMBAT] Combat automatique en cours...")
        # Le combat automatique est géré par le moteur
    
    def execute_end_phase(self):
        """Exécute la phase de fin de tour"""
        if not self.combat_engine:
            return
        
        print("[PHASE FIN] Fin de tour")
        # La réduction des cooldowns est gérée dans next_turn()
    
    def execute_complete_turn(self):
        """Exécute automatiquement toutes les phases d'un tour complet"""
        if not self.combat_engine:
            logger.error("[DEBUG TOUR] ERREUR: combat_engine est None dans execute_complete_turn()")
            return
        
        logger.debug("[TOUR] Exécution automatique du tour complet")
        logger.debug(f"[DEBUG TOUR] Tour actuel avant execute_complete_turn: {self.combat_engine.turn_count}")
        logger.debug(f"[DEBUG TOUR] Joueur actuel avant execute_complete_turn: {self.combat_engine.current_player_index}")
        logger.debug("[DEBUG TEST] Test de debug dans execute_complete_turn() - CODE MODIFIÉ")
        
        # Phase 1: Pioche
        self.execute_draw_phase()
        
        # Phase 2: Mana
        self.execute_mana_phase()
        
        # Phase 3: Combat automatique
        self.execute_combat_phase()
        
        # Phase 4: Fin de tour
        self.execute_end_phase()
        
        # Passer au tour suivant
        logger.debug("[DEBUG TOUR] Appel de next_turn()...")
        try:
            self.combat_engine.next_turn()
            logger.debug(f"[DEBUG TOUR] Tour actuel après next_turn: {self.combat_engine.turn_count}")
            logger.debug(f"[DEBUG TOUR] Joueur actuel après next_turn: {self.combat_engine.current_player_index}")
        except Exception as e:
            logger.error(f"[ERREUR] Exception dans next_turn(): {e}")
            import traceback
            logger.error(f"[ERREUR] Traceback: {traceback.format_exc()}")
        
        # La réduction des cooldowns est déjà gérée dans next_turn()
        
        # Vérifier si c'est maintenant le tour de l'IA
        if self.combat_engine.current_player_index == 1:
            # C'est le tour de l'IA, démarrer le timer de timeout
            self.start_ai_turn_timer()
        else:
            # C'est le tour du joueur, remplir le mana et démarrer le timer normal
            if self.player:
                old_mana = self.player.mana
                self.player.mana = self.player.max_mana
                self.combat_log.append(f"[MANA] {self.player.name} mana rempli après tour IA ({old_mana} → {self.player.mana}/{self.player.max_mana})")
                print(f"[MANA] {self.player.name} mana rempli après tour IA ({old_mana} → {self.player.mana}/{self.player.max_mana})")
            
            # Retourner à la phase actions pour le joueur
            self.current_phase = "actions"
            
            # Démarrer le timer du nouveau tour
            self.start_turn_timer()
    
    def start_turn_timer(self):
        """Démarre le timer de 45 secondes pour le tour actuel"""
        self.turn_start_time = pygame.time.get_ticks()
        self.turn_auto_end = False
        print(f"[TIMER] Timer de {self.turn_timer} secondes démarré à {self.turn_start_time}")
        print(f"[TIMER] Temps restant initial: {self.get_remaining_time()}s")
        print(f"[TIMER] Tour du joueur: {self.combat_engine.current_player_index if self.combat_engine else 'None'}")
        print(f"[TIMER] Tour du joueur: {self.combat_engine.current_player_index if self.combat_engine else 'None'}")
    
    def check_turn_timer(self):
        """Vérifie si le timer du tour est écoulé"""
        if self.turn_start_time is None:
            return
        
        current_time = pygame.time.get_ticks()
        elapsed_seconds = (current_time - self.turn_start_time) // 1000
        
        if elapsed_seconds >= self.turn_timer and not self.turn_auto_end:
            logger.debug(f"[TIMER] Timer écoulé ({elapsed_seconds}s), fin automatique du tour")
            logger.debug(f"[DEBUG TIMER] Tour actuel avant timer: {self.combat_engine.turn_count if self.combat_engine else 'None'}")
            self.turn_auto_end = True
            self.execute_complete_turn()
    
    def get_remaining_time(self):
        """Retourne le temps restant en secondes"""
        if self.turn_start_time is None:
            print(f"[TIMER DEBUG] turn_start_time est None, retourne {self.turn_timer}")
            return self.turn_timer
        
        current_time = pygame.time.get_ticks()
        elapsed_seconds = (current_time - self.turn_start_time) // 1000
        remaining = max(0, self.turn_timer - elapsed_seconds)
        
        # Debug toutes les 5 secondes
        if elapsed_seconds % 5 == 0 and elapsed_seconds > 0:
            print(f"[TIMER DEBUG] Temps écoulé: {elapsed_seconds}s, Restant: {remaining}s")
        
        return remaining
    
    def start_ai_turn_timer(self):
        """Démarre le timer de timeout pour le tour de l'IA"""
        self.ai_turn_start_time = pygame.time.get_ticks()
        self.ai_turn_auto_end = False
        print(f"[AI TIMER] Timer de {self.ai_turn_timeout}s démarré pour l'IA")
    
    def check_ai_turn_timeout(self):
        """Vérifie si le timeout du tour de l'IA est écoulé"""
        if (self.ai_turn_start_time is None or 
            self.ai_turn_auto_end or 
            not self.combat_engine or 
            self.combat_engine.current_player_index != 1):
            return
        
        current_time = pygame.time.get_ticks()
        elapsed_seconds = (current_time - self.ai_turn_start_time) / 1000.0
        
        if elapsed_seconds >= self.ai_turn_timeout:
            print(f"[AI TIMER] Timeout écoulé ({elapsed_seconds:.1f}s), fin forcée du tour de l'IA")
            self.ai_turn_auto_end = True
            self.force_ai_turn_end()
    
    def force_ai_turn_end(self):
        """Force la fin du tour de l'IA"""
        if not self.combat_engine or self.combat_engine.current_player_index != 1:
            return
        
        print("[AI TIMER] Forçage de la fin du tour de l'IA")
        self.combat_log.append("[AI TIMER] Tour de l'IA terminé par timeout")
        
        # Exécuter le tour complet pour passer au joueur suivant
        self.execute_complete_turn()
    
    def draw(self, screen: pygame.Surface):
        """Dessin de l'écran de combat"""
        # Le background est déjà dessiné par GameUI.draw_background()
        # Pas besoin de screen.fill() qui recouvrirait le background
        
        # Dessiner le plateau de combat
        # self.draw_battlefield(screen)  # Méthode supprimée car elle n'existe pas
        
        # Dessiner les héros
        if hasattr(self, 'player_hero_rect') and hasattr(self, 'opponent_hero_rect'):
            # Dessiner le héros du joueur
            if self.player and self.player.hero:
                hero_surface = self.create_hero_overlay_surface_combat(self.player.hero)
                screen.blit(hero_surface, self.player_hero_rect)
            # Dessiner le héros de l'adversaire
            if self.opponent and self.opponent.hero:
                hero_surface = self.create_hero_overlay_surface_combat(self.opponent.hero)
                screen.blit(hero_surface, self.opponent_hero_rect)
        

        # Dessiner les unités (bloc centré)
        # Calculer les positions Y pour le bloc centré
        unit_height = 288
        spacing_between_groups = 40  # Espacement entre unités ennemies et alliées
        
        # Position Y du centre de l'écran
        center_y = SCREEN_HEIGHT // 2
        
        # Position Y des unités ennemies (haut du bloc)
        enemy_units_y = center_y - unit_height - spacing_between_groups // 2
        
        # Position Y des unités alliées (bas du bloc)
        ally_units_y = center_y + spacing_between_groups // 2
        
        # Unités ennemies (haut)
        logger.debug(f"[DEBUG] Vérification unités ennemies: opponent={self.opponent}, units={getattr(self.opponent, 'units', None) if self.opponent else None}")
        if self.opponent and self.opponent.units:
            logger.debug(f"[DEBUG] Appel draw_opponent_units à Y={enemy_units_y}")
            self.draw_opponent_units(screen, enemy_units_y)
        
        # Unités alliées (bas)
        logger.debug(f"[DEBUG] Vérification unités joueur: player={self.player}, units={getattr(self.player, 'units', None) if self.player else None}")
        if self.player and self.player.units:
            logger.debug(f"[DEBUG] Appel draw_player_units à Y={ally_units_y}")
            self.draw_player_units(screen, ally_units_y)
        
        # Dessiner les mains
        self.draw_hands(screen)


        
        # Dessiner l'interface d'information
        self.draw_info_panel(screen)
        
        # Dessiner les boutons normaux seulement si pas en mode mulligan
        if not self.mulligan_mode:
            for button in self.buttons:
                button.draw(screen)
        

        
        # Dessiner les tooltips
        self.draw_tooltips(screen)
        
        # Dessiner les logs si activés
        if hasattr(self, 'show_logs') and self.show_logs:
            self.draw_combat_logs(screen)
        
        # Dessiner les effets visuels
        self.draw_visual_effects(screen)
        
        # Dessiner l'overlay de ciblage
        self.draw_targeting_overlay(screen)
        
        # Dessiner les cooldowns des capacités
        self.draw_ability_cooldowns(screen)
        
        # Dessiner l'overlay de clic droit au premier plan
        self.draw_right_click_overlay(screen)
        
        # Dessiner le menu des capacités au premier plan
        if self.ability_menu is not None and self.ability_menu_rect is not None:
            screen.blit(self.ability_menu, self.ability_menu_rect)
        
        # Dessiner l'overlay de mulligan si actif
        if self.mulligan_mode:
            self.draw_mulligan_overlay(screen)
        
        # Dessiner le compte à rebours de début de combat
        if self.combat_start_countdown:
            self.draw_combat_countdown(screen)
    
        # Popup d'abandon de l'adversaire
        if self.surrender_popup_visible:
            self.draw_surrender_popup(screen)

    def show_surrender_popup(self):
        """Affiche la popup informant que l'adversaire a abandonné"""
        self.surrender_popup_visible = True
        # La position/rect sera calculée dans draw_surrender_popup

    def draw_surrender_popup(self, screen: pygame.Surface):
        """Dessine la popup d'abandon de l'adversaire avec un bouton OK"""
        popup_width = 560
        popup_height = 180
        popup_x = (SCREEN_WIDTH - popup_width) // 2
        popup_y = (SCREEN_HEIGHT - popup_height) // 2
        self.surrender_popup_rect = pygame.Rect(popup_x, popup_y, popup_width, popup_height)

        # Fond semi-transparent pour focus
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        screen.blit(overlay, (0, 0))

        # Cadre de la popup
        pygame.draw.rect(screen, COLORS['deep_black'], self.surrender_popup_rect, border_radius=10)
        pygame.draw.rect(screen, COLORS['light_gold'], self.surrender_popup_rect, width=2, border_radius=10)

        # Texte du message
        message = "Votre Adversaire a abandonné le Duel"
        title_surface = self.game_ui.font_medium.render(message, True, COLORS['white'])
        title_rect = title_surface.get_rect(center=(self.surrender_popup_rect.centerx, self.surrender_popup_rect.top + 60))
        screen.blit(title_surface, title_rect)

        # Bouton OK
        button_width, button_height = 120, 40
        ok_x = self.surrender_popup_rect.centerx - button_width // 2
        ok_y = self.surrender_popup_rect.bottom - 60
        self.surrender_ok_button = pygame.Rect(ok_x, ok_y, button_width, button_height)
        pygame.draw.rect(screen, COLORS['blue'], self.surrender_ok_button, border_radius=6)
        ok_text = self.game_ui.font_small.render("OK", True, COLORS['white'])
        ok_text_rect = ok_text.get_rect(center=self.surrender_ok_button.center)
        screen.blit(ok_text, ok_text_rect)
    
    def find_target_at_position(self, mouse_pos):
        """Trouve une cible à la position de la souris"""
        x, y = mouse_pos
        
        # Vérifier les unités du joueur
        if self.player and self.player.units:
            for unit in self.player.units:
                if hasattr(unit, 'rect') and unit.rect.collidepoint(x, y):
                    return unit
        
        # Vérifier les unités de l'adversaire
        if self.opponent and self.opponent.units:
            for unit in self.opponent.units:
                if hasattr(unit, 'rect') and unit.rect.collidepoint(x, y):
                    return unit
        
        # Vérifier le héros du joueur
        if self.player and self.player.hero:
            if hasattr(self.player_hero_rect, 'collidepoint') and self.player_hero_rect.collidepoint(x, y):
                return self.player.hero
        
        # Vérifier le héros de l'adversaire
        if self.opponent and self.opponent.hero:
            if hasattr(self.opponent_hero_rect, 'collidepoint') and self.opponent_hero_rect.collidepoint(x, y):
                return self.opponent.hero
        
        return None
    
    def show_unit_abilities(self, unit):
        """Affiche les capacités disponibles d'une unité"""

        print("=" * 50)
        print(f"[SHOW ABILITIES DEBUG] show_unit_abilities appelée pour: {unit.name if hasattr(unit, 'name') else 'Unité sans nom'}")
        print(f"[SHOW ABILITIES DEBUG] Unités du joueur: {len(self.player.units) if self.player and self.player.units else 0}")
        print(f"[SHOW ABILITIES DEBUG] Capacités de l'unité: {len(unit.abilities) if hasattr(unit, 'abilities') and unit.abilities else 0}")
        
        if hasattr(unit, 'abilities') and unit.abilities:
            for i, ability in enumerate(unit.abilities):
                print(f"[SHOW ABILITIES DEBUG] Capacité {i}: {ability.name} - cooldown: {getattr(ability, 'cooldown', 'N/A')}")
        
        print(f"[SHOW ABILITIES DEBUG] self.combat_engine: {self.combat_engine is not None}")
        if self.combat_engine:
            print(f"[SHOW ABILITIES DEBUG] current_player_index: {getattr(self.combat_engine, 'current_player_index', 'N/A')}")
        print("=" * 50)

        if not self.combat_engine or not hasattr(unit, 'abilities'):
            return
        
        # Afficher toutes les capacités, même celles en cooldown
        if unit.abilities:
            # Créer le menu des capacités avec toutes les capacités
            self.create_ability_menu(unit, unit.abilities)
        else:
            self.combat_log.append(f"Aucune capacité pour {unit.name}")
    
    def show_hero_abilities(self, hero):
        """Affiche les capacités disponibles d'un héros"""
        logger.debug(f"[DEBUG] show_hero_abilities appelé avec hero: {hero}")
        logger.debug(f"[DEBUG] self.combat_engine: {self.combat_engine}")
        
        if not self.combat_engine or not hero:
            logger.debug(f"[DEBUG] Retour anticipé - combat_engine: {self.combat_engine}, hero: {hero}")
            return
        
        # Afficher la capacité du héros, même si elle est en cooldown
        logger.debug(f"[DEBUG] Vérification des capacités du héros...")
        logger.debug(f"[DEBUG] hasattr(hero, 'ability'): {hasattr(hero, 'ability')}")
        
        if hasattr(hero, 'ability') and hero.ability:
            logger.debug(f"[DEBUG] hero.ability: {hero.ability}")
            logger.debug(f"[DEBUG] can_use_ability: {self.combat_engine.can_use_ability(hero, hero.ability)}")
            
            # Créer le menu des capacités avec la capacité du héros
            logger.debug(f"[DEBUG] Création du menu avec la capacité du héros")
            self.create_ability_menu(hero, [hero.ability])
        else:
            hero_name = hero.name if hasattr(hero, 'name') else "Héros"
            logger.debug(f"[DEBUG] Aucune capacité pour {hero_name}")
            self.combat_log.append(f"Aucune capacité pour {hero_name}")
    
    def create_ability_menu(self, entity, abilities):
        """Crée le menu flottant des capacités pour unités et héros"""
        # Fermer le menu existant s'il y en a un
        self.close_ability_menu()
        
        # Déterminer si c'est un héros ou une unité
        is_hero = False
        if self.player and self.player.hero and entity == self.player.hero:
            is_hero = True
            logger.debug(f"[DEBUG] Héros détecté: {self.player.hero.name if hasattr(self.player.hero, 'name') else 'Héros sans nom'}")
        else:
            logger.debug(f"[DEBUG] Entity n'est pas le héros du joueur")
            if not self.player:
                logger.debug(f"[DEBUG] self.player est None")
            elif not self.player.hero:
                logger.debug(f"[DEBUG] self.player.hero est None")
            else:
                logger.debug(f"[DEBUG] Entity != self.player.hero")
        
        if is_hero:
            # Position pour les héros (à droite du héros)
            if hasattr(self, 'player_hero_rect') and self.player_hero_rect:
                hero_rect = self.player_hero_rect
                unit_x = hero_rect.x
                unit_y = hero_rect.y
                unit_width = hero_rect.width
                unit_height = hero_rect.height
            else:
                # Fallback si le rect du héros n'est pas défini
                unit_x = self.battlefield_rect.centerx - 100
                unit_y = self.battlefield_rect.bottom - 150
                unit_width = 80
                unit_height = 120
        else:
            # Position pour les unités (au-dessus de l'unité)
            unit_width = 80
            unit_height = 120
            spacing = 20
            
            if entity in self.player.units:
                unit_index = self.player.units.index(entity)
                total_width = len(self.player.units) * unit_width + (len(self.player.units) - 1) * spacing
                start_x = self.battlefield_rect.centerx - total_width // 2
                y_pos = self.battlefield_rect.bottom - 80
                unit_x = start_x + unit_index * (unit_width + spacing)
                unit_y = y_pos
            else:
                # Fallback si l'unité n'est pas trouvée
                unit_x = self.battlefield_rect.centerx
                unit_y = self.battlefield_rect.centery
        
        # Créer le menu
        menu_width = 200
        menu_height = 30 * len(abilities) + 20
        
        if is_hero:
            # Pour les héros : menu à droite
            menu_x = unit_x + unit_width + 10
            menu_y = unit_y
        else:
            # Pour les unités : menu au-dessus
            menu_x = unit_x
            menu_y = unit_y - menu_height - 10
        
        # S'assurer que le menu ne sorte pas de l'écran
        if menu_x + menu_width > SCREEN_WIDTH:
            menu_x = unit_x - menu_width - 10
        if menu_y + menu_height > SCREEN_HEIGHT:
            menu_y = SCREEN_HEIGHT - menu_height - 10
        if menu_y < 0:
            menu_y = unit_y + unit_height + 10
        
        self.ability_menu_rect = pygame.Rect(menu_x, menu_y, menu_width, menu_height)
        self.ability_menu_unit = entity
        
        # Créer la surface du menu
        self.ability_menu = pygame.Surface((menu_width, menu_height))
        self.ability_menu.fill(COLORS['deep_black'])
        
        # Dessiner les capacités
        for i, ability in enumerate(abilities):
            ability_y = 10 + i * 30
            ability_rect = pygame.Rect(5, ability_y, menu_width - 10, 25)
            
            # Vérifier si la capacité peut être utilisée
            can_use = self.combat_engine.can_use_ability(entity, ability)
            
            # Fond de la capacité
            if can_use:
                pygame.draw.rect(self.ability_menu, COLORS['gray'], ability_rect, border_radius=3)
            else:
                # Fond semi-transparent rouge pour les capacités en cooldown
                overlay_surface = pygame.Surface((ability_rect.width, ability_rect.height))
                overlay_surface.set_alpha(102)  # 40% d'opacité (255 * 0.4 = 102)
                overlay_surface.fill(COLORS['ruby_red'])
                pygame.draw.rect(self.ability_menu, COLORS['gray'], ability_rect, border_radius=3)
                self.ability_menu.blit(overlay_surface, ability_rect)
            
            # Texte de la capacité
            text_color = COLORS['white'] if can_use else COLORS['dark_gray']
            ability_text = self.game_ui.font_small.render(ability.name, True, text_color)
            text_rect = ability_text.get_rect(center=ability_rect.center)
            self.ability_menu.blit(ability_text, text_rect)
            
            # Afficher le cooldown si la capacité n'est pas utilisable
            if not can_use:
                cooldown = self.combat_engine.get_ability_cooldown(entity, ability)
                if cooldown > 0:
                    cooldown_text = self.game_ui.font_small.render(f"CD: {cooldown}", True, COLORS['red'])
                    cooldown_rect = cooldown_text.get_rect()
                    cooldown_rect.right = ability_rect.right - 5
                    cooldown_rect.centery = ability_rect.centery
                    self.ability_menu.blit(cooldown_text, cooldown_rect)
    
    def close_ability_menu(self):
        """Ferme le menu des capacités"""
        self.ability_menu = None
        self.ability_menu_unit = None
        self.ability_menu_rect = None
    
    def handle_ability_menu_click(self, mouse_pos):
        """Gère les clics sur le menu des capacités"""
        logger.debug(f"[DEBUG] handle_ability_menu_click appelé avec mouse_pos: {mouse_pos}")
        
        if not self.ability_menu or not self.ability_menu_rect:
            logger.debug(f"[DEBUG] Menu non disponible - ability_menu: {self.ability_menu}, ability_menu_rect: {self.ability_menu_rect}")
            return False
        
        if not self.ability_menu_rect.collidepoint(mouse_pos):
            logger.debug(f"[DEBUG] Clic en dehors du menu - mouse_pos: {mouse_pos}, menu_rect: {self.ability_menu_rect}")
            return False
        
        logger.debug(f"[DEBUG] Clic détecté dans le menu")
        
        # Convertir la position de la souris en coordonnées relatives au menu
        rel_x = mouse_pos[0] - self.ability_menu_rect.left
        rel_y = mouse_pos[1] - self.ability_menu_rect.top
        logger.debug(f"[DEBUG] Position relative: rel_x={rel_x}, rel_y={rel_y}")
        
        # Déterminer si c'est un héros ou une unité
        is_hero = False
        if self.player and self.player.hero and self.ability_menu_unit == self.player.hero:
            is_hero = True
            logger.debug(f"[DEBUG] Menu héros détecté: {self.player.hero.name if hasattr(self.player.hero, 'name') else 'Héros sans nom'}")
        else:
            logger.debug(f"[DEBUG] Menu: Entity n'est pas le héros du joueur")
            if not self.player:
                logger.debug(f"[DEBUG] Menu: self.player est None")
            elif not self.player.hero:
                logger.debug(f"[DEBUG] Menu: self.player.hero est None")
            else:
                logger.debug(f"[DEBUG] Menu: Entity != self.player.hero")
        
        if is_hero:
            # Pour les héros : une seule capacité
            logger.debug(f"[DEBUG] Traitement héros - vérification des capacités")
            if (self.ability_menu_unit and hasattr(self.ability_menu_unit, 'ability') and 
                self.ability_menu_unit.ability and 
                self.combat_engine.can_use_ability(self.ability_menu_unit, self.ability_menu_unit.ability)):
                logger.debug(f"[DEBUG] Capacité héros valide, lancement du ciblage")
                logger.debug(f"[DEBUG] ability_menu_unit avant close: {self.ability_menu_unit}")
                logger.debug(f"[DEBUG] ability avant close: {self.ability_menu_unit.ability}")
                
                # Sauvegarder les références avant de fermer le menu
                hero_ability = self.ability_menu_unit.ability
                hero_unit = self.ability_menu_unit
                
                # Fermer le menu et lancer le ciblage
                self.close_ability_menu()
                
                logger.debug(f"[DEBUG] Références sauvegardées - hero_ability: {hero_ability}, hero_unit: {hero_unit}")
                self.start_ability_targeting(hero_ability, hero_unit)
                return True
            else:
                logger.debug(f"[DEBUG] Capacité héros invalide ou non utilisable")
        else:
            # Pour les unités : plusieurs capacités
            ability_index = (rel_y - 10) // 30
            logger.debug(f"[DEBUG] Index capacité calculé: {ability_index}")
            if 0 <= ability_index < len(self.ability_menu_unit.abilities):
                ability = self.ability_menu_unit.abilities[ability_index]
                logger.debug(f"[DEBUG] Capacité sélectionnée: {ability.name}")
                if self.combat_engine.can_use_ability(self.ability_menu_unit, ability):
                    logger.debug(f"[DEBUG] Capacité unité valide, lancement du ciblage")
                    logger.debug(f"[DEBUG] ability_menu_unit avant close: {self.ability_menu_unit}")
                    logger.debug(f"[DEBUG] ability avant close: {ability}")
                    
                    # Sauvegarder les références avant de fermer le menu
                    unit_ability = ability
                    unit_entity = self.ability_menu_unit
                    
                    # Fermer le menu et lancer le ciblage
                    self.close_ability_menu()
                    
                    logger.debug(f"[DEBUG] Références sauvegardées - unit_ability: {unit_ability}, unit_entity: {unit_entity}")
                    self.start_ability_targeting(unit_ability, unit_entity)
                    return True
                else:
                    logger.debug(f"[DEBUG] Capacité unité non utilisable")
            else:
                logger.debug(f"[DEBUG] Index capacité invalide: {ability_index}")
        
        logger.debug(f"[DEBUG] Aucune action effectuée")
        return False
    
    def draw_visual_effects(self, screen):
        """Dessine tous les effets visuels"""
        # Dessiner les nombres de dégâts
        for effect in self.damage_numbers:
            if hasattr(effect['target'], 'rect'):
                x = effect['target'].rect.centerx
                y = effect['target'].rect.centery + effect['y_offset']
                color = COLORS['red'] if effect['critical'] else COLORS['orange']
                text = self.game_ui.font_small.render(f"-{effect['amount']}", True, color)
                screen.blit(text, (x - text.get_width()//2, y - text.get_height()//2))
        
        # Dessiner les nombres de soins
        for effect in self.heal_numbers:
            if hasattr(effect['target'], 'rect'):
                x = effect['target'].rect.centerx
                y = effect['target'].rect.centery + effect['y_offset']
                text = self.game_ui.font_small.render(f"+{effect['amount']}", True, COLORS['green'])
                screen.blit(text, (x - text.get_width()//2, y - text.get_height()//2))
        
        # Dessiner les indicateurs d'effets
        for indicator in self.effect_indicators:
            if hasattr(indicator['target'], 'rect'):
                x = indicator['target'].rect.centerx
                y = indicator['target'].rect.top - 20
                
                # Créer une surface avec alpha
                effect_surface = pygame.Surface((100, 20))
                effect_surface.set_alpha(indicator['alpha'])
                effect_surface.fill(COLORS['blue'])
                
                # Texte de l'effet
                effect_text = self.game_ui.font_small.render(indicator['type'], True, COLORS['white'])
                effect_surface.blit(effect_text, (5, 2))
                
                screen.blit(effect_surface, (x - 50, y))
    
    def draw_targeting_overlay(self, screen):
        """Dessine l'overlay de ciblage"""
        if not self.targeting_mode and not self.ability_mode:
            return
        
        # Dessiner les cibles valides
        targets = []
        if self.targeting_mode and hasattr(self, 'valid_targets'):
            targets = self.valid_targets
        elif self.ability_mode and hasattr(self, 'ability_targets'):
            targets = self.ability_targets
        
        for target in targets:
            # Déterminer la position de la cible
            target_rect = None
            
            # Vérifier si c'est un héros
            if target == self.player.hero:
                # Ne pas afficher le héros du joueur s'il n'est pas activé
                if getattr(self.player.hero, 'is_active', False):
                    target_rect = self.player_hero_rect
            elif target == self.opponent.hero:
                # Ne pas afficher le héros adverse s'il n'est pas activé
                if getattr(self.opponent.hero, 'is_active', False):
                    target_rect = self.opponent_hero_rect
            # Vérifier si c'est une unité avec un attribut rect
            elif hasattr(target, 'rect'):
                target_rect = target.rect
            # Sinon, calculer la position basée sur l'index dans la liste
            else:
                # Calculer la position pour les unités du joueur
                if target in self.player.units:
                    unit_width = 80
                    unit_height = 120
                    spacing = 20
                    total_width = len(self.player.units) * unit_width + (len(self.player.units) - 1) * spacing
                    start_x = self.battlefield_rect.centerx - total_width // 2
                    y_pos = self.battlefield_rect.bottom - 80
                    unit_index = self.player.units.index(target)
                    x = start_x + unit_index * (unit_width + spacing)
                    target_rect = pygame.Rect(x, y_pos, unit_width, unit_height)
                # Calculer la position pour les unités de l'adversaire
                elif target in self.opponent.units:
                    unit_width = 80
                    unit_height = 120
                    spacing = 20
                    total_width = len(self.opponent.units) * unit_width + (len(self.opponent.units) - 1) * spacing
                    start_x = self.battlefield_rect.centerx - total_width // 2
                    y_pos = self.battlefield_rect.top + 20
                    unit_index = self.opponent.units.index(target)
                    x = start_x + unit_index * (unit_width + spacing)
                    target_rect = pygame.Rect(x, y_pos, unit_width, unit_height)
            
            if target_rect:
                # Surbrillance verte pour les cibles valides
                highlight_surface = pygame.Surface((target_rect.width + 10, target_rect.height + 10))
                highlight_surface.set_alpha(128)
                highlight_surface.fill(COLORS['green'])
                screen.blit(highlight_surface, (target_rect.x - 5, target_rect.y - 5))
                
                # Bordure verte
                pygame.draw.rect(screen, COLORS['green'], target_rect, 3)
    
    def draw_ability_cooldowns(self, screen):
        """Dessine les cooldowns des capacités"""
        if not self.combat_engine:
            return
        
        # Cooldowns des unités du joueur
        for i, unit in enumerate(self.player.units):
            logger.debug(f"[DEBUG] Traitement unité {i}: {unit.name}, HP={getattr(unit, 'hp', 'N/A')}")
            if unit.hp <= 0:
                logger.debug(f"[DEBUG] Unité {i} morte, on passe")
                continue  # Unité morte
            
            # Dessiner les cooldowns des capacités de l'unité (via moteur)
            if hasattr(unit, 'abilities'):
                for j, ability in enumerate(unit.abilities):
                    cooldown = 0
                    if hasattr(ability, 'ability_id') and self.combat_engine:
                        try:
                            cooldown = self.combat_engine.get_unit_ability_cooldown(unit, getattr(ability, 'ability_id'))
                        except Exception:
                            cooldown = 0
                    elif self.combat_engine:
                        try:
                            cooldown = self.combat_engine.get_ability_cooldown(unit, ability)
                        except Exception:
                            cooldown = 0
                    # Ne plus afficher le chiffre de cooldown en bas de la carte d'unité
                    # (Affichages ailleurs conservés: héros, overlays, etc.)
                    pass
        
        # Cooldown du héros du joueur
        if self.player and self.player.hero and self.player.hero.ability:
            hero = self.player.hero
            ability = hero.ability
            if hasattr(ability, 'current_cooldown') and ability.current_cooldown > 0:
                # Position pour afficher le cooldown du héros
                if hasattr(self, 'player_hero_rect') and self.player_hero_rect:
                    cooldown_x = self.player_hero_rect.x + 10
                    cooldown_y = self.player_hero_rect.y + self.player_hero_rect.height - 20
                    
                    # Afficher le cooldown
                    cooldown_text = str(ability.current_cooldown)
                    cooldown_surface = self.game_ui.font_small.render(cooldown_text, True, COLORS['red'])
                    screen.blit(cooldown_surface, (cooldown_x, cooldown_y))
                    logger.debug(f"[DEBUG] Cooldown du héros {hero.name}: {ability.current_cooldown}")
        
        # Cooldowns des unités de l'adversaire
        for i, unit in enumerate(self.opponent.units):
            if unit.hp <= 0:
                continue  # Unité morte
            
            # Dessiner les cooldowns des capacités de l'unité (via moteur)
            if hasattr(unit, 'abilities'):
                for j, ability in enumerate(unit.abilities):
                    cooldown = 0
                    if hasattr(ability, 'ability_id') and self.combat_engine:
                        try:
                            cooldown = self.combat_engine.get_unit_ability_cooldown(unit, getattr(ability, 'ability_id'))
                        except Exception:
                            cooldown = 0
                    elif self.combat_engine:
                        try:
                            cooldown = self.combat_engine.get_ability_cooldown(unit, ability)
                        except Exception:
                            cooldown = 0
                    # Ne plus afficher le chiffre de cooldown en bas de la carte d'unité
                    # (Affichages ailleurs conservés: héros, overlays, etc.)
                    pass
    
    def draw_player_units(self, screen, y_pos):
        """Dessine les unités du joueur (bas du bloc centré)"""
        logger.debug(f"[DEBUG] draw_player_units appelée avec y_pos={y_pos}")
        if not self.player or not self.player.units:
            logger.debug(f"[DEBUG] Pas d'unités joueur: player={self.player}, units={getattr(self.player, 'units', None) if self.player else None}")
            return
        logger.debug(f"[DEBUG] {len(self.player.units)} unités joueur à dessiner")
        
        # Dimensions comme dans le deck builder
        unit_width = 200
        unit_height = 288
        spacing = 20
        total_width = len(self.player.units) * unit_width + (len(self.player.units) - 1) * spacing
        start_x = SCREEN_WIDTH // 2 - total_width // 2  # Centré horizontalement
        
        for i, unit in enumerate(self.player.units):
            # Vérifier les HP de manière robuste
            unit_hp = getattr(unit, "hp", None)
            if unit_hp is None and hasattr(unit, "stats") and unit.stats:
                unit_hp = unit.stats.get("hp", 0)
            if unit_hp is None:
                unit_hp = 0
            if unit_hp <= 0:
                continue  # Unité morte
            
            x = start_x + i * (unit_width + spacing)
            unit_rect = pygame.Rect(x, y_pos, unit_width, unit_height)
            
            # Stocker le rect pour la détection de clic
            unit.rect = unit_rect
            
            # Créer l'overlay de l'unité comme dans le deck builder
            unit_overlay = self.create_unit_overlay_surface(unit)
            
            # Dessiner l'overlay
            screen.blit(unit_overlay, unit_rect)
            
            # Bordure verte pour les unités alliées
            pygame.draw.rect(screen, COLORS['green'], unit_rect, 3)
        

    
    def draw_opponent_units(self, screen, y_pos):
        """Dessine les unités de l'adversaire (haut du bloc centré)"""
        logger.debug(f"[DEBUG] draw_opponent_units appelée avec y_pos={y_pos}")
        if not self.opponent or not self.opponent.units:
            logger.debug(f"[DEBUG] Pas d'unités ennemies: opponent={self.opponent}, units={getattr(self.opponent, 'units', None) if self.opponent else None}")
            return
        logger.debug(f"[DEBUG] {len(self.opponent.units)} unités ennemies à dessiner")
        
        # Dimensions comme dans le deck builder
        unit_width = 200
        unit_height = 288
        spacing = 20
        total_width = len(self.opponent.units) * unit_width + (len(self.opponent.units) - 1) * spacing
        start_x = SCREEN_WIDTH // 2 - total_width // 2  # Centré horizontalement
        
        for i, unit in enumerate(self.opponent.units):
            logger.debug(f"[DEBUG] Traitement unité ennemie {i}: {unit.name}, HP={getattr(unit, 'hp', 'N/A')}")
            # Vérifier les HP de manière robuste
            unit_hp = getattr(unit, "hp", None)
            if unit_hp is None and hasattr(unit, "stats") and unit.stats:
                unit_hp = unit.stats.get("hp", 0)
            if unit_hp is None:
                unit_hp = 0
            if unit_hp <= 0:
                logger.debug(f"[DEBUG] Unité ennemie {i} morte, on passe")
                continue  # Unité morte
            
            x = start_x + i * (unit_width + spacing)
            unit_rect = pygame.Rect(x, y_pos, unit_width, unit_height)
            
            # Stocker le rect pour la détection de clic
            unit.rect = unit_rect
            
            # Créer l'overlay de l'unité comme dans le deck builder
            unit_overlay = self.create_unit_overlay_surface(unit)
            
            # Dessiner l'overlay
            screen.blit(unit_overlay, unit_rect)
            
            # Bordure rouge pour les unités ennemies
            pygame.draw.rect(screen, COLORS['red'], unit_rect, 3)
        

    
    def draw_hands(self, screen):
        """Dessine les mains des joueurs"""
        # Main du joueur (bas)
        self.draw_player_hand(screen)
        
        # Main de l'adversaire (haut, cartes face cachée)
        self.draw_opponent_hand(screen)
    
    def draw_player_hand(self, screen):
        """Dessine la main du joueur avec le même style que le deck builder"""
        if not self.player or not self.player.hand:
            return
        
        # Dessiner les cartes avec des dimensions adaptées au combat
        card_width = 120
        card_height = 180
        spacing = 10
        total_width = len(self.player.hand) * card_width + (len(self.player.hand) - 1) * spacing
        start_x = self.player_hand_rect.centerx - total_width // 2
        
        for i, card in enumerate(self.player.hand):
            x = start_x + i * (card_width + spacing)
            card_rect = pygame.Rect(x, self.player_hand_rect.centery - card_height // 2, card_width, card_height)
            
            # Stocker le rect pour la détection de clic
            card.rect = card_rect
            
            # Fond de la carte (même style que deck builder)
            pygame.draw.rect(screen, COLORS['dark_gray'], card_rect)
            
            # Bordure selon la sélection
            if self.mulligan_mode and i in self.mulligan_selected_cards:
                # Carte sélectionnée pour mulligan (bordure rouge)
                pygame.draw.rect(screen, COLORS['crimson'], card_rect, 4)
            elif card == self.selected_card:
                pygame.draw.rect(screen, COLORS['gold'], card_rect, 4)
            else:
                pygame.draw.rect(screen, COLORS['gold'], card_rect, 2)
            
            # Image de la carte
            card_image_path = getattr(card, 'image_path', 'Card/1.png')
            card_image = self.game_ui.asset_manager.get_image(card_image_path)
            if card_image:
                # Redimensionner l'image pour les cartes de combat (plus grande)
                scaled_image = pygame.transform.scale(card_image, (80, 120))
                image_rect = scaled_image.get_rect(center=(card_rect.centerx, card_rect.centery))
                screen.blit(scaled_image, image_rect)
            
            # Nom de la carte
            name_text = card.name[:12] if len(card.name) > 12 else card.name
            name_surface = self.game_ui.font_small.render(name_text, True, COLORS['white'])
            name_rect = name_surface.get_rect(center=(card_rect.centerx, card_rect.bottom - 15))
            screen.blit(name_surface, name_rect)
            
            # Coût de la carte
            cost_text = f"{getattr(card, 'cost', 0)}"
            cost_surface = self.game_ui.font_small.render(cost_text, True, COLORS['light_blue'])
            cost_rect = cost_surface.get_rect(center=(card_rect.centerx, card_rect.top + 20))
            screen.blit(cost_surface, cost_rect)
    
    def draw_opponent_hand(self, screen):
        """Dessine la main de l'adversaire (cartes face cachée)"""
        if not self.opponent or not self.opponent.hand:
            return
        
        # Dessiner les cartes face cachée
        card_width = 80
        card_height = 115
        spacing = 10
        total_width = len(self.opponent.hand) * card_width + (len(self.opponent.hand) - 1) * spacing
        start_x = self.opponent_hand_rect.centerx - total_width // 2
        
        for i in range(len(self.opponent.hand)):
            x = start_x + i * (card_width + spacing)
            card_rect = pygame.Rect(x, self.opponent_hand_rect.centery - card_height // 2, card_width, card_height)
            
            # Dos de carte
            pygame.draw.rect(screen, COLORS['deep_blue'], card_rect)
            pygame.draw.rect(screen, COLORS['white'], card_rect, 2)
            
            # Motif de dos de carte
            back_text = "CARTE"
            back_surface = self.game_ui.font_small.render(back_text, True, COLORS['white'])
            back_rect = back_surface.get_rect(center=card_rect.center)
            screen.blit(back_surface, back_rect)
    
    def draw_info_panel(self, screen):
        """Dessine le panneau d'information"""
        # Fond du panneau
        pygame.draw.rect(screen, COLORS['dark_gray'], self.info_rect)
        pygame.draw.rect(screen, COLORS['white'], self.info_rect, 2)
        
        if self.player:
            # Mana du joueur (sans décimales pour l'affichage)
            mana_display = int(self.player.mana)
            max_mana_display = int(self.player.max_mana)
            mana_text = f"Mana: {mana_display}/{max_mana_display}"
            mana_surface = self.game_ui.font_small.render(mana_text, True, COLORS['blue'])
            mana_rect = mana_surface.get_rect(center=(self.info_rect.centerx, self.info_rect.top + 15))
            screen.blit(mana_surface, mana_rect)
            
            # Tour actuel
            turn_text = f"Tour: {getattr(self.combat_engine, 'turn_count', 1)}"
            turn_surface = self.game_ui.font_small.render(turn_text, True, COLORS['white'])
            turn_rect = turn_surface.get_rect(center=(self.info_rect.centerx, self.info_rect.top + 35))
            screen.blit(turn_surface, turn_rect)
            
            # Phase actuelle
            phase_text = f"Phase: {self.current_phase.upper()}"
            phase_surface = self.game_ui.font_small.render(phase_text, True, COLORS['gold'])
            phase_rect = phase_surface.get_rect(center=(self.info_rect.centerx, self.info_rect.top + 55))
            screen.blit(phase_surface, phase_rect)
            
            # Indication du tour actuel (Joueur ou IA)
            if (self.combat_engine and 
                hasattr(self.combat_engine, 'current_player_index')):
                if self.combat_engine.current_player_index == 0:
                    turn_indicator_text = "TOUR DU JOUEUR"
                    turn_indicator_color = COLORS['green']
                else:
                    turn_indicator_text = "TOUR DE L'IA"
                    turn_indicator_color = COLORS['crimson']
                
                turn_indicator_surface = self.game_ui.font_small.render(turn_indicator_text, True, turn_indicator_color)
                turn_indicator_rect = turn_indicator_surface.get_rect(center=(self.info_rect.centerx, self.info_rect.top + 95))
                screen.blit(turn_indicator_surface, turn_indicator_rect)
            
            # Timer du tour
            remaining_time = self.get_remaining_time()
            timer_text = f"Temps: {remaining_time}s"
            
            # Changer la couleur du timer selon le temps restant
            if remaining_time <= 10:
                timer_color = COLORS['crimson']  # Rouge pour les 10 dernières secondes
            elif remaining_time <= 20:
                timer_color = COLORS['orange']   # Orange pour les 20 dernières secondes
            else:
                timer_color = COLORS['white']    # Blanc normal
            
            timer_surface = self.game_ui.font_small.render(timer_text, True, timer_color)
            timer_rect = timer_surface.get_rect(center=(self.info_rect.centerx, self.info_rect.top + 115))
            screen.blit(timer_surface, timer_rect)
            
            # Barre de progression du timer
            bar_width = 150
            bar_height = 8
            bar_x = self.info_rect.centerx - bar_width // 2
            bar_y = self.info_rect.top + 125
            
            # Fond de la barre
            pygame.draw.rect(screen, COLORS['dark_gray'], (bar_x, bar_y, bar_width, bar_height))
            pygame.draw.rect(screen, COLORS['white'], (bar_x, bar_y, bar_width, bar_height), 1)
            
            # Progression de la barre
            progress_ratio = remaining_time / self.turn_timer
            progress_width = int(bar_width * progress_ratio)
            
            if remaining_time <= 10:
                progress_color = COLORS['crimson']  # Rouge
            elif remaining_time <= 20:
                progress_color = COLORS['orange']   # Orange
            else:
                progress_color = COLORS['green']    # Vert
            
            pygame.draw.rect(screen, progress_color, (bar_x, bar_y, progress_width, bar_height))
            
            # Mode de ciblage
            if self.targeting_mode:
                targeting_text = f"CIBLAGE: {self.targeting_card.name}"
                targeting_surface = self.game_ui.font_small.render(targeting_text, True, COLORS['green'])
                targeting_rect = targeting_surface.get_rect(center=(self.info_rect.centerx, self.info_rect.top + 145))
                screen.blit(targeting_surface, targeting_rect)
            elif self.ability_mode:
                ability_text = f"CAPACITÉ: {self.selected_ability.name}"
                ability_surface = self.game_ui.font_small.render(ability_text, True, COLORS['blue'])
                ability_rect = ability_surface.get_rect(center=(self.info_rect.centerx, self.info_rect.top + 145))
                screen.blit(ability_surface, ability_rect)
    
    def draw_tooltips(self, screen):
        """Dessine les tooltips"""
        mouse_pos = pygame.mouse.get_pos()
        
        # Tooltips des boutons
        for button in self.buttons:
            button.update_hover(mouse_pos)
            if button.hover and button.tooltip:
                button.draw_tooltip(screen, mouse_pos)
        

    
    def draw_combat_logs(self, screen):
        """Dessine les logs de combat"""
        log_rect = pygame.Rect(20, 20, 400, 300)
        pygame.draw.rect(screen, COLORS['black'], log_rect)
        pygame.draw.rect(screen, COLORS['white'], log_rect, 2)
        
        # Titre des logs
        log_title = self.game_ui.font_medium.render("LOGS DE COMBAT", True, COLORS['white'])
        title_rect = log_title.get_rect(center=(log_rect.centerx, log_rect.top + 15))
        screen.blit(log_title, title_rect)
        
        # Afficher les derniers logs
        y_offset = 40
        for i, log_entry in enumerate(self.combat_log[-10:]):  # Derniers 10 logs
            if y_offset > log_rect.height - 20:
                break
            
            log_surface = self.game_ui.font_small.render(log_entry, True, COLORS['white'])
            log_rect_entry = log_surface.get_rect(topleft=(log_rect.left + 10, log_rect.top + y_offset))
            screen.blit(log_surface, log_rect_entry)
            y_offset += 20
    
    def handle_event(self, event):
        """Gère les événements de l'écran de combat"""
        # Sécurité: ignorer les interactions tant que le combat n'est pas initialisé
        if (self.combat_engine is None) or (self.player is None) or (self.opponent is None):
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.game_ui.change_screen("pre_combat")
            return
        
        # Si la popup d'abandon est visible, ne gérer que le bouton OK
        if self.surrender_popup_visible:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                if self.surrender_ok_button and self.surrender_ok_button.collidepoint(mouse_pos):
                    # Fermer la popup et retourner à l'écran de matchmaking
                    self.surrender_popup_visible = False
                    self.game_ui.change_screen("matchmaking")
            return

        # Bloquer toutes les actions pendant le compte à rebours de début de combat
        if getattr(self, 'combat_start_countdown', None):
            # Autoriser uniquement ESC pour revenir si besoin
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.game_ui.change_screen("pre_combat")
            return
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            
            # VÉRIFICATION DU TOUR : Empêcher le joueur de jouer si c'est le tour de l'IA
            if (self.combat_engine and 
                hasattr(self.combat_engine, 'current_player_index') and 
                self.combat_engine.current_player_index == 1 and 
                not self.mulligan_mode):
                # C'est le tour de l'IA, empêcher les actions du joueur
                # Mais permettre de fermer les overlays et menus
                if self.right_click_overlay is not None:
                    self.close_right_click_overlay()
                    return
                if self.ability_menu is not None:
                    self.close_ability_menu()
                    return
                # Permettre les clics sur les logs
                if hasattr(self, 'show_logs') and self.show_logs:
                    log_rect = pygame.Rect(SCREEN_WIDTH - 300, 50, 280, 200)
                    if log_rect.collidepoint(mouse_pos):
                        return
                # Permettre les clics sur le bouton abandon
                if hasattr(self, 'buttons'):
                    for button in self.buttons:
                        if button.rect.collidepoint(mouse_pos):
                            return
                # Bloquer tous les autres clics (cartes, unités, héros, fin de tour)
                return
            
            # Si un overlay de clic droit est affiché, le fermer avec n'importe quel clic
            if self.right_click_overlay is not None:
                self.close_right_click_overlay()
                return
            
            # Si le menu des capacités est affiché, vérifier les clics dessus
            if self.ability_menu is not None:
                logger.debug(f"[DEBUG] Menu des capacités détecté, vérification du clic")
                if self.handle_ability_menu_click(mouse_pos):
                    logger.debug(f"[DEBUG] Clic sur menu des capacités traité")
                    return
                else:
                    # Si pas de clic sur le menu, le fermer
                    logger.debug(f"[DEBUG] Fermeture du menu des capacités")
                    self.close_ability_menu()
                    return
            
            # Vérifier les clics sur les logs (toujours autorisés)
            if hasattr(self, 'show_logs') and self.show_logs:
                log_rect = pygame.Rect(SCREEN_WIDTH - 300, 50, 280, 200)
                if log_rect.collidepoint(mouse_pos):
                    # Permettre les clics sur les logs même en mode mulligan
                    return
            
            if event.button == 1:  # Clic gauche
                # Vérifier les clics sur les boutons de mulligan en premier
                if self.mulligan_mode:
                    # Vérifier les clics sur les nouveaux boutons simplifiés
                    if hasattr(self, 'mulligan_button_rect') and self.mulligan_button_rect.collidepoint(mouse_pos):
                        if len(self.mulligan_selected_cards) > 0:
                            self.confirm_mulligan()
                        return
                    
                    if hasattr(self, 'ready_button_rect') and self.ready_button_rect.collidepoint(mouse_pos):
                        self.set_player_ready()
                        return
                    
                    # Vérifier les clics sur les cartes de mulligan
                    if self.player and self.player.hand:
                        for i in range(min(5, len(self.player.hand))):
                            card = self.player.hand[i]
                            if hasattr(card, 'rect') and card.rect.collidepoint(mouse_pos):
                                self.toggle_card_mulligan_selection(i)
                                return
                    

                
                # Vérifier les clics sur les boutons normaux seulement si pas en mode mulligan
                if not self.mulligan_mode:
                    for i, button in enumerate(self.buttons):
                        if button.is_clicked(mouse_pos):
                            logger.debug(f"[DEBUG BOUTON] Clic détecté sur bouton {i}: '{button.text}' à la position {mouse_pos}")
                            logger.debug(f"[DEBUG BOUTON] Action du bouton: {button.action.__name__}")
                            button.action()
                            return
                

                
                # Gestion du ciblage
                if self.targeting_mode:
                    # Chercher une cible valide
                    target = self.find_target_at_position(mouse_pos)
                    if target:
                        self.select_target(target)
                        return
                    else:
                        # Clic ailleurs = annuler le ciblage
                        self.cancel_targeting()
                        return
                
                # Gestion du ciblage des capacités
                if self.ability_mode:
                    # Chercher une cible valide
                    target = self.find_target_at_position(mouse_pos)
                    if target:
                        self.use_ability_on_target(target)
                        return
                    else:
                        # Clic ailleurs = annuler le ciblage
                        self.cancel_ability_targeting()
                        return
                
                # Gestion normale des clics seulement si pas en mode mulligan
                if not self.mulligan_mode:
                    self.handle_card_click(mouse_pos)
                    self.handle_entity_click(mouse_pos)
            
            elif event.button == 3:  # Clic droit
                # Gérer le clic droit pour afficher l'overlay seulement si pas en mode mulligan
                if not self.mulligan_mode:
                    self.handle_right_click(mouse_pos)
        
        elif event.type == pygame.MOUSEMOTION:
            mouse_pos = pygame.mouse.get_pos()
            self.handle_hover(mouse_pos)
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                # Annuler le ciblage si actif
                if self.targeting_mode:
                    self.cancel_targeting()
                    return
                if self.ability_mode:
                    self.cancel_ability_targeting()
                    return
                
                # Fermer l'overlay de clic droit si ouvert
                if self.right_click_overlay is not None:
                    self.close_right_click_overlay()
                    return
                
                # Retour au menu principal
                self.game_ui.change_screen("main_menu")
        

    
    def handle_card_click(self, mouse_pos):
        """Gère les clics sur les cartes"""
        if not self.player or not self.player.hand:
            return
        
        # Vérifier si on clique sur une carte de la main (dimensions adaptées au combat)
        card_width = 120
        card_height = 180
        spacing = 10
        total_width = len(self.player.hand) * card_width + (len(self.player.hand) - 1) * spacing
        start_x = self.player_hand_rect.centerx - total_width // 2
        
        for i, card in enumerate(self.player.hand):
            x = start_x + i * (card_width + spacing)
            card_rect = pygame.Rect(x, self.player_hand_rect.centery - card_height // 2, card_width, card_height)
            
            if card_rect.collidepoint(mouse_pos):
                # En mode mulligan, sélectionner/désélectionner la carte
                if self.mulligan_mode:
                    self.toggle_card_mulligan_selection(i)
                    return
                
                # Vérifier si le joueur a assez de mana
                if self.player.mana >= card.cost:
                    # Obtenir les informations de ciblage
                    targeting_info = self.combat_engine.get_targeting_info(card, self.player)
                    
                    if targeting_info["requires_target"]:
                        # Démarrer le mode de ciblage
                        self.start_targeting(card)
                    else:
                        # Carte qui ne nécessite pas de ciblage (sort de zone, etc.)
                        try:
                            # Trouver l'index de la carte
                            card_index = self.player.hand.index(card)
                            
                            # Jouer la carte directement
                            success, message = self.combat_engine.play_card_with_target(card_index, None, self.player)
                            
                            if success:
                                print(f"[CARTE] {card.name} jouée avec succès")
                                self.combat_log.append(f"[CARTE] {card.name} jouée avec succès")
                                # Ajouter effet visuel
                                self.add_visual_effect("card_played", None)
                            else:
                                print(f"[ERREUR] Échec de l'utilisation de {card.name}: {message}")
                                self.combat_log.append(f"[ERREUR] {message}")
                                
                        except Exception as e:
                            print(f"[ERREUR] Erreur lors de l'utilisation de {card.name}: {e}")
                            self.combat_log.append(f"[ERREUR] Erreur lors de l'utilisation de {card.name}: {e}")
                else:
                    self.combat_log.append(f"Pas assez de mana pour jouer {card.name} (coût: {card.cost}, mana: {self.player.mana})")
                return
    
    def handle_entity_click(self, mouse_pos):
        """Gère les clics sur les unités et héros"""
        # Sécurité: si les entités ne sont pas prêtes, ignorer
        if not self.player or not getattr(self.player, 'units', None):
            return
        # DEBUG: Log des clics sur les unités
        print("=" * 50)
        print(f"[CLIC DEBUG] handle_entity_click appelé avec mouse_pos: {mouse_pos}")
        print(f"[CLIC DEBUG] self.player.units: {len(self.player.units) if self.player and self.player.units else 0} unités")

        # DEBUG: Log des rectangles des unités
        print("=" * 50)
        print(f"[RECT DEBUG] Vérification des rectangles des unités du joueur")
        
        if self.player and self.player.units:
            unit_width = 80
            unit_height = 120
            spacing = 20
            total_width = len(self.player.units) * unit_width + (len(self.player.units) - 1) * spacing
            start_x = self.battlefield_rect.centerx - total_width // 2
            y_pos = self.battlefield_rect.bottom - 80
            
            print(f"[RECT DEBUG] battlefield_rect.centerx: {self.battlefield_rect.centerx}")
            print(f"[RECT DEBUG] battlefield_rect.bottom: {self.battlefield_rect.bottom}")
            print(f"[RECT DEBUG] total_width: {total_width}")
            print(f"[RECT DEBUG] start_x: {start_x}")
            print(f"[RECT DEBUG] y_pos: {y_pos}")
            
            for i, unit in enumerate(self.player.units):
                if unit.hp <= 0:
                    continue
                
                x = start_x + i * (unit_width + spacing)
                unit_rect = pygame.Rect(x, y_pos, unit_width, unit_height)
                
                print(f"[RECT DEBUG] Unité {i}: {unit.name}")
                print(f"[RECT DEBUG]   Rectangle: x={x}, y={y_pos}, w={unit_width}, h={unit_height}")
                print(f"[RECT DEBUG]   Centre: ({x + unit_width//2}, {y_pos + unit_height//2})")
                print(f"[RECT DEBUG]   Clic dans rectangle: {unit_rect.collidepoint(mouse_pos)}")
        print("=" * 50)
        if self.player and self.player.units:
            for i, unit in enumerate(self.player.units):
                print(f"[CLIC DEBUG] Unité {i}: {unit.name if hasattr(unit, 'name') else 'Sans nom'} - HP: {unit.hp}")
        print("=" * 50)

        for i, unit in enumerate(self.player.units):
            print(f"[DEBUG] Unité {i}: {unit.name if hasattr(unit, 'name') else 'Sans nom'} - HP: {unit.hp}")

        for i, unit in enumerate(self.player.units):
            print(f"[DEBUG] Unité {i}: {unit.name if hasattr(unit, 'name') else 'Sans nom'} - HP: {unit.hp}")

        # Vérifier les clics sur les héros
        if self.player and self.player.hero and hasattr(self, 'player_hero_rect') and self.player_hero_rect:
            if self.player_hero_rect.collidepoint(mouse_pos):
                logger.debug(f"[DEBUG] Clic sur héros du joueur")
                logger.debug(f"[DEBUG] self.player.hero: {self.player.hero}")
                logger.debug(f"[DEBUG] is_active: {getattr(self.player.hero, 'is_active', False) if self.player.hero else 'N/A'}")
                
                # Le héros du joueur n'est ciblable que s'il est activé
                if getattr(self.player.hero, 'is_active', False):
                    if self.targeting_mode:
                        self.select_target(self.player.hero)
                    elif self.ability_mode:
                        self.use_ability_on_target(self.player.hero)
                    else:
                        # Mode normal : afficher le menu des capacités du héros
                        logger.debug(f"[DEBUG] Mode normal - vérification des capacités")
                        if (hasattr(self.player.hero, 'ability') and self.player.hero.ability and 
                            self.combat_engine.can_use_ability(self.player.hero, self.player.hero.ability)):
                            logger.debug(f"[DEBUG] Appel de show_hero_abilities")
                            self.show_hero_abilities(self.player.hero)
                        else:
                            logger.debug(f"[DEBUG] Capacité non disponible")
                            self.combat_log.append("La capacité du héros n'est pas disponible")
                else:
                    logger.debug(f"[DEBUG] Héros non activé")
                    self.combat_log.append("Le héros n'est pas encore activé")
                return
        
        if self.opponent and self.opponent.hero and hasattr(self, 'opponent_hero_rect') and self.opponent_hero_rect:
            if self.opponent_hero_rect.collidepoint(mouse_pos):
                # Le héros adverse n'est ciblable que s'il est activé
                if getattr(self.opponent.hero, 'is_active', False):
                    if self.targeting_mode:
                        self.select_target(self.opponent.hero)
                    elif self.ability_mode:
                        self.use_ability_on_target(self.opponent.hero)
                else:
                    self.combat_log.append("Le héros adverse n'est pas encore activé")
                return
        
        # Vérifier les clics sur les unités du joueur
        if self.player and self.player.units:
            logger.debug(f"[DEBUG] Vérification des clics sur {len(self.player.units)} unités du joueur")
            for unit in self.player.units:
                # Vérifier les HP de manière robuste
                unit_hp = getattr(unit, "hp", None)
                if unit_hp is None and hasattr(unit, "stats") and unit.stats:
                    unit_hp = unit.stats.get("hp", 0)
                if unit_hp is None:
                    unit_hp = 0
                if unit_hp <= 0:
                    logger.debug(f"[DEBUG] Unité {unit.name} morte, on passe")
                    continue  # Unité morte
                
                # Utiliser le rectangle stocké dans l'unité (créé dans draw_player_units)
                if hasattr(unit, 'rect') and unit.rect:
                    logger.debug(f"[DEBUG] Unité {unit.name} - Rectangle: {unit.rect}")
                    logger.debug(f"[DEBUG] Clic à {mouse_pos} - Dans rectangle: {unit.rect.collidepoint(mouse_pos)}")
                    if unit.rect.collidepoint(mouse_pos):
                        logger.debug(f"[DEBUG] Clic sur unité du joueur: {unit.name}")
                        
                        if self.targeting_mode:
                            self.select_target(unit)
                        elif self.ability_mode:
                            self.use_ability_on_target(unit)
                        else:
                            # Mode normal : afficher le menu des capacités de l'unité
                            logger.debug(f"[DEBUG] Mode normal - affichage des capacités de l'unité")
                            self.show_unit_abilities(unit)
                        return
                else:
                    logger.debug(f"[DEBUG] Unité {unit.name} - Pas de rectangle")
        
        # Vérifier les clics sur les unités de l'adversaire
        if self.opponent and self.opponent.units:
            for unit in self.opponent.units:
                # Vérifier les HP de manière robuste
                unit_hp = getattr(unit, "hp", None)
                if unit_hp is None and hasattr(unit, "stats") and unit.stats:
                    unit_hp = unit.stats.get("hp", 0)
                if unit_hp is None:
                    unit_hp = 0
                if unit_hp <= 0:
                    continue  # Unité morte
                
                # Utiliser le rectangle stocké dans l'unité (créé dans draw_opponent_units)
                if hasattr(unit, 'rect') and unit.rect:
                    if unit.rect.collidepoint(mouse_pos):
                        logger.debug(f"[DEBUG] Clic sur unité ennemie: {unit.name}")
                        
                        if self.targeting_mode:
                            self.select_target(unit)
                        elif self.ability_mode:
                            self.use_ability_on_target(unit)
                        else:
                            # Mode normal : pas de capacités pour les unités ennemies
                            logger.debug(f"[DEBUG] Clic sur unité ennemie (pas de capacités)")
                        return
    
    def handle_hover(self, mouse_pos):
        """Gère les survols de souris"""
        # Mise à jour des hover states pour les boutons
        for button in self.buttons:
            button.update_hover(mouse_pos)
    
    def handle_right_click(self, mouse_pos):
        """Gère les clics droits pour afficher l'overlay d'informations"""
        # Vérifier les clics sur les cartes
        if self.handle_right_click_cards(mouse_pos):
            return
        
        # Vérifier les clics sur les héros
        if self.handle_right_click_heroes(mouse_pos):
            return
        
        # Vérifier les clics sur les unités
        if self.handle_right_click_units(mouse_pos):
            return
    
    def handle_right_click_cards(self, mouse_pos):
        """Gère les clics droits sur les cartes"""
        if not self.player or not self.player.hand:
            return False
        
        # Vérifier si on clique sur une carte de la main (dimensions adaptées au combat)
        card_width = 120
        card_height = 180
        spacing = 10
        total_width = len(self.player.hand) * card_width + (len(self.player.hand) - 1) * spacing
        start_x = self.player_hand_rect.centerx - total_width // 2
        
        for i, card in enumerate(self.player.hand):
            x = start_x + i * (card_width + spacing)
            card_rect = pygame.Rect(x, self.player_hand_rect.centery - card_height // 2, card_width, card_height)
            
            if card_rect.collidepoint(mouse_pos):
                self.show_right_click_overlay(card, "card")
                return True
        
        return False
    
    def handle_right_click_heroes(self, mouse_pos):
        """Gère les clics droits sur les héros"""
        # Vérifier le héros du joueur
        if self.player and self.player.hero and hasattr(self, 'player_hero_rect') and self.player_hero_rect:
            if self.player_hero_rect.collidepoint(mouse_pos):
                self.show_right_click_overlay(self.player.hero, "hero")
                return True
        
        # Vérifier le héros de l'adversaire
        if self.opponent and self.opponent.hero and hasattr(self, 'opponent_hero_rect') and self.opponent_hero_rect:
            if self.opponent_hero_rect.collidepoint(mouse_pos):
                self.show_right_click_overlay(self.opponent.hero, "hero")
                return True
        
        return False
    
    def handle_right_click_units(self, mouse_pos):
        """Gère les clics droits sur les unités"""
        # Vérifier les unités du joueur
        if self.player and self.player.units:
            for unit in self.player.units:
                # Vérifier si l'unité est vivante
                if hasattr(unit, 'stats') and unit.stats.get('hp', 0) <= 0:
                    continue
                if hasattr(unit, 'hp') and unit.hp <= 0:
                    continue
                
                # Utiliser le rect stocké par draw_player_units
                if hasattr(unit, 'rect') and unit.rect.collidepoint(mouse_pos):
                    self.show_right_click_overlay(unit, "unit")
                    return True
        
        # Vérifier les unités de l'adversaire
        if self.opponent and self.opponent.units:
            for unit in self.opponent.units:
                # Vérifier si l'unité est vivante
                if hasattr(unit, 'stats') and unit.stats.get('hp', 0) <= 0:
                    continue
                if hasattr(unit, 'hp') and unit.hp <= 0:
                    continue
                
                # Utiliser le rect stocké par draw_opponent_units
                if hasattr(unit, 'rect') and unit.rect.collidepoint(mouse_pos):
                    self.show_right_click_overlay(unit, "unit")
                    return True
        
        return False
    
    def show_right_click_overlay(self, item, item_type):
        """Affiche l'overlay d'informations pour un élément"""
        # Couleurs de bordure selon le type
        border_colors = {
            'hero': COLORS['gold'],
            'unit': COLORS['royal_blue'],
            'card': COLORS['ruby_red']
        }
        border_color = border_colors.get(item_type, COLORS['white'])
        
        # Créer l'overlay selon le type d'élément
        if item_type == 'hero':
            self.right_click_overlay = self.create_hero_overlay_surface_high_res(item)
        elif item_type == 'unit':
            self.right_click_overlay = self.create_right_click_unit_overlay(item, border_color)
        elif item_type == 'card':
            self.right_click_overlay = self.create_right_click_card_overlay(item, border_color)
        
        self.right_click_overlay_type = item_type
        self.right_click_overlay_alpha = 255
    
    def update_right_click_overlay(self):
        """Met à jour l'overlay de clic droit"""
        if self.right_click_overlay is not None:
            # Animation d'apparition seulement
            if self.right_click_overlay_alpha < 255:
                self.right_click_overlay_alpha = min(255, self.right_click_overlay_alpha + 15)
    
    def draw_right_click_overlay(self, screen):
        """Dessine l'overlay de clic droit"""
        if self.right_click_overlay is not None and self.right_click_overlay_alpha > 0:
            # Fond semi-transparent noir à 80%
            overlay_bg = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay_bg.fill((0, 0, 0, 204))  # 204 = 80% de 255
            screen.blit(overlay_bg, (0, 0))
            
            # Appliquer l'alpha pour l'animation
            overlay_surface = self.right_click_overlay.copy()
            overlay_surface.set_alpha(self.right_click_overlay_alpha)
            
            # Positionner à 5 pixels de la bordure gauche, centré en hauteur
            overlay_rect = overlay_surface.get_rect(left=5, centery=SCREEN_HEIGHT // 2)
            screen.blit(overlay_surface, overlay_rect)
    
    def end_turn(self):
        """Termine le tour actuel manuellement"""
        if self.combat_engine:
            logger.debug("[TOUR] Fin de tour manuelle")
            logger.debug(f"[DEBUG TOUR] Tour actuel avant end_turn: {self.combat_engine.turn_count}")
            logger.debug(f"[DEBUG TOUR] Joueur actuel avant end_turn: {self.combat_engine.current_player_index}")
            self.combat_log.append("=== FIN DE TOUR MANUELLE ===")
            
            # === MODE RÉSEAU ===
            if self.network_mode:
                # En mode multijoueur, envoyer l'action de fin de tour au réseau
                self.send_network_action({
                    "type": "end_turn",
                    "player_id": 0  # Notre ID
                })
                print("[RÉSEAU] Action 'end_turn' envoyée")
            
            # Exécuter automatiquement toutes les phases du tour
            self.execute_complete_turn()
        else:
            logger.error("[DEBUG TOUR] ERREUR: combat_engine est None dans end_turn()")
    
    def activate_hero(self):
        """Active le héros du joueur"""
        if self.player and self.player.hero and not self.player.hero.is_active:
            # Vérifier le coût d'activation
            activation_cost = getattr(self.player.hero, 'activation_cost', 3)
            if self.player.mana >= activation_cost:
                self.player.mana -= activation_cost
                self.player.hero.is_active = True
                self.combat_log.append(f"Héros {self.player.hero.name} activé!")
            else:
                self.combat_log.append("Mana insuffisant pour activer le héros!")
    
    def surrender(self):
        """Abandonne la partie"""
        # Log l'abandon
        self.combat_log.append("=== PARTIE ABANDONNÉE ===")

        # Si en multijoueur, notifier le serveur et arrêter la synchronisation
        try:
            if getattr(self, 'network_mode', False) and hasattr(self, 'multiplayer_sync') and self.multiplayer_sync:
                result_payload = {
                    "reason": "surrender",
                    "by": getattr(self.multiplayer_sync, 'player_id', None),
                    "result": "forfeit"
                }
                # Tenter d'envoyer la fin de partie au serveur (best-effort)
                self.multiplayer_sync.end_game(result_payload)
                # Arrêter la synchronisation côté client quoi qu'il arrive
                self.multiplayer_sync.stop_sync()
                # En multi: retour matchmaking
                self.game_ui.change_screen("matchmaking")
                return
        except Exception as e:
            print(f"[MULTIPLAYER] Erreur lors de l'abandon: {e}")

        # Solo: retour à l'écran précédent si possible, sinon pre_combat
        if getattr(self.game_ui, 'previous_screen', None) and self.game_ui.previous_screen != "combat":
            self.game_ui.change_screen(self.game_ui.previous_screen)
        else:
            self.game_ui.change_screen("pre_combat")
    
    def toggle_logs(self):
        """Affiche/masque les logs de combat"""
        if not hasattr(self, 'show_logs'):
            self.show_logs = False
        self.show_logs = not self.show_logs
    
    # === MÉTHODES RÉSEAU ===
    
    def send_network_action(self, action):
        """Envoie une action au réseau (mode multijoueur)"""
        if self.network_mode:
            # Stocker l'action pour que SteamGameUI puisse la récupérer
            self.last_action = action
            print(f"[RÉSEAU] Action stockée: {action}")
    
    def receive_network_action(self, action):
        """Reçoit une action du réseau (mode multijoueur)"""
        if self.network_mode and self.combat_engine:
            action_type = action.get("type")
            
            if action_type == "end_turn":
                # L'adversaire a terminé son tour
                print("[RÉSEAU] Action 'end_turn' reçue de l'adversaire")
                self.combat_log.append("=== L'ADVERSAIRE A TERMINÉ SON TOUR ===")
                # Le moteur de jeu gère automatiquement le changement de tour
                
            elif action_type == "play_card":
                # L'adversaire a joué une carte
                card_index = action.get("card_index")
                target_info = action.get("target_info")
                print(f"[RÉSEAU] Action 'play_card' reçue: carte {card_index}, cible {target_info}")
                self.combat_log.append(f"=== L'ADVERSAIRE JOUE UNE CARTE ===")
                
            elif action_type == "use_ability":
                # L'adversaire a utilisé une capacité
                entity_id = action.get("entity_id")
                ability_index = action.get("ability_index")
                target_info = action.get("target_info")
                print(f"[RÉSEAU] Action 'use_ability' reçue: entité {entity_id}, capacité {ability_index}")
                self.combat_log.append(f"=== L'ADVERSAIRE UTILISE UNE CAPACITÉ ===")

    def close_right_click_overlay(self):
        """Ferme l'overlay de clic droit"""
        self.right_click_overlay = None
        self.right_click_overlay_type = None
        self.right_click_overlay_alpha = 0
        # Réinitialiser l'unité de l'overlay
        if hasattr(self, 'right_click_overlay_unit'):
            self.right_click_overlay_unit = None
    
    def start_mulligan(self):
        """Démarre le mode mulligan"""
        print(f"[DEBUG MULLIGAN] start_mulligan() appelé")
        print(f"[DEBUG MULLIGAN] self.player existe: {self.player is not None}")
        
        if not self.player:
            print(f"[DEBUG MULLIGAN] Pas de joueur, arrêt")
            return
        
        print(f"[DEBUG MULLIGAN] self.player.can_mulligan() existe: {hasattr(self.player, 'can_mulligan')}")
        if hasattr(self.player, 'can_mulligan'):
            can_mulligan = self.player.can_mulligan()
            print(f"[DEBUG MULLIGAN] can_mulligan() retourne: {can_mulligan}")
            if not can_mulligan:
                print(f"[DEBUG MULLIGAN] Le joueur ne peut pas mulliganer, arrêt")
                return
        else:
            print(f"[DEBUG MULLIGAN] Méthode can_mulligan() n'existe pas, arrêt")
            return
        
        self.mulligan_mode = True
        self.mulligan_selected_cards = []
        self.mulligan_completed = False
        self.mulligan_start_time = pygame.time.get_ticks()
        self.player_ready = False
        self.opponent_ready = False
        print(f"[MULLIGAN] Mode mulligan activé pour {self.player.name} - Timer: {self.mulligan_timer}s")
        
        # Ajouter aux logs de combat
        self.combat_log.append(f"[MULLIGAN] Mode mulligan activé pour {self.player.name}")
        self.combat_log.append(f"[MULLIGAN] Timer: {self.mulligan_timer} secondes")
        
        # Faire le mulligan de l'IA automatiquement
        self.perform_ai_mulligan()
    
    def perform_ai_mulligan(self):
        """Effectue le mulligan de l'IA automatiquement"""
        self.combat_log.append(f"[MULLIGAN IA] perform_ai_mulligan() appelé")
        self.combat_log.append(f"[MULLIGAN IA] opponent existe: {self.opponent is not None}")
        
        if not self.opponent:
            self.combat_log.append("[MULLIGAN IA] ERREUR: Pas d'opponent")
            self.opponent_ready = True
            return
        
        self.combat_log.append(f"[MULLIGAN IA] opponent.can_mulligan() existe: {hasattr(self.opponent, 'can_mulligan')}")
        if not self.opponent.can_mulligan():
            self.combat_log.append(f"[MULLIGAN IA] {self.opponent.name} ne peut pas mulliganer")
            self.opponent_ready = True
            return
        
        self.combat_log.append(f"[MULLIGAN IA] {self.opponent.name} peut mulliganer")
        self.combat_log.append(f"[MULLIGAN IA] Main de l'IA: {len(self.opponent.hand)} cartes")
        
        # L'IA va mulliganer les cartes coûtant 4+ mana (stratégie simple)
        cards_to_mulligan = []
        for i, card in enumerate(self.opponent.hand):
            if hasattr(card, 'cost') and card.cost >= 4:
                cards_to_mulligan.append(i)
                self.combat_log.append(f"[MULLIGAN IA] Carte {i} ({card.name}) coûte {card.cost}, sélectionnée")
        
        # Limiter à 2 cartes maximum pour l'IA
        if len(cards_to_mulligan) > 2:
            cards_to_mulligan = cards_to_mulligan[:2]
            self.combat_log.append(f"[MULLIGAN IA] Limité à 2 cartes maximum")
        
        if cards_to_mulligan:
            self.combat_log.append(f"[MULLIGAN IA] Tentative de mulligan de {len(cards_to_mulligan)} cartes")
            if self.opponent.perform_mulligan(cards_to_mulligan):
                self.combat_log.append(f"[MULLIGAN IA] {self.opponent.name} a mulligané {len(cards_to_mulligan)} cartes")
                print(f"[MULLIGAN IA] {self.opponent.name} a mulligané {len(cards_to_mulligan)} cartes")
            else:
                self.combat_log.append(f"[MULLIGAN IA] Échec du mulligan pour {self.opponent.name}")
        else:
            self.combat_log.append(f"[MULLIGAN IA] {self.opponent.name} n'a pas mulligané (aucune carte coûtant 4+ mana)")
            print(f"[MULLIGAN IA] {self.opponent.name} n'a pas mulligané")
        
        self.opponent_ready = True
        self.combat_log.append(f"[MULLIGAN IA] {self.opponent.name} marqué comme prêt")
    
    def check_mulligan_timer(self):
        """Vérifie si le timer de mulligan est écoulé"""
        if not self.mulligan_mode or not self.mulligan_start_time:
            return
        
        current_time = pygame.time.get_ticks()
        elapsed_seconds = (current_time - self.mulligan_start_time) // 1000
        
        if elapsed_seconds >= self.mulligan_timer:
            print(f"[MULLIGAN] Timer écoulé ({elapsed_seconds}s), fin automatique du mulligan")
            self.end_mulligan_phase()
    
    def get_mulligan_remaining_time(self):
        """Retourne le temps restant pour le mulligan en secondes"""
        if not self.mulligan_mode or not self.mulligan_start_time:
            return self.mulligan_timer
        
        current_time = pygame.time.get_ticks()
        elapsed_seconds = (current_time - self.mulligan_start_time) // 1000
        remaining = max(0, self.mulligan_timer - elapsed_seconds)
        return remaining
    
    def set_player_ready(self):
        """Marque le joueur comme prêt"""
        if not self.mulligan_mode:
            return
        
        self.player_ready = True
        print(f"[MULLIGAN] {self.player.name} est prêt")
        
        # Si les deux joueurs sont prêts, terminer la phase de mulligan
        if self.player_ready and self.opponent_ready:
            self.end_mulligan_phase()
    
    def end_mulligan_phase(self):
        """Termine la phase de mulligan avec fade-out"""
        print(f"[MULLIGAN] Phase de mulligan terminée")
        
        # Effet de fade-out
        self.mulligan_fade_out = True
        self.mulligan_fade_alpha = 204  # Commencer à 80%
        
        # Programmer la fin du fade-out et le lancement du compte à rebours
        import threading
        import time
        def complete_fade_out():
            time.sleep(0.5)  # Durée du fade-out
            self.mulligan_mode = False
            self.mulligan_completed = True
            self.mulligan_selected_cards = []
            self.mulligan_start_time = None
            self.mulligan_fade_out = False
            print(f"[MULLIGAN] Transition vers le combat terminée")
            
            # Lancer le compte à rebours de début de combat
            self.start_combat_countdown()
        
        threading.Thread(target=complete_fade_out, daemon=True).start()
    
    def start_combat_countdown(self):
        """Démarre le compte à rebours de 3 secondes avant le début du combat"""
        self.combat_start_countdown = True
        self.combat_start_start_time = pygame.time.get_ticks()
        print(f"[COMBAT] Compte à rebours de début de combat lancé")
    
    def check_combat_countdown(self):
        """Vérifie le compte à rebours de début de combat"""
        if not self.combat_start_countdown or not self.combat_start_start_time:
            return
        
        current_time = pygame.time.get_ticks()
        elapsed_seconds = (current_time - self.combat_start_start_time) // 1000
        
        if elapsed_seconds >= self.combat_start_timer:
            print(f"[COMBAT] Compte à rebours terminé, début du combat !")
            self.combat_start_countdown = False
            self.combat_start_start_time = None
            
            # Vérifier si c'est le tour de l'IA et démarrer le timer approprié
            if self.combat_engine.current_player_index == 1:
                print("[COMBAT] Tour de l'IA détecté après compte à rebours, démarrage du timer de timeout")
                self.start_ai_turn_timer()
            else:
                # Démarrer le timer du premier tour pour le joueur
                self.start_turn_timer()
    
    def get_combat_countdown_remaining(self):
        """Retourne le temps restant du compte à rebours"""
        if not self.combat_start_countdown or not self.combat_start_start_time:
            return 0
        
        current_time = pygame.time.get_ticks()
        elapsed_seconds = (current_time - self.combat_start_start_time) // 1000
        remaining = max(0, self.combat_start_timer - elapsed_seconds)
        return remaining
    
    def toggle_card_mulligan_selection(self, card_index):
        """Bascule la sélection d'une carte pour le mulligan"""
        if not self.mulligan_mode:
            return
        
        if card_index in self.mulligan_selected_cards:
            self.mulligan_selected_cards.remove(card_index)
            self.combat_log.append(f"[MULLIGAN] Carte {card_index} désélectionnée")
        else:
            self.mulligan_selected_cards.append(card_index)
            self.combat_log.append(f"[MULLIGAN] Carte {card_index} sélectionnée")
        
        print(f"[MULLIGAN] Cartes sélectionnées: {self.mulligan_selected_cards}")
        self.combat_log.append(f"[MULLIGAN] Cartes sélectionnées: {self.mulligan_selected_cards}")
    
    def confirm_mulligan(self):
        """Confirme le mulligan avec les cartes sélectionnées"""
        self.combat_log.append(f"[MULLIGAN] confirm_mulligan() appelé")
        self.combat_log.append(f"[MULLIGAN] mulligan_mode: {self.mulligan_mode}")
        self.combat_log.append(f"[MULLIGAN] cartes sélectionnées: {self.mulligan_selected_cards}")
        
        if not self.mulligan_mode or not self.player:
            self.combat_log.append("[MULLIGAN] ERREUR: Mode mulligan inactif ou pas de joueur")
            return
        
        self.combat_log.append("[MULLIGAN] Tentative de mulligan...")
        if self.player.perform_mulligan(self.mulligan_selected_cards):
            self.combat_log.append(f"[MULLIGAN] Mulligan confirmé")
            print(f"[MULLIGAN] Mulligan confirmé")
            self.set_player_ready()
        else:
            self.combat_log.append(f"[MULLIGAN] Échec du mulligan")
            print(f"[MULLIGAN] Échec du mulligan")
    
    def skip_mulligan(self):
        """Passe le mulligan"""
        if not self.mulligan_mode:
            return
        
        print(f"[MULLIGAN] Mulligan passé")
        self.set_player_ready()
    
    def draw_mulligan_overlay(self, screen):
        """Dessine l'overlay de mulligan avec interface dédiée"""
        # Gérer le fade-out
        if self.mulligan_fade_out:
            self.mulligan_fade_alpha = max(0, self.mulligan_fade_alpha - 10)  # Diminuer progressivement
        
        # Fond semi-transparent
        overlay_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay_surface.set_alpha(self.mulligan_fade_alpha)
        overlay_surface.fill(COLORS['black'])
        screen.blit(overlay_surface, (0, 0))
        
        # Si en fade-out, ne pas dessiner le contenu
        if self.mulligan_fade_out:
            return
        
        # Titre
        title_text = "MULLIGAN"
        title_surface = self.game_ui.font_medium.render(title_text, True, COLORS['white'])
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 100))
        screen.blit(title_surface, title_rect)
        
        # Timer de mulligan
        remaining_time = self.get_mulligan_remaining_time()
        timer_color = COLORS['crimson'] if remaining_time <= 3 else COLORS['white']
        timer_text = f"Temps restant: {remaining_time}s"
        timer_surface = self.game_ui.font_small.render(timer_text, True, timer_color)
        timer_rect = timer_surface.get_rect(center=(SCREEN_WIDTH // 2, 130))
        screen.blit(timer_surface, timer_rect)
        
        # Dessiner les 5 cartes en grand
        self.draw_mulligan_cards(screen)
        
        # Dessiner les boutons simplifiés
        self.draw_mulligan_buttons(screen)
        
        # État des joueurs en bas
        self.draw_mulligan_status(screen)
    
    def draw_mulligan_cards(self, screen):
        """Dessine les 5 cartes en grand pour le mulligan"""
        if not self.player or not self.player.hand:
            return
        
        # Dimensions des cartes en grand
        card_width = 200
        card_height = 288
        spacing = 20
        
        # Calculer la position de départ pour centrer les 5 cartes
        total_width = 5 * card_width + 4 * spacing
        start_x = (SCREEN_WIDTH - total_width) // 2
        center_y = SCREEN_HEIGHT // 2
        
        # Dessiner les 5 premières cartes
        for i in range(min(5, len(self.player.hand))):
            card = self.player.hand[i]
            x = start_x + i * (card_width + spacing)
            card_rect = pygame.Rect(x, center_y - card_height // 2, card_width, card_height)
            
            # Stocker le rect pour la détection de clic
            card.rect = card_rect
            
            # Fond de la carte
            pygame.draw.rect(screen, COLORS['dark_gray'], card_rect)
            
            # Bordure selon la sélection
            if i in self.mulligan_selected_cards:
                pygame.draw.rect(screen, COLORS['crimson'], card_rect, 4)
            else:
                pygame.draw.rect(screen, COLORS['gold'], card_rect, 2)
            
            # Image de la carte (redimensionnée pour les cartes en grand)
            card_image_path = getattr(card, 'image_path', 'Card/1.png')
            card_image = self.game_ui.asset_manager.get_image(card_image_path)
            if card_image:
                scaled_image = pygame.transform.scale(card_image, (140, 200))
                image_rect = scaled_image.get_rect(center=(card_rect.centerx, card_rect.centery - 20))
                screen.blit(scaled_image, image_rect)
            
            # Nom de la carte
            name_text = card.name[:15] if len(card.name) > 15 else card.name
            name_surface = self.game_ui.font_small.render(name_text, True, COLORS['white'])
            name_rect = name_surface.get_rect(center=(card_rect.centerx, card_rect.bottom - 30))
            screen.blit(name_surface, name_rect)
            
            # Coût de la carte
            cost_text = f"{getattr(card, 'cost', 0)}"
            cost_surface = self.game_ui.font_small.render(cost_text, True, COLORS['light_blue'])
            cost_rect = cost_surface.get_rect(center=(card_rect.centerx, card_rect.top + 25))
            screen.blit(cost_surface, cost_rect)
    
    def draw_mulligan_buttons(self, screen):
        """Dessine les boutons simplifiés pour le mulligan"""
        button_width = 150
        button_height = 50
        spacing = 10
        total_width = 2 * button_width + spacing
        start_x = (SCREEN_WIDTH - total_width) // 2
        button_y = SCREEN_HEIGHT // 2 + 200  # 50px sous les cartes
        
        # Bouton MULLIGAN
        mulligan_rect = pygame.Rect(start_x, button_y, button_width, button_height)
        mulligan_color = COLORS['orange'] if len(self.mulligan_selected_cards) > 0 else COLORS['gray']
        pygame.draw.rect(screen, mulligan_color, mulligan_rect)
        pygame.draw.rect(screen, COLORS['white'], mulligan_rect, 2)
        
        mulligan_text = self.game_ui.font_small.render("MULLIGAN", True, COLORS['white'])
        mulligan_text_rect = mulligan_text.get_rect(center=mulligan_rect.center)
        screen.blit(mulligan_text, mulligan_text_rect)
        
        # Stocker le rect pour la détection de clic
        self.mulligan_button_rect = mulligan_rect
        
        # Bouton PRÊT
        ready_rect = pygame.Rect(start_x + button_width + spacing, button_y, button_width, button_height)
        ready_color = COLORS['green'] if not self.player_ready else COLORS['blue']
        pygame.draw.rect(screen, ready_color, ready_rect)
        pygame.draw.rect(screen, COLORS['white'], ready_rect, 2)
        
        ready_text = self.game_ui.font_small.render("PRÊT", True, COLORS['white'])
        ready_text_rect = ready_text.get_rect(center=ready_rect.center)
        screen.blit(ready_text, ready_text_rect)
        
        # Stocker le rect pour la détection de clic
        self.ready_button_rect = ready_rect
    
    def draw_mulligan_status(self, screen):
        """Dessine le statut des joueurs en bas de l'écran"""
        # État des joueurs
        player_status = "PRÊT" if self.player_ready else "EN ATTENTE"
        opponent_status = "PRÊT" if self.opponent_ready else "EN ATTENTE"
        
        player_status_color = COLORS['green'] if self.player_ready else COLORS['orange']
        opponent_status_color = COLORS['green'] if self.opponent_ready else COLORS['orange']
        
        # Statut du joueur
        player_status_text = f"{self.player.name}: {player_status}"
        player_status_surface = self.game_ui.font_small.render(player_status_text, True, player_status_color)
        player_status_rect = player_status_surface.get_rect(center=(SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT - 50))
        screen.blit(player_status_surface, player_status_rect)
        
        # Statut de l'adversaire
        opponent_status_text = f"{self.opponent.name}: {opponent_status}"
        opponent_status_surface = self.game_ui.font_small.render(opponent_status_text, True, opponent_status_color)
        opponent_status_rect = opponent_status_surface.get_rect(center=(SCREEN_WIDTH // 2 + 200, SCREEN_HEIGHT - 50))
        screen.blit(opponent_status_surface, opponent_status_rect)
    
    def draw_combat_countdown(self, screen):
        """Dessine le compte à rebours de début de combat en grand"""
        # Fond semi-transparent
        overlay_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay_surface.set_alpha(180)
        overlay_surface.fill(COLORS['black'])
        screen.blit(overlay_surface, (0, 0))
        
        # Texte "COMBAT COMMENCE DANS"
        title_text = "COMBAT COMMENCE DANS"
        title_surface = self.game_ui.font_medium.render(title_text, True, COLORS['white'])
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
        screen.blit(title_surface, title_rect)
        
        # Nombre du compte à rebours (très grand)
        remaining = self.get_combat_countdown_remaining()
        countdown_text = str(remaining)
        
        # Police très grande pour le nombre
        countdown_font = pygame.font.Font(None, 200)  # Police de 200px
        countdown_surface = countdown_font.render(countdown_text, True, COLORS['crimson'])
        countdown_rect = countdown_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(countdown_surface, countdown_rect)
        
        # Animation de pulsation pour le dernier chiffre
        if remaining <= 1:
            # Effet de pulsation rouge
            pulse_alpha = abs(pygame.time.get_ticks() % 1000 - 500) / 500 * 255
            pulse_surface = pygame.Surface((countdown_rect.width + 20, countdown_rect.height + 20))
            pulse_surface.set_alpha(int(pulse_alpha))
            pulse_surface.fill(COLORS['crimson'])
            pulse_rect = pulse_surface.get_rect(center=countdown_rect.center)
            screen.blit(pulse_surface, pulse_rect)
        
        # Texte "SECONDES"
        seconds_text = "SECONDES"
        seconds_surface = self.game_ui.font_medium.render(seconds_text, True, COLORS['white'])
        seconds_rect = seconds_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))
        screen.blit(seconds_surface, seconds_rect)

    def get_cached_font(self, size):
        """Retourne une police mise en cache"""
        if size not in self._font_cache:
            self._font_cache[size] = pygame.font.Font(None, size)
        return self._font_cache[size]

    def draw_wrapped_text(self, surface, text, font, color, rect, line_spacing=5):
        """Dessine du texte avec retour à la ligne automatique"""
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            test_surface = font.render(test_line, True, color)
            
            if test_surface.get_width() <= rect.width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    lines.append(word)
        
        if current_line:
            lines.append(' '.join(current_line))
        
        y = rect.y
        for line in lines:
            if y + font.get_height() > rect.bottom:
                break
            text_surface = font.render(line, True, color)
            surface.blit(text_surface, (rect.x, y))
            y += font.get_height() + line_spacing

    def smart_wrap_text(self, text, font, max_width):
        """Retourne une liste de lignes de texte qui tiennent dans la largeur maximale"""
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            test_surface = font.render(test_line, True, (255, 255, 255))
            
            if test_surface.get_width() <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    lines.append(word)
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines

    def create_right_click_card_overlay(self, card, border_color):
        """Crée l'overlay de clic droit pour une carte"""
        # Format 80% de l'écran
        overlay_width = int(SCREEN_WIDTH * 0.8)
        overlay_height = int(SCREEN_HEIGHT * 0.8)
        overlay_surface = pygame.Surface((overlay_width, overlay_height), pygame.SRCALPHA)

        # Bordure colorée avec coins arrondis
        border_radius = 30
        pygame.draw.rect(overlay_surface, border_color, (0, 0, overlay_width, overlay_height), 4, border_radius=border_radius)

        # Layout : Image à gauche (40%), Texte à droite (60%)
        image_width = int(overlay_width * 0.4)
        text_width = int(overlay_width * 0.6)
        image_x = 0
        text_x = image_width + 20

        # Image de la carte - côté gauche avec bordure
        border_margin = 30
        image_inner_width = image_width - (border_margin * 2)
        image_inner_height = overlay_height - (border_margin * 2)
        
        # Image de la carte
        card_image_path = getattr(card, 'image_path', 'Card/1.png')
        card_image = self.game_ui.asset_manager.get_image(card_image_path)
        if card_image:
            # Redimensionner l'image pour l'overlay
            scaled_image = pygame.transform.scale(card_image, (image_inner_width, image_inner_height))
            
            # Créer une surface avec coins arrondis pour l'image
            image_surface = pygame.Surface((image_inner_width, image_inner_height), pygame.SRCALPHA)
            
            # Créer un masque avec coins arrondis précis
            mask_surface = self.create_rounded_mask(image_inner_width, image_inner_height, 30)
            
            # Appliquer le masque à l'image
            image_surface.blit(scaled_image, (0, 0))
            image_surface.blit(mask_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            
            overlay_surface.blit(image_surface, (border_margin, border_margin))
        else:
            # Image par défaut avec coins arrondis optimisée
            default_surface = self.apply_rounded_corners_to_image(
                pygame.Surface((image_inner_width, image_inner_height)).fill(COLORS['dark_gray']), 
                image_inner_width, image_inner_height, 30
            )
            overlay_surface.blit(default_surface, (border_margin, border_margin))

        # Zone texte - côté droit
        text_y = 40
        current_y = text_y

        # Nom complet de la carte
        full_name = card.name
        name_surface = self.get_cached_font(48).render(full_name, True, COLORS['white'])
        overlay_surface.blit(name_surface, (text_x, current_y))
        current_y += 80

        # Type de carte
        if hasattr(card, 'card_type'):
            card_type_text = card.card_type.replace('CARDTYPE.', '').title()
            card_type_surface = self.get_cached_font(28).render(card_type_text, True, COLORS['light_gold'])
            overlay_surface.blit(card_type_surface, (text_x, current_y))
            current_y += 50

        # Coût
        if hasattr(card, 'cost'):
            cost_text = f"Coût: {card.cost} mana"
            cost_surface = self.get_cached_font(32).render(cost_text, True, COLORS['light_blue'])
            overlay_surface.blit(cost_surface, (text_x, current_y))
            current_y += 50

        # Élément
        if hasattr(card, 'element'):
            element_text = f"Élément: {card.element}"
            element_surface = self.get_cached_font(28).render(element_text, True, COLORS['light_gold'])
            overlay_surface.blit(element_surface, (text_x, current_y))
            current_y += 50

        # Effet
        if hasattr(card, 'effect') and card.effect:
            effect_text = f"Effet: {card.effect}"
            effect_surface = self.get_cached_font(24).render(effect_text, True, COLORS['white'])
            overlay_surface.blit(effect_surface, (text_x, current_y))

        return overlay_surface

    def create_right_click_unit_overlay(self, unit, border_color):
        """Crée l'overlay de clic droit pour une unité avec le même format que le deck builder"""
        # Format 80% de l'écran comme le deck builder
        overlay_width = int(1920 * 0.8)  # 1536 pixels
        overlay_height = int(1080 * 0.8)  # 864 pixels
        overlay_surface = pygame.Surface((overlay_width, overlay_height), pygame.SRCALPHA)

        # Bordure colorée avec coins arrondis
        border_radius = 30
        pygame.draw.rect(overlay_surface, border_color, (0, 0, overlay_width, overlay_height), 4, border_radius=border_radius)

        # Layout : Image à gauche (40%), Texte à droite (60%) - comme le deck builder
        image_width = int(overlay_width * 0.4)  # 614 pixels
        text_width = int(overlay_width * 0.6)   # 922 pixels
        image_x = 0
        text_x = image_width + 20  # Espacement entre image et texte

        # Image de l'unité - côté gauche avec bordure
        if hasattr(unit, 'image_path') and unit.image_path:
            unit_image = self.game_ui.asset_manager.get_image(unit.image_path)
            if unit_image:
                # Image avec bordure intérieure
                border_margin = 30
                image_inner_width = image_width - (border_margin * 2)
                image_inner_height = overlay_height - (border_margin * 2)
                
                # Redimensionner l'image
                scaled_image = pygame.transform.scale(unit_image, (image_inner_width, image_inner_height))
                
                # Créer une surface avec coins arrondis pour l'image
                image_surface = pygame.Surface((image_inner_width, image_inner_height), pygame.SRCALPHA)
                
                # Créer un masque avec coins arrondis précis
                mask_surface = self.create_rounded_mask(image_inner_width, image_inner_height, 30)
                
                # Appliquer le masque à l'image
                image_surface.blit(scaled_image, (0, 0))
                image_surface.blit(mask_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                
                overlay_surface.blit(image_surface, (border_margin, border_margin))
            else:
                # Image par défaut avec coins arrondis
                default_surface = pygame.Surface((image_inner_width, image_inner_height), pygame.SRCALPHA)
                default_surface.fill(COLORS['dark_gray'])
                mask_surface = self.create_rounded_mask(image_inner_width, image_inner_height, 30)
                default_surface.blit(mask_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                overlay_surface.blit(default_surface, (border_margin, border_margin))

        # Zone texte - côté droit
        text_y = 40  # Marge supérieure
        current_y = text_y

        # Élément (symbole + texte) - comme le deck builder
        if hasattr(unit, 'element') and unit.element:
            element_mapping = {
                'feu': 'feu', 'eau': 'eau', 'glace': 'glace', 'terre': 'terre', 'air': 'air',
                'foudre': 'foudre', 'lumière': 'lumiere', 'ténèbres': 'tenebres', 'arcanique': 'arcane',
                'poison': 'poison', 'néant': 'neant'
            }
            element_name = unit.element.lower()
            file_name = element_mapping.get(element_name, element_name)
            element_symbol_path = f"Symbols/{file_name}.png"
            element_symbol = self.game_ui.asset_manager.get_image(element_symbol_path)
            if element_symbol:
                # Symbole + texte comme le deck builder
                symbol_size = (64, 64)
                scaled_symbol = pygame.transform.scale(element_symbol, symbol_size)
                symbol_rect = scaled_symbol.get_rect(topleft=(text_x, current_y))
                overlay_surface.blit(scaled_symbol, symbol_rect)
                
                # Texte de l'élément (sans "Élément:") comme le deck builder
                element_text = unit.element
                element_surface = self.get_cached_font(32).render(element_text, True, COLORS['light_gold'])
                overlay_surface.blit(element_surface, (text_x + 80, current_y + 20))
            else:
                # Texte seulement (sans "Élément:") comme le deck builder
                element_text = unit.element
                element_surface = self.get_cached_font(32).render(element_text, True, COLORS['light_gold'])
                overlay_surface.blit(element_surface, (text_x, current_y))
            
            current_y += 80

        # Nom complet de l'unité - comme le deck builder
        name_text = unit.name if hasattr(unit, 'name') else "Unité"
        name_surface = self.get_cached_font(48).render(name_text, True, COLORS['white'])
        overlay_surface.blit(name_surface, (text_x, current_y))
        current_y += 80

        # Capacités de l'unité
        if hasattr(unit, 'abilities') and unit.abilities:
            # Titre des capacités
            abilities_title = self.get_cached_font(32).render("Capacités:", True, COLORS['light_gold'])
            overlay_surface.blit(abilities_title, (text_x, current_y))
            current_y += 50
            
                        # Afficher chaque capacité
            for i, ability in enumerate(unit.abilities):
                ability_name = getattr(ability, 'name', f"Capacité {i+1}")
                ability_description = getattr(ability, 'description', "Aucune description")
                ability_cooldown = getattr(ability, 'cooldown', 0)
                ability_element = getattr(ability, 'element', "1")  # Récupérer l'élément de la capacité
                
                # Symbole d'élément de la capacité
                element_mapping = {
                    '1': 'feu', '2': 'eau', '3': 'terre', '4': 'air', '5': 'glace',
                    '6': 'foudre', '7': 'lumière', '8': 'ténèbres', '9': 'arcanique',
                    '10': 'poison', '11': 'néant', '12': 'néant'
                }
                element_name = element_mapping.get(str(ability_element), 'feu')
                element_symbol_path = f"Symbols/{element_name}.png"
                element_symbol = self.game_ui.asset_manager.get_image(element_symbol_path)
                
                # Position du symbole et du texte
                symbol_x = text_x
                text_start_x = text_x + 40  # Espace après le symbole
                
                if element_symbol:
                    # Afficher le symbole d'élément (32x32)
                    symbol_size = (32, 32)
                    scaled_symbol = pygame.transform.scale(element_symbol, symbol_size)
                    symbol_rect = scaled_symbol.get_rect(topleft=(symbol_x, current_y))
                    overlay_surface.blit(scaled_symbol, symbol_rect)
                
                # Nom de la capacité avec cooldown
                name_text = f"{ability_name} (Cooldown: {ability_cooldown})"
                name_surface = self.get_cached_font(28).render(name_text, True, COLORS['cyan'])
                # Centrer verticalement le texte par rapport au symbole (32px de hauteur)
                text_y = current_y + (32 - name_surface.get_height()) // 2
                overlay_surface.blit(name_surface, (text_start_x, text_y))
                current_y += 35
                
                # Description de la capacité
                wrapped_lines = self.smart_wrap_text(ability_description, self.get_cached_font(24), text_width - 40)
                for wrapped_line in wrapped_lines:
                    desc_surface = self.get_cached_font(24).render(wrapped_line, True, COLORS['white'])
                    overlay_surface.blit(desc_surface, (text_x, current_y))
                    current_y += 30
                
                current_y += 20  # Espace entre les capacités
            
            current_y += 20
        else:
            # Aucune capacité
            no_abilities_text = "Aucune capacité"
            no_abilities_surface = self.get_cached_font(28).render(no_abilities_text, True, COLORS['gray'])
            overlay_surface.blit(no_abilities_surface, (text_x, current_y))
            current_y += 60
        
        # Passifs de l'unité
        if hasattr(unit, 'passive_ids') and unit.passive_ids:
            # Titre des passifs
            passives_title = self.get_cached_font(32).render("Passifs:", True, COLORS['light_gold'])
            overlay_surface.blit(passives_title, (text_x, current_y))
            current_y += 50
            
            # Charger les données des passifs
            try:
                with open("Data/effects_database.json", 'r', encoding='utf-8') as f:
                    effects_data = json.load(f)
                passives_data = effects_data.get("passives", {})
            except:
                passives_data = {}
            
            # Afficher chaque passif
            for i, passive_id in enumerate(unit.passive_ids):
                if passive_id in passives_data:
                    passive = passives_data[passive_id]
                    passive_name = passive.get("name", f"Passif {i+1}")
                    passive_description = passive.get("description", "Aucune description")
                    
                    # Nom du passif
                    name_text = passive_name
                    name_surface = self.get_cached_font(28).render(name_text, True, COLORS['purple'])
                    overlay_surface.blit(name_surface, (text_x, current_y))
                    current_y += 35
                    
                    # Description du passif
                    wrapped_lines = self.smart_wrap_text(passive_description, self.get_cached_font(24), text_width - 40)
                    for wrapped_line in wrapped_lines:
                        desc_surface = self.get_cached_font(24).render(wrapped_line, True, COLORS['white'])
                        overlay_surface.blit(desc_surface, (text_x, current_y))
                        current_y += 30
                    
                    current_y += 20  # Espace entre les passifs
                else:
                    # Passif non trouvé
                    name_text = f"Passif {i+1} (ID: {passive_id})"
                    name_surface = self.get_cached_font(28).render(name_text, True, COLORS['red'])
                    overlay_surface.blit(name_surface, (text_x, current_y))
                    current_y += 35
                    
                    desc_text = "Passif non trouvé dans la base de données"
                    desc_surface = self.get_cached_font(24).render(desc_text, True, COLORS['gray'])
                    overlay_surface.blit(desc_surface, (text_x, current_y))
                    current_y += 50
            
            current_y += 20
        else:
            # Aucun passif
            no_passives_text = "Aucun passif"
            no_passives_surface = self.get_cached_font(28).render(no_passives_text, True, COLORS['gray'])
            overlay_surface.blit(no_passives_surface, (text_x, current_y))
            current_y += 60

        # Stats affichées une à une - comme le deck builder
        stats_y = current_y + 20
        if hasattr(unit, 'stats'):
            hp = unit.stats.get('hp', 0)
            max_hp = unit.stats.get('max_hp', hp)
            attack = unit.stats.get('attack', 0)
            defense = unit.stats.get('defense', 0)
            
            # HP
            hp_text = f"HP: {hp}/{max_hp}"
            hp_surface = self.get_cached_font(32).render(hp_text, True, COLORS['light_gold'])
            overlay_surface.blit(hp_surface, (text_x, stats_y))
            stats_y += 30

            # Attaque
            attack_text = f"Attaque: {attack}"
            attack_surface = self.get_cached_font(32).render(attack_text, True, COLORS['light_gold'])
            overlay_surface.blit(attack_surface, (text_x, stats_y))
            stats_y += 30

            # Défense
            defense_text = f"Défense: {defense}"
            defense_surface = self.get_cached_font(32).render(defense_text, True, COLORS['light_gold'])
            overlay_surface.blit(defense_surface, (text_x, stats_y))
            stats_y += 60
        else:
            # Fallback pour les anciennes unités
            hp = getattr(unit, 'hp', 0)
            max_hp = getattr(unit, 'max_hp', hp)
            attack = getattr(unit, 'attack', 0)
            defense = getattr(unit, 'defense', 0)
            
            # HP
            hp_text = f"HP: {hp}/{max_hp}"
            hp_surface = self.get_cached_font(32).render(hp_text, True, COLORS['light_gold'])
            overlay_surface.blit(hp_surface, (text_x, stats_y))
            stats_y += 30

            # Attaque
            attack_text = f"Attaque: {attack}"
            attack_surface = self.get_cached_font(32).render(attack_text, True, COLORS['light_gold'])
            overlay_surface.blit(attack_surface, (text_x, stats_y))
            stats_y += 30

            # Défense
            defense_text = f"Défense: {defense}"
            defense_surface = self.get_cached_font(32).render(defense_text, True, COLORS['light_gold'])
            overlay_surface.blit(defense_surface, (text_x, stats_y))
            stats_y += 60

        # Effets temporaires (ajout spécifique au combat)
        if hasattr(unit, 'temporary_effects') and unit.temporary_effects:
            stats_y += 20
            effects_title = self.get_cached_font(28).render("Effets temporaires:", True, COLORS['yellow'])
            overlay_surface.blit(effects_title, (text_x, stats_y))
            stats_y += 30
            
            for effect in unit.temporary_effects:
                # Support dict ou objet
                if isinstance(effect, dict):
                    e_type = effect.get('type', 'effet')
                    e_intensity = effect.get('value') or effect.get('amount') or effect.get('damage_per_turn') or ''
                    e_duration = effect.get('duration', '')
                else:
                    e_type = getattr(effect, 'effect_type', 'effet')
                    e_intensity = getattr(effect, 'intensity', '')
                    e_duration = getattr(effect, 'duration', '')
                effect_text = f"• {e_type}: {e_intensity} (durée: {e_duration})"
                effect_surface = self.get_cached_font(24).render(effect_text, True, COLORS['light_blue'])
                overlay_surface.blit(effect_surface, (text_x, stats_y))
                stats_y += 25

        return overlay_surface
    
    def create_hero_overlay_surface_combat(self, hero):
        """Crée une surface d'overlay compacte pour un héros en combat (format 200x288 comme les unités)"""
        overlay_width = 200  # Même largeur que les unités
        overlay_height = 288  # Même hauteur que les unités
        
        overlay_surface = pygame.Surface((overlay_width, overlay_height), pygame.SRCALPHA)

        # Bordure de la carte (couleur adaptée selon l'équipe)
        border_color = COLORS['crimson'] if hasattr(hero, 'is_enemy') and hero.is_enemy else COLORS['gold']
        pygame.draw.rect(overlay_surface, border_color, (0, 0, overlay_width, overlay_height), 2, border_radius=10)
        
        # Nom du héros - seulement avant la virgule, à 8% de la hauteur
        name_text = hero.name.split(',')[0].strip()  # Prendre seulement avant la virgule
        name_y = int(overlay_height * 0.08)  # 8% de la hauteur
        name_surface = self.get_cached_font(22).render(name_text, True, COLORS['white'])
        name_rect = name_surface.get_rect(centerx=overlay_width//2, y=name_y)
        
        # Fond pour le nom
        name_bg_rect = pygame.Rect(name_rect.x - 5, name_rect.y - 2, name_rect.width + 10, name_rect.height + 4)
        pygame.draw.rect(overlay_surface, (*COLORS['deep_black'], 200), name_bg_rect, border_radius=5)
        overlay_surface.blit(name_surface, name_rect)
        
        # Charger et afficher l'image du héros
        if hasattr(hero, 'image_path') and hero.image_path:
            hero_image = self.game_ui.asset_manager.get_image(hero.image_path)
            if hero_image:
                # Redimensionner l'image pour qu'elle remplisse toute la carte
                image_width = overlay_width  # 200 pixels - remplir toute la largeur
                image_height = overlay_height  # 288 pixels - remplir toute la hauteur
                scaled_image = pygame.transform.scale(hero_image, (image_width, image_height))
                
                # Créer une surface avec coins arrondis pour l'image
                image_surface = pygame.Surface((image_width, image_height), pygame.SRCALPHA)
                
                # Créer un masque avec coins arrondis précis
                mask_surface = self.create_rounded_mask(image_width, image_height, 10)
                
                # Appliquer le masque à l'image
                image_surface.blit(scaled_image, (0, 0))
                image_surface.blit(mask_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                
                # L'image remplit toute la carte avec coins arrondis
                image_x = 0
                image_y = 0
                overlay_surface.blit(image_surface, (image_x, image_y))
        
        # Élément avec symbole - dans le coin avec fond circulaire
        if hasattr(hero, 'element') and hero.element:
            element_mapping = {
                'feu': 'feu', 'eau': 'eau', 'glace': 'glace', 'terre': 'terre', 'air': 'air',
                'foudre': 'foudre', 'lumière': 'lumiere', 'ténèbres': 'tenebres', 'arcanique': 'arcane',
                'poison': 'poison', 'néant': 'neant'
            }
            
            element_name = hero.element.lower()
            file_name = element_mapping.get(element_name, element_name)
            element_symbol_path = f"Symbols/{file_name}.png"
            element_symbol = self.game_ui.asset_manager.get_image(element_symbol_path)
            
            if element_symbol:
                # Afficher le symbole d'élément dans le coin
                symbol_size = (24, 24)
                scaled_symbol = pygame.transform.scale(element_symbol, symbol_size)
                symbol_rect = scaled_symbol.get_rect(topleft=(10, 10))  # Coin supérieur gauche
                
                # Fond circulaire pour le symbole
                circle_radius = 15
                circle_center = (symbol_rect.centerx, symbol_rect.centery)
                pygame.draw.circle(overlay_surface, (*COLORS['deep_black'], 200), circle_center, circle_radius)
                overlay_surface.blit(scaled_symbol, symbol_rect)
            else:
                # Fallback vers le texte si le symbole n'est pas trouvé
                element_text = f"Élément: {hero.element}"
                element_surface = self.get_cached_font(12).render(element_text, True, COLORS['light_gold'])
                element_rect = element_surface.get_rect(topleft=(10, 10))
                
                # Fond circulaire pour le texte d'élément
                circle_radius = 15
                circle_center = (element_rect.centerx, element_rect.centery)
                pygame.draw.circle(overlay_surface, (*COLORS['deep_black'], 200), circle_center, circle_radius)
                overlay_surface.blit(element_surface, element_rect)
        
        # Rareté - tout en bas avec fond ovale coloré
        rarity_y = overlay_height - 30  # Tout en bas
        if hasattr(hero, 'rarity') and hero.rarity:
            rarity_text = hero.rarity
            rarity_surface = self.get_cached_font(11).render(rarity_text, True, COLORS['white'])
            rarity_rect = rarity_surface.get_rect(centerx=overlay_width//2, y=rarity_y)
            
            # Couleur de rareté
            rarity_colors = {
                'Commun': COLORS['gray'],
                'Peu Commun': COLORS['green'],
                'Rare': COLORS['royal_blue'],
                'Épique': COLORS['crimson'],
                'Héros': COLORS['orange'],
                'Mythique': COLORS['gold'],
                'Spécial': COLORS['cyan'],
                'commun': COLORS['gray'],
                'peu commun': COLORS['green'],
                'rare': COLORS['royal_blue'],
                'épique': COLORS['crimson'],
                'héros': COLORS['orange'],
                'mythique': COLORS['gold'],
                'spécial': COLORS['cyan'],
            }
            rarity_color = rarity_colors.get(rarity_text, COLORS['gray'])
            
            # Fond ovale pour la rareté
            oval_width = rarity_rect.width + 20
            oval_height = rarity_rect.height + 8
            oval_rect = pygame.Rect(rarity_rect.centerx - oval_width//2, rarity_rect.centery - oval_height//2, oval_width, oval_height)
            pygame.draw.ellipse(overlay_surface, (*rarity_color, 200), oval_rect)
            overlay_surface.blit(rarity_surface, rarity_rect)
        
        # Stats secondaires - au-dessus de la rareté avec 1% d'espace
        secondary_stats_y = rarity_y - 20 - int(overlay_height * 0.01)  # 1% d'espace
        secondary_stats = []
        if hasattr(hero, 'crit_pct'):
            secondary_stats.append(f"Crit: {hero.crit_pct}%")
        if hasattr(hero, 'esquive_pct'):
            secondary_stats.append(f"Esq: {hero.esquive_pct}%")
        if hasattr(hero, 'precision_pct'):
            secondary_stats.append(f"Préc: {hero.precision_pct}%")
        
        if secondary_stats:
            secondary_stats_text = " | ".join(secondary_stats)
            secondary_stats_surface = self.get_cached_font(12).render(secondary_stats_text, True, COLORS['light_blue'])
            secondary_stats_rect = secondary_stats_surface.get_rect(centerx=overlay_width//2, y=secondary_stats_y)
            
            # Fond pour les stats secondaires
            secondary_stats_bg_rect = pygame.Rect(secondary_stats_rect.x - 5, secondary_stats_rect.y - 2, secondary_stats_rect.width + 10, secondary_stats_rect.height + 4)
            pygame.draw.rect(overlay_surface, (*COLORS['deep_black'], 200), secondary_stats_bg_rect, border_radius=5)
            overlay_surface.blit(secondary_stats_surface, secondary_stats_rect)
        
        # Stats primaires - juste au-dessus des stats secondaires (fonds collés)
        primary_stats_y = secondary_stats_y - 20
        if hasattr(hero, 'base_stats'):
            hp = hero.base_stats.get('hp', 0)
            max_hp = hero.base_stats.get('max_hp', hp)
            attack = hero.base_stats.get('attack', 0)
            defense = hero.base_stats.get('defense', 0)
        else:
            # Fallback pour les anciens héros
            hp = getattr(hero, 'hp', 0)
            max_hp = getattr(hero, 'max_hp', hp)
            attack = getattr(hero, 'attack', 0)
            defense = getattr(hero, 'defense', 0)
        
        stats_text = f"HP: {hp} | ATK: {attack} | DEF: {defense}"
        stats_surface = self.get_cached_font(14).render(stats_text, True, COLORS['light_gold'])
        stats_rect = stats_surface.get_rect(centerx=overlay_width//2, y=primary_stats_y)
        
        # Fond pour les stats primaires (collé au fond des stats secondaires)
        stats_bg_rect = pygame.Rect(stats_rect.x - 5, stats_rect.y - 2, stats_rect.width + 10, stats_rect.height + 4)
        pygame.draw.rect(overlay_surface, (*COLORS['deep_black'], 200), stats_bg_rect, border_radius=5)
        overlay_surface.blit(stats_surface, stats_rect)
        
        # Capacité - à environ 40% de la hauteur depuis le bas, seulement le nom
        ability_y = overlay_height - int(overlay_height * 0.40)  # 40% depuis le bas
        if hasattr(hero, 'ability') and hero.ability:
            # Prendre seulement le nom de la capacité (avant le ":")
            ability_name = hero.ability.name.split(':')[0].strip()  # Prendre avant le ":"
            if len(ability_name) > 30:
                ability_name = ability_name[:27] + "..."
            
            # Récupérer le cooldown via le moteur de jeu
            if self.combat_engine:
                cooldown = self.combat_engine.get_ability_cooldown(hero, hero.ability)
            else:
                cooldown = getattr(hero.ability, 'current_cooldown', 0)
            
            # Déterminer la couleur (vert si cooldown = 0, sinon rouge)
            ability_color = COLORS['crimson'] if cooldown > 0 else (0, 255, 0)  # Vert si utilisable
            
            # Afficher le nom de la capacité
            ability_surface = self.get_cached_font(14).render(ability_name, True, ability_color)
            ability_rect = ability_surface.get_rect(centerx=overlay_width//2, y=ability_y)
            
            # Fond pour la capacité
            ability_bg_rect = pygame.Rect(ability_rect.x - 5, ability_rect.y - 2, ability_rect.width + 10, ability_rect.height + 4)
            pygame.draw.rect(overlay_surface, (*COLORS['deep_black'], 200), ability_bg_rect, border_radius=5)
            overlay_surface.blit(ability_surface, ability_rect)
            
            # Afficher le cooldown à côté du nom
            cooldown_text = str(cooldown)
            cooldown_surface = self.get_cached_font(14).render(cooldown_text, True, ability_color)
            cooldown_rect = cooldown_surface.get_rect(midleft=(ability_rect.right + 5, ability_rect.centery))
            
            # Fond pour le cooldown
            cooldown_bg_rect = pygame.Rect(cooldown_rect.x - 3, cooldown_rect.y - 2, cooldown_rect.width + 6, cooldown_rect.height + 4)
            pygame.draw.rect(overlay_surface, (*COLORS['deep_black'], 200), cooldown_bg_rect, border_radius=3)
            overlay_surface.blit(cooldown_surface, cooldown_rect)
        
        return overlay_surface

    def create_hero_overlay_surface_high_res(self, hero, border_color=None):
        """Crée l'overlay de clic droit pour un héros avec le même format que le deck builder"""
        # Format 80% de l'écran comme le deck builder
        overlay_width = int(1920 * 0.8)  # 1536 pixels
        overlay_height = int(1080 * 0.8)  # 864 pixels
        overlay_surface = pygame.Surface((overlay_width, overlay_height), pygame.SRCALPHA)

        # Bordure colorée avec coins arrondis
        border_radius = 30
        if border_color is None:
            border_color = COLORS['gold']  # Couleur dorée par défaut pour les héros
        pygame.draw.rect(overlay_surface, border_color, (0, 0, overlay_width, overlay_height), 4, border_radius=border_radius)

        # Layout : Image à gauche (40%), Texte à droite (60%) - comme le deck builder
        image_width = int(overlay_width * 0.4)  # 614 pixels
        text_width = int(overlay_width * 0.6)   # 922 pixels
        image_x = 0
        text_x = image_width + 20  # Espacement entre image et texte

        # Image du héros - côté gauche avec bordure
        if hasattr(hero, 'image_path') and hero.image_path:
            hero_image = self.game_ui.asset_manager.get_image(hero.image_path)
            if hero_image:
                # Image avec bordure intérieure
                border_margin = 30
                image_inner_width = image_width - (border_margin * 2)
                image_inner_height = overlay_height - (border_margin * 2)
                
                # Redimensionner l'image
                scaled_image = pygame.transform.scale(hero_image, (image_inner_width, image_inner_height))
                
                # Créer une surface avec coins arrondis pour l'image
                image_surface = pygame.Surface((image_inner_width, image_inner_height), pygame.SRCALPHA)
                
                # Créer un masque avec coins arrondis précis
                mask_surface = self.create_rounded_mask(image_inner_width, image_inner_height, 30)
                
                # Appliquer le masque à l'image
                image_surface.blit(scaled_image, (0, 0))
                image_surface.blit(mask_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                
                overlay_surface.blit(image_surface, (border_margin, border_margin))
            else:
                # Image par défaut avec coins arrondis
                default_surface = pygame.Surface((image_inner_width, image_inner_height), pygame.SRCALPHA)
                default_surface.fill(COLORS['dark_gray'])
                mask_surface = self.create_rounded_mask(image_inner_width, image_inner_height, 30)
                default_surface.blit(mask_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                overlay_surface.blit(default_surface, (border_margin, border_margin))

        # Zone texte - côté droit
        text_y = 40  # Marge supérieure
        current_y = text_y

        # Élément (symbole + texte) - comme le deck builder
        if hasattr(hero, 'element') and hero.element:
            element_mapping = {
                'feu': 'feu', 'eau': 'eau', 'glace': 'glace', 'terre': 'terre', 'air': 'air',
                'foudre': 'foudre', 'lumière': 'lumiere', 'ténèbres': 'tenebres', 'arcanique': 'arcane',
                'poison': 'poison', 'néant': 'neant'
            }
            element_name = hero.element.lower()
            file_name = element_mapping.get(element_name, element_name)
            element_symbol_path = f"Symbols/{file_name}.png"
            element_symbol = self.game_ui.asset_manager.get_image(element_symbol_path)
            if element_symbol:
                # Symbole + texte comme le deck builder
                symbol_size = (64, 64)
                scaled_symbol = pygame.transform.scale(element_symbol, symbol_size)
                symbol_rect = scaled_symbol.get_rect(topleft=(text_x, current_y))
                overlay_surface.blit(scaled_symbol, symbol_rect)
                
                # Texte de l'élément (sans "Élément:") comme le deck builder
                element_text = hero.element
                element_surface = self.get_cached_font(32).render(element_text, True, COLORS['light_gold'])
                overlay_surface.blit(element_surface, (text_x + 80, current_y + 20))
            else:
                # Texte seulement (sans "Élément:") comme le deck builder
                element_text = hero.element
                element_surface = self.get_cached_font(32).render(element_text, True, COLORS['light_gold'])
                overlay_surface.blit(element_surface, (text_x, current_y))
            
            current_y += 80

        # Nom complet du héros - comme le deck builder
        name_text = hero.name if hasattr(hero, 'name') else "Héros"
        name_surface = self.get_cached_font(48).render(name_text, True, COLORS['white'])
        overlay_surface.blit(name_surface, (text_x, current_y))
        current_y += 80

        # Capacité (nom sans "Capacité:")
        if hasattr(hero, 'ability_name') and hero.ability_name:
            ability_text = hero.ability_name
            ability_surface = self.get_cached_font(36).render(ability_text, True, COLORS['crimson'])
            overlay_surface.blit(ability_surface, (text_x, current_y))
            current_y += 30

        # Cooldown (déplacé sous le nom de capacité)
        if hasattr(hero, 'ability_cooldown') and hero.ability_cooldown:
            cooldown_text = f"Cooldown : {hero.ability_cooldown}"
            cooldown_surface = self.get_cached_font(28).render(cooldown_text, True, COLORS['crimson'])
            overlay_surface.blit(cooldown_surface, (text_x, current_y))
            current_y += 30

        # Description de la capacité (avec retour à la ligne intelligent)
        if hasattr(hero, 'ability_description') and hero.ability_description:
            desc_text = hero.ability_description
            # Retour à la ligne après chaque "."
            desc_lines = desc_text.split('.')
            for line in desc_lines:
                if line.strip():
                    line = line.strip() + '.'
                    # Wrapping intelligent
                    wrapped_lines = self.smart_wrap_text(line, self.get_cached_font(28), text_width - 40)
                    for wrapped_line in wrapped_lines:
                        desc_surface = self.get_cached_font(28).render(wrapped_line, True, COLORS['white'])
                        overlay_surface.blit(desc_surface, (text_x, current_y))
                        current_y += 40
            current_y += 60

        # Passif (si présent)
        if hasattr(hero, 'passive') and hero.passive:
            # Nettoyer le texte du passif en supprimant le coût entre parenthèses
            passive_text_raw = hero.passive
            # Supprimer tout ce qui est entre parenthèses à la fin
            if '(' in passive_text_raw:
                # Trouver la dernière parenthèse ouvrante
                last_open = passive_text_raw.rfind('(')
                if last_open != -1:
                    # Supprimer tout ce qui suit la dernière parenthèse ouvrante
                    passive_text_raw = passive_text_raw[:last_open].strip()
            
            passive_text = f"Passif: {passive_text_raw}"
            # Retour à la ligne après chaque "."
            passive_lines = passive_text.split('.')
            for line in passive_lines:
                if line.strip():
                    line = line.strip() + '.'
                    # Wrapping intelligent
                    wrapped_lines = self.smart_wrap_text(line, self.get_cached_font(28), text_width - 40)
                    for wrapped_line in wrapped_lines:
                        passive_surface = self.get_cached_font(28).render(wrapped_line, True, COLORS['light_gold'])
                        overlay_surface.blit(passive_surface, (text_x, current_y))
                        current_y += 40
            current_y += 60

        # Description générale (fallback si pas de capacité spécifique)
        if hasattr(hero, 'description') and hero.description and not hasattr(hero, 'ability_description'):
            # Nettoyer le texte de la description en supprimant le coût entre parenthèses
            desc_text_raw = hero.description
            if '(' in desc_text_raw:
                last_open = desc_text_raw.rfind('(')
                if last_open != -1:
                    desc_text_raw = desc_text_raw[:last_open].strip()
            
            # Wrapping intelligent après chaque "." comme le deck builder
            desc_lines = desc_text_raw.split('.')
            for line in desc_lines:
                if line.strip():
                    line = line.strip() + '.'
                    wrapped_lines = self.smart_wrap_text(line, self.get_cached_font(28), text_width - 40)
                    for wrapped_line in wrapped_lines:
                        desc_surface = self.get_cached_font(28).render(wrapped_line, True, COLORS['white'])
                        overlay_surface.blit(desc_surface, (text_x, current_y))
                        current_y += 40
            current_y += 60

        # Stats affichées une à une - comme le deck builder
        stats_y = current_y + 20
        if hasattr(hero, 'base_stats'):
            hp = hero.base_stats.get('hp', 0)
            max_hp = hero.base_stats.get('max_hp', hp)
            attack = hero.base_stats.get('attack', 0)
            defense = hero.base_stats.get('defense', 0)
            
            # HP
            hp_text = f"HP: {hp}/{max_hp}"
            hp_surface = self.get_cached_font(32).render(hp_text, True, COLORS['light_gold'])
            overlay_surface.blit(hp_surface, (text_x, stats_y))
            stats_y += 30

            # Attaque
            attack_text = f"Attaque: {attack}"
            attack_surface = self.get_cached_font(32).render(attack_text, True, COLORS['light_gold'])
            overlay_surface.blit(attack_surface, (text_x, stats_y))
            stats_y += 30

            # Défense
            defense_text = f"Défense: {defense}"
            defense_surface = self.get_cached_font(32).render(defense_text, True, COLORS['light_gold'])
            overlay_surface.blit(defense_surface, (text_x, stats_y))
            stats_y += 60
        else:
            # Fallback pour les anciens héros
            hp = getattr(hero, 'hp', 0)
            max_hp = getattr(hero, 'max_hp', hp)
            attack = getattr(hero, 'attack', 0)
            defense = getattr(hero, 'defense', 0)
            
            # HP
            hp_text = f"HP: {hp}/{max_hp}"
            hp_surface = self.get_cached_font(32).render(hp_text, True, COLORS['light_gold'])
            overlay_surface.blit(hp_surface, (text_x, stats_y))
            stats_y += 30

            # Attaque
            attack_text = f"Attaque: {attack}"
            attack_surface = self.get_cached_font(32).render(attack_text, True, COLORS['light_gold'])
            overlay_surface.blit(attack_surface, (text_x, stats_y))
            stats_y += 30

            # Défense
            defense_text = f"Défense: {defense}"
            defense_surface = self.get_cached_font(32).render(defense_text, True, COLORS['light_gold'])
            overlay_surface.blit(defense_surface, (text_x, stats_y))
            stats_y += 60

        # Stats secondaires
        if hasattr(hero, 'crit_pct') and hero.crit_pct:
            crit_text = f"Critique: {hero.crit_pct}%"
            crit_surface = self.get_cached_font(28).render(crit_text, True, COLORS['light_blue'])
            overlay_surface.blit(crit_surface, (text_x, stats_y))
            stats_y += 30

        if hasattr(hero, 'esquive_pct') and hero.esquive_pct:
            esquive_text = f"Esquive: {hero.esquive_pct}%"
            esquive_surface = self.get_cached_font(28).render(esquive_text, True, COLORS['light_blue'])
            overlay_surface.blit(esquive_surface, (text_x, stats_y))
            stats_y += 30

        if hasattr(hero, 'precision_pct') and hero.precision_pct:
            precision_text = f"Précision: {hero.precision_pct}%"
            precision_surface = self.get_cached_font(28).render(precision_text, True, COLORS['light_blue'])
            overlay_surface.blit(precision_surface, (text_x, stats_y))
            stats_y += 60

        # Rareté (sans "Rareté:")
        if hasattr(hero, 'rarity') and hero.rarity:
            rarity_text = hero.rarity
            rarity_surface = self.get_cached_font(28).render(rarity_text, True, COLORS['white'])
            overlay_surface.blit(rarity_surface, (text_x, stats_y))

        # Effets temporaires (ajout spécifique au combat)
        if hasattr(hero, 'temporary_effects') and hero.temporary_effects:
            stats_y += 20
            effects_title = self.get_cached_font(28).render("Effets temporaires:", True, COLORS['yellow'])
            overlay_surface.blit(effects_title, (text_x, stats_y))
            stats_y += 30
            
            for effect in hero.temporary_effects:
                # Support dict ou objet
                if isinstance(effect, dict):
                    e_type = effect.get('type', 'effet')
                    e_intensity = effect.get('value') or effect.get('amount') or effect.get('damage_per_turn') or ''
                    e_duration = effect.get('duration', '')
                else:
                    e_type = getattr(effect, 'effect_type', 'effet')
                    e_intensity = getattr(effect, 'intensity', '')
                    e_duration = getattr(effect, 'duration', '')
                effect_text = f"• {e_type}: {e_intensity} (durée: {e_duration})"
                effect_surface = self.get_cached_font(24).render(effect_text, True, COLORS['light_blue'])
                overlay_surface.blit(effect_surface, (text_x, stats_y))
                stats_y += 25

        return overlay_surface
    
    def create_unit_overlay_surface(self, unit):
        """Crée une surface d'overlay pour une unité en combat (même style que le deck builder)"""
        overlay_width = 200  # Même largeur que la carte
        overlay_height = 288  # Même hauteur que la carte
        
        overlay_surface = pygame.Surface((overlay_width, overlay_height), pygame.SRCALPHA)
        
        # Fond coloré de base pour s'assurer que l'unité est visible
        background_color = (100, 100, 150) if hasattr(unit, "is_enemy") and unit.is_enemy else (100, 150, 100)
        pygame.draw.rect(overlay_surface, background_color, (0, 0, overlay_width, overlay_height))
        

        # Définir desc_x pour les éléments qui en ont besoin
        desc_x = 20
        
        # Bordure de la carte (couleur adaptée selon l'équipe)
        border_color = COLORS['crimson'] if hasattr(unit, 'is_enemy') and unit.is_enemy else COLORS['royal_blue']
        pygame.draw.rect(overlay_surface, border_color, (0, 0, overlay_width, overlay_height), 2, border_radius=10)
        
        # Nom de l'unité - seulement avant la virgule, à 8% de la hauteur
        name_text = unit.name.split(',')[0].strip()  # Prendre seulement avant la virgule
        name_y = int(overlay_height * 0.08)  # 8% de la hauteur
        name_surface = self.get_cached_font(22).render(name_text, True, COLORS['white'])
        name_rect = name_surface.get_rect(centerx=overlay_width//2, y=name_y)
        
        # Fond pour le nom
        name_bg_rect = pygame.Rect(name_rect.x - 5, name_rect.y - 2, name_rect.width + 10, name_rect.height + 4)
        pygame.draw.rect(overlay_surface, (*COLORS['deep_black'], 200), name_bg_rect, border_radius=5)
        overlay_surface.blit(name_surface, name_rect)
        
        # Charger et afficher l'image de l'unité
        if hasattr(unit, 'image_path') and unit.image_path:
            # Utiliser directement le chemin de l'unité (AssetManager gère déjà les chemins)
            image_path = unit.image_path
            logger.debug(f"[DEBUG] Chargement image unité: {image_path}")
            unit_image = self.game_ui.asset_manager.get_image(image_path)
            if unit_image:
                logger.debug(f"[DEBUG] Image trouvée pour {unit.name}: {unit.image_path}")
                logger.debug(f"[DEBUG] Taille originale: {unit_image.get_size()}")
                # Redimensionner l'image pour qu'elle remplisse toute la carte (même taille que deck builder)
                image_width = overlay_width  # 200 pixels - remplir toute la largeur
                image_height = overlay_height  # 288 pixels - remplir toute la hauteur
                scaled_image = pygame.transform.scale(unit_image, (image_width, image_height))
                logger.debug(f"[DEBUG] Taille redimensionnée: {scaled_image.get_size()}")
                
                # Créer une surface avec coins arrondis pour l'image
                image_surface = pygame.Surface((image_width, image_height), pygame.SRCALPHA)
                
                # Créer un masque avec coins arrondis précis
                mask_surface = self.create_rounded_mask(image_width, image_height, 10)
                
                # Appliquer le masque à l'image
                image_surface.blit(scaled_image, (0, 0))
                image_surface.blit(mask_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                
                # L'image remplit toute la carte avec coins arrondis
                image_x = 0
                image_y = 0
                overlay_surface.blit(image_surface, (image_x, image_y))
                logger.debug(f"[DEBUG] Image dessinée sur overlay_surface avec coins arrondis")
            else:
                logger.debug(f"[DEBUG] Image NON trouvée pour {unit.name}: {unit.image_path}")
        else:
            logger.debug(f"[DEBUG] Pas d'image_path pour {unit.name}")
        
        # Élément avec symbole - dans le coin avec fond circulaire
        if hasattr(unit, 'element') and unit.element:
            # Mapping des noms d'éléments vers les noms de fichiers
            element_mapping = {
                'feu': 'feu',
                'eau': 'eau',
                'glace': 'glace',
                'terre': 'terre',
                'air': 'air',
                'foudre': 'foudre',
                'lumière': 'lumiere',
                'ténèbres': 'tenebres',
                'arcanique': 'arcane',
                'poison': 'poison',
                'néant': 'neant'
            }
            
            element_name = unit.element.lower()
            file_name = element_mapping.get(element_name, element_name)
            element_symbol_path = f"Symbols/{file_name}.png"
            element_symbol = self.game_ui.asset_manager.get_image(element_symbol_path)
            
            if element_symbol:
                # Afficher le symbole d'élément dans le coin
                symbol_size = (24, 24)
                scaled_symbol = pygame.transform.scale(element_symbol, symbol_size)
                symbol_rect = scaled_symbol.get_rect(topleft=(10, 10))  # Coin supérieur gauche
                
                # Fond circulaire pour le symbole
                circle_radius = 15
                circle_center = (symbol_rect.centerx, symbol_rect.centery)
                pygame.draw.circle(overlay_surface, (*COLORS['deep_black'], 200), circle_center, circle_radius)
                overlay_surface.blit(scaled_symbol, symbol_rect)
            else:
                # Fallback vers le texte si le symbole n'est pas trouvé
                element_text = f"Élément: {unit.element}"
                element_surface = self.get_cached_font(12).render(element_text, True, COLORS['light_gold'])
                element_rect = element_surface.get_rect(topleft=(10, 10))
                
                # Fond circulaire pour le texte d'élément
                circle_radius = 15
                circle_center = (element_rect.centerx, element_rect.centery)
                pygame.draw.circle(overlay_surface, (*COLORS['deep_black'], 200), circle_center, circle_radius)
                overlay_surface.blit(element_surface, element_rect)
        
        # Indicateur de bouclier - centré au-dessus des stats principales
        if hasattr(unit, 'temporary_effects') and unit.temporary_effects:
            shield_effects = [e for e in unit.temporary_effects if (isinstance(e, dict) and e.get("type") == "shield") or getattr(e, 'effect_type', None) == "shield"]
            if shield_effects:
                def _shield_value(e):
                    if isinstance(e, dict):
                        return e.get('amount') or e.get('value') or e.get('damage_per_turn') or 0
                    return getattr(e, 'intensity', 0)
                total_shield = sum(_shield_value(e) for e in shield_effects)
                shield_text = f"Bouclier : {total_shield}"
                shield_surface = self.get_cached_font(14).render(shield_text, True, COLORS['white'])
                shield_rect = shield_surface.get_rect(centerx=overlay_width//2, y=200)
                
                # Fond pour le bouclier
                shield_bg_rect = pygame.Rect(shield_rect.x - 8, shield_rect.y - 3, shield_rect.width + 16, shield_rect.height + 6)
                pygame.draw.rect(overlay_surface, (*COLORS['deep_black'], 200), shield_bg_rect, border_radius=5)
                overlay_surface.blit(shield_surface, shield_rect)
        
        # Rareté - tout en bas avec fond ovale coloré
        rarity_y = overlay_height - 30  # Tout en bas
        if hasattr(unit, 'rarity') and unit.rarity:
            rarity_text = unit.rarity
            rarity_surface = self.get_cached_font(11).render(rarity_text, True, COLORS['white'])
            rarity_rect = rarity_surface.get_rect(centerx=overlay_width//2, y=rarity_y)
            
            # Couleur de rareté
            rarity_colors = {
                'Commun': COLORS['gray'],
                'Peu Commun': COLORS['green'],
                'Rare': COLORS['royal_blue'],
                'Épique': COLORS['crimson'],
                'Héros': COLORS['orange'],
                'Mythique': COLORS['gold'],
                'Spécial': COLORS['cyan'],
                'commun': COLORS['gray'],
                'peu commun': COLORS['green'],
                'rare': COLORS['royal_blue'],
                'épique': COLORS['crimson'],
                'héros': COLORS['orange'],
                'mythique': COLORS['gold'],
                'spécial': COLORS['cyan'],
            }
            rarity_color = rarity_colors.get(rarity_text, COLORS['gray'])
            
            # Fond ovale pour la rareté
            oval_width = rarity_rect.width + 20
            oval_height = rarity_rect.height + 8
            oval_rect = pygame.Rect(rarity_rect.centerx - oval_width//2, rarity_rect.centery - oval_height//2, oval_width, oval_height)
            pygame.draw.ellipse(overlay_surface, (*rarity_color, 200), oval_rect)
            overlay_surface.blit(rarity_surface, rarity_rect)
        
        # Stats secondaires - au-dessus de la rareté avec 1% d'espace
        secondary_stats_y = rarity_y - 20 - int(overlay_height * 0.01)  # 1% d'espace
        
        # Calculer les stats finales avec les effets temporaires
        base_crit = getattr(unit, 'crit_pct', 0)
        base_esquive = getattr(unit, 'esquive_pct', 0)
        base_precision = getattr(unit, 'precision_pct', 0)
        
        final_crit = base_crit
        final_esquive = base_esquive
        final_precision = base_precision
        
        # Debug: afficher les stats de base
        print(f"[DEBUG] {unit.name} - Stats de base: Crit={base_crit}%, Esq={base_esquive}%")
        
        # Appliquer les effets temporaires
        if hasattr(unit, 'temporary_effects') and unit.temporary_effects:
            print(f"[DEBUG] {unit.name} - {len(unit.temporary_effects)} effets temporaires trouvés")
            for effect in unit.temporary_effects:
                if isinstance(effect, dict) and effect.get('duration', 0) > 0:
                    effect_type = effect.get('type', '')
                    effect_value = effect.get('value', 0)
                    
                    print(f"[DEBUG] {unit.name} - Effet: {effect_type} = {effect_value}")
                    
                    if effect_type == 'crit_boost':
                        # Le crit_boost est déjà en pourcentage (0.2 = 20%)
                        boost_amount = int(effect_value * 100)
                        final_crit += boost_amount
                        print(f"[DEBUG] {unit.name} - Crit boosté: {base_crit}% + {boost_amount}% = {final_crit}%")
                    elif effect_type == 'dodge_boost':
                        # Le dodge_boost est déjà en pourcentage (0.1 = 10%)
                        boost_amount = int(effect_value * 100)
                        final_esquive += boost_amount
                        print(f"[DEBUG] {unit.name} - Esq boostée: {base_esquive}% + {boost_amount}% = {final_esquive}%")
        else:
            print(f"[DEBUG] {unit.name} - Aucun effet temporaire")
        
        print(f"[DEBUG] {unit.name} - Stats finales: Crit={final_crit}%, Esq={final_esquive}%")
        
        # Construire le texte des stats secondaires avec indication des boosts
        secondary_stats = []
        if hasattr(unit, 'crit_pct'):
            if final_crit > base_crit:
                secondary_stats.append(f"Crit: {final_crit}%")
            else:
                secondary_stats.append(f"Crit: {final_crit}%")
        if hasattr(unit, 'esquive_pct'):
            if final_esquive > base_esquive:
                secondary_stats.append(f"Esq: {final_esquive}%")
            else:
                secondary_stats.append(f"Esq: {final_esquive}%")
        if hasattr(unit, 'precision_pct'):
            secondary_stats.append(f"Préc: {final_precision}%")
        
        if secondary_stats:
            secondary_stats_text = " | ".join(secondary_stats)
            # Couleur verte si des stats sont boostées
            secondary_color = COLORS['green'] if (final_crit > base_crit or final_esquive > base_esquive) else COLORS['light_blue']
            secondary_stats_surface = self.get_cached_font(12).render(secondary_stats_text, True, secondary_color)
            secondary_stats_rect = secondary_stats_surface.get_rect(centerx=overlay_width//2, y=secondary_stats_y)
            
            # Fond pour les stats secondaires
            secondary_stats_bg_rect = pygame.Rect(secondary_stats_rect.x - 5, secondary_stats_rect.y - 2, secondary_stats_rect.width + 10, secondary_stats_rect.height + 4)
            pygame.draw.rect(overlay_surface, (*COLORS['deep_black'], 200), secondary_stats_bg_rect, border_radius=5)
            overlay_surface.blit(secondary_stats_surface, secondary_stats_rect)
        
        # Position des stats primaires
        primary_stats_y = secondary_stats_y - 20
        
        # Stats primaires - juste au-dessus des stats secondaires (fonds collés)
        logger.debug(f"[DEBUG] Stats unité {unit.name}: HP={unit.hp}, ATK={unit.attack}, DEF={unit.defense}")
        logger.debug(f"[DEBUG] Stats unité {unit.name} (base_stats): {getattr(unit, 'base_stats', 'N/A')}")
        logger.debug(f"[DEBUG] Stats unité {unit.name} (stats): {getattr(unit, 'stats', 'N/A')}")
        
        # Utiliser les stats actuelles de l'unité (qui incluent les effets temporaires)
        current_stats = getattr(unit, 'stats', {})
        current_hp = current_stats.get('hp', unit.hp)
        current_attack = current_stats.get('attack', unit.attack)
        current_defense = current_stats.get('defense', unit.defense)
        
        # Vérifier si les stats sont boostées
        base_stats = getattr(unit, 'base_stats', {})
        base_hp = base_stats.get('hp', unit.hp)
        base_attack = base_stats.get('attack', unit.attack)
        base_defense = base_stats.get('defense', unit.defense)
        
        stats_boosted = (current_hp > base_hp or current_attack > base_attack or current_defense > base_defense)
        
        stats_text = f"HP: {current_hp} | ATK: {current_attack} | DEF: {current_defense}"
        # Couleur verte si les stats sont boostées
        stats_color = COLORS['green'] if stats_boosted else COLORS['light_gold']
        stats_surface = self.get_cached_font(14).render(stats_text, True, stats_color)
        stats_rect = stats_surface.get_rect(centerx=overlay_width//2, y=primary_stats_y)
        
        # Fond pour les stats primaires (collé au fond des stats secondaires)
        stats_bg_rect = pygame.Rect(stats_rect.x - 5, stats_rect.y - 2, stats_rect.width + 10, stats_rect.height + 4)
        pygame.draw.rect(overlay_surface, (*COLORS['deep_black'], 200), stats_bg_rect, border_radius=5)
        overlay_surface.blit(stats_surface, stats_rect)
        
        # Capacités - lister TOUTES les capacités, centrées autour de la position actuelle
        ability_y_center = overlay_height - int(overlay_height * 0.40)  # centre vertical de la zone des capacités
        if hasattr(unit, 'abilities') and unit.abilities:
            font = self.get_cached_font(14)
            line_height = font.get_height()
            line_spacing = 4
            total_height = len(unit.abilities) * line_height + max(0, (len(unit.abilities) - 1) * line_spacing)
            start_y = int(ability_y_center - total_height / 2)
            
            for idx, ab in enumerate(unit.abilities):
                ability_name = getattr(ab, 'name', 'Capacité')
                ability_id = getattr(ab, 'ability_id', 'N/A')
                
                # Log détaillé pour debug (seulement si problème)
                if ability_name == 'Capacité' or ability_id == 'N/A':
                    print(f"[OVERLAY] PROBLÈME: Capacité {idx+1}: '{ability_name}' (ID: {ability_id})")
                
                if len(ability_name) > 30:
                    ability_name = ability_name[:27] + "..."
            
                # Cooldown via moteur: préférer le système par ID si disponible
                cooldown = 0
                if self.combat_engine:
                    if hasattr(ab, 'ability_id'):
                        cooldown = self.combat_engine.get_unit_ability_cooldown(unit, getattr(ab, 'ability_id'))
                    else:
                        cooldown = self.combat_engine.get_ability_cooldown(unit, ab)
                
                ability_color = COLORS['crimson'] if cooldown > 0 else (0, 255, 0)
                
                line_y = start_y + idx * (line_height + line_spacing)
                
                # Récupérer l'élément de la capacité pour le symbole
                ability_element = "1"  # Par défaut feu
                if hasattr(ab, 'ability_id'):
                    # Utiliser les données déjà chargées dans l'objet Ability
                    # L'élément devrait être stocké dans l'objet lors de la création
                    if hasattr(ab, 'element'):
                        ability_element = ab.element
                    else:
                        # Fallback: essayer de récupérer depuis effects_database.json
                        try:
                            with open("Data/effects_database.json", 'r', encoding='utf-8') as f:
                                effects_data = json.load(f)
                            abilities_data = effects_data.get("abilities", {})
                            if getattr(ab, 'ability_id') in abilities_data:
                                ability_element = abilities_data[getattr(ab, 'ability_id')].get("element", "1")
                        except:
                            pass
                
                # Symbole d'élément de la capacité (12x12)
                element_mapping = {
                    '1': 'feu', '2': 'eau', '3': 'terre', '4': 'air', '5': 'glace',
                    '6': 'foudre', '7': 'lumière', '8': 'ténèbres', '9': 'arcanique',
                    '10': 'poison', '11': 'néant', '12': 'néant'
                }
                element_name = element_mapping.get(str(ability_element), 'feu')
                element_symbol_path = f"Symbols/{element_name}.png"
                element_symbol = self.game_ui.asset_manager.get_image(element_symbol_path)
                
                # Calculer la largeur totale de la ligne (symbole + nom + cooldown)
                symbol_size = (12, 12)
                ability_surface = font.render(ability_name, True, ability_color)
                cooldown_surface = font.render(str(cooldown), True, ability_color)
                
                # Largeurs des éléments
                symbol_width = 12
                text_width = ability_surface.get_width()
                cooldown_width = cooldown_surface.get_width()
                spacing = 6  # Espace entre les éléments
                
                # Largeur totale de la ligne
                total_line_width = symbol_width + spacing + text_width + spacing + cooldown_width
                
                # Position de départ pour centrer toute la ligne
                line_start_x = (overlay_width - total_line_width) // 2
                
                # Positions des éléments
                symbol_x = line_start_x
                text_x = symbol_x + symbol_width + spacing
                cooldown_x = text_x + text_width + spacing
                
                # Nom de la capacité
                ability_rect = ability_surface.get_rect(x=text_x, y=line_y)
                
                # Fond pour la capacité (élargi pour inclure le symbole et le cooldown)
                ability_bg_rect = pygame.Rect(symbol_x - 2, ability_rect.y - 2, total_line_width + 4, ability_rect.height + 4)
                
                pygame.draw.rect(overlay_surface, (*COLORS['deep_black'], 200), ability_bg_rect, border_radius=5)
                overlay_surface.blit(ability_surface, ability_rect)
                
                # Afficher le symbole d'élément APRÈS le fond (pour qu'il soit visible)
                if element_symbol:
                    # Afficher le symbole d'élément (12x12)
                    scaled_symbol = pygame.transform.scale(element_symbol, symbol_size)
                    symbol_y = line_y + (line_height - 12) // 2  # Centrer verticalement
                    symbol_rect = scaled_symbol.get_rect(topleft=(symbol_x, symbol_y))
                    overlay_surface.blit(scaled_symbol, symbol_rect)
                
                # Cooldown à droite
                cooldown_rect = cooldown_surface.get_rect(x=cooldown_x, y=line_y)
                overlay_surface.blit(cooldown_surface, cooldown_rect)
        
        return overlay_surface
    
    def create_rounded_mask(self, width, height, radius):
        """Crée un masque avec coins arrondis parfaits sans artefacts - Version optimisée avec cache"""
        
        # Validation du radius pour éviter les artefacts
        max_radius = min(width, height) // 2
        if radius > max_radius:
            radius = max_radius
            print(f"⚠️  Radius ajusté à {max_radius} pour éviter les artefacts")
        
        # Cache des masques pour éviter la régénération
        if not hasattr(self, '_mask_cache'):
            self._mask_cache = {}
        
        # Clé de cache unique
        cache_key = f"{width}x{height}_r{radius}"
        
        # Retourner le masque en cache s'il existe
        if cache_key in self._mask_cache:
            return self._mask_cache[cache_key]
        
        # Créer un nouveau masque
        mask_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Créer un masque de forme avec des coins arrondis
        # Le masque final : blanc (opaque) dans le rectangle arrondi, transparent ailleurs
        mask_surface.fill((0, 0, 0, 0))  # Tout transparent par défaut
        pygame.draw.rect(mask_surface, (255, 255, 255, 255), (0, 0, width, height), border_radius=radius)
        
        # Mettre en cache pour réutilisation
        self._mask_cache[cache_key] = mask_surface
        
        # Limiter la taille du cache (garder les 50 derniers masques)
        if len(self._mask_cache) > 50:
            # Supprimer les entrées les plus anciennes
            oldest_keys = list(self._mask_cache.keys())[:10]
            for key in oldest_keys:
                del self._mask_cache[key]
        
        return mask_surface

    def apply_rounded_corners_to_image(self, original_image, target_width, target_height, radius, use_smooth_scale=True):
        """
        Applique des coins arrondis à une image avec optimisations
        
        Args:
            original_image: Surface pygame de l'image originale
            target_width: Largeur cible
            target_height: Hauteur cible
            radius: Rayon des coins arrondis
            use_smooth_scale: Utiliser smoothscale pour un meilleur redimensionnement
        
        Returns:
            Surface pygame avec coins arrondis optimisée
        """
        # Validation du radius
        max_radius = min(target_width, target_height) // 2
        if radius > max_radius:
            radius = max_radius
        
        # Redimensionner l'image avec choix de qualité
        if use_smooth_scale and (target_width > original_image.get_width() * 1.5 or 
                                target_height > original_image.get_height() * 1.5):
            # Utiliser smoothscale pour les gros agrandissements
            scaled_image = pygame.transform.smoothscale(original_image, (target_width, target_height))
        else:
            # Utiliser scale normal pour les autres cas
            scaled_image = pygame.transform.scale(original_image, (target_width, target_height))
        
        # Créer une surface avec support alpha
        image_surface = pygame.Surface((target_width, target_height), pygame.SRCALPHA)
        
        # Créer le masque de coins arrondis (avec cache)
        mask_surface = self.create_rounded_mask(target_width, target_height, radius)
        
        # Appliquer l'image d'abord
        image_surface.blit(scaled_image, (0, 0))
        
        # Puis appliquer le masque pour couper les coins
        image_surface.blit(mask_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        
        # Optimisation finale : convertir pour accélérer l'affichage
        return image_surface.convert_alpha()

    def clear_mask_cache(self):
        """Vide le cache des masques de coins arrondis"""
        if hasattr(self, '_mask_cache'):
            self._mask_cache.clear()
            print("✅ Cache des masques vidé")

    

class HeroCustomizationScreen(Screen):
    def __init__(self, game_ui: GameUI):
        super().__init__(game_ui)
        self.hero_to_customize = None
        self.original_hero_data = None  # Données originales du héros
        self.customization = None
        self.sliders = {}
        self.ability_buttons = []
        self.cached_customized_hero = None  # Cache pour éviter les recalculs
        self._font_cache = {}  # Cache pour les polices
        self.setup_buttons()
    
    def setup_buttons(self):
        """Configure les boutons de l'écran"""
        button_width = 200
        button_height = 50
        button_spacing = 20
        
        # Position des boutons
        button_y = SCREEN_HEIGHT - button_height - 20
        button_x = SCREEN_WIDTH - button_width - 20
        
        self.buttons = [
            Button(button_x, button_y, button_width, button_height, "RETOUR", COLORS['gray'], COLORS['white'], 
                   self.discard_changes_and_return, "Annule les modifications et retourne au deck builder"),
            Button(button_x - button_width - button_spacing, button_y, button_width, button_height, "RÉINITIALISER", 
                   COLORS['crimson'], COLORS['white'], self.reset_customization, "Remet à zéro toutes les personnalisations du héros"),
            Button(button_x - 2 * (button_width + button_spacing), button_y, button_width, button_height, "APPLIQUER", 
                   COLORS['gold'], COLORS['deep_black'], self.apply_customization, "Sauvegarde et applique les modifications")
        ]
    
    def setup_sliders(self, force_reset=False):
        """Configure les sliders pour les stats"""
        if not self.customization:
            return
        

        
        # Position des sliders selon les spécifications exactes
        slider_x = 50
        slider_width = 300
        slider_height = 20
        
        # Positions exactes pour chaque slider
        slider_positions = {
            "hp": 245,      # Premier slider
            "attack": 345,  # Deuxième slider (245 + 100)
            "defense": 445  # Troisième slider (245 + 200)
        }
        
        # Créer les sliders pour chaque stat
        stats = [
            ("hp", "HP", 0, 15, 5),  # (name, label, min, max, step)
            ("attack", "Attaque", 0, 15, 5),
            ("defense", "Défense", 0, 15, 5)
        ]
        
        # Sauvegarder les valeurs actuelles des sliders existants (sauf si on force le reset)
        old_values = {}
        if not force_reset and hasattr(self, 'sliders'):
            for stat_name in self.sliders:
                if stat_name in self.sliders:
                    old_values[stat_name] = self.sliders[stat_name].value
        
        self.sliders = {}
        for i, (stat_name, label, min_val, max_val, step) in enumerate(stats):
            y = slider_positions[stat_name]
            
            # Afficher le texte de la stat au-dessus des graduations
            text_y = y - 40  # 40 pixels au-dessus du slider
            text_surface = self.game_ui.font_medium.render(label, True, COLORS['white'])
            # Le texte sera affiché dans la méthode draw du slider
            
            # Obtenir la valeur actuelle (préférer l'ancienne valeur si elle existe et qu'on ne force pas le reset)
            if not force_reset and stat_name in old_values:
                current_value = old_values[stat_name]
            else:
                current_value = getattr(self.customization, f"{stat_name}_bonus", 0)
            

            
            # Créer le slider
            hero_name = self.hero_to_customize.get("name", "Héros inconnu") if self.hero_to_customize else None
            slider = Slider(
                slider_x, y, slider_width, slider_height,
                min_val, max_val, current_value, step,
                label, self.on_slider_change, stat_name, hero_name, self.game_ui
            )
            self.sliders[stat_name] = slider
    
    def setup_ability_buttons(self):
        """Configure les boutons pour la sélection d'aptitude et passif"""
        if not self.customization or not self.hero_to_customize:
            return
        
        # Position des boutons d'aptitude
        button_x = 50
        button_y = 500
        button_width = 220  # Légèrement plus large pour accommoder le texte
        button_height = 55  # Légèrement plus haut pour accommoder le texte
        spacing = 20
        
        # Récupérer les informations du héros pour les tooltips
        hero = self.hero_to_customize
        basic_cooldown = hero.get('basic_attack_cooldown', 1)
        ability_name = hero.get('ability_name', 'Capacité inconnue')
        ability_description = hero.get('ability_description', 'Aucune description disponible')
        ability_cooldown = hero.get('ability_cooldown', 0)
        passive_description = hero.get('passive', 'Aucun passif disponible')
        
        # Créer les tooltips
        basic_tooltip = f"Attaque Basique\n\nInflige des dégâts physiques à l'ennemi ciblé.\nCooldown: {basic_cooldown} tour(s)\n\nSimple et efficace, cette attaque peut être utilisée fréquemment."
        
        # Extraire seulement la description après les ":"
        ability_desc_only = ability_description
        if ":" in ability_description:
            ability_desc_only = ability_description.split(":", 1)[1].strip()
        
        hero_tooltip = f"Capacité du Héros\n\n{ability_name}\n\n{ability_desc_only}\n\nCooldown: {ability_cooldown} tour(s)\n\nCapacité spéciale unique du héros avec des effets puissants."
        
        # Créer le tooltip pour le passif
        passive_tooltip = f"Passif du Héros\n\n{passive_description}\n\nEffet automatique qui s'active en permanence.\n\nPar défaut, les héros n'ont pas leur passif activé."
        
        # Calculer le coût du passif pour ce héros
        passive_cost = 0
        if self.customization.has_passive and hero_customization_manager:
            passive_cost = self.customization._get_passive_cost(hero)
        
        # Déterminer le texte et la couleur du bouton passif selon l'état actuel
        if self.customization.has_passive:
            passive_text = f"Désactiver Passif (-{passive_cost} mana)"
            passive_color = COLORS['red']
        else:
            passive_text = f"Activer Passif (+{passive_cost} mana)"
            passive_color = COLORS['purple']
        
        # Créer les boutons pour les aptitudes et le passif
        self.ability_buttons = [
            Button(button_x, button_y, button_width, button_height, 
                   "Attaque Basique (+0 mana)", COLORS['gray'], COLORS['white'],
                   lambda: self.select_ability(False), basic_tooltip),
            Button(button_x + button_width + spacing, button_y, button_width, button_height,
                   "Capacité du Héros (+1 mana)", COLORS['gold'], COLORS['white'],
                   lambda: self.select_ability(True), hero_tooltip),
            Button(button_x, button_y + button_height + spacing, button_width * 2 + spacing, button_height,
                   passive_text, passive_color, COLORS['white'],
                   lambda: self.toggle_passive(), passive_tooltip)
        ]
        
        # Mettre à jour les textes des boutons selon l'état actuel
        self.update_ability_button_texts()
    
    def on_slider_change(self, stat_name, value):
        """Appelé quand un slider change"""
        if not self.customization:
            return
        
        # Mettre à jour la valeur directement dans l'objet customization
        setattr(self.customization, f"{stat_name}_bonus", value)
        
        # Recalculer le coût d'activation avec les données du héros
        self.customization.calculate_activation_cost(self.hero_to_customize)
        
        # Vider le cache pour forcer la mise à jour de l'overlay
        self.cached_customized_hero = None
    
    def select_ability(self, use_hero_ability):
        """Sélectionne l'aptitude à utiliser"""
        if not self.customization or not hero_customization_manager:
            return
        
        self.customization.use_hero_ability = use_hero_ability
        
        # Recalculer le coût d'activation avec les données du héros
        self.customization.calculate_activation_cost(self.hero_to_customize)
        
        # Vider le cache pour forcer la mise à jour de l'overlay
        self.cached_customized_hero = None
        
        # Mettre à jour les textes des boutons de capacité
        self.update_ability_button_texts()
        
        # Ne pas sauvegarder immédiatement - seulement lors de l'application
    
    def update_ability_button_texts(self):
        """Met à jour les textes et couleurs des boutons de capacité selon leur état"""
        if not self.ability_buttons or len(self.ability_buttons) < 2:
            return
        
        # Bouton attaque basique (index 0)
        basic_button = self.ability_buttons[0]
        if self.customization and not self.customization.use_hero_ability:
            basic_button.text = "Attaque Basique (+0 mana)"
            basic_button.text_color = COLORS['crimson']  # Rouge foncé pour texte sélectionné
        else:
            basic_button.text = "Attaque Basique (+0 mana)"
            basic_button.text_color = COLORS['white']  # Blanc pour texte normal
        
        # Bouton capacité du héros (index 1)
        hero_button = self.ability_buttons[1]
        if self.customization and self.customization.use_hero_ability:
            hero_button.text = "Capacité du Héros (+1 mana)"
            hero_button.text_color = COLORS['crimson']  # Rouge foncé pour texte sélectionné
        else:
            hero_button.text = "Capacité du Héros (+1 mana)"
            hero_button.text_color = COLORS['white']  # Blanc pour texte normal
    
    def toggle_passive(self):
        """Active/désactive le passif du héros"""
        if not self.customization or not hero_customization_manager:
            return
        
        self.customization.has_passive = not self.customization.has_passive
        
        # Recalculer le coût d'activation avec les données du héros
        self.customization.calculate_activation_cost(self.hero_to_customize)
        
        # Vider le cache pour forcer la mise à jour de l'overlay
        self.cached_customized_hero = None
        
        # Mettre à jour le texte du bouton
        self.update_passive_button_text()
        
        # Ne pas sauvegarder immédiatement - seulement lors de l'application
    
    def update_passive_button_text(self):
        """Met à jour le texte du bouton passif selon son état"""
        if not self.ability_buttons or len(self.ability_buttons) < 3:
            return
        
        # Calculer le coût du passif pour ce héros
        passive_cost = 0
        if self.customization and hero_customization_manager:
            passive_cost = self.customization._get_passive_cost(self.hero_to_customize)
        
        passive_button = self.ability_buttons[2]  # Le troisième bouton est le passif
        if self.customization and self.customization.has_passive:
            passive_button.text = f"Désactiver Passif (-{passive_cost} mana)"
            passive_button.color = COLORS['red']
        else:
            passive_button.text = f"Activer Passif (+{passive_cost} mana)"
            passive_button.color = COLORS['purple']
    
    def discard_changes(self):
        """Annule les modifications et recharge la dernière personnalisation sauvegardée"""
        if not self.hero_to_customize or not hero_customization_manager:
            return
        
        hero_name = self.hero_to_customize.get("name", "Héros inconnu")
        
        # Recharger la personnalisation depuis le fichier (annule les modifications non sauvegardées)
        self.customization = hero_customization_manager.get_customization(hero_name)
        if not self.customization:
            # Si aucune personnalisation n'existe, créer une nouvelle par défaut
            self.customization = hero_customization_manager.create_customization(hero_name)
        
        # Vider le cache pour forcer le recalcul
        self.cached_customized_hero = None
        
        # Reconfigurer les sliders et boutons avec les valeurs sauvegardées
        self.setup_sliders(force_reset=True)
        self.setup_ability_buttons()
        
        print(f"[CUSTOMIZATION] Modifications annulées pour {hero_name}")
    
    def discard_changes_and_return(self):
        """Annule les modifications et retourne au deck builder"""
        # RESTAURATION COMPLÈTE de tout l'état d'ouverture
        if hasattr(self, '_opening_customization_cache') and self._opening_customization_cache:
            import copy
            
            # Restaurer TOUT l'état d'ouverture
            cache = self._opening_customization_cache
            
            # 1. Restaurer l'objet customization de manière robuste
            if 'customization' in cache and cache['customization']:
                # Créer un nouvel objet customization propre
                hero_name = self.hero_to_customize.get("name", "Héros inconnu") if self.hero_to_customize else "Héros inconnu"
                
                # Créer une nouvelle personnalisation
                if hero_customization_manager:
                    self.customization = hero_customization_manager.create_customization(hero_name)
                    
                    # Copier manuellement toutes les propriétés
                    cached_customization = cache['customization']
                    self.customization.hp_bonus = getattr(cached_customization, 'hp_bonus', 0)
                    self.customization.attack_bonus = getattr(cached_customization, 'attack_bonus', 0)
                    self.customization.defense_bonus = getattr(cached_customization, 'defense_bonus', 0)
                    self.customization.use_hero_ability = getattr(cached_customization, 'use_hero_ability', False)
                    self.customization.has_passive = getattr(cached_customization, 'has_passive', False)
                    
                    # Recalculer le coût d'activation
                    if self.hero_to_customize:
                        self.customization.calculate_activation_cost(self.hero_to_customize)
                    
                    print(f"[CUSTOMIZATION] Objet customization restauré pour {hero_name}")
                else:
                    print("[ERREUR] Gestionnaire de personnalisation non disponible")
            else:
                print("[ERREUR] Cache de personnalisation manquant")
            
            # 2. Restaurer les données du héros
            self.hero_to_customize = copy.deepcopy(cache['hero_data'])
            self.original_hero_data = copy.deepcopy(cache['original_hero_data'])
            
            # 3. Restaurer les valeurs des sliders
            if 'slider_values' in cache:
                for stat_name, value in cache['slider_values'].items():
                    if hasattr(self, 'sliders') and stat_name in self.sliders:
                        self.sliders[stat_name].value = value
            
            # 4. Restaurer l'état des boutons
            if 'button_states' in cache:
                button_states = cache['button_states']
                self.customization.use_hero_ability = button_states.get('use_hero_ability', False)
                self.customization.has_passive = button_states.get('has_passive', False)
            
            # 5. Restaurer les couleurs des boutons
            if 'button_colors' in cache:
                for i, colors in cache['button_colors'].items():
                    if hasattr(self, 'ability_buttons') and i < len(self.ability_buttons):
                        self.ability_buttons[i].color = colors['color']
                        self.ability_buttons[i].text_color = colors['text_color']
            
            # 6. Vider tous les caches
            self.cached_customized_hero = None
            
            # 7. Forcer la mise à jour complète
            self._force_visual_update()
            
            # 8. Vérification de la restauration
            self._verify_restoration()
            
            hero_name = self.hero_to_customize.get("name", "Héros inconnu") if self.hero_to_customize else "Héros inconnu"
            print(f"[CUSTOMIZATION] Restauration complète effectuée pour {hero_name}")
        
        # Invalider le cache du deck builder
        deck_builder_screen = self.game_ui.screens.get("deck_builder")
        if deck_builder_screen:
            deck_builder_screen.invalidate_cache()
        
        self.game_ui.change_screen("deck_builder")
    
    def _force_visual_update(self):
        """Force la mise à jour de tous les éléments visuels"""
        # Recalculer le coût d'activation
        if self.customization and self.hero_to_customize:
            self.customization.calculate_activation_cost(self.hero_to_customize)
        
        # Mettre à jour les textes des boutons
        self.update_ability_button_texts()
        self.update_passive_button_text()
        
        # Forcer la mise à jour des couleurs des boutons
        if hasattr(self, 'ability_buttons') and self.customization:
            # Attaque basique
            if not self.customization.use_hero_ability:
                self.ability_buttons[0].color = COLORS['light_gold']
                self.ability_buttons[1].color = COLORS['gray']
            else:
                self.ability_buttons[0].color = COLORS['gray']
                self.ability_buttons[1].color = COLORS['light_gold']
            
            # Passif
            if self.customization.has_passive:
                self.ability_buttons[2].color = COLORS['red']
            else:
                self.ability_buttons[2].color = COLORS['purple']
    
    def _verify_restoration(self):
        """Vérifie que la restauration s'est bien passée"""
        if not hasattr(self, '_opening_customization_cache') or not self._opening_customization_cache:
            print("[VERIFICATION] Pas de cache disponible")
            return
        
        cache = self._opening_customization_cache
        if not self.customization:
            print("[VERIFICATION] Objet customization manquant après restauration")
            return
        
        # Vérifier les valeurs des sliders
        if 'slider_values' in cache:
            for stat_name, expected_value in cache['slider_values'].items():
                if hasattr(self, 'sliders') and stat_name in self.sliders:
                    actual_value = self.sliders[stat_name].value
                    if actual_value != expected_value:
                        print(f"[VERIFICATION] Slider {stat_name}: attendu {expected_value}, obtenu {actual_value}")
                    else:
                        print(f"[VERIFICATION] Slider {stat_name}: OK ({actual_value})")
        
        # Vérifier l'objet customization
        if 'customization' in cache and cache['customization']:
            cached_customization = cache['customization']
            print(f"[VERIFICATION] Customization - HP: {self.customization.hp_bonus} (attendu: {getattr(cached_customization, 'hp_bonus', 'N/A')})")
            print(f"[VERIFICATION] Customization - ATK: {self.customization.attack_bonus} (attendu: {getattr(cached_customization, 'attack_bonus', 'N/A')})")
            print(f"[VERIFICATION] Customization - DEF: {self.customization.defense_bonus} (attendu: {getattr(cached_customization, 'defense_bonus', 'N/A')})")
            print(f"[VERIFICATION] Customization - Ability: {self.customization.use_hero_ability} (attendu: {getattr(cached_customization, 'use_hero_ability', 'N/A')})")
            print(f"[VERIFICATION] Customization - Passive: {self.customization.has_passive} (attendu: {getattr(cached_customization, 'has_passive', 'N/A')})")
    
    def set_hero_to_customize(self, hero_data):
        """Définit le héros à personnaliser"""
        # Stocker une copie profonde des données originales du héros
        import copy
        self.hero_to_customize = copy.deepcopy(hero_data)
        self.original_hero_data = copy.deepcopy(hero_data)  # Garder une copie des données originales
        hero_name = hero_data.get("name", "Héros inconnu")
        
        # Vider le cache pour forcer le recalcul avec le nouveau héros
        self.cached_customized_hero = None
        
        # Récupérer ou créer la personnalisation
        if hero_customization_manager:
            self.customization = hero_customization_manager.get_customization(hero_name)
            if not self.customization:
                self.customization = hero_customization_manager.create_customization(hero_name)
            
            # Configurer les sliders et boutons
            self.setup_sliders()
            self.setup_ability_buttons()
            
            # SAUVEGARDE COMPLÈTE de tout l'état du héros au moment de l'ouverture
            self._opening_customization_cache = {
                'customization': copy.deepcopy(self.customization),
                'slider_values': {},
                'button_states': {},
                'button_colors': {},
                'hero_data': copy.deepcopy(self.hero_to_customize),
                'original_hero_data': copy.deepcopy(self.original_hero_data)
            }
            
            # Sauvegarder les valeurs des sliders
            if hasattr(self, 'sliders'):
                for stat_name, slider in self.sliders.items():
                    self._opening_customization_cache['slider_values'][stat_name] = slider.value
            
            # Sauvegarder l'état des boutons
            if hasattr(self, 'ability_buttons'):
                self._opening_customization_cache['button_states'] = {
                    'use_hero_ability': self.customization.use_hero_ability,
                    'has_passive': self.customization.has_passive
                }
                
                # Sauvegarder les couleurs des boutons
                for i, button in enumerate(self.ability_buttons):
                    self._opening_customization_cache['button_colors'][i] = {
                        'color': button.color,
                        'text_color': button.text_color
                    }
            
            print(f"[CUSTOMIZATION] Sauvegarde complète créée pour {hero_name}")
            
            # Invalider le cache du deck builder pour forcer la mise à jour
            deck_builder_screen = self.game_ui.screens.get("deck_builder")
            if deck_builder_screen:
                deck_builder_screen.invalidate_cache()
        else:
            print("[ERREUR] Gestionnaire de personnalisation non disponible")
    
    def get_customized_hero(self):
        """Retourne le héros personnalisé"""
        if not self.original_hero_data or not self.customization:
            return self.hero_to_customize
        
        # Vérifier si le cache est valide
        if (self.cached_customized_hero and 
            self.cached_customized_hero.get('_cache_hp_bonus') == self.customization.hp_bonus and
            self.cached_customized_hero.get('_cache_attack_bonus') == self.customization.attack_bonus and
            self.cached_customized_hero.get('_cache_defense_bonus') == self.customization.defense_bonus):
            return self.cached_customized_hero
        
        if hero_customization_manager:
            customized_hero = hero_customization_manager.apply_customization_to_hero(self.original_hero_data, self.customization)
            
            # Ajouter des métadonnées de cache
            customized_hero['_cache_hp_bonus'] = self.customization.hp_bonus
            customized_hero['_cache_attack_bonus'] = self.customization.attack_bonus
            customized_hero['_cache_defense_bonus'] = self.customization.defense_bonus
            
            # Mettre en cache
            self.cached_customized_hero = customized_hero
            return customized_hero
        
        return self.hero_to_customize
    
    def reset_customization(self):
        """Remet à zéro la personnalisation"""
        if not self.customization or not hero_customization_manager:
            return
        
        hero_name = self.hero_to_customize.get("name", "Héros inconnu")
        hero_customization_manager.reset_customization(hero_name)
        self.customization = hero_customization_manager.create_customization(hero_name)
        
        # Vider le cache pour forcer le recalcul
        self.cached_customized_hero = None
        
        # Reconfigurer les sliders et boutons
        self.setup_sliders(force_reset=True)
        self.setup_ability_buttons()
    
    def apply_customization(self):
        """Applique la personnalisation"""
        if not self.customization or not hero_customization_manager:
            return
        
        hero_name = self.hero_to_customize.get("name", "Héros inconnu")
        
        # Sauvegarder la personnalisation complète
        hero_customization_manager.customizations[hero_name] = self.customization
        hero_customization_manager.save_customizations()
        
        # Supprimer les modifications temporaires pour ce héros
        if hasattr(self, '_temp_customizations') and hero_name in self._temp_customizations:
            del self._temp_customizations[hero_name]
        
        # Forcer l'invalidation du cache du deck builder
        deck_builder_screen = self.game_ui.screens.get("deck_builder")
        if deck_builder_screen:
            deck_builder_screen.invalidate_cache()
            # Forcer aussi la mise à jour de l'état de cache
            deck_builder_screen._last_hero_customization = None
        
        print(f"[CUSTOMIZATION] Personnalisation appliquée pour {hero_name}")
        self.game_ui.change_screen("deck_builder")
    
    def handle_event(self, event):
        """Gestion des événements de l'écran de personnalisation"""
        mouse_pos = pygame.mouse.get_pos()
        
        # Mise à jour du hover pour tous les boutons
        for button in self.buttons + self.ability_buttons:
            button.update_hover(mouse_pos)
        
        # Gestion des clics
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Vérifier les clics sur les boutons
            for button in self.buttons + self.ability_buttons:
                if button.is_clicked(mouse_pos):
                    button.action()
                    return
            
            # Vérifier les clics sur les sliders
            for slider in self.sliders.values():
                if slider.handle_click(mouse_pos):
                    return
        
        # Gestion du relâchement de souris
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            # Relâcher les sliders actifs
            for slider in self.sliders.values():
                if slider.dragging:
                    slider.handle_release()
                    return
        
        # Gestion du mouvement de souris pour le drag des sliders
        if event.type == pygame.MOUSEMOTION:
            # Mettre à jour les sliders en cours de drag
            for slider in self.sliders.values():
                if slider.dragging:
                    slider.handle_drag(mouse_pos)
                    return
    
    def draw(self, screen: pygame.Surface):
        """Dessine l'écran de personnalisation"""
        # Le background est déjà dessiné par GameUI.draw_background()
        # Pas besoin de screen.fill() qui recouvrirait le background
        
        if not self.hero_to_customize:
            # Afficher un message d'erreur
            text = self.game_ui.font_large.render("Aucun héros sélectionné", True, COLORS['white'])
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(text, text_rect)
            return
        
        # Titre
        title = self.game_ui.font_large.render(f"Personnalisation: {self.hero_to_customize.get('name', 'Héros')}", True, COLORS['gold'])
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 50))
        screen.blit(title, title_rect)
        
        # Informations du héros de base
        base_stats = self.original_hero_data.get("base_stats", {})
        base_hp = base_stats.get("hp", 1000)
        base_attack = base_stats.get("attack", 30)
        base_defense = base_stats.get("defense", 25)
        

        
        # Dessiner les sliders
        for slider in self.sliders.values():
            slider.draw(screen)
        
        # Dessiner les boutons d'aptitude
        for button in self.ability_buttons:
            button.draw(screen)
        
        # Mettre à jour les couleurs des boutons d'aptitude selon la sélection
        if self.customization:
            # Attaque basique
            if not self.customization.use_hero_ability:
                self.ability_buttons[0].color = COLORS['light_gold']
                self.ability_buttons[1].color = COLORS['gray']
            else:
                self.ability_buttons[0].color = COLORS['gray']
                self.ability_buttons[1].color = COLORS['light_gold']
        
        # Afficher le coût d'activation centré sous le cadre de prévisualisation
        if self.customization:
            cost_text = f"Coût d'activation: {self.customization.activation_cost} mana"
            cost_surface = self.game_ui.font_medium.render(cost_text, True, COLORS['light_gold'])
            # Centrer par rapport au cadre de prévisualisation (à droite)
            preview_x = SCREEN_WIDTH - 400 - 50  # Même position que dans draw_hero_preview
            cost_rect = cost_surface.get_rect()
            cost_x = preview_x + (400 - cost_rect.width) // 2  # 400 = largeur du cadre
            cost_y = 100 + 600 + 20  # 100 + 600 = bas du cadre + 20px d'espace
            screen.blit(cost_surface, (cost_x, cost_y))
        
        # Dessiner la prévisualisation du héros à droite
        self.draw_hero_preview(screen)
        
        # Dessiner les boutons
        for button in self.buttons:
            button.draw(screen)
        
        # Dessiner les tooltips de tous les boutons
        mouse_pos = pygame.mouse.get_pos()
        for button in self.buttons + self.ability_buttons:
            button.draw_tooltip(screen, mouse_pos)
        
    def draw_hero_preview(self, screen):
        """Dessine la prévisualisation du héros personnalisé avec l'overlay du deck builder"""
        if not self.hero_to_customize:
            return
        
        # Obtenir le héros personnalisé
        customized_hero = self.get_customized_hero()
        
        # Position de la prévisualisation (à droite)
        preview_width = 400
        preview_height = 600
        preview_x = SCREEN_WIDTH - preview_width - 50
        preview_y = 100
        
        # Fond de la prévisualisation
        preview_rect = pygame.Rect(preview_x, preview_y, preview_width, preview_height)
        pygame.draw.rect(screen, COLORS['dark_gray'], preview_rect)
        pygame.draw.rect(screen, COLORS['gold'], preview_rect, 2)
        
        # Charger l'image du héros
        hero_image_path = self.original_hero_data.get("image_path", "default_hero.png")
        hero_image = self.game_ui.asset_manager.get_image(hero_image_path)
        
        if hero_image:
            # Redimensionner l'image pour qu'elle occupe toute la zone de prévisualisation
            scaled_image = pygame.transform.scale(hero_image, (preview_width, preview_height))
            
            # Créer une surface avec coins arrondis pour l'image
            image_surface = pygame.Surface((preview_width, preview_height), pygame.SRCALPHA)
            
            # Créer un masque avec coins arrondis précis
            mask_surface = self.create_rounded_mask(preview_width, preview_height, 20)
            
            # Appliquer le masque à l'image
            image_surface.blit(scaled_image, (0, 0))
            image_surface.blit(mask_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            
            screen.blit(image_surface, (preview_x, preview_y))
        
        # Créer l'overlay du héros personnalisé avec une résolution plus élevée
        overlay_surface = self.create_hero_overlay_surface_high_res(customized_hero)
        
        # Redimensionner l'overlay pour qu'il occupe toute la zone (sans marge)
        scaled_overlay = pygame.transform.scale(overlay_surface, (preview_width, preview_height))
        
        # Afficher l'overlay dans toute la zone de prévisualisation
        screen.blit(scaled_overlay, (preview_x, preview_y))
    
    def get_cached_font(self, size):
        """Retourne une police de la taille spécifiée"""
        if size not in self._font_cache:
            self._font_cache[size] = pygame.font.Font(None, size)
        return self._font_cache[size]
    
    def create_rounded_mask(self, width, height, radius):
        """Crée un masque avec coins arrondis parfaits sans artefacts - Version optimisée avec cache"""
        
        # Validation du radius pour éviter les artefacts
        max_radius = min(width, height) // 2
        if radius > max_radius:
            radius = max_radius
            print(f"⚠️  Radius ajusté à {max_radius} pour éviter les artefacts")
        
        # Cache des masques pour éviter la régénération
        if not hasattr(self, '_mask_cache'):
            self._mask_cache = {}
        
        # Clé de cache unique
        cache_key = f"{width}x{height}_r{radius}"
        
        # Retourner le masque en cache s'il existe
        if cache_key in self._mask_cache:
            return self._mask_cache[cache_key]
        
        # Créer un nouveau masque
        mask_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Créer un masque de forme avec des coins arrondis
        # Le masque final : blanc (opaque) dans le rectangle arrondi, transparent ailleurs
        mask_surface.fill((0, 0, 0, 0))  # Tout transparent par défaut
        pygame.draw.rect(mask_surface, (255, 255, 255, 255), (0, 0, width, height), border_radius=radius)
        
        # Mettre en cache pour réutilisation
        self._mask_cache[cache_key] = mask_surface
        
        # Limiter la taille du cache (garder les 50 derniers masques)
        if len(self._mask_cache) > 50:
            # Supprimer les entrées les plus anciennes
            oldest_keys = list(self._mask_cache.keys())[:10]
            for key in oldest_keys:
                del self._mask_cache[key]
        
        return mask_surface
    
    def create_hero_overlay_surface(self, hero):
        """Crée une surface d'overlay pour un héros (même structure que les unités)"""
        overlay_width = 200
        overlay_height = 288
        overlay_surface = pygame.Surface((overlay_width, overlay_height), pygame.SRCALPHA)
        desc_x = 20

        # Bordure or
        pygame.draw.rect(overlay_surface, COLORS['gold'], (0, 0, overlay_width, overlay_height), 2, border_radius=10)

        # Nom (avant la virgule)
        name_text = hero['name'].split(',')[0].strip()
        name_y = int(overlay_height * 0.08)
        name_surface = self.get_cached_font(22).render(name_text, True, COLORS['white'])
        name_rect = name_surface.get_rect(centerx=overlay_width//2, y=name_y)
        name_bg_rect = pygame.Rect(name_rect.x - 5, name_rect.y - 2, name_rect.width + 10, name_rect.height + 4)
        pygame.draw.rect(overlay_surface, (*COLORS['deep_black'], 200), name_bg_rect, border_radius=5)
        overlay_surface.blit(name_surface, name_rect)

        # Élément (symbole)
        if 'element' in hero and hero['element']:
            element_mapping = {
                'feu': 'feu', 'eau': 'eau', 'glace': 'glace', 'terre': 'terre', 'air': 'air',
                'foudre': 'foudre', 'lumière': 'lumiere', 'ténèbres': 'tenebres', 'arcanique': 'arcane',
                'poison': 'poison', 'néant': 'neant'
            }
            element_name = hero['element'].lower()
            file_name = element_mapping.get(element_name, element_name)
            element_symbol_path = f"Symbols/{file_name}.png"
            element_symbol = self.game_ui.asset_manager.get_image(element_symbol_path)
            if element_symbol:
                symbol_size = (24, 24)
                scaled_symbol = pygame.transform.scale(element_symbol, symbol_size)
                symbol_rect = scaled_symbol.get_rect(topleft=(10, 10))
                circle_radius = 15
                circle_center = (symbol_rect.centerx, symbol_rect.centery)
                pygame.draw.circle(overlay_surface, (*COLORS['deep_black'], 200), circle_center, circle_radius)
                overlay_surface.blit(scaled_symbol, symbol_rect)
            else:
                element_text = f"Élément: {hero['element']}"
                element_surface = self.get_cached_font(12).render(element_text, True, COLORS['light_gold'])
                element_rect = element_surface.get_rect(topleft=(10, 10))
                circle_radius = 15
                circle_center = (element_rect.centerx, element_rect.centery)
                pygame.draw.circle(overlay_surface, (*COLORS['deep_black'], 200), circle_center, circle_radius)
                overlay_surface.blit(element_surface, element_rect)

        # Rareté (mêmes couleurs que unités)
        rarity_y = overlay_height - 30
        if 'rarity' in hero:
            rarity_text = hero['rarity']
            rarity_surface = self.get_cached_font(11).render(rarity_text, True, COLORS['white'])
            rarity_rect = rarity_surface.get_rect(centerx=overlay_width//2, y=rarity_y)
            rarity_colors = {
                'Commun': COLORS['gray'],
                'Peu Commun': COLORS['green'],
                'Rare': COLORS['royal_blue'],
                'Épique': COLORS['crimson'],
                'Héros': COLORS['orange'],
                'Mythique': COLORS['gold'],
                'Spécial': COLORS['cyan'],
                'commun': COLORS['gray'],
                'peu commun': COLORS['green'],
                'rare': COLORS['royal_blue'],
                'épique': COLORS['crimson'],
                'héros': COLORS['orange'],
                'mythique': COLORS['gold'],
                'spécial': COLORS['cyan'],
            }
            rarity_color = rarity_colors.get(rarity_text.lower(), COLORS['white'])
            oval_width = rarity_rect.width + 20
            oval_height = rarity_rect.height + 8
            oval_rect = pygame.Rect(rarity_rect.centerx - oval_width//2, rarity_rect.centery - oval_height//2, oval_width, oval_height)
            pygame.draw.ellipse(overlay_surface, (*COLORS['deep_black'], 200), oval_rect)
            overlay_surface.blit(rarity_surface, rarity_rect)

        # Stats secondaires
        secondary_stats_y = rarity_y - 20 - int(overlay_height * 0.01)
        desc_y = 100
        y_offset = desc_y
        secondary_stats = []
        if 'crit_pct' in hero:
            secondary_stats.append(f"Crit: {hero['crit_pct']}%")
        if 'esquive_pct' in hero:
            secondary_stats.append(f"Esq: {hero['esquive_pct']}%")
        if 'blocage_pct' in hero:
            secondary_stats.append(f"Bloc: {hero['blocage_pct']}%")
        if 'precision_pct' in hero:
            secondary_stats.append(f"Préc: {hero['precision_pct']}%")
        if secondary_stats:
            secondary_stats_text = " | ".join(secondary_stats)
            secondary_stats_surface = self.get_cached_font(12).render(secondary_stats_text, True, COLORS['light_blue'])
            secondary_stats_rect = secondary_stats_surface.get_rect(centerx=overlay_width//2, y=secondary_stats_y)
            secondary_stats_bg_rect = pygame.Rect(secondary_stats_rect.x - 5, secondary_stats_rect.y - 2, secondary_stats_rect.width + 10, secondary_stats_rect.height + 4)
            pygame.draw.rect(overlay_surface, (*COLORS['deep_black'], 200), secondary_stats_bg_rect, border_radius=5)
            overlay_surface.blit(secondary_stats_surface, secondary_stats_rect)

        # Stats primaires
        primary_stats_y = secondary_stats_y - 20
        hp = hero.get('hp', hero.get('base_stats', {}).get('hp', 0))
        attack = hero.get('attack', hero.get('base_stats', {}).get('attack', 0))
        defense = hero.get('defense', hero.get('base_stats', {}).get('defense', 0))
        stats_text = f"HP: {hp} | ATK: {attack} | DEF: {defense}"
        stats_surface = self.get_cached_font(14).render(stats_text, True, COLORS['light_gold'])
        stats_rect = stats_surface.get_rect(centerx=overlay_width//2, y=primary_stats_y)
        stats_bg_rect = pygame.Rect(stats_rect.x - 5, stats_rect.y - 2, stats_rect.width + 10, stats_rect.height + 4)
        pygame.draw.rect(overlay_surface, (*COLORS['deep_black'], 200), stats_bg_rect, border_radius=5)
        overlay_surface.blit(stats_surface, stats_rect)

        # Capacité (nom + cooldown, couleur verte si utilisable)
        ability_y = overlay_height - int(overlay_height * 0.40)
        if 'ability_name' in hero and hero['ability_name']:
            ability_name = hero['ability_name']
            if len(ability_name) > 30:
                ability_name = ability_name[:27] + "..."
            cooldown = hero.get('ability_cooldown', 0)
            ability_color = COLORS['crimson'] if cooldown > 0 else (0, 255, 0)
            ability_surface = self.get_cached_font(14).render(ability_name, True, ability_color)
            ability_rect = ability_surface.get_rect(centerx=overlay_width//2, y=ability_y)
            ability_bg_rect = pygame.Rect(ability_rect.x - 5, ability_rect.y - 2, ability_rect.width + 10, ability_rect.height + 4)
            pygame.draw.rect(overlay_surface, (*COLORS['deep_black'], 200), ability_bg_rect, border_radius=5)
            overlay_surface.blit(ability_surface, ability_rect)
            cooldown_text = str(cooldown)
            cooldown_surface = self.get_cached_font(14).render(cooldown_text, True, ability_color)
            cooldown_rect = cooldown_surface.get_rect(midleft=(ability_rect.right + 5, ability_rect.centery))
            cooldown_bg_rect = pygame.Rect(cooldown_rect.x - 3, cooldown_rect.y - 2, cooldown_rect.width + 6, cooldown_rect.height + 4)
            pygame.draw.rect(overlay_surface, (*COLORS['deep_black'], 200), cooldown_bg_rect, border_radius=3)
            overlay_surface.blit(cooldown_surface, cooldown_rect)

        return overlay_surface

    def create_hero_overlay_surface_high_res(self, hero):
        """Crée une surface d'overlay haute résolution pour un héros dans la personnalisation"""
        # Résolution plus élevée pour une meilleure qualité
        overlay_width = 400
        overlay_height = 576  # 2x la hauteur originale
        overlay_surface = pygame.Surface((overlay_width, overlay_height), pygame.SRCALPHA)

        # Bordure or
        pygame.draw.rect(overlay_surface, COLORS['gold'], (0, 0, overlay_width, overlay_height), 4, border_radius=20)

        # Nom (avant la virgule) - police plus grande
        name_text = hero['name'].split(',')[0].strip()
        name_y = int(overlay_height * 0.08)
        name_surface = self.get_cached_font(44).render(name_text, True, COLORS['white'])
        name_rect = name_surface.get_rect(centerx=overlay_width//2, y=name_y)
        name_bg_rect = pygame.Rect(name_rect.x - 10, name_rect.y - 4, name_rect.width + 20, name_rect.height + 8)
        pygame.draw.rect(overlay_surface, (*COLORS['deep_black'], 200), name_bg_rect, border_radius=10)
        overlay_surface.blit(name_surface, name_rect)

        # Élément (symbole) - plus grand
        if 'element' in hero and hero['element']:
            element_mapping = {
                'feu': 'feu', 'eau': 'eau', 'glace': 'glace', 'terre': 'terre', 'air': 'air',
                'foudre': 'foudre', 'lumière': 'lumiere', 'ténèbres': 'tenebres', 'arcanique': 'arcane',
                'poison': 'poison', 'néant': 'neant'
            }
            element_name = hero['element'].lower()
            file_name = element_mapping.get(element_name, element_name)
            element_symbol_path = f"Symbols/{file_name}.png"
            element_symbol = self.game_ui.asset_manager.get_image(element_symbol_path)
            if element_symbol:
                symbol_size = (48, 48)  # Plus grand symbole
                scaled_symbol = pygame.transform.scale(element_symbol, symbol_size)
                symbol_rect = scaled_symbol.get_rect(topleft=(20, 20))
                circle_radius = 30  # Plus grand cercle
                circle_center = (symbol_rect.centerx, symbol_rect.centery)
                pygame.draw.circle(overlay_surface, (*COLORS['deep_black'], 200), circle_center, circle_radius)
                overlay_surface.blit(scaled_symbol, symbol_rect)
            else:
                element_text = f"Élément: {hero['element']}"
                element_surface = self.get_cached_font(24).render(element_text, True, COLORS['light_gold'])
                element_rect = element_surface.get_rect(topleft=(20, 20))
                circle_radius = 30
                circle_center = (element_rect.centerx, element_rect.centery)
                pygame.draw.circle(overlay_surface, (*COLORS['deep_black'], 200), circle_center, circle_radius)
                overlay_surface.blit(element_surface, element_rect)

        # Rareté - plus grande police
        rarity_y = overlay_height - 60
        if 'rarity' in hero:
            rarity_text = hero['rarity']
            rarity_surface = self.get_cached_font(22).render(rarity_text, True, COLORS['white'])
            rarity_rect = rarity_surface.get_rect(centerx=overlay_width//2, y=rarity_y)
            rarity_colors = {
                'Commun': COLORS['gray'],
                'Peu Commun': COLORS['green'],
                'Rare': COLORS['royal_blue'],
                'Épique': COLORS['crimson'],
                'Héros': COLORS['orange'],
                'Mythique': COLORS['gold'],
                'Spécial': COLORS['cyan'],
                'commun': COLORS['gray'],
                'peu commun': COLORS['green'],
                'rare': COLORS['royal_blue'],
                'épique': COLORS['crimson'],
                'héros': COLORS['orange'],
                'mythique': COLORS['gold'],
                'spécial': COLORS['cyan'],
            }
            rarity_color = rarity_colors.get(rarity_text.lower(), COLORS['white'])
            oval_width = rarity_rect.width + 40
            oval_height = rarity_rect.height + 16
            oval_rect = pygame.Rect(rarity_rect.centerx - oval_width//2, rarity_rect.centery - oval_height//2, oval_width, oval_height)
            pygame.draw.ellipse(overlay_surface, (*COLORS['deep_black'], 200), oval_rect)
            overlay_surface.blit(rarity_surface, rarity_rect)

        # Stats secondaires - plus grande police
        secondary_stats_y = rarity_y - 40 - int(overlay_height * 0.01)
        secondary_stats = []
        if 'crit_pct' in hero:
            secondary_stats.append(f"Crit: {hero['crit_pct']}%")
        if 'esquive_pct' in hero:
            secondary_stats.append(f"Esq: {hero['esquive_pct']}%")
        if 'blocage_pct' in hero:
            secondary_stats.append(f"Bloc: {hero['blocage_pct']}%")
        if 'precision_pct' in hero:
            secondary_stats.append(f"Préc: {hero['precision_pct']}%")
        if secondary_stats:
            secondary_stats_text = " | ".join(secondary_stats)
            secondary_stats_surface = self.get_cached_font(24).render(secondary_stats_text, True, COLORS['light_blue'])
            secondary_stats_rect = secondary_stats_surface.get_rect(centerx=overlay_width//2, y=secondary_stats_y)
            secondary_stats_bg_rect = pygame.Rect(secondary_stats_rect.x - 10, secondary_stats_rect.y - 4, secondary_stats_rect.width + 20, secondary_stats_rect.height + 8)
            pygame.draw.rect(overlay_surface, (*COLORS['deep_black'], 200), secondary_stats_bg_rect, border_radius=10)
            overlay_surface.blit(secondary_stats_surface, secondary_stats_rect)

        # Stats primaires - plus grande police
        primary_stats_y = secondary_stats_y - 40
        hp = hero.get('hp', hero.get('base_stats', {}).get('hp', 0))
        attack = hero.get('attack', hero.get('base_stats', {}).get('attack', 0))
        defense = hero.get('defense', hero.get('base_stats', {}).get('defense', 0))
        stats_text = f"HP: {hp} | ATK: {attack} | DEF: {defense}"
        stats_surface = self.get_cached_font(28).render(stats_text, True, COLORS['light_gold'])
        stats_rect = stats_surface.get_rect(centerx=overlay_width//2, y=primary_stats_y)
        stats_bg_rect = pygame.Rect(stats_rect.x - 10, stats_rect.y - 4, stats_rect.width + 20, stats_rect.height + 8)
        pygame.draw.rect(overlay_surface, (*COLORS['deep_black'], 200), stats_bg_rect, border_radius=10)
        overlay_surface.blit(stats_surface, stats_rect)

        # Capacité dynamique selon le choix de l'utilisateur
        ability_y = overlay_height - int(overlay_height * 0.40)
        if self.customization and self.customization.use_hero_ability:
            # Capacité du héros
            if 'ability_name' in hero and hero['ability_name']:
                ability_name = hero['ability_name']
                if len(ability_name) > 40:
                    ability_name = ability_name[:37] + "..."
                cooldown = hero.get('ability_cooldown', 0)
                ability_color = COLORS['crimson'] if cooldown > 0 else (0, 255, 0)
                ability_surface = self.get_cached_font(28).render(ability_name, True, ability_color)
                ability_rect = ability_surface.get_rect(centerx=overlay_width//2, y=ability_y)
                ability_bg_rect = pygame.Rect(ability_rect.x - 10, ability_rect.y - 4, ability_rect.width + 20, ability_rect.height + 8)
                pygame.draw.rect(overlay_surface, (*COLORS['deep_black'], 200), ability_bg_rect, border_radius=10)
                overlay_surface.blit(ability_surface, ability_rect)
                
                # Cooldown
                cooldown_text = str(cooldown)
                cooldown_surface = self.get_cached_font(28).render(cooldown_text, True, ability_color)
                cooldown_rect = cooldown_surface.get_rect(midleft=(ability_rect.right + 10, ability_rect.centery))
                cooldown_bg_rect = pygame.Rect(cooldown_rect.x - 6, cooldown_rect.y - 4, cooldown_rect.width + 12, cooldown_rect.height + 8)
                pygame.draw.rect(overlay_surface, (*COLORS['deep_black'], 200), cooldown_bg_rect, border_radius=6)
                overlay_surface.blit(cooldown_surface, cooldown_rect)
        else:
            # Attaque basique
            ability_name = "Attaque basique"
            basic_cooldown = hero.get('basic_attack_cooldown', 1)
            ability_color = (0, 255, 0) if basic_cooldown == 0 else COLORS['crimson']
            ability_surface = self.get_cached_font(28).render(ability_name, True, ability_color)
            ability_rect = ability_surface.get_rect(centerx=overlay_width//2, y=ability_y)
            ability_bg_rect = pygame.Rect(ability_rect.x - 10, ability_rect.y - 4, ability_rect.width + 10, ability_rect.height + 4)
            pygame.draw.rect(overlay_surface, (*COLORS['deep_black'], 200), ability_bg_rect, border_radius=10)
            overlay_surface.blit(ability_surface, ability_rect)
            cooldown_text = str(basic_cooldown)
            cooldown_surface = self.get_cached_font(28).render(cooldown_text, True, ability_color)
            cooldown_rect = cooldown_surface.get_rect(midleft=(ability_rect.right + 10, ability_rect.centery))
            cooldown_bg_rect = pygame.Rect(cooldown_rect.x - 6, cooldown_rect.y - 4, cooldown_rect.width + 12, cooldown_rect.height + 4)
            pygame.draw.rect(overlay_surface, (*COLORS['deep_black'], 200), cooldown_bg_rect, border_radius=6)
            overlay_surface.blit(cooldown_surface, cooldown_rect)

        # Affichage du passif (si activé)
        if self.customization and self.customization.has_passive:
            passive_y = ability_y + 50
            passive_text = "Passif Activé"
            passive_color = COLORS['purple']
            passive_surface = self.get_cached_font(24).render(passive_text, True, passive_color)
            passive_rect = passive_surface.get_rect(centerx=overlay_width//2, y=passive_y)
            passive_bg_rect = pygame.Rect(passive_rect.x - 10, passive_rect.y - 4, passive_rect.width + 20, passive_rect.height + 8)
            pygame.draw.rect(overlay_surface, (*COLORS['deep_black'], 200), passive_bg_rect, border_radius=10)
            overlay_surface.blit(passive_surface, passive_rect)

        return overlay_surface
    def create_hover_unit_overlay(self, unit, border_color):
        """Crée l'overlay de hover pour une unité avec image et descriptions sur le côté"""
        # Taille de l'overlay (80% de l'écran)
        overlay_width = int(SCREEN_WIDTH * 0.8)
        overlay_height = int(SCREEN_HEIGHT * 0.8)
        
        # Créer la surface avec transparence
        overlay_surface = pygame.Surface((overlay_width, overlay_height), pygame.SRCALPHA)
        
        # Fond semi-transparent
        pygame.draw.rect(overlay_surface, (*COLORS['deep_black'], 230), (0, 0, overlay_width, overlay_height), border_radius=20)
        
        # Bordure colorée
        pygame.draw.rect(overlay_surface, border_color, (0, 0, overlay_width, overlay_height), 4, border_radius=20)
        
        # Diviser l'overlay en deux parties : image à gauche, descriptions à droite
        image_width = int(overlay_width * 0.4)  # 40% pour l'image
        desc_width = overlay_width - image_width - 40  # 60% pour les descriptions
        margin = 20
        
        # Zone de l'image (centrée à gauche)
        image_x = margin
        image_y = margin
        image_height = overlay_height - 2 * margin
        
        # Charger et afficher l'image de l'unité
        if 'image_path' in unit:
            unit_image = self.game_ui.asset_manager.get_image(unit['image_path'])
            if unit_image:
                # Redimensionner l'image pour s'adapter à la zone
                scaled_image = pygame.transform.scale(unit_image, (image_width, image_height))
                
                # Créer une surface avec coins arrondis pour l'image
                image_surface = pygame.Surface((image_width, image_height), pygame.SRCALPHA)
                
                # Créer un masque avec coins arrondis précis
                mask_surface = self.create_rounded_mask(image_width, image_height, 20)
                
                # Appliquer le masque à l'image
                image_surface.blit(scaled_image, (0, 0))
                image_surface.blit(mask_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                
                overlay_surface.blit(image_surface, (image_x, image_y))
            else:
                # Image par défaut si pas trouvée
                default_surface = pygame.Surface((image_width, image_height))
                default_surface.fill(COLORS['dark_gray'])
                overlay_surface.blit(default_surface, (image_x, image_y))
        
        # Zone des descriptions (à droite)
        desc_x = image_x + image_width + 20
        desc_y = margin + 20
        y_offset = desc_y
        
        # Nom de l'unité
        name_text = unit['name']
        name_surface = self.get_cached_font(36).render(name_text, True, COLORS['white'])
        name_rect = name_surface.get_rect(topleft=(desc_x, y_offset))
        
        # Fond pour le nom
        name_bg_rect = pygame.Rect(name_rect.x - 10, name_rect.y - 5, name_rect.width + 20, name_rect.height + 10)
        pygame.draw.rect(overlay_surface, (*COLORS['deep_black'], 200), name_bg_rect, border_radius=8)
        overlay_surface.blit(name_surface, name_rect)
        y_offset += 60
        
        # Élément avec symbole
        if 'element' in unit and unit['element']:
            # Mapping des noms d'éléments vers les noms de fichiers
            element_mapping = {
                'feu': 'feu',
                'eau': 'eau',
                'glace': 'glace',
                'terre': 'terre',
                'air': 'air',
                'foudre': 'foudre',
                'lumière': 'lumiere',
                'ténèbres': 'tenebres',
                'arcanique': 'arcane',
                'poison': 'poison',
                'néant': 'neant'
            }
            
            element_name = unit['element'].lower()
            file_name = element_mapping.get(element_name, element_name)
            element_symbol_path = f"Symbols/{file_name}.png"
            element_symbol = self.game_ui.asset_manager.get_image(element_symbol_path)
            
            if element_symbol:
                # Afficher le symbole d'élément
                symbol_size = (48, 48)
                scaled_symbol = pygame.transform.scale(element_symbol, symbol_size)
                symbol_rect = scaled_symbol.get_rect(topleft=(desc_x, y_offset))
                
                # Fond pour le symbole
                symbol_bg_rect = pygame.Rect(symbol_rect.x - 5, symbol_rect.y - 5, symbol_rect.width + 10, symbol_rect.height + 10)
                pygame.draw.rect(overlay_surface, (*COLORS['deep_black'], 200), symbol_bg_rect, border_radius=8)
                overlay_surface.blit(scaled_symbol, symbol_rect)
            else:
                # Fallback vers le texte si le symbole n'est pas trouvé
                element_text = f"Élément: {unit['element']}"
                element_surface = self.get_cached_font(24).render(element_text, True, COLORS['light_gold'])
                element_rect = element_surface.get_rect(topleft=(desc_x, y_offset))
                
                # Fond pour le texte d'élément
                element_bg_rect = pygame.Rect(element_rect.x - 10, element_rect.y - 5, element_rect.width + 20, element_rect.height + 10)
                pygame.draw.rect(overlay_surface, (*COLORS['deep_black'], 200), element_bg_rect, border_radius=8)
                overlay_surface.blit(element_surface, element_rect)
            y_offset += 60
        
        # Rareté
        if 'rarity' in unit:
            rarity_text = f"Rareté: {unit['rarity']}"
            rarity_surface = self.get_cached_font(24).render(rarity_text, True, COLORS['light_gold'])
            rarity_rect = rarity_surface.get_rect(topleft=(desc_x, y_offset))
            
            # Fond pour la rareté
            rarity_bg_rect = pygame.Rect(rarity_rect.x - 10, rarity_rect.y - 5, rarity_rect.width + 20, rarity_rect.height + 10)
            pygame.draw.rect(overlay_surface, (*COLORS['deep_black'], 200), rarity_bg_rect, border_radius=8)
            overlay_surface.blit(rarity_surface, rarity_rect)
            y_offset += 40
        
        # Stats
        stats_text = f"HP: {unit['hp']} | ATK: {unit['attack']} | DEF: {unit['defense']}"
        stats_surface = self.get_cached_font(24).render(stats_text, True, COLORS['light_gold'])
        stats_rect = stats_surface.get_rect(topleft=(desc_x, y_offset))
        
        # Fond pour les stats
        stats_bg_rect = pygame.Rect(stats_rect.x - 10, stats_rect.y - 5, stats_rect.width + 20, stats_rect.height + 10)
        pygame.draw.rect(overlay_surface, (*COLORS['deep_black'], 200), stats_bg_rect, border_radius=8)
        overlay_surface.blit(stats_surface, stats_rect)
        y_offset += 40
        
        # Stats secondaires
        secondary_stats = []
        if 'crit_pct' in unit:
            secondary_stats.append(f"Crit: {unit['crit_pct']}%")
        if 'esquive_pct' in unit:
            secondary_stats.append(f"Esq: {unit['esquive_pct']}%")
        if 'precision_pct' in unit:
            secondary_stats.append(f"Préc: {unit['precision_pct']}%")
        
        if secondary_stats:
            secondary_stats_text = " | ".join(secondary_stats)
            secondary_stats_surface = self.get_cached_font(20).render(secondary_stats_text, True, COLORS['light_blue'])
            secondary_stats_rect = secondary_stats_surface.get_rect(topleft=(desc_x, y_offset))
            
            # Fond pour les stats secondaires
            secondary_stats_bg_rect = pygame.Rect(secondary_stats_rect.x - 10, secondary_stats_rect.y - 5, secondary_stats_rect.width + 20, secondary_stats_rect.height + 10)
            pygame.draw.rect(overlay_surface, (*COLORS['deep_black'], 200), secondary_stats_bg_rect, border_radius=8)
            overlay_surface.blit(secondary_stats_surface, secondary_stats_rect)
            y_offset += 40
        
        # Capacité
        if 'ability_name' in unit and unit['ability_name']:
            ability_name = unit['ability_name']
            ability_surface = self.get_cached_font(28).render(ability_name, True, COLORS['crimson'])
            ability_rect = ability_surface.get_rect(topleft=(desc_x, y_offset))
            
            # Fond pour la capacité
            ability_bg_rect = pygame.Rect(ability_rect.x - 10, ability_rect.y - 5, ability_rect.width + 20, ability_rect.height + 10)
            pygame.draw.rect(overlay_surface, (*COLORS['deep_black'], 200), ability_bg_rect, border_radius=8)
            overlay_surface.blit(ability_surface, ability_rect)
            y_offset += 40
        
        # Cooldown
        if 'cooldown' in unit and unit['cooldown'] > 0:
            cooldown_text = f"Cooldown: {unit['cooldown']}"
            cooldown_surface = self.get_cached_font(24).render(cooldown_text, True, COLORS['light_blue'])
            cooldown_rect = cooldown_surface.get_rect(topleft=(desc_x, y_offset))
            
            # Fond pour le cooldown
            cooldown_bg_rect = pygame.Rect(cooldown_rect.x - 10, cooldown_rect.y - 5, cooldown_rect.width + 20, cooldown_rect.height + 10)
            pygame.draw.rect(overlay_surface, (*COLORS['deep_black'], 200), cooldown_bg_rect, border_radius=8)
            overlay_surface.blit(cooldown_surface, cooldown_rect)
            y_offset += 40
        
        # Description (mode compacte)
        if 'description' in unit and unit['description']:
            description = unit['description']
            lines = self.smart_wrap_text(description, self.get_cached_font(36), desc_width - 20)
            
            # Afficher les lignes (limitées à 6 lignes)
            for i, line in enumerate(lines[:6]):
                desc_surface = self.get_cached_font(36).render(line, True, COLORS['white'])
                desc_rect = desc_surface.get_rect(topleft=(desc_x, y_offset))
                
                # Fond pour chaque ligne de description
                desc_bg_rect = pygame.Rect(desc_rect.x - 5, desc_rect.y - 2, desc_rect.width + 10, desc_rect.height + 4)
                pygame.draw.rect(overlay_surface, (*COLORS['deep_black'], 200), desc_bg_rect, border_radius=5)
                overlay_surface.blit(desc_surface, desc_rect)
                y_offset += 50
            
            if len(lines) > 6:
                more_text = "..."
                more_surface = self.get_cached_font(36).render(more_text, True, COLORS['gray'])
                more_rect = more_surface.get_rect(topleft=(desc_x, y_offset))
                
                # Fond pour le texte "..."
                more_bg_rect = pygame.Rect(more_rect.x - 5, more_rect.y - 2, more_rect.width + 10, more_rect.height + 4)
                pygame.draw.rect(overlay_surface, (*COLORS['deep_black'], 200), more_bg_rect, border_radius=5)
                overlay_surface.blit(more_surface, more_rect)
        
        return overlay_surface
    
    def create_hover_card_overlay(self, card, border_color):
        """Crée l'overlay de hover pour une carte avec image et descriptions sur le côté"""
        # Taille de l'overlay (80% de l'écran)
        overlay_width = int(SCREEN_WIDTH * 0.8)
        overlay_height = int(SCREEN_HEIGHT * 0.8)
        
        # Créer la surface avec transparence
        overlay_surface = pygame.Surface((overlay_width, overlay_height), pygame.SRCALPHA)
        
        # Fond semi-transparent
        pygame.draw.rect(overlay_surface, (*COLORS['deep_black'], 230), (0, 0, overlay_width, overlay_height), border_radius=20)
        
        # Bordure colorée
        pygame.draw.rect(overlay_surface, border_color, (0, 0, overlay_width, overlay_height), 4, border_radius=20)
        
        # Diviser l'overlay en deux parties : image à gauche, descriptions à droite
        image_width = int(overlay_width * 0.4)  # 40% pour l'image
        desc_width = overlay_width - image_width - 40  # 60% pour les descriptions
        margin = 20
        
        # Zone de l'image (centrée à gauche)
        image_x = margin
        image_y = margin
        image_height = overlay_height - 2 * margin
        
        # Charger et afficher l'image de la carte
        if 'image_path' in card:
            card_image = self.game_ui.asset_manager.get_image(card['image_path'])
            if card_image:
                # Redimensionner l'image pour s'adapter à la zone
                scaled_image = pygame.transform.scale(card_image, (image_width, image_height))
                
                # Créer une surface avec coins arrondis pour l'image
                image_surface = pygame.Surface((image_width, image_height), pygame.SRCALPHA)
                
                # Créer un masque avec coins arrondis précis
                mask_surface = self.create_rounded_mask(image_width, image_height, 20)
                
                # Appliquer le masque à l'image
                image_surface.blit(scaled_image, (0, 0))
                image_surface.blit(mask_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                
                overlay_surface.blit(image_surface, (image_x, image_y))
        else:
                # Image par défaut si pas trouvée
                default_surface = pygame.Surface((image_width, image_height))
                default_surface.fill(COLORS['dark_gray'])
                overlay_surface.blit(default_surface, (image_x, image_y))
        
        # Zone des descriptions (à droite)
        desc_x = image_x + image_width + 20
        desc_y = margin + 20
        y_offset = desc_y
        
        # Nom de la carte
        name_text = card['name']
        name_surface = self.get_cached_font(36).render(name_text, True, COLORS['white'])
        name_rect = name_surface.get_rect(topleft=(desc_x, y_offset))
        
        # Fond pour le nom
        name_bg_rect = pygame.Rect(name_rect.x - 10, name_rect.y - 5, name_rect.width + 20, name_rect.height + 10)
        pygame.draw.rect(overlay_surface, (*COLORS['deep_black'], 200), name_bg_rect, border_radius=8)
        overlay_surface.blit(name_surface, name_rect)
        y_offset += 60
        
        # Type de carte
        if 'type' in card:
            type_text = f"Type: {card['type']}"
            type_surface = self.get_cached_font(24).render(type_text, True, COLORS['light_gold'])
            type_rect = type_surface.get_rect(topleft=(desc_x, y_offset))
            
            # Fond pour le type
            type_bg_rect = pygame.Rect(type_rect.x - 10, type_rect.y - 5, type_rect.width + 20, type_rect.height + 10)
            pygame.draw.rect(overlay_surface, (*COLORS['deep_black'], 200), type_bg_rect, border_radius=8)
            overlay_surface.blit(type_surface, type_rect)
            y_offset += 40
        
        # Coût en mana
        if 'cost' in card:
            cost_text = f"Coût: {card['cost']} mana"
            cost_surface = self.get_cached_font(24).render(cost_text, True, COLORS['light_blue'])
            cost_rect = cost_surface.get_rect(topleft=(desc_x, y_offset))
            
            # Fond pour le coût
            cost_bg_rect = pygame.Rect(cost_rect.x - 10, cost_rect.y - 5, cost_rect.width + 20, cost_rect.height + 10)
            pygame.draw.rect(overlay_surface, (*COLORS['deep_black'], 200), cost_bg_rect, border_radius=8)
            overlay_surface.blit(cost_surface, cost_rect)
            y_offset += 40
        
        # Élément avec symbole
        if 'element' in card and card['element']:
            # Mapping des noms d'éléments vers les noms de fichiers
            element_mapping = {
                'feu': 'feu',
                'eau': 'eau',
                'glace': 'glace',
                'terre': 'terre',
                'air': 'air',
                'foudre': 'foudre',
                'lumière': 'lumiere',
                'ténèbres': 'tenebres',
                'arcanique': 'arcane',
                'poison': 'poison',
                'néant': 'neant'
            }
            
            element_name = card['element'].lower()
            file_name = element_mapping.get(element_name, element_name)
            element_symbol_path = f"Symbols/{file_name}.png"
            element_symbol = self.game_ui.asset_manager.get_image(element_symbol_path)
            
            if element_symbol:
                # Afficher le symbole d'élément
                symbol_size = (48, 48)
                scaled_symbol = pygame.transform.scale(element_symbol, symbol_size)
                symbol_rect = scaled_symbol.get_rect(topleft=(desc_x, y_offset))
                
                # Fond pour le symbole
                symbol_bg_rect = pygame.Rect(symbol_rect.x - 5, symbol_rect.y - 5, symbol_rect.width + 10, symbol_rect.height + 10)
                pygame.draw.rect(overlay_surface, (*COLORS['deep_black'], 200), symbol_bg_rect, border_radius=8)
                overlay_surface.blit(scaled_symbol, symbol_rect)
            else:
                # Fallback vers le texte si le symbole n'est pas trouvé
                element_text = f"Élément: {card['element']}"
                element_surface = self.get_cached_font(24).render(element_text, True, COLORS['light_gold'])
                element_rect = element_surface.get_rect(topleft=(desc_x, y_offset))
                
                # Fond pour le texte d'élément
                element_bg_rect = pygame.Rect(element_rect.x - 10, element_rect.y - 5, element_rect.width + 20, element_rect.height + 10)
                pygame.draw.rect(overlay_surface, (*COLORS['deep_black'], 200), element_bg_rect, border_radius=8)
                overlay_surface.blit(element_surface, element_rect)
            y_offset += 60
        
        # Rareté (si applicable)
        if 'rarity' in card:
            rarity_text = f"Rareté: {card['rarity']}"
            rarity_surface = self.get_cached_font(24).render(rarity_text, True, COLORS['light_gold'])
            rarity_rect = rarity_surface.get_rect(topleft=(desc_x, y_offset))
            
            # Fond pour la rareté
            rarity_bg_rect = pygame.Rect(rarity_rect.x - 10, rarity_rect.y - 5, rarity_rect.width + 20, rarity_rect.height + 10)
            pygame.draw.rect(overlay_surface, (*COLORS['deep_black'], 200), rarity_bg_rect, border_radius=8)
            overlay_surface.blit(rarity_surface, rarity_rect)
            y_offset += 40
        
        # Description (mode compacte)
        if 'description' in card and card['description']:
            description = card['description']
            lines = self.smart_wrap_text(description, self.get_cached_font(36), desc_width - 20)
            
            # Afficher les lignes (limitées à 8 lignes pour les cartes)
            for i, line in enumerate(lines[:8]):
                desc_surface = self.get_cached_font(36).render(line, True, COLORS['white'])
                desc_rect = desc_surface.get_rect(topleft=(desc_x, y_offset))
                
                # Fond pour chaque ligne de description
                desc_bg_rect = pygame.Rect(desc_rect.x - 5, desc_rect.y - 2, desc_rect.width + 10, desc_rect.height + 4)
                pygame.draw.rect(overlay_surface, (*COLORS['deep_black'], 200), desc_bg_rect, border_radius=5)
                overlay_surface.blit(desc_surface, desc_rect)
                y_offset += 50
            
            if len(lines) > 8:
                more_text = "..."
                more_surface = self.get_cached_font(36).render(more_text, True, COLORS['gray'])
                more_rect = more_surface.get_rect(topleft=(desc_x, y_offset))
                
                # Fond pour le texte "..."
                more_bg_rect = pygame.Rect(more_rect.x - 5, more_rect.y - 2, more_rect.width + 10, more_rect.height + 4)
                pygame.draw.rect(overlay_surface, (*COLORS['deep_black'], 200), more_bg_rect, border_radius=5)
                overlay_surface.blit(more_surface, more_rect)
            y_offset += 20
        
        # Effets détaillés (si disponibles)
        if 'effects' in card and card['effects']:
            effects_title = "Effets:"
            effects_title_surface = self.get_cached_font(28).render(effects_title, True, COLORS['crimson'])
            effects_title_rect = effects_title_surface.get_rect(topleft=(desc_x, y_offset))
            
            # Fond pour le titre des effets
            effects_title_bg_rect = pygame.Rect(effects_title_rect.x - 10, effects_title_rect.y - 5, effects_title_rect.width + 20, effects_title_rect.height + 10)
            pygame.draw.rect(overlay_surface, (*COLORS['deep_black'], 200), effects_title_bg_rect, border_radius=8)
            overlay_surface.blit(effects_title_surface, effects_title_rect)
            y_offset += 40
            
            # Afficher chaque effet
            for i, effect in enumerate(card['effects'][:4]):  # Limiter à 4 effets
                effect_text = f"• {effect.get('type', 'Effet')}: {effect.get('amount', 'N/A')}"
                if 'target' in effect:
                    effect_text += f" → {effect['target']}"
                if 'duration' in effect:
                    effect_text += f" ({effect['duration']} tours)"
                
                effect_surface = self.get_cached_font(20).render(effect_text, True, COLORS['light_blue'])
                effect_rect = effect_surface.get_rect(topleft=(desc_x, y_offset))
                
                # Fond pour chaque effet
                effect_bg_rect = pygame.Rect(effect_rect.x - 5, effect_rect.y - 2, effect_rect.width + 10, effect_rect.height + 4)
                pygame.draw.rect(overlay_surface, (*COLORS['deep_black'], 200), effect_bg_rect, border_radius=5)
                overlay_surface.blit(effect_surface, effect_rect)
                y_offset += 30
        
        return overlay_surface

    def create_unit_overlay_surface(self, unit):
        """Crée une surface d'overlay pour une unité avec le même style que les héros"""
        # Taille de l'overlay (même que les héros)
        overlay_width = 400
        overlay_height = 576
        overlay_surface = pygame.Surface((overlay_width, overlay_height), pygame.SRCALPHA)
        
        # Bordure colorée
        pygame.draw.rect(overlay_surface, COLORS['royal_blue'], (0, 0, overlay_width, overlay_height), 4, border_radius=20)
        
        # Nom (avant la virgule) - police plus grande
        name_text = unit['name'].split(',')[0].strip()
        name_y = int(overlay_height * 0.08)
        name_surface = self.get_cached_font(44).render(name_text, True, COLORS['white'])
        name_rect = name_surface.get_rect(centerx=overlay_width//2, y=name_y)
        name_bg_rect = pygame.Rect(name_rect.x - 10, name_rect.y - 4, name_rect.width + 20, name_rect.height + 8)
        pygame.draw.rect(overlay_surface, (*COLORS['deep_black'], 200), name_bg_rect, border_radius=10)
        overlay_surface.blit(name_surface, name_rect)
        
        # Élément (symbole) - plus grand
        if 'element' in unit and unit['element']:
            element_mapping = {
                'feu': 'feu', 'eau': 'eau', 'glace': 'glace', 'terre': 'terre', 'air': 'air',
                'foudre': 'foudre', 'lumière': 'lumiere', 'ténèbres': 'tenebres', 'arcanique': 'arcane',
                'poison': 'poison', 'néant': 'neant'
            }
            element_name = unit['element'].lower()
            file_name = element_mapping.get(element_name, element_name)
            element_symbol_path = f"Symbols/{file_name}.png"
            element_symbol = self.game_ui.asset_manager.get_image(element_symbol_path)
            if element_symbol:
                symbol_size = (48, 48)  # Plus grand symbole
                scaled_symbol = pygame.transform.scale(element_symbol, symbol_size)
                symbol_rect = scaled_symbol.get_rect(topleft=(20, 20))
                circle_radius = 30  # Plus grand cercle
                circle_center = (symbol_rect.centerx, symbol_rect.centery)
                pygame.draw.circle(overlay_surface, (*COLORS['deep_black'], 200), circle_center, circle_radius)
                overlay_surface.blit(scaled_symbol, symbol_rect)
            else:
                element_text = f"Élément: {unit['element']}"
                element_surface = self.get_cached_font(24).render(element_text, True, COLORS['light_gold'])
                element_rect = element_surface.get_rect(topleft=(20, 20))
                circle_radius = 30
                circle_center = (element_rect.centerx, element_rect.centery)
                pygame.draw.circle(overlay_surface, (*COLORS['deep_black'], 200), circle_center, circle_radius)
                overlay_surface.blit(element_surface, element_rect)
        
        # Rareté - plus grande police
        rarity_y = overlay_height - 60
        if 'rarity' in unit:
            rarity_text = unit['rarity']
            rarity_surface = self.get_cached_font(22).render(rarity_text, True, COLORS['white'])
            rarity_rect = rarity_surface.get_rect(centerx=overlay_width//2, y=rarity_y)
            rarity_colors = {
                'Commun': COLORS['gray'],
                'Peu Commun': COLORS['green'],
                'Rare': COLORS['royal_blue'],
                'Épique': COLORS['crimson'],
                'Héros': COLORS['orange'],
                'Mythique': COLORS['gold'],
                'Spécial': COLORS['cyan'],
                'commun': COLORS['gray'],
                'peu commun': COLORS['green'],
                'rare': COLORS['royal_blue'],
                'épique': COLORS['crimson'],
                'héros': COLORS['orange'],
                'mythique': COLORS['gold'],
                'spécial': COLORS['cyan'],
            }
            rarity_color = rarity_colors.get(rarity_text.lower(), COLORS['white'])
            oval_width = rarity_rect.width + 40
            oval_height = rarity_rect.height + 16
            oval_rect = pygame.Rect(rarity_rect.centerx - oval_width//2, rarity_rect.centery - oval_height//2, oval_width, oval_height)
            pygame.draw.ellipse(overlay_surface, (*COLORS['deep_black'], 200), oval_rect)
            overlay_surface.blit(rarity_surface, rarity_rect)
        
        # Stats secondaires - plus grande police
        secondary_stats_y = rarity_y - 40 - int(overlay_height * 0.01)
        secondary_stats = []
        if 'crit_pct' in unit:
            secondary_stats.append(f"Crit: {unit['crit_pct']}%")
        if 'esquive_pct' in unit:
            secondary_stats.append(f"Esq: {unit['esquive_pct']}%")
        if 'precision_pct' in unit:
            secondary_stats.append(f"Préc: {unit['precision_pct']}%")
        if secondary_stats:
            secondary_stats_text = " | ".join(secondary_stats)
            secondary_stats_surface = self.get_cached_font(24).render(secondary_stats_text, True, COLORS['light_blue'])
            secondary_stats_rect = secondary_stats_surface.get_rect(centerx=overlay_width//2, y=secondary_stats_y)
            secondary_stats_bg_rect = pygame.Rect(secondary_stats_rect.x - 10, secondary_stats_rect.y - 4, secondary_stats_rect.width + 20, secondary_stats_rect.height + 8)
            pygame.draw.rect(overlay_surface, (*COLORS['deep_black'], 200), secondary_stats_bg_rect, border_radius=10)
            overlay_surface.blit(secondary_stats_surface, secondary_stats_rect)
        
        # Stats primaires - plus grande police
        primary_stats_y = secondary_stats_y - 40
        hp = unit.get('hp', 0)
        attack = unit.get('attack', 0)
        defense = unit.get('defense', 0)
        stats_text = f"HP: {hp} | ATK: {attack} | DEF: {defense}"
        stats_surface = self.get_cached_font(28).render(stats_text, True, COLORS['light_gold'])
        stats_rect = stats_surface.get_rect(centerx=overlay_width//2, y=primary_stats_y)
        stats_bg_rect = pygame.Rect(stats_rect.x - 10, stats_rect.y - 4, stats_rect.width + 20, stats_rect.height + 8)
        pygame.draw.rect(overlay_surface, (*COLORS['deep_black'], 200), stats_bg_rect, border_radius=10)
        overlay_surface.blit(stats_surface, stats_rect)
        
        # Capacités (liste) – centrer autour de la position de référence
        ability_y_center = overlay_height - int(overlay_height * 0.40)
        names = []
        ability_elements = []
        if 'ability_ids' in unit and unit['ability_ids']:
            try:
                effects_mgr = EffectsDatabaseManager()
                for aid in unit['ability_ids']:
                    data = effects_mgr.get_ability(str(aid))
                    names.append(data.get('name') if data else f"Capacité {aid}")
                    ability_elements.append(data.get('element', '1') if data else '1')
            except Exception:
                pass
        if not names and unit.get('description'):
            names = [unit['description']]
            ability_elements = ['1']  # Par défaut feu
        if names:
            font = self.get_cached_font(22)
            line_h = font.get_height()
            spacing = 6
            total_h = len(names) * line_h + max(0, (len(names) - 1) * spacing)
            start_y = int(ability_y_center - total_h / 2)
            
            # Mappage des éléments pour les symboles
            element_mapping = {
                '1': 'feu', '2': 'eau', '3': 'terre', '4': 'air', '5': 'glace',
                '6': 'foudre', '7': 'lumière', '8': 'ténèbres', '9': 'arcanique',
                '10': 'poison', '11': 'néant', '12': 'néant'
            }
            
            for idx, name in enumerate(names):
                text = name if len(name) <= 40 else (name[:37] + '...')
                line_y = start_y + idx * (line_h + spacing)
                
                # Récupérer l'élément de la capacité
                ability_element = ability_elements[idx] if idx < len(ability_elements) else '1'
                element_name = element_mapping.get(str(ability_element), 'feu')
                element_symbol_path = f"Symbols/{element_name}.png"
                element_symbol = self.game_ui.asset_manager.get_image(element_symbol_path)
                
                # Calculer la largeur totale de la ligne (symbole + nom)
                symbol_size = (12, 12)
                surf = font.render(text, True, COLORS['white'])
                
                # Largeurs des éléments
                symbol_width = 12
                text_width = surf.get_width()
                spacing = 6  # Espace entre les éléments
                
                # Largeur totale de la ligne
                total_line_width = symbol_width + spacing + text_width
                
                # Position de départ pour centrer toute la ligne
                line_start_x = (overlay_width - total_line_width) // 2
                
                # Positions des éléments
                symbol_x = line_start_x
                text_x = symbol_x + symbol_width + spacing
                
                # Nom de la capacité
                rect = surf.get_rect(x=text_x, y=line_y)
                
                # Fond pour la capacité (élargi pour inclure le symbole)
                bg_rect = pygame.Rect(symbol_x - 2, rect.y - 4, total_line_width + 4, rect.height + 8)
                pygame.draw.rect(overlay_surface, (*COLORS['deep_black'], 200), bg_rect, border_radius=10)
                overlay_surface.blit(surf, rect)
                
                # Afficher le symbole d'élément APRÈS le fond (pour qu'il soit visible)
                if element_symbol:
                        # Afficher le symbole d\'élément (12x12)
                    scaled_symbol = pygame.transform.scale(element_symbol, symbol_size)
                    symbol_y = line_y + (line_h - 12) // 2  # Centrer verticalement
                    symbol_rect = scaled_symbol.get_rect(topleft=(symbol_x, symbol_y))
                    overlay_surface.blit(scaled_symbol, symbol_rect)
        
        return overlay_surface
    
    def create_hero_overlay_surface(self, hero):
        """Crée une surface d'overlay pour un héros (même structure que les unités)"""
        overlay_width = 200
        overlay_height = 288
        overlay_surface = pygame.Surface((overlay_width, overlay_height), pygame.SRCALPHA)
        desc_x = 20

        # Bordure or
        pygame.draw.rect(overlay_surface, COLORS['gold'], (0, 0, overlay_width, overlay_height), 2, border_radius=10)

        # Nom (avant la virgule)
        name_text = hero['name'].split(',')[0].strip()
        name_y = int(overlay_height * 0.08)
        name_surface = self.get_cached_font(22).render(name_text, True, COLORS['white'])
        name_rect = name_surface.get_rect(centerx=overlay_width//2, y=name_y)
        name_bg_rect = pygame.Rect(name_rect.x - 5, name_rect.y - 2, name_rect.width + 10, name_rect.height + 4)
        pygame.draw.rect(overlay_surface, (*COLORS['deep_black'], 200), name_bg_rect, border_radius=5)
        overlay_surface.blit(name_surface, name_rect)

        # Élément (symbole)
        if 'element' in hero and hero['element']:
            element_mapping = {
                'feu': 'feu', 'eau': 'eau', 'glace': 'glace', 'terre': 'terre', 'air': 'air',
                'foudre': 'foudre', 'lumière': 'lumiere', 'ténèbres': 'tenebres', 'arcanique': 'arcane',
                'poison': 'poison', 'néant': 'neant'
            }
            element_name = hero['element'].lower()
            file_name = element_mapping.get(element_name, element_name)
            element_symbol_path = f"Symbols/{file_name}.png"
            element_symbol = self.game_ui.asset_manager.get_image(element_symbol_path)
            if element_symbol:
                symbol_size = (24, 24)
                scaled_symbol = pygame.transform.scale(element_symbol, symbol_size)
                symbol_rect = scaled_symbol.get_rect(topleft=(10, 10))
                circle_radius = 15
                circle_center = (symbol_rect.centerx, symbol_rect.centery)
                pygame.draw.circle(overlay_surface, (*COLORS['deep_black'], 200), circle_center, circle_radius)
                overlay_surface.blit(scaled_symbol, symbol_rect)
            else:
                element_text = f"Élément: {hero['element']}"
                element_surface = self.get_cached_font(12).render(element_text, True, COLORS['light_gold'])
                element_rect = element_surface.get_rect(topleft=(10, 10))
                circle_radius = 15
                circle_center = (element_rect.centerx, element_rect.centery)
                pygame.draw.circle(overlay_surface, (*COLORS['deep_black'], 200), circle_center, circle_radius)
                overlay_surface.blit(element_surface, element_rect)

        # Rareté (mêmes couleurs que unités)
        rarity_y = overlay_height - 30
        if 'rarity' in hero:
            rarity_text = hero['rarity']
            rarity_surface = self.get_cached_font(11).render(rarity_text, True, COLORS['white'])
            rarity_rect = rarity_surface.get_rect(centerx=overlay_width//2, y=rarity_y)
            rarity_colors = {
                'Commun': COLORS['gray'],
                'Peu Commun': COLORS['green'],
                'Rare': COLORS['royal_blue'],
                'Épique': COLORS['crimson'],
                'Héros': COLORS['orange'],
                'Mythique': COLORS['gold'],
                'Spécial': COLORS['cyan'],
                'commun': COLORS['gray'],
                'peu commun': COLORS['green'],
                'rare': COLORS['royal_blue'],
                'épique': COLORS['crimson'],
                'héros': COLORS['orange'],
                'mythique': COLORS['gold'],
                'spécial': COLORS['cyan'],
            }
            rarity_color = rarity_colors.get(rarity_text.lower(), COLORS['white'])
            oval_width = rarity_rect.width + 20
            oval_height = rarity_rect.height + 8
            oval_rect = pygame.Rect(rarity_rect.centerx - oval_width//2, rarity_rect.centery - oval_height//2, oval_width, oval_height)
            pygame.draw.ellipse(overlay_surface, (*COLORS['deep_black'], 200), oval_rect)
            overlay_surface.blit(rarity_surface, rarity_rect)

        # Stats secondaires
        secondary_stats_y = rarity_y - 20 - int(overlay_height * 0.01)
        desc_y = 100
        y_offset = desc_y
        secondary_stats = []
        if 'crit_pct' in hero:
            secondary_stats.append(f"Crit: {hero['crit_pct']}%")
        if 'esquive_pct' in hero:
            secondary_stats.append(f"Esq: {hero['esquive_pct']}%")
        if 'blocage_pct' in hero:
            secondary_stats.append(f"Bloc: {hero['blocage_pct']}%")
        if 'precision_pct' in hero:
            secondary_stats.append(f"Préc: {hero['precision_pct']}%")
        if secondary_stats:
            secondary_stats_text = " | ".join(secondary_stats)
            secondary_stats_surface = self.get_cached_font(12).render(secondary_stats_text, True, COLORS['light_blue'])
            secondary_stats_rect = secondary_stats_surface.get_rect(centerx=overlay_width//2, y=secondary_stats_y)
            secondary_stats_bg_rect = pygame.Rect(secondary_stats_rect.x - 5, secondary_stats_rect.y - 2, secondary_stats_rect.width + 10, secondary_stats_rect.height + 4)
            pygame.draw.rect(overlay_surface, (*COLORS['deep_black'], 200), secondary_stats_bg_rect, border_radius=5)
            overlay_surface.blit(secondary_stats_surface, secondary_stats_rect)

        # Stats primaires
        primary_stats_y = secondary_stats_y - 20
        hp = hero.get('hp', hero.get('base_stats', {}).get('hp', 0))
        attack = hero.get('attack', hero.get('base_stats', {}).get('attack', 0))
        defense = hero.get('defense', hero.get('base_stats', {}).get('defense', 0))
        stats_text = f"HP: {hp} | ATK: {attack} | DEF: {defense}"
        stats_surface = self.get_cached_font(14).render(stats_text, True, COLORS['light_gold'])
        stats_rect = stats_surface.get_rect(centerx=overlay_width//2, y=primary_stats_y)
        stats_bg_rect = pygame.Rect(stats_rect.x - 5, stats_rect.y - 2, stats_rect.width + 10, stats_rect.height + 4)
        pygame.draw.rect(overlay_surface, (*COLORS['deep_black'], 200), stats_bg_rect, border_radius=5)
        overlay_surface.blit(stats_surface, stats_rect)

        # Capacité (nom + cooldown, couleur verte si utilisable)
        ability_y = overlay_height - int(overlay_height * 0.40)
        
        # Récupérer la personnalisation du héros si elle existe
        hero_name = hero.get("name", "Héros inconnu")
        customization = None
        try:
            from Engine.hero_customization_manager import hero_customization_manager
            if hero_customization_manager:
                customization = hero_customization_manager.get_customization(hero_name)
        except:
            pass
        
        # Déterminer quelle capacité afficher selon la personnalisation
        if customization and customization.use_hero_ability:
            # Capacité du héros
            if 'ability_name' in hero and hero['ability_name']:
                ability_name = hero['ability_name']
                if len(ability_name) > 30:
                    ability_name = ability_name[:27] + "..."
                cooldown = hero.get('ability_cooldown', 0)
                ability_color = COLORS['crimson'] if cooldown > 0 else (0, 255, 0)
                ability_surface = self.get_cached_font(14).render(ability_name, True, ability_color)
                ability_rect = ability_surface.get_rect(centerx=overlay_width//2, y=ability_y)
                ability_bg_rect = pygame.Rect(ability_rect.x - 5, ability_rect.y - 2, ability_rect.width + 10, ability_rect.height + 4)
                pygame.draw.rect(overlay_surface, (*COLORS['deep_black'], 200), ability_bg_rect, border_radius=5)
                overlay_surface.blit(ability_surface, ability_rect)
                cooldown_text = str(cooldown)
                cooldown_surface = self.get_cached_font(14).render(cooldown_text, True, ability_color)
                cooldown_rect = cooldown_surface.get_rect(midleft=(ability_rect.right + 5, ability_rect.centery))
                cooldown_bg_rect = pygame.Rect(cooldown_rect.x - 3, cooldown_rect.y - 2, cooldown_rect.width + 6, cooldown_rect.height + 4)
                pygame.draw.rect(overlay_surface, (*COLORS['deep_black'], 200), cooldown_bg_rect, border_radius=3)
                overlay_surface.blit(cooldown_surface, cooldown_rect)
        else:
            # Attaque basique
            ability_name = "Attaque basique"
            basic_cooldown = hero.get('basic_attack_cooldown', 1)
            ability_color = (0, 255, 0) if basic_cooldown == 0 else COLORS['crimson']
            ability_surface = self.get_cached_font(14).render(ability_name, True, ability_color)
            ability_rect = ability_surface.get_rect(centerx=overlay_width//2, y=ability_y)
            ability_bg_rect = pygame.Rect(ability_rect.x - 5, ability_rect.y - 2, ability_rect.width + 10, ability_rect.height + 4)
            pygame.draw.rect(overlay_surface, (*COLORS['deep_black'], 200), ability_bg_rect, border_radius=5)
            overlay_surface.blit(ability_surface, ability_rect)
            cooldown_text = str(basic_cooldown)
            cooldown_surface = self.get_cached_font(14).render(cooldown_text, True, ability_color)
            cooldown_rect = cooldown_surface.get_rect(midleft=(ability_rect.right + 5, ability_rect.centery))
            cooldown_bg_rect = pygame.Rect(cooldown_rect.x - 3, cooldown_rect.y - 2, cooldown_rect.width + 6, cooldown_rect.height + 4)
            pygame.draw.rect(overlay_surface, (*COLORS['deep_black'], 200), cooldown_bg_rect, border_radius=3)
            overlay_surface.blit(cooldown_surface, cooldown_rect)

        # Affichage du passif (si activé)
        if customization and customization.has_passive:
            passive_y = ability_y + 30
            passive_text = "Passif"
            passive_color = COLORS['purple']
            passive_surface = self.get_cached_font(12).render(passive_text, True, passive_color)
            passive_rect = passive_surface.get_rect(centerx=overlay_width//2, y=passive_y)
            passive_bg_rect = pygame.Rect(passive_rect.x - 5, passive_rect.y - 2, passive_rect.width + 10, passive_rect.height + 4)
            pygame.draw.rect(overlay_surface, (*COLORS['deep_black'], 200), passive_bg_rect, border_radius=5)
            overlay_surface.blit(passive_surface, passive_rect)

        return overlay_surface

    def create_right_click_unit_overlay(self, unit, border_color):
        """Crée l'overlay de clic droit pour une unité avec le même format que les héros"""
        # Même format que les héros : compact et vertical
        overlay_width = 400
        overlay_height = 576
        overlay_surface = pygame.Surface((overlay_width, overlay_height), pygame.SRCALPHA)

        # Bordure colorée selon le type
        pygame.draw.rect(overlay_surface, border_color, (0, 0, overlay_width, overlay_height), 4, border_radius=20)

        # Nom (avant la virgule) - police plus grande
        name_text = unit['name'].split(',')[0].strip()
        name_y = int(overlay_height * 0.08)
        name_surface = self.get_cached_font(44).render(name_text, True, COLORS['white'])
        name_rect = name_surface.get_rect(centerx=overlay_width//2, y=name_y)
        name_bg_rect = pygame.Rect(name_rect.x - 10, name_rect.y - 4, name_rect.width + 20, name_rect.height + 8)
        pygame.draw.rect(overlay_surface, (*COLORS['deep_black'], 200), name_bg_rect, border_radius=10)
        overlay_surface.blit(name_surface, name_rect)

        # Élément (symbole) - plus grand
        if 'element' in unit and unit['element']:
            element_mapping = {
                'feu': 'feu', 'eau': 'eau', 'glace': 'glace', 'terre': 'terre', 'air': 'air',
                'foudre': 'foudre', 'lumière': 'lumiere', 'ténèbres': 'tenebres', 'arcanique': 'arcane',
                'poison': 'poison', 'néant': 'neant'
            }
            element_name = unit['element'].lower()
            file_name = element_mapping.get(element_name, element_name)
            element_symbol_path = f"Symbols/{file_name}.png"
            element_symbol = self.game_ui.asset_manager.get_image(element_symbol_path)
            if element_symbol:
                symbol_size = (48, 48)  # Plus grand symbole
                scaled_symbol = pygame.transform.scale(element_symbol, symbol_size)
                symbol_rect = scaled_symbol.get_rect(topleft=(20, 20))
                circle_radius = 30  # Plus grand cercle
                circle_center = (symbol_rect.centerx, symbol_rect.centery)
                pygame.draw.circle(overlay_surface, (*COLORS['deep_black'], 200), circle_center, circle_radius)
                overlay_surface.blit(scaled_symbol, symbol_rect)
            else:
                element_text = f"Élément: {unit['element']}"
                element_surface = self.get_cached_font(24).render(element_text, True, COLORS['light_gold'])
                element_rect = element_surface.get_rect(topleft=(20, 20))
                circle_radius = 30
                circle_center = (element_rect.centerx, element_rect.centery)
                pygame.draw.circle(overlay_surface, (*COLORS['deep_black'], 200), circle_center, circle_radius)
                overlay_surface.blit(element_surface, element_rect)

        # Rareté - plus grande police
        rarity_y = overlay_height - 60
        if 'rarity' in unit:
            rarity_text = unit['rarity']
            rarity_surface = self.get_cached_font(22).render(rarity_text, True, COLORS['white'])
            rarity_rect = rarity_surface.get_rect(centerx=overlay_width//2, y=rarity_y)
            rarity_colors = {
                'Commun': COLORS['gray'],
                'Peu Commun': COLORS['green'],
                'Rare': COLORS['royal_blue'],
                'Épique': COLORS['crimson'],
                'Héros': COLORS['orange'],
                'Mythique': COLORS['gold'],
                'Spécial': COLORS['cyan'],
                'commun': COLORS['gray'],
                'peu commun': COLORS['green'],
                'rare': COLORS['royal_blue'],
                'épique': COLORS['crimson'],
                'héros': COLORS['orange'],
                'mythique': COLORS['gold'],
                'spécial': COLORS['cyan'],
            }
            rarity_color = rarity_colors.get(rarity_text.lower(), COLORS['white'])
            oval_width = rarity_rect.width + 40
            oval_height = rarity_rect.height + 16
            oval_rect = pygame.Rect(rarity_rect.centerx - oval_width//2, rarity_rect.centery - oval_height//2, oval_width, oval_height)
            pygame.draw.ellipse(overlay_surface, (*COLORS['deep_black'], 200), oval_rect)
            overlay_surface.blit(rarity_surface, rarity_rect)

        # Stats secondaires - plus grande police
        secondary_stats_y = rarity_y - 40 - int(overlay_height * 0.01)
        secondary_stats = []
        if 'crit_pct' in unit:
            secondary_stats.append(f"Crit: {unit['crit_pct']}%")
        if 'esquive_pct' in unit:
            secondary_stats.append(f"Esq: {unit['esquive_pct']}%")
        if 'precision_pct' in unit:
            secondary_stats.append(f"Préc: {unit['precision_pct']}%")
        if secondary_stats:
            secondary_stats_text = " | ".join(secondary_stats)
            secondary_stats_surface = self.get_cached_font(24).render(secondary_stats_text, True, COLORS['light_blue'])
            secondary_stats_rect = secondary_stats_surface.get_rect(centerx=overlay_width//2, y=secondary_stats_y)
            secondary_stats_bg_rect = pygame.Rect(secondary_stats_rect.x - 10, secondary_stats_rect.y - 4, secondary_stats_rect.width + 20, secondary_stats_rect.height + 8)
            pygame.draw.rect(overlay_surface, (*COLORS['deep_black'], 200), secondary_stats_bg_rect, border_radius=10)
            overlay_surface.blit(secondary_stats_surface, secondary_stats_rect)

        # Stats primaires - plus grande police
        primary_stats_y = secondary_stats_y - 40
        hp = unit.get('hp', 0)
        attack = unit.get('attack', 0)
        defense = unit.get('defense', 0)
        stats_text = f"HP: {hp} | ATK: {attack} | DEF: {defense}"
        stats_surface = self.get_cached_font(28).render(stats_text, True, COLORS['light_gold'])
        stats_rect = stats_surface.get_rect(centerx=overlay_width//2, y=primary_stats_y)
        stats_bg_rect = pygame.Rect(stats_rect.x - 10, stats_rect.y - 4, stats_rect.width + 20, stats_rect.height + 8)
        pygame.draw.rect(overlay_surface, (*COLORS['deep_black'], 200), stats_bg_rect, border_radius=10)
        overlay_surface.blit(stats_surface, stats_rect)

        # Cooldown de capacité
        cooldown_y = primary_stats_y - 40
        if 'cooldown' in unit:
            cooldown_text = f"Cooldown: {unit['cooldown']}"
            cooldown_surface = self.get_cached_font(24).render(cooldown_text, True, COLORS['crimson'])
            cooldown_rect = cooldown_surface.get_rect(centerx=overlay_width//2, y=cooldown_y)
            cooldown_bg_rect = pygame.Rect(cooldown_rect.x - 10, cooldown_rect.y - 4, cooldown_rect.width + 20, cooldown_rect.height + 8)
            pygame.draw.rect(overlay_surface, (*COLORS['deep_black'], 200), cooldown_bg_rect, border_radius=10)
            overlay_surface.blit(cooldown_surface, cooldown_rect)

        # Capacités de l'unité
        abilities_y = cooldown_y - 40
        if 'ability_ids' in unit and unit['ability_ids']:
            # Titre des capacités
            abilities_title = "Capacités:"
            abilities_title_surface = self.get_cached_font(20).render(abilities_title, True, COLORS['light_gold'])
            abilities_title_rect = abilities_title_surface.get_rect(centerx=overlay_width//2, y=abilities_y)
            abilities_title_bg_rect = pygame.Rect(abilities_title_rect.x - 10, abilities_title_rect.y - 4, abilities_title_rect.width + 20, abilities_title_rect.height + 8)
            pygame.draw.rect(overlay_surface, (*COLORS['deep_black'], 200), abilities_title_bg_rect, border_radius=10)
            overlay_surface.blit(abilities_title_surface, abilities_title_rect)
            
            # Charger les données des capacités
            try:
                with open("Data/effects_database.json", 'r', encoding='utf-8') as f:
                    effects_data = json.load(f)
                abilities_data = effects_data.get("abilities", {})
            except Exception as e:
                abilities_data = {}
            
            # Afficher chaque capacité
            current_ability_y = abilities_y + 30
            for i, ability_id in enumerate(unit['ability_ids']):
                if ability_id in abilities_data:
                    ability = abilities_data[ability_id]
                    ability_name = ability.get("name", f"Capacité {i+1}")
                    ability_cooldown = ability.get("base_cooldown", 0)
                    ability_element = ability.get("element", "1")  # Récupérer l'élément de la capacité
                    
                    # Symbole d'élément de la capacité
                    element_mapping = {
                        '1': 'feu', '2': 'eau', '3': 'terre', '4': 'air', '5': 'glace',
                        '6': 'foudre', '7': 'lumière', '8': 'ténèbres', '9': 'arcanique',
                        '10': 'poison', '11': 'néant', '12': 'néant'
                    }
                    element_name = element_mapping.get(str(ability_element), 'feu')
                    element_symbol_path = f"Symbols/{element_name}.png"
                    element_symbol = self.game_ui.asset_manager.get_image(element_symbol_path)
                    
                    # Position du symbole et du texte
                    symbol_x = overlay_width//2 - 60  # Symbole à gauche du centre
                    text_x = overlay_width//2 - 20   # Texte à droite du symbole
                    
                    if element_symbol:
                        # Afficher le symbole d'élément (32x32)
                        symbol_size = (32, 32)
                        scaled_symbol = pygame.transform.scale(element_symbol, symbol_size)
                        symbol_rect = scaled_symbol.get_rect(centerx=symbol_x, centery=current_ability_y + 8)
                        overlay_surface.blit(scaled_symbol, symbol_rect)
                    
                    # Nom de la capacité avec cooldown
                    name_text = f"{ability_name} (CD: {ability_cooldown})"
                    name_surface = self.get_cached_font(16).render(name_text, True, COLORS['cyan'])
                    # Centrer verticalement le texte par rapport au symbole (32px de hauteur)
                    text_y = current_ability_y + (32 - name_surface.get_height()) // 2
                    name_rect = name_surface.get_rect(centerx=text_x, y=text_y)
                    name_bg_rect = pygame.Rect(name_rect.x - 5, name_rect.y - 2, name_rect.width + 10, name_rect.height + 4)
                    pygame.draw.rect(overlay_surface, (*COLORS['deep_black'], 200), name_bg_rect, border_radius=5)
                    overlay_surface.blit(name_surface, name_rect)
                    current_ability_y += 25
                else:
                    # Capacité non trouvée
                    name_text = f"Capacité {i+1} (ID: {ability_id})"
                    name_surface = self.get_cached_font(16).render(name_text, True, COLORS['red'])
                    name_rect = name_surface.get_rect(centerx=overlay_width//2, y=current_ability_y)
                    name_bg_rect = pygame.Rect(name_rect.x - 5, name_rect.y - 2, name_rect.width + 10, name_rect.height + 4)
                    pygame.draw.rect(overlay_surface, (*COLORS['deep_black'], 200), name_bg_rect, border_radius=5)
                    overlay_surface.blit(name_surface, name_rect)
                    current_ability_y += 25
        else:
            # Aucune capacité
            no_abilities_text = "Aucune capacité"
            no_abilities_surface = self.get_cached_font(18).render(no_abilities_text, True, COLORS['gray'])
            no_abilities_rect = no_abilities_surface.get_rect(centerx=overlay_width//2, y=abilities_y)
            no_abilities_bg_rect = pygame.Rect(no_abilities_rect.x - 10, no_abilities_rect.y - 4, no_abilities_rect.width + 20, no_abilities_rect.height + 8)
            pygame.draw.rect(overlay_surface, (*COLORS['deep_black'], 200), no_abilities_bg_rect, border_radius=10)
            overlay_surface.blit(no_abilities_surface, no_abilities_rect)
        
        # Passifs de l'unité (format compact)
        passives_y = abilities_y + 100  # Espace après les capacités
        if 'passive_ids' in unit and unit['passive_ids']:
            # Titre des passifs
            passives_title = "Passifs:"
            passives_title_surface = self.get_cached_font(20).render(passives_title, True, COLORS['light_gold'])
            passives_title_rect = passives_title_surface.get_rect(centerx=overlay_width//2, y=passives_y)
            passives_title_bg_rect = pygame.Rect(passives_title_rect.x - 10, passives_title_rect.y - 4, passives_title_rect.width + 20, passives_title_rect.height + 8)
            pygame.draw.rect(overlay_surface, (*COLORS['deep_black'], 200), passives_title_bg_rect, border_radius=10)
            overlay_surface.blit(passives_title_surface, passives_title_rect)
            
            # Charger les données des passifs
            try:
                with open("Data/effects_database.json", 'r', encoding='utf-8') as f:
                    effects_data = json.load(f)
                passives_data = effects_data.get("passives", {})
            except:
                passives_data = {}
            
            # Afficher chaque passif
            current_passive_y = passives_y + 30
            for i, passive_id in enumerate(unit['passive_ids']):
                if passive_id in passives_data:
                    passive = passives_data[passive_id]
                    passive_name = passive.get("name", f"Passif {i+1}")
                    
                    # Nom du passif
                    name_text = passive_name
                    name_surface = self.get_cached_font(16).render(name_text, True, COLORS['purple'])
                    name_rect = name_surface.get_rect(centerx=overlay_width//2, y=current_passive_y)
                    name_bg_rect = pygame.Rect(name_rect.x - 5, name_rect.y - 2, name_rect.width + 10, name_rect.height + 4)
                    pygame.draw.rect(overlay_surface, (*COLORS['deep_black'], 200), name_bg_rect, border_radius=5)
                    overlay_surface.blit(name_surface, name_rect)
                    current_passive_y += 25
                else:
                    # Passif non trouvé
                    name_text = f"Passif {i+1} (ID: {passive_id})"
                    name_surface = self.get_cached_font(16).render(name_text, True, COLORS['red'])
                    name_rect = name_surface.get_rect(centerx=overlay_width//2, y=current_passive_y)
                    name_bg_rect = pygame.Rect(name_rect.x - 5, name_rect.y - 2, name_rect.width + 10, name_rect.height + 4)
                    pygame.draw.rect(overlay_surface, (*COLORS['deep_black'], 200), name_bg_rect, border_radius=5)
                    overlay_surface.blit(name_surface, name_rect)
                    current_passive_y += 25
        else:
            # Aucun passif
            no_passives_text = "Aucun passif"
            no_passives_surface = self.get_cached_font(18).render(no_passives_text, True, COLORS['gray'])
            no_passives_rect = no_passives_surface.get_rect(centerx=overlay_width//2, y=passives_y)
            no_passives_bg_rect = pygame.Rect(no_passives_rect.x - 10, no_passives_rect.y - 4, no_passives_rect.width + 20, no_passives_rect.height + 8)
            pygame.draw.rect(overlay_surface, (*COLORS['deep_black'], 200), no_passives_bg_rect, border_radius=10)
            overlay_surface.blit(no_passives_surface, no_passives_rect)

        return overlay_surface

    def create_right_click_card_overlay(self, card, border_color):
        """Crée l'overlay de clic droit pour une carte avec le même format que les héros"""
        # Format 80% de l'écran comme les héros
        SCREEN_WIDTH = 1920
        SCREEN_HEIGHT = 1080
        overlay_width = int(SCREEN_WIDTH * 0.8)
        overlay_height = int(SCREEN_HEIGHT * 0.8)
        overlay_surface = pygame.Surface((overlay_width, overlay_height), pygame.SRCALPHA)

        # Bordure colorée avec coins arrondis
        border_radius = 30
        pygame.draw.rect(overlay_surface, border_color, (0, 0, overlay_width, overlay_height), 4, border_radius=border_radius)

        # Layout : Image à gauche (40%), Texte à droite (60%) - comme les héros
        image_width = int(overlay_width * 0.4)  # 614 pixels
        text_width = int(overlay_width * 0.6)   # 922 pixels
        image_x = 0
        text_x = image_width + 20  # Espacement entre image et texte

        # Image de la carte - côté gauche avec bordure
        border_margin = 30
        image_inner_width = image_width - (border_margin * 2)
        image_inner_height = overlay_height - (border_margin * 2)
        
        if 'image_path' in card and card['image_path']:
            card_image = self.game_ui.asset_manager.get_image(card['image_path'])
            if card_image:
                # Redimensionner l'image
                scaled_image = pygame.transform.scale(card_image, (image_inner_width, image_inner_height))
                
                # Créer une surface avec coins arrondis pour l'image
                image_surface = pygame.Surface((image_inner_width, image_inner_height), pygame.SRCALPHA)
                
                # Créer un masque avec coins arrondis précis
                mask_surface = self.create_rounded_mask(image_inner_width, image_inner_height, 30)
                
                # Appliquer le masque à l'image
                image_surface.blit(scaled_image, (0, 0))
                image_surface.blit(mask_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                
                overlay_surface.blit(image_surface, (border_margin, border_margin))
            else:
                # Image par défaut avec coins arrondis
                default_surface = pygame.Surface((image_inner_width, image_inner_height), pygame.SRCALPHA)
                default_surface.fill(COLORS['dark_gray'])
                mask_surface = self.create_rounded_mask(image_inner_width, image_inner_height, 30)
                default_surface.blit(mask_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                overlay_surface.blit(default_surface, (border_margin, border_margin))
        else:
            # Image par défaut avec coins arrondis (pas d'image_path)
            default_surface = pygame.Surface((image_inner_width, image_inner_height), pygame.SRCALPHA)
            default_surface.fill(COLORS['dark_gray'])
            mask_surface = self.create_rounded_mask(image_inner_width, image_inner_height, 30)
            default_surface.blit(mask_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            overlay_surface.blit(default_surface, (border_margin, border_margin))

        # Zone texte - côté droit
        text_y = 40  # Marge supérieure
        current_y = text_y

        # Symbole élémentaire + texte
        if 'element' in card and card['element']:
            element_mapping = {
                'feu': 'feu', 'eau': 'eau', 'glace': 'glace', 'terre': 'terre', 'air': 'air',
                'foudre': 'foudre', 'lumière': 'lumiere', 'ténèbres': 'tenebres', 'arcanique': 'arcane',
                'poison': 'poison', 'néant': 'neant', 'neutre': 'neant'
            }
            element_name = card['element'].lower()
            file_name = element_mapping.get(element_name, element_name)
            element_symbol_path = f"Symbols/{file_name}.png"
            element_symbol = self.game_ui.asset_manager.get_image(element_symbol_path)
            
            if element_symbol:
                # Symbole + texte
                symbol_size = (64, 64)
                scaled_symbol = pygame.transform.scale(element_symbol, symbol_size)
                symbol_rect = scaled_symbol.get_rect(topleft=(text_x, current_y))
                overlay_surface.blit(scaled_symbol, symbol_rect)
                
                # Texte de l'élément (sans "Élément:")
                element_text = card['element']
                element_surface = self.get_cached_font(32).render(element_text, True, COLORS['light_gold'])
                overlay_surface.blit(element_surface, (text_x + 80, current_y + 20))
            else:
                # Texte seulement (sans "Élément:")
                element_text = card['element']
                element_surface = self.get_cached_font(32).render(element_text, True, COLORS['light_gold'])
                overlay_surface.blit(element_surface, (text_x, current_y))
            
            current_y += 80

        # Nom complet de la carte
        full_name = card['name']
        name_surface = self.get_cached_font(48).render(full_name, True, COLORS['white'])
        overlay_surface.blit(name_surface, (text_x, current_y))
        current_y += 80

        # Type de carte
        if 'card_type' in card:
            card_type_text = card['card_type'].replace('CARDTYPE.', '').title()
            card_type_surface = self.get_cached_font(28).render(card_type_text, True, COLORS['light_gold'])
            overlay_surface.blit(card_type_surface, (text_x, current_y))
            current_y += 50

        # Coût en mana
        if 'cost' in card:
            cost_text = f"Coût : {card['cost']}"
            cost_surface = self.get_cached_font(28).render(cost_text, True, COLORS['crimson'])
            overlay_surface.blit(cost_surface, (text_x, current_y))
            current_y += 50

        # Description si présente
        if 'description' in card and card['description']:
            # Nettoyer le texte de la description en supprimant le coût entre parenthèses
            desc_text_raw = card['description']
            if '(' in desc_text_raw:
                last_open = desc_text_raw.rfind('(')
                if last_open != -1:
                    desc_text_raw = desc_text_raw[:last_open].strip()
            
            # Wrapping intelligent après chaque "."
            desc_lines = desc_text_raw.split('.')
            for line in desc_lines:
                if line.strip():
                    line = line.strip() + '.'
                    wrapped_lines = self.smart_wrap_text(line, self.get_cached_font(28), text_width - 40)
                    for wrapped_line in wrapped_lines:
                        desc_surface = self.get_cached_font(28).render(wrapped_line, True, COLORS['white'])
                        overlay_surface.blit(desc_surface, (text_x, current_y))
                        current_y += 40
            current_y += 60

        # Rareté (sans "RARITY.")
        if 'rarity' in card:
            rarity_text = card['rarity'].replace('RARITY.', '')
            rarity_surface = self.get_cached_font(28).render(rarity_text, True, COLORS['white'])
            overlay_surface.blit(rarity_surface, (text_x, current_y))

        return overlay_surface



class Slider:
    """Classe pour créer des sliders interactifs"""
    
    def __init__(self, x, y, width, height, min_val, max_val, initial_value, step, label, callback, stat_name, hero_name=None, game_ui=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial_value
        self.step = step
        self.label = label
        self.callback = callback
        self.stat_name = stat_name
        self.hero_name = hero_name
        self.game_ui = game_ui
        self.dragging = False
        self.rect = pygame.Rect(x, y, width, height)
        self.last_saved_value = initial_value  # Pour éviter les sauvegardes multiples
        
    def draw(self, screen):
        """Dessine le slider"""
        # Afficher le texte de la stat aux positions exactes demandées
        text_surface = self.game_ui.font_medium.render(self.label, True, COLORS['white'])
        
        # Positions exactes pour chaque label selon les spécifications
        if self.label == "HP":
            text_rect = text_surface.get_rect(centerx=200, bottom=220)
        elif self.label == "Attaque":
            text_rect = text_surface.get_rect(centerx=200, bottom=320)
        elif self.label == "Défense":
            text_rect = text_surface.get_rect(centerx=200, bottom=420)
        else:
            # Fallback pour les autres labels
            text_rect = text_surface.get_rect(centerx=self.x + self.width//2, bottom=self.y - 55)
        
        screen.blit(text_surface, text_rect)
        
        # Fond du slider
        pygame.draw.rect(screen, COLORS['dark_gray'], self.rect)
        pygame.draw.rect(screen, COLORS['gray'], self.rect, 2)
        
        # Dessiner les graduations et labels
        self.draw_graduations(screen)
        
        # Calculer la position du curseur
        value_ratio = (self.value - self.min_val) / (self.max_val - self.min_val)
        cursor_x = self.x + int(value_ratio * self.width)
        cursor_rect = pygame.Rect(cursor_x - 5, self.y - 5, 10, self.height + 10)
        
        # Dessiner le curseur
        pygame.draw.rect(screen, COLORS['gold'], cursor_rect)
        
        # Texte de la valeur et du coût
        mana_cost = 0
        if self.value == 5:
            mana_cost = 1
        elif self.value == 10:
            mana_cost = 2
        elif self.value == 15:
            mana_cost = 3
        
        value_text = f"{self.value}% (+{mana_cost} mana)"
        value_surface = self.game_ui.font_small.render(value_text, True, COLORS['white'])
        screen.blit(value_surface, (self.x, self.y + self.height + 10))
        

    
    def draw_graduations(self, screen):
        """Dessine les graduations et labels sur le slider"""
        # Valeurs des graduations
        graduation_values = [0, 5, 10, 15]
        
        # Police pour les labels
        font = pygame.font.Font(None, 18)
        
        for value in graduation_values:
            # Calculer la position de la graduation
            ratio = (value - self.min_val) / (self.max_val - self.min_val)
            grad_x = self.x + int(ratio * self.width)
            
            # Dessiner le trait de graduation
            grad_height = 8
            grad_rect = pygame.Rect(grad_x - 1, self.y - grad_height, 2, grad_height)
            pygame.draw.rect(screen, COLORS['white'], grad_rect)
            
            # Calculer le coût en mana pour cette valeur
            mana_cost = 0
            if value == 5:
                mana_cost = 1
            elif value == 10:
                mana_cost = 2
            elif value == 15:
                mana_cost = 3
            
            # Dessiner le label au-dessus avec le coût
            label_text = f"{value}% (+{mana_cost})"
            text_surface = font.render(label_text, True, COLORS['white'])
            text_rect = text_surface.get_rect(centerx=grad_x, bottom=self.y - grad_height - 5)
            screen.blit(text_surface, text_rect)
    
    def handle_click(self, mouse_pos):
        """Gère les clics sur le slider"""
        if self.rect.collidepoint(mouse_pos):
            self.dragging = True
            return True
        return False
    
    def handle_release(self):
        """Gère le relâchement de la souris"""
        if self.dragging:
            # Mettre à jour et sauvegarder seulement quand on relâche la souris ET que la valeur a changé
            if self.value != self.last_saved_value:
                # Marquer la valeur comme sauvegardée
                self.last_saved_value = self.value
                # Mettre à jour et sauvegarder seulement ici, lors du relâchement
                if hero_customization_manager and self.hero_name:
                    hero_customization_manager.update_and_save_customization(
                        self.hero_name,
                        self.stat_name,
                        self.value
                    )
        self.dragging = False
    
    def handle_drag(self, mouse_pos):
        """Gère le glissement de la souris"""
        if self.dragging:
            self.update_value_from_mouse(mouse_pos[0])
    
    def update_value_from_mouse(self, mouse_x):
        """Met à jour la valeur selon la position de la souris"""
        # Calculer la nouvelle valeur
        ratio = max(0, min(1, (mouse_x - self.x) / self.width))
        new_value = self.min_val + ratio * (self.max_val - self.min_val)
        
        # Arrondir au step le plus proche
        new_value = round(new_value / self.step) * self.step
        
        # Limiter aux bornes
        new_value = max(self.min_val, min(self.max_val, new_value))
        
        # Mettre à jour seulement si la valeur a vraiment changé
        if new_value != self.value:
            self.value = new_value



class DeckBuilderScreen(Screen):
    """Écran de construction de deck"""
    
    def __init__(self, game_ui: GameUI):
        super().__init__(game_ui)
        
        # Variables de base
        self.current_tab = "heroes"
        self.scroll_y = 0
        self.scroll_speed = 50
        self.max_scroll = 0
        self.scrollbar_dragging = False
        self.scrollbar_drag_start = 0
        
        # Données du jeu
        self.heroes_data = []
        self.units_data = []
        self.cards_data = []
        
        # Sélections
        self.selected_hero = None
        self.selected_units = []
        self.selected_cards = []
        self.customized_stats = {}
        
        # Filtres
        self.filter_element = "all"
        self.filter_cost = "all"
        self.search_text = ""
        
        # Interface
        self.tabs = []
        self.setup_interface()
        
        # Cache pour les performances
        self.font_cache = {}
        self.text_surfaces_cache = {}
        
        # Cache pour les surfaces pré-rendues
        self.cached_content_surfaces = {}
        self.cached_content_heights = {}
        self.last_tab = None
        self.last_filter_state = None
        
        # Variables pour l'effet hover de la colonne de droite
        self.hovered_item = None
        self.hovered_item_type = None
        self.hover_animation_alpha = 0
        self.hover_animation_speed = 10
        self.hover_rects = {}
        
        # Variables pour la scrollbar
        self.scrollbar_dragging = False
        self.scrollbar_drag_start = 0
        
        # Variables pour l'overlay de clic droit
        self.right_click_overlay = None
        self.right_click_overlay_type = None
        self.right_click_overlay_alpha = 255
        
        # Gestionnaire de deck
        self.deck_manager = None
        self.deck_dropdown = None
        self.deck_buttons = []
        self.current_deck_name = None
        self.rename_mode = False
        self.rename_text = ""
        self.rename_cursor_pos = 0
        
        # Charger les données depuis les JSON
        self.load_data()
        
        # Initialiser le gestionnaire de deck
        self.setup_deck_manager()
    
    def setup_deck_manager(self):
        """Initialise le gestionnaire de deck et l'interface"""
        from Engine.deck_manager import deck_manager
        self.deck_manager = deck_manager
        
        # Obtenir le deck actuel
        current_deck = self.deck_manager.get_current_deck()
        if current_deck:
            self.current_deck_name = current_deck.name
        else:
            self.current_deck_name = "Nouveau Deck"
        
        # Créer le menu déroulant des decks
        self.update_deck_dropdown()
        
        # Créer les boutons du gestionnaire
        self.setup_deck_buttons()
        
        # Charger le deck actuel
        self.load_current_deck()
    
    def update_deck_dropdown(self):
        """Met à jour le menu déroulant des decks"""
        if not self.deck_manager:
            return
        
        # Obtenir la liste des noms de decks
        deck_names = self.deck_manager.get_deck_names()
        if not deck_names:
            deck_names = ["Nouveau Deck"]
        
        # Créer les options sans croix (juste les noms)
        options = []
        for name in deck_names:
            # Limiter à 18 caractères
            display_name = name[:18] if len(name) <= 18 else name[:15] + "..."
            options.append(display_name)
        
        # Position du menu déroulant (au-dessus de la colonne de droite)
        left_width = int(SCREEN_WIDTH * 0.8)
        dropdown_x = left_width + 20
        dropdown_y = 120
        dropdown_width = 200
        dropdown_height = 30
        
        # Créer le menu déroulant
        self.deck_dropdown = DropdownMenu(
            dropdown_x, dropdown_y, dropdown_width, dropdown_height,
            options, self.current_deck_name[:18] if self.current_deck_name else "Nouveau Deck"
        )
    
    def setup_deck_buttons(self):
        """Configure les boutons du gestionnaire de deck"""
        left_width = int(SCREEN_WIDTH * 0.8)
        button_y = 120
        button_size = 30
        
        # Bouton "+" pour créer un nouveau deck
        create_x = left_width + 240
        self.create_deck_button = Button(
            create_x, button_y, button_size, button_size, "+",
            COLORS['green'], COLORS['white'], self.create_new_deck,
            "Créer un nouveau deck"
        )
        
        # Bouton "✕" pour supprimer le deck actuel
        delete_x = create_x + button_size + 10
        self.delete_deck_button = Button(
            delete_x, button_y, button_size, button_size, "✕",
            COLORS['red'], COLORS['white'], self.delete_current_deck,
            "Supprimer le deck actuel"
        )
        
        # Bouton pour renommer le deck (décalé)
        rename_x = delete_x + button_size + 10
        self.rename_deck_button = Button(
            rename_x, button_y, button_size, button_size, "✏",
            COLORS['blue'], COLORS['white'], self.start_rename_deck,
            "Renommer le deck"
        )
        
        # Ajouter les boutons à la liste
        self.deck_buttons = [self.create_deck_button, self.delete_deck_button, self.rename_deck_button]
    
    def delete_current_deck(self):
        """Supprime le deck actuel"""
        if not self.deck_manager or not self.current_deck_name:
            print("[ERREUR] Aucun deck à supprimer")
            return
        
        # Vérifier qu'il y a au moins un autre deck avant de supprimer
        all_decks = self.deck_manager.get_deck_names()
        if len(all_decks) <= 1:
            print("[ERREUR] Impossible de supprimer le dernier deck")
            return
        
        # Supprimer le deck actuel
        if self.deck_manager.delete_deck(self.current_deck_name):
            # Changer vers un autre deck
            remaining_decks = self.deck_manager.get_deck_names()
            if remaining_decks:
                self.current_deck_name = remaining_decks[0]
                self.deck_manager.set_current_deck(self.current_deck_name)
                self.load_current_deck()
                self.update_deck_dropdown()
                print(f"[DECK BUILDER] Deck supprimé: {self.current_deck_name}")
            else:
                self.current_deck_name = "Nouveau Deck"
                self.update_deck_dropdown()
        else:
            print(f"[ERREUR] Impossible de supprimer le deck: {self.current_deck_name}")
    
    def create_new_deck(self):
        """Crée un nouveau deck"""
        if not self.deck_manager:
            return
        
        # Générer un nom unique
        base_name = "Nouveau Deck"
        counter = 1
        deck_name = base_name
        while deck_name in self.deck_manager.get_deck_names():
            deck_name = f"{base_name} ({counter})"
            counter += 1
        
        # Créer le deck
        if self.deck_manager.create_deck(deck_name):
            self.current_deck_name = deck_name
            self.update_deck_dropdown()
            print(f"[DECK BUILDER] Nouveau deck créé: {deck_name}")
        else:
            print(f"[ERREUR] Impossible de créer le deck: {deck_name}")
    
    def start_rename_deck(self):
        """Démarre le mode renommage du deck"""
        if not self.current_deck_name or not self.deck_manager:
            return
        
        self.rename_mode = True
        self.rename_text = self.current_deck_name
        self.rename_cursor_pos = len(self.rename_text)
    
    def finish_rename_deck(self):
        """Termine le renommage du deck"""
        if not self.rename_mode or not self.deck_manager:
            return
        
        new_name = self.rename_text.strip()
        if new_name and new_name != self.current_deck_name:
            # Limiter à 18 caractères
            if len(new_name) > 18:
                new_name = new_name[:18]
            
            # Vérifier que le nom n'existe pas déjà
            if new_name not in self.deck_manager.get_deck_names():
                if self.deck_manager.rename_deck(self.current_deck_name, new_name):
                    self.current_deck_name = new_name
                    self.update_deck_dropdown()
                    print(f"[DECK BUILDER] Deck renommé: {self.current_deck_name} → {new_name}")
                else:
                    print(f"[ERREUR] Impossible de renommer le deck")
            else:
                print(f"[ERREUR] Un deck avec ce nom existe déjà")
        
        self.rename_mode = False
        self.rename_text = ""
        self.rename_cursor_pos = 0
    

        
    def update(self):
        """Mise à jour de l'écran deck builder"""
        # Mise à jour de l'animation du hover
        self.update_hover_animation()
        
        # Mise à jour de l'overlay de clic droit
        self.update_right_click_overlay()
        
        # Mise à jour du hover pour les boutons du gestionnaire
        mouse_pos = pygame.mouse.get_pos()
        for button in self.deck_buttons:
            button.update_hover(mouse_pos)
        
        # Vérifier si le cache doit être invalidé
        self.check_cache_invalidation()
    
    def change_deck(self, deck_name):
        """Change le deck actuel"""
        if not self.deck_manager:
            return
        
        # Trouver le nom complet du deck
        full_deck_name = None
        for name in self.deck_manager.get_deck_names():
            display_name = name[:18] if len(name) <= 18 else name[:15] + "..."
            if display_name == deck_name:
                full_deck_name = name
                break
        
        if full_deck_name and self.deck_manager.set_current_deck(full_deck_name):
            self.current_deck_name = full_deck_name
            # Charger le contenu du deck
            self.load_current_deck()
            print(f"[DECK BUILDER] Deck changé vers: {full_deck_name}")
        else:
            print(f"[ERREUR] Impossible de changer vers le deck: {deck_name}")
    
    def load_current_deck(self):
        """Charge le contenu du deck actuel"""
        if not self.deck_manager:
            return
        
        current_deck = self.deck_manager.get_current_deck()
        if not current_deck:
            # Réinitialiser les sélections
            self.selected_hero = None
            self.selected_units = []
            self.selected_cards = []
            return
        
        # Charger le héros
        self.selected_hero = current_deck.hero if current_deck.hero else None
        
        # Charger les unités
        self.selected_units = current_deck.units.copy() if current_deck.units else []
        
        # Charger les cartes
        self.selected_cards = current_deck.cards.copy() if current_deck.cards else []
        
        # Charger les personnalisations
        if current_deck.customizations:
            self.customized_stats = current_deck.customizations.copy()
        else:
            self.customized_stats = {}
        
        print(f"[DECK BUILDER] Deck chargé: {len(self.selected_units)} unités, {len(self.selected_cards)} cartes")
    
    def load_data(self):
        """Charge les données depuis les fichiers JSON"""
        try:
            project_root = os.path.join(os.path.dirname(__file__), '..')
            
            # Charger les héros
            heroes_path = os.path.join(project_root, 'Data', 'heroes.json')
            if os.path.exists(heroes_path):
                with open(heroes_path, 'r', encoding='utf-8') as f:
                    self.heroes_data = json.load(f)
                print(f"[DECK BUILDER] {len(self.heroes_data)} héros chargés")
            
            # Charger les unités
            units_path = os.path.join(project_root, 'Data', 'units.json')
            if os.path.exists(units_path):
                with open(units_path, 'r', encoding='utf-8') as f:
                    self.units_data = json.load(f)
                print(f"[DECK BUILDER] {len(self.units_data)} unités chargées")
            
            # Charger les cartes
            cards_path = os.path.join(project_root, 'Data', 'cards.json')
            if os.path.exists(cards_path):
                with open(cards_path, 'r', encoding='utf-8') as f:
                    self.cards_data = json.load(f)
                print(f"[DECK BUILDER] {len(self.cards_data)} cartes chargées")
            
        except Exception as e:
            print(f"[ERREUR] Impossible de charger les données: {e}")
    
    def setup_interface(self):
        """Configure l'interface utilisateur"""
        # Onglets
        tab_width = 200
        tab_height = 50
        tab_y = 150
        
        self.tabs = [
            Button(50, tab_y, tab_width, tab_height, "HÉROS", COLORS['gold'], COLORS['deep_black'], lambda: self.change_tab("heroes")),
            Button(260, tab_y, tab_width, tab_height, "UNITÉS", COLORS['royal_blue'], COLORS['white'], lambda: self.change_tab("units")),
            Button(470, tab_y, tab_width, tab_height, "CARTES", COLORS['ruby_red'], COLORS['white'], lambda: self.change_tab("cards"))
        ]
        
        # Boutons d'action
        button_width = 150
        button_height = 50
        button_y = SCREEN_HEIGHT - 100
        
        self.buttons = [
            Button(50, button_y, button_width, button_height, "SAUVEGARDER", COLORS['gold'], COLORS['deep_black'], self.save_deck),
            Button(220, button_y, button_width, button_height, "RÉINITIALISER", COLORS['crimson'], COLORS['white'], self.reset_deck),
            Button(390, button_y, button_width, button_height, "PERSONNALISER", COLORS['light_gold'], COLORS['deep_black'], self.open_customization),
            Button(560, button_y, button_width, button_height, "RETOUR", COLORS['royal_blue'], COLORS['white'], lambda: self.game_ui.change_screen("main_menu"))
        ]
    
    def change_tab(self, tab_name: str):
        """Change d'onglet"""
        self.current_tab = tab_name
        self.scroll_y = 0
        # Ne pas invalider le cache à chaque changement d'onglet pour éviter les problèmes de performance
        # self.invalidate_cache()  # Commenté pour éviter l'invalidation excessive
        print(f"[DECK BUILDER] Changement d'onglet : {tab_name}")
    
    def check_cache_invalidation(self):
        """Vérifie si le cache doit être invalidé"""
        current_filter_state = (
            self.current_tab,
            self.filter_element,
            self.filter_cost,
            self.search_text
        )
        
        # Vérifier si les personnalisations ont changé
        hero_customization_changed = False
        if self.selected_hero and hero_customization_manager:
            hero_name = self.selected_hero.get("name", "Héros inconnu")
            current_customization = hero_customization_manager.get_customization(hero_name)
            if current_customization:
                # Comparer avec la dernière personnalisation connue
                if not hasattr(self, '_last_hero_customization'):
                    self._last_hero_customization = None
                
                current_customization_str = str(current_customization.__dict__)
                if self._last_hero_customization != current_customization_str:
                    self._last_hero_customization = current_customization_str
                    hero_customization_changed = True
        
        if (self.last_tab != self.current_tab or 
            self.last_filter_state != current_filter_state or
            hero_customization_changed):
            self.invalidate_cache()
            self.last_tab = self.current_tab
            self.last_filter_state = current_filter_state
    
    def invalidate_cache(self):
        """Invalide le cache des surfaces"""
        self.cached_content_surfaces.clear()
        self.cached_content_heights.clear()
        print("[DECK BUILDER] Cache invalidé")
    
    def get_cached_content_surface(self, content_rect):
        """Récupère ou crée la surface de contenu mise en cache"""
        cache_key = f"{self.current_tab}_{content_rect.width}_{content_rect.height}"
        
        if cache_key in self.cached_content_surfaces:
            return self.cached_content_surfaces[cache_key], self.cached_content_heights[cache_key]
        
        # Créer la surface mise en cache
        filtered_items = self.get_filtered_items()
        total_rows = (len(filtered_items) + 5) // 6
        total_content_height = total_rows * 320 + 40
        
        content_surface = pygame.Surface((content_rect.width, total_content_height))
        content_surface.fill(COLORS['royal_blue'])
        
        # Dessiner le contenu selon l'onglet
        if self.current_tab == "heroes":
            self.draw_heroes_list_cached(content_surface, content_rect)
        elif self.current_tab == "units":
            self.draw_units_list_cached(content_surface, content_rect)
        elif self.current_tab == "cards":
            self.draw_cards_list_cached(content_surface, content_rect)
        
        # Mettre en cache
        self.cached_content_surfaces[cache_key] = content_surface
        self.cached_content_heights[cache_key] = total_content_height
        
        return content_surface, total_content_height
    
    def get_filtered_items(self):
        """Retourne les éléments filtrés selon l'onglet actuel"""
        if self.current_tab == "heroes":
            return self.filter_heroes()
        elif self.current_tab == "units":
            return self.filter_units()
        elif self.current_tab == "cards":
            return self.filter_cards()
        return []
    
    def create_hero_overlay_surface_for_deck_builder(self, hero):
        """Crée une surface d'overlay pour un héros dans le deck builder (même style que les unités)"""
        overlay_width = 200  # Même largeur que la carte
        overlay_height = 288  # Même hauteur que la carte
        
        overlay_surface = pygame.Surface((overlay_width, overlay_height), pygame.SRCALPHA)

        # Bordure de la carte
        pygame.draw.rect(overlay_surface, COLORS['gold'], (0, 0, overlay_width, overlay_height), 2, border_radius=10)
        
        # Nom du héros - seulement avant la virgule, à 8% de la hauteur
        name_text = hero['name'].split(',')[0].strip()  # Prendre seulement avant la virgule
        name_y = int(overlay_height * 0.08)  # 8% de la hauteur
        name_surface = self.get_cached_font(22).render(name_text, True, COLORS['white'])
        name_rect = name_surface.get_rect(centerx=overlay_width//2, y=name_y)
        
        # Fond pour le nom
        name_bg_rect = pygame.Rect(name_rect.x - 5, name_rect.y - 2, name_rect.width + 10, name_rect.height + 4)
        pygame.draw.rect(overlay_surface, (*COLORS['deep_black'], 200), name_bg_rect, border_radius=5)
        overlay_surface.blit(name_surface, name_rect)
        
        # Élément avec symbole - dans le coin avec fond circulaire
        if 'element' in hero and hero['element']:
            # Mapping des noms d'éléments vers les noms de fichiers
            element_mapping = {
                'feu': 'feu',
                'eau': 'eau',
                'glace': 'glace',
                'terre': 'terre',
                'air': 'air',
                'foudre': 'foudre',
                'lumière': 'lumiere',
                'ténèbres': 'tenebres',
                'arcanique': 'arcane',
                'poison': 'poison',
                'néant': 'neant'
            }
            
            element_name = hero['element'].lower()
            file_name = element_mapping.get(element_name, element_name)
            element_symbol_path = f"Symbols/{file_name}.png"
            element_symbol = self.game_ui.asset_manager.get_image(element_symbol_path)
            
            if element_symbol:
                # Afficher le symbole d'élément dans le coin
                symbol_size = (24, 24)
                scaled_symbol = pygame.transform.scale(element_symbol, symbol_size)
                symbol_rect = scaled_symbol.get_rect(topleft=(10, 10))  # Coin supérieur gauche
                
                # Fond circulaire pour le symbole
                circle_radius = 15
                circle_center = (symbol_rect.centerx, symbol_rect.centery)
                pygame.draw.circle(overlay_surface, (*COLORS['deep_black'], 200), circle_center, circle_radius)
                overlay_surface.blit(scaled_symbol, symbol_rect)
            else:
                # Fallback vers le texte si le symbole n'est pas trouvé
                element_text = f"Élément: {hero['element']}"
                element_surface = self.get_cached_font(12).render(element_text, True, COLORS['light_gold'])
                element_rect = element_surface.get_rect(topleft=(10, 10))
                
                # Fond circulaire pour le texte d'élément
                circle_radius = 15
                circle_center = (element_rect.centerx, element_rect.centery)
                pygame.draw.circle(overlay_surface, (*COLORS['deep_black'], 200), circle_center, circle_radius)
                overlay_surface.blit(element_surface, element_rect)
        
        # Rareté - tout en bas avec fond ovale coloré
        rarity_y = overlay_height - 30  # Tout en bas
        if 'rarity' in hero:
            rarity_text = hero['rarity']
            rarity_surface = self.get_cached_font(11).render(rarity_text, True, COLORS['white'])
            rarity_rect = rarity_surface.get_rect(centerx=overlay_width//2, y=rarity_y)
            
            # Couleur de rareté
            rarity_colors = {
                'Commun': COLORS['gray'],
                'Peu Commun': COLORS['green'],
                'Rare': COLORS['royal_blue'],
                'Épique': COLORS['crimson'],
                'Héros': COLORS['orange'],
                'Mythique': COLORS['gold'],
                'Spécial': COLORS['cyan'],
                'commun': COLORS['gray'],
                'peu commun': COLORS['green'],
                'rare': COLORS['royal_blue'],
                'épique': COLORS['crimson'],
                'héros': COLORS['orange'],
                'mythique': COLORS['gold'],
                'spécial': COLORS['cyan'],
            }
            rarity_color = rarity_colors.get(rarity_text, COLORS['gray'])
            
            # Fond ovale pour la rareté
            oval_width = rarity_rect.width + 20
            oval_height = rarity_rect.height + 8
            oval_rect = pygame.Rect(rarity_rect.centerx - oval_width//2, rarity_rect.centery - oval_height//2, oval_width, oval_height)
            pygame.draw.ellipse(overlay_surface, (*rarity_color, 200), oval_rect)
            overlay_surface.blit(rarity_surface, rarity_rect)
        
        # Stats secondaires - au-dessus de la rareté avec 1% d'espace
        secondary_stats_y = rarity_y - 20 - int(overlay_height * 0.01)  # 1% d'espace
        secondary_stats = []
        if 'crit_pct' in hero:
            secondary_stats.append(f"Crit: {hero['crit_pct']}%")
        if 'esquive_pct' in hero:
            secondary_stats.append(f"Esq: {hero['esquive_pct']}%")
        if 'precision_pct' in hero:
            secondary_stats.append(f"Préc: {hero['precision_pct']}%")
        
        if secondary_stats:
            secondary_stats_text = " | ".join(secondary_stats)
            secondary_stats_surface = self.get_cached_font(12).render(secondary_stats_text, True, COLORS['light_blue'])
            secondary_stats_rect = secondary_stats_surface.get_rect(centerx=overlay_width//2, y=secondary_stats_y)
            
            # Fond pour les stats secondaires
            secondary_stats_bg_rect = pygame.Rect(secondary_stats_rect.x - 5, secondary_stats_rect.y - 2, secondary_stats_rect.width + 10, secondary_stats_rect.height + 4)
            pygame.draw.rect(overlay_surface, (*COLORS['deep_black'], 200), secondary_stats_bg_rect, border_radius=5)
            overlay_surface.blit(secondary_stats_surface, secondary_stats_rect)
        
        # Stats primaires - juste au-dessus des stats secondaires (fonds collés)
        primary_stats_y = secondary_stats_y - 20
        # Utiliser base_stats si disponible, sinon les stats directes
        if 'base_stats' in hero:
            hp = hero['base_stats'].get('hp', 0)
            attack = hero['base_stats'].get('attack', 0)
            defense = hero['base_stats'].get('defense', 0)
        else:
            hp = hero.get('hp', 0)
            attack = hero.get('attack', 0)
            defense = hero.get('defense', 0)
        
        stats_text = f"HP: {hp} | ATK: {attack} | DEF: {defense}"
        stats_surface = self.get_cached_font(14).render(stats_text, True, COLORS['light_gold'])
        stats_rect = stats_surface.get_rect(centerx=overlay_width//2, y=primary_stats_y)
        
        # Fond pour les stats primaires (collé au fond des stats secondaires)
        stats_bg_rect = pygame.Rect(stats_rect.x - 5, stats_rect.y - 2, stats_rect.width + 10, stats_rect.height + 4)
        pygame.draw.rect(overlay_surface, (*COLORS['deep_black'], 200), stats_bg_rect, border_radius=5)
        overlay_surface.blit(stats_surface, stats_rect)
        
        # Capacité - à environ 40% de la hauteur depuis le bas, seulement le nom
        ability_y = overlay_height - int(overlay_height * 0.40)  # 40% depuis le bas
        if 'ability_name' in hero and hero['ability_name']:
            # Prendre seulement le nom de la capacité
            ability_name = hero['ability_name'].strip()
            if len(ability_name) > 30:
                ability_name = ability_name[:27] + "..."
            
            # Récupérer le cooldown
            cooldown = hero.get('ability_cooldown', 0)
            
            # Déterminer la couleur (vert si cooldown = 0, sinon rouge)
            ability_color = COLORS['crimson'] if cooldown > 0 else (0, 255, 0)  # Vert si utilisable
            
            # Afficher le nom de la capacité
            ability_surface = self.get_cached_font(14).render(ability_name, True, ability_color)
            ability_rect = ability_surface.get_rect(centerx=overlay_width//2, y=ability_y)
            
            # Fond pour la capacité
            ability_bg_rect = pygame.Rect(ability_rect.x - 5, ability_rect.y - 2, ability_rect.width + 10, ability_rect.height + 4)
            pygame.draw.rect(overlay_surface, (*COLORS['deep_black'], 200), ability_bg_rect, border_radius=5)
            overlay_surface.blit(ability_surface, ability_rect)
            
            # Afficher le cooldown à côté du nom
            cooldown_text = str(cooldown)
            cooldown_surface = self.get_cached_font(14).render(cooldown_text, True, ability_color)
            cooldown_rect = cooldown_surface.get_rect(midleft=(ability_rect.right + 5, ability_rect.centery))
            
            # Fond pour le cooldown
            cooldown_bg_rect = pygame.Rect(cooldown_rect.x - 3, cooldown_rect.y - 2, cooldown_rect.width + 6, cooldown_rect.height + 4)
            pygame.draw.rect(overlay_surface, (*COLORS['deep_black'], 200), cooldown_bg_rect, border_radius=3)
            overlay_surface.blit(cooldown_surface, cooldown_rect)
        
        return overlay_surface

    def draw_heroes_list_cached(self, screen, content_rect):
        """Dessine la liste des héros (version mise en cache)"""
        filtered_heroes = self.filter_heroes()
        
        for i, hero in enumerate(filtered_heroes):
            col = i % 6
            row = i // 6
            
            x = col * 220 + 20
            y = row * 320 + 20
            
            # Fond de la carte
            card_rect = pygame.Rect(x, y, 200, 288)
            
            # Vérifier si c'est le héros sélectionné et s'il a des personnalisations
            display_hero = hero
            if (self.selected_hero and 
                hero.get('name') == self.selected_hero.get('name')):
                # Utiliser le héros personnalisé pour l'affichage
                display_hero = self.get_customized_hero()
            
            # Image du héros
            hero_image_path = display_hero.get('image_path', 'Hero/1.png')
            hero_image = self.game_ui.asset_manager.get_image(hero_image_path)
            
            if hero_image:
                scaled_image = pygame.transform.scale(hero_image, (200, 288))
                image_rect = scaled_image.get_rect(topleft=(x, y))
                screen.blit(scaled_image, image_rect)
            
            # Overlay permanent - même style que les unités
            overlay_surface = self.create_hero_overlay_surface_for_deck_builder(display_hero)
            overlay_rect = overlay_surface.get_rect(topleft=(x, y))
            screen.blit(overlay_surface, overlay_rect)
    
    def draw_units_list_cached(self, screen, content_rect):
        """Dessine la liste des unités (version mise en cache)"""
        filtered_units = self.filter_units()
        
        for i, unit in enumerate(filtered_units):
            col = i % 6
            row = i // 6
            
            x = col * 220 + 20
            y = row * 320 + 20
            
            # Fond de la carte
            card_rect = pygame.Rect(x, y, 200, 288)
            
            # Image de l'unité
            unit_image_path = unit.get('image_path', 'Crea/1.png')
            unit_image = self.game_ui.asset_manager.get_image(unit_image_path)
            
            if unit_image:
                scaled_image = pygame.transform.scale(unit_image, (200, 288))
                image_rect = scaled_image.get_rect(topleft=(x, y))
                screen.blit(scaled_image, image_rect)
            
            # Overlay permanent
            overlay_surface = self.create_unit_overlay_surface(unit)
            overlay_rect = overlay_surface.get_rect(topleft=(x, y))
            screen.blit(overlay_surface, overlay_rect)
    
    def draw_cards_list_cached(self, screen, content_rect):
        """Dessine la liste des cartes (version mise en cache)"""
        filtered_cards = self.filter_cards()
        
        for i, card in enumerate(filtered_cards):
            col = i % 6
            row = i // 6
            
            x = col * 220 + 20
            y = row * 320 + 20
            
            # Fond de la carte
            card_rect = pygame.Rect(x, y, 200, 288)
            pygame.draw.rect(screen, COLORS['dark_gray'], card_rect)
            pygame.draw.rect(screen, COLORS['gold'], card_rect, 2)
            
            # Image de la carte
            card_image = self.game_ui.asset_manager.get_image("Carte/DosCarte1")
            if card_image:
                scaled_image = pygame.transform.scale(card_image, (80, 115))
                image_rect = scaled_image.get_rect(center=(x + 150, y + 150))
                screen.blit(scaled_image, image_rect)
            
            # Nom de la carte
            name_text = self.smart_truncate(card['name'], 20)
            name_surface = self.get_cached_font(20).render(name_text, True, COLORS['white'])
            name_rect = name_surface.get_rect(center=(x + 100, y + 250))
            screen.blit(name_surface, name_rect)
            
            # Coût de la carte
            cost_text = str(card.get('cost', 0))
            cost_surface = self.get_cached_font(24).render(cost_text, True, COLORS['gold'])
            cost_rect = cost_surface.get_rect(center=(x + 30, y + 30))
            screen.blit(cost_surface, cost_rect)
            
            # Compteur d'exemplaires
            current_count = self.get_card_count(card['name'])
            if current_count > 0:
                count_text = f"{current_count}/2"
                count_surface = self.get_cached_font(18).render(count_text, True, COLORS['white'])
                count_rect = count_surface.get_rect(topright=(x + 190, y + 10))
                screen.blit(count_surface, count_rect)
                
                # Bordure colorée selon le nombre
                border_color = COLORS['gold'] if current_count == 1 else COLORS['green']
                pygame.draw.rect(screen, border_color, card_rect, 3)
    
    def get_cached_font(self, size):
        """Récupère une police mise en cache"""
        if size not in self.font_cache:
            self.font_cache[size] = pygame.font.Font(None, size)
        return self.font_cache[size]
    
    def create_rounded_mask(self, width, height, radius):
        """Crée un masque avec coins arrondis parfaits sans artefacts - Version optimisée avec cache"""
        
        # Validation du radius pour éviter les artefacts
        max_radius = min(width, height) // 2
        if radius > max_radius:
            radius = max_radius
            print(f"⚠️  Radius ajusté à {max_radius} pour éviter les artefacts")
        
        # Cache des masques pour éviter la régénération
        if not hasattr(self, '_mask_cache'):
            self._mask_cache = {}
        
        # Clé de cache unique
        cache_key = f"{width}x{height}_r{radius}"
        
        # Retourner le masque en cache s'il existe
        if cache_key in self._mask_cache:
            return self._mask_cache[cache_key]
        
        # Créer un nouveau masque
        mask_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Créer un masque de forme avec des coins arrondis
        # Le masque final : blanc (opaque) dans le rectangle arrondi, transparent ailleurs
        mask_surface.fill((0, 0, 0, 0))  # Tout transparent par défaut
        pygame.draw.rect(mask_surface, (255, 255, 255, 255), (0, 0, width, height), border_radius=radius)
        
        # Mettre en cache pour réutilisation
        self._mask_cache[cache_key] = mask_surface
        
        # Limiter la taille du cache (garder les 50 derniers masques)
        if len(self._mask_cache) > 50:
            # Supprimer les entrées les plus anciennes
            oldest_keys = list(self._mask_cache.keys())[:10]
            for key in oldest_keys:
                del self._mask_cache[key]
        
        return mask_surface
    
    def smart_truncate(self, text, max_length):
        """Tronque intelligemment un texte"""
        if len(text) <= max_length:
            return text
        return text[:max_length-3] + "..."
    
    def smart_wrap_text(self, text, font, max_width):
        """Retourne à la ligne intelligemment un texte pour qu'il tienne dans une largeur donnée"""
        # D'abord, diviser le texte en phrases (après chaque point)
        sentences = []
        current_sentence = ""
        
        for char in text:
            current_sentence += char
            if char == '.':
                sentences.append(current_sentence.strip())
                current_sentence = ""
        
        # Ajouter la dernière phrase si elle existe
        if current_sentence.strip():
            sentences.append(current_sentence.strip())
        
        # Maintenant, traiter chaque phrase pour le retour à la ligne
        lines = []
        for sentence in sentences:
            if not sentence:
                continue
                
            words = sentence.split()
            current_line = ""
            
            for word in words:
                test_line = current_line + " " + word if current_line else word
                test_surface = font.render(test_line, True, (255, 255, 255))
                if test_surface.get_width() <= max_width:
                    current_line = test_line
                else:
                    if current_line:
                        lines.append(current_line)
                    current_line = word
            
            if current_line:
                lines.append(current_line)
        
        return lines
    
    def draw_wrapped_text(self, surface, text, font, color, rect, line_spacing=5):
        """Dessine un texte avec retour à la ligne intelligent dans un rectangle donné"""
        lines = self.smart_wrap_text(text, font, rect.width)
        y_offset = rect.top
        
        for line in lines:
            if y_offset + font.get_height() > rect.bottom:
                break  # Arrêter si on dépasse la hauteur
            
            line_surface = font.render(line, True, color)
            line_rect = line_surface.get_rect(topleft=(rect.left, y_offset))
            surface.blit(line_surface, line_rect)
            y_offset += font.get_height() + line_spacing
        
        return y_offset - rect.top  # Retourner la hauteur utilisée
    
    def update_hover_animation(self):
        """Met à jour l'animation du hover"""
        if self.hovered_item is not None:
            # Animation d'apparition
            if self.hover_animation_alpha < 255:
                self.hover_animation_alpha = min(255, self.hover_animation_alpha + self.hover_animation_speed)
        else:
            # Animation de disparition
            if self.hover_animation_alpha > 0:
                self.hover_animation_alpha = max(0, self.hover_animation_alpha - self.hover_animation_speed)
    
    def filter_heroes(self):
        """Filtre les héros selon les critères"""
        filtered = []
        for hero in self.heroes_data:
            # Filtre par élément
            if self.filter_element != "all" and hero.get('element') != self.filter_element:
                continue
            
            # Filtre par recherche
            if self.search_text and self.search_text.lower() not in hero['name'].lower():
                continue
            
            filtered.append(hero)
        return filtered
    
    def filter_units(self):
        """Filtre les unités selon les critères"""
        filtered = []
        for unit in self.units_data:
            # Filtre par élément
            if self.filter_element != "all" and unit.get('element') != self.filter_element:
                continue
            
            # Filtre par recherche
            if self.search_text and self.search_text.lower() not in unit['name'].lower():
                continue
            
            filtered.append(unit)
        return filtered
    
    def filter_cards(self):
        """Filtre les cartes selon les critères"""
        filtered = []
        for card in self.cards_data:
            # Filtre par élément
            if self.filter_element != "all" and card.get('element') != self.filter_element:
                continue
            
            # Filtre par coût
            if self.filter_cost != "all":
                if self.filter_cost == "0-2" and card.get('cost', 0) > 2:
                    continue
                elif self.filter_cost == "3-5" and (card.get('cost', 0) < 3 or card.get('cost', 0) > 5):
                    continue
                elif self.filter_cost == "6+" and card.get('cost', 0) < 6:
                    continue
            
            # Filtre par recherche
            if self.search_text and self.search_text.lower() not in card['name'].lower():
                continue
            
            filtered.append(card)
        return filtered
    
    def handle_event(self, event):
        """Gestion des événements du deck builder"""
        mouse_pos = pygame.mouse.get_pos()
        
        # Mise à jour du survol pour tous les boutons
        for button in self.buttons + self.tabs:
            button.update_hover(mouse_pos)
        
        # Gestion des touches pour la recherche et le renommage
        if event.type == pygame.KEYDOWN:
            # Mode renommage
            if self.rename_mode:
                if event.key == pygame.K_RETURN:
                    self.finish_rename_deck()
                    return
                elif event.key == pygame.K_ESCAPE:
                    self.rename_mode = False
                    self.rename_text = ""
                    self.rename_cursor_pos = 0
                    return
                elif event.key == pygame.K_BACKSPACE:
                    if self.rename_cursor_pos > 0:
                        self.rename_text = self.rename_text[:self.rename_cursor_pos-1] + self.rename_text[self.rename_cursor_pos:]
                        self.rename_cursor_pos -= 1
                    return
                elif event.key == pygame.K_LEFT:
                    self.rename_cursor_pos = max(0, self.rename_cursor_pos - 1)
                    return
                elif event.key == pygame.K_RIGHT:
                    self.rename_cursor_pos = min(len(self.rename_text), self.rename_cursor_pos + 1)
                    return
                elif event.unicode.isprintable() and len(self.rename_text) < 18:
                    self.rename_text = self.rename_text[:self.rename_cursor_pos] + event.unicode + self.rename_text[self.rename_cursor_pos:]
                    self.rename_cursor_pos += 1
                    return
            
            # Gestion normale des touches
            if event.key == pygame.K_BACKSPACE:
                self.search_text = self.search_text[:-1]
            elif event.key == pygame.K_RETURN:
                pass
            elif event.unicode.isprintable():
                self.search_text += event.unicode
            elif event.key == pygame.K_UP:
                self.scroll_y = max(0, self.scroll_y - self.scroll_speed)
            elif event.key == pygame.K_DOWN:
                self.scroll_y = min(self.max_scroll, self.scroll_y + self.scroll_speed)
            elif event.key == pygame.K_PAGEUP:
                self.scroll_y = max(0, self.scroll_y - self.scroll_speed * 3)
            elif event.key == pygame.K_PAGEDOWN:
                self.scroll_y = min(self.max_scroll, self.scroll_y + self.scroll_speed * 3)
            elif event.key == pygame.K_HOME:
                self.scroll_y = 0
            elif event.key == pygame.K_END:
                self.scroll_y = self.max_scroll
        
        # Gestion des clics
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Si un overlay de clic droit est affiché, fermer l'overlay avec n'importe quel clic
            if self.right_click_overlay is not None:
                self.close_right_click_overlay()
                return
            
            if event.button == 1:  # Clic gauche
                # Vérifier les clics sur les onglets
                for i, tab in enumerate(self.tabs):
                    if tab.is_clicked(mouse_pos):
                        if i == 0:
                            self.change_tab("heroes")
                        elif i == 1:
                            self.change_tab("units")
                        elif i == 2:
                            self.change_tab("cards")
                        return
                
                # Vérifier les clics sur les boutons d'action
                for button in self.buttons:
                    if button.is_clicked(mouse_pos):
                        button.action()
                        return
                
                # Vérifier les clics sur les boutons du gestionnaire de deck
                for button in self.deck_buttons:
                    if button.is_clicked(mouse_pos):
                        button.action()
                        return
                
                # Vérifier les clics sur le menu déroulant des decks
                if self.deck_dropdown:
                    selected_option = self.deck_dropdown.handle_click(mouse_pos)
                    if selected_option:
                        # Changer de deck
                        self.change_deck(selected_option)
                        return
                
                # Vérifier les clics sur la scrollbar
                if self.handle_scrollbar_click(mouse_pos):
                    return
                
                # Vérifier les clics dans la zone de contenu
                self.handle_content_click(mouse_pos)
                
                # Vérifier les clics dans la zone de prévisualisation (colonne de droite)
                self.handle_preview_click(mouse_pos)
            
            elif event.button == 3:  # Clic droit
                # Gérer le clic droit pour afficher l'overlay
                self.handle_right_click(mouse_pos)
        
        # Gestion du scroll avec la molette de souris
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:  # Molette vers le haut
                self.scroll_y = max(0, self.scroll_y - 50)
            elif event.button == 5:  # Molette vers le bas
                self.scroll_y = min(self.max_scroll, self.scroll_y + 50)
        
        # Gestion du relâchement de la souris
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.scrollbar_dragging = False
        
        # Gestion du mouvement de la souris pour le hover et le drag de la scrollbar
        if event.type == pygame.MOUSEMOTION:
            # Gestion du drag de la scrollbar
            if self.scrollbar_dragging:
                self.handle_scrollbar_drag(mouse_pos)
            
            # Détecter le hover dans la colonne de droite
            self.handle_right_column_hover(mouse_pos)
    
    def handle_scrollbar_click(self, mouse_pos):
        """Gestion des clics sur la scrollbar"""
        left_width = int(SCREEN_WIDTH * 0.8)
        content_rect = pygame.Rect(50, 200, left_width - 100, SCREEN_HEIGHT - 300)
        scrollbar_width = 20
        scrollbar_rect = pygame.Rect(content_rect.right - scrollbar_width, content_rect.top, scrollbar_width, content_rect.height)
        
        if not scrollbar_rect.collidepoint(mouse_pos):
            return False
        
        # Calculer la position relative dans la scrollbar
        rel_y = mouse_pos[1] - scrollbar_rect.top
        
        if self.max_scroll > 0:
            # Calculer la position du curseur de la scrollbar
            cursor_height = max(30, (content_rect.height / (self.max_scroll + content_rect.height)) * content_rect.height)
            cursor_y = (self.scroll_y / self.max_scroll) * (content_rect.height - cursor_height)
            
            # Vérifier si on clique sur le curseur
            if cursor_y <= rel_y <= cursor_y + cursor_height:
                # Clic sur le curseur - commencer le drag
                self.scrollbar_dragging = True
                self.scrollbar_drag_start = rel_y - cursor_y
                print("[DECK BUILDER] Début du drag de la scrollbar")
            else:
                # Clic sur la piste de la scrollbar - sauter à la position
                scroll_ratio = rel_y / content_rect.height
                self.scroll_y = int(scroll_ratio * self.max_scroll)
                print(f"[DECK BUILDER] Scrollbar cliquée à la position {scroll_ratio:.2f}")
        
        return True
    
    def handle_scrollbar_drag(self, mouse_pos):
        """Gestion du drag de la scrollbar"""
        left_width = int(SCREEN_WIDTH * 0.8)
        content_rect = pygame.Rect(50, 200, left_width - 100, SCREEN_HEIGHT - 300)
        scrollbar_width = 20
        scrollbar_rect = pygame.Rect(content_rect.right - scrollbar_width, content_rect.top, scrollbar_width, content_rect.height)
        
        if not scrollbar_rect.collidepoint(mouse_pos):
            return
        
        # Calculer la position relative dans la scrollbar
        rel_y = mouse_pos[1] - scrollbar_rect.top - self.scrollbar_drag_start
        
        # Calculer la nouvelle position de scroll
        if self.max_scroll > 0:
            scroll_ratio = max(0, min(1, rel_y / (content_rect.height - 30)))  # 30 = hauteur minimale du curseur
            self.scroll_y = int(scroll_ratio * self.max_scroll)
    
    def handle_preview_click(self, mouse_pos):
        """Gestion des clics dans la zone de prévisualisation (colonne de droite)"""
        left_width = int(SCREEN_WIDTH * 0.8)
        right_width = SCREEN_WIDTH - left_width
        
        # Zone de prévisualisation
        preview_rect = pygame.Rect(left_width + 20, 200, right_width - 40, SCREEN_HEIGHT - 300)
        
        if not preview_rect.collidepoint(mouse_pos):
            return
        
        # Calculer la position relative dans la zone de prévisualisation
        rel_x = mouse_pos[0] - preview_rect.x
        rel_y = mouse_pos[1] - preview_rect.y
        
        # Initial y_offset for content (relative to preview_rect.y)
        current_hover_y_relative = 50 + 25 + 25 + 30  # 130 (titre + compteurs)
        
        # Vérifier le clic sur le héros
        if self.selected_hero:
            hero_line_height = 30
            hero_y_start = current_hover_y_relative
            hero_y_end = hero_y_start + hero_line_height
            
            if hero_y_start <= rel_y <= hero_y_end and 10 <= rel_x <= preview_rect.width - 10:
                self.selected_hero = None
                print(f"[DECK BUILDER] Héros retiré du deck")
                self.invalidate_cache()
                return
            current_hover_y_relative += hero_line_height
        
        # Vérifier le clic sur les unités
        if self.selected_units:
            line_height_units = self.get_cached_font(24).get_height() + 6
            units_y_start = current_hover_y_relative
            
            for i, unit in enumerate(self.selected_units):
                unit_y_start = units_y_start + i * line_height_units
                unit_y_end = unit_y_start + line_height_units
                
                if unit_y_start <= rel_y <= unit_y_end and 10 <= rel_x <= preview_rect.width - 10:
                    self.selected_units.pop(i)
                    print(f"[DECK BUILDER] Unité retirée du deck : {unit['name']}")
                    self.invalidate_cache()
                    return
            current_hover_y_relative += len(self.selected_units) * line_height_units + 5
        
        # Vérifier le clic sur les cartes
        if self.selected_cards:
            # Regrouper les cartes par nom
            card_counts = {}
            for card in self.selected_cards:
                card_name = card['name']
                card_counts[card_name] = card_counts.get(card_name, 0) + 1
            
            line_height_cards = self.get_cached_font(24).get_height() + 6
            cards_y_start = current_hover_y_relative
            
            for i, (card_name, count) in enumerate(card_counts.items()):
                card_y_start = cards_y_start + i * line_height_cards
                card_y_end = card_y_start + line_height_cards
                
                if card_y_start <= rel_y <= card_y_end and 10 <= rel_x <= preview_rect.width - 10:
                    # Retirer un exemplaire de cette carte
                    for j, selected_card in enumerate(self.selected_cards):
                        if selected_card['name'] == card_name:
                            self.selected_cards.pop(j)
                            print(f"[DECK BUILDER] Carte retirée du deck : {card_name} ({count-1}/2)")
                            break
                    self.invalidate_cache()
                    return
    def handle_right_click(self, mouse_pos):
        """Gère les clics droits pour afficher l'overlay d'informations"""
        # Vérifier d'abord la colonne de droite (prévisualisation)
        left_width = int(SCREEN_WIDTH * 0.8)
        right_width = SCREEN_WIDTH - left_width
        preview_rect = pygame.Rect(left_width + 20, 200, right_width - 40, SCREEN_HEIGHT - 300)
        
        if preview_rect.collidepoint(mouse_pos):
            # Clic droit dans la colonne de droite
            self.handle_right_click_preview(mouse_pos)
            return
        
        # Vérifier la colonne de gauche (liste des éléments)
        content_rect = pygame.Rect(50, 200, left_width - 100, SCREEN_HEIGHT - 300)
        
        if content_rect.collidepoint(mouse_pos):
            # Clic droit dans la colonne de gauche
            self.handle_right_click_content(mouse_pos)
            return
    
    def handle_right_click_preview(self, mouse_pos):
        """Gère les clics droits dans la zone de prévisualisation"""
        left_width = int(SCREEN_WIDTH * 0.8)
        right_width = SCREEN_WIDTH - left_width
        preview_rect = pygame.Rect(left_width + 20, 200, right_width - 40, SCREEN_HEIGHT - 300)
        
        rel_x = mouse_pos[0] - preview_rect.x
        rel_y = mouse_pos[1] - preview_rect.y
        
        # Initial y_offset for content (relative to preview_rect.y)
        current_y = 50 + 25 + 25 + 30  # 130 (titre + compteurs)
        
        # Vérifier le clic sur le héros
        if self.selected_hero:
            hero_line_height = 30
            if current_y <= rel_y <= current_y + hero_line_height and 10 <= rel_x <= preview_rect.width - 10:
                self.show_right_click_overlay(self.selected_hero, "hero")
                return
            current_y += hero_line_height
        
        # Vérifier le clic sur les unités
        if self.selected_units:
            line_height_units = self.get_cached_font(24).get_height() + 6
            
            for i, unit in enumerate(self.selected_units):
                unit_y_start = current_y + i * line_height_units
                unit_y_end = unit_y_start + line_height_units
                
                if unit_y_start <= rel_y <= unit_y_end and 10 <= rel_x <= preview_rect.width - 10:
                    self.show_right_click_overlay(unit, "unit")
                    return
            current_y += len(self.selected_units) * line_height_units + 5
        
        # Vérifier le clic sur les cartes
        if self.selected_cards:
            # Regrouper les cartes par nom
            card_counts = {}
            for card in self.selected_cards:
                card_name = card['name']
                card_counts[card_name] = card_counts.get(card_name, 0) + 1
            
            line_height_cards = self.get_cached_font(24).get_height() + 6
            
            for i, (card_name, count) in enumerate(card_counts.items()):
                card_y_start = current_y + i * line_height_cards
                card_y_end = card_y_start + line_height_cards
                
                if card_y_start <= rel_y <= card_y_end and 10 <= rel_x <= preview_rect.width - 10:
                    # Trouver la première carte avec ce nom
                    for card in self.selected_cards:
                        if card['name'] == card_name:
                            self.show_right_click_overlay(card, "card")
                            return
    
    def handle_right_click_content(self, mouse_pos):
        """Gère les clics droits dans la zone de contenu"""
        left_width = int(SCREEN_WIDTH * 0.8)
        content_rect = pygame.Rect(50, 200, left_width - 100, SCREEN_HEIGHT - 300)
        
        if not content_rect.collidepoint(mouse_pos):
            return
        
        # Position relative dans la zone de contenu
        rel_x = mouse_pos[0] - content_rect.x
        rel_y = mouse_pos[1] - content_rect.y + self.scroll_y
        
        # Déterminer quel élément est cliqué selon l'onglet actuel
        if self.current_tab == "heroes":
            self.handle_right_click_heroes(rel_x, rel_y)
        elif self.current_tab == "units":
            self.handle_right_click_units(rel_x, rel_y)
        elif self.current_tab == "cards":
            self.handle_right_click_cards(rel_x, rel_y)
    
    def handle_right_click_heroes(self, rel_x, rel_y):
        """Gère les clics droits sur les héros avec détection précise"""
        filtered_heroes = self.get_filtered_items()
        
        # Calculer la position dans la grille (6 colonnes)
        col = rel_x // 220
        row = rel_y // 320
        
        if 0 <= col < 6:
            index = row * 6 + col
            if 0 <= index < len(filtered_heroes):
                # Vérifier que le clic est bien dans la zone de la carte (200x288)
                card_x = col * 220 + 20
                card_y = row * 320 + 20
                
                # Si le clic est dans la zone de la carte
                if (card_x <= rel_x <= card_x + 200 and 
                    card_y <= rel_y <= card_y + 288):
                    self.show_right_click_overlay(filtered_heroes[index], "hero")
                    return
    
    def handle_right_click_units(self, rel_x, rel_y):
        """Gère les clics droits sur les unités avec détection précise"""
        filtered_units = self.get_filtered_items()
        
        # Calculer la position dans la grille (6 colonnes)
        col = rel_x // 220
        row = rel_y // 320
        
        if 0 <= col < 6:
            index = row * 6 + col
            if 0 <= index < len(filtered_units):
                # Vérifier que le clic est bien dans la zone de la carte (200x288)
                card_x = col * 220 + 20
                card_y = row * 320 + 20
                
                # Si le clic est dans la zone de la carte
                if (card_x <= rel_x <= card_x + 200 and 
                    card_y <= rel_y <= card_y + 288):
                    self.show_right_click_overlay(filtered_units[index], "unit")
                    return
    
    def handle_right_click_cards(self, rel_x, rel_y):
        """Gère les clics droits sur les cartes avec détection précise"""
        filtered_cards = self.get_filtered_items()
        
        # Calculer la position dans la grille (6 colonnes)
        col = rel_x // 220
        row = rel_y // 320
        
        if 0 <= col < 6:
            index = row * 6 + col
            if 0 <= index < len(filtered_cards):
                # Vérifier que le clic est bien dans la zone de la carte (200x288)
                card_x = col * 220 + 20
                card_y = row * 320 + 20
                
                # Si le clic est dans la zone de la carte
                if (card_x <= rel_x <= card_x + 200 and 
                    card_y <= rel_y <= card_y + 288):
                    self.show_right_click_overlay(filtered_cards[index], "card")
                    return
    
    def show_right_click_overlay(self, item, item_type):
        """Affiche l'overlay d'informations pour un élément"""
        # Couleurs de bordure selon le type
        border_colors = {
            'hero': COLORS['gold'],
            'unit': COLORS['royal_blue'],
            'card': COLORS['ruby_red']
        }
        border_color = border_colors.get(item_type, COLORS['white'])
        
        # Créer l'overlay selon le type d'élément
        if item_type == 'hero':
            self.right_click_overlay = self.create_hero_overlay_surface_high_res(item)
        elif item_type == 'unit':
            self.right_click_overlay = self.create_right_click_unit_overlay(item, border_color)
        elif item_type == 'card':
            self.right_click_overlay = self.create_right_click_card_overlay(item, border_color)
        
        self.right_click_overlay_type = item_type
        self.right_click_overlay_alpha = 255
    
    def update_right_click_overlay(self):
        """Met à jour l'overlay de clic droit"""
        if self.right_click_overlay is not None:
            # Animation d'apparition seulement
            if self.right_click_overlay_alpha < 255:
                self.right_click_overlay_alpha = min(255, self.right_click_overlay_alpha + 15)
    
    def draw_right_click_overlay(self, screen):
        """Dessine l'overlay de clic droit"""
        if self.right_click_overlay is not None and self.right_click_overlay_alpha > 0:
            # Fond semi-transparent noir à 80%
            overlay_bg = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay_bg.fill((0, 0, 0, 204))  # 204 = 80% de 255
            screen.blit(overlay_bg, (0, 0))
            
            # Appliquer l'alpha pour l'animation
            overlay_surface = self.right_click_overlay.copy()
            overlay_surface.set_alpha(self.right_click_overlay_alpha)
            
            # Positionner à 5 pixels de la bordure gauche, centré en hauteur
            overlay_rect = overlay_surface.get_rect(left=5, centery=SCREEN_HEIGHT // 2)
            screen.blit(overlay_surface, overlay_rect)
    
    def close_right_click_overlay(self):
        """Ferme l'overlay de clic droit"""
        self.right_click_overlay = None
        self.right_click_overlay_type = None
        self.right_click_overlay_alpha = 0
    

    
    def handle_content_click(self, mouse_pos):
        """Gestion des clics dans la zone de contenu"""
        left_width = int(SCREEN_WIDTH * 0.8)
        content_rect = pygame.Rect(50, 200, left_width - 100, SCREEN_HEIGHT - 300)
        
        if not content_rect.collidepoint(mouse_pos):
            return
        
        # Calculer la position relative
        rel_x = mouse_pos[0] - content_rect.x
        rel_y = mouse_pos[1] - content_rect.y + self.scroll_y
        
        # Gestion selon l'onglet actuel
        if self.current_tab == "heroes":
            self.handle_hero_click(rel_x, rel_y)
        elif self.current_tab == "units":
            self.handle_unit_click(rel_x, rel_y)
        elif self.current_tab == "cards":
            self.handle_card_click(rel_x, rel_y)
    
    def handle_hero_click(self, rel_x, rel_y):
        """Gestion des clics sur les héros"""
        filtered_heroes = self.filter_heroes()
        
        # Calculer la position dans la grille (6 colonnes)
        col = rel_x // 220
        row = rel_y // 320
        
        if 0 <= col < 6:
            index = row * 6 + col
            if 0 <= index < len(filtered_heroes):
                # Vérifier si on clique sur le même héros (pour le désélectionner)
                if self.selected_hero and self.selected_hero['name'] == filtered_heroes[index]['name']:
                    self.selected_hero = None
                    print(f"[DECK BUILDER] Héros désélectionné")
                else:
                    self.selected_hero = filtered_heroes[index]
                    print(f"[DECK BUILDER] Héros sélectionné : {self.selected_hero['name']}")
                
                # Invalider le cache car les sélections ont changé
                self.invalidate_cache()
    
    def handle_unit_click(self, rel_x, rel_y):
        """Gestion des clics sur les unités"""
        filtered_units = self.filter_units()
        
        # Calculer la position dans la grille (6 colonnes)
        col = rel_x // 220
        row = rel_y // 320
        
        if 0 <= col < 6:
            index = row * 6 + col
            if 0 <= index < len(filtered_units):
                unit = filtered_units[index]
                if unit in self.selected_units:
                    self.selected_units.remove(unit)
                    print(f"[DECK BUILDER] Unité retirée du deck : {unit['name']}")
                else:
                    # Vérifier la limite de 5 unités
                    if len(self.selected_units) >= 5:
                        print(f"[DECK BUILDER] Limite de 5 unités atteinte")
                        return
                    self.selected_units.append(unit)
                    print(f"[DECK BUILDER] Unité ajoutée au deck : {unit['name']}")
                
                # Invalider le cache car les sélections ont changé
                self.invalidate_cache()
    
    def get_card_count(self, card_name):
        """Retourne le nombre d'exemplaires d'une carte dans le deck"""
        return sum(1 for card in self.selected_cards if card['name'] == card_name)
    
    def handle_card_click(self, rel_x, rel_y):
        """Gestion des clics sur les cartes"""
        filtered_cards = self.filter_cards()
        
        # Calculer la position dans la grille (6 colonnes)
        col = rel_x // 220
        row = rel_y // 320
        
        if 0 <= col < 6:
            index = row * 6 + col
            if 0 <= index < len(filtered_cards):
                card = filtered_cards[index]
                card_name = card['name']
                current_count = self.get_card_count(card_name)
                
                # Vérifier la limite totale de cartes (30)
                if len(self.selected_cards) >= 30 and current_count == 0:
                    print(f"[DECK BUILDER] Limite de 30 cartes atteinte")
                    return
                
                if current_count < 2:
                    # Ajouter un exemplaire (max 2)
                    self.selected_cards.append(card)
                    print(f"[DECK BUILDER] Carte ajoutée au deck : {card_name} ({current_count+1}/2)")
                else:
                    print(f"[DECK BUILDER] Maximum d'exemplaires atteint pour : {card_name} (2/2)")
                
                # Invalider le cache car les sélections ont changé
                self.invalidate_cache()
    
    def save_deck(self):
        """Sauvegarde le deck"""
        if not self.deck_manager:
            print("[ERREUR] Gestionnaire de decks non disponible")
            return
        
        try:
            # Récupérer le deck actuel
            current_deck = self.deck_manager.get_current_deck()
            if not current_deck:
                print("[ERREUR] Aucun deck actuel. Créez d'abord un deck.")
                return
            
            # Mettre à jour le deck avec les données actuelles
            success = self.deck_manager.update_deck(
                name=current_deck.name,
                hero=self.selected_hero,
                units=self.selected_units,
                cards=self.selected_cards,
                customizations=self.customized_stats
            )
            
            if success:
                print(f"[DECK BUILDER] Deck '{current_deck.name}' sauvegardé avec succès")
            else:
                print("[ERREUR] Échec de la sauvegarde du deck")
                
        except Exception as e:
            print(f"[ERREUR] Erreur lors de la sauvegarde: {e}")
    
    def reset_deck(self):
        """Remet à zéro le deck"""
        self.selected_hero = None
        self.selected_units = []
        self.selected_cards = []
        self.customized_stats = {}
        self.invalidate_cache()
        print("[DECK BUILDER] Deck remis à zéro")
    
    def open_customization(self):
        """Ouvre l'écran de personnalisation du héros"""
        if self.selected_hero:
            # Forcer l'invalidation du cache avant d'ouvrir la personnalisation
            self.invalidate_cache()
            self._last_hero_customization = None
            
            self.game_ui.change_screen("hero_customization")
            # Passer les données du héros à l'écran de personnalisation
            hero_customization_screen = self.game_ui.screens.get("hero_customization")
            if hero_customization_screen:
                hero_customization_screen.set_hero_to_customize(self.selected_hero)
        else:
            print("[DECK BUILDER] Aucun héros sélectionné pour la personnalisation")
    
    def get_customized_hero(self):
        """Retourne le héros personnalisé"""
        if not self.selected_hero or not hero_customization_manager:
            return self.selected_hero
        
        hero_name = self.selected_hero.get("name", "Héros inconnu")
        
        # Vérifier si l'écran de personnalisation a des modifications en cours
        hero_customization_screen = self.game_ui.screens.get("hero_customization")
        if (hero_customization_screen and 
            hero_customization_screen.hero_to_customize and 
            hero_customization_screen.hero_to_customize.get("name") == hero_name and
            hero_customization_screen.customization):
            # Utiliser les modifications en cours de l'écran de personnalisation
            return hero_customization_manager.apply_customization_to_hero(
                self.selected_hero, 
                hero_customization_screen.customization
            )
        
        # Sinon, utiliser la personnalisation sauvegardée
        customization = hero_customization_manager.get_customization(hero_name)
        if customization:
            return hero_customization_manager.apply_customization_to_hero(self.selected_hero, customization)
        
        return self.selected_hero
    

    
    def draw(self, screen: pygame.Surface):
        """Dessin du deck builder"""
        # Le background est déjà dessiné par GameUI.draw_background()
        # Pas besoin de screen.fill() qui recouvrirait le background
        
        # Titre
        title = self.game_ui.font_large.render("CONSTRUCTEUR DE DECK", True, COLORS['gold'])
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 50))
        screen.blit(title, title_rect)
        
        # Onglets
        for i, tab in enumerate(self.tabs):
            # Couleur active
            if (self.current_tab == "heroes" and i == 0) or \
               (self.current_tab == "units" and i == 1) or \
               (self.current_tab == "cards" and i == 2):
                tab.color = COLORS['light_gold']
            else:
                tab.color = COLORS['dark_gray']
            tab.draw(screen)
        
        # Gestionnaire de deck
        self.draw_deck_manager(screen)
        
        # Interface en deux colonnes
        self.draw_left_column(screen)
        self.draw_right_column(screen)
        
        # Boutons d'action
        for button in self.buttons:
            button.draw(screen)
        
        # Dessiner l'overlay de hover au premier plan
        self.draw_hover_overlay(screen)
        
        # Dessiner l'overlay de clic droit au premier plan
        self.draw_right_click_overlay(screen)
        
        # Dessiner les tooltips
        self.draw_tooltips(screen)
    
    def draw_tooltips(self, screen):
        """Dessine les tooltips pour tous les boutons"""
        mouse_pos = pygame.mouse.get_pos()
        
        # Tooltips pour les boutons d'action
        for button in self.buttons:
            button.draw_tooltip(screen, mouse_pos)
        
        # Tooltips pour les boutons du gestionnaire de deck
        for button in self.deck_buttons:
            button.draw_tooltip(screen, mouse_pos)
        
        # Tooltips pour les onglets
        for tab in self.tabs:
            tab.draw_tooltip(screen, mouse_pos)
    
    def draw_deck_manager(self, screen):
        """Dessine le gestionnaire de deck"""
        left_width = int(SCREEN_WIDTH * 0.8)
        
        # Titre du gestionnaire
        title = self.game_ui.font_medium.render("GESTIONNAIRE DE DECK", True, COLORS['gold'])
        screen.blit(title, (left_width + 20, 80))
        
        # Zone du gestionnaire
        manager_rect = pygame.Rect(left_width + 20, 110, SCREEN_WIDTH - left_width - 40, 50)
        pygame.draw.rect(screen, COLORS['dark_gray'], manager_rect)
        pygame.draw.rect(screen, COLORS['gold'], manager_rect, 2)
        
        # Menu déroulant des decks
        if self.deck_dropdown:
            self.deck_dropdown.draw(screen)
        
        # Boutons du gestionnaire
        for button in self.deck_buttons:
            button.draw(screen)
        
        # Mode renommage
        if self.rename_mode:
            self.draw_rename_input(screen, manager_rect)
    
    def draw_rename_input(self, screen, manager_rect):
        """Dessine l'interface de renommage"""
        # Fond semi-transparent
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(COLORS['black'])
        screen.blit(overlay, (0, 0))
        
        # Zone de saisie
        input_rect = pygame.Rect(manager_rect.x + 50, manager_rect.y + 10, 200, 30)
        pygame.draw.rect(screen, COLORS['white'], input_rect)
        pygame.draw.rect(screen, COLORS['black'], input_rect, 2)
        
        # Texte de saisie
        font = self.game_ui.font_small
        text_surface = font.render(self.rename_text, True, COLORS['black'])
        screen.blit(text_surface, (input_rect.x + 5, input_rect.y + 5))
        
        # Curseur
        if len(self.rename_text) > 0:
            cursor_x = input_rect.x + 5 + font.size(self.rename_text[:self.rename_cursor_pos])[0]
            pygame.draw.line(screen, COLORS['black'], 
                           (cursor_x, input_rect.y + 5), 
                           (cursor_x, input_rect.y + 25), 2)
        
        # Instructions
        instruction = font.render("Appuyez sur Entrée pour valider, Échap pour annuler", True, COLORS['white'])
        screen.blit(instruction, (input_rect.x, input_rect.y + 40))
        
        # Boutons d'action
        for button in self.buttons:
            button.draw(screen)
        
        # Dessiner l'overlay de hover au premier plan
        self.draw_hover_overlay(screen)
        
        # Dessiner l'overlay de clic droit au premier plan
        self.draw_right_click_overlay(screen)
    
    def draw_left_column(self, screen):
        """Dessin de la colonne de gauche (80% de l'écran)"""
        left_width = int(SCREEN_WIDTH * 0.8)
        
        # Zone de contenu
        content_rect = pygame.Rect(50, 200, left_width - 100, SCREEN_HEIGHT - 300)
        pygame.draw.rect(screen, COLORS['royal_blue'], content_rect)
        pygame.draw.rect(screen, COLORS['gold'], content_rect, 2)
        
        # Zone de scroll pour le contenu
        scroll_content_rect = pygame.Rect(content_rect.x + 20, content_rect.y + 20, 
                                        content_rect.width - 60, content_rect.height - 40)
        
        # Utiliser le système de cache pour le contenu
        content_surface, total_content_height = self.get_cached_content_surface(scroll_content_rect)
        self.max_scroll = max(0, total_content_height - scroll_content_rect.height)
        
        # Limiter le scroll aux valeurs valides
        self.scroll_y = max(0, min(self.scroll_y, self.max_scroll))
        
        # Afficher la partie visible du contenu avec clipping
        visible_rect = pygame.Rect(0, self.scroll_y, scroll_content_rect.width, scroll_content_rect.height)
        screen.blit(content_surface, (scroll_content_rect.x, scroll_content_rect.y), visible_rect)
        
        # Scrollbar
        if self.max_scroll > 0:
            self.draw_scrollbar(screen, content_rect)
    
    def draw_right_column(self, screen):
        """Dessin de la colonne de droite (20% de l'écran)"""
        left_width = int(SCREEN_WIDTH * 0.8)
        right_width = SCREEN_WIDTH - left_width
        
        # Zone de prévisualisation
        preview_rect = pygame.Rect(left_width + 20, 200, right_width - 40, SCREEN_HEIGHT - 300)
        pygame.draw.rect(screen, COLORS['deep_blue'], preview_rect)
        pygame.draw.rect(screen, COLORS['gold'], preview_rect, 2)
        
        # Titre
        title = self.game_ui.font_medium.render("VOTRE DECK", True, COLORS['gold'])
        screen.blit(title, (preview_rect.x + 10, preview_rect.y + 10))
        
        # Contenu du deck
        y_offset = preview_rect.y + 50
        
        # Compteur Héros
        hero_count = "1" if self.selected_hero else "0"
        hero_count_text = f"Héros: {hero_count}/1"
        hero_count_surface = self.get_cached_font(24).render(hero_count_text, True, COLORS['white'])
        screen.blit(hero_count_surface, (preview_rect.x + 10, y_offset))
        y_offset += 25
        
        # Compteur Unités
        units_count_text = f"Unités: {len(self.selected_units)}/5"
        units_count_surface = self.get_cached_font(24).render(units_count_text, True, COLORS['white'])
        screen.blit(units_count_surface, (preview_rect.x + 10, y_offset))
        y_offset += 25
        
        # Compteur Cartes
        cards_count_text = f"Cartes: {len(self.selected_cards)}/30"
        cards_count_surface = self.get_cached_font(24).render(cards_count_text, True, COLORS['white'])
        screen.blit(cards_count_surface, (preview_rect.x + 10, y_offset))
        y_offset += 30
        
        # Héros sélectionné - seulement le nom
        if self.selected_hero:
            customized_hero = self.get_customized_hero()
            hero_color = COLORS['gold']
            hero_text = self.smart_truncate(customized_hero['name'], 30)
            hero_surface = self.get_cached_font(24).render(hero_text, True, hero_color)
            hero_rect = hero_surface.get_rect(topleft=(preview_rect.x + 10, y_offset))
            pygame.draw.rect(screen, COLORS['silver'], hero_rect.inflate(8, 4), 1)
            screen.blit(hero_surface, hero_rect)
            y_offset += 30
        
        # Unités sélectionnées - seulement les noms
        if self.selected_units:
            unit_color = COLORS['orange']
            for unit in self.selected_units:
                unit_text = self.smart_truncate(unit['name'], 30)
                unit_surface = self.get_cached_font(24).render(unit_text, True, unit_color)
                unit_rect = unit_surface.get_rect(topleft=(preview_rect.x + 10, y_offset))
                pygame.draw.rect(screen, COLORS['silver'], unit_rect.inflate(8, 4), 1)
                screen.blit(unit_surface, unit_rect)
                y_offset += self.get_cached_font(24).get_height() + 6
            y_offset += 5
        
        # Cartes sélectionnées - regrouper par nom et afficher les quantités
        if self.selected_cards:
            card_color = COLORS['white']
            
            # Regrouper les cartes par nom
            card_counts = {}
            for card in self.selected_cards:
                card_name = card['name']
                card_counts[card_name] = card_counts.get(card_name, 0) + 1
            
            # Afficher toutes les cartes groupées
            for card_name, count in card_counts.items():
                card_text = self.smart_truncate(card_name, 25)  # Réduire pour laisser de la place au compteur
                if count > 1:
                    card_text += f" (x{count})"
                
                card_surface = self.get_cached_font(24).render(card_text, True, card_color)
                card_rect = card_surface.get_rect(topleft=(preview_rect.x + 10, y_offset))
                pygame.draw.rect(screen, COLORS['silver'], card_rect.inflate(8, 4), 1)
                screen.blit(card_surface, card_rect)
                y_offset += self.get_cached_font(24).get_height() + 6
    
    def draw_scrollbar(self, screen, content_rect):
        """Dessine la scrollbar"""
        scrollbar_width = 20
        scrollbar_rect = pygame.Rect(content_rect.right - scrollbar_width, content_rect.top, scrollbar_width, content_rect.height)
        
        # Fond de la scrollbar
        pygame.draw.rect(screen, COLORS['dark_gray'], scrollbar_rect)
        pygame.draw.rect(screen, COLORS['white'], scrollbar_rect, 1)
        
        # Curseur de la scrollbar
        if self.max_scroll > 0:
            cursor_height = max(30, (content_rect.height / (self.max_scroll + content_rect.height)) * content_rect.height)
            cursor_y = content_rect.top + (self.scroll_y / self.max_scroll) * (content_rect.height - cursor_height)
            cursor_rect = pygame.Rect(scrollbar_rect.x, cursor_y, scrollbar_width, cursor_height)
            
            # Couleur du curseur selon l'état
            if self.scrollbar_dragging:
                cursor_color = COLORS['light_gold']
            else:
                cursor_color = COLORS['gold']
            
            pygame.draw.rect(screen, cursor_color, cursor_rect)
            pygame.draw.rect(screen, COLORS['white'], cursor_rect, 1)
            
            # Ajouter des détails visuels au curseur
            if cursor_height > 40:
                # Ligne centrale pour indiquer la position
                center_y = cursor_y + cursor_height // 2
                pygame.draw.line(screen, COLORS['white'], 
                               (scrollbar_rect.x + 5, center_y), 
                               (scrollbar_rect.x + scrollbar_width - 5, center_y), 2)
    
    def draw_heroes_list(self, screen, content_rect):
        """Dessine la liste des héros (version avec scroll)"""
        filtered_heroes = self.filter_heroes()
        
        for i, hero in enumerate(filtered_heroes):
            col = i % 6
            row = i // 6
            
            x = col * 220 + 20
            y = row * 320 + 20 - self.scroll_y
            
            # Vérifier si la carte est visible dans la zone de contenu
            if y + 288 < 0 or y > content_rect.height:
                continue
            
            # Fond de la carte
            card_rect = pygame.Rect(x, y, 200, 288)
            
            # Image du héros
            hero_image_path = hero.get('image_path', 'Hero/1.png')
            hero_image = self.game_ui.asset_manager.get_image(hero_image_path)
            
            if hero_image:
                scaled_image = pygame.transform.scale(hero_image, (200, 288))
                image_rect = scaled_image.get_rect(topleft=(x, y))
                screen.blit(scaled_image, image_rect)
            
            # Overlay permanent - version simplifiée
            overlay_surface = pygame.Surface((200, 288), pygame.SRCALPHA)
            pygame.draw.rect(overlay_surface, COLORS['gold'], (0, 0, 200, 288), 2, border_radius=10)
            
            # Nom
            name_text = hero['name'].split(',')[0].strip()
            name_surface = self.get_cached_font(22).render(name_text, True, COLORS['white'])
            name_rect = name_surface.get_rect(centerx=100, y=20)
            overlay_surface.blit(name_surface, name_rect)
            
            # Stats
            hp = hero.get('hp', 0)
            attack = hero.get('attack', 0)
            defense = hero.get('defense', 0)
            stats_text = f"HP: {hp} | ATK: {attack} | DEF: {defense}"
            stats_surface = self.get_cached_font(14).render(stats_text, True, COLORS['light_gold'])
            stats_rect = stats_surface.get_rect(centerx=100, y=238)
            overlay_surface.blit(stats_surface, stats_rect)
            
            overlay_rect = overlay_surface.get_rect(topleft=(x, y))
            screen.blit(overlay_surface, overlay_rect)
            
            # Indicateur de sélection
            if self.selected_hero == hero:
                pygame.draw.rect(screen, COLORS['gold'], card_rect, 4)
    
    def draw_units_list(self, screen, content_rect):
        """Dessine la liste des unités (version avec scroll)"""
        filtered_units = self.filter_units()
        
        for i, unit in enumerate(filtered_units):
            col = i % 6
            row = i // 6
            
            x = col * 220 + 20
            y = row * 320 + 20 - self.scroll_y
            
            # Vérifier si la carte est visible dans la zone de contenu
            if y + 288 < 0 or y > content_rect.height:
                continue
            
            # Fond de la carte
            card_rect = pygame.Rect(x, y, 200, 288)
            
            # Image de l'unité
            unit_image_path = unit.get('image_path', 'Crea/1.png')
            unit_image = self.game_ui.asset_manager.get_image(unit_image_path)
            
            if unit_image:
                scaled_image = pygame.transform.scale(unit_image, (200, 288))
                image_rect = scaled_image.get_rect(topleft=(x, y))
                screen.blit(scaled_image, image_rect)
            
            # Overlay permanent
            overlay_surface = self.create_unit_overlay_surface(unit)
            overlay_rect = overlay_surface.get_rect(topleft=(x, y))
            screen.blit(overlay_surface, overlay_rect)
            
            # Indicateur de sélection
            if unit in self.selected_units:
                pygame.draw.rect(screen, COLORS['gold'], card_rect, 4)
    
    def draw_cards_list(self, screen, content_rect):
        """Dessine la liste des cartes (version avec scroll)"""
        filtered_cards = self.filter_cards()
        
        for i, card in enumerate(filtered_cards):
            col = i % 6
            row = i // 6
            
            x = col * 220 + 20
            y = row * 320 + 20 - self.scroll_y
            
            # Vérifier si la carte est visible dans la zone de contenu
            if y + 288 < 0 or y > content_rect.height:
                continue
            
            # Fond de la carte
            card_rect = pygame.Rect(x, y, 200, 288)
            pygame.draw.rect(screen, COLORS['dark_gray'], card_rect)
            pygame.draw.rect(screen, COLORS['gold'], card_rect, 2)
            
            # Image de la carte (utiliser le dos de carte par défaut)
            card_image = self.game_ui.asset_manager.get_image("Carte/DosCarte1")
            if card_image:
                # Redimensionner l'image selon la documentation : 80x115 pixels pour le dos de carte
                scaled_image = pygame.transform.scale(card_image, (80, 115))
                image_rect = scaled_image.get_rect(center=(x + 150, y + 150))
                screen.blit(scaled_image, image_rect)
            
            # Nom de la carte
            name_text = self.smart_truncate(card['name'], 20)
            name_surface = self.get_cached_font(20).render(name_text, True, COLORS['white'])
            name_rect = name_surface.get_rect(center=(x + 150, y + 290))
            screen.blit(name_surface, name_rect)
            
            # Coût
            if 'cost' in card:
                cost_text = f"Coût: {card['cost']} mana"
                cost_surface = self.get_cached_font(16).render(cost_text, True, COLORS['light_blue'])
                cost_rect = cost_surface.get_rect(center=(x + 150, y + 80))
                screen.blit(cost_surface, cost_rect)
            
            # Indicateur de sélection avec nombre d'exemplaires
            card_count = self.get_card_count(card['name'])
            if card_count > 0:
                # Bordure colorée selon le nombre d'exemplaires
                if card_count == 1:
                    border_color = COLORS['gold']
                else:  # card_count == 2
                    border_color = COLORS['green']
                
                pygame.draw.rect(screen, border_color, card_rect, 4)
                
                # Afficher le nombre d'exemplaires
                count_text = f"{card_count}/2"
                count_surface = self.get_cached_font(18).render(count_text, True, border_color)
                count_rect = count_surface.get_rect(topright=(x + 195, y + 5))
                screen.blit(count_surface, count_rect)
    
    def handle_right_column_hover(self, mouse_pos):
        """Gère la détection du hover dans la colonne de droite"""
        left_width = int(SCREEN_WIDTH * 0.8)
        right_width = SCREEN_WIDTH - left_width
        
        # Zone de prévisualisation
        preview_rect = pygame.Rect(left_width + 20, 200, right_width - 40, SCREEN_HEIGHT - 300)
        
        if not preview_rect.collidepoint(mouse_pos):
            # Souris en dehors de la zone, arrêter le hover
            if self.hovered_item is not None:
                self.hovered_item = None
                self.hovered_item_type = None
            return
        
        # Calculer la position relative dans la zone de prévisualisation
        rel_x = mouse_pos[0] - preview_rect.x
        rel_y = mouse_pos[1] - preview_rect.y
        
        # Initial y_offset for content (relative to preview_rect.y)
        # This corresponds to preview_rect.y + 50 (title) + 25 (hero count) + 25 (units count) + 30 (cards count)
        current_hover_y_relative = 50 + 25 + 25 + 30 # This is 130

        # Get the actual line height for font size 24 for units/cards
        # This is the height of each item line (name + border)
        line_height_units_cards = self.get_cached_font(24).get_height() + 6 
        
        # Vérifier le hover sur le héros
        if self.selected_hero:
            hero_line_height = 30 # Explicitly 30 in draw_right_column
            hero_y_start = current_hover_y_relative
            hero_y_end = hero_y_start + hero_line_height
            
            if hero_y_start <= rel_y <= hero_y_end:
                # Utiliser le héros personnalisé pour le hover
                customized_hero = self.get_customized_hero()
                if self.hovered_item != customized_hero or self.hovered_item_type != 'hero':
                    self.hovered_item = customized_hero
                    self.hovered_item_type = 'hero'
                return
            current_hover_y_relative += hero_line_height # Advance y_offset after hero
        
        # Vérifier le hover sur les unités
        if self.selected_units:
            units_y_start = current_hover_y_relative
            units_total_height = len(self.selected_units) * line_height_units_cards
            units_y_end = units_y_start + units_total_height
            
            if units_y_start <= rel_y <= units_y_end:
                unit_index = (rel_y - units_y_start) // line_height_units_cards
                if 0 <= unit_index < len(self.selected_units):
                    unit = self.selected_units[unit_index]
                    if self.hovered_item != unit or self.hovered_item_type != 'unit':
                        self.hovered_item = unit
                        self.hovered_item_type = 'unit'
                    return
            current_hover_y_relative += units_total_height # Advance y_offset after all units
            current_hover_y_relative += 5 # Add the 5px spacing after the units block
        
        # Vérifier le hover sur les cartes
        if self.selected_cards:
            cards_y_start = current_hover_y_relative
            cards_total_height = min(10, len(self.selected_cards)) * line_height_units_cards
            cards_y_end = cards_y_start + cards_total_height
            
            if cards_y_start <= rel_y <= cards_y_end:
                card_index = (rel_y - cards_y_start) // line_height_units_cards
                if 0 <= card_index < min(10, len(self.selected_cards)):
                    card = self.selected_cards[card_index]
                    if self.hovered_item != card or self.hovered_item_type != 'card':
                        self.hovered_item = card
                        self.hovered_item_type = 'card'
                    return
        
        # Aucun élément survolé
        if self.hovered_item is not None:
            self.hovered_item = None
            self.hovered_item_type = None
    
    def draw_hover_overlay(self, screen):
        """Dessine l'overlay de hover centré à l'écran avec image et descriptions sur le côté"""
        if self.hovered_item is None or self.hover_animation_alpha == 0:
            return
        
        # Couleurs de bordure selon le type
        border_colors = {
            'hero': COLORS['gold'],
            'unit': COLORS['royal_blue'],
            'card': COLORS['ruby_red']
        }
        border_color = border_colors.get(self.hovered_item_type, COLORS['white'])
        
        # Créer l'overlay selon le type d'élément
        if self.hovered_item_type == 'hero':
            overlay_surface = self.create_hover_hero_overlay(self.hovered_item, border_color)
        elif self.hovered_item_type == 'unit':
            overlay_surface = self.create_hover_unit_overlay(self.hovered_item, border_color)
        elif self.hovered_item_type == 'card':
            overlay_surface = self.create_hover_card_overlay(self.hovered_item, border_color)
        else:
            return
        
        # Appliquer l'alpha pour l'animation
        overlay_surface.set_alpha(self.hover_animation_alpha)
        
        # Aligner l'overlay à gauche avec 5 pixels de marge
        overlay_rect = overlay_surface.get_rect(topleft=(5, (SCREEN_HEIGHT - overlay_surface.get_height()) // 2))
        screen.blit(overlay_surface, overlay_rect)
    def create_hover_hero_overlay(self, hero, border_color):
        """Crée l'overlay de hover pour un héros avec image et descriptions sur le côté"""
        # Utiliser le héros personnalisé si disponible
        customized_hero = self.get_customized_hero() if hero == self.selected_hero else hero
        
        # Taille de l'overlay (80% de l'écran)
        overlay_width = int(SCREEN_WIDTH * 0.8)
        overlay_height = int(SCREEN_HEIGHT * 0.8)
        
        # Créer la surface avec transparence
        overlay_surface = pygame.Surface((overlay_width, overlay_height), pygame.SRCALPHA)
        
        # Fond semi-transparent
        pygame.draw.rect(overlay_surface, (*COLORS['deep_black'], 230), (0, 0, overlay_width, overlay_height), border_radius=20)
        
        # Bordure colorée
        pygame.draw.rect(overlay_surface, border_color, (0, 0, overlay_width, overlay_height), 4, border_radius=20)
        
        # Diviser l'overlay en deux parties : image à gauche, descriptions à droite
        image_width = int(overlay_width * 0.4)  # 40% pour l'image
        desc_width = overlay_width - image_width - 40  # 60% pour les descriptions
        margin = 20
        
        # Zone de l'image (centrée à gauche)
        image_x = margin
        image_y = margin
        image_height = overlay_height - 2 * margin
        
        # Charger et afficher l'image du héros
        if 'image_path' in customized_hero:
            hero_image = self.game_ui.asset_manager.get_image(customized_hero['image_path'])
            if hero_image:
                # Redimensionner l'image pour s'adapter à la zone
                scaled_image = pygame.transform.scale(hero_image, (image_width, image_height))
                
                # Créer une surface avec coins arrondis pour l'image
                image_surface = pygame.Surface((image_width, image_height), pygame.SRCALPHA)
                
                # Créer un masque avec coins arrondis précis
                mask_surface = self.create_rounded_mask(image_width, image_height, 20)
                
                # Appliquer le masque à l'image
                image_surface.blit(scaled_image, (0, 0))
                image_surface.blit(mask_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                
                overlay_surface.blit(image_surface, (image_x, image_y))
            else:
                # Image par défaut si pas trouvée
                default_surface = pygame.Surface((image_width, image_height))
                default_surface.fill(COLORS['dark_gray'])
                overlay_surface.blit(default_surface, (image_x, image_y))
        
        # Zone des descriptions (à droite)
        desc_x = image_x + image_width + 20
        desc_y = margin + 20
        y_offset = desc_y
        
        # Nom du héros
        name_text = customized_hero['name']
        name_surface = self.get_cached_font(36).render(name_text, True, COLORS['white'])
        name_rect = name_surface.get_rect(topleft=(desc_x, y_offset))
        
        # Fond pour le nom
        name_bg_rect = pygame.Rect(name_rect.x - 10, name_rect.y - 5, name_rect.width + 20, name_rect.height + 10)
        pygame.draw.rect(overlay_surface, (*COLORS['deep_black'], 200), name_bg_rect, border_radius=8)
        overlay_surface.blit(name_surface, name_rect)
        y_offset += 60
        
        # Élément avec symbole
        if 'element' in customized_hero and customized_hero['element']:
            # Mapping des noms d'éléments vers les noms de fichiers
            element_mapping = {
                'feu': 'feu',
                'eau': 'eau',
                'glace': 'glace',
                'terre': 'terre',
                'air': 'air',
                'foudre': 'foudre',
                'lumière': 'lumiere',
                'ténèbres': 'tenebres',
                'arcanique': 'arcane',
                'poison': 'poison',
                'néant': 'neant'
            }
            
            element_name = customized_hero['element'].lower()
            file_name = element_mapping.get(element_name, element_name)
            element_symbol_path = f"Symbols/{file_name}.png"
            element_symbol = self.game_ui.asset_manager.get_image(element_symbol_path)
            
            if element_symbol:
                # Afficher le symbole d'élément
                symbol_size = (48, 48)
                scaled_symbol = pygame.transform.scale(element_symbol, symbol_size)
                symbol_rect = scaled_symbol.get_rect(topleft=(desc_x, y_offset))
                
                # Fond pour le symbole
                symbol_bg_rect = pygame.Rect(symbol_rect.x - 5, symbol_rect.y - 5, symbol_rect.width + 10, symbol_rect.height + 10)
                pygame.draw.rect(overlay_surface, (*COLORS['deep_black'], 200), symbol_bg_rect, border_radius=8)
                overlay_surface.blit(scaled_symbol, symbol_rect)
            else:
                # Fallback vers le texte si le symbole n'est pas trouvé
                element_text = f"Élément: {hero['element']}"
                element_surface = self.get_cached_font(24).render(element_text, True, COLORS['light_gold'])
                element_rect = element_surface.get_rect(topleft=(desc_x, y_offset))
                
                # Fond pour le texte d'élément
                element_bg_rect = pygame.Rect(element_rect.x - 10, element_rect.y - 5, element_rect.width + 20, element_rect.height + 10)
                pygame.draw.rect(overlay_surface, (*COLORS['deep_black'], 200), element_bg_rect, border_radius=8)
                overlay_surface.blit(element_surface, element_rect)
            y_offset += 60
        
        # Stats primaires (avec personnalisation)
        base_stats = hero.get('base_stats', {})
        hp = hero.get('hp', base_stats.get('hp', 100))
        attack = hero.get('attack', base_stats.get('attack', 10))
        defense = hero.get('defense', base_stats.get('defense', 5))
        
        stats_text = f"HP: {hp} | ATK: {attack} | DEF: {defense}"
        stats_surface = self.get_cached_font(24).render(stats_text, True, COLORS['light_gold'])
        stats_rect = stats_surface.get_rect(topleft=(desc_x, y_offset))
        
        # Fond pour les stats
        stats_bg_rect = pygame.Rect(stats_rect.x - 10, stats_rect.y - 5, stats_rect.width + 20, stats_rect.height + 10)
        pygame.draw.rect(overlay_surface, (*COLORS['deep_black'], 200), stats_bg_rect, border_radius=8)
        overlay_surface.blit(stats_surface, stats_rect)
        y_offset += 40
        
        # Stats secondaires
        secondary_stats = []
        if 'crit_pct' in hero:
            secondary_stats.append(f"Crit: {hero['crit_pct']}%")
        if 'esquive_pct' in hero:
            secondary_stats.append(f"Esq: {hero['esquive_pct']}%")
        if 'precision_pct' in hero:
            secondary_stats.append(f"Préc: {hero['precision_pct']}%")
        
        if secondary_stats:
            secondary_stats_text = " | ".join(secondary_stats)
            secondary_stats_surface = self.get_cached_font(20).render(secondary_stats_text, True, COLORS['light_blue'])
            secondary_stats_rect = secondary_stats_surface.get_rect(topleft=(desc_x, y_offset))
            
            # Fond pour les stats secondaires
            secondary_stats_bg_rect = pygame.Rect(secondary_stats_rect.x - 10, secondary_stats_rect.y - 5, secondary_stats_rect.width + 20, secondary_stats_rect.height + 10)
            pygame.draw.rect(overlay_surface, (*COLORS['deep_black'], 200), secondary_stats_bg_rect, border_radius=8)
            overlay_surface.blit(secondary_stats_surface, secondary_stats_rect)
        y_offset += 40
        
        # Capacité (selon la personnalisation)
        hero_name = customized_hero.get("name", "Héros inconnu")
        customization = None
        if hero_customization_manager:
            customization = hero_customization_manager.get_customization(hero_name)
        
        if customization and customization.use_hero_ability:
            # Capacité du héros
            if 'ability_name' in customized_hero and customized_hero['ability_name']:
                ability_name = customized_hero['ability_name']
                ability_surface = self.get_cached_font(28).render(ability_name, True, COLORS['crimson'])
                ability_rect = ability_surface.get_rect(topleft=(desc_x, y_offset))
                
                # Fond pour la capacité
                ability_bg_rect = pygame.Rect(ability_rect.x - 10, ability_rect.y - 5, ability_rect.width + 20, ability_rect.height + 10)
                pygame.draw.rect(overlay_surface, (*COLORS['deep_black'], 200), ability_bg_rect, border_radius=8)
                overlay_surface.blit(ability_surface, ability_rect)
                y_offset += 40
            
            # Description de la capacité du héros
            if 'ability_description' in customized_hero and customized_hero['ability_description']:
                ability_desc = customized_hero['ability_description']
                
                # Zone pour la description avec retour à la ligne intelligent
                desc_rect = pygame.Rect(desc_x, y_offset, desc_width - 20, 200)  # Hauteur limitée à 200px
                
                # Fond pour la zone de description
                desc_bg_rect = pygame.Rect(desc_rect.x - 10, desc_rect.y - 5, desc_rect.width + 20, desc_rect.height + 10)
                pygame.draw.rect(overlay_surface, (*COLORS['deep_black'], 200), desc_bg_rect, border_radius=8)
                
                # Dessiner le texte avec retour à la ligne intelligent
                used_height = self.draw_wrapped_text(overlay_surface, ability_desc, self.get_cached_font(24), COLORS['white'], desc_rect, line_spacing=8)
                y_offset += used_height + 20
            
            # Cooldown de la capacité du héros
            if 'ability_cooldown' in customized_hero and customized_hero['ability_cooldown'] > 0:
                cooldown_text = f"Cooldown: {customized_hero['ability_cooldown']} tours"
                cooldown_surface = self.get_cached_font(24).render(cooldown_text, True, COLORS['light_blue'])
                cooldown_rect = cooldown_surface.get_rect(topleft=(desc_x, y_offset))
                
                # Fond pour le cooldown
                cooldown_bg_rect = pygame.Rect(cooldown_rect.x - 10, cooldown_rect.y - 5, cooldown_rect.width + 20, cooldown_rect.height + 10)
                pygame.draw.rect(overlay_surface, (*COLORS['deep_black'], 200), cooldown_bg_rect, border_radius=8)
                overlay_surface.blit(cooldown_surface, cooldown_rect)
                y_offset += 40
        else:
            # Attaque basique
            ability_name = "Attaque basique"
            ability_surface = self.get_cached_font(28).render(ability_name, True, (0, 255, 0))
            ability_rect = ability_surface.get_rect(topleft=(desc_x, y_offset))
            
            # Fond pour la capacité
            ability_bg_rect = pygame.Rect(ability_rect.x - 10, ability_rect.y - 5, ability_rect.width + 20, ability_rect.height + 10)
            pygame.draw.rect(overlay_surface, (*COLORS['deep_black'], 200), ability_bg_rect, border_radius=8)
            overlay_surface.blit(ability_surface, ability_rect)
            y_offset += 40
            
            # Description de l'attaque basique
            basic_cooldown = customized_hero.get('basic_attack_cooldown', 1)
            ability_desc = f"Attaque basique : Inflige des dégâts physiques à l'ennemi ciblé. Cooldown de {basic_cooldown} tour(s)."
            lines = self.smart_wrap_text(ability_desc, self.get_cached_font(36), desc_width - 20)
            
            # Afficher les lignes (limitées à 4 lignes)
            for i, line in enumerate(lines[:4]):
                desc_surface = self.get_cached_font(36).render(line, True, COLORS['white'])
                desc_rect = desc_surface.get_rect(topleft=(desc_x, y_offset))
                
                # Fond pour chaque ligne de description
                desc_bg_rect = pygame.Rect(desc_rect.x - 5, desc_rect.y - 2, desc_rect.width + 10, desc_rect.height + 4)
                pygame.draw.rect(overlay_surface, (*COLORS['deep_black'], 200), desc_bg_rect, border_radius=5)
                overlay_surface.blit(desc_surface, desc_rect)
                y_offset += 50
            
            if len(lines) > 4:
                more_text = "..."
                more_surface = self.get_cached_font(36).render(more_text, True, COLORS['gray'])
                more_rect = more_surface.get_rect(topleft=(desc_x, y_offset))
                
                # Fond pour le texte "..."
                more_bg_rect = pygame.Rect(more_rect.x - 5, more_rect.y - 2, more_rect.width + 10, more_rect.height + 4)
                pygame.draw.rect(overlay_surface, (*COLORS['deep_black'], 200), more_bg_rect, border_radius=5)
                overlay_surface.blit(more_surface, more_rect)
            y_offset += 20
            
            # Cooldown de l'attaque basique
            if basic_cooldown > 0:
                cooldown_text = f"Cooldown: {basic_cooldown} tour(s)"
                cooldown_surface = self.get_cached_font(24).render(cooldown_text, True, COLORS['light_blue'])
                cooldown_rect = cooldown_surface.get_rect(topleft=(desc_x, y_offset))
                
                # Fond pour le cooldown
                cooldown_bg_rect = pygame.Rect(cooldown_rect.x - 10, cooldown_rect.y - 5, cooldown_rect.width + 20, cooldown_rect.height + 10)
                pygame.draw.rect(overlay_surface, (*COLORS['deep_black'], 200), cooldown_bg_rect, border_radius=8)
                overlay_surface.blit(cooldown_surface, cooldown_rect)
                y_offset += 40
        
        # Capacité passive
        if 'passive' in customized_hero and customized_hero['passive']:
            # Vérifier si le passif est activé dans la personnalisation
            is_passive_active = False
            if customization:
                is_passive_active = customization.has_passive
            
            # Texte du passif avec statut
            if is_passive_active:
                passive_text = f"Passif (ACTIVÉ): {customized_hero['passive']}"
                passive_color = COLORS['purple']
            else:
                passive_text = f"Passif (DÉSACTIVÉ): {customized_hero['passive']}"
                passive_color = COLORS['gray']
            
            # Zone pour la description du passif avec retour à la ligne intelligent
            passive_rect = pygame.Rect(desc_x, y_offset, desc_width - 20, 150)  # Hauteur limitée à 150px
            
            # Fond pour la zone de passif
            passive_bg_rect = pygame.Rect(passive_rect.x - 10, passive_rect.y - 5, passive_rect.width + 20, passive_rect.height + 10)
            pygame.draw.rect(overlay_surface, (*COLORS['deep_black'], 200), passive_bg_rect, border_radius=8)
            
            # Dessiner le texte avec retour à la ligne intelligent
            used_height = self.draw_wrapped_text(overlay_surface, passive_text, self.get_cached_font(20), passive_color, passive_rect, line_spacing=6)
            y_offset += used_height + 20
        
        return overlay_surface
    def create_unit_overlay_surface(self, unit):
        """Crée une surface d'overlay pour une unité"""
        overlay_width = 200  # Même largeur que la carte
        overlay_height = 288  # Même hauteur que la carte
        
        overlay_surface = pygame.Surface((overlay_width, overlay_height), pygame.SRCALPHA)

        # Définir desc_x pour les éléments qui en ont besoin
        desc_x = 20
        
        # Bordure de la carte
        pygame.draw.rect(overlay_surface, COLORS['royal_blue'], (0, 0, overlay_width, overlay_height), 2, border_radius=10)
        
        # Nom de l'unité - seulement avant la virgule, à 8% de la hauteur
        name_text = unit['name'].split(',')[0].strip()  # Prendre seulement avant la virgule
        name_y = int(overlay_height * 0.08)  # 8% de la hauteur
        name_surface = self.get_cached_font(22).render(name_text, True, COLORS['white'])
        name_rect = name_surface.get_rect(centerx=overlay_width//2, y=name_y)
        
        # Fond pour le nom
        name_bg_rect = pygame.Rect(name_rect.x - 5, name_rect.y - 2, name_rect.width + 10, name_rect.height + 4)
        pygame.draw.rect(overlay_surface, (*COLORS['deep_black'], 200), name_bg_rect, border_radius=5)
        overlay_surface.blit(name_surface, name_rect)
        
        # Élément avec symbole - dans le coin avec fond circulaire
        if 'element' in unit and unit['element']:
            # Mapping des noms d'éléments vers les noms de fichiers
            element_mapping = {
                'feu': 'feu',
                'eau': 'eau',
                'glace': 'glace',
                'terre': 'terre',
                'air': 'air',
                'foudre': 'foudre',
                'lumière': 'lumiere',
                'ténèbres': 'tenebres',
                'arcanique': 'arcane',
                'poison': 'poison',
                'néant': 'neant'
            }
            
            element_name = unit['element'].lower()
            file_name = element_mapping.get(element_name, element_name)
            element_symbol_path = f"Symbols/{file_name}.png"
            element_symbol = self.game_ui.asset_manager.get_image(element_symbol_path)
            
            if element_symbol:
                # Afficher le symbole d'élément dans le coin
                symbol_size = (24, 24)
                scaled_symbol = pygame.transform.scale(element_symbol, symbol_size)
                symbol_rect = scaled_symbol.get_rect(topleft=(10, 10))  # Coin supérieur gauche
                
                # Fond circulaire pour le symbole
                circle_radius = 15
                circle_center = (symbol_rect.centerx, symbol_rect.centery)
                pygame.draw.circle(overlay_surface, (*COLORS['deep_black'], 200), circle_center, circle_radius)
                overlay_surface.blit(scaled_symbol, symbol_rect)
            else:
                # Fallback vers le texte si le symbole n'est pas trouvé
                element_text = f"Élément: {unit['element']}"
                element_surface = self.get_cached_font(12).render(element_text, True, COLORS['light_gold'])
                element_rect = element_surface.get_rect(topleft=(10, 10))
                
                # Fond circulaire pour le texte d'élément
                circle_radius = 15
                circle_center = (element_rect.centerx, element_rect.centery)
                pygame.draw.circle(overlay_surface, (*COLORS['deep_black'], 200), circle_center, circle_radius)
                overlay_surface.blit(element_surface, element_rect)
        
        # Rareté - tout en bas avec fond ovale coloré
        rarity_y = overlay_height - 30  # Tout en bas
        if 'rarity' in unit:
            rarity_text = unit['rarity']
            rarity_surface = self.get_cached_font(11).render(rarity_text, True, COLORS['white'])
            rarity_rect = rarity_surface.get_rect(centerx=overlay_width//2, y=rarity_y)
            
            # Couleur de rareté
            rarity_colors = {
                'Commun': COLORS['gray'],
                'Peu Commun': COLORS['green'],
                'Rare': COLORS['royal_blue'],
                'Épique': COLORS['crimson'],
                'Héros': COLORS['orange'],
                'Mythique': COLORS['gold'],
                'Spécial': COLORS['cyan'],
                'commun': COLORS['gray'],
                'peu commun': COLORS['green'],
                'rare': COLORS['royal_blue'],
                'épique': COLORS['crimson'],
                'héros': COLORS['orange'],
                'mythique': COLORS['gold'],
                'spécial': COLORS['cyan'],
            }
            rarity_color = rarity_colors.get(rarity_text, COLORS['gray'])
            
            # Fond ovale pour la rareté
            oval_width = rarity_rect.width + 20
            oval_height = rarity_rect.height + 8
            oval_rect = pygame.Rect(rarity_rect.centerx - oval_width//2, rarity_rect.centery - oval_height//2, oval_width, oval_height)
            pygame.draw.ellipse(overlay_surface, (*rarity_color, 200), oval_rect)
            overlay_surface.blit(rarity_surface, rarity_rect)
        
        # Stats secondaires - au-dessus de la rareté avec 1% d'espace
        secondary_stats_y = rarity_y - 20 - int(overlay_height * 0.01)  # 1% d'espace
        secondary_stats = []
        if 'crit_pct' in unit:
            secondary_stats.append(f"Crit: {unit['crit_pct']}%")
        if 'esquive_pct' in unit:
            secondary_stats.append(f"Esq: {unit['esquive_pct']}%")
        if 'precision_pct' in unit:
            secondary_stats.append(f"Préc: {unit['precision_pct']}%")
        
        if secondary_stats:
            secondary_stats_text = " | ".join(secondary_stats)
            secondary_stats_surface = self.get_cached_font(12).render(secondary_stats_text, True, COLORS['light_blue'])
            secondary_stats_rect = secondary_stats_surface.get_rect(centerx=overlay_width//2, y=secondary_stats_y)
            
            # Fond pour les stats secondaires
            secondary_stats_bg_rect = pygame.Rect(secondary_stats_rect.x - 5, secondary_stats_rect.y - 2, secondary_stats_rect.width + 10, secondary_stats_rect.height + 4)
            pygame.draw.rect(overlay_surface, (*COLORS['deep_black'], 200), secondary_stats_bg_rect, border_radius=5)
            overlay_surface.blit(secondary_stats_surface, secondary_stats_rect)
        
        # Stats primaires - juste au-dessus des stats secondaires (fonds collés)
        primary_stats_y = secondary_stats_y - 20
        stats_text = f"HP: {unit['hp']} | ATK: {unit['attack']} | DEF: {unit['defense']}"
        stats_surface = self.get_cached_font(14).render(stats_text, True, COLORS['light_gold'])
        stats_rect = stats_surface.get_rect(centerx=overlay_width//2, y=primary_stats_y)
        
        # Fond pour les stats primaires (collé au fond des stats secondaires)
        stats_bg_rect = pygame.Rect(stats_rect.x - 5, stats_rect.y - 2, stats_rect.width + 10, stats_rect.height + 4)
        pygame.draw.rect(overlay_surface, (*COLORS['deep_black'], 200), stats_bg_rect, border_radius=5)
        overlay_surface.blit(stats_surface, stats_rect)
        
        # Capacités - liste centrée (deck builder)
        ability_y_center = overlay_height - int(overlay_height * 0.40)
        names_cds = []
        ability_elements = []
        if 'ability_ids' in unit and unit['ability_ids']:
            try:
                effects_mgr = EffectsDatabaseManager()
                for aid in unit['ability_ids']:
                    data = effects_mgr.get_ability(str(aid))
                    name = data.get('name') if data else f"Capacité {aid}"
                    cd = data.get('base_cooldown', 0) if data else 0
                    element = data.get('element', '1') if data else '1'
                    names_cds.append((name, cd))
                    ability_elements.append(element)
            except Exception:
                pass
        if not names_cds and unit.get('description'):
            names_cds = [(unit['description'].split(':')[0].strip(), 0)]
            ability_elements = ['1']  # Par défaut feu
        if names_cds:
            font = self.get_cached_font(14)
            lh = font.get_height()
            spacing = 4
            total_h = len(names_cds) * lh + max(0, (len(names_cds) - 1) * spacing)
            start_y = int(ability_y_center - total_h / 2)
            
            # Mappage des éléments pour les symboles
            element_mapping = {
                '1': 'feu', '2': 'eau', '3': 'terre', '4': 'air', '5': 'glace',
                '6': 'foudre', '7': 'lumière', '8': 'ténèbres', '9': 'arcanique',
                '10': 'poison', '11': 'néant', '12': 'néant'
            }
            
            for idx, (nm, cd) in enumerate(names_cds):
                nm_short = nm if len(nm) <= 30 else (nm[:27] + '...')
                color = COLORS['crimson'] if cd > 0 else (0, 255, 0)
                y = start_y + idx * (lh + spacing)
                
                # Récupérer l'élément de la capacité
                ability_element = ability_elements[idx] if idx < len(ability_elements) else '1'
                element_name = element_mapping.get(str(ability_element), 'feu')
                element_symbol_path = f"Symbols/{element_name}.png"
                element_symbol = self.game_ui.asset_manager.get_image(element_symbol_path)
                
                # Calculer la largeur totale de la ligne (symbole + nom + cooldown)
                symbol_size = (12, 12)
                surf = font.render(nm_short, True, color)
                cd_surf = font.render(str(cd), True, color)
                
                # Largeurs des éléments
                symbol_width = 12
                text_width = surf.get_width()
                cooldown_width = cd_surf.get_width()
                spacing = 6  # Espace entre les éléments
                
                # Largeur totale de la ligne
                total_line_width = symbol_width + spacing + text_width + spacing + cooldown_width
                
                # Position de départ pour centrer toute la ligne
                line_start_x = (overlay_width - total_line_width) // 2
                
                # Positions des éléments
                symbol_x = line_start_x
                text_x = symbol_x + symbol_width + spacing
                cooldown_x = text_x + text_width + spacing
                
                # Nom de la capacité
                rect = surf.get_rect(x=text_x, y=y)
                
                # Fond pour la capacité (élargi pour inclure le symbole et le cooldown)
                bg = pygame.Rect(symbol_x - 2, rect.y - 2, total_line_width + 4, rect.height + 4)
                pygame.draw.rect(overlay_surface, (*COLORS['deep_black'], 200), bg, border_radius=5)
                overlay_surface.blit(surf, rect)
                
                # Afficher le symbole d'élément APRÈS le fond (pour qu'il soit visible)
                if element_symbol:
                        # Afficher le symbole d\'élément (12x12)
                    scaled_symbol = pygame.transform.scale(element_symbol, symbol_size)
                    symbol_y = y + (lh - 12) // 2  # Centrer verticalement
                    symbol_rect = scaled_symbol.get_rect(topleft=(symbol_x, symbol_y))
                    overlay_surface.blit(scaled_symbol, symbol_rect)
                
                # cooldown à droite
                cd_rect = cd_surf.get_rect(x=cooldown_x, y=y)
                overlay_surface.blit(cd_surf, cd_rect)
        
        return overlay_surface
    
    def create_hover_unit_overlay(self, unit, border_color):
        """Crée un overlay de hover pour une unité avec retour à la ligne intelligent"""
        overlay_width = 300
        overlay_height = 400
        overlay_surface = pygame.Surface((overlay_width, overlay_height), pygame.SRCALPHA)
        
        # Fond semi-transparent
        pygame.draw.rect(overlay_surface, (*COLORS['deep_black'], 230), (0, 0, overlay_width, overlay_height), border_radius=10)
        
        # Bordure colorée
        pygame.draw.rect(overlay_surface, border_color, (0, 0, overlay_width, overlay_height), 3, border_radius=10)
        
        # Nom de l'unité
        name_text = unit['name'].split(',')[0].strip()
        name_surface = self.get_cached_font(18).render(name_text, True, COLORS['white'])
        name_rect = name_surface.get_rect(centerx=overlay_width//2, y=20)
        overlay_surface.blit(name_surface, name_rect)
        
        # Stats
        stats_text = f"HP: {unit['hp']} | ATK: {unit['attack']} | DEF: {unit['defense']}"
        stats_surface = self.get_cached_font(14).render(stats_text, True, COLORS['light_gold'])
        stats_rect = stats_surface.get_rect(centerx=overlay_width//2, y=50)
        overlay_surface.blit(stats_surface, stats_rect)
        
        # Description avec retour à la ligne intelligent
        if 'description' in unit and unit['description']:
            desc_rect = pygame.Rect(20, 80, overlay_width - 40, overlay_height - 100)
            self.draw_wrapped_text(overlay_surface, unit['description'], self.get_cached_font(12), COLORS['white'], desc_rect)
        
        return overlay_surface
    
    def create_hover_card_overlay(self, card, border_color):
        """Crée un overlay de hover pour une carte avec retour à la ligne intelligent"""
        overlay_width = 300
        overlay_height = 400
        overlay_surface = pygame.Surface((overlay_width, overlay_height), pygame.SRCALPHA)
        
        # Fond semi-transparent
        pygame.draw.rect(overlay_surface, (*COLORS['deep_black'], 230), (0, 0, overlay_width, overlay_height), border_radius=10)
        
        # Bordure colorée
        pygame.draw.rect(overlay_surface, border_color, (0, 0, overlay_width, overlay_height), 3, border_radius=10)
        
        # Nom de la carte
        name_text = card['name'].split(',')[0].strip()
        name_surface = self.get_cached_font(18).render(name_text, True, COLORS['white'])
        name_rect = name_surface.get_rect(centerx=overlay_width//2, y=20)
        overlay_surface.blit(name_surface, name_rect)
        
        # Coût en mana
        if 'mana_cost' in card:
            mana_text = f"Mana: {card['mana_cost']}"
            mana_surface = self.get_cached_font(14).render(mana_text, True, COLORS['light_blue'])
            mana_rect = mana_surface.get_rect(centerx=overlay_width//2, y=50)
            overlay_surface.blit(mana_surface, mana_rect)
        
        # Description avec retour à la ligne intelligent
        if 'description' in card and card['description']:
            desc_rect = pygame.Rect(20, 80, overlay_width - 40, overlay_height - 100)
            self.draw_wrapped_text(overlay_surface, card['description'], self.get_cached_font(12), COLORS['white'], desc_rect)
        
        # Layout avec image occupant l'espace intérieur de la bordure et texte à l'extérieur
        # Marges pour la bordure
        border_margin = 20
        content_y = 100  # Position fixe pour le contenu
        content_height = overlay_height - content_y - 60
        
        # Image de la carte - occupe l'espace intérieur de la bordure
        # Zone pour l'image (espace intérieur de la bordure)
        image_width = overlay_width - (border_margin * 2)  # Largeur moins marges bordure
        image_height = overlay_height - (border_margin * 2)  # Hauteur moins marges bordure
        
        # Position de l'image (avec marges pour la bordure)
        image_x = border_margin
        image_y = border_margin
        
        if 'image_path' in card:
            card_image = self.game_ui.asset_manager.get_image(card['image_path'])
            if card_image:
                # Redimensionner l'image
                scaled_image = pygame.transform.scale(card_image, (image_width, image_height))
                
                # Créer une surface avec coins arrondis pour l'image
                image_surface = pygame.Surface((image_width, image_height), pygame.SRCALPHA)
                
                # Créer un masque avec coins arrondis précis
                mask_surface = self.create_rounded_mask(image_width, image_height, 20)
                
                # Appliquer le masque à l'image
                image_surface.blit(scaled_image, (0, 0))
                image_surface.blit(mask_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                
                overlay_surface.blit(image_surface, (image_x, image_y))
            else:
                # Image par défaut si pas trouvée
                default_surface = pygame.Surface((image_width, image_height))
                default_surface.fill(COLORS['dark_gray'])
                overlay_surface.blit(default_surface, (image_x, image_y))
        
        # Zone texte avec fond semi-transparent - à l'extérieur de l'image+bordure
        text_x = overlay_width + 20  # Complètement à droite de l'overlay
        text_width = 200  # Largeur fixe pour la zone texte
        
        # Fond semi-transparent pour le texte (60% d'opacité)
        text_bg_rect = pygame.Rect(text_x - 10, content_y - 10, text_width + 20, content_height + 20)
        pygame.draw.rect(overlay_surface, (*COLORS['deep_black'], 153), text_bg_rect, border_radius=15)  # 153 = 60% de 255
        
        # Type de carte
        type_y = content_y
        if 'card_type' in card:
            card_type_text = card['card_type'].replace('CARDTYPE.', '').title()
            type_surface = self.get_cached_font(20).render(f"Type: {card_type_text}", True, COLORS['light_gold'])
            overlay_surface.blit(type_surface, (text_x, type_y))
        
        # Coût en mana
        cost_y = type_y + 30
        if 'cost' in card:
            cost_text = f"Coût: {card['cost']}"
            cost_surface = self.get_cached_font(20).render(cost_text, True, COLORS['light_blue'])
            overlay_surface.blit(cost_surface, (text_x, cost_y))
        
        # Description
        desc_y = cost_y + 30
        if 'description' in card and card['description']:
            desc_surface = self.get_cached_font(16).render(card['description'], True, COLORS['white'])
            overlay_surface.blit(desc_surface, (text_x, desc_y))
        
        # Rareté
        rarity_y = desc_y + 30
        if 'rarity' in card:
            rarity_text = f"Rareté: {card['rarity']}"
            rarity_surface = self.get_cached_font(18).render(rarity_text, True, COLORS['white'])
            overlay_surface.blit(rarity_surface, (text_x, rarity_y))
        
        return overlay_surface

    def create_hero_overlay_surface_high_res(self, hero):
        """Crée une surface d'overlay haute résolution pour un héros - Layout 80% écran"""
        # Taille 80% de l'écran
        screen_width, screen_height = 1920, 1080
        overlay_width = int(screen_width * 0.8)  # 1536 pixels
        overlay_height = int(screen_height * 0.8)  # 864 pixels
        overlay_surface = pygame.Surface((overlay_width, overlay_height), pygame.SRCALPHA)

        # Bordure or
        pygame.draw.rect(overlay_surface, COLORS['gold'], (0, 0, overlay_width, overlay_height), 6, border_radius=30)

        # Layout : Image à gauche (40%), Texte à droite (60%)
        image_width = int(overlay_width * 0.4)  # 614 pixels
        text_width = int(overlay_width * 0.6)   # 922 pixels
        image_x = 0
        text_x = image_width + 20  # Espacement entre image et texte

        # Image du héros - côté gauche avec bordure
        if 'image_path' in hero:
            hero_image = self.game_ui.asset_manager.get_image(hero['image_path'])
            if hero_image:
                # Image avec bordure intérieure
                border_margin = 30
                image_inner_width = image_width - (border_margin * 2)
                image_inner_height = overlay_height - (border_margin * 2)
                
                # Redimensionner l'image
                scaled_image = pygame.transform.scale(hero_image, (image_inner_width, image_inner_height))
                
                # Créer une surface avec coins arrondis pour l'image
                image_surface = pygame.Surface((image_inner_width, image_inner_height), pygame.SRCALPHA)
                
                # Créer un masque avec coins arrondis précis
                mask_surface = self.create_rounded_mask(image_inner_width, image_inner_height, 30)
                
                # Appliquer le masque à l'image
                image_surface.blit(scaled_image, (0, 0))
                image_surface.blit(mask_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                
                overlay_surface.blit(image_surface, (border_margin, border_margin))
            else:
                # Image par défaut avec coins arrondis
                default_surface = pygame.Surface((image_inner_width, image_inner_height), pygame.SRCALPHA)
                default_surface.fill(COLORS['dark_gray'])
                mask_surface = self.create_rounded_mask(image_inner_width, image_inner_height, 30)
                default_surface.blit(mask_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                overlay_surface.blit(default_surface, (border_margin, border_margin))

        # Zone texte - côté droit
        text_y = 40  # Marge supérieure
        current_y = text_y

        # Symbole élémentaire + texte
        if 'element' in hero and hero['element']:
            element_mapping = {
                'feu': 'feu', 'eau': 'eau', 'glace': 'glace', 'terre': 'terre', 'air': 'air',
                'foudre': 'foudre', 'lumière': 'lumiere', 'ténèbres': 'tenebres', 'arcanique': 'arcane',
                'poison': 'poison', 'néant': 'neant'
            }
            element_name = hero['element'].lower()
            file_name = element_mapping.get(element_name, element_name)
            element_symbol_path = f"Symbols/{file_name}.png"
            element_symbol = self.game_ui.asset_manager.get_image(element_symbol_path)
            
            if element_symbol:
                # Symbole + texte
                symbol_size = (64, 64)
                scaled_symbol = pygame.transform.scale(element_symbol, symbol_size)
                symbol_rect = scaled_symbol.get_rect(topleft=(text_x, current_y))
                overlay_surface.blit(scaled_symbol, symbol_rect)
                
                # Texte de l'élément (sans "Élément:")
                element_text = hero['element']
                element_surface = self.get_cached_font(32).render(element_text, True, COLORS['light_gold'])
                overlay_surface.blit(element_surface, (text_x + 80, current_y + 20))
            else:
                # Texte seulement (sans "Élément:")
                element_text = hero['element']
                element_surface = self.get_cached_font(32).render(element_text, True, COLORS['light_gold'])
                overlay_surface.blit(element_surface, (text_x, current_y))
            
            current_y += 80

        # Nom complet du héros
        full_name = hero['name']
        name_surface = self.get_cached_font(48).render(full_name, True, COLORS['white'])
        overlay_surface.blit(name_surface, (text_x, current_y))
        current_y += 80

        # Capacité (nom sans "Capacité:")
        if 'ability_name' in hero:
            ability_text = hero['ability_name']
            ability_surface = self.get_cached_font(36).render(ability_text, True, COLORS['crimson'])
            overlay_surface.blit(ability_surface, (text_x, current_y))
            current_y += 30

        # Cooldown (déplacé sous le nom de capacité)
        if 'ability_cooldown' in hero:
            cooldown_text = f"Cooldown : {hero['ability_cooldown']}"
            cooldown_surface = self.get_cached_font(28).render(cooldown_text, True, COLORS['crimson'])
            overlay_surface.blit(cooldown_surface, (text_x, current_y))
            current_y += 30

        # Description de la capacité (avec retour à la ligne intelligent)
        if 'ability_description' in hero and hero['ability_description']:
            desc_text = hero['ability_description']
            # Retour à la ligne après chaque "."
            desc_lines = desc_text.split('.')
            for line in desc_lines:
                if line.strip():
                    line = line.strip() + '.'
                    # Wrapping intelligent
                    wrapped_lines = self.smart_wrap_text(line, self.get_cached_font(28), text_width - 40)
                    for wrapped_line in wrapped_lines:
                        desc_surface = self.get_cached_font(28).render(wrapped_line, True, COLORS['white'])
                        overlay_surface.blit(desc_surface, (text_x, current_y))
                        current_y += 40
            current_y += 60

        # Passif (si présent)
        if 'passive' in hero and hero['passive']:
            # Nettoyer le texte du passif en supprimant le coût entre parenthèses
            passive_text_raw = hero['passive']
            # Supprimer tout ce qui est entre parenthèses à la fin
            if '(' in passive_text_raw:
                # Trouver la dernière parenthèse ouvrante
                last_open = passive_text_raw.rfind('(')
                if last_open != -1:
                    # Supprimer tout ce qui suit la dernière parenthèse ouvrante
                    passive_text_raw = passive_text_raw[:last_open].strip()
            
            passive_text = f"Passif: {passive_text_raw}"
            # Retour à la ligne après chaque "."
            passive_lines = passive_text.split('.')
            for line in passive_lines:
                if line.strip():
                    line = line.strip() + '.'
                    # Wrapping intelligent
                    wrapped_lines = self.smart_wrap_text(line, self.get_cached_font(28), text_width - 40)
                    for wrapped_line in wrapped_lines:
                        passive_surface = self.get_cached_font(28).render(wrapped_line, True, COLORS['light_gold'])
                        overlay_surface.blit(passive_surface, (text_x, current_y))
                        current_y += 40
            current_y += 60

        # Stats affichées une à une
        stats_y = current_y + 20
        
        # HP
        hp = hero.get('hp', hero.get('base_stats', {}).get('hp', 0))
        hp_text = f"Points de vie: {hp}"
        hp_surface = self.get_cached_font(32).render(hp_text, True, COLORS['light_gold'])
        overlay_surface.blit(hp_surface, (text_x, stats_y))
        stats_y += 30

        # Attaque
        attack = hero.get('attack', hero.get('base_stats', {}).get('attack', 0))
        attack_text = f"Attaque: {attack}"
        attack_surface = self.get_cached_font(32).render(attack_text, True, COLORS['light_gold'])
        overlay_surface.blit(attack_surface, (text_x, stats_y))
        stats_y += 30

        # Défense
        defense = hero.get('defense', hero.get('base_stats', {}).get('defense', 0))
        defense_text = f"Défense: {defense}"
        defense_surface = self.get_cached_font(32).render(defense_text, True, COLORS['light_gold'])
        overlay_surface.blit(defense_surface, (text_x, stats_y))
        stats_y += 60

        # Stats secondaires
        if 'crit_pct' in hero:
            crit_text = f"Critique: {hero['crit_pct']}%"
            crit_surface = self.get_cached_font(28).render(crit_text, True, COLORS['light_blue'])
            overlay_surface.blit(crit_surface, (text_x, stats_y))
            stats_y += 30

        if 'esquive_pct' in hero:
            esquive_text = f"Esquive: {hero['esquive_pct']}%"
            esquive_surface = self.get_cached_font(28).render(esquive_text, True, COLORS['light_blue'])
            overlay_surface.blit(esquive_surface, (text_x, stats_y))
            stats_y += 30

        if 'precision_pct' in hero:
            precision_text = f"Précision: {hero['precision_pct']}%"
            precision_surface = self.get_cached_font(28).render(precision_text, True, COLORS['light_blue'])
            overlay_surface.blit(precision_surface, (text_x, stats_y))
            stats_y += 60

        # Rareté (sans "Rareté:")
        if 'rarity' in hero:
            rarity_text = hero['rarity']
            rarity_surface = self.get_cached_font(28).render(rarity_text, True, COLORS['white'])
            overlay_surface.blit(rarity_surface, (text_x, stats_y))

        return overlay_surface

    def calculate_final_stats(self, unit):
        """Calcule les stats finales d'une unité en tenant compte des effets temporaires"""
        # Stats de base
        base_hp = unit.get('hp', 0)
        base_attack = unit.get('attack', 0)
        base_defense = unit.get('defense', 0)
        
        # Stats finales (commencent par les stats de base)
        final_hp = base_hp
        final_attack = base_attack
        final_defense = base_defense
        
        # Effets temporaires actifs
        active_effects = []
        
        # Vérifier les effets temporaires et calculer les stats finales
        if hasattr(unit, 'temporary_effects') and unit.temporary_effects:
            for effect in unit.temporary_effects:
                if isinstance(effect, dict):
                    effect_type = effect.get('type', '')
                    value = effect.get('value', 0)
                    duration = effect.get('duration', 0)
                    
                    if duration > 0:  # Effet encore actif
                        active_effects.append({
                            'type': effect_type,
                            'value': value,
                            'duration': duration
                        })
                        
                        # Appliquer les modificateurs selon le type d'effet
                        if effect_type == 'crit_boost':
                            # Boost de critique (affecte les dégâts mais pas directement l'attaque)
                            # Les boosts de critique sont gérés dans l'affichage des stats secondaires
                            pass
                        elif effect_type == 'dodge_boost':
                            # Boost d'esquive (affecte l'esquive mais pas les stats principales)
                            # Les boosts d'esquive sont gérés dans l'affichage des stats secondaires
                            pass
                        elif effect_type == 'damage_boost':
                            # Boost de dégâts (affecte les dégâts mais pas directement l'attaque)
                            pass
                        elif effect_type == 'grant_passive':
                            # Passif temporaire (peut affecter les stats)
                            passive_id = effect.get('passive_id', '')
                            if passive_id:
                                # Chercher le passif dans la base de données
                                try:
                                    with open("Data/effects_database.json", 'r', encoding='utf-8') as f:
                                        effects_data = json.load(f)
                                    passives_data = effects_data.get("passives", {})
                                    if passive_id in passives_data:
                                        passive = passives_data[passive_id]
                                        effect_ids = passive.get("effect_ids", [])
                                        
                                        # Appliquer les effets du passif
                                        for effect_id in effect_ids:
                                            effect_data = effects_data.get("base_effects", {}).get(effect_id, {})
                                            if effect_data:
                                                effect_name = effect_data.get("name", "")
                                                if "fire_damage_boost" in effect_data:
                                                    # Boost de dégâts de feu
                                                    pass
                                                elif "water_effect_boost" in effect_data:
                                                    # Boost d'effets d'eau
                                                    pass
                                                elif "earth_effect_boost" in effect_data:
                                                    # Boost d'effets de terre
                                                    pass
                                                elif "air_effect_boost" in effect_data:
                                                    # Boost d'effets d'air
                                                    pass
                                                elif "ice_effect_boost" in effect_data:
                                                    # Boost d'effets de glace
                                                    pass
                                                elif "lightning_effect_boost" in effect_data:
                                                    # Boost d'effets de foudre
                                                    pass
                                                elif "light_effect_boost" in effect_data:
                                                    # Boost d'effets de lumière
                                                    pass
                                                elif "dark_effect_boost" in effect_data:
                                                    # Boost d'effets de ténèbres
                                                    pass
                                                elif "arcane_effect_boost" in effect_data:
                                                    # Boost d'effets arcaniques
                                                    pass
                                                elif "poison_effect_boost" in effect_data:
                                                    # Boost d'effets de poison
                                                    pass
                                                elif "void_effect_boost" in effect_data:
                                                    # Boost d'effets du néant
                                                    pass
                                                elif "neutral_effect_boost" in effect_data:
                                                    # Boost d'effets neutres
                                                    pass
                                except:
                                    pass
        
        # Utiliser les stats actuelles de l'unité (qui incluent les effets temporaires)
        current_stats = getattr(unit, 'stats', {})
        current_hp = current_stats.get('hp', base_hp)
        current_attack = current_stats.get('attack', base_attack)
        current_defense = current_stats.get('defense', base_defense)
        
        return {
            'base': {
                'hp': base_hp,
                'attack': base_attack,
                'defense': base_defense,
                'crit_pct': unit.get('crit_pct', 0),
                'esquive_pct': unit.get('esquive_pct', 0),
                'precision_pct': unit.get('precision_pct', 0)
            },
            'final': {
                'hp': current_hp,
                'attack': current_attack,
                'defense': current_defense,
                'crit_pct': unit.get('crit_pct', 0),
                'esquive_pct': unit.get('esquive_pct', 0),
                'precision_pct': unit.get('precision_pct', 0)
            },
            'active_effects': active_effects
        }

    def create_right_click_unit_overlay(self, unit, border_color):
        """Crée l'overlay de clic droit pour une unité avec le même format que les héros"""
        # Format 80% de l'écran comme les héros
        SCREEN_WIDTH = 1920
        SCREEN_HEIGHT = 1080
        overlay_width = int(SCREEN_WIDTH * 0.8)
        overlay_height = int(SCREEN_HEIGHT * 0.8)
        overlay_surface = pygame.Surface((overlay_width, overlay_height), pygame.SRCALPHA)

        # Bordure colorée avec coins arrondis
        border_radius = 30
        pygame.draw.rect(overlay_surface, border_color, (0, 0, overlay_width, overlay_height), 4, border_radius=border_radius)

        # Layout : Image à gauche (40%), Texte à droite (60%) - comme les héros
        image_width = int(overlay_width * 0.4)  # 614 pixels
        text_width = int(overlay_width * 0.6)   # 922 pixels
        image_x = 0
        text_x = image_width + 20  # Espacement entre image et texte

        # Image de l'unité - côté gauche avec bordure
        if 'image_path' in unit:
            unit_image = self.game_ui.asset_manager.get_image(unit['image_path'])
            if unit_image:
                # Image avec bordure intérieure
                border_margin = 30
                image_inner_width = image_width - (border_margin * 2)
                image_inner_height = overlay_height - (border_margin * 2)
                
                # Redimensionner l'image
                scaled_image = pygame.transform.scale(unit_image, (image_inner_width, image_inner_height))
                
                # Créer une surface avec coins arrondis pour l'image
                image_surface = pygame.Surface((image_inner_width, image_inner_height), pygame.SRCALPHA)
                
                # Créer un masque avec coins arrondis précis
                mask_surface = self.create_rounded_mask(image_inner_width, image_inner_height, 30)
                
                # Appliquer le masque à l'image
                image_surface.blit(scaled_image, (0, 0))
                image_surface.blit(mask_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                
                overlay_surface.blit(image_surface, (border_margin, border_margin))
            else:
                # Image par défaut avec coins arrondis
                default_surface = pygame.Surface((image_inner_width, image_inner_height), pygame.SRCALPHA)
                default_surface.fill(COLORS['dark_gray'])
                mask_surface = self.create_rounded_mask(image_inner_width, image_inner_height, 30)
                default_surface.blit(mask_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                overlay_surface.blit(default_surface, (border_margin, border_margin))

        # Zone texte - côté droit
        text_y = 40  # Marge supérieure
        current_y = text_y

        # Élément (symbole + texte)
        if 'element' in unit and unit['element']:
            element_mapping = {
                'feu': 'feu', 'eau': 'eau', 'glace': 'glace', 'terre': 'terre', 'air': 'air',
                'foudre': 'foudre', 'lumière': 'lumiere', 'ténèbres': 'tenebres', 'arcanique': 'arcane',
                'poison': 'poison', 'néant': 'neant'
            }
            element_name = unit['element'].lower()
            file_name = element_mapping.get(element_name, element_name)
            element_symbol_path = f"Symbols/{file_name}.png"
            element_symbol = self.game_ui.asset_manager.get_image(element_symbol_path)
            if element_symbol:
                # Symbole + texte
                symbol_size = (64, 64)
                scaled_symbol = pygame.transform.scale(element_symbol, symbol_size)
                symbol_rect = scaled_symbol.get_rect(topleft=(text_x, current_y))
                overlay_surface.blit(scaled_symbol, symbol_rect)
                
                # Texte de l'élément (sans "Élément:")
                element_text = unit['element']
                element_surface = self.get_cached_font(32).render(element_text, True, COLORS['light_gold'])
                overlay_surface.blit(element_surface, (text_x + 80, current_y + 20))
            else:
                # Texte seulement (sans "Élément:")
                element_text = unit['element']
                element_surface = self.get_cached_font(32).render(element_text, True, COLORS['light_gold'])
                overlay_surface.blit(element_surface, (text_x, current_y))
            
            current_y += 80

        # Nom complet de l'unité
        name_text = unit['name']
        name_surface = self.get_cached_font(48).render(name_text, True, COLORS['white'])
        overlay_surface.blit(name_surface, (text_x, current_y))
        current_y += 80

        # Capacités de l'unité
        if 'ability_ids' in unit and unit['ability_ids']:
            # Titre des capacités
            abilities_title = self.get_cached_font(32).render("Capacités:", True, COLORS['light_gold'])
            overlay_surface.blit(abilities_title, (text_x, current_y))
            current_y += 50
            
            # Charger les données des capacités
            try:
                with open("Data/effects_database.json", 'r', encoding='utf-8') as f:
                    effects_data = json.load(f)
                abilities_data = effects_data.get("abilities", {})
            except Exception as e:
                abilities_data = {}
            
            # Afficher chaque capacité
            for i, ability_id in enumerate(unit['ability_ids']):
                if ability_id in abilities_data:
                    ability = abilities_data[ability_id]
                    ability_name = ability.get("name", f"Capacité {i+1}")
                    ability_description = ability.get("description", "Aucune description")
                    ability_cooldown = ability.get("base_cooldown", 0)
                    ability_element = ability.get("element", "1")  # Récupérer l'élément de la capacité
                    
                    # Symbole d'élément de la capacité
                    element_mapping = {
                        '1': 'feu', '2': 'eau', '3': 'terre', '4': 'air', '5': 'glace',
                        '6': 'foudre', '7': 'lumière', '8': 'ténèbres', '9': 'arcanique',
                        '10': 'poison', '11': 'néant', '12': 'néant'
                    }
                    element_name = element_mapping.get(str(ability_element), 'feu')
                    element_symbol_path = f"Symbols/{element_name}.png"
                    element_symbol = self.game_ui.asset_manager.get_image(element_symbol_path)
                    
                    # Position du symbole et du texte
                    symbol_x = text_x
                    text_start_x = text_x + 40  # Espace après le symbole
                    
                    if element_symbol:
                        # Afficher le symbole d'élément (32x32)
                        symbol_size = (32, 32)
                        scaled_symbol = pygame.transform.scale(element_symbol, symbol_size)
                        symbol_rect = scaled_symbol.get_rect(topleft=(symbol_x, current_y))
                        overlay_surface.blit(scaled_symbol, symbol_rect)
                    
                    # Nom de la capacité avec cooldown
                    name_text = f"{ability_name} (Cooldown: {ability_cooldown})"
                    name_surface = self.get_cached_font(28).render(name_text, True, COLORS['cyan'])
                    # Centrer verticalement le texte par rapport au symbole (32px de hauteur)
                    text_y = current_y + (32 - name_surface.get_height()) // 2
                    overlay_surface.blit(name_surface, (text_start_x, text_y))
                    current_y += 35
                    
                    # Description de la capacité
                    wrapped_lines = self.smart_wrap_text(ability_description, self.get_cached_font(24), text_width - 40)
                    for wrapped_line in wrapped_lines:
                        desc_surface = self.get_cached_font(24).render(wrapped_line, True, COLORS['white'])
                        overlay_surface.blit(desc_surface, (text_x, current_y))
                        current_y += 30
                    
                    current_y += 20  # Espace entre les capacités
                else:
                    # Capacité non trouvée
                    name_text = f"Capacité {i+1} (ID: {ability_id})"
                    name_surface = self.get_cached_font(28).render(name_text, True, COLORS['red'])
                    overlay_surface.blit(name_surface, (text_x, current_y))
                    current_y += 35
                    
                    desc_text = "Capacité non trouvée dans la base de données"
                    desc_surface = self.get_cached_font(24).render(desc_text, True, COLORS['gray'])
                    overlay_surface.blit(desc_surface, (text_x, current_y))
                    current_y += 50
            
            current_y += 20
        else:
            # Aucune capacité
            no_abilities_text = "Aucune capacité"
            no_abilities_surface = self.get_cached_font(28).render(no_abilities_text, True, COLORS['gray'])
            overlay_surface.blit(no_abilities_surface, (text_x, current_y))
            current_y += 60
        
        # Passifs de l'unité
        if 'passive_ids' in unit and unit['passive_ids']:
            # Titre des passifs
            passives_title = self.get_cached_font(32).render("Passifs:", True, COLORS['light_gold'])
            overlay_surface.blit(passives_title, (text_x, current_y))
            current_y += 50
            
            # Charger les données des passifs
            try:
                with open("Data/effects_database.json", 'r', encoding='utf-8') as f:
                    effects_data = json.load(f)
                passives_data = effects_data.get("passives", {})
            except:
                passives_data = {}
            
            # Afficher chaque passif
            for i, passive_id in enumerate(unit['passive_ids']):
                if passive_id in passives_data:
                    passive = passives_data[passive_id]
                    passive_name = passive.get("name", f"Passif {i+1}")
                    passive_description = passive.get("description", "Aucune description")
                    
                    # Nom du passif
                    name_text = passive_name
                    name_surface = self.get_cached_font(28).render(name_text, True, COLORS['purple'])
                    overlay_surface.blit(name_surface, (text_x, current_y))
                    current_y += 35
                    
                    # Description du passif
                    wrapped_lines = self.smart_wrap_text(passive_description, self.get_cached_font(24), text_width - 40)
                    for wrapped_line in wrapped_lines:
                        desc_surface = self.get_cached_font(24).render(wrapped_line, True, COLORS['white'])
                        overlay_surface.blit(desc_surface, (text_x, current_y))
                        current_y += 30
                    
                    current_y += 20  # Espace entre les passifs
                else:
                    # Passif non trouvé
                    name_text = f"Passif {i+1} (ID: {passive_id})"
                    name_surface = self.get_cached_font(28).render(name_text, True, COLORS['red'])
                    overlay_surface.blit(name_surface, (text_x, current_y))
                    current_y += 35
                    
                    desc_text = "Passif non trouvé dans la base de données"
                    desc_surface = self.get_cached_font(24).render(desc_text, True, COLORS['gray'])
                    overlay_surface.blit(desc_surface, (text_x, current_y))
                    current_y += 50
            
            current_y += 20
        else:
            # Aucun passif
            no_passives_text = "Aucun passif"
            no_passives_surface = self.get_cached_font(28).render(no_passives_text, True, COLORS['gray'])
            overlay_surface.blit(no_passives_surface, (text_x, current_y))
            current_y += 60

        # Stats affichées une à une avec calcul des stats finales
        stats_y = current_y + 20
        
        # Calculer les stats finales
        final_stats = self.calculate_final_stats(unit)
        
        # HP
        base_hp = final_stats['base']['hp']
        final_hp = final_stats['final']['hp']
        if base_hp == final_hp:
            hp_text = f"Points de vie: {final_hp}"
            hp_color = COLORS['light_gold']
        else:
            hp_text = f"Points de vie: {final_hp} (base: {base_hp})"
            hp_color = COLORS['green']  # Vert pour indiquer un boost
        hp_surface = self.get_cached_font(32).render(hp_text, True, hp_color)
        overlay_surface.blit(hp_surface, (text_x, stats_y))
        stats_y += 30

        # Attaque
        base_attack = final_stats['base']['attack']
        final_attack = final_stats['final']['attack']
        if base_attack == final_attack:
            attack_text = f"Attaque: {final_attack}"
            attack_color = COLORS['light_gold']
        else:
            attack_text = f"Attaque: {final_attack} (base: {base_attack})"
            attack_color = COLORS['green']  # Vert pour indiquer un boost
        attack_surface = self.get_cached_font(32).render(attack_text, True, attack_color)
        overlay_surface.blit(attack_surface, (text_x, stats_y))
        stats_y += 30

        # Défense
        base_defense = final_stats['base']['defense']
        final_defense = final_stats['final']['defense']
        if base_defense == final_defense:
            defense_text = f"Défense: {final_defense}"
            defense_color = COLORS['light_gold']
        else:
            defense_text = f"Défense: {final_defense} (base: {base_defense})"
            defense_color = COLORS['green']  # Vert pour indiquer un boost
        defense_surface = self.get_cached_font(32).render(defense_text, True, defense_color)
        overlay_surface.blit(defense_surface, (text_x, stats_y))
        stats_y += 60

        # Afficher les effets temporaires actifs
        active_effects = []
        if hasattr(unit, 'temporary_effects') and unit.temporary_effects:
            for effect in unit.temporary_effects:
                if isinstance(effect, dict) and effect.get('duration', 0) > 0:
                    active_effects.append(effect)
        
        if active_effects:
            effects_title = self.get_cached_font(28).render("Effets temporaires actifs:", True, COLORS['yellow'])
            overlay_surface.blit(effects_title, (text_x, stats_y))
            stats_y += 30
            
            for effect in active_effects:
                effect_type = effect.get('type', 'N/A')
                effect_value = effect.get('value', 0)
                effect_duration = effect.get('duration', 0)
                
                # Formater l'affichage selon le type d'effet
                if effect_type == 'crit_boost':
                    effect_text = f"• Boost Critique: +{int(effect_value * 100)}% (durée: {effect_duration})"
                elif effect_type == 'dodge_boost':
                    effect_text = f"• Boost Esquive: +{int(effect_value * 100)}% (durée: {effect_duration})"
                elif effect_type == 'grant_passive':
                    passive_id = effect.get('passive_id', 'N/A')
                    effect_text = f"• Passif temporaire: {passive_id} (durée: {effect_duration})"
                else:
                    effect_text = f"• {effect_type}: +{effect_value} (durée: {effect_duration})"
                
                effect_surface = self.get_cached_font(24).render(effect_text, True, COLORS['light_blue'])
                overlay_surface.blit(effect_surface, (text_x, stats_y))
                stats_y += 25
            
            stats_y += 20

        # Stats secondaires avec calcul des stats finales
        if 'crit_pct' in unit:
            base_crit = unit['crit_pct']
            final_crit = base_crit
            # Vérifier les boosts de critique dans les effets temporaires
            if hasattr(unit, 'temporary_effects') and unit.temporary_effects:
                for effect in unit.temporary_effects:
                    if isinstance(effect, dict) and effect.get('type') == 'crit_boost' and effect.get('duration', 0) > 0:
                        final_crit += int(effect.get('value', 0) * 100)  # Convertir en pourcentage
            
            if base_crit == final_crit:
                crit_text = f"Critique: {final_crit}%"
                crit_color = COLORS['light_blue']
            else:
                crit_text = f"Critique: {final_crit}% (base: {base_crit}%)"
                crit_color = COLORS['green']
            crit_surface = self.get_cached_font(28).render(crit_text, True, crit_color)
            overlay_surface.blit(crit_surface, (text_x, stats_y))
            stats_y += 30

        if 'esquive_pct' in unit:
            base_esquive = unit['esquive_pct']
            final_esquive = base_esquive
            # Vérifier les boosts d'esquive dans les effets temporaires
            if hasattr(unit, 'temporary_effects') and unit.temporary_effects:
                for effect in unit.temporary_effects:
                    if isinstance(effect, dict) and effect.get('type') == 'dodge_boost' and effect.get('duration', 0) > 0:
                        final_esquive += int(effect.get('value', 0) * 100)  # Convertir en pourcentage
            
            if base_esquive == final_esquive:
                esquive_text = f"Esquive: {final_esquive}%"
                esquive_color = COLORS['light_blue']
            else:
                esquive_text = f"Esquive: {final_esquive}% (base: {base_esquive}%)"
                esquive_color = COLORS['green']
            esquive_surface = self.get_cached_font(28).render(esquive_text, True, esquive_color)
            overlay_surface.blit(esquive_surface, (text_x, stats_y))
            stats_y += 30

        if 'precision_pct' in unit:
            base_precision = unit['precision_pct']
            final_precision = base_precision
            # Pour l'instant, pas de boost de précision dans les effets temporaires
            # Mais la structure est prête pour l'ajouter
            
            if base_precision == final_precision:
                precision_text = f"Précision: {final_precision}%"
                precision_color = COLORS['light_blue']
            else:
                precision_text = f"Précision: {final_precision}% (base: {base_precision}%)"
                precision_color = COLORS['green']
            precision_surface = self.get_cached_font(28).render(precision_text, True, precision_color)
            overlay_surface.blit(precision_surface, (text_x, stats_y))
            stats_y += 60

        # Cooldown si présent
        if 'cooldown' in unit:
            cooldown_text = f"Cooldown : {unit['cooldown']}"
            cooldown_surface = self.get_cached_font(28).render(cooldown_text, True, COLORS['crimson'])
            overlay_surface.blit(cooldown_surface, (text_x, stats_y))
            stats_y += 60

        # Rareté (sans "Rareté:")
        if 'rarity' in unit:
            rarity_text = unit['rarity']
            rarity_surface = self.get_cached_font(28).render(rarity_text, True, COLORS['white'])
            overlay_surface.blit(rarity_surface, (text_x, stats_y))

        return overlay_surface

    def create_right_click_card_overlay(self, card, border_color):
        """Crée l'overlay de clic droit pour une carte avec le même format que les héros"""
        # Format 80% de l'écran comme les héros
        SCREEN_WIDTH = 1920
        SCREEN_HEIGHT = 1080
        overlay_width = int(SCREEN_WIDTH * 0.8)
        overlay_height = int(SCREEN_HEIGHT * 0.8)
        overlay_surface = pygame.Surface((overlay_width, overlay_height), pygame.SRCALPHA)

        # Bordure colorée avec coins arrondis
        border_radius = 30
        pygame.draw.rect(overlay_surface, border_color, (0, 0, overlay_width, overlay_height), 4, border_radius=border_radius)

        # Layout : Image à gauche (40%), Texte à droite (60%) - comme les héros
        image_width = int(overlay_width * 0.4)  # 614 pixels
        text_width = int(overlay_width * 0.6)   # 922 pixels
        image_x = 0
        text_x = image_width + 20  # Espacement entre image et texte

        # Image de la carte - côté gauche avec bordure
        border_margin = 30
        image_inner_width = image_width - (border_margin * 2)
        image_inner_height = overlay_height - (border_margin * 2)
        
        if 'image_path' in card and card['image_path']:
            card_image = self.game_ui.asset_manager.get_image(card['image_path'])
            if card_image:
                # Redimensionner l'image
                scaled_image = pygame.transform.scale(card_image, (image_inner_width, image_inner_height))
                
                # Créer une surface avec coins arrondis pour l'image
                image_surface = pygame.Surface((image_inner_width, image_inner_height), pygame.SRCALPHA)
                
                # Créer un masque avec coins arrondis précis
                mask_surface = self.create_rounded_mask(image_inner_width, image_inner_height, 30)
                
                # Appliquer le masque à l'image
                image_surface.blit(scaled_image, (0, 0))
                image_surface.blit(mask_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                
                overlay_surface.blit(image_surface, (border_margin, border_margin))
            else:
                # Image par défaut avec coins arrondis
                default_surface = pygame.Surface((image_inner_width, image_inner_height), pygame.SRCALPHA)
                default_surface.fill(COLORS['dark_gray'])
                mask_surface = self.create_rounded_mask(image_inner_width, image_inner_height, 30)
                default_surface.blit(mask_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                overlay_surface.blit(default_surface, (border_margin, border_margin))
        else:
            # Image par défaut avec coins arrondis (pas d'image_path)
            default_surface = pygame.Surface((image_inner_width, image_inner_height), pygame.SRCALPHA)
            default_surface.fill(COLORS['dark_gray'])
            mask_surface = self.create_rounded_mask(image_inner_width, image_inner_height, 30)
            default_surface.blit(mask_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            overlay_surface.blit(default_surface, (border_margin, border_margin))

        # Zone texte - côté droit
        text_y = 40  # Marge supérieure
        current_y = text_y

        # Symbole élémentaire + texte
        if 'element' in card and card['element']:
            element_mapping = {
                'feu': 'feu', 'eau': 'eau', 'glace': 'glace', 'terre': 'terre', 'air': 'air',
                'foudre': 'foudre', 'lumière': 'lumiere', 'ténèbres': 'tenebres', 'arcanique': 'arcane',
                'poison': 'poison', 'néant': 'neant', 'neutre': 'neant'
            }
            element_name = card['element'].lower()
            file_name = element_mapping.get(element_name, element_name)
            element_symbol_path = f"Symbols/{file_name}.png"
            element_symbol = self.game_ui.asset_manager.get_image(element_symbol_path)
            
            if element_symbol:
                # Symbole + texte
                symbol_size = (64, 64)
                scaled_symbol = pygame.transform.scale(element_symbol, symbol_size)
                symbol_rect = scaled_symbol.get_rect(topleft=(text_x, current_y))
                overlay_surface.blit(scaled_symbol, symbol_rect)
                
                # Texte de l'élément (sans "Élément:")
                element_text = card['element']
                element_surface = self.get_cached_font(32).render(element_text, True, COLORS['light_gold'])
                overlay_surface.blit(element_surface, (text_x + 80, current_y + 20))
            else:
                # Texte seulement (sans "Élément:")
                element_text = card['element']
                element_surface = self.get_cached_font(32).render(element_text, True, COLORS['light_gold'])
                overlay_surface.blit(element_surface, (text_x, current_y))
            
            current_y += 80

        # Nom complet de la carte
        full_name = card['name']
        name_surface = self.get_cached_font(48).render(full_name, True, COLORS['white'])
        overlay_surface.blit(name_surface, (text_x, current_y))
        current_y += 80

        # Type de carte
        if 'card_type' in card:
            card_type_text = card['card_type'].replace('CARDTYPE.', '').title()
            card_type_surface = self.get_cached_font(28).render(card_type_text, True, COLORS['light_gold'])
            overlay_surface.blit(card_type_surface, (text_x, current_y))
            current_y += 50

        # Coût en mana
        if 'cost' in card:
            cost_text = f"Coût : {card['cost']}"
            cost_surface = self.get_cached_font(28).render(cost_text, True, COLORS['crimson'])
            overlay_surface.blit(cost_surface, (text_x, current_y))
            current_y += 50

        # Description si présente
        if 'description' in card and card['description']:
            # Nettoyer le texte de la description en supprimant le coût entre parenthèses
            desc_text_raw = card['description']
            if '(' in desc_text_raw:
                last_open = desc_text_raw.rfind('(')
                if last_open != -1:
                    desc_text_raw = desc_text_raw[:last_open].strip()
            
            # Wrapping intelligent après chaque "."
            desc_lines = desc_text_raw.split('.')
            for line in desc_lines:
                if line.strip():
                    line = line.strip() + '.'
                    wrapped_lines = self.smart_wrap_text(line, self.get_cached_font(28), text_width - 40)
                    for wrapped_line in wrapped_lines:
                        desc_surface = self.get_cached_font(28).render(wrapped_line, True, COLORS['white'])
                        overlay_surface.blit(desc_surface, (text_x, current_y))
                        current_y += 40
            current_y += 60

        # Rareté (sans "RARITY.")
        if 'rarity' in card:
            rarity_text = card['rarity'].replace('RARITY.', '')
            rarity_surface = self.get_cached_font(28).render(rarity_text, True, COLORS['white'])
            overlay_surface.blit(rarity_surface, (text_x, current_y))

        return overlay_surface




