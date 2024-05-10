import subprocess
import time
import re
import webbrowser

# Installation de Docker Compose
print("Installation de Docker Compose...")
docker_installation = subprocess.run(["sudo", "apt", "install", "-y", "docker-compose"], capture_output=True, text=True)

# Vérification de l'installation de Docker
if docker_installation.returncode == 0:
    print("Docker Compose installé avec succès.")

    # Téléchargement de l'image Docker Jenkins
    print("Téléchargement de l'image Docker Jenkins...")
    subprocess.run(["sudo", "docker", "pull", "jenkins/jenkins:2.440-jdk17"])

    # Démarrage du conteneur Jenkins
    print("Démarrage du conteneur Jenkins...")
    container_id = subprocess.run(["sudo", "docker", "run", "-d", "-p", "8080:8080", "jenkins/jenkins:2.440-jdk17"], capture_output=True, text=True).stdout.strip()

    # Attente du démarrage complet de Jenkins
    print("Attente du démarrage complet de Jenkins...")
    time.sleep(80)  # Pause permettant le temps à jenkins de s'installer 
    # Ouvrir Firefox pour rechercher l'URL de Jenkins
    webbrowser.open_new_tab("http://localhost:8080")
