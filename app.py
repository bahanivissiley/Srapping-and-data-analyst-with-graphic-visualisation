#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Application Flask pour l'analyse des performances des équipes de hockey.
"""

import os
import json
from flask import Flask, render_template, request, redirect, url_for, jsonify, send_from_directory
from scraper import HockeyScraper
from analyzer import HockeyAnalyzer

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = 'hockeystats2023secretkey'
app.config['UPLOAD_FOLDER'] = 'data'
app.config['STATIC_FOLDER'] = 'static'

# Assurer que les dossiers nécessaires existent
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(os.path.join(app.config['STATIC_FOLDER'], 'plots'), exist_ok=True)

# Initialiser les classes
scraper = HockeyScraper()


@app.route('/')
def index():
    """Page d'accueil."""
    return render_template('index.html')


@app.route('/search', methods=['POST'])
def search():
    """Recherche une équipe et redirige vers la page des résultats."""
    team_name = request.form.get('team_name', '').strip()
    
    if not team_name:
        return redirect(url_for('index'))
    
    # Scraper les données
    csv_file = scraper.scrape_team_data(team_name)
    
    if not csv_file:
        return render_template('index.html', error="Aucune donnée trouvée pour cette équipe. Vérifiez l'orthographe.")
    
    return redirect(url_for('results', team_name=team_name))


@app.route('/results/<team_name>')
def results(team_name):
    """Affiche les résultats d'analyse pour une équipe spécifique."""
    # Construire le chemin du fichier CSV
    csv_filename = f"data/{team_name.replace(' ', '_').lower()}_stats.csv"
    
    if not os.path.exists(csv_filename):
        return redirect(url_for('index'))
    
    # Analyser les données
    analyzer = HockeyAnalyzer(csv_filename)
    dashboard_data = analyzer.generate_dashboard_data()
    
    if not dashboard_data:
        return render_template('index.html', error="Erreur lors de l'analyse des données.")
    
    return render_template('results.html', team_name=team_name, dashboard_data=dashboard_data)


@app.route('/api/team/<team_name>')
def api_team_data(team_name):
    """API pour récupérer les données d'une équipe au format JSON."""
    # Construire le chemin du fichier CSV
    csv_filename = f"data/{team_name.replace(' ', '_').lower()}_stats.csv"
    
    if not os.path.exists(csv_filename):
        return jsonify({'error': 'Équipe non trouvée'}), 404
    
    # Analyser les données
    analyzer = HockeyAnalyzer(csv_filename)
    dashboard_data = analyzer.generate_dashboard_data()
    
    if not dashboard_data:
        return jsonify({'error': 'Erreur lors de l\'analyse des données'}), 500
    
    return jsonify(dashboard_data)


@app.route('/api/compare-teams', methods=['POST'])
def api_compare_teams():
    """API pour comparer plusieurs équipes."""
    data = request.json
    team_names = data.get('teams', [])
    metric = data.get('metric', 'Win %')
    
    if not team_names or len(team_names) < 2:
        return jsonify({'error': 'Veuillez spécifier au moins deux équipes à comparer'}), 400
    
    comparison_data = []
    for team_name in team_names:
        csv_filename = f"data/{team_name.replace(' ', '_').lower()}_stats.csv"
        
        if not os.path.exists(csv_filename):
            # Scraper les données si elles n'existent pas
            csv_filename = scraper.scrape_team_data(team_name)
            if not csv_filename:
                continue
        
        analyzer = HockeyAnalyzer(csv_filename)
        team_data = {
            'team_name': team_name,
            'years': [],
            'values': []
        }
        
        for _, row in analyzer.data.sort_values('Year').iterrows():
            team_data['years'].append(int(row['Year']))
            team_data['values'].append(float(row[metric]))
        
        team_data['avg'] = sum(team_data['values']) / len(team_data['values']) if team_data['values'] else 0
        comparison_data.append(team_data)
    
    return jsonify(comparison_data)


@app.route('/download/<team_name>')
def download_csv(team_name):
    """Télécharge le fichier CSV pour une équipe spécifique."""
    csv_filename = f"{team_name.replace(' ', '_').lower()}_stats.csv"
    return send_from_directory(app.config['UPLOAD_FOLDER'], csv_filename, as_attachment=True)


@app.route('/search-suggestions')
def search_suggestions():
    """API pour les suggestions de recherche d'équipes."""
    # Liste des équipes de hockey connues pour l'autocomplétion
    teams = [
        "Anaheim Ducks", "Arizona Coyotes", "Boston Bruins", "Buffalo Sabres", "Calgary Flames",
        "Carolina Hurricanes", "Chicago Blackhawks", "Colorado Avalanche", "Columbus Blue Jackets",
        "Dallas Stars", "Detroit Red Wings", "Edmonton Oilers", "Florida Panthers", "Los Angeles Kings",
        "Minnesota Wild", "Montreal Canadiens", "Nashville Predators", "New Jersey Devils",
        "New York Islanders", "New York Rangers", "Ottawa Senators", "Philadelphia Flyers",
        "Pittsburgh Penguins", "San Jose Sharks", "Seattle Kraken", "St. Louis Blues", "Tampa Bay Lightning",
        "Toronto Maple Leafs", "Vancouver Canucks", "Vegas Golden Knights", "Washington Capitals",
        "Winnipeg Jets"
    ]
    query = request.args.get('q', '').lower()
    
    if query:
        suggestions = [team for team in teams if query in team.lower()]
    else:
        suggestions = teams
    
    return jsonify(suggestions)


@app.route('/team-colors/<team_name>')
def team_colors(team_name):
    """API pour récupérer les couleurs associées à une équipe."""
    team_colors = {
        'anaheim ducks': {'primary': '#F47A38', 'secondary': '#B9975B'},
        'arizona coyotes': {'primary': '#8C2633', 'secondary': '#E2D6B5'},
        'boston bruins': {'primary': '#FFB81C', 'secondary': '#000000'},
        'buffalo sabres': {'primary': '#002654', 'secondary': '#FCB514'},
        'calgary flames': {'primary': '#C8102E', 'secondary': '#F1BE48'},
        'carolina hurricanes': {'primary': '#CC0000', 'secondary': '#000000'},
        'chicago blackhawks': {'primary': '#CF0A2C', 'secondary': '#FFD100'},
        'colorado avalanche': {'primary': '#6F263D', 'secondary': '#236192'},
        'columbus blue jackets': {'primary': '#002654', 'secondary': '#CE1126'},
        'dallas stars': {'primary': '#006847', 'secondary': '#8F8F8C'},
        'detroit red wings': {'primary': '#CE1126', 'secondary': '#FFFFFF'},
        'edmonton oilers': {'primary': '#041E42', 'secondary': '#FF4C00'},
        'florida panthers': {'primary': '#041E42', 'secondary': '#C8102E'},
        'los angeles kings': {'primary': '#111111', 'secondary': '#A2AAAD'},
        'minnesota wild': {'primary': '#154734', 'secondary': '#A6192E'},
        'montreal canadiens': {'primary': '#AF1E2D', 'secondary': '#192168'},
        'nashville predators': {'primary': '#FFB81C', 'secondary': '#041E42'},
        'new jersey devils': {'primary': '#CE1126', 'secondary': '#000000'},
        'new york islanders': {'primary': '#00539B', 'secondary': '#F47D30'},
        'new york rangers': {'primary': '#0038A8', 'secondary': '#CE1126'},
        'ottawa senators': {'primary': '#C52032', 'secondary': '#C2912C'},
        'philadelphia flyers': {'primary': '#F74902', 'secondary': '#000000'},
        'pittsburgh penguins': {'primary': '#000000', 'secondary': '#FCB514'},
        'san jose sharks': {'primary': '#006D75', 'secondary': '#EA7200'},
        'seattle kraken': {'primary': '#99D9D9', 'secondary': '#001F5B'},
        'st. louis blues': {'primary': '#002F87', 'secondary': '#FCB514'},
        'tampa bay lightning': {'primary': '#002868', 'secondary': '#FFFFFF'},
        'toronto maple leafs': {'primary': '#00205B', 'secondary': '#FFFFFF'},
        'vancouver canucks': {'primary': '#00205B', 'secondary': '#00843D'},
        'vegas golden knights': {'primary': '#B4975A', 'secondary': '#333F42'},
        'washington capitals': {'primary': '#C8102E', 'secondary': '#041E42'},
        'winnipeg jets': {'primary': '#041E42', 'secondary': '#004C97'}
    }
    
    team_name_lower = team_name.lower()
    if team_name_lower in team_colors:
        return jsonify(team_colors[team_name_lower])
    else:
        # Couleurs par défaut
        return jsonify({'primary': '#0066cc', 'secondary': '#ff9900'})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)