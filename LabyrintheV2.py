#--------------------------------------- Importations et Constantes -----------------------------------
import pygame
import random
import heapq
from math import sqrt
import sys
import time

# Constantes d'affichage
WIDTH, HEIGHT = 600, 600
EXTRA_WIDTH = 50  # Largeur supplémentaire pour les côtés
EXTRA_HEIGHT = 50  # Hauteur supplémentaire pour le haut et le bas
WINDOW_WIDTH = WIDTH + EXTRA_WIDTH * 2  # Nouvelle largeur totale de la fenêtre
WINDOW_HEIGHT = HEIGHT + EXTRA_HEIGHT * 2  # Nouvelle hauteur totale de la fenêtre

# Couleurs
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (50, 50, 50)
BLUE = (0, 0, 128)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
HOVER_COLOR = BLUE  # Couleur des boutons lorsqu'ils sont survolés

# Initialisation de Pygame
pygame.init()
pygame.mixer.init()
pygame.display.set_caption("Le Labyrinthe")
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
font = pygame.font.SysFont(None, 40)

# Charger l'image de fond
background_image = pygame.image.load("image/BR.jpeg")
background_image = pygame.transform.scale(background_image, (WINDOW_WIDTH, WINDOW_HEIGHT))

# Charger les fichiers audio
sound_Click_start = pygame.mixer.Sound("Son/StartButton.wav")
sound_click = pygame.mixer.Sound("Son/ClickButton.wav")
sound_hover = pygame.mixer.Sound("Son/HoverButton.wav")
sound_start = pygame.mixer.Sound("Son/Lancement.mp3")
pygame.mixer.music.load("Son/BackSound.mp3")
StartSound1 = True
StartSound2 = True

# Réglage du volume des effets sonores (0.0 pour muet, 1.0 pour volume maximal)
sound_Click_start.set_volume(0.7)  # Volume à 70% pour le clic sur le bouton "Commencer"
sound_click.set_volume(0.7)        # Volume à 70% pour le clic des autres boutons
sound_hover.set_volume(0.5)        # Volume à 50% pour le son de survol
sound_start.set_volume(0.3)        # Volume à 30% pour le son de démarrage
pygame.mixer.music.set_volume(0.4)

#--------------------------------------- Classe ButtonHandler avec anti-rebonds -----------------------------------
class ButtonHandler:
    """
    Gestionnaire de clics de bouton avec anti-rebonds.
    """
    def __init__(self, debounce_time=0.2):
        # Temps de déparasitage en secondes pour éviter les rebonds
        self.debounce_time = debounce_time
        # Dictionnaire pour stocker le dernier clic enregistré pour chaque bouton
        self.last_click_time = {}
        # États des boutons de la souris
        self.mouse_state = {"left": False, "middle": False, "right": False}

    def is_clicked(self, button_rect, button_number=1):
        """
        Vérifie si un bouton a été cliqué sans rebond et retourne True si un clic valide est détecté.
        :param button_rect: pygame.Rect représentant la zone du bouton
        :param button_number: 1 pour gauche, 2 pour milieu, 3 pour droit
        :return: True si un clic valide est détecté, False sinon
        """
        mouse_pos = pygame.mouse.get_pos()
        mouse_buttons = pygame.mouse.get_pressed()

        # Nom du bouton selon son numéro
        button_name = {1: "left", 2: "middle", 3: "right"}.get(button_number, "left")

        # Si la souris est enfoncée dans la zone du bouton
        if mouse_buttons[button_number - 1] and button_rect.collidepoint(mouse_pos):
            # Temps actuel
            current_time = time.time()

            # Vérifier si le clic est "valide" selon le temps de debounce
            if (button_name not in self.last_click_time or
                current_time - self.last_click_time[button_name] > self.debounce_time):
                
                # Enregistrer l'heure du dernier clic pour ce bouton
                self.last_click_time[button_name] = current_time

                # Mettre à jour l'état du bouton
                self.mouse_state[button_name] = True
                return True
        else:
            # Mettre à jour l'état du bouton quand il n'est pas enfoncé
            self.mouse_state[button_name] = False
        
        return False

button_handler = ButtonHandler()  # Création de l'instance pour gérer les clics avec anti-rebonds

def evntQ():
    for evenement in pygame.event.get():
            if evenement.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
#--------------------------------------- Classes -----------------------------------
class Cell:
    """
    Représente une cellule dans le labyrinthe avec ses propriétés
    de murs et d'état de visite.
    """
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.visited = False
        self.walls = {'top': True, 'right': True, 'bottom': True, 'left': True}
        self.distance = float('inf')
        self.previous = None
        self.f_cost = 0

    def draw(self, color=WHITE):
        x = EXTRA_WIDTH + self.col * CELL_SIZE
        y = EXTRA_HEIGHT + self.row * CELL_SIZE
        if self.walls['top']:
            pygame.draw.line(screen, color, (x, y), (x + CELL_SIZE, y), 2)
        if self.walls['right']:
            pygame.draw.line(screen, color, (x + CELL_SIZE, y), (x + CELL_SIZE, y + CELL_SIZE), 2)
        if self.walls['bottom']:
            pygame.draw.line(screen, color, (x, y + CELL_SIZE), (x + CELL_SIZE, y + CELL_SIZE), 2)
        if self.walls['left']:
            pygame.draw.line(screen, color, (x, y), (x, y + CELL_SIZE), 2)

    def __lt__(self, other):
        return self.distance < other.distance


class Button:
    """
    Représente un bouton cliquable avec changement de couleur au survol.
    """
    def __init__(self, x, y, width, height, color, text, hover_color=HOVER_COLOR):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = GREY
        self.hover_color = hover_color
        self.text = text
        self.is_hovered = False
        self.hovered_last_frame = False

    def draw(self):
        # Vérifie si le bouton est survolé pour jouer le son une seule fois
        if self.is_hovered and not self.hovered_last_frame:
            sound_hover.play()

        # Changer la couleur si le bouton est survolé
        if self.is_hovered:
            pygame.draw.rect(screen, self.hover_color, self.rect)
        else:
            pygame.draw.rect(screen, self.color, self.rect)

        # Mettre à jour l'état de survol
        self.hovered_last_frame = self.is_hovered

        # Afficher le texte du bouton
        font = pygame.font.Font(None, 36)
        text_surface = font.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def check_hover(self, mouse_pos):
        # Met à jour l'état survolé en fonction de la position de la souris
        self.is_hovered = self.rect.collidepoint(mouse_pos)

#--------------------------------------- Génération du Labyrinthe -----------------------------------
def generate_lab(grid):
    """
    Génère un labyrinthe en utilisant un algorithme de backtracking avec une pile.
    """
    stack = []
    current = grid[0][0]
    current.visited = True

    while True:
        next_cell = get_next_unvisited_neighbor(grid, current)
        if next_cell:
            stack.append(current)
            remove_walls(current, next_cell)
            next_cell.visited = True
            current = next_cell
        elif stack:
            current = stack.pop()
        else:
            break

def get_next_unvisited_neighbor(grid, current):
    """
    Récupère un voisin non visité au hasard autour de la cellule actuelle.
    """
    neighbors = []
    row, col = current.row, current.col
    if row > 0 and not grid[row - 1][col].visited:
        neighbors.append(grid[row - 1][col])
    if row < ROWS - 1 and not grid[row + 1][col].visited:
        neighbors.append(grid[row + 1][col])
    if col > 0 and not grid[row][col - 1].visited:
        neighbors.append(grid[row][col - 1])
    if col < COLS - 1 and not grid[row][col + 1].visited:
        neighbors.append(grid[row][col + 1])

    return random.choice(neighbors) if neighbors else None

def remove_walls(current, next_cell):
    """
    Enlève les murs entre deux cellules adjacentes.
    """
    dx = current.col - next_cell.col
    dy = current.row - next_cell.row

    if dx == 1:
        current.walls['left'] = False
        next_cell.walls['right'] = False
    elif dx == -1:
        current.walls['right'] = False
        next_cell.walls['left'] = False
    elif dy == 1:
        current.walls['top'] = False
        next_cell.walls['bottom'] = False
    elif dy == -1:
        current.walls['bottom'] = False
        next_cell.walls['top'] = False

def reset_grid(grid):
    """
    Réinitialise le labyrinthe pour une nouvelle recherche.
    """
    for row in grid:
        for cell in row:
            cell.visited = False
            cell.distance = float('inf')
            cell.previous = None

#--------------------------------------- Dessin du Labyrinthe et des Objets -----------------------------------
def draw_ball(cell, color=RED):
    """
    Dessine une balle rouge pour représenter la position actuelle dans le labyrinthe.
    """
    x = EXTRA_WIDTH + cell.col * CELL_SIZE + CELL_SIZE // 2
    y = EXTRA_HEIGHT + cell.row * CELL_SIZE + CELL_SIZE // 2
    pygame.draw.circle(screen, color, (x, y), CELL_SIZE // 4)

def draw_start_end(start, end):
    """
    Dessine les points de départ et de fin.
    """
    start_x = EXTRA_WIDTH + start.col * CELL_SIZE + CELL_SIZE // 2 
    start_y = EXTRA_HEIGHT + start.row * CELL_SIZE + CELL_SIZE // 2 + 20
    end_x = EXTRA_WIDTH + end.col * CELL_SIZE + CELL_SIZE // 2
    end_y = EXTRA_HEIGHT + end.row * CELL_SIZE + CELL_SIZE // 2 + 20

    pygame.draw.polygon(screen, BLUE, [(start_x, start_y - 20), (start_x - 10, start_y - 30), (start_x + 10, start_y - 30)])
    pygame.draw.polygon(screen, YELLOW, [(end_x, end_y - 20), (end_x - 10, end_y - 30), (end_x + 10, end_y - 30)])

#--------------------------------------- Algorithmes de Recherche -----------------------------------
def copy_grid(grid):
    """
    Crée une copie du labyrinthe pour chaque algorithme.
    """
    grid_copy = [[Cell(cell.row, cell.col) for cell in row] for row in grid]
    for r in range(ROWS):
        for c in range(COLS):
            grid_copy[r][c].walls = grid[r][c].walls.copy()  # Copier aussi les murs
    return grid_copy

def dijkstra(grid, start, end):
    """
    Algorithme de Dijkstra pour trouver le chemin le plus court.
    """
    start.distance = 0
    queue = []
    heapq.heappush(queue, (start.distance, start))

    while queue:
        _, current = heapq.heappop(queue)

        if current == end:
            return True

        for neighbor in get_neighbors(grid, current):
            temp_distance = current.distance + 1
            if temp_distance < neighbor.distance:
                neighbor.distance = temp_distance
                neighbor.previous = current
                heapq.heappush(queue, (neighbor.distance, neighbor))

    return False

def a_star(grid, start, end):
    """
    Algorithme A* pour trouver le chemin le plus court.
    """
    open_set = []
    heapq.heappush(open_set, (0, start))
    start.distance = 0

    while open_set:
        _, current = heapq.heappop(open_set)

        if current == end:
            return True

        for neighbor in get_neighbors(grid, current):
            tentative_g_score = current.distance + 1
            if tentative_g_score < neighbor.distance:
                neighbor.distance = tentative_g_score
                neighbor.f_cost = tentative_g_score + heuristic(neighbor, end)
                neighbor.previous = current
                heapq.heappush(open_set, (neighbor.f_cost, neighbor))

    return False

def bfs(grid, start, end):
    """
    Algorithme BFS (Breadth-First Search) pour trouver le chemin le plus court.
    """
    queue = [start]
    start.distance = 0
    start.visited = True

    while queue:
        current = queue.pop(0)

        if current == end:
            return True

        for neighbor in get_neighbors(grid, current):
            if not neighbor.visited:
                neighbor.visited = True
                neighbor.distance = current.distance + 1
                neighbor.previous = current
                queue.append(neighbor)

    return False

def dfs(grid, start, end):
    """
    Algorithme DFS (Depth-First Search) pour explorer le labyrinthe.
    """
    stack = [start]
    start.visited = True

    while stack:
        current = stack.pop()

        if current == end:
            return True

        for neighbor in get_neighbors(grid, current):
            if not neighbor.visited:
                neighbor.visited = True
                neighbor.previous = current
                stack.append(neighbor)

    return False

def get_neighbors(grid, cell):
    """
    Récupère les voisins accessibles d'une cellule.
    """
    neighbors = []
    row, col = cell.row, cell.col
    if row > 0 and not cell.walls['top']:
        neighbors.append(grid[row - 1][col])
    if row < ROWS - 1 and not cell.walls['bottom']:
        neighbors.append(grid[row + 1][col])
    if col > 0 and not cell.walls['left']:
        neighbors.append(grid[row][col - 1])
    if col < COLS - 1 and not cell.walls['right']:
        neighbors.append(grid[row][col + 1])
    return neighbors

def heuristic(cell, end):
    """
    Heuristique pour l'algorithme A* (distance euclidienne).
    """
    return sqrt((cell.row - end.row) ** 2 + (cell.col - end.col) ** 2)

def reconstruct_p(end):
    """
    Reconstruit le chemin trouvé à partir de la cellule de fin.
    """
    path = []
    current = end
    while current.previous:
        path.append(current)
        current = current.previous
    path.reverse()
    return path

#--------------------------------------- Comparaison des Algorithmes -----------------------------------
def display_comparison_animation(grid, start, end, results):
    """
    Affiche une animation de comparaison visuelle des algorithmes avec un effet "serpent".
    """
    max_path_length = max(len(res[3]) for res in results)

    path_points = {algo_name: [] for algo_name, _, _, _ in results}

    for step in range(max_path_length):
        screen.blit(background_image, (0, 0))
        pygame.draw.rect(screen, BLACK, (EXTRA_WIDTH, EXTRA_HEIGHT, WIDTH, HEIGHT))

        for row in grid:
            for cell in row:
                cell.draw()

        draw_start_end(start, end)

        for algo_name, elapsed_time, color, path in results:
            if step < len(path):
                cell = path[step]
                x = EXTRA_WIDTH + cell.col * CELL_SIZE + CELL_SIZE // 2
                y = EXTRA_HEIGHT + cell.row * CELL_SIZE + CELL_SIZE // 2

                path_points[algo_name].append((x, y))

                if len(path_points[algo_name]) > 1:
                    pygame.draw.lines(screen, RED, False, path_points[algo_name], 3)  # Tracer la ligne

                pygame.draw.circle(screen, RED, (x, y), CELL_SIZE // 4)

                evntQ();
        # Mise à jour
        pygame.display.update()
        pygame.time.delay(50)

def display_comparison_results(results):
    """
    Affiche les résultats de la comparaison des algorithmes.
    """
    # Trier les résultats du plus rapide au plus lent
    sorted_results = sorted(results, key=lambda x: x[1])

    # Afficher les résultats
    screen.blit(background_image, (0, 0))
    font = pygame.font.Font(None, 36)
    y_offset = 100

    title_surface = font.render("Résultats de la comparaison :", True, WHITE)
    screen.blit(title_surface, (50, y_offset))
    y_offset += 50

    for rank, (algo_name, elapsed_time, color, _) in enumerate(sorted_results):
        result_text = f"{rank + 1}. {algo_name} - Temps : {elapsed_time*(10**6):.2f} us"
        text_surface = font.render(result_text, True, color)
        screen.blit(text_surface, (50, y_offset))
        y_offset += 50

    pygame.display.update()

def compare_algorithms_animation(grid, start, end):
    """
    Lance la comparaison des différents algorithmes et renvoie les résultats.
    """
    algorithms = [
        ('Dijkstra', dijkstra, BLACK),
        ('A*', a_star, BLACK),
        ('BFS', bfs, BLACK),
        ('DFS', dfs, BLACK)
    ]

    results = []
    for algo_name, algo_func, color in algorithms:
        grid_copy = copy_grid(grid)
        reset_grid(grid_copy)

        start_time = time.time()
        found = algo_func(grid_copy, grid_copy[start.row][start.col], grid_copy[end.row][end.col])
        elapsed_time = time.time() - start_time

        if found:
            path = reconstruct_p(grid_copy[end.row][end.col])
            results.append((algo_name, elapsed_time, color, path))
        else:
            results.append((algo_name, float('inf'), color, []))

    return results

def draw_info_panel(algo_name, elapsed_time):
    """
    Affiche un panneau d'informations en bas de l'écran.
    """
    panel_rect = pygame.Rect(0, WINDOW_HEIGHT - 50, WINDOW_WIDTH, 50)
    pygame.draw.rect(screen, BLACK, panel_rect)

    # Afficher le texte
    font = pygame.font.Font(None, 36)
    info_text = f"Algorithme : {algo_name} | Temps : {elapsed_time*(10**6):.2f} us"
    text_surface = font.render(info_text, True, WHITE)
    screen.blit(text_surface, (20, WINDOW_HEIGHT - 40))

#--------------------------------------- Menu Principal et Sélection d'Algorithme -----------------------------------
def main_menu():
    """
    Affiche le menu principal avec un bouton pour commencer le jeu.
    """
    global StartSound1
    if StartSound1:
        sound_start.play()
        StartSound1 = False

    start_button = Button((WINDOW_WIDTH - 200) // 2, (WINDOW_HEIGHT - 50) // 2, 200, 50, GREY, "START")

    while True:
        screen.blit(background_image, (0, 0))

        # Afficher le titre "Menu Principal"
        font = pygame.font.Font(None, 72)
        title_surface = font.render("Menu Principal", True, WHITE)
        screen.blit(title_surface, ((WINDOW_WIDTH - title_surface.get_width()) // 2, 50))

        # Vérifier le survol et dessiner le bouton
        mouse_pos = pygame.mouse.get_pos()
        start_button.check_hover(mouse_pos)
        start_button.draw()
        pygame.display.update()

        # Gestion des événements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Vérification du clic sur le bouton "Commencer" avec anti-rebonds
            if button_handler.is_clicked(start_button.rect):
                sound_Click_start.play()
                return

def size_menu():
    """
    Affiche un menu pour choisir la taille du labyrinthe (Petit, Moyen, Grand).
    """
    S_button = Button((WINDOW_WIDTH - 200) // 2, (WINDOW_HEIGHT - 50) // 2, 200, 50, GREY, "Petit")
    M_button = Button((WINDOW_WIDTH - 200) // 2, (WINDOW_HEIGHT - 50) // 2 + 60, 200, 50, GREY, "Moyen")
    L_button = Button((WINDOW_WIDTH - 200) // 2, (WINDOW_HEIGHT - 50) // 2 + 120, 200, 50, GREY, "Grand")

    while True:
        screen.blit(background_image, (0, 0))

        font = pygame.font.Font(None, 50)
        title_surface = font.render("Choix de la taille du labyrinthe", True, WHITE)
        screen.blit(title_surface, ((WINDOW_WIDTH - title_surface.get_width()) // 2, 50))

        # Vérifier le survol et dessiner les boutons
        mouse_pos = pygame.mouse.get_pos()
        for size_button in [S_button, M_button, L_button]:
            size_button.check_hover(mouse_pos)
            size_button.draw()

        pygame.display.update()

        # Gestion des événements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if button_handler.is_clicked(S_button.rect):
                sound_click.play()
                return 20
            elif button_handler.is_clicked(M_button.rect):
                sound_click.play()
                return 30
            elif button_handler.is_clicked(L_button.rect):
                sound_click.play()
                return 40

def algorithm_selection_menu():
    """
    Affiche le menu pour sélectionner l'algorithme de recherche.
    """
    screen.blit(background_image, (0, 0))

    # Afficher le titre "Choisissez un mode"
    font = pygame.font.Font(None, 60)
    title_surface = font.render("Choisissez un mode", True, WHITE)
    screen.blit(title_surface, ((WINDOW_WIDTH - title_surface.get_width()) // 2, 50))

    # Boutons pour les algorithmes
    dijkstra_button = Button((WINDOW_WIDTH - 200) // 2, 150, 200, 50, GREEN, 'Dijkstra')
    astar_button = Button((WINDOW_WIDTH - 200) // 2, 220, 200, 50, RED, 'A*')
    bfs_button = Button((WINDOW_WIDTH - 200) // 2, 290, 200, 50, BLUE, 'BFS')
    dfs_button = Button((WINDOW_WIDTH - 200) // 2, 360, 200, 50, YELLOW, 'DFS')
    compare_button = Button((WINDOW_WIDTH - 200) // 2, 430, 200, 50, ORANGE, 'Comparer')

    buttons = [dijkstra_button, astar_button, bfs_button, dfs_button, compare_button]
    for button in buttons:
        button.draw()

    pygame.display.update()

    chosen_algo = None
    while not chosen_algo:
        mouse_pos = pygame.mouse.get_pos()
        for button in buttons:
            button.check_hover(mouse_pos)
            button.draw()

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if button_handler.is_clicked(dijkstra_button.rect):
                sound_click.play()
                chosen_algo = 'dijkstra'
            elif button_handler.is_clicked(astar_button.rect):
                sound_click.play()
                chosen_algo = 'astar'
            elif button_handler.is_clicked(bfs_button.rect):
                sound_click.play()
                chosen_algo = 'bfs'
            elif button_handler.is_clicked(dfs_button.rect):
                sound_click.play()
                chosen_algo = 'dfs'
            elif button_handler.is_clicked(compare_button.rect):
                sound_click.play()
                chosen_algo = 'compare'

    return chosen_algo

def display_solution(grid, start, end, path, algo_name, elapsed_time):
    """
    Affiche la solution trouvée par l'algorithme.
    """
    path_points = []

    for cell in path:

        x = EXTRA_WIDTH + cell.col * CELL_SIZE + CELL_SIZE // 2
        y = EXTRA_HEIGHT + cell.row * CELL_SIZE + CELL_SIZE // 2
        path_points.append((x, y))

        screen.blit(background_image, (0, 0))
        pygame.draw.rect(screen, BLACK, (EXTRA_WIDTH, EXTRA_HEIGHT, WIDTH, HEIGHT))
        for row in grid:
            for c in row:
                c.draw()
                

        draw_start_end(start, end)

        if len(path_points) > 1:
            pygame.draw.lines(screen, RED, False, path_points, 3)

        pygame.draw.circle(screen, RED, (x, y), CELL_SIZE // 4)

        pygame.display.update()
        pygame.time.delay(50)
        evntQ();

    draw_info_panel(algo_name, elapsed_time)

    retry_button = Button((WINDOW_WIDTH - 200) // 2, WINDOW_HEIGHT - WINDOW_HEIGHT / 2, 200, 50, BLUE, 'Réessayer')
    quit_button = Button((WINDOW_WIDTH - 200) // 2, WINDOW_HEIGHT - WINDOW_HEIGHT / 2 + 60, 200, 50, RED, 'Quitter')

    handle_retry_or_quit(retry_button, quit_button)

def handle_retry_or_quit(retry_button, quit_button):
    """
    Gère les boutons "Réessayer" et "Quitter".
    """
    while True:
        mouse_pos = pygame.mouse.get_pos()
        for button in [retry_button, quit_button]:
            button.check_hover(mouse_pos)
            button.draw()

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif button_handler.is_clicked(retry_button.rect):
                main()
                return
            elif button_handler.is_clicked(quit_button.rect):
                pygame.quit()
                sys.exit()

def display_no_solution(algo_name):
    """
    Affiche un message si aucun chemin n'a été trouvé.
    """
    font = pygame.font.Font(None, 48)
    text_surface = font.render(f"Aucun chemin trouvé pour {algo_name}", True, RED)
    screen.blit(text_surface, ((WINDOW_WIDTH - text_surface.get_width()) // 2, WINDOW_HEIGHT // 2))
    pygame.display.update()
    pygame.time.delay(3000)
    main()

#--------------------------------------- Fonction Principale -----------------------------------
def main():
    """
    Fonction principale qui gère la logique du jeu.
    """
    global ROWS, COLS, CELL_SIZE, CELL_SIZE_HEIGHT, CELL_SIZE_WIDTH, StartSound2

    main_menu()

    if StartSound2:
        sound_start.stop()
        pygame.mixer.music.play(-1)
        StartSound2 = False

    ROWS = COLS = size_menu()
    CELL_SIZE_WIDTH = WIDTH // COLS
    CELL_SIZE_HEIGHT = HEIGHT // ROWS
    CELL_SIZE = min(CELL_SIZE_WIDTH, CELL_SIZE_HEIGHT)

    chosen_algo = algorithm_selection_menu()

    # Génération du labyrinthe
    grid = [[Cell(row, col) for col in range(COLS)] for row in range(ROWS)]
    generate_lab(grid)
    start, end = grid[random.randint(0, ROWS - 1)][0], grid[random.randint(0, ROWS - 1)][COLS - 1]

    if chosen_algo == 'compare':
        grid = [[Cell(row, col) for col in range(COLS)] for row in range(ROWS)]
        generate_lab(grid)
        results = compare_algorithms_animation(grid, start, end)
        display_comparison_animation(grid, start, end, results)
        display_comparison_results(results)
        pygame.time.delay(5000)
        main()
        return

    elif chosen_algo in ['dijkstra', 'astar', 'bfs', 'dfs']:
        grid = [[Cell(row, col) for col in range(COLS)] for row in range(ROWS)]
        generate_lab(grid)
        grid_copy = copy_grid(grid)
        reset_grid(grid_copy)

        start_time = time.time()

        if chosen_algo == 'dijkstra':
            found = dijkstra(grid_copy, grid_copy[start.row][start.col], grid_copy[end.row][end.col])
            algo_name = 'Dijkstra'
        elif chosen_algo == 'astar':
            found = a_star(grid_copy, grid_copy[start.row][start.col], grid_copy[end.row][end.col])
            algo_name = 'A*'
        elif chosen_algo == 'bfs':
            found = bfs(grid_copy, grid_copy[start.row][start.col], grid_copy[end.row][end.col])
            algo_name = 'BFS'
        elif chosen_algo == 'dfs':
            found = dfs(grid_copy, grid_copy[start.row][start.col], grid_copy[end.row][end.col])
            algo_name = 'DFS'

        elapsed_time = time.time() - start_time

        if found:
            path = reconstruct_p(grid_copy[end.row][end.col])
            display_solution(grid, start, end, path, algo_name, elapsed_time)
        else:
            display_no_solution(algo_name)
        pygame.display.update()

#--------------------------------------- Lancement du Jeu -----------------------------------
if __name__ == "__main__":
    main()
