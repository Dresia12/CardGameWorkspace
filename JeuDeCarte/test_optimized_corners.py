import pygame
import sys
import os
import time

# Ajouter le répertoire parent au path pour importer les modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_optimized_rounded_corners():
    """Teste les optimisations des coins arrondis"""
    
    # Initialiser Pygame
    pygame.init()
    screen = pygame.display.set_mode((1200, 800))
    pygame.display.set_caption("Test Coins Arrondis Optimisés")
    
    # Créer une classe de test avec les fonctions optimisées
    class TestOptimizedMask:
        def __init__(self):
            self._mask_cache = {}
        
        def create_rounded_mask(self, width, height, radius):
            """Version optimisée avec cache"""
            # Validation du radius
            max_radius = min(width, height) // 2
            if radius > max_radius:
                radius = max_radius
                print(f"⚠️  Radius ajusté à {max_radius}")
            
            # Cache des masques
            cache_key = f"{width}x{height}_r{radius}"
            
            if cache_key in self._mask_cache:
                print(f"✅ Masque réutilisé depuis le cache: {cache_key}")
                return self._mask_cache[cache_key]
            
            # Créer un nouveau masque
            mask_surface = pygame.Surface((width, height), pygame.SRCALPHA)
            mask_surface.fill((0, 0, 0, 0))
            pygame.draw.rect(mask_surface, (255, 255, 255, 255), (0, 0, width, height), border_radius=radius)
            
            # Mettre en cache
            self._mask_cache[cache_key] = mask_surface
            print(f"🆕 Nouveau masque créé et mis en cache: {cache_key}")
            
            return mask_surface
        
        def apply_rounded_corners_to_image(self, original_image, target_width, target_height, radius, use_smooth_scale=True):
            """Fonction optimisée complète"""
            # Validation du radius
            max_radius = min(target_width, target_height) // 2
            if radius > max_radius:
                radius = max_radius
            
            # Choix du redimensionnement
            if use_smooth_scale and (target_width > original_image.get_width() * 1.5 or 
                                   target_height > original_image.get_height() * 1.5):
                scaled_image = pygame.transform.smoothscale(original_image, (target_width, target_height))
                print("🔄 Utilisation de smoothscale pour gros agrandissement")
            else:
                scaled_image = pygame.transform.scale(original_image, (target_width, target_height))
                print("🔄 Utilisation de scale normal")
            
            # Créer la surface avec coins arrondis
            image_surface = pygame.Surface((target_width, target_height), pygame.SRCALPHA)
            mask_surface = self.create_rounded_mask(target_width, target_height, radius)
            
            image_surface.blit(scaled_image, (0, 0))
            image_surface.blit(mask_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            
            return image_surface.convert_alpha()
        
        def clear_mask_cache(self):
            """Vide le cache"""
            self._mask_cache.clear()
            print("🗑️  Cache des masques vidé")
    
    test_mask = TestOptimizedMask()
    
    # Créer des images de test
    test_images = []
    
    # Image rouge simple
    red_image = pygame.Surface((100, 100))
    red_image.fill((255, 100, 100))
    test_images.append(("Rouge 100x100", red_image))
    
    # Image bleue plus grande
    blue_image = pygame.Surface((200, 150))
    blue_image.fill((100, 100, 255))
    test_images.append(("Bleu 200x150", blue_image))
    
    # Image verte avec motif
    green_image = pygame.Surface((150, 150))
    green_image.fill((100, 255, 100))
    # Ajouter un motif
    for i in range(0, 150, 20):
        pygame.draw.line(green_image, (50, 200, 50), (i, 0), (i, 150), 2)
    test_images.append(("Vert avec motif 150x150", green_image))
    
    # Tester différents radius
    radius_values = [10, 25, 40]  # Le dernier devrait être ajusté automatiquement
    y_offset = 100
    
    for i, (name, original_image) in enumerate(test_images):
        x_offset = 50 + (i * 350)
        
        # Afficher l'image originale
        screen.blit(original_image, (x_offset, y_offset - 80))
        
        # Afficher le nom
        font = pygame.font.Font(None, 24)
        name_surface = font.render(name, True, (255, 255, 255))
        screen.blit(name_surface, (x_offset, y_offset - 100))
        
        for j, radius in enumerate(radius_values):
            # Tester la fonction optimisée
            start_time = time.time()
            rounded_image = test_mask.apply_rounded_corners_to_image(
                original_image, 
                original_image.get_width(), 
                original_image.get_height(), 
                radius
            )
            end_time = time.time()
            
            # Afficher l'image avec coins arrondis
            display_x = x_offset + (j * 120)
            display_y = y_offset + (j * 120)
            screen.blit(rounded_image, (display_x, display_y))
            
            # Afficher le radius et le temps
            info_text = f"r={radius} ({end_time-start_time:.3f}s)"
            info_surface = font.render(info_text, True, (200, 200, 200))
            screen.blit(info_surface, (display_x, display_y + original_image.get_height() + 5))
    
    # Afficher les informations
    font_large = pygame.font.Font(None, 36)
    title = font_large.render("Test des Coins Arrondis Optimisés", True, (255, 255, 255))
    screen.blit(title, (50, 20))
    
    font_small = pygame.font.Font(None, 20)
    instructions = [
        "Optimisations testées :",
        "• Cache des masques (réutilisation)",
        "• Validation automatique du radius",
        "• Choix intelligent scale/smoothscale",
        "• Optimisation convert_alpha()",
        "",
        "ESPACE = Vider le cache, Q = Quitter"
    ]
    
    for i, instruction in enumerate(instructions):
        instruction_surface = font_small.render(instruction, True, (200, 200, 200))
        screen.blit(instruction_surface, (50, 600 + i * 25))
    
    pygame.display.flip()
    
    # Boucle d'événements
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    test_mask.clear_mask_cache()
                    print("Cache vidé par l'utilisateur")
                elif event.key == pygame.K_q:
                    running = False
    
    pygame.quit()
    print("✅ Test des optimisations terminé")

if __name__ == "__main__":
    test_optimized_rounded_corners()
