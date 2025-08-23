import pygame
import sys
import os

# Ajouter le répertoire parent au path pour importer les modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_rounded_corners():
    """Teste la fonction create_rounded_mask avec différentes tailles"""
    
    # Initialiser Pygame
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Test Coins Arrondis")
    
    # Créer une classe de test avec la fonction create_rounded_mask
    class TestMask:
        def create_rounded_mask(self, width, height, radius):
            """Crée un masque avec coins arrondis parfaits sans artefacts"""
            mask_surface = pygame.Surface((width, height), pygame.SRCALPHA)
            
            # Créer un masque de forme avec des coins arrondis
            # Le masque final : blanc (opaque) dans le rectangle arrondi, transparent ailleurs
            mask_surface.fill((0, 0, 0, 0))  # Tout transparent par défaut
            pygame.draw.rect(mask_surface, (255, 255, 255, 255), (0, 0, width, height), border_radius=radius)
            
            return mask_surface
    
    test_mask = TestMask()
    
    # Créer une image de test colorée
    test_image = pygame.Surface((200, 200))
    test_image.fill((255, 100, 100))  # Rouge
    
    # Tester différents radius
    radius_values = [10, 20, 30]
    y_offset = 50
    
    for i, radius in enumerate(radius_values):
        # Créer le masque
        mask = test_mask.create_rounded_mask(200, 200, radius)
        
        # Créer une surface pour l'image avec coins arrondis
        rounded_surface = pygame.Surface((200, 200), pygame.SRCALPHA)
        
        # Appliquer le masque
        rounded_surface.blit(test_image, (0, 0))
        rounded_surface.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        
        # Afficher sur l'écran
        x_pos = 50 + (i * 250)
        screen.blit(rounded_surface, (x_pos, y_offset))
        
        # Afficher le radius
        font = pygame.font.Font(None, 24)
        text = font.render(f"Radius: {radius}", True, (255, 255, 255))
        screen.blit(text, (x_pos, y_offset + 220))
    
    # Afficher les instructions
    font = pygame.font.Font(None, 36)
    title = font.render("Test des Coins Arrondis - Nouvelle Méthode", True, (255, 255, 255))
    screen.blit(title, (50, 10))
    
    font_small = pygame.font.Font(None, 24)
    instruction = font_small.render("Appuyez sur ESPACE pour quitter", True, (200, 200, 200))
    screen.blit(instruction, (50, 550))
    
    pygame.display.flip()
    
    # Boucle d'événements
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    running = False
    
    pygame.quit()
    print("✅ Test des coins arrondis terminé")

if __name__ == "__main__":
    test_rounded_corners()
