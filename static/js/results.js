/**
 * results.js - JavaScript pour la page de résultats
 * Script pour afficher les visualisations et gérer l'interactivité de la page de résultats
 */

$(document).ready(function() {
    
    // ===== Initialisation des graphiques Plotly =====
    // Récupération des données JSON des visualisations Plotly
    try {
        // Évolution des victoires
        var winsEvolutionData = JSON.parse(teamData.plotly_data.wins_evolution);
        Plotly.newPlot('wins-evolution-chart', winsEvolutionData.data, winsEvolutionData.layout, {responsive: true});
        
        // Comparaison des buts
        var goalsComparisonData = JSON.parse(teamData.plotly_data.goals_comparison);
        Plotly.newPlot('goals-comparison-chart', goalsComparisonData.data, goalsComparisonData.layout, {responsive: true});
        
        // Nuage de points
        var scatterPlotData = JSON.parse(teamData.plotly_data.scatter_plot);
        Plotly.newPlot('scatter-plot', scatterPlotData.data, scatterPlotData.layout, {responsive: true});
        
        // Tableau de performance
        var performanceTableData = JSON.parse(teamData.plotly_data.performance_table);
        Plotly.newPlot('performance-table', performanceTableData.data, performanceTableData.layout, {responsive: true});
    } catch (error) {
        console.error("Erreur lors du chargement des graphiques:", error);
    }
    
    // ===== Gestion des couleurs d'équipe pour le thème =====
    $.ajax({
        url: "/team-colors/" + encodeURIComponent(teamData.team_name),
        dataType: "json",
        success: function(colors) {
            // Appliquer les couleurs d'équipe à différents éléments
            applyTeamColors(colors);
        },
        error: function() {
            console.error("Impossible de récupérer les couleurs d'équipe");
        }
    });
    
    /**
     * Applique les couleurs de l'équipe aux éléments de la page
     * @param {Object} colors Les couleurs de l'équipe (primary et secondary)
     */
    function applyTeamColors(colors) {
        // Bannière d'en-tête
        $('.results-header').css('background-color', colors.primary);
        
        // Éléments d'accent
        $('.section-title::after').css('background-color', colors.secondary);
        
        // Mettre à jour les couleurs des graphiques Plotly si possible
        try {
            var winsEvolutionData = JSON.parse(teamData.plotly_data.wins_evolution);
            if (winsEvolutionData.data && winsEvolutionData.data.length > 0) {
                winsEvolutionData.data[0].line.color = colors.primary;
                if (winsEvolutionData.data.length > 1) {
                    winsEvolutionData.data[1].line.color = colors.secondary;
                }
                Plotly.newPlot('wins-evolution-chart', winsEvolutionData.data, winsEvolutionData.layout, {responsive: true});
            }
        } catch (e) {
            console.error("Erreur lors de la mise à jour des couleurs du graphique:", e);
        }
    }
    
    // ===== Navigation fluide =====
    $('a[href^="#"]').on('click', function(event) {
        var target = $(this.getAttribute('href'));
        if (target.length) {
            event.preventDefault();
            $('html, body').stop().animate({
                scrollTop: target.offset().top - 100
            }, 1000);
        }
    });
    
    // ===== Gestion du modal de comparaison =====
    // Chargement des équipes dans le select
    $.ajax({
        url: "/search-suggestions",
        dataType: "json",
        success: function(data) {
            var teamSelect = $("#team-select");
            // Conserver l'option déjà présente (l'équipe actuelle)
            var currentTeamOption = teamSelect.find("option[value='" + teamData.team_name + "']");
            
            teamSelect.empty();
            teamSelect.append(currentTeamOption);
            
            // Ajouter les autres équipes
            $.each(data, function(index, team) {
                if (team !== teamData.team_name) {
                    teamSelect.append(
                        $("<option></option>")
                        .attr("value", team)
                        .text(team)
                    );
                }
            });
        }
    });
    
    // Bouton de comparaison (même code que dans main.js)
    $("#compare-button").on("click", function() {
        var selectedTeams = $("#team-select").val();
        var metric = $("#metric-select").val();
        
        if (!selectedTeams || selectedTeams.length < 2) {
            alert("Veuillez sélectionner au moins deux équipes à comparer.");
            return;
        }
        
        if (selectedTeams.length > 5) {
            alert("Veuillez sélectionner au maximum 5 équipes à comparer.");
            return;
        }
        
        // Afficher le spinner
        $("#comparison-chart-container").addClass("d-none");
        $("#comparison-loading").removeClass("d-none");
        $("#comparison-error").addClass("d-none");
        
        // Requête AJAX pour récupérer les données de comparaison
        $.ajax({
            url: "/api/compare-teams",
            method: "POST",
            contentType: "application/json",
            data: JSON.stringify({
                teams: selectedTeams,
                metric: metric
            }),
            success: function(data) {
                $("#comparison-loading").addClass("d-none");
                
                if (data.length < 2) {
                    $("#comparison-error").text("Impossible de récupérer suffisamment de données pour la comparaison.").removeClass("d-none");
                    return;
                }
                
                // Créer le graphique de comparaison
                createComparisonChart(data, metric);
                $("#comparison-chart-container").removeClass("d-none");
            },
            error: function(xhr, status, error) {
                $("#comparison-loading").addClass("d-none");
                $("#comparison-error").text("Erreur lors de la récupération des données: " + error).removeClass("d-none");
            }
        });
    });
    
    /**
     * Crée un graphique de comparaison des équipes (copié de main.js)
     * @param {Array} data Les données des équipes à comparer
     * @param {String} metric La métrique utilisée pour la comparaison
     */
    function createComparisonChart(data, metric) {
        var metricLabels = {
            "Win %": "Pourcentage de victoires",
            "Wins": "Victoires",
            "Goals For (GF)": "Buts marqués",
            "Goals Against (GA)": "Buts encaissés",
            "Goal Difference": "Différence de buts"
        };
        
        var plotData = [];
        var uniqueYears = new Set();
        
        // Récupérer toutes les années disponibles
        data.forEach(function(team) {
            team.years.forEach(function(year) {
                uniqueYears.add(year);
            });
        });
        
        // Trier les années
        uniqueYears = Array.from(uniqueYears).sort();
        
        // Demander les couleurs de chaque équipe
        var colorPromises = data.map(function(team) {
            return $.ajax({
                url: "/team-colors/" + encodeURIComponent(team.team_name),
                dataType: "json"
            });
        });
        
        // Une fois que toutes les requêtes de couleurs sont terminées
        Promise.all(colorPromises).then(function(colors) {
            // Créer les séries pour chaque équipe
            data.forEach(function(team, index) {
                var teamData = {
                    x: team.years,
                    y: team.values,
                    type: 'scatter',
                    mode: 'lines+markers',
                    name: team.team_name,
                    line: {
                        width: 3,
                        color: colors[index].primary
                    },
                    marker: {
                        size: 8,
                        color: colors[index].secondary
                    }
                };
                
                plotData.push(teamData);
                
                // Ajouter une ligne horizontale pour la moyenne
                var avgLine = {
                    x: [Math.min(...uniqueYears), Math.max(...uniqueYears)],
                    y: [team.avg, team.avg],
                    type: 'scatter',
                    mode: 'lines',
                    name: team.team_name + ' (Moyenne)',
                    line: {
                        dash: 'dash',
                        width: 2,
                        color: colors[index].primary
                    },
                    opacity: 0.7,
                    showlegend: false
                };
                
                plotData.push(avgLine);
            });
            
            var layout = {
                title: 'Comparaison des équipes - ' + metricLabels[metric],
                xaxis: {
                    title: 'Année',
                    tickmode: 'array',
                    tickvals: uniqueYears,
                    ticktext: uniqueYears.map(String)
                },
                yaxis: {
                    title: metricLabels[metric]
                },
                legend: {
                    x: 0,
                    y: 1.1,
                    orientation: 'h'
                },
                margin: {
                    l: 50,
                    r: 50,
                    b: 50,
                    t: 50,
                    pad: 4
                },
                hovermode: 'closest',
                template: 'plotly_white'
            };
            
            Plotly.newPlot('comparison-chart', plotData, layout, {responsive: true});
        }).catch(function(error) {
            console.error("Erreur lors de la récupération des couleurs d'équipe:", error);
            
            // Fallback: créer le graphique sans couleurs personnalisées
            data.forEach(function(team) {
                var teamData = {
                    x: team.years,
                    y: team.values,
                    type: 'scatter',
                    mode: 'lines+markers',
                    name: team.team_name
                };
                
                plotData.push(teamData);
            });
            
            var layout = {
                title: 'Comparaison des équipes - ' + metricLabels[metric],
                xaxis: {
                    title: 'Année',
                    tickmode: 'array',
                    tickvals: uniqueYears,
                    ticktext: uniqueYears.map(String)
                },
                yaxis: {
                    title: metricLabels[metric]
                },
                legend: {
                    x: 0,
                    y: 1.1,
                    orientation: 'h'
                },
                margin: {
                    l: 50,
                    r: 50,
                    b: 50,
                    t: 50,
                    pad: 4
                },
                hovermode: 'closest',
                template: 'plotly_white'
            };
            
            Plotly.newPlot('comparison-chart', plotData, layout, {responsive: true});
        });
    }
    
    // ===== Exportation des données =====
    // Permettre le téléchargement des données brutes au format CSV
    $('#export-csv').on('click', function(e) {
        e.preventDefault();
        
        // Rediriger vers l'URL de téléchargement
        window.location.href = "/download/" + encodeURIComponent(teamData.team_name);
    });
    
    // ===== Redimensionnement des graphiques =====
    // Redimensionner les graphiques lorsque la fenêtre est redimensionnée
    $(window).on('resize', function() {
        $('.plotly-chart').each(function() {
            Plotly.relayout(this.id, {
                'autosize': true
            });
        });
    });
});