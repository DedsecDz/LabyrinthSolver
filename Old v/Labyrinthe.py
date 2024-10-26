#---------------------------------------- Bibliothèques et paramètres ----------------------------------------
import pygame
import random
import heapq
from math import sqrt
import sys
import time

# Dimensions de l'affichage
LARGEUR, HAUTEUR = 600, 600
MARGE_X = 50  # Ajout d'une marge horizontale
MARGE_Y = 50  # Ajout d'une marge verticale
FENETRE_LARGEUR = LARGEUR + MARGE_X * 2  # Largeur totale de la fenêtre
FENETRE_HAUTEUR = HAUTEUR + MARGE_Y * 2  # Hauteur totale de la fenêtre

# Définitions des couleurs
BLANC = (255, 255, 255)
NOIR = (0, 0, 0)
GRIS = (50, 50, 50)
BLEU_FONCE = (0, 0, 128)
VERT = (0, 255, 0)
ROUGE = (255, 0, 0)
JAUNE = (255, 255, 0)
ORANGE = (255, 165, 0)
COULEUR_SURVOL = BLEU_FONCE  # Couleur des boutons quand la souris passe dessus

# Initialisation de Pygame
pygame.init()
pygame.display.set_caption("Jeu de Labyrinthe")
fenetre = pygame.display.set_mode((FENETRE_LARGEUR, FENETRE_HAUTEUR))
police = pygame.font.SysFont(None, 40)

# Chargement d'une image d'arrière-plan
image_fond = pygame.image.load("BR.jpeg")
image_fond = pygame.transform.scale(image_fond, (FENETRE_LARGEUR, FENETRE_HAUTEUR))

#---------------------------------------- Classes de Base ----------------------------------------
class Case:
    """
    Une case individuelle dans le labyrinthe, avec ses attributs pour les murs et son état.
    """
    def __init__(self, ligne, colonne):
        self.ligne = ligne
        self.colonne = colonne
        self.visitee = False
        self.murs = {'haut': True, 'droite': True, 'bas': True, 'gauche': True}
        self.distance = float('inf')
        self.precedente = None
        self.cout_estime = 0

    def dessiner(self, couleur=BLANC):
        x = MARGE_X + self.colonne * TAILLE_CASE
        y = MARGE_Y + self.ligne * TAILLE_CASE
        if self.murs['haut']:
            pygame.draw.line(fenetre, couleur, (x, y), (x + TAILLE_CASE, y), 2)
        if self.murs['droite']:
            pygame.draw.line(fenetre, couleur, (x + TAILLE_CASE, y), (x + TAILLE_CASE, y + TAILLE_CASE), 2)
        if self.murs['bas']:
            pygame.draw.line(fenetre, couleur, (x, y + TAILLE_CASE), (x + TAILLE_CASE, y + TAILLE_CASE), 2)
        if self.murs['gauche']:
            pygame.draw.line(fenetre, couleur, (x, y), (x, y + TAILLE_CASE), 2)

    def __lt__(self, autre):
        return self.distance < autre.distance


class Bouton:
    """
    Classe pour un bouton interactif avec des modifications de couleur au survol.
    """
    def __init__(self, x, y, largeur, hauteur, couleur, texte, couleur_survol=COULEUR_SURVOL):
        self.rect = pygame.Rect(x, y, largeur, hauteur)
        self.couleur_base = GRIS
        self.couleur_survol = couleur_survol
        self.texte = texte
        self.est_survole = False

    def dessiner(self):
        # Affiche le bouton avec une couleur différente si survolé
        couleur_actuelle = self.couleur_survol if self.est_survole else self.couleur_base
        pygame.draw.rect(fenetre, couleur_actuelle, self.rect)
        
        font = pygame.font.Font(None, 36)
        texte_surface = font.render(self.texte, True, BLANC)
        texte_rect = texte_surface.get_rect(center=self.rect.center)
        fenetre.blit(texte_surface, texte_rect)

    def verifier_survol(self, position_souris):
        # Met à jour l'état de survol du bouton
        self.est_survole = self.rect.collidepoint(position_souris)

    def est_clique(self, position):
        return self.rect.collidepoint(position)

#---------------------------------------- Génération du Labyrinthe ----------------------------------------
def creer_labyrinthe(grille):
    """
    Crée le labyrinthe avec un algorithme de backtracking en utilisant une pile.
    """
    pile = []
    courant = grille[0][0]
    courant.visitee = True

    while True:
        voisin = voisin_non_visite(grille, courant)
        if voisin:
            pile.append(courant)
            supprimer_murs(courant, voisin)
            voisin.visitee = True
            courant = voisin
        elif pile:
            courant = pile.pop()
        else:
            break


def voisin_non_visite(grille, case):
    """
    Sélectionne un voisin non visité au hasard autour de la case actuelle.
    """
    voisins = []
    ligne, colonne = case.ligne, case.colonne
    if ligne > 0 and not grille[ligne - 1][colonne].visitee:
        voisins.append(grille[ligne - 1][colonne])
    if ligne < NB_LIGNES - 1 and not grille[ligne + 1][colonne].visitee:
        voisins.append(grille[ligne + 1][colonne])
    if colonne > 0 and not grille[ligne][colonne - 1].visitee:
        voisins.append(grille[ligne][colonne - 1])
    if colonne < NB_COLONNES - 1 and not grille[ligne][colonne + 1].visitee:
        voisins.append(grille[ligne][colonne + 1])

    return random.choice(voisins) if voisins else None


def supprimer_murs(case_actuelle, prochaine_case):
    """
    Enlève les murs entre deux cases adjacentes pour créer un chemin.
    """
    dx = case_actuelle.colonne - prochaine_case.colonne
    dy = case_actuelle.ligne - prochaine_case.ligne

    if dx == 1:
        case_actuelle.murs['gauche'] = False
        prochaine_case.murs['droite'] = False
    elif dx == -1:
        case_actuelle.murs['droite'] = False
        prochaine_case.murs['gauche'] = False
    elif dy == 1:
        case_actuelle.murs['haut'] = False
        prochaine_case.murs['bas'] = False
    elif dy == -1:
        case_actuelle.murs['bas'] = False
        prochaine_case.murs['haut'] = False

#---------------------------------------- Dessin et Réinitialisation du Labyrinthe ----------------------------------------
def reinitialiser_grille(grille):
    """
    Réinitialise toutes les cases du labyrinthe pour une nouvelle exploration.
    """
    for ligne in grille:
        for case in ligne:
            case.visitee = False
            case.distance = float('inf')
            case.precedente = None


def dessiner_balle(case, couleur=ROUGE):
    """
    Affiche une balle (point) rouge à la position actuelle dans le labyrinthe.
    """
    x = MARGE_X + case.colonne * TAILLE_CASE + TAILLE_CASE // 2
    y = MARGE_Y + case.ligne * TAILLE_CASE + TAILLE_CASE // 2
    pygame.draw.circle(fenetre, couleur, (x, y), TAILLE_CASE // 4)


def dessiner_depart_arrivee(depart, arrivee):
    """
    Dessine les marqueurs de départ et d'arrivée du labyrinthe.
    """
    depart_x = MARGE_X + depart.colonne * TAILLE_CASE + TAILLE_CASE // 2
    depart_y = MARGE_Y + depart.ligne * TAILLE_CASE + TAILLE_CASE // 2 + 20
    arrivee_x = MARGE_X + arrivee.colonne * TAILLE_CASE + TAILLE_CASE // 2
    arrivee_y = MARGE_Y + arrivee.ligne * TAILLE_CASE + TAILLE_CASE // 2 + 20

    # Dessine des triangles pour marquer les points de départ et d'arrivée
    pygame.draw.polygon(fenetre, BLEU_FONCE, [(depart_x, depart_y - 20), (depart_x - 10, depart_y - 30), (depart_x + 10, depart_y - 30)])
    pygame.draw.polygon(fenetre, JAUNE, [(arrivee_x, arrivee_y - 20), (arrivee_x - 10, arrivee_y - 30), (arrivee_x + 10, arrivee_y - 30)])

#---------------------------------------- Sélection et Menu des Algorithmes ----------------------------------------
def menu_principal():
    """
    Affiche le menu principal avec une option pour lancer le jeu.
    """
    while True:
        fenetre.blit(image_fond, (0, 0))

        # Affiche le titre du menu
        police_grande = pygame.font.Font(None, 72)
        texte_titre = police_grande.render("Menu Principal", True, BLANC)
        fenetre.blit(texte_titre, ((FENETRE_LARGEUR - texte_titre.get_width()) // 2, 50))
        
        bouton_commencer = Bouton((FENETRE_LARGEUR - 200) // 2, (FENETRE_HAUTEUR - 50) // 2, 200, 50, GRIS, "Commencer")

        # Gestion du survol et affichage du bouton
        pos_souris = pygame.mouse.get_pos()
        clic_souris = pygame.mouse.get_pressed()

        bouton_commencer.verifier_survol(pos_souris)
        bouton_commencer.dessiner()

        pygame.display.update()

        # Événements utilisateur
        for evenement in pygame.event.get():
            if evenement.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            # Vérifie si le bouton "Commencer" est cliqué
            if clic_souris[0] and bouton_commencer.est_clique(pos_souris):
                return  # Quitte la fonction pour passer au jeu


def menu_selection_algo():
    """
    Affiche le menu de sélection de l'algorithme à utiliser.
    """
    fenetre.blit(image_fond, (0, 0))
    
    # Titre du menu de sélection
    police_moyenne = pygame.font.Font(None, 60)
    texte_titre = police_moyenne.render("Choisissez un algorithme", True, BLANC)
    fenetre.blit(texte_titre, ((FENETRE_LARGEUR - texte_titre.get_width()) // 2, 50))
    
    # Boutons pour les différents algorithmes
    bouton_dijkstra = Bouton((FENETRE_LARGEUR - 200) // 2, 150, 200, 50, VERT, 'Dijkstra')
    bouton_astar = Bouton((FENETRE_LARGEUR - 200) // 2, 220, 200, 50, ROUGE, 'A*')
    bouton_bfs = Bouton((FENETRE_LARGEUR - 200) // 2, 290, 200, 50, BLEU_FONCE, 'BFS')
    bouton_dfs = Bouton((FENETRE_LARGEUR - 200) // 2, 360, 200, 50, JAUNE, 'DFS')
    bouton_comparer = Bouton((FENETRE_LARGEUR - 200) // 2, 430, 200, 50, ORANGE, 'Comparer')

    boutons = [bouton_dijkstra, bouton_astar, bouton_bfs, bouton_dfs, bouton_comparer]
    for bouton in boutons:
        bouton.dessiner()

    pygame.display.update()

    algo_choisi = None
    while not algo_choisi:
        pos_souris = pygame.mouse.get_pos()
        clic_souris = pygame.mouse.get_pressed()

        # Vérifie le survol et redessine les boutons
        for bouton in boutons:
            bouton.verifier_survol(pos_souris)
            bouton.dessiner()
        
        pygame.display.update()

        for evenement in pygame.event.get():
            if evenement.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if clic_souris[0]:
                if bouton_dijkstra.est_clique(pos_souris):
                    algo_choisi = 'dijkstra'
                elif bouton_astar.est_clique(pos_souris):
                    algo_choisi = 'astar'
                elif bouton_bfs.est_clique(pos_souris):
                    algo_choisi = 'bfs'
                elif bouton_dfs.est_clique(pos_souris):
                    algo_choisi = 'dfs'
                elif bouton_comparer.est_clique(pos_souris):
                    algo_choisi = 'comparer'

    return algo_choisi

#---------------------------------------- Algorithmes de Recherche ----------------------------------------
def copie_grille(grille):
    """
    Crée une copie complète du labyrinthe pour chaque algorithme.
    """
    copie = [[Case(case.ligne, case.colonne) for case in ligne] for ligne in grille]
    for i in range(NB_LIGNES):
        for j in range(NB_COLONNES):
            copie[i][j].murs = grille[i][j].murs.copy()  # Copier aussi les murs
    return copie


def algorithme_dijkstra(grille, depart, arrivee):
    """
    Implémentation de l'algorithme de Dijkstra pour la recherche du chemin le plus court.
    """
    depart.distance = 0
    file_priorite = []
    heapq.heappush(file_priorite, (depart.distance, depart))

    while file_priorite:
        _, courant = heapq.heappop(file_priorite)

        if courant == arrivee:
            return True

        for voisin in recuperer_voisins(grille, courant):
            nouvelle_distance = courant.distance + 1
            if nouvelle_distance < voisin.distance:
                voisin.distance = nouvelle_distance
                voisin.precedente = courant
                heapq.heappush(file_priorite, (voisin.distance, voisin))

    return False


def algorithme_astar(grille, depart, arrivee):
    """
    Implémentation de l'algorithme A* pour trouver un chemin optimal.
    """
    ensemble_ouvert = []
    heapq.heappush(ensemble_ouvert, (0, depart))
    depart.distance = 0

    while ensemble_ouvert:
        _, courant = heapq.heappop(ensemble_ouvert)

        if courant == arrivee:
            return True

        for voisin in recuperer_voisins(grille, courant):
            score_g = courant.distance + 1
            if score_g < voisin.distance:
                voisin.distance = score_g
                voisin.cout_estime = score_g + heuristique(voisin, arrivee)
                voisin.precedente = courant
                heapq.heappush(ensemble_ouvert, (voisin.cout_estime, voisin))

    return False


def algorithme_bfs(grille, depart, arrivee):
    """
    Recherche en largeur (BFS) pour explorer le labyrinthe.
    """
    file = [depart]
    depart.distance = 0
    depart.visitee = True

    while file:
        courant = file.pop(0)

        if courant == arrivee:
            return True

        for voisin in recuperer_voisins(grille, courant):
            if not voisin.visitee:
                voisin.visitee = True
                voisin.distance = courant.distance + 1
                voisin.precedente = courant
                file.append(voisin)

    return False


def algorithme_dfs(grille, depart, arrivee):
    """
    Recherche en profondeur (DFS) pour parcourir le labyrinthe.
    """
    pile = [depart]
    depart.visitee = True

    while pile:
        courant = pile.pop()

        if courant == arrivee:
            return True

        for voisin in recuperer_voisins(grille, courant):
            if not voisin.visitee:
                voisin.visitee = True
                voisin.precedente = courant
                pile.append(voisin)

    return False


def recuperer_voisins(grille, case):
    """
    Récupère les voisins d'une case en fonction des murs présents.
    """
    voisins = []
    ligne, colonne = case.ligne, case.colonne
    if ligne > 0 and not case.murs['haut']:
        voisins.append(grille[ligne - 1][colonne])
    if ligne < NB_LIGNES - 1 and not case.murs['bas']:
        voisins.append(grille[ligne + 1][colonne])
    if colonne > 0 and not case.murs['gauche']:
        voisins.append(grille[ligne][colonne - 1])
    if colonne < NB_COLONNES - 1 and not case.murs['droite']:
        voisins.append(grille[ligne][colonne + 1])
    return voisins


def heuristique(case, arrivee):
    """
    Calcul de l'heuristique pour A* (distance euclidienne).
    """
    return sqrt((case.ligne - arrivee.ligne) ** 2 + (case.colonne - arrivee.colonne) ** 2)


def reconstruire_chemin(arrivee):
    """
    Reconstruit le chemin de la case de fin à la case de départ.
    """
    chemin = []
    courant = arrivee
    while courant.precedente:
        chemin.append(courant)
        courant = courant.precedente
    chemin.reverse()
    return chemin

#---------------------------------------- Comparaison des Algorithmes ----------------------------------------
def afficher_animation_comparaison(grille, depart, arrivee, resultats):
    """
    Anime la comparaison des algorithmes de recherche visuellement.
    """
    longueur_max_chemin = max(len(resultat[3]) for resultat in resultats)
    
    for etape in range(longueur_max_chemin):
        fenetre.blit(image_fond, (0, 0))
        pygame.draw.rect(fenetre, NOIR, (MARGE_X, MARGE_Y, LARGEUR, HAUTEUR))
        
        # Redessiner toutes les cases
        for ligne in grille:
            for case in ligne:
                case.dessiner()
        dessiner_depart_arrivee(depart, arrivee)
        
        # Afficher la progression de chaque algorithme
        for nom_algo, temps, couleur, chemin in resultats:
            if etape < len(chemin):
                dessiner_balle(chemin[etape], couleur)
        
        pygame.display.update()
        pygame.time.delay(50)


def afficher_resultats_comparaison(resultats):
    """
    Affiche les résultats finaux de la comparaison des algorithmes.
    """
    # Trie les résultats pour afficher du plus rapide au plus lent
    resultats_tries = sorted(resultats, key=lambda x: x[1])
        
    # Affiche les résultats sur l'écran
    fenetre.blit(image_fond, (0, 0))
    police = pygame.font.Font(None, 36)
    decalage_y = 100
    
    titre_surface = police.render("Résultats de la comparaison :", True, BLANC)
    fenetre.blit(titre_surface, (50, decalage_y))
    decalage_y += 50
    
    for rang, (nom_algo, temps, couleur, _) in enumerate(resultats_tries):
        texte_resultat = f"{rang + 1}. {nom_algo} - Temps : {temps*(10**6):.2f} us"
        texte_surface = police.render(texte_resultat, True, couleur)
        fenetre.blit(texte_surface, (50, decalage_y))
        decalage_y += 50
    
    pygame.display.update()


def comparer_algorithmes_animation(grille, depart, arrivee):
    """
    Exécute et compare les algorithmes de recherche sur le même labyrinthe.
    """
    algorithmes = [
        ('Dijkstra', algorithme_dijkstra, VERT),
        ('A*', algorithme_astar, ORANGE),
        ('BFS', algorithme_bfs, BLEU_FONCE),
        ('DFS', algorithme_dfs, JAUNE)
    ]
    
    resultats = []
    for nom_algo, fonction_algo, couleur in algorithmes:
        copie = copie_grille(grille)
        reinitialiser_grille(copie)

        debut = time.time()
        trouve = fonction_algo(copie, copie[depart.ligne][depart.colonne], copie[arrivee.ligne][arrivee.colonne])
        temps_execution = time.time() - debut
        
        if trouve:
            chemin = reconstruire_chemin(copie[arrivee.ligne][arrivee.colonne])
            resultats.append((nom_algo, temps_execution, couleur, chemin))
        else:
            resultats.append((nom_algo, float('inf'), couleur, []))
    
    return resultats

def afficher_panneau_info(nom_algo, temps_execution):
    """
    Affiche un panneau d'informations avec le nom de l'algorithme et le temps écoulé.
    """
    panneau_rect = pygame.Rect(0, FENETRE_HAUTEUR - 50, FENETRE_LARGEUR, 50)
    pygame.draw.rect(fenetre, NOIR, panneau_rect)
    
    # Texte des informations
    police = pygame.font.Font(None, 36)
    texte_info = f"Algorithme : {nom_algo} | Temps : {temps_execution*(10**6):.2f} us"
    texte_surface = police.render(texte_info, True, BLANC)
    fenetre.blit(texte_surface, (20, FENETRE_HAUTEUR - 40))

#---------------------------------------- Choix de la Taille du Labyrinthe ----------------------------------------
def menu_taille_labyrinthe():
    """
    Affiche un menu pour choisir la taille du labyrinthe (Petit, Moyen, Grand).
    """
    while True:
        fenetre.blit(image_fond, (0, 0))

        police_grande = pygame.font.Font(None, 50)
        texte_titre = police_grande.render("Choisissez la taille du labyrinthe", True, BLANC)
        fenetre.blit(texte_titre, ((FENETRE_LARGEUR - texte_titre.get_width()) // 2, 50))

        bouton_petit = Bouton((FENETRE_LARGEUR - 200) // 2, (FENETRE_HAUTEUR - 50) // 2, 200, 50, GRIS, "Petit")
        bouton_moyen = Bouton((FENETRE_LARGEUR - 200) // 2, (FENETRE_HAUTEUR - 50) // 2 + 60, 200, 50, GRIS, "Moyen")
        bouton_grand = Bouton((FENETRE_LARGEUR - 200) // 2, (FENETRE_HAUTEUR - 50) // 2 + 120, 200, 50, GRIS, "Grand")

        pos_souris = pygame.mouse.get_pos()
        clic_souris = pygame.mouse.get_pressed()

        # Vérification du survol et affichage des boutons
        for bouton in [bouton_petit, bouton_moyen, bouton_grand]:
            bouton.verifier_survol(pos_souris)
            bouton.dessiner()

        pygame.display.update()

        # Gestion des événements pour choisir la taille
        for evenement in pygame.event.get():
            if evenement.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if clic_souris[0]:
                if bouton_petit.est_clique(pos_souris):
                    return 20
                elif bouton_moyen.est_clique(pos_souris):
                    return 30
                elif bouton_grand.est_clique(pos_souris):
                    return 40

#---------------------------------------- Fonction Principale ----------------------------------------
def principal():
    """
    Fonction principale pour gérer l'ensemble du jeu.
    """
    global NB_LIGNES, NB_COLONNES, TAILLE_CASE, LARGEUR_CASE, HAUTEUR_CASE

    menu_principal()
    NB_LIGNES = NB_COLONNES = menu_taille_labyrinthe()
    LARGEUR_CASE = LARGEUR // NB_COLONNES
    HAUTEUR_CASE = HAUTEUR // NB_LIGNES
    TAILLE_CASE = min(LARGEUR_CASE, HAUTEUR_CASE)
    algo_choisi = menu_selection_algo()
    
    # Génération et configuration du labyrinthe
    grille = [[Case(ligne, colonne) for colonne in range(NB_COLONNES)] for ligne in range(NB_LIGNES)]
    creer_labyrinthe(grille)
    depart, arrivee = grille[random.randint(0, NB_LIGNES - 1)][0], grille[random.randint(0, NB_LIGNES - 1)][NB_COLONNES - 1]

    if algo_choisi == 'comparer':
        grille = [[Case(ligne, colonne) for colonne in range(NB_COLONNES)] for ligne in range(NB_LIGNES)]
        creer_labyrinthe(grille)
        resultats = comparer_algorithmes_animation(grille, depart, arrivee)
        afficher_animation_comparaison(grille, depart, arrivee, resultats)
        afficher_resultats_comparaison(resultats)
        pygame.time.delay(5000)
        principal()  # Relancer le jeu après comparaison
        return

    elif algo_choisi in ['dijkstra', 'astar', 'bfs', 'dfs']:
        grille = [[Case(ligne, colonne) for colonne in range(NB_COLONNES)] for ligne in range(NB_LIGNES)]
        creer_labyrinthe(grille)
        copie_grille_jeu = copie_grille(grille)
        reinitialiser_grille(copie_grille_jeu)

        debut = time.time()

        if algo_choisi == 'dijkstra':
            trouve = algorithme_dijkstra(copie_grille_jeu, copie_grille_jeu[depart.ligne][depart.colonne], copie_grille_jeu[arrivee.ligne][arrivee.colonne])
            nom_algo = 'Dijkstra'
        elif algo_choisi == 'astar':
            trouve = algorithme_astar(copie_grille_jeu, copie_grille_jeu[depart.ligne][depart.colonne], copie_grille_jeu[arrivee.ligne][arrivee.colonne])
            nom_algo = 'A*'
        elif algo_choisi == 'bfs':
            trouve = algorithme_bfs(copie_grille_jeu, copie_grille_jeu[depart.ligne][depart.colonne], copie_grille_jeu[arrivee.ligne][arrivee.colonne])
            nom_algo = 'BFS'
        elif algo_choisi == 'dfs':
            trouve = algorithme_dfs(copie_grille_jeu, copie_grille_jeu[depart.ligne][depart.colonne], copie_grille_jeu[arrivee.ligne][arrivee.colonne])
            nom_algo = 'DFS'

        temps_execution = time.time() - debut

        if trouve:
            chemin = reconstruire_chemin(copie_grille_jeu[arrivee.ligne][arrivee.colonne])
            
            # Animation du chemin trouvé
            for case in chemin:
                fenetre.blit(image_fond, (0, 0))
                pygame.draw.rect(fenetre, NOIR, (MARGE_X, MARGE_Y, LARGEUR, HAUTEUR))
                for ligne in copie_grille_jeu:
                    for case_grille in ligne:
                        case_grille.dessiner()
                dessiner_depart_arrivee(depart, arrivee)
                dessiner_balle(case)
                pygame.display.update()
                pygame.time.delay(50)
            
            # Affichage du panneau d'informations
            afficher_panneau_info(nom_algo, temps_execution)

            # Boutons pour réessayer ou quitter
            bouton_reessayer = Bouton((FENETRE_LARGEUR - 200) // 2, FENETRE_HAUTEUR - FENETRE_HAUTEUR // 2, 200, 50, BLEU_FONCE, 'Réessayer')
            bouton_quitter = Bouton((FENETRE_LARGEUR - 200) // 2, FENETRE_HAUTEUR - FENETRE_HAUTEUR // 2 + 60, 200, 50, ROUGE, 'Quitter')

            bouton_reessayer.dessiner()
            bouton_quitter.dessiner()
            pygame.display.update()

            attente_reponse = True
            while attente_reponse:
                for evenement in pygame.event.get():
                    if evenement.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    elif evenement.type == pygame.MOUSEBUTTONDOWN:
                        if bouton_reessayer.est_clique(evenement.pos):
                            principal()
                            return
                        elif bouton_quitter.est_clique(evenement.pos):
                            pygame.quit()
                            sys.exit()

        else:
            # Cas où aucun chemin n'est trouvé
            police_grande = pygame.font.Font(None, 48)
            texte_erreur = police_grande.render(f"Aucun chemin trouvé pour {nom_algo}", True, ROUGE)
            fenetre.blit(texte_erreur, ((FENETRE_LARGEUR - texte_erreur.get_width()) // 2, FENETRE_HAUTEUR // 2))
            pygame.display.update()
            pygame.time.delay(3000)
            principal()
            return

        pygame.display.update()

        for evenement in pygame.event.get():
            if evenement.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

    pygame.quit()

#---------------------------------------- Lancement du Jeu ----------------------------------------
if __name__ == "__main__":
    principal()
