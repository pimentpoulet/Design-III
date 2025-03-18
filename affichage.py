import numpy as np
import cv2
import sys
rows, cols = 24, 32
def show_image_opencv(image_array):
    """Affiche l'image thermique avec OpenCV en plein écran."""
    #image_array = np.array(image_array, dtype=np.float32).reshape((rows, cols))
    #print(image_array)

    # Correction des valeurs invalides
    image_array = np.nan_to_num(image_array, nan=0.0, posinf=255.0, neginf=0.0)

    norm_image = cv2.normalize(image_array, None, 0, 255, cv2.NORM_MINMAX)
    color_image = cv2.applyColorMap(np.uint8(norm_image), cv2.COLORMAP_INFERNO)

    # Affichage en plein écran
    cv2.namedWindow("Thermal Camera", cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty("Thermal Camera", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    cv2.imshow("Thermal Camera", color_image)

    # Quitter proprement avec 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("Fermeture détectée. Arrêt du programme...")
        cv2.destroyAllWindows()
        sys.exit(0)