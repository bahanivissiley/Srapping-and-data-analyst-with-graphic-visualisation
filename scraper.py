#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module de scraping pour récupérer les données des équipes de hockey.
"""

import os
import csv
import re
import time
import requests
from bs4 import BeautifulSoup


class HockeyScraper:
    """Classe permettant d'extraire les données des équipes de hockey depuis le site web."""
    
    BASE_URL = "https://www.scrapethissite.com/pages/forms/"
    
    def __init__(self):
        """Initialise le scraper avec les en-têtes HTTP nécessaires."""
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        # Créer le dossier data s'il n'existe pas
        os.makedirs('data', exist_ok=True)
    
    def build_search_url(self, team_name):
        """Construit l'URL de recherche pour l'équipe spécifiée."""
        # Nettoyer le nom de l'équipe pour la recherche
        team_query = team_name.strip().replace(' ', '+')
        return f"{self.BASE_URL}?q={team_query}"
    
    def scrape_team_data(self, team_name):
        """
        Récupère les données d'une équipe spécifique et les stocke dans un fichier CSV.
        
        Args:
            team_name (str): Nom de l'équipe à rechercher
            
        Returns:
            str: Chemin vers le fichier CSV généré
        """
        search_url = self.build_search_url(team_name)
        
        try:
            # Ajouter un délai pour éviter de surcharger le serveur
            time.sleep(1.5)
            
            # Envoyer la requête GET
            response = requests.get(search_url, headers=self.headers)
            response.raise_for_status()  # Vérifier si la requête a réussi
            
            # Analyser le contenu HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extraire les données des équipes
            team_rows = soup.select('table.table tbody tr')
            
            if not team_rows:
                print(f"Aucune donnée trouvée pour l'équipe '{team_name}'")
                return None
            
            # Préparer le fichier CSV pour enregistrer les données
            csv_filename = f"data/{team_name.replace(' ', '_').lower()}_stats.csv"
            
            # Définir les en-têtes du CSV
            fieldnames = [
                'Team Name', 'Year', 'Wins', 'Losses', 'OT Losses', 
                'Win %', 'Goals For (GF)', 'Goals Against (GA)'
            ]
            
            with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for row in team_rows:
                    # Extraire les données de chaque colonne
                    team = row.select_one('td.name').text.strip()
                    year = row.select_one('td.year').text.strip()
                    wins = row.select_one('td.wins').text.strip()
                    losses = row.select_one('td.losses').text.strip()
                    ot_losses = row.select_one('td.ot-losses').text.strip()
                    win_pct = row.select_one('td.pct').text.strip()
                    gf = row.select_one('td.gf').text.strip()
                    ga = row.select_one('td.ga').text.strip()
                    
                    # Vérifier si l'équipe correspond à celle recherchée
                    if team_name.lower() in team.lower():
                        # Écrire les données dans le CSV
                        writer.writerow({
                            'Team Name': team,
                            'Year': year,
                            'Wins': wins,
                            'Losses': losses,
                            'OT Losses': ot_losses,
                            'Win %': win_pct,
                            'Goals For (GF)': gf,
                            'Goals Against (GA)': ga
                        })
            
            print(f"Données sauvegardées dans {csv_filename}")
            return csv_filename
            
        except requests.RequestException as e:
            print(f"Erreur lors de la récupération des données: {e}")
            return None
        except Exception as e:
            print(f"Une erreur s'est produite: {e}")
            return None
    
    def scrape_multiple_teams(self, team_names):
        """
        Récupère les données pour plusieurs équipes.
        
        Args:
            team_names (list): Liste des noms d'équipes à rechercher
            
        Returns:
            list: Liste des chemins vers les fichiers CSV générés
        """
        csv_files = []
        for team in team_names:
            csv_file = self.scrape_team_data(team)
            if csv_file:
                csv_files.append(csv_file)
        return csv_files


# Test du module si exécuté directement
if __name__ == "__main__":
    scraper = HockeyScraper()
    test_team = "Boston Bruins"  # Tester avec une équipe connue
    csv_file = scraper.scrape_team_data(test_team)
    
    if csv_file:
        print(f"Test réussi! Vérifiez le fichier {csv_file}")
    else:
        print("Le test a échoué. Vérifiez le code.")