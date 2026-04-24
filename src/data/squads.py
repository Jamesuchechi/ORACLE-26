
"""
◈ CONFLUX — Squad Data Engine (March 2026 Edition)
==================================================
Provides player-level data, squad lists, and market valuations.
Reflects the state of international football as of the March 2026 break.
"""

import json
import random
import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Dict, Optional
from src.utils.assets import AssetPipeline

# Constants for valuation scaling (CIES-like logic)
BASE_VALUATION_MULTIPLIER = 1.25  # General market inflation by 2026
TOP_TIER_PREMIUM = 1.5
EMERGING_TALENT_BOOST = 2.0

# Curated Star Players (March 2026 Context)
# Note: Ages and clubs reflected as of 2026.
SQUAD_STARS = {
    "Argentina": [
        {"name": "Emiliano Martínez", "pos": "GK", "age": 33, "value": 30, "club": "Aston Villa", "status": "Golden Glove"},
        {"name": "Franco Armani", "pos": "GK", "age": 39, "value": 2, "club": "River Plate", "status": "Veteran"},
        {"name": "Gerónimo Rulli", "pos": "GK", "age": 33, "value": 10, "club": "Marseille", "status": "Active"},
        {"name": "Cristian Romero", "pos": "DF", "age": 28, "value": 75, "club": "Tottenham", "status": "Wall"},
        {"name": "Nicolás Otamendi", "pos": "DF", "age": 38, "value": 5, "club": "Benfica", "status": "Leader"},
        {"name": "Lisandro Martínez", "pos": "DF", "age": 28, "value": 60, "club": "Man United", "status": "The Butcher"},
        {"name": "Nahuel Molina", "pos": "DF", "age": 28, "value": 45, "club": "Atlético Madrid", "status": "Core"},
        {"name": "Marcos Acuña", "pos": "DF", "age": 34, "value": 10, "club": "River Plate", "status": "Veteran"},
        {"name": "Rodrigo De Paul", "pos": "MF", "age": 31, "value": 40, "club": "Atlético Madrid", "status": "Motor"},
        {"name": "Enzo Fernández", "pos": "MF", "age": 25, "value": 85, "club": "Chelsea", "status": "Core"},
        {"name": "Alexis Mac Allister", "pos": "MF", "age": 27, "value": 90, "club": "Liverpool", "status": "Core"},
        {"name": "Leandro Paredes", "pos": "MF", "age": 31, "value": 20, "club": "Roma", "status": "Active"},
        {"name": "Lionel Messi", "pos": "FW", "age": 38, "value": 25, "club": "Inter Miami", "status": "GOAT"},
        {"name": "Julián Álvarez", "pos": "FW", "age": 26, "value": 95, "club": "Atlético Madrid", "status": "Star"},
        {"name": "Lautaro Martínez", "pos": "FW", "age": 28, "value": 115, "club": "Inter Milan", "status": "In-form"},
        {"name": "Ángel Di María", "pos": "FW", "age": 38, "value": 10, "club": "Benfica", "status": "Legend"},
    ],
    "England": [
        {"name": "Jordan Pickford", "pos": "GK", "age": 32, "value": 35, "club": "Everton", "status": "Number 1"},
        {"name": "Dean Henderson", "pos": "GK", "age": 29, "value": 25, "club": "Crystal Palace", "status": "Active"},
        {"name": "Aaron Ramsdale", "pos": "GK", "age": 27, "value": 30, "club": "Southampton", "status": "Active"},
        {"name": "James Trafford", "pos": "GK", "age": 23, "value": 20, "club": "Burnley", "status": "Prospect"},
        {"name": "Jason Steele", "pos": "GK", "age": 35, "value": 5, "club": "Brighton", "status": "Veteran"},
        {"name": "John Stones", "pos": "DF", "age": 31, "value": 60, "club": "Man City", "status": "Elite"},
        {"name": "Harry Maguire", "pos": "DF", "age": 33, "value": 20, "club": "Man United", "status": "Leader"},
        {"name": "Marc Guéhi", "pos": "DF", "age": 25, "value": 75, "club": "Newcastle", "status": "Core"},
        {"name": "Ezri Konsa", "pos": "DF", "age": 28, "value": 45, "club": "Aston Villa", "status": "Reliable"},
        {"name": "Ben White", "pos": "DF", "age": 28, "value": 65, "club": "Arsenal", "status": "Returned"},
        {"name": "Dan Burn", "pos": "DF", "age": 33, "value": 15, "club": "Newcastle", "status": "Giant"},
        {"name": "Lewis Hall", "pos": "DF", "age": 21, "value": 45, "club": "Newcastle", "status": "Rising"},
        {"name": "Tino Livramento", "pos": "DF", "age": 23, "value": 50, "club": "Newcastle", "status": "Rising"},
        {"name": "Fikayo Tomori", "pos": "DF", "age": 28, "value": 55, "club": "AC Milan", "status": "Active"},
        {"name": "Jarell Quansah", "pos": "DF", "age": 23, "value": 40, "club": "Liverpool", "status": "Talent"},
        {"name": "Djed Spence", "pos": "DF", "age": 25, "value": 18, "club": "Genoa", "status": "Active"},
        {"name": "Nico O’Reilly", "pos": "DF", "age": 21, "value": 25, "club": "Man City", "status": "Debut"},
        {"name": "Jude Bellingham", "pos": "MF", "age": 22, "value": 225, "club": "Real Madrid", "status": "Ballon d'Or Favorite"},
        {"name": "Declan Rice", "pos": "MF", "age": 27, "value": 120, "club": "Arsenal", "status": "Anchor"},
        {"name": "Kobbie Mainoo", "pos": "MF", "age": 21, "value": 90, "club": "Man United", "status": "Elite Talent"},
        {"name": "Adam Wharton", "pos": "MF", "age": 22, "value": 55, "club": "Crystal Palace", "status": "Maestro"},
        {"name": "Elliot Anderson", "pos": "MF", "age": 23, "value": 40, "club": "Nottingham Forest", "status": "Active"},
        {"name": "James Garner", "pos": "MF", "age": 25, "value": 35, "club": "Everton", "status": "Active"},
        {"name": "Jordan Henderson", "pos": "MF", "age": 35, "value": 5, "club": "Ajax", "status": "Veteran"},
        {"name": "Morgan Rogers", "pos": "MF", "age": 23, "value": 50, "club": "Aston Villa", "status": "Impact"},
        {"name": "Harry Kane", "pos": "FW", "age": 32, "value": 85, "club": "Bayern Munich", "status": "Legend"},
        {"name": "Phil Foden", "pos": "FW", "age": 25, "value": 160, "club": "Man City", "status": "Maestro"},
        {"name": "Bukayo Saka", "pos": "FW", "age": 24, "value": 150, "club": "Arsenal", "status": "Star"},
        {"name": "Cole Palmer", "pos": "FW", "age": 23, "value": 130, "club": "Chelsea", "status": "Cold"},
        {"name": "Anthony Gordon", "pos": "FW", "age": 25, "value": 80, "club": "Newcastle", "status": "Winger"},
        {"name": "Jarrod Bowen", "pos": "FW", "age": 29, "value": 60, "club": "West Ham", "status": "Active"},
        {"name": "Marcus Rashford", "pos": "FW", "age": 28, "value": 70, "club": "Man United", "status": "Active"},
        {"name": "Dominic Solanke", "pos": "FW", "age": 28, "value": 65, "club": "Tottenham", "status": "Striker"},
        {"name": "Dominic Calvert-Lewin", "pos": "FW", "age": 29, "value": 35, "club": "Everton", "status": "Active"},
        {"name": "Noni Madueke", "pos": "FW", "age": 24, "value": 45, "club": "Chelsea", "status": "Active"},
        {"name": "Harvey Barnes", "pos": "FW", "age": 28, "value": 40, "club": "Newcastle", "status": "Active"},
    ],
    "France": [
        {"name": "Mike Maignan", "pos": "GK", "age": 30, "value": 45, "club": "AC Milan", "status": "Number 1"},
        {"name": "Brice Samba", "pos": "GK", "age": 32, "value": 15, "club": "Lens", "status": "Active"},
        {"name": "Alphonse Areola", "pos": "GK", "age": 33, "value": 10, "club": "West Ham", "status": "Active"},
        {"name": "William Saliba", "pos": "DF", "age": 25, "value": 105, "club": "Arsenal", "status": "Elite"},
        {"name": "Dayot Upamecano", "pos": "DF", "age": 27, "value": 60, "club": "Bayern Munich", "status": "Core"},
        {"name": "Jules Koundé", "pos": "DF", "age": 27, "value": 65, "club": "Barcelona", "status": "Core"},
        {"name": "Theo Hernández", "pos": "DF", "age": 28, "value": 65, "club": "AC Milan", "status": "Speed"},
        {"name": "Benjamin Pavard", "pos": "DF", "age": 30, "value": 40, "club": "Inter Milan", "status": "Core"},
        {"name": "Lucas Hernández", "pos": "DF", "age": 30, "value": 45, "club": "PSG", "status": "Core"},
        {"name": "Aurélien Tchouaméni", "pos": "MF", "age": 26, "value": 110, "club": "Real Madrid", "status": "Pivot"},
        {"name": "Adrien Rabiot", "pos": "MF", "age": 31, "value": 35, "club": "Marseille", "status": "Active"},
        {"name": "Eduardo Camavinga", "pos": "MF", "age": 23, "value": 125, "club": "Real Madrid", "status": "Engine"},
        {"name": "Antoine Griezmann", "pos": "MF", "age": 35, "value": 25, "club": "Atlético Madrid", "status": "Maestro"},
        {"name": "Kylian Mbappé", "pos": "FW", "age": 27, "value": 210, "club": "Real Madrid", "status": "Captain & Icon"},
        {"name": "Ousmane Dembélé", "pos": "FW", "age": 28, "value": 70, "club": "PSG", "status": "Wizard"},
        {"name": "Randal Kolo Muani", "pos": "FW", "age": 27, "value": 55, "club": "PSG", "status": "Active"},
        {"name": "Marcus Thuram", "pos": "FW", "age": 28, "value": 75, "club": "Inter Milan", "status": "Active"},
        {"name": "Olivier Giroud", "pos": "FW", "age": 39, "value": 5, "club": "LAFC", "status": "Veteran"},
    ],
    "Brazil": [
        {"name": "Alisson Becker", "pos": "GK", "age": 33, "value": 30, "club": "Liverpool", "status": "Wall"},
        {"name": "Ederson", "pos": "GK", "age": 32, "value": 35, "club": "Man City", "status": "Precise"},
        {"name": "Bento", "pos": "GK", "age": 26, "value": 20, "club": "Al-Nassr", "status": "Rising"},
        {"name": "Marquinhos", "pos": "DF", "age": 31, "value": 55, "club": "PSG", "status": "Leader"},
        {"name": "Éder Militão", "pos": "DF", "age": 28, "value": 70, "club": "Real Madrid", "status": "Elite"},
        {"name": "Gabriel Magalhães", "pos": "DF", "age": 28, "value": 75, "club": "Arsenal", "status": "Titan"},
        {"name": "Danilo", "pos": "DF", "age": 34, "value": 15, "club": "Juventus", "status": "Veteran"},
        {"name": "Guilherme Arana", "pos": "DF", "age": 29, "value": 12, "club": "Atletico Mineiro", "status": "Active"},
        {"name": "Bruno Guimarães", "pos": "MF", "age": 28, "value": 90, "club": "Newcastle", "status": "Leader"},
        {"name": "Casemiro", "pos": "MF", "age": 34, "value": 20, "club": "Al-Nassr", "status": "Veteran"},
        {"name": "Lucas Paquetá", "pos": "MF", "age": 28, "value": 65, "club": "West Ham", "status": "Magic"},
        {"name": "João Gomes", "pos": "MF", "age": 25, "value": 45, "club": "Wolves", "status": "Pitbull"},
        {"name": "Neymar", "pos": "FW", "age": 34, "value": 30, "club": "Al-Hilal", "status": "Icon"},
        {"name": "Vinícius Júnior", "pos": "FW", "age": 25, "value": 200, "club": "Real Madrid", "status": "Top 3"},
        {"name": "Rodrygo", "pos": "FW", "age": 25, "value": 120, "club": "Real Madrid", "status": "Clutch"},
        {"name": "Raphinha", "pos": "FW", "age": 29, "value": 65, "club": "Barcelona", "status": "Star"},
        {"name": "Gabriel Martinelli", "pos": "FW", "age": 24, "value": 80, "club": "Arsenal", "status": "Speed"},
        {"name": "Richarlison", "pos": "FW", "age": 28, "value": 45, "club": "Tottenham", "status": "Pigeon"},
    ],
    "Spain": [
        {"name": "Unai Simón", "pos": "GK", "age": 28, "value": 45, "club": "Athletic Club", "status": "Core"},
        {"name": "David Raya", "pos": "GK", "age": 30, "value": 40, "club": "Arsenal", "status": "Active"},
        {"name": "Kepa Arrizabalaga", "pos": "GK", "age": 31, "value": 15, "club": "Bournemouth", "status": "Active"},
        {"name": "Dani Carvajal", "pos": "DF", "age": 34, "value": 15, "club": "Real Madrid", "status": "Leader"},
        {"name": "Jesús Navas", "pos": "DF", "age": 40, "value": 2, "club": "Sevilla", "status": "Veteran"},
        {"name": "Aymeric Laporte", "pos": "DF", "age": 31, "value": 25, "club": "Al-Nassr", "status": "Core"},
        {"name": "Robin Le Normand", "pos": "DF", "age": 29, "value": 45, "club": "Atlético Madrid", "status": "Core"},
        {"name": "Alejandro Balde", "pos": "DF", "age": 22, "value": 50, "club": "Barcelona", "status": "Speed"},
        {"name": "Jordi Alba", "pos": "DF", "age": 37, "value": 5, "club": "Inter Miami", "status": "Veteran"},
        {"name": "Rodri", "pos": "MF", "age": 29, "value": 120, "club": "Man City", "status": "Standard"},
        {"name": "Pedri", "pos": "MF", "age": 23, "value": 100, "club": "Barcelona", "status": "Genius"},
        {"name": "Gavi", "pos": "MF", "age": 21, "value": 110, "club": "Barcelona", "status": "Heartbeat"},
        {"name": "Fabián Ruiz", "pos": "MF", "age": 30, "value": 35, "club": "PSG", "status": "Core"},
        {"name": "Dani Olmo", "pos": "MF", "age": 27, "value": 75, "club": "Barcelona", "status": "Creative"},
        {"name": "Álvaro Morata", "pos": "FW", "age": 33, "value": 20, "club": "AC Milan", "status": "Captain"},
        {"name": "Nico Williams", "pos": "FW", "age": 23, "value": 95, "club": "Athletic Club", "status": "Electric"},
        {"name": "Lamine Yamal", "pos": "FW", "age": 18, "value": 180, "club": "Barcelona", "status": "Generational"},
    ],
    "Germany": [
        {"name": "Manuel Neuer", "pos": "GK", "age": 40, "value": 5, "club": "Bayern Munich", "status": "Legend"},
        {"name": "Marc-André ter Stegen", "pos": "GK", "age": 33, "value": 30, "club": "Barcelona", "status": "Number 1"},
        {"name": "Kevin Trapp", "pos": "GK", "age": 35, "value": 5, "club": "Eintracht Frankfurt", "status": "Active"},
        {"name": "Antonio Rüdiger", "pos": "DF", "age": 33, "value": 45, "club": "Real Madrid", "status": "Leader"},
        {"name": "Nico Schlotterbeck", "pos": "DF", "age": 26, "value": 50, "club": "Borussia Dortmund", "status": "Core"},
        {"name": "Jonathan Tah", "pos": "DF", "age": 30, "value": 40, "club": "Bayer Leverkusen", "status": "Core"},
        {"name": "Joshua Kimmich", "pos": "MF", "age": 31, "value": 60, "club": "Bayern Munich", "status": "Core"},
        {"name": "İlkay Gündoğan", "pos": "MF", "age": 35, "value": 15, "club": "Man City", "status": "Veteran"},
        {"name": "Leon Goretzka", "pos": "MF", "age": 31, "value": 35, "club": "Bayern Munich", "status": "Power"},
        {"name": "Florian Wirtz", "pos": "MF", "age": 22, "value": 160, "club": "Bayer Leverkusen", "status": "Artist"},
        {"name": "Jamal Musiala", "pos": "MF", "age": 23, "value": 150, "club": "Bayern Munich", "status": "Bambi"},
        {"name": "Leroy Sané", "pos": "FW", "age": 30, "value": 65, "club": "Bayern Munich", "status": "Flash"},
        {"name": "Serge Gnabry", "pos": "FW", "age": 30, "value": 45, "club": "Bayern Munich", "status": "Active"},
        {"name": "Niclas Füllkrug", "pos": "FW", "age": 33, "value": 20, "club": "West Ham", "status": "Striker"},
        {"name": "Thomas Müller", "pos": "FW", "age": 36, "value": 10, "club": "Bayern Munich", "status": "Legend"},
    ],
    "Portugal": [
        {"name": "Diogo Costa", "pos": "GK", "age": 26, "value": 45, "club": "FC Porto", "status": "Core"},
        {"name": "Rui Patrício", "pos": "GK", "age": 38, "value": 2, "club": "Atalanta", "status": "Veteran"},
        {"name": "José Sá", "pos": "GK", "age": 33, "value": 10, "club": "Wolves", "status": "Active"},
        {"name": "Rúben Dias", "pos": "DF", "age": 28, "value": 85, "club": "Man City", "status": "Shield"},
        {"name": "Pepe", "pos": "DF", "age": 43, "value": 1, "club": "Free Agent", "status": "Legend"},
        {"name": "António Silva", "pos": "DF", "age": 22, "value": 55, "club": "Benfica", "status": "Talent"},
        {"name": "João Cancelo", "pos": "DF", "age": 31, "value": 35, "club": "Al-Hilal", "status": "Core"},
        {"name": "Nuno Mendes", "pos": "DF", "age": 23, "value": 60, "club": "PSG", "status": "Speed"},
        {"name": "Bruno Fernandes", "pos": "MF", "age": 31, "value": 70, "club": "Man United", "status": "Magnifico"},
        {"name": "Bernardo Silva", "pos": "MF", "age": 31, "value": 75, "club": "Man City", "status": "Genius"},
        {"name": "Vitinha", "pos": "MF", "age": 26, "value": 65, "club": "PSG", "status": "Core"},
        {"name": "João Neves", "pos": "MF", "age": 21, "value": 95, "club": "PSG", "status": "Elite Prospect"},
        {"name": "Cristiano Ronaldo", "pos": "FW", "age": 41, "value": 10, "club": "Al-Nassr", "status": "Legendary"},
        {"name": "Gonçalo Ramos", "pos": "FW", "age": 24, "value": 55, "club": "PSG", "status": "Striker"},
        {"name": "Rafael Leão", "pos": "FW", "age": 26, "value": 110, "club": "AC Milan", "status": "Unstoppable"},
        {"name": "Diogo Jota", "pos": "FW", "age": 29, "value": 55, "club": "Liverpool", "status": "Active"},
    ],
    "Netherlands": [
        {"name": "Bart Verbruggen", "pos": "GK", "age": 23, "value": 35, "club": "Brighton", "status": "Number 1"},
        {"name": "Mark Flekken", "pos": "GK", "age": 32, "value": 15, "club": "Brentford", "status": "Active"},
        {"name": "Justin Bijlow", "pos": "GK", "age": 28, "value": 15, "club": "Feyenoord", "status": "Active"},
        {"name": "Virgil van Dijk", "pos": "DF", "age": 34, "value": 35, "club": "Liverpool", "status": "Captain"},
        {"name": "Matthijs de Ligt", "pos": "DF", "age": 26, "value": 75, "club": "Man United", "status": "Core"},
        {"name": "Nathan Aké", "pos": "DF", "age": 31, "value": 45, "club": "Man City", "status": "Core"},
        {"name": "Denzel Dumfries", "pos": "DF", "age": 30, "value": 30, "club": "Inter Milan", "status": "Speed"},
        {"name": "Quilindschy Hartman", "pos": "DF", "age": 24, "value": 25, "club": "Feyenoord", "status": "Active"},
        {"name": "Frenkie de Jong", "pos": "MF", "age": 28, "value": 80, "club": "Barcelona", "status": "Control"},
        {"name": "Teun Koopmeiners", "pos": "MF", "age": 28, "value": 60, "club": "Juventus", "status": "Maestro"},
        {"name": "Tijjani Reijnders", "pos": "MF", "age": 27, "value": 45, "club": "AC Milan", "status": "Core"},
        {"name": "Xavi Simons", "pos": "MF", "age": 23, "value": 115, "club": "RB Leipzig", "status": "Rising Star"},
        {"name": "Cody Gakpo", "pos": "FW", "age": 26, "value": 75, "club": "Liverpool", "status": "Clinical"},
        {"name": "Memphis Depay", "pos": "FW", "age": 32, "value": 20, "club": "Corinthians", "status": "Icon"},
        {"name": "Donyell Malen", "pos": "FW", "age": 27, "value": 40, "club": "Dortmund", "status": "Speed"},
    ],
    "Belgium": [
        {"name": "Thibaut Courtois", "pos": "GK", "age": 33, "value": 35, "club": "Real Madrid", "status": "Wall"},
        {"name": "Koen Casteels", "pos": "GK", "age": 33, "value": 10, "club": "Al-Qadsiah", "status": "Active"},
        {"name": "Matz Sels", "pos": "GK", "age": 34, "value": 8, "club": "Nottingham Forest", "status": "Active"},
        {"name": "Jan Vertonghen", "pos": "DF", "age": 39, "value": 2, "club": "Anderlecht", "status": "Veteran"},
        {"name": "Wout Faes", "pos": "DF", "age": 28, "value": 25, "club": "Leicester", "status": "Core"},
        {"name": "Arthur Theate", "pos": "DF", "age": 25, "value": 25, "club": "Frankfurt", "status": "Core"},
        {"name": "Timothy Castagne", "pos": "DF", "age": 30, "value": 20, "club": "Fulham", "status": "Core"},
        {"name": "Jérémy Doku", "pos": "FW", "age": 23, "value": 85, "club": "Man City", "status": "Speed"},
        {"name": "Kevin De Bruyne", "pos": "MF", "age": 34, "value": 60, "club": "Man City", "status": "Maestro"},
        {"name": "Youri Tielemans", "pos": "MF", "age": 28, "value": 45, "club": "Aston Villa", "status": "Core"},
        {"name": "Amadou Onana", "pos": "MF", "age": 24, "value": 65, "club": "Aston Villa", "status": "Power"},
        {"name": "Leandro Trossard", "pos": "MF", "age": 31, "value": 35, "club": "Arsenal", "status": "Impact"},
        {"name": "Romelu Lukaku", "pos": "FW", "age": 32, "value": 35, "club": "Napoli", "status": "Striker"},
        {"name": "Loïs Openda", "pos": "FW", "age": 26, "value": 75, "club": "RB Leipzig", "status": "Speed"},
    ],
    "Italy": [],
    "Chile": [
        {"name": "Claudio Bravo", "pos": "GK", "age": 43, "value": 1, "club": "Retired", "status": "Icon"},
        {"name": "Brayan Cortés", "pos": "GK", "age": 31, "value": 5, "club": "Colo-Colo", "status": "Number 1"},
        {"name": "Gary Medel", "pos": "DF", "age": 38, "value": 2, "club": "Boca Juniors", "status": "Pitbull"},
        {"name": "Guillermo Maripán", "pos": "DF", "age": 32, "value": 15, "club": "Torino", "status": "Core"},
        {"name": "Gabriel Suazo", "pos": "DF", "age": 28, "value": 12, "club": "Toulouse", "status": "Core"},
        {"name": "Mauricio Isla", "pos": "DF", "age": 37, "value": 1, "club": "Colo-Colo", "status": "Veteran"},
        {"name": "Erick Pulgar", "pos": "MF", "age": 32, "value": 10, "club": "Flamengo", "status": "Anchor"},
        {"name": "Marcelino Núñez", "pos": "MF", "age": 26, "value": 15, "club": "Norwich City", "status": "Core"},
        {"name": "Arturo Vidal", "pos": "MF", "age": 38, "value": 1, "club": "Colo-Colo", "status": "King"},
        {"name": "Alexis Sánchez", "pos": "FW", "age": 37, "value": 5, "club": "Udinese", "status": "Legend"},
        {"name": "Víctor Dávila", "pos": "FW", "age": 28, "value": 8, "club": "América", "status": "Active"},
        {"name": "Ben Brereton Díaz", "pos": "FW", "age": 27, "value": 10, "club": "Southampton", "status": "Striker"},
    ],
    "Peru": [
        {"name": "Pedro Gallese", "pos": "GK", "age": 36, "value": 2, "club": "Orlando City", "status": "Wall"},
        {"name": "Carlos Cáceda", "pos": "GK", "age": 34, "value": 1, "club": "Melgar", "status": "Active"},
        {"name": "Luis Advíncula", "pos": "DF", "age": 36, "value": 2, "club": "Boca Juniors", "status": "Bolt"},
        {"name": "Carlos Zambrano", "pos": "DF", "age": 36, "value": 1, "club": "Alianza Lima", "status": "Leader"},
        {"name": "Alexander Callens", "pos": "DF", "age": 34, "value": 2, "club": "AEK Athens", "status": "Core"},
        {"name": "Miguel Trauco", "pos": "DF", "age": 33, "value": 1, "club": "Criciúma", "status": "Active"},
        {"name": "Renato Tapia", "pos": "MF", "age": 30, "value": 10, "club": "Leganés", "status": "Pivot"},
        {"name": "Yoshimar Yotún", "pos": "MF", "age": 36, "value": 1, "club": "Sporting Cristal", "status": "Veteran"},
        {"name": "André Carrillo", "pos": "FW", "age": 34, "value": 2, "club": "Corinthians", "status": "Wizard"},
        {"name": "Christian Cueva", "pos": "FW", "age": 34, "value": 1, "club": "Cienciano", "status": "Active"},
        {"name": "Gianluca Lapadula", "pos": "FW", "age": 36, "value": 2, "club": "Cagliari", "status": "Striker"},
        {"name": "Paolo Guerrero", "pos": "FW", "age": 42, "value": 1, "club": "Alianza Lima", "status": "Legend"},
    ],
    "Venezuela": [
        {"name": "Rafael Romo", "pos": "GK", "age": 36, "value": 1, "club": "Universidad Católica", "status": "Wall"},
        {"name": "Joel Graterol", "pos": "GK", "age": 29, "value": 1, "club": "América de Cali", "status": "Active"},
        {"name": "Yordan Osorio", "pos": "DF", "age": 31, "value": 5, "club": "Parma", "status": "Core"},
        {"name": "Nahuel Ferraresi", "pos": "DF", "age": 27, "value": 5, "club": "São Paulo", "status": "Core"},
        {"name": "Miguel Navarro", "pos": "DF", "age": 27, "value": 3, "club": "Talleres", "status": "Active"},
        {"name": "Roberto Rosales", "pos": "DF", "age": 37, "value": 1, "club": "Sport Recife", "status": "Veteran"},
        {"name": "Yangel Herrera", "pos": "MF", "age": 28, "value": 25, "club": "Girona", "status": "Star"},
        {"name": "Tomás Rincón", "pos": "MF", "age": 38, "value": 1, "club": "Santos", "status": "General"},
        {"name": "José Martínez", "pos": "MF", "age": 31, "value": 3, "club": "Corinthians", "status": "Active"},
        {"name": "Jefferson Savarino", "pos": "FW", "age": 29, "value": 8, "club": "Botafogo", "status": "Active"},
        {"name": "Salomón Rondón", "pos": "FW", "age": 36, "value": 2, "club": "Pachuca", "status": "King"},
        {"name": "Darwin Machís", "pos": "FW", "age": 33, "value": 3, "club": "Real Valladolid", "status": "Speed"},
    ],
    "Mexico": [
        {"name": "Guillermo Ochoa", "pos": "GK", "age": 40, "value": 2, "club": "AVS", "status": "Legend"},
        {"name": "Luis Malagón", "pos": "GK", "age": 29, "value": 15, "club": "América", "status": "Core"},
        {"name": "Johan Vásquez", "pos": "DF", "age": 27, "value": 25, "club": "Genoa", "status": "Core"},
        {"name": "César Montes", "pos": "DF", "age": 29, "value": 20, "club": "Lokomotiv Moscow", "status": "Core"},
        {"name": "Jesús Gallardo", "pos": "DF", "age": 31, "value": 8, "club": "Toluca", "status": "Active"},
        {"name": "Jorge Sánchez", "pos": "DF", "age": 28, "value": 10, "club": "Cruz Azul", "status": "Active"},
        {"name": "Edson Álvarez", "pos": "MF", "age": 28, "value": 55, "club": "West Ham", "status": "Leader"},
        {"name": "Luis Chávez", "pos": "MF", "age": 30, "value": 18, "club": "Dynamo Moscow", "status": "Core"},
        {"name": "Orbelín Pineda", "pos": "MF", "age": 30, "value": 12, "club": "AEK Athens", "status": "Active"},
        {"name": "Hirving Lozano", "pos": "FW", "age": 30, "value": 35, "club": "San Diego FC", "status": "Star"},
        {"name": "Uriel Antuna", "pos": "FW", "age": 28, "value": 15, "club": "Tigres", "status": "Speed"},
        {"name": "Santiago Giménez", "pos": "FW", "age": 25, "value": 60, "club": "Feyenoord", "status": "Goal Machine"},
        {"name": "Raúl Jiménez", "pos": "FW", "age": 34, "value": 15, "club": "Fulham", "status": "Veteran"},
    ],
    "Canada": [
        {"name": "Maxime Crépeau", "pos": "GK", "age": 32, "value": 5, "club": "Portland Timbers", "status": "Core"},
        {"name": "Milan Borjan", "pos": "GK", "age": 38, "value": 1, "club": "Slovan Bratislava", "status": "Veteran"},
        {"name": "Alistair Johnston", "pos": "DF", "age": 27, "value": 25, "club": "Celtic", "status": "Core"},
        {"name": "Moïse Bombito", "pos": "DF", "age": 26, "value": 15, "club": "Nice", "status": "Rising"},
        {"name": "Kamal Miller", "pos": "DF", "age": 28, "value": 10, "club": "Portland Timbers", "status": "Core"},
        {"name": "Richie Laryea", "pos": "DF", "age": 31, "value": 8, "club": "Toronto FC", "status": "Active"},
        {"name": "Alphonso Davies", "pos": "DF", "age": 25, "value": 85, "club": "Real Madrid", "status": "Global Star"},
        {"name": "Stephen Eustáquio", "pos": "MF", "age": 29, "value": 30, "club": "FC Porto", "status": "Anchor"},
        {"name": "Ismaël Koné", "pos": "MF", "age": 23, "value": 35, "club": "Marseille", "status": "Rising"},
        {"name": "Jonathan David", "pos": "FW", "age": 26, "value": 75, "club": "Napoli", "status": "Elite"},
        {"name": "Cyle Larin", "pos": "FW", "age": 31, "value": 15, "club": "Mallorca", "status": "Active"},
        {"name": "Tajon Buchanan", "pos": "FW", "age": 27, "value": 25, "club": "Inter Milan", "status": "Speed"},
    ],
    "Uruguay": [
        {"name": "Sergio Rochet", "pos": "GK", "age": 33, "value": 8, "club": "Internacional", "status": "Core"},
        {"name": "Santiago Mele", "pos": "GK", "age": 28, "value": 5, "club": "Junior", "status": "Active"},
        {"name": "Ronald Araújo", "pos": "DF", "age": 27, "value": 85, "club": "Barcelona", "status": "Wall"},
        {"name": "José María Giménez", "pos": "DF", "age": 31, "value": 40, "club": "Atlético Madrid", "status": "Leader"},
        {"name": "Mathías Olivera", "pos": "DF", "age": 28, "value": 30, "club": "Napoli", "status": "Core"},
        {"name": "Guillermo Varela", "pos": "DF", "age": 33, "value": 5, "club": "Flamengo", "status": "Active"},
        {"name": "Federico Valverde", "pos": "MF", "age": 27, "value": 130, "club": "Real Madrid", "status": "Elite"},
        {"name": "Manuel Ugarte", "pos": "MF", "age": 25, "value": 70, "club": "Man United", "status": "Pivot"},
        {"name": "Rodrigo Bentancur", "pos": "MF", "age": 28, "value": 55, "club": "Tottenham", "status": "Core"},
        {"name": "Giorgian De Arrascaeta", "pos": "MF", "age": 31, "value": 20, "club": "Flamengo", "status": "Creative"},
        {"name": "Darwin Núñez", "pos": "FW", "age": 26, "value": 95, "club": "Liverpool", "status": "Striker"},
        {"name": "Luis Suárez", "pos": "FW", "age": 39, "value": 5, "club": "Inter Miami", "status": "Legend"},
        {"name": "Facundo Pellistri", "pos": "FW", "age": 24, "value": 25, "club": "Panathinaikos", "status": "Active"},
    ],
    "Ecuador": [
        {"name": "Hernán Galíndez", "pos": "GK", "age": 39, "value": 1, "club": "Huracán", "status": "Veteran"},
        {"name": "Alexander Domínguez", "pos": "GK", "age": 38, "value": 1, "club": "LDU Quito", "status": "Legend"},
        {"name": "Pervis Estupiñán", "pos": "DF", "age": 28, "value": 45, "club": "Brighton", "status": "Elite"},
        {"name": "Félix Torres", "pos": "DF", "age": 29, "value": 10, "club": "Corinthians", "status": "Core"},
        {"name": "Piero Hincapié", "pos": "DF", "age": 24, "value": 75, "club": "Bayer Leverkusen", "status": "Elite"},
        {"name": "Ángelo Preciado", "pos": "DF", "age": 28, "value": 15, "club": "Sparta Prague", "status": "Speed"},
        {"name": "Moisés Caicedo", "pos": "MF", "age": 24, "value": 110, "club": "Chelsea", "status": "Engine"},
        {"name": "Alan Franco", "pos": "MF", "age": 27, "value": 10, "club": "Atlético Mineiro", "status": "Core"},
        {"name": "Carlos Gruezo", "pos": "MF", "age": 31, "value": 5, "club": "San Jose Earthquakes", "status": "Anchor"},
        {"name": "Gonzalo Plata", "pos": "FW", "age": 25, "value": 20, "club": "Flamengo", "status": "Wizard"},
        {"name": "Enner Valencia", "pos": "FW", "age": 36, "value": 5, "club": "Internacional", "status": "Legend"},
        {"name": "Kevin Rodríguez", "pos": "FW", "age": 26, "value": 8, "club": "Union SG", "status": "Active"},
    ],
    "Japan": [
        {"name": "Zion Suzuki", "pos": "GK", "age": 23, "value": 15, "club": "Parma", "status": "Rising"},
        {"name": "Eiji Kawashima", "pos": "GK", "age": 43, "value": 1, "club": "Jubilo Iwata", "status": "Legend"},
        {"name": "Takehiro Tomiyasu", "pos": "DF", "age": 27, "value": 55, "club": "Arsenal", "status": "Elite"},
        {"name": "Ko Itakura", "pos": "DF", "age": 29, "value": 25, "club": "Gladbach", "status": "Core"},
        {"name": "Hiroki Ito", "pos": "DF", "age": 27, "value": 45, "club": "Bayern Munich", "status": "Core"},
        {"name": "Yuto Nagatomo", "pos": "DF", "age": 39, "value": 1, "club": "FC Tokyo", "status": "Veteran"},
        {"name": "Wataru Endo", "pos": "MF", "age": 33, "value": 20, "club": "Liverpool", "status": "Captain"},
        {"name": "Hidemasa Morita", "pos": "MF", "age": 31, "value": 25, "club": "Sporting CP", "status": "Control"},
        {"name": "Daichi Kamada", "pos": "MF", "age": 29, "value": 30, "club": "Crystal Palace", "status": "Creative"},
        {"name": "Takefusa Kubo", "pos": "FW", "age": 24, "value": 75, "club": "Real Sociedad", "status": "Genius"},
        {"name": "Kaoru Mitoma", "pos": "FW", "age": 28, "value": 65, "club": "Brighton", "status": "Wizard"},
        {"name": "Ayase Ueda", "pos": "FW", "age": 27, "value": 20, "club": "Feyenoord", "status": "Striker"},
        {"name": "Kyogo Furuhashi", "pos": "FW", "age": 31, "value": 18, "club": "Celtic", "status": "Active"},
    ],
    "South Korea": [
        {"name": "Kim Seung-gyu", "pos": "GK", "age": 35, "value": 2, "club": "Al-Shabab", "status": "Veteran"},
        {"name": "Jo Hyeon-woo", "pos": "GK", "age": 34, "value": 1, "club": "Ulsan HD", "status": "Active"},
        {"name": "Kim Min-jae", "pos": "DF", "age": 29, "value": 70, "club": "Bayern Munich", "status": "Monster"},
        {"name": "Kim Young-gwon", "pos": "DF", "age": 36, "value": 1, "club": "Ulsan HD", "status": "Veteran"},
        {"name": "Seol Young-woo", "pos": "DF", "age": 27, "value": 10, "club": "Crvena Zvezda", "status": "Core"},
        {"name": "Lee Ki-je", "pos": "DF", "age": 34, "value": 1, "club": "Suwon Samsung", "status": "Active"},
        {"name": "Hwang In-beom", "pos": "MF", "age": 29, "value": 25, "club": "Feyenoord", "status": "Control"},
        {"name": "Jung Woo-young", "pos": "MF", "age": 36, "value": 1, "club": "Ulsan HD", "status": "Veteran"},
        {"name": "Lee Kang-in", "pos": "MF", "age": 25, "value": 60, "club": "PSG", "status": "Creative"},
        {"name": "Son Heung-min", "pos": "FW", "age": 33, "value": 40, "club": "Inter Miami", "status": "Legend"},
        {"name": "Hwang Hee-chan", "pos": "FW", "age": 30, "value": 35, "club": "Wolves", "status": "Bull"},
        {"name": "Cho Gue-sung", "pos": "FW", "age": 28, "value": 10, "club": "Midtjylland", "status": "Striker"},
    ],
    "Morocco": [
        {"name": "Yassine Bounou", "pos": "GK", "age": 35, "value": 15, "club": "Al-Hilal", "status": "Wall"},
        {"name": "Munir Mohamedi", "pos": "GK", "age": 36, "value": 2, "club": "RS Berkane", "status": "Active"},
        {"name": "Achraf Hakimi", "pos": "DF", "age": 27, "value": 80, "club": "PSG", "status": "Elite"},
        {"name": "Noussair Mazraoui", "pos": "DF", "age": 28, "value": 45, "club": "Man United", "status": "Core"},
        {"name": "Romain Saïss", "pos": "DF", "age": 36, "value": 5, "club": "Al-Sadd", "status": "Captain"},
        {"name": "Nayef Aguerd", "pos": "DF", "age": 30, "value": 40, "club": "Real Sociedad", "status": "Core"},
        {"name": "Sofyan Amrabat", "pos": "MF", "age": 29, "value": 35, "club": "Fenerbahce", "status": "Anchor"},
        {"name": "Azzedine Ounahi", "pos": "MF", "age": 26, "value": 20, "club": "Panathinaikos", "status": "Creative"},
        {"name": "Selim Amallah", "pos": "MF", "age": 29, "value": 10, "club": "Valencia", "status": "Active"},
        {"name": "Hakim Ziyech", "pos": "FW", "age": 33, "value": 15, "club": "Galatasaray", "status": "Wizard"},
        {"name": "Sofiane Boufal", "pos": "FW", "age": 32, "value": 10, "club": "Union SG", "status": "Active"},
        {"name": "Youssef En-Nesyri", "pos": "FW", "age": 28, "value": 35, "club": "Fenerbahce", "status": "Striker"},
        {"name": "Abde Ezzalzouli", "pos": "FW", "age": 24, "value": 25, "club": "Real Betis", "status": "Active"},
    ],
    "Senegal": [
        {"name": "Edouard Mendy", "pos": "GK", "age": 34, "value": 15, "club": "Al-Ahli", "status": "Wall"},
        {"name": "Seny Dieng", "pos": "GK", "age": 31, "value": 5, "club": "Middlesbrough", "status": "Active"},
        {"name": "Kalidou Koulibaly", "pos": "DF", "age": 34, "value": 10, "club": "Al-Hilal", "status": "Leader"},
        {"name": "Abdou Diallo", "pos": "DF", "age": 29, "value": 15, "club": "Al-Arabi", "status": "Core"},
        {"name": "Ismaël Jakobs", "pos": "DF", "age": 26, "value": 20, "club": "Galatasaray", "status": "Speed"},
        {"name": "Idrissa Gueye", "pos": "MF", "age": 36, "value": 5, "club": "Everton", "status": "Veteran"},
        {"name": "Pape Matar Sarr", "pos": "MF", "age": 23, "value": 65, "club": "Tottenham", "status": "Engine"},
        {"name": "Nampalys Mendy", "pos": "MF", "age": 33, "value": 5, "club": "Lens", "status": "Active"},
        {"name": "Sadio Mané", "pos": "FW", "age": 34, "value": 20, "club": "Al-Nassr", "status": "Legend"},
        {"name": "Ismaïla Sarr", "pos": "FW", "age": 28, "value": 30, "club": "Crystal Palace", "status": "Speed"},
        {"name": "Nicolas Jackson", "pos": "FW", "age": 24, "value": 75, "club": "Chelsea", "status": "Star"},
        {"name": "Boulaye Dia", "pos": "FW", "age": 29, "value": 20, "club": "Lazio", "status": "Active"},
    ],
    "Norway": [
        {"name": "Ørjan Nyland", "pos": "GK", "age": 35, "value": 2, "club": "Sevilla", "status": "Core"},
        {"name": "Kristoffer Klaesson", "pos": "GK", "age": 25, "value": 1, "club": "Aarhus", "status": "Active"},
        {"name": "Stefan Strandberg", "pos": "DF", "age": 35, "value": 1, "club": "Valerenga", "status": "Veteran"},
        {"name": "Leo Østigård", "pos": "DF", "age": 26, "value": 15, "club": "Rennes", "status": "Core"},
        {"name": "Birger Meling", "pos": "DF", "age": 31, "value": 5, "club": "Copenhagen", "status": "Core"},
        {"name": "Marcus Holmgren Pedersen", "pos": "DF", "age": 25, "value": 8, "club": "Feyenoord", "status": "Speed"},
        {"name": "Martin Ødegaard", "pos": "MF", "age": 27, "value": 140, "club": "Arsenal", "status": "Maestro"},
        {"name": "Sander Berge", "pos": "MF", "age": 28, "value": 25, "club": "Fulham", "status": "Core"},
        {"name": "Patrick Berg", "pos": "MF", "age": 28, "value": 10, "club": "Bodo/Glimt", "status": "Anchor"},
        {"name": "Antonio Nusa", "pos": "FW", "age": 21, "value": 50, "club": "RB Leipzig", "status": "Wizard"},
        {"name": "Erling Haaland", "pos": "FW", "age": 25, "value": 250, "club": "Man City", "status": "Cyborg"},
        {"name": "Alexander Sørloth", "pos": "FW", "age": 30, "value": 35, "club": "Atlético Madrid", "status": "Striker"},
    ],
    "Sweden": [
        {"name": "Robin Olsen", "pos": "GK", "age": 36, "value": 1, "club": "Aston Villa", "status": "Veteran"},
        {"name": "Kristoffer Nordfeldt", "pos": "GK", "age": 36, "value": 1, "club": "AIK", "status": "Active"},
        {"name": "Victor Lindelöf", "pos": "DF", "age": 31, "value": 15, "club": "Man United", "status": "Captain"},
        {"name": "Isak Hien", "pos": "DF", "age": 27, "value": 25, "club": "Atalanta", "status": "Core"},
        {"name": "Ludwig Augustinsson", "pos": "DF", "age": 32, "value": 3, "club": "Anderlecht", "status": "Core"},
        {"name": "Emil Krafth", "pos": "DF", "age": 31, "value": 3, "club": "Newcastle", "status": "Active"},
        {"name": "Dejan Kulusevski", "pos": "MF", "age": 26, "value": 75, "club": "Tottenham", "status": "Star"},
        {"name": "Albin Ekdal", "pos": "MF", "age": 36, "value": 1, "club": "Djurgården", "status": "Veteran"},
        {"name": "Jens Cajuste", "pos": "MF", "age": 26, "value": 12, "club": "Ipswich", "status": "Active"},
        {"name": "Emil Forsberg", "pos": "MF", "age": 34, "value": 5, "club": "New York Red Bulls", "status": "Legend"},
        {"name": "Alexander Isak", "pos": "FW", "age": 26, "value": 100, "club": "Newcastle", "status": "Elite"},
        {"name": "Anthony Elanga", "pos": "FW", "age": 24, "value": 35, "club": "Nottingham Forest", "status": "Speed"},
    ],
    "Austria": [
        {"name": "Alexander Schlager", "pos": "GK", "age": 30, "value": 5, "club": "RB Salzburg", "status": "Core"},
        {"name": "Patrick Pentz", "pos": "GK", "age": 29, "value": 3, "club": "Brøndby", "status": "Active"},
        {"name": "David Alaba", "pos": "DF", "age": 33, "value": 25, "club": "Real Madrid", "status": "Captain"},
        {"name": "Maximilian Wöber", "pos": "DF", "age": 28, "value": 15, "club": "Leeds", "status": "Core"},
        {"name": "Stefan Posch", "pos": "DF", "age": 28, "value": 20, "club": "Bologna", "status": "Core"},
        {"name": "Phillipp Mwene", "pos": "DF", "age": 32, "value": 3, "club": "Mainz", "status": "Active"},
        {"name": "Marcel Sabitzer", "pos": "MF", "age": 32, "value": 25, "club": "Dortmund", "status": "Maestro"},
        {"name": "Konrad Laimer", "pos": "MF", "age": 28, "value": 35, "club": "Bayern Munich", "status": "Engine"},
        {"name": "Nicolas Seiwald", "pos": "MF", "age": 24, "value": 25, "club": "RB Leipzig", "status": "Anchor"},
        {"name": "Christoph Baumgartner", "pos": "MF", "age": 26, "value": 40, "club": "RB Leipzig", "status": "Creative"},
        {"name": "Marko Arnautović", "pos": "FW", "age": 37, "value": 5, "club": "Inter Milan", "status": "Legend"},
        {"name": "Michael Gregoritsch", "pos": "FW", "age": 32, "value": 10, "club": "Freiburg", "status": "Striker"},
    ],
    "Ukraine": [
        {"name": "Andriy Lunin", "pos": "GK", "age": 27, "value": 35, "club": "Real Madrid", "status": "Wall"},
        {"name": "Anatoliy Trubin", "pos": "GK", "age": 24, "value": 45, "club": "Benfica", "status": "Core"},
        {"name": "Oleksandr Zinchenko", "pos": "DF", "age": 29, "value": 35, "club": "Arsenal", "status": "Leader"},
        {"name": "Illia Zabarnyi", "pos": "DF", "age": 23, "value": 50, "club": "Bournemouth", "status": "Titan"},
        {"name": "Mykola Matviyenko", "pos": "DF", "age": 29, "value": 25, "club": "Shakhtar Donetsk", "status": "Core"},
        {"name": "Vitaliy Mykolenko", "pos": "DF", "age": 26, "value": 35, "club": "Everton", "status": "Core"},
        {"name": "Taras Stepanenko", "pos": "MF", "age": 36, "value": 2, "club": "Shakhtar Donetsk", "status": "Veteran"},
        {"name": "Georgiy Sudakov", "pos": "MF", "age": 23, "value": 60, "club": "Shakhtar Donetsk", "status": "Star"},
        {"name": "Mykhailo Mudryk", "pos": "FW", "age": 25, "value": 65, "club": "Chelsea", "status": "Speed"},
        {"name": "Viktor Tsygankov", "pos": "FW", "age": 28, "value": 45, "club": "Girona", "status": "Creative"},
        {"name": "Artem Dovbyk", "pos": "FW", "age": 28, "value": 60, "club": "Roma", "status": "Pichichi"},
        {"name": "Roman Yaremchuk", "pos": "FW", "age": 30, "value": 10, "club": "Olympiacos", "status": "Active"},
    ],
    "Czechia": [
        {"name": "Jiří Pavlenka", "pos": "GK", "age": 34, "value": 2, "club": "PAOK", "status": "Active"},
        {"name": "Tomáš Vaclík", "pos": "GK", "age": 37, "value": 1, "club": "Albacete", "status": "Veteran"},
        {"name": "Tomáš Souček", "pos": "MF", "age": 31, "value": 40, "club": "West Ham", "status": "Captain"},
        {"name": "Vladimír Coufal", "pos": "DF", "age": 33, "value": 5, "club": "West Ham", "status": "Core"},
        {"name": "Ladislav Krejčí", "pos": "DF", "age": 27, "value": 15, "club": "Girona", "status": "Core"},
        {"name": "David Zima", "pos": "DF", "age": 25, "value": 8, "club": "Slavia Prague", "status": "Active"},
        {"name": "Alex Král", "pos": "MF", "age": 27, "value": 10, "club": "Espanyol", "status": "Active"},
        {"name": "Václav Černý", "pos": "FW", "age": 28, "value": 12, "club": "Rangers", "status": "Active"},
        {"name": "Adam Hložek", "pos": "FW", "age": 23, "value": 25, "club": "Hoffenheim", "status": "Talent"},
        {"name": "Patrik Schick", "pos": "FW", "age": 30, "value": 35, "club": "Bayer Leverkusen", "status": "Elite"},
        {"name": "Jan Kuchta", "pos": "FW", "age": 29, "value": 5, "club": "Midtjylland", "status": "Active"},
    ],
    "USA": [
        {"name": "Matt Turner", "pos": "GK", "age": 31, "value": 10, "club": "Crystal Palace", "status": "Core"},
        {"name": "Ethan Horvath", "pos": "GK", "age": 30, "value": 5, "club": "Cardiff City", "status": "Active"},
        {"name": "Tim Ream", "pos": "DF", "age": 38, "value": 2, "club": "Charlotte FC", "status": "Veteran"},
        {"name": "Walker Zimmerman", "pos": "DF", "age": 32, "value": 5, "club": "Nashville SC", "status": "Leader"},
        {"name": "Chris Richards", "pos": "DF", "age": 26, "value": 35, "club": "Crystal Palace", "status": "Core"},
        {"name": "Antonee Robinson", "pos": "DF", "age": 28, "value": 45, "club": "Fulham", "status": "Jedi"},
        {"name": "Sergiño Dest", "pos": "DF", "age": 25, "value": 25, "club": "PSV", "status": "Active"},
        {"name": "Weston McKennie", "pos": "MF", "age": 27, "value": 40, "club": "Juventus", "status": "Core"},
        {"name": "Yunus Musah", "pos": "MF", "age": 23, "value": 40, "club": "AC Milan", "status": "Engine"},
        {"name": "Tyler Adams", "pos": "MF", "age": 27, "value": 45, "club": "Bournemouth", "status": "Anchor"},
        {"name": "Gio Reyna", "pos": "MF", "age": 23, "value": 40, "club": "Dortmund", "status": "Creative"},
        {"name": "Christian Pulisic", "pos": "FW", "age": 27, "value": 65, "club": "AC Milan", "status": "Captain America"},
        {"name": "Timothy Weah", "pos": "FW", "age": 26, "value": 35, "club": "Juventus", "status": "Speed"},
        {"name": "Folarin Balogun", "pos": "FW", "age": 24, "value": 45, "club": "Monaco", "status": "Striker"},
    ],
    "Croatia": [
        {"name": "Dominik Livaković", "pos": "GK", "age": 31, "value": 15, "club": "Fenerbahce", "status": "Wall"},
        {"name": "Ivica Ivušić", "pos": "GK", "age": 31, "value": 5, "club": "Pafos", "status": "Active"},
        {"name": "Joško Gvardiol", "pos": "DF", "age": 24, "value": 120, "club": "Man City", "status": "Elite"},
        {"name": "Dejan Lovren", "pos": "DF", "age": 36, "value": 2, "club": "PAOK", "status": "Veteran"},
        {"name": "Josip Stanišić", "pos": "DF", "age": 26, "value": 40, "club": "Bayern Munich", "status": "Core"},
        {"name": "Borna Sosa", "pos": "DF", "age": 28, "value": 20, "club": "Torino", "status": "Core"},
        {"name": "Luka Modrić", "pos": "MF", "age": 40, "value": 10, "club": "Real Madrid", "status": "Legend"},
        {"name": "Marcelo Brozović", "pos": "MF", "age": 33, "value": 15, "club": "Al-Nassr", "status": "Engine"},
        {"name": "Mateo Kovačić", "pos": "MF", "age": 31, "value": 45, "club": "Man City", "status": "Core"},
        {"name": "Lovro Majer", "pos": "MF", "age": 28, "value": 35, "club": "Wolfsburg", "status": "Creative"},
        {"name": "Ivan Perišić", "pos": "FW", "age": 37, "value": 5, "club": "PSV", "status": "Veteran"},
        {"name": "Andrej Kramarić", "pos": "FW", "age": 34, "value": 10, "club": "Hoffenheim", "status": "Veteran"},
        {"name": "Bruno Petković", "pos": "FW", "age": 31, "value": 15, "club": "Dinamo Zagreb", "status": "Active"},
    ]
}

GENERIC_SURNAMES = {
    "Latin": ["García", "Rodríguez", "Martínez", "Hernández", "López", "González", "Pérez", "Sánchez"],
    "European": ["Müller", "Schmidt", "Fischer", "Weber", "Meyer", "Wagner", "Becker", "Schulz"],
    "African": ["Mensah", "Traoré", "Diallo", "Keita", "Sow", "Diop", "Touré", "Kamara"],
    "Asian": ["Kim", "Lee", "Park", "Wang", "Zhang", "Li", "Sato", "Tanaka"],
    "Global": ["Smith", "Jones", "Brown", "Taylor", "Wilson", "Johnson", "White", "Harris"]
}

class SquadEngine:
    def __init__(self):
        from src.constants import ALL_WC_TEAMS, CURATED_ELO
        self.teams = ALL_WC_TEAMS
        self.elo = CURATED_ELO
        self.processed_dir = Path("data/processed")
        self.processed_dir.mkdir(parents=True, exist_ok=True)

    def _get_region_names(self, team: str) -> List[str]:
        # Simple heuristic for regional names
        latin_teams = ["Argentina", "Brazil", "Mexico", "Uruguay", "Colombia", "Ecuador", "Paraguay", "Chile", "Peru", "Costa Rica", "Panama"]
        euro_teams  = ["France", "Spain", "Germany", "England", "Italy", "Netherlands", "Belgium", "Portugal", "Croatia", "Switzerland", "Austria", "Serbia", "Turkey", "Czechia", "Scotland", "Bosnia"]
        asia_teams  = ["Japan", "South Korea", "Iran", "Australia", "Saudi Arabia", "Iraq", "Uzbekistan"]
        africa_teams = ["Morocco", "Senegal", "Ivory Coast", "Egypt", "Algeria", "Nigeria", "Tunisia", "Cameroon", "South Africa", "Ghana", "DR Congo"]
        
        if team in latin_teams: return GENERIC_SURNAMES["Latin"]
        if team in euro_teams: return GENERIC_SURNAMES["European"]
        if team in asia_teams: return GENERIC_SURNAMES["Asian"]
        if team in africa_teams: return GENERIC_SURNAMES["African"]
        return GENERIC_SURNAMES["Global"]

    def _calculate_cies_valuation(self, base_val: float, age: int, is_star: bool) -> int:
        """
        Refined CIES-style valuation formula.
        - Peak age (23-27) gets a multiplier.
        - Stars get a status premium.
        - Young talents (under 21) get scarcity premium.
        """
        multiplier = 1.0
        
        # Age Factor
        if 23 <= age <= 27:
            multiplier *= 1.4
        elif age < 21:
            multiplier *= 1.6 # Wonderkid tax
        elif age > 31:
            multiplier *= 0.6 # Aging curve
            
        # Status Factor
        if is_star:
            multiplier *= 1.3
            
        final_val = int(base_val * multiplier * random.uniform(0.9, 1.1))
        return max(2_000_000, final_val)

    def generate_squad(self, team: str) -> List[Dict]:
        """Generate a full squad for March 2026. Minimum 23 players."""
        squad = []
        
        # 1. Start with curated stars
        stars = SQUAD_STARS.get(team, [])
        for p in stars:
            # Use CIES logic even for stars
            refined_val = self._calculate_cies_valuation(p["value"] * 1_000_000, p["age"], True)
            
            squad.append({
                "name": p["name"],
                "position": p["pos"],
                "age": p["age"],
                "market_value_eur": refined_val,
                "club": p["club"],
                "status": p.get("status", "Active"),
                "is_star": True,
                "conflux_influence": round(random.uniform(0.8, 0.98), 2),
                "image_url": AssetPipeline.get_player_image(p["name"], team)
            })
            
        # 2. Fill if squad is small (less than 23)
        if len(squad) < 23:
            remaining = 23 - len(squad)
            region_names = self._get_region_names(team)
            
            # Team quality context
            team_elo = self.elo.get(team, 1600)
            # Base player value for this nation
            nation_base_val = (team_elo - 1400) * 1_200_000 
            
            # Distribute remaining positions
            positions = ["GK"] * 2 + ["DF"] * 7 + ["MF"] * 7 + ["FW"] * 4
            # Slice to fit remaining slots
            positions = positions[:remaining]
            
            for i, pos in enumerate(positions):
                surname = random.choice(region_names)
                first_names = ["L.", "J.", "M.", "A.", "K.", "D.", "S.", "T."]
                name = f"{random.choice(first_names)} {surname}"
                age = random.randint(18, 33)
                
                val = self._calculate_cies_valuation(nation_base_val, age, False)
                
                squad.append({
                    "name": name,
                    "position": pos,
                    "age": age,
                    "market_value_eur": val,
                    "club": f"{team} Pro League",
                    "status": "National Pool",
                    "is_star": False,
                    "conflux_influence": round(random.uniform(0.1, 0.45), 2),
                    "image_url": AssetPipeline.get_player_image(name, team)
                })
            
        return sorted(squad, key=lambda x: x["market_value_eur"], reverse=True)
            
        return sorted(squad, key=lambda x: x["market_value_eur"], reverse=True)

    def build_all_squads(self):
        """Save all squads to a single JSON for the API."""
        print(f"◈ CONFLUX | Generating March 2026 squads for {len(self.teams)} teams...")
        all_data = {}
        for team in self.teams:
            squad = self.generate_squad(team)
            total_val = sum(p["market_value_eur"] for p in squad)
            all_data[team] = {
                "squad": squad,
                "total_valuation": total_val,
                "last_update": "2026-03-24" # March 2026 Break
            }
            
        out_path = self.processed_dir / "squad_data.json"
        with open(out_path, "w") as f:
            json.dump(all_data, f, indent=2)
        print(f"  [squads] ✓ Saved data to {out_path}")
        return all_data

if __name__ == "__main__":
    engine = SquadEngine()
    engine.build_all_squads()
