# 🏒 Hockey Team Performance Analysis  

Ce projet est une application web interactive pour l'analyse des performances des équipes de hockey. Elle utilise **Flask** pour le back-end, des **scripts de scraping** pour récupérer les données et un **module d'analyse** pour traiter et visualiser les performances des équipes.  

## 🚀 Fonctionnalités  
- **Recherche d'équipes** : Entrez le nom d'une équipe pour récupérer et analyser ses statistiques.  
- **Analyse des performances** :  
  - Affichage des statistiques sous forme de tableau.  
  - Visualisation des performances à l'aide de graphiques.  
- **Comparaison d'équipes** : Comparez les performances de plusieurs équipes sur des métriques spécifiques (par exemple, pourcentage de victoires).  
- **Téléchargement de données** : Téléchargez les statistiques d'une équipe sous forme de fichier CSV.  
- **API intégrée** :  
  - Récupération des données d'une équipe au format JSON.  
  - Comparaison des performances de plusieurs équipes via une API dédiée.  
  - Suggestions de recherche d'équipes pour l'autocomplétion.  
  - Récupération des couleurs des équipes pour un affichage personnalisé.  

## 💻 Technologies utilisées  
- **Python** pour le développement back-end.  
- **Flask** pour la gestion des routes et la structure de l'application.  
- **Scraper personnalisé** pour extraire les données des équipes.  
- **HockeyAnalyzer** pour analyser et visualiser les performances.  
- **HTML**, **CSS**, **JavaScript** pour l'interface utilisateur.  

## 📂 Structure du projet  
- `app.py` : Point d'entrée de l'application Flask.  
- `scraper.py` : Script de scraping pour récupérer les données des équipes.  
- `analyzer.py` : Analyse et traitement des données.  
- `templates/` : Dossiers contenant les fichiers HTML pour les pages web.  
- `static/` : Fichiers CSS, JavaScript et ressources graphiques.  
- `data/` : Fichiers CSV générés pour chaque équipe.  

## 🌟 Lancer l'application  
1. Cloner le dépôt :  
   ```bash  
   git clone https://github.com/username/hockey-analysis.git  
   cd hockey-analysis
   
2. Installer les dépendances :
  ```bash
  pip install -r requirements.txt

3. Lancer l'application :
```bash
python app.py
