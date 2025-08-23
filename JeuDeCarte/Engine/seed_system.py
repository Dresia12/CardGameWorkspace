"""
Système de gestion des graines explosives
Gère les graines plantées par Flamby et leur explosion
"""

from typing import Dict, List, Any
import random

class SeedSystem:
    """Système de gestion des graines explosives"""
    
    def __init__(self):
        self.seeds: Dict[str, List[Dict[str, Any]]] = {}  # target_id -> list of seeds
        self.seed_counter = 0
    
    def plant_seed(self, target_id: str, damage: int, duration: int, caster_id: str) -> str:
        """
        Plante une graine sur une cible
        
        Args:
            target_id: ID de la cible
            damage: Dégâts de la graine
            duration: Durée en tours
            caster_id: ID du lanceur
        
        Returns:
            ID de la graine plantée
        """
        if target_id not in self.seeds:
            self.seeds[target_id] = []
        
        seed_id = f"seed_{self.seed_counter}"
        self.seed_counter += 1
        
        seed = {
            "id": seed_id,
            "damage": damage,
            "duration": duration,
            "caster_id": caster_id,
            "turns_remaining": duration
        }
        
        self.seeds[target_id].append(seed)
        return seed_id
    
    def update_seeds(self) -> List[Dict[str, Any]]:
        """
        Met à jour toutes les graines et retourne celles qui explosent
        
        Returns:
            Liste des graines qui explosent
        """
        exploding_seeds = []
        
        for target_id, target_seeds in list(self.seeds.items()):
            for seed in target_seeds[:]:  # Copie pour éviter les erreurs de modification
                seed["turns_remaining"] -= 1
                
                if seed["turns_remaining"] <= 0:
                    # La graine explose
                    exploding_seeds.append({
                        "target_id": target_id,
                        "seed": seed,
                        "total_damage": len(target_seeds) * seed["damage"]
                    })
                    # Retirer toutes les graines de cette cible
                    self.seeds[target_id].clear()
        
        # Nettoyer les cibles sans graines
        self.seeds = {k: v for k, v in self.seeds.items() if v}
        
        return exploding_seeds
    
    def explode_seeds(self, target_id: str) -> Dict[str, Any]:
        """
        Fait exploser toutes les graines d'une cible
        
        Args:
            target_id: ID de la cible
        
        Returns:
            Informations sur l'explosion
        """
        if target_id not in self.seeds:
            return {"damage": 0, "seeds_exploded": 0}
        
        target_seeds = self.seeds[target_id]
        total_damage = len(target_seeds) * 10  # 10 dégâts par graine
        
        # Retirer toutes les graines
        self.seeds[target_id].clear()
        
        return {
            "damage": total_damage,
            "seeds_exploded": len(target_seeds)
        }
    
    def get_seed_count(self, target_id: str) -> int:
        """Retourne le nombre de graines sur une cible"""
        return len(self.seeds.get(target_id, []))
    
    def get_all_seeds(self) -> Dict[str, List[Dict[str, Any]]]:
        """Retourne toutes les graines"""
        return self.seeds.copy()

# Instance globale du système de graines
seed_system = SeedSystem()
