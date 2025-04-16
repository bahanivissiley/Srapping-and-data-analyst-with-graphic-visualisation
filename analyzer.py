#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module d'analyse des données des équipes de hockey.
"""

import os
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import pearsonr
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


class HockeyAnalyzer:
    """Classe d'analyse des données des équipes de hockey."""
    
    def __init__(self, csv_path=None):
        """
        Initialise l'analyseur avec les données du CSV spécifié.
        
        Args:
            csv_path (str, optional): Chemin vers le fichier CSV. Defaults to None.
        """
        self.data = None
        self.team_name = None
        
        if csv_path and os.path.exists(csv_path):
            self.load_data(csv_path)
    
    def load_data(self, csv_path):
        """
        Charge les données à partir d'un fichier CSV.
        
        Args:
            csv_path (str): Chemin vers le fichier CSV
            
        Returns:
            bool: True si le chargement a réussi, False sinon
        """
        try:
            # Extraire le nom de l'équipe à partir du nom du fichier
            filename = os.path.basename(csv_path)
            self.team_name = filename.split('_stats.csv')[0].replace('_', ' ').title()
            
            # Charger les données
            self.data = pd.read_csv(csv_path)
            
            # Convertir les colonnes en types appropriés
            self.data['Year'] = self.data['Year'].astype(int)
            self.data['Wins'] = self.data['Wins'].astype(int)
            self.data['Losses'] = self.data['Losses'].astype(int)
            self.data['OT Losses'] = self.data['OT Losses'].astype(int)
            self.data['Win %'] = self.data['Win %'].astype(float)
            self.data['Goals For (GF)'] = self.data['Goals For (GF)'].astype(int)
            self.data['Goals Against (GA)'] = self.data['Goals Against (GA)'].astype(int)
            
            # Ajouter quelques colonnes calculées
            self.data['Total Games'] = self.data['Wins'] + self.data['Losses'] + self.data['OT Losses']
            self.data['Goal Difference'] = self.data['Goals For (GF)'] - self.data['Goals Against (GA)']
            self.data['Points'] = self.data['Wins'] * 2 + self.data['OT Losses']
            
            print(f"Données chargées avec succès: {len(self.data)} saisons pour {self.team_name}")
            return True
        except Exception as e:
            print(f"Erreur lors du chargement des données: {e}")
            return False
    
    def get_basic_stats(self):
        """
        Calcule les statistiques descriptives de base.
        
        Returns:
            dict: Dictionnaire des statistiques par colonne
        """
        if self.data is None:
            return None
        
        # Colonnes numériques à analyser
        numeric_cols = ['Wins', 'Losses', 'OT Losses', 'Win %', 
                        'Goals For (GF)', 'Goals Against (GA)', 
                        'Goal Difference', 'Points']
        
        stats = {}
        for col in numeric_cols:
            stats[col] = {
                'mean': self.data[col].mean(),
                'median': self.data[col].median(),
                'std': self.data[col].std(),
                'min': self.data[col].min(),
                'max': self.data[col].max()
            }
        
        return stats
    
    def get_best_season(self, metric='Win %'):
        """
        Trouve la meilleure saison selon la métrique spécifiée.
        
        Args:
            metric (str, optional): Métrique à utiliser. Defaults to 'Win %'.
            
        Returns:
            pd.Series: Série Pandas avec les données de la meilleure saison
        """
        if self.data is None or metric not in self.data.columns:
            return None
        
        best_idx = self.data[metric].idxmax()
        return self.data.iloc[best_idx]
    
    def get_worst_season(self, metric='Win %'):
        """
        Trouve la pire saison selon la métrique spécifiée.
        
        Args:
            metric (str, optional): Métrique à utiliser. Defaults to 'Win %'.
            
        Returns:
            pd.Series: Série Pandas avec les données de la pire saison
        """
        if self.data is None or metric not in self.data.columns:
            return None
        
        worst_idx = self.data[metric].idxmin()
        return self.data.iloc[worst_idx]
    
    def calculate_correlations(self):
        """
        Calcule les corrélations entre différentes métriques.
        
        Returns:
            dict: Dictionnaire des corrélations calculées
        """
        if self.data is None:
            return None
        
        correlations = {}
        
        # Corrélation entre victoires et buts marqués
        wins_gf_corr, p_value = pearsonr(self.data['Wins'], self.data['Goals For (GF)'])
        correlations['Wins_vs_GoalsFor'] = {
            'correlation': wins_gf_corr,
            'p_value': p_value,
            'interpretation': self._interpret_correlation(wins_gf_corr)
        }
        
        # Corrélation entre pourcentage de victoires et buts encaissés
        winpct_ga_corr, p_value = pearsonr(self.data['Win %'], self.data['Goals Against (GA)'])
        correlations['WinPct_vs_GoalsAgainst'] = {
            'correlation': winpct_ga_corr,
            'p_value': p_value,
            'interpretation': self._interpret_correlation(winpct_ga_corr)
        }
        
        # Corrélation entre différence de buts et pourcentage de victoires
        goaldiff_winpct_corr, p_value = pearsonr(self.data['Goal Difference'], self.data['Win %'])
        correlations['GoalDiff_vs_WinPct'] = {
            'correlation': goaldiff_winpct_corr,
            'p_value': p_value,
            'interpretation': self._interpret_correlation(goaldiff_winpct_corr)
        }
        
        return correlations
    
    def _interpret_correlation(self, corr_value):
        """
        Interprète la valeur de corrélation.
        
        Args:
            corr_value (float): Valeur de corrélation
            
        Returns:
            str: Interprétation textuelle de la corrélation
        """
        abs_corr = abs(corr_value)
        if abs_corr < 0.1:
            strength = "négligeable"
        elif abs_corr < 0.3:
            strength = "faible"
        elif abs_corr < 0.5:
            strength = "modérée"
        elif abs_corr < 0.7:
            strength = "forte"
        elif abs_corr < 0.9:
            strength = "très forte"
        else:
            strength = "presque parfaite"
        
        direction = "positive" if corr_value > 0 else "négative"
        return f"Corrélation {strength} et {direction}"
    
    def performance_trend(self, metric='Win %'):
        """
        Analyse la tendance des performances au fil du temps.
        
        Args:
            metric (str, optional): Métrique à analyser. Defaults to 'Win %'.
            
        Returns:
            dict: Informations sur la tendance
        """
        if self.data is None or metric not in self.data.columns:
            return None
        
        # Trier les données par année
        sorted_data = self.data.sort_values('Year')
        
        # Calculer la tendance linéaire
        years = sorted_data['Year'].values
        values = sorted_data[metric].values
        
        # Utiliser np.polyfit pour trouver la pente de la droite de régression
        if len(years) >= 2:  # Besoin d'au moins 2 points pour une régression
            slope, intercept = np.polyfit(years, values, 1)
            
            # Calculer les valeurs prédites
            predictions = slope * years + intercept
            
            return {
                'slope': slope,
                'trend': 'en hausse' if slope > 0 else 'en baisse' if slope < 0 else 'stable',
                'start_value': values[0],
                'end_value': values[-1],
                'years': years.tolist(),
                'values': values.tolist(),
                'predictions': predictions.tolist()
            }
        else:
            return {
                'trend': 'indéterminée (pas assez de données)',
                'years': years.tolist(),
                'values': values.tolist()
            }
    
    def generate_plotly_data(self):
        """
        Génère des visualisations interactives avec Plotly.
        
        Returns:
            dict: Données JSON pour les graphiques Plotly
        """
        if self.data is None:
            return None
        
        # Trier les données par année
        sorted_data = self.data.sort_values('Year')
        
        # Graphique d'évolution des victoires
        wins_fig = px.line(
            sorted_data, 
            x='Year', 
            y='Wins',
            markers=True,
            title=f"Évolution des victoires de {self.team_name}",
            labels={'Year': 'Année', 'Wins': 'Nombre de victoires'},
            template='plotly_white'
        )
        
        # Ajouter la moyenne mobile
        wins_fig.add_scatter(
            x=sorted_data['Year'],
            y=sorted_data['Wins'].rolling(window=3, min_periods=1).mean(),
            mode='lines',
            line=dict(dash='dash', color='red'),
            name='Moyenne mobile (3 ans)'
        )
        
        # Graphique de comparaison des buts
        goals_fig = go.Figure()
        
        goals_fig.add_trace(go.Bar(
            x=sorted_data['Year'],
            y=sorted_data['Goals For (GF)'],
            name='Buts Marqués',
            marker_color='rgb(26, 118, 255)'
        ))
        
        goals_fig.add_trace(go.Bar(
            x=sorted_data['Year'],
            y=sorted_data['Goals Against (GA)'],
            name='Buts Encaissés',
            marker_color='rgb(255, 80, 80)'
        ))
        
        goals_fig.update_layout(
            title=f"Buts marqués et encaissés - {self.team_name}",
            xaxis=dict(title='Année'),
            yaxis=dict(title='Nombre de buts'),
            barmode='group',
            template='plotly_white'
        )
        
        # Nuage de points des buts marqués vs pourcentage de victoires
        scatter_fig = px.scatter(
            self.data,
            x='Goals For (GF)',
            y='Win %',
            color='Year',
            size='Total Games',
            hover_data=['Year', 'Wins', 'Losses', 'OT Losses'],
            trendline='ols',
            title=f"Relation entre buts marqués et pourcentage de victoires - {self.team_name}",
            labels={
                'Goals For (GF)': 'Buts marqués',
                'Win %': 'Pourcentage de victoires',
                'Year': 'Année'
            },
            template='plotly_white'
        )
        
        # Tableau de performances
        performance_table = go.Figure(data=[go.Table(
            header=dict(
                values=['Année', 'Victoires', 'Défaites', 'OT Défaites', 'Win %', 'GF', 'GA', 'Diff.'],
                fill_color='paleturquoise',
                align='left',
                font=dict(size=14)
            ),
            cells=dict(
                values=[
                    sorted_data['Year'],
                    sorted_data['Wins'],
                    sorted_data['Losses'],
                    sorted_data['OT Losses'],
                    sorted_data['Win %'].round(3),
                    sorted_data['Goals For (GF)'],
                    sorted_data['Goals Against (GA)'],
                    sorted_data['Goal Difference']
                ],
                fill_color=[
                    ['white'] * len(sorted_data),
                    [f'rgba(0, 255, 0, {win/max(sorted_data["Wins"])})' for win in sorted_data['Wins']],
                    [f'rgba(255, 0, 0, {loss/max(sorted_data["Losses"])})' for loss in sorted_data['Losses']],
                    ['white'] * len(sorted_data),
                    [f'rgba(0, 0, 255, {wp})' for wp in sorted_data['Win %']],
                    ['white'] * len(sorted_data),
                    ['white'] * len(sorted_data),
                    [
                        f'rgba(0, 255, 0, {max(0, diff)/max(abs(sorted_data["Goal Difference"]))})'
                        if diff > 0 else
                        f'rgba(255, 0, 0, {abs(min(0, diff))/max(abs(sorted_data["Goal Difference"]))})' 
                        for diff in sorted_data['Goal Difference']
                    ]
                ],
                align='left',
                font=dict(size=12)
            )
        )])
        
        performance_table.update_layout(
            title=f"Statistiques annuelles - {self.team_name}",
            height=400 + len(sorted_data) * 25
        )
        
        # Convertir les figures en JSON pour JavaScript
        return {
            'wins_evolution': wins_fig.to_json(),
            'goals_comparison': goals_fig.to_json(),
            'scatter_plot': scatter_fig.to_json(),
            'performance_table': performance_table.to_json()
        }
    
    def generate_wins_evolution_plot(self, save_path=None):
        """
        Génère un graphique montrant l'évolution des victoires au fil des années.
        
        Args:
            save_path (str, optional): Chemin pour sauvegarder le graphique. Defaults to None.
            
        Returns:
            str: Chemin vers l'image sauvegardée, ou None si échec
        """
        if self.data is None:
            return None
        
        plt.figure(figsize=(12, 6))
        
        # Trier les données par année
        sorted_data = self.data.sort_values('Year')
        
        # Tracer la courbe d'évolution des victoires
        plt.plot(sorted_data['Year'], sorted_data['Wins'], marker='o', linewidth=2, markersize=8)
        
        plt.title(f"Évolution des victoires de {self.team_name} au fil des saisons", fontsize=16)
        plt.xlabel('Année', fontsize=12)
        plt.ylabel('Nombre de victoires', fontsize=12)
        plt.grid(True, linestyle='--', alpha=0.7)
        
        # Ajouter les annotations pour chaque point
        for i, row in sorted_data.iterrows():
            plt.annotate(f"{int(row['Wins'])}", 
                         (row['Year'], row['Wins']),
                         textcoords="offset points",
                         xytext=(0, 10),
                         ha='center')
        
        plt.tight_layout()
        
        # Sauvegarder le graphique si demandé
        if save_path:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
            return save_path
        else:
            plt.close()
            return None
    
    def generate_goals_comparison_plot(self, save_path=None):
        """
        Génère un graphique comparant les buts marqués et encaissés.
        
        Args:
            save_path (str, optional): Chemin pour sauvegarder le graphique. Defaults to None.
            
        Returns:
            str: Chemin vers l'image sauvegardée, ou None si échec
        """
        if self.data is None:
            return None
        
        plt.figure(figsize=(14, 7))
        
        # Trier les données par année
        sorted_data = self.data.sort_values('Year')
        years = sorted_data['Year']
        
        # Créer un graphique à barres groupées
        x = np.arange(len(years))
        width = 0.35
        
        plt.bar(x - width/2, sorted_data['Goals For (GF)'], width, label='Buts Marqués (GF)')
        plt.bar(x + width/2, sorted_data['Goals Against (GA)'], width, label='Buts Encaissés (GA)')
        
        plt.xlabel('Année', fontsize=12)
        plt.ylabel('Nombre de buts', fontsize=12)
        plt.title(f"Comparaison des buts marqués et encaissés - {self.team_name}", fontsize=16)
        plt.xticks(x, sorted_data['Year'], rotation=45)
        plt.legend()
        plt.grid(True, axis='y', linestyle='--', alpha=0.7)
        
        plt.tight_layout()
        
        # Sauvegarder le graphique si demandé
        if save_path:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
            return save_path
        else:
            plt.close()
            return None
    
    def generate_win_percentage_boxplot(self, save_path=None):
        """
        Génère un boxplot du pourcentage de victoires.
        
        Args:
            save_path (str, optional): Chemin pour sauvegarder le graphique. Defaults to None.
            
        Returns:
            str: Chemin vers l'image sauvegardée, ou None si échec
        """
        if self.data is None:
            return None
        
        plt.figure(figsize=(10, 6))
        
        # Créer un boxplot
        sns.boxplot(y=self.data['Win %'])
        sns.stripplot(y=self.data['Win %'], color='red', jitter=True, size=8)
        
        plt.title(f"Distribution du pourcentage de victoires - {self.team_name}", fontsize=16)
        plt.ylabel('Pourcentage de victoires', fontsize=12)
        plt.grid(True, axis='y', linestyle='--', alpha=0.5)
        
        plt.tight_layout()
        
        # Sauvegarder le graphique si demandé
        if save_path:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
            return save_path
        else:
            plt.close()
            return None
    
    def generate_correlation_heatmap(self, save_path=None):
        """
        Génère une heatmap des corrélations entre différentes métriques.
        
        Args:
            save_path (str, optional): Chemin pour sauvegarder le graphique. Defaults to None.
            
        Returns:
            str: Chemin vers l'image sauvegardée, ou None si échec
        """
        if self.data is None:
            return None
        
        # Sélectionner les colonnes numériques pertinentes
        numeric_cols = ['Wins', 'Losses', 'OT Losses', 'Win %', 
                        'Goals For (GF)', 'Goals Against (GA)', 
                        'Goal Difference', 'Points']
        
        # Calculer la matrice de corrélation
        corr_matrix = self.data[numeric_cols].corr()
        
        plt.figure(figsize=(12, 10))
        
        # Créer la heatmap
        sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt=".2f", linewidths=0.5)
        
        plt.title(f"Matrice de corrélation des métriques de performance - {self.team_name}", fontsize=16)
        plt.tight_layout()
        
        # Sauvegarder le graphique si demandé
        if save_path:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
            return save_path
        else:
            plt.close()
            return None
    
    def generate_scatter_plot(self, save_path=None):
        """
        Génère un nuage de points entre les buts marqués et le pourcentage de victoires.
        
        Args:
            save_path (str, optional): Chemin pour sauvegarder le graphique. Defaults to None.
            
        Returns:
            str: Chemin vers l'image sauvegardée, ou None si échec
        """
        if self.data is None:
            return None
        
        plt.figure(figsize=(10, 8))
        
        # Créer le scatter plot
        scatter = plt.scatter(
            self.data['Goals For (GF)'], 
            self.data['Win %'],
            c=self.data['Year'],  # Colorer selon l'année
            cmap='viridis',
            s=100,
            alpha=0.7,
            edgecolors='k'
        )
        
        # Ajouter les années comme annotations
        for i, row in self.data.iterrows():
            plt.annotate(
                str(int(row['Year'])),
                (row['Goals For (GF)'], row['Win %']),
                textcoords="offset points",
                xytext=(5, 5),
                fontsize=9
            )
        
        # Ajouter une ligne de tendance
        x = self.data['Goals For (GF)']
        y = self.data['Win %']
        z = np.polyfit(x, y, 1)
        p = np.poly1d(z)
        plt.plot(x, p(x), "r--", alpha=0.8)
        
        plt.colorbar(scatter, label='Année')
        plt.title(f"Relation entre buts marqués et pourcentage de victoires - {self.team_name}", fontsize=16)
        plt.xlabel('Buts marqués (GF)', fontsize=12)
        plt.ylabel('Pourcentage de victoires', fontsize=12)
        plt.grid(True, linestyle='--', alpha=0.7)
        
        plt.tight_layout()
        
        # Sauvegarder le graphique si demandé
        if save_path:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
            return save_path
        else:
            plt.close()
            return None
    
    def generate_dashboard_data(self, static_folder='static'):
        """
        Génère toutes les visualisations et les données pour le tableau de bord.
        
        Args:
            static_folder (str, optional): Dossier pour les fichiers statiques. Defaults to 'static'.
            
        Returns:
            dict: Données pour le tableau de bord
        """
        if self.data is None:
            return None
        
        # Créer le dossier pour les visualisations
        plots_folder = os.path.join(static_folder, 'plots')
        os.makedirs(plots_folder, exist_ok=True)
        
        # Générer les visualisations
        wins_plot = self.generate_wins_evolution_plot(os.path.join(plots_folder, f"{self.team_name.lower().replace(' ', '_')}_wins.png"))
        goals_plot = self.generate_goals_comparison_plot(os.path.join(plots_folder, f"{self.team_name.lower().replace(' ', '_')}_goals.png"))
        boxplot = self.generate_win_percentage_boxplot(os.path.join(plots_folder, f"{self.team_name.lower().replace(' ', '_')}_boxplot.png"))
        heatmap = self.generate_correlation_heatmap(os.path.join(plots_folder, f"{self.team_name.lower().replace(' ', '_')}_heatmap.png"))
        scatter = self.generate_scatter_plot(os.path.join(plots_folder, f"{self.team_name.lower().replace(' ', '_')}_scatter.png"))
        
        # Générer les données pour Plotly
        plotly_data = self.generate_plotly_data()
        
        # Assembler les données pour le tableau de bord
        dashboard_data = {
            'team_name': self.team_name,
            'basic_stats': self.get_basic_stats(),
            'best_season': self.get_best_season().to_dict(),
            'worst_season': self.get_worst_season().to_dict(),
            'correlations': self.calculate_correlations(),
            'performance_trend': self.performance_trend(),
            'plots': {
                'wins_plot': os.path.basename(wins_plot) if wins_plot else None,
                'goals_plot': os.path.basename(goals_plot) if goals_plot else None,
                'boxplot': os.path.basename(boxplot) if boxplot else None,
                'heatmap': os.path.basename(heatmap) if heatmap else None,
                'scatter': os.path.basename(scatter) if scatter else None
            },
            'plotly_data': plotly_data,
            'raw_data': self.data.to_dict(orient='records')
        }
        
        return dashboard_data


# Test du module si exécuté directement
if __name__ == "__main__":
    # Tester avec un fichier existant, s'il existe
    import glob
    
    test_files = glob.glob("data/*_stats.csv")
    if test_files:
        test_file = test_files[0]
        analyzer = HockeyAnalyzer(test_file)
        
        # Tester quelques méthodes
        print("Statistiques de base:")
        print(analyzer.get_basic_stats())
        
        print("\nMeilleure saison:")
        print(analyzer.get_best_season())
        
        print("\nCorrélations:")
        print(analyzer.calculate_correlations())
        
        # Générer un graphique pour tester
        analyzer.generate_wins_evolution_plot("test_wins_plot.png")
        print("\nGraphique généré: test_wins_plot.png")
    else:
        print("Aucun fichier de données trouvé pour le test. Exécutez d'abord scraper.py.")