from typing import Optional

import pygame


def get_image(self, col: int, row: int, resize: Optional[int] = None, sprite_sheet: Optional[pygame.Surface] = None) -> pygame.Surface:
    """
    Récupère une image à partir d'une feuille de sprites et la redimensionne si nécessaire.
    
    Args:
        col (int): La colonne de l'image dans la feuille de sprites.
        row (int): La ligne de l'image dans la feuille de sprites.
        resize (Optional[int]): La taille de redimensionnement de l'image (facultatif).
        sprite_sheet (Optional[pygame.Surface]): La feuille de sprites personnalisée (facultatif).

    Returns:
        pygame.Surface: L'image récupérée, redimensionnée si nécessaire.
    """
    # Récupère les dimensions de l'image sur la feuille de sprites
    x, y = self.sprite_size

    # Crée une surface pour l'image extraite
    image = pygame.Surface((x, y), pygame.SRCALPHA)

    # Si sprite_sheet est fourni, on l'utilise, sinon on utilise celle de la classe
    sheet = sprite_sheet if sprite_sheet else self.sprite_sheet

    # Récupère l'image à la position (col, row) dans la feuille de sprites
    image.blit(sheet, (0, 0), (col * x, row * y, x, y))

    # Si un redimensionnement est demandé, on l'applique
    if resize:
        # Calcule le coefficient de redimensionnement
        coef = resize / x
        image = pygame.transform.rotozoom(image, 0, coef)

    return image
