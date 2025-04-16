/**
 * main.js - JavaScript pour la page d'accueil
 * Script principal pour la gestion de l'interface utilisateur de la page d'accueil
 */

$(document).ready(function() {
    
    // ===== Initialisation de l'autocomplétion =====
    $("#team-search").autocomplete({
        source: function(request, response) {
            $.ajax({
                url: "/search-suggestions",
                dataType: "json",
                data: {
                    q: request.term
                },
                success: function(data) {
                    response(data);
                }
            });
        },
        minLength: 2,
        select: function(event, ui) {
            $("#team-search").val(ui.item.value);
            $("#search-form").submit();
        }
    });
    
    // ===== Gestion des "team pills" =====
    $(".team-pill").on("click", function(e) {
        e.preventDefault();
        var teamName = $(this).data("team");
        $("#team-search").val(teamName);
        $("#search-form").submit();
    });
    
    // ===== Gestion du modal de comparaison =====
    // Chargement des équipes dans le select
    $.ajax({
        url: "/search-suggestions",
        dataType: "json",
        success: function(data) {
            var teamSelect = $("#team-select");
            teamSelect.empty();
            
            // Ajouter les options
            $.each(data, function(index, team) {
                teamSelect.append(
                    $("<option></option>")
                    .attr("value", team)
                    .text(team)
                );
            });
        }
    });
    
    // Bouton de comparaison
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
     * Crée un graphique de comparaison des équipes
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
    
    // ===== Animation au défilement =====
    function animateOnScroll() {
        $('.feature-card').each(function() {
            var elementPos = $(this).offset().top;
            var topOfWindow = $(window).scrollTop();
            var windowHeight = $(window).height();
            
            if (elementPos < topOfWindow + windowHeight - 100) {
                $(this).addClass('animated fadeInUp');
            }
        });
    }
    
    // Déclencher les animations au chargement et au défilement
    animateOnScroll();
    $(window).scroll(function() {
        animateOnScroll();
    });
});