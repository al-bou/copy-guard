import shutil
import logging
import os
import hashlib
import sys
import signal
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

# === CONFIGURATION ===
source_dir = "I:/nextcloud/data/alandji/files_trashbin/files"
dest_dir = "G:/nextcloud_sauvegarde/files_trashbin"
os.makedirs(dest_dir, exist_ok=True)

logging.basicConfig(filename='copy_errors.log', level=logging.ERROR,
                    format='%(asctime)s - %(message)s')

dry_run = "--real" not in sys.argv  # Mode test par défaut
interrupted = threading.Event()  # Flag d'interruption


# === HANDLER CTRL+C ===
def handle_sigint(signum, frame):
    print("\n⛔ Interruption demandée. Arrêt en cours...")
    interrupted.set()

signal.signal(signal.SIGINT, handle_sigint)


# === UTILITAIRES ===
def compute_hash(file_path, block_size=65536):
    sha256 = hashlib.sha256()
    try:
        with open(file_path, 'rb') as f:
            while chunk := f.read(block_size):
                sha256.update(chunk)
        return sha256.hexdigest()
    except Exception as e:
        logging.error(f"Erreur de lecture pour le hash : {file_path} : {str(e)}")
        return None


# === TRAITEMENT PAR FICHIER ===
def process_file(src_path, dst_path):
    try:
        if os.path.exists(dst_path):
            src_stat = os.stat(src_path)
            dst_stat = os.stat(dst_path)
            if (src_stat.st_size == dst_stat.st_size and
                int(src_stat.st_mtime) == int(dst_stat.st_mtime)):
                src_hash = compute_hash(src_path)
                dst_hash = compute_hash(dst_path)
                if src_hash == dst_hash:
                    if not dry_run:
                        os.remove(src_path)
                    return "skipped-deleted" if not dry_run else "skipped-would-delete"

        shutil.copy2(src_path, dst_path)
        src_hash = compute_hash(src_path)
        dst_hash = compute_hash(dst_path)

        if src_hash and dst_hash and src_hash == dst_hash:
            if not dry_run:
                os.remove(src_path)
            return "copied-deleted" if not dry_run else "copied-would-delete"
        else:
            return "copied-mismatch"
    except Exception as e:
        logging.error(f"Erreur avec {src_path}: {str(e)}")
        return "error"


# === PARCOURS DU DOSSIER ===
def process_directory(src, dst):
    try:
        for root, dirs, files in os.walk(src):
            rel_path = os.path.relpath(root, src)
            target_root = os.path.join(dst, rel_path)
            os.makedirs(target_root, exist_ok=True)
            for file in files:
                src_file = os.path.join(root, file)
                dst_file = os.path.join(target_root, file)
                yield (src_file, dst_file)
    except Exception as e:
        logging.error(f"Erreur lors du parcours de {src}: {str(e)}")


# === SCRIPT PRINCIPAL ===
if __name__ == '__main__':
    try:
        print("🔎 Mode TEST (dry-run) : aucune suppression" if dry_run else "🧨 Mode RÉEL : fichiers supprimés après copie vérifiée")

        tasks = list(process_directory(source_dir, dest_dir))
        if not tasks:
            print("Aucun fichier à traiter.")
            sys.exit(0)

        results = {
            "copied-deleted": 0,
            "copied-would-delete": 0,
            "skipped-deleted": 0,
            "skipped-would-delete": 0,
            "copied-mismatch": 0,
            "error": 0
        }
        max_workers = min(32, 4 * os.cpu_count())
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(process_file, *task) for task in tasks]

            with tqdm(total=len(futures), desc="Traitement fichiers") as pbar:
                try:
                    for future in as_completed(futures):
                        if interrupted.is_set():
                            break
                        result = future.result()
                        if result in results:
                            results[result] += 1
                        else:
                            results["error"] += 1
                        pbar.update(1)
                except KeyboardInterrupt:
                    interrupted.set()
                    print("\n⛔ Interruption manuelle. Arrêt en cours...")

            # Nettoyage
            if interrupted.is_set():
                executor.shutdown(wait=False, cancel_futures=True)
            else:
                executor.shutdown()

        # Résumé
        print("\n✅ Traitement terminé." if not interrupted.is_set() else "\n⚠️ Traitement interrompu.")
        if dry_run:
            print(f"➡️ {results['copied-would-delete']} fichiers copiés et vérifiés (auraient été supprimés)")
            print(f"↪️ {results['skipped-would-delete']} fichiers déjà présents et identiques (auraient été supprimés)")
        else:
            print(f"➡️ {results['copied-deleted']} fichiers copiés et supprimés")
            print(f"↪️ {results['skipped-deleted']} fichiers déjà présents et identiques supprimés")

        print(f"⚠️ {results['copied-mismatch']} fichiers copiés mais non identiques (non supprimés)")
        print(f"❌ {results['error']} erreurs (voir copy_errors.log)")

    except Exception as e:
        logging.error(f"Erreur principale : {str(e)}")
        print("❌ Une erreur s’est produite. Voir copy_errors.log")
