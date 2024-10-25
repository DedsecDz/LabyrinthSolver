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
pygame.display.set_caption("Le Labyrinthe")
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
font = pygame.font.SysFont(None, 40)

# Charger l'image de fond
background_image = pygame.image.load("BR.jpeg")
background_image = pygame.transform.scale(background_image, (WINDOW_WIDTH, WINDOW_HEIGHT))

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

    def draw(self):
        # Changer la couleur si le bouton est survolé
        if self.is_hovered:
            pygame.draw.rect(screen, self.hover_color, self.rect)
        else:
            pygame.draw.rect(screen, self.color, self.rect)
        
        font = pygame.font.Font(None, 36)
        text_surface = font.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def check_hover(self, mouse_pos):
        # Met à jour l'état survolé en fonction de la position de la souris
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

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

#--------------------------------------- Menu Principal et Sélection d'Algorithme -----------------------------------
def main_menu():
    """
    Affiche le menu principal avec un bouton pour commencer le jeu.
    """
    while True:
        screen.blit(background_image, (0, 0))
        
        # Afficher le titre "Menu Principal"
        font = pygame.font.Font(None, 72)
        title_surface = font.render("Menu Principal", True, WHITE)
        screen.blit(title_surface, ((WINDOW_WIDTH - title_surface.get_width()) // 2, 50))
        
        start_button = Button((WINDOW_WIDTH - 200) // 2, (WINDOW_HEIGHT - 50) // 2, 200, 50, GREY, "Commencer")

        # Vérifier le survol et dessiner le bouton
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()

        start_button.check_hover(mouse_pos)
        start_button.draw()

        pygame.display.update()

        # Gestion des événements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            # Vérification du clic sur le bouton "Commencer"
            if mouse_click[0] and start_button.is_clicked(mouse_pos):
                return  # Quitte la fonction `main_menu` une fois que le bouton est cliqué


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
        mouse_click = pygame.mouse.get_pressed()

        for button in buttons:
            button.check_hover(mouse_pos)
            button.draw()
        
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if mouse_click[0]:
                if dijkstra_button.is_clicked(mouse_pos):
                    chosen_algo = 'dijkstra'
                elif astar_button.is_clicked(mouse_pos):
                    chosen_algo = 'astar'
                elif bfs_button.is_clicked(mouse_pos):
                    chosen_algo = 'bfs'
                elif dfs_button.is_clicked(mouse_pos):
                    chosen_algo = 'dfs'
                elif compare_button.is_clicked(mouse_pos):
                    chosen_algo = 'compare'

    return chosen_algo

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

                for evenement in pygame.event.get():
                    if evenement.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
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
        ('Dijkstra', dijkstra, GREEN),
        ('A*', a_star, ORANGE),
        ('BFS', bfs, BLUE),
        ('DFS', dfs, YELLOW)
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

#--------------------------------------- Choix de la Taille du Labyrinthe -----------------------------------
def size_menu():
    """
    Affiche un menu pour choisir la taille du labyrinthe (Petit, Moyen, Grand).
    """
    while True:
        screen.blit(background_image, (0, 0))

        font = pygame.font.Font(None,50)
        title_surface = font.render("Choix de la taille du labyrinthe", True, WHITE)
        screen.blit(title_surface, ((WINDOW_WIDTH - title_surface.get_width()) // 2, 50))

        S_button = Button((WINDOW_WIDTH - 200) // 2, (WINDOW_HEIGHT - 50) // 2, 200, 50, GREY, "Petit")
        M_button = Button((WINDOW_WIDTH - 200) // 2, (WINDOW_HEIGHT - 50) // 2 + 60, 200, 50, GREY, "Moyen")
        L_button = Button((WINDOW_WIDTH - 200) // 2, (WINDOW_HEIGHT - 50) // 2 + 120, 200, 50, GREY, "Grand")

        mouse_pos = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()

        for size_button in [S_button, L_button, M_button]:
            size_button.check_hover(mouse_pos)
            size_button.draw()

        pygame.display.update()

        # Gestion des events 
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if mouse_click[0]:
                if S_button.is_clicked(mouse_pos):
                    return 20
                elif M_button.is_clicked(mouse_pos):
                    return 30
                elif L_button.is_clicked(mouse_pos):
                    return 40

#--------------------------------------- Fonction Principale -----------------------------------
def main():
    """
    Fonction principale qui gère la logique du jeu.
    """
    global ROWS, COLS, CELL_SIZE, CELL_SIZE_HEIGHT, CELL_SIZE_WIDTH

    main_menu()
    ROWS = COLS = size_menu()
    CELL_SIZE_WIDTH = WIDTH // COLS
    CELL_SIZE_HEIGHT = HEIGHT // ROWS
    CELL_SIZE = min(CELL_SIZE_WIDTH,CELL_SIZE_HEIGHT)
    chosen_algo = algorithm_selection_menu()
    
    # Génération du labyrinthe
    grid = [[Cell(row, col) for col in range(COLS)] for row in range(ROWS)]
    generate_lab(grid)
    start, end = grid[random.randint(0,ROWS-1)][0], grid[random.randint(0,ROWS-1)][COLS - 1]

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
            
            # Initialiser une liste pour stocker le chemin parcouru
            path_points = []

            for cell in path:
                # Calculer les coordonnées de la cellule courante
                x = EXTRA_WIDTH + cell.col * CELL_SIZE + CELL_SIZE // 2
                y = EXTRA_HEIGHT + cell.row * CELL_SIZE + CELL_SIZE // 2
                
                # Ajouter le point actuel à la liste des points du chemin
                path_points.append((x, y))

              
                screen.blit(background_image, (0, 0))
                pygame.draw.rect(screen, BLACK, (EXTRA_WIDTH, EXTRA_HEIGHT, WIDTH, HEIGHT))
                for row in grid_copy:
                    for c in row:
                        c.draw()
                        for evenement in pygame.event.get():
                            if evenement.type == pygame.QUIT:
                                pygame.quit()
                                sys.exit()
                
                # Dessiner les points de départ et de fin
                draw_start_end(start, end)
                
                # serpent
                if len(path_points) > 1:
                    pygame.draw.lines(screen, RED, False, path_points, 3) 

                # Boule à la position actuelle
                pygame.draw.circle(screen, RED, (x, y), CELL_SIZE // 4)
                
                # Mise à jour 
                pygame.display.update()
                pygame.time.delay(50)
            
            # Afficher le temps écoulé et le nom de l'algorithme
            draw_info_panel(algo_name, elapsed_time)

            # Afficher les boutons "Réessayer" et "Quitter"
            retry_button = Button((WINDOW_WIDTH - 200) // 2, WINDOW_HEIGHT - WINDOW_HEIGHT/2, 200, 50, BLUE, 'Réessayer')
            quit_button = Button((WINDOW_WIDTH - 200) // 2, WINDOW_HEIGHT - WINDOW_HEIGHT/2 + 60, 200, 50, RED, 'Quitter')

            

            waiting_for_retry = True
            while waiting_for_retry:

                mouse_pos = pygame.mouse.get_pos()
                for button in [retry_button, quit_button]:
                    button.check_hover(mouse_pos)
                    button.draw()

                pygame.display.update()

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        if retry_button.is_clicked(event.pos):
                            main()
                            return
                        elif quit_button.is_clicked(event.pos):
                            pygame.quit()
                            sys.exit()

        
        else:
            # Aucun chemin trouvé
            font = pygame.font.Font(None, 48)
            text_surface = font.render(f"Aucun chemin trouvé pour {algo_name}", True, RED)
            screen.blit(text_surface, ((WINDOW_WIDTH - text_surface.get_width()) // 2, WINDOW_HEIGHT // 2))
            pygame.display.update()
            pygame.time.delay(3000)
            main()
            return

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

    pygame.quit()

#--------------------------------------- Lancement du Jeu -----------------------------------
if __name__ == "__main__":
    main()
