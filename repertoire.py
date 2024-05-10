import requests
import os
from urllib.parse import urljoin
from datetime import datetime

def scan_directories(server_ip, server_port, wordlist_path):
    """Recherche des répertoires sur le serveur spécifié à l'aide d'une wordlist donnée."""
    base_url = f"http://{server_ip}:{server_port}"
    existing_directories = []
    scan_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")  # Format date and time

    # Vérifier si le fichier wordlist existe
    if not os.path.exists(wordlist_path):
        print("Le chemin de la wordlist est invalide.")
        return existing_directories

    # Comptage du nombre total de répertoires dans la liste de mots pour calculer la barre de progression
    total_directories = sum(1 for _ in open(wordlist_path))

    try:
        with open(wordlist_path, 'r') as file:
            for index, line in enumerate(file, start=1):
                directory = line.strip()
                if directory:
                    url = urljoin(base_url, directory)
                    try:
                        response = requests.get(url)
                        if response.status_code == 200:
                            if url != base_url:
                                existing_directories.append(url)
                        else:
                            pass  # Ne rien faire si le répertoire n'est pas trouvé
                    except requests.RequestException:
                        pass  # Do nothing if connection error occurs
                # Display progress
                print(f"\rProgression : {index}/{total_directories}", end='', flush=True)
    except IOError:
        print("Le fichier wordlist n'a pas pu être ouvert.")

    # Write results to CSV file in "Résultats Enumération" folder
    results_folder = "Résultats Enumération"
    if not os.path.exists(results_folder):
        os.makedirs(results_folder)
    csv_filename = os.path.join(results_folder, f"scan_results_{scan_datetime}.csv")
    with open(csv_filename, 'w') as csv_file:
        for directory in existing_directories:
            csv_file.write(directory + '\n')

    print(f"\nRésultats du scan enregistrés dans le fichier : {csv_filename}")

    return existing_directories

def get_user_input(prompt):
    """Get user input with error handling."""
    while True:
        user_input = input(prompt)
        if user_input.strip():
            return user_input.strip()
        else:
            print("Veuillez entrer une valeur valide.")

def main():
    """Ask user for necessary information and initiate the scan."""
    server_ip = get_user_input("Entrez l'IP du serveur à scanner : ")
    server_port = get_user_input("Entrez le port du serveur : ")
    wordlist_path = get_user_input("Entrez le chemin complet de la wordlist à utiliser : ")

    print("\nDémarrage du scan...")
    directories = scan_directories(server_ip, server_port, wordlist_path)
    if directories:
        print("\nRépertoires existants trouvés :")
        for directory in directories:
            print(directory)
    else:
        print("\nAucun répertoire existant trouvé.")

if __name__ == "__main__":
    main()
