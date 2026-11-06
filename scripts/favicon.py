"""Génère les icônes d'onglet du site (photo en cercle) à partir de img/Gabriel Fortin.png.

Usage, depuis la racine du site (nécessite Pillow) :
    python3 scripts/favicon.py

Produit : favicon.ico (16/32/48), favicon-48.png, favicon-192.png (cercle sur fond
transparent) et apple-touch-icon.png (180 px, carré plein : iOS arrondit les coins
lui-même et remplace la transparence par du noir).
favicon-96.png (logo de la barre de navigation, flux RSS) n'est pas touché.
"""
from PIL import Image, ImageDraw

SOURCE = "img/Gabriel Fortin.png"
# Carré centré sur le visage, en pixels de l'image source (742 × 860).
CENTRE_X, CENTRE_Y, COTE = 375, 375, 540

photo = Image.open(SOURCE).convert("RGB")
demi = COTE // 2
carre = photo.crop((CENTRE_X - demi, CENTRE_Y - demi, CENTRE_X + demi, CENTRE_Y + demi))


def cercle(taille):
    """Photo en cercle, bord adouci (masque dessiné 4× plus grand puis réduit)."""
    grand = taille * 4
    masque = Image.new("L", (grand, grand), 0)
    ImageDraw.Draw(masque).ellipse((0, 0, grand - 1, grand - 1), fill=255)
    masque = masque.resize((taille, taille), Image.LANCZOS)
    image = carre.resize((taille, taille), Image.LANCZOS).convert("RGBA")
    image.putalpha(masque)
    return image


cercle(48).save("favicon-48.png", optimize=True)
cercle(192).save("favicon-192.png", optimize=True)
cercle(256).save("favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])
carre.resize((180, 180), Image.LANCZOS).save("apple-touch-icon.png", optimize=True)
print("Icônes régénérées.")
