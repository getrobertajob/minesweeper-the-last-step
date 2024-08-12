import os
import sys
import pygame
import random
import time

# Initialize Pygame
pygame.init()

# Function to get the correct path to the resources
def resource_path(relative_path):
    """ Get the absolute path to a resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores the path in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Define some constants
GRID_SIZE = 10
CELL_SIZE = 40
BUTTON_WIDTH = 120
BUTTON_HEIGHT = 40
SCOREBOARD_HEIGHT = 40
WINDOW_WIDTH = GRID_SIZE * CELL_SIZE
WINDOW_HEIGHT = GRID_SIZE * CELL_SIZE + BUTTON_HEIGHT + SCOREBOARD_HEIGHT + 30  # Extra height for buttons and scoreboard
BACKGROUND_COLOR = (255, 255, 255)
LINE_COLOR = (0, 0, 0)
BUTTON_COLOR = (200, 200, 200)
BUTTON_TEXT_COLOR = (0, 0, 0)
BUTTON_HOVER_COLOR = (170, 170, 170)
BUTTON_DISABLED_COLOR = (220, 220, 220)
BUTTON_DISABLED_TEXT_COLOR = (180, 180, 180)
BUTTON_ENABLED_BORDER_COLOR = (255, 255, 0)  # Yellow color for enabled border
POPUP_COLOR = (240, 240, 240)
POPUP_BORDER_COLOR = (0, 0, 0)
SCOREBOARD_COLOR = (230, 230, 230)  # Light grey for the scoreboard background
SCOREBOARD_TEXT_COLOR = (0, 0, 0)  # Black color for text
CIRCLE_COLOR = (0, 255, 0, 100)  # Green with transparency (RGBA)

# Update paths to resources using the resource_path function
CHARACTER_IMAGE_PATH = resource_path('images/character.png')
LANDMINE_IMAGE_PATH = resource_path('images/landmine.png')
EXPLOSION_IMAGE_PATH = resource_path('images/explosion.png')
FOOTSTEPS_SOUND_PATH = resource_path('audio/footsteps.mp3')
CLICK_SOUND_PATH = resource_path('audio/click.mp3')
EXPLOSION_SOUND_PATH = resource_path('audio/explosion.mp3')
WIN_SOUND_PATH = resource_path('audio/win.mp3')
LOSE_SOUND_PATH = resource_path('audio/loose.mp3')

# Set up the display
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Minesweeper Grid")

# Set the number of mines
num_mines = 5  # You can change this value to control the number of mines

# Load the character image, landmine image, and explosion image
character_image = pygame.image.load(CHARACTER_IMAGE_PATH)
character_image = pygame.transform.scale(character_image, (CELL_SIZE, CELL_SIZE))
landmine_image = pygame.image.load(LANDMINE_IMAGE_PATH)
landmine_image = pygame.transform.scale(landmine_image, (CELL_SIZE, CELL_SIZE))
explosion_image = pygame.image.load(EXPLOSION_IMAGE_PATH)
explosion_image = pygame.transform.scale(explosion_image, (CELL_SIZE, CELL_SIZE))

# Load the sound effects
footsteps_sound = pygame.mixer.Sound(FOOTSTEPS_SOUND_PATH)
click_sound = pygame.mixer.Sound(CLICK_SOUND_PATH)
explosion_sound = pygame.mixer.Sound(EXPLOSION_SOUND_PATH)
win_sound = pygame.mixer.Sound(WIN_SOUND_PATH)
lose_sound = pygame.mixer.Sound(LOSE_SOUND_PATH)

# Function to reset the game
def reset_game():
    global character_pos, mine_positions, score, time_remaining, start_ticks, timer_stopped, landmines, explosions
    character_pos = [random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1)]
    mine_positions.clear()
    landmines = []
    explosions = []
    while len(mine_positions) < num_mines:
        mine_pos = (random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1))
        if mine_pos != tuple(character_pos):
            mine_positions.add(mine_pos)
    score = 0
    time_remaining = 60
    start_ticks = pygame.time.get_ticks()
    timer_stopped = False

# Initialize the game
character_pos = [random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1)]
mine_positions = set()
landmines = []
explosions = []
reset_game()

# Initialize the score variable and timer
score = 0
time_remaining = 60
start_ticks = pygame.time.get_ticks()
timer_stopped = False

# Function to count mines around a given cell
def count_adjacent_mines(pos, mine_positions):
    x, y = pos
    count = 0
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            if dx == 0 and dy == 0:
                continue
            if (x + dx, y + dy) in mine_positions:
                count += 1
    return count

# Function to get the positions of adjacent mines
def get_adjacent_mines(pos, mine_positions):
    x, y = pos
    adjacent_mines = []
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            if dx == 0 and dy == 0:
                continue
            adjacent_pos = (x + dx, y + dy)
            if adjacent_pos in mine_positions:
                adjacent_mines.append(adjacent_pos)
    return adjacent_mines

# Function to check if the character is adjacent to any mine
def is_adjacent_to_mine(character_pos, mine_positions):
    return count_adjacent_mines(character_pos, mine_positions) > 0

# Function to display the "Game Over" or "Congratulations" popup
def show_popup(message, score, time_taken=None, win=False):
    popup_width = 300
    popup_height = 220
    popup_x = (WINDOW_WIDTH - popup_width) // 2
    popup_y = (WINDOW_HEIGHT - popup_height) // 2

    # Play the win or lose sound
    if win:
        win_sound.play()
    else:
        lose_sound.play()

    popup_rect = pygame.Rect(popup_x, popup_y, popup_width, popup_height)
    pygame.draw.rect(screen, POPUP_COLOR, popup_rect)
    pygame.draw.rect(screen, POPUP_BORDER_COLOR, popup_rect, 2)

    font = pygame.font.SysFont(None, 30)
    text_surface = font.render(message, True, SCOREBOARD_TEXT_COLOR)
    screen.blit(text_surface, (popup_x + (popup_width - text_surface.get_width()) // 2, popup_y + 20))

    score_surface = font.render(f"Points from mines: {score}", True, SCOREBOARD_TEXT_COLOR)
    screen.blit(score_surface, (popup_x + (popup_width - score_surface.get_width()) // 2, popup_y + 50))

    if time_taken is not None:
        time_bonus = 60 - time_taken
        time_surface = font.render(f"Time bonus: {time_bonus}", True, SCOREBOARD_TEXT_COLOR)
        screen.blit(time_surface, (popup_x + (popup_width - time_surface.get_width()) // 2, popup_y + 80))

        # Draw the black line separator
        pygame.draw.line(screen, SCOREBOARD_TEXT_COLOR, (popup_x + 20, popup_y + 110), (popup_x + popup_width - 20, popup_y + 110), 3)

        final_score = score + time_bonus
        final_score_surface = font.render(f"Final score: {final_score}", True, SCOREBOARD_TEXT_COLOR)
        screen.blit(final_score_surface, (popup_x + (popup_width - final_score_surface.get_width()) // 2, popup_y + 120))

    try_again_button_rect = pygame.Rect(popup_x + 30, popup_y + 150, 100, 40)
    end_game_button_rect = pygame.Rect(popup_x + 170, popup_y + 150, 100, 40)

    draw_button("Try Again", try_again_button_rect.x, try_again_button_rect.y, try_again_button_rect.width, try_again_button_rect.height)
    draw_button("End Game", end_game_button_rect.x, end_game_button_rect.y, end_game_button_rect.width, end_game_button_rect.height)

    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()  # Updated to sys.exit() instead of exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if try_again_button_rect.collidepoint(pygame.mouse.get_pos()):
                    reset_game()
                    return
                elif end_game_button_rect.collidepoint(pygame.mouse.get_pos()):
                    pygame.quit()
                    sys.exit()  # Updated to sys.exit() instead of exit()

# Set up the font for rendering text
font = pygame.font.SysFont(None, 24)

# Function to draw a button
def draw_button(text, x, y, width, height, enabled=True, hover=False, border=False):
    if not enabled:
        color = BUTTON_DISABLED_COLOR
        text_color = BUTTON_DISABLED_TEXT_COLOR
        text = "Searching..."
    else:
        color = BUTTON_HOVER_COLOR if hover else BUTTON_COLOR
        text_color = BUTTON_TEXT_COLOR

    pygame.draw.rect(screen, color, (x, y, width, height))

    if border and enabled:
        pygame.draw.rect(screen, BUTTON_ENABLED_BORDER_COLOR, (x - 3, y - 3, width + 6, height + 6), 3)

    text_surface = font.render(text, True, text_color)
    screen.blit(text_surface, (x + (width - text_surface.get_width()) // 2,
                               y + (height - text_surface.get_height()) // 2))

# Function to draw the scoreboard and timer
def draw_scoreboard(score, time_remaining, x, y, width, height):
    pygame.draw.rect(screen, SCOREBOARD_COLOR, (x, y, width, height))
    text_surface = font.render(f"Score: {score}", True, SCOREBOARD_TEXT_COLOR)
    screen.blit(text_surface, (x + 10, y + (height - text_surface.get_height()) // 2))

    timer_surface = font.render(f"Time: {time_remaining}s", True, SCOREBOARD_TEXT_COLOR)
    screen.blit(timer_surface, (x + width - timer_surface.get_width() - 10, y + (height - timer_surface.get_height()) // 2))

# Button and scoreboard positions
scoreboard_rect = pygame.Rect(10, GRID_SIZE * CELL_SIZE + 10, WINDOW_WIDTH - 20, SCOREBOARD_HEIGHT)
disarm_button_rect = pygame.Rect((WINDOW_WIDTH - BUTTON_WIDTH * 2 - 20) // 2, 
                                  WINDOW_HEIGHT - BUTTON_HEIGHT - 10, 
                                  BUTTON_WIDTH, BUTTON_HEIGHT)
end_game_button_rect = pygame.Rect((WINDOW_WIDTH + BUTTON_WIDTH) // 2 + 10, 
                                    WINDOW_HEIGHT - BUTTON_HEIGHT - 10, 
                                    BUTTON_WIDTH, BUTTON_HEIGHT)

# Game loop
running = True
while running:
    mouse_pos = pygame.mouse.get_pos()
    adjacent_to_mine = is_adjacent_to_mine(character_pos, mine_positions)

    # Calculate time remaining if the timer is not stopped
    if not timer_stopped:
        time_remaining = 60 - (pygame.time.get_ticks() - start_ticks) // 1000
        if time_remaining <= 0:
            show_popup("Time's Up! Game Over!", score, win=False)
            continue

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            # Play the footsteps sound whenever an arrow key is pressed
            if event.key in [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN]:
                footsteps_sound.play()

            if event.key == pygame.K_LEFT and character_pos[0] > 0:
                character_pos[0] -= 1
            elif event.key == pygame.K_RIGHT and character_pos[0] < GRID_SIZE - 1:
                character_pos[0] += 1
            elif event.key == pygame.K_UP and character_pos[1] > 0:
                character_pos[1] -= 1
            elif event.key == pygame.K_DOWN and character_pos[1] < GRID_SIZE - 1:
                character_pos[1] += 1

            # Check if the character has moved to a mine
            if tuple(character_pos) in mine_positions:
                explosion_sound.play()  # Play explosion sound
                explosions.append(tuple(character_pos))  # Add explosion at the character's position
                
                # Draw explosion immediately
                screen.blit(explosion_image, (character_pos[0] * CELL_SIZE, character_pos[1] * CELL_SIZE))
                pygame.display.flip()  # Update the display to show the explosion
                
                # Delay for a brief moment to ensure explosion is visible before popup
                pygame.time.wait(500)  # Wait for 500 milliseconds (0.5 seconds)
                
                show_popup("Game Over!", score, win=False)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if disarm_button_rect.collidepoint(mouse_pos) and adjacent_to_mine:
                mines_nearby = get_adjacent_mines(character_pos, mine_positions)
                score += len(mines_nearby) * 10  # Increment the score by 10 for each adjacent mine
                click_sound.play()  # Play click sound when mines are removed
                print(f"Disarm Mine button clicked, {len(mines_nearby)} mines removed, score incremented by {len(mines_nearby) * 10}")
                # Add landmine images and remove the adjacent mines from the mine_positions set
                for mine in mines_nearby:
                    landmines.append(mine)
                    mine_positions.remove(mine)
                # Check if all mines are cleared
                if not mine_positions:
                    timer_stopped = True  # Stop the timer
                    time_taken = 60 - time_remaining  # Calculate time taken
                    show_popup("YAY! All safe now.", score, time_taken, win=True)
            elif end_game_button_rect.collidepoint(mouse_pos):
                print("End Game button clicked")
                running = False

    # Fill the background
    screen.fill(BACKGROUND_COLOR)

    # Draw the grid
    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE):
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, BACKGROUND_COLOR, rect)
            pygame.draw.rect(screen, LINE_COLOR, rect, 1)

            # Count mines around the current cell if adjacent to the character
            if abs(x - character_pos[0]) <= 1 and abs(y - character_pos[1]) <= 1:
                mine_count = count_adjacent_mines((x, y), mine_positions)
                if mine_count > 0:
                    text = font.render(str(mine_count), True, SCOREBOARD_TEXT_COLOR)
                    screen.blit(text, (x * CELL_SIZE + CELL_SIZE // 3, y * CELL_SIZE + CELL_SIZE // 4))

    # Draw the landmines where mines were removed
    for landmine in landmines:
        screen.blit(landmine_image, (landmine[0] * CELL_SIZE, landmine[1] * CELL_SIZE))

    # Draw the explosions where the character hit a mine
    for explosion in explosions:
        screen.blit(explosion_image, (explosion[0] * CELL_SIZE, explosion[1] * CELL_SIZE))

    # Draw the transparent green circle around the character and adjacent cells, including corners
    circle_center = (character_pos[0] * CELL_SIZE + CELL_SIZE // 2, character_pos[1] * CELL_SIZE + CELL_SIZE // 2)
    circle_radius = int(2.5 * CELL_SIZE)  # Increased radius to cover character, adjacent, and corner cells
    circle_surface = pygame.Surface((2 * circle_radius, 2 * circle_radius), pygame.SRCALPHA)
    pygame.draw.circle(circle_surface, CIRCLE_COLOR, (circle_radius, circle_radius), circle_radius)
    screen.blit(circle_surface, (circle_center[0] - circle_radius, circle_center[1] - circle_radius))

    # Draw the character in the current cell, unless there's an explosion
    if tuple(character_pos) not in explosions:
        screen.blit(character_image, (character_pos[0] * CELL_SIZE, character_pos[1] * CELL_SIZE))

    # Draw the scoreboard and timer below the grid
    draw_scoreboard(score, time_remaining, scoreboard_rect.x, scoreboard_rect.y, 
                    scoreboard_rect.width, scoreboard_rect.height)

    # Draw the buttons
    draw_button("Disarm Mine", disarm_button_rect.x, disarm_button_rect.y, 
                disarm_button_rect.width, disarm_button_rect.height, 
                enabled=adjacent_to_mine, 
                hover=disarm_button_rect.collidepoint(mouse_pos) and adjacent_to_mine,
                border=adjacent_to_mine)
    draw_button("End Game", end_game_button_rect.x, end_game_button_rect.y, 
                end_game_button_rect.width, end_game_button_rect.height, 
                hover=end_game_button_rect.collidepoint(mouse_pos))

    # Update the display
    pygame.display.flip()

# Quit Pygame
pygame.quit()
sys.exit()  # Updated to sys.exit() instead of exit()
