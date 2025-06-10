import shutil
import logging
import os

# Configuration du logging
logging.basicConfig(filename='copy_errors.log', level=logging.ERROR,
                    format='%(asctime)s - %(message)s')

# Dossier source et destination
source_dir = "path/to/source/folder"  # Remplacez par votre dossier source
dest_dir = "path/to/dest/folder"      # Remplacez par votre dossier destination

# Création du dossier de destination s'il n'existe pas
os.makedirs(dest_dir, exist_ok=True)

# Parcourir les fichiers du dossier source
for item in os.listdir(source_dir):
    source_path = os.path.join(source_dir, item)
    dest_path = os.path.join(dest_dir, item)
    try:
        if os.path.isfile(source_path):
            shutil.copy2(source_path, dest_path)  # Copie avec préservation des métadonnées
            print(f"Copié : {item}")
        else:
            print(f"Ignoré (dossier) : {item}")
    except Exception as e:
        logging.error(f"Erreur avec {item}: {str(e)}")
        print(f"Erreur avec {item}, voir log pour détails")