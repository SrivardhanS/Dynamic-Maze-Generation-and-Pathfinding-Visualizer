import pygame
import random
from collections import deque

# Initialize Pygame
pygame.init()

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (200, 200, 200)
DARK_GRAY = (150, 150, 150)
ORANGE = (255, 165, 0)
PURPLE = (160, 32, 240)
GOLD = (255, 215, 0)

# Screen dimensions
WIDTH = 800
HEIGHT = 600

# Maze dimensions
MAZE_WIDTH = 31
MAZE_HEIGHT = 23

# Calculate cell size
CELL_SIZE = min((WIDTH - 200) // MAZE_WIDTH, HEIGHT // MAZE_HEIGHT)

# Adjust screen size to fit maze and buttons
SCREEN_WIDTH = CELL_SIZE * MAZE_WIDTH + 200
SCREEN_HEIGHT = max(CELL_SIZE * MAZE_HEIGHT, 300)

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Maze Generator and Solver")

# Default speed (higher value = slower speed)
speed = 100  # milliseconds

class Button:
    def __init__(self, x, y, width, height, text, color, text_color, action):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.text_color = text_color
        self.action = action

    def draw(self):
        pygame.draw.rect(screen, self.color, self.rect)
        font = pygame.font.Font(None, 30)
        text = font.render(self.text, True, self.text_color)
        text_rect = text.get_rect(center=self.rect.center)
        screen.blit(text, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.action()

class Maze:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.maze = [[1 for _ in range(width)] for _ in range(height)]

    def generate(self):
        def dfs(x, y):
            self.maze[y][x] = 0
            directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
            random.shuffle(directions)
            for dx, dy in directions:
                nx, ny = x + dx * 2, y + dy * 2
                if 0 <= nx < self.width and 0 <= ny < self.height and self.maze[ny][nx] == 1:
                    self.maze[y + dy][x + dx] = 0
                    dfs(nx, ny)

        self.maze = [[1 for _ in range(self.width)] for _ in range(self.height)]
        dfs(1, 1)
        self.maze[1][0] = 0  # entrance
        self.maze[self.height - 2][self.width - 1] = 0  # exit

    def solve(self):
        start = (0, 1)
        end = (self.width - 1, self.height - 2)
        queue = deque([(start, [start])])
        visited = set([start])
        frontier = set([start])
        explored = set()

        while queue:
            (x, y), path = queue.popleft()
            frontier.remove((x, y))
            explored.add((x, y))

            if (x, y) == end:
                return path, frontier, explored

            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                nx, ny = x + dx, y + dy
                if (0 <= nx < self.width and 0 <= ny < self.height and
                    self.maze[ny][nx] == 0 and (nx, ny) not in visited):
                    queue.append(((nx, ny), path + [(nx, ny)]))
                    visited.add((nx, ny))
                    frontier.add((nx, ny))
                    yield (nx, ny), frontier, explored

        return None, frontier, explored

def draw_maze(maze, solution=None, current=None, frontier=None, explored=None, show_restart=False):
    screen.fill(WHITE)
    
    # Draw maze cells
    for y in range(maze.height):
        for x in range(maze.width):
            if maze.maze[y][x] == 1:
                pygame.draw.rect(screen, BLACK, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
            elif explored and (x, y) in explored:
                pygame.draw.rect(screen, PURPLE, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
            elif frontier and (x, y) in frontier:
                pygame.draw.rect(screen, ORANGE, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

    if solution:
        for x, y in solution:
            pygame.draw.rect(screen, RED, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

        # Start point
        start_x, start_y = solution[0]
        pygame.draw.rect(screen, GREEN, (start_x * CELL_SIZE, start_y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

        # End point
        end_x, end_y = solution[-1]
        pygame.draw.rect(screen, BLUE, (end_x * CELL_SIZE, end_y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

    if current:
        pygame.draw.rect(screen, BLUE, (current[0] * CELL_SIZE, current[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE))

    for button in buttons:
        button.draw()

    if show_restart:
        restart_font = pygame.font.Font(None, 50)
        restart_text = restart_font.render("Press 'R' to Restart", True, BLACK)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
        pygame.draw.rect(screen, GOLD, restart_rect.inflate(20, 10))  # Draw background rectangle with gold color
        screen.blit(restart_text, restart_rect)

    pygame.display.flip()

def generate_new_maze():
    global maze, solution, solver, game_over, frontier, explored
    maze.generate()
    solution = None
    solver = None
    game_over = False
    frontier = set()  # Reset the frontier
    explored = set()  # Reset the explored nodes

def start_solving():
    global solver, game_over, frontier, explored
    solver = maze.solve()
    game_over = False
    frontier = set()  # Reset the frontier
    explored = set()  # Reset the explored nodes

def increase_speed():
    global speed
    speed = max(10, speed - 10)

def decrease_speed():
    global speed
    speed += 10

def pause_game():
    global paused
    paused = not paused

def handle_restart(event):
    global game_over
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_r:
            generate_new_maze()
            start_solving()
        elif event.key == pygame.K_ESCAPE:
            pygame.quit()
            exit()

maze = Maze(MAZE_WIDTH, MAZE_HEIGHT)
maze.generate()
solution = None
solver = None
game_over = False
paused = False

buttons = [
    Button(SCREEN_WIDTH - 180, 50, 160, 50, "Generate Maze", GRAY, BLACK, generate_new_maze),
    Button(SCREEN_WIDTH - 180, 120, 160, 50, "Solve Maze", GRAY, BLACK, start_solving),
    Button(SCREEN_WIDTH - 180, 190, 160, 50, "Faster", GRAY, BLACK, increase_speed),
    Button(SCREEN_WIDTH - 180, 260, 160, 50, "Slower", GRAY, BLACK, decrease_speed),
    Button(SCREEN_WIDTH - 180, 330, 160, 50, "Pause", GRAY, BLACK, pause_game)
]

def main():
    global solution, solver, game_over, paused
    clock = pygame.time.Clock()
    running = True
    frontier = set()
    explored = set()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            for button in buttons:
                button.handle_event(event)
            handle_restart(event)

        if not paused:
            if solver:
                try:
                    current, frontier, explored = next(solver)
                    draw_maze(maze, solution, current, frontier, explored)
                    pygame.time.delay(speed)
                except StopIteration:
                    result = maze.solve()
                    if isinstance(result, tuple) and len(result) == 3:
                        solution, frontier, explored = result
                    else:
                        solution, frontier, explored = None, set(), set()
                    solver = None
                    game_over = True
            else:
                draw_maze(maze, solution, frontier=frontier, explored=explored, show_restart=game_over)

        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
