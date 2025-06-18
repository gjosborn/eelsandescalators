import pygame
import random
import math
import time

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 800
BOARD_SIZE = 600
BOARD_OFFSET_X = 50
BOARD_OFFSET_Y = 50
CELL_SIZE = BOARD_SIZE // 10
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 100, 200)
GREEN = (0, 150, 0)
RED = (200, 0, 0)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
LIGHT_BLUE = (173, 216, 230)
DARK_GREEN = (0, 100, 0)
BROWN = (139, 69, 19)
PINK = (255, 192, 203)
GRAY = (128, 128, 128)
LIGHT_GRAY = (211, 211, 211)

# Player colors
PLAYER_COLORS = [RED, BLUE, GREEN, YELLOW]

class Button:
    def __init__(self, x, y, width, height, text, color, text_color=BLACK):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.text_color = text_color
        self.font = pygame.font.Font(None, 24)
        self.clicked = False
        
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)
        
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
    
    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)


class EelsAndEscalatorsGUI:
    def __init__(self):
        self.pending_move = None
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Eels and Escalators")
        self.clock = pygame.time.Clock()
        
        # Game state
        self.game_state = "menu"  # menu, playing, game_over
        self.num_players = 2
        self.players = {}
        self.current_player = 0
        self.dice_value = 1
        self.winner = None
        self.animation_active = False
        self.animation_start_time = 0
        self.dragging_player = None
        
        # Fonts
        self.title_font = pygame.font.Font(None, 48)
        self.subtitle_font = pygame.font.Font(None, 32)
        self.text_font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        
        # Escalators and Eels
        self.escalators = {
            4: 14, 9: 31, 20: 38, 28: 84, 40: 59,
            51: 67, 63: 81, 71: 91
        }
        
        self.eels = {
            16: 6, 47: 26, 49: 11, 56: 53, 62: 19,
            64: 60, 87: 24, 93: 73, 95: 75, 98: 78
        }
        
        # Buttons
        self.roll_button = Button(700, 300, 120, 40, "Roll Dice", LIGHT_BLUE)
        self.new_game_button = Button(700, 350, 120, 40, "New Game", LIGHT_GRAY)
        self.player_buttons = []
        for i in range(4):
            self.player_buttons.append(
                Button(700, 150 + i * 40, 100, 30, f"{i+2} Players", LIGHT_GRAY)
            )
        
        self.setup_game()
    
    def setup_game(self):
        """Initialize game with default settings"""
        self.players = {}
        for i in range(self.num_players):
            self.players[f"Player {i+1}"] = {
                'position': 1,
                'color': PLAYER_COLORS[i],
                'x': 0,
                'y': 0
            }
        self.current_player = 0
        self.winner = None
        self.update_player_positions()
    
    def get_board_coordinates(self, position):
        """Convert board position to screen coordinates"""
        if position < 1:
            position = 1
        if position > 100:
            position = 100
            
        # Calculate row and column (0-indexed)
        row = (position - 1) // 10
        col = (position - 1) % 10
        
        # Reverse column for odd rows (snake pattern)
        if row % 2 == 1:
            col = 9 - col
        
        # Convert to screen coordinates (flip Y axis)
        screen_row = 9 - row
        x = BOARD_OFFSET_X + col * CELL_SIZE + CELL_SIZE // 2
        y = BOARD_OFFSET_Y + screen_row * CELL_SIZE + CELL_SIZE // 2
        
        return x, y
    
    def update_player_positions(self):
        """Update player screen positions based on board positions"""
        for player_data in self.players.values():
            x, y = self.get_board_coordinates(player_data['position'])
            player_data['x'] = x
            player_data['y'] = y
    
    def draw_board(self):
        """Draw the game board"""
        # Draw board background
        board_rect = pygame.Rect(BOARD_OFFSET_X, BOARD_OFFSET_Y, BOARD_SIZE, BOARD_SIZE)
        pygame.draw.rect(self.screen, WHITE, board_rect)
        pygame.draw.rect(self.screen, BLACK, board_rect, 3)
        
        # Draw grid and numbers
        for row in range(10):
            for col in range(10):
                # Calculate position number
                board_row = 9 - row  # Flip for display
                if board_row % 2 == 0:
                    position = board_row * 10 + col + 1
                else:
                    position = board_row * 10 + (9 - col) + 1
                
                # Cell coordinates
                x = BOARD_OFFSET_X + col * CELL_SIZE
                y = BOARD_OFFSET_Y + row * CELL_SIZE
                
                # Alternate cell colors
                if (row + col) % 2 == 0:
                    color = LIGHT_GRAY
                else:
                    color = WHITE
                
                cell_rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(self.screen, color, cell_rect)
                pygame.draw.rect(self.screen, BLACK, cell_rect, 1)
                
                # Draw position number
                text = self.small_font.render(str(position), True, BLACK)
                text_rect = text.get_rect(topleft=(x + 2, y + 2))
                self.screen.blit(text, text_rect)
        
        # Draw escalators
        for start, end in self.escalators.items():
            start_x, start_y = self.get_board_coordinates(start)
            end_x, end_y = self.get_board_coordinates(end)
            
            # Draw escalator line
            pygame.draw.line(self.screen, BROWN, (start_x, start_y), (end_x, end_y), 8)
            
            # Draw escalator steps
            steps = 5
            for i in range(1, steps):
                step_x = start_x + (end_x - start_x) * i / steps
                step_y = start_y + (end_y - start_y) * i / steps
                pygame.draw.line(self.screen, BROWN, 
                               (step_x - 10, step_y), (step_x + 10, step_y), 3)
            
            # Draw escalator markers
            pygame.draw.circle(self.screen, DARK_GREEN, (start_x, start_y), 8)
            pygame.draw.circle(self.screen, DARK_GREEN, (end_x, end_y), 8)
        
        # Draw eels
        for start, end in self.eels.items():
            start_x, start_y = self.get_board_coordinates(start)
            end_x, end_y = self.get_board_coordinates(end)
            
            # Draw eel body (curved line)
            points = []
            segments = 10
            for i in range(segments + 1):
                t = i / segments
                # Create a wavy line
                mid_x = start_x + (end_x - start_x) * t
                mid_y = start_y + (end_y - start_y) * t
                wave = math.sin(t * math.pi * 2) * 20
                mid_x += wave
                points.append((mid_x, mid_y))
            
            if len(points) > 1:
                pygame.draw.lines(self.screen, GREEN, False, points, 6)
            
            # Draw eel head and tail
            pygame.draw.circle(self.screen, DARK_GREEN, (start_x, start_y), 10)
            pygame.draw.circle(self.screen, GREEN, (end_x, end_y), 6)
    
    def draw_players(self):
        """Draw all players on the board"""
        player_names = list(self.players.keys())
        
        for i, (name, player_data) in enumerate(self.players.items()):
            x, y = player_data['x'], player_data['y']
            color = player_data['color']
            
            # Offset multiple players on same square
            offset_x = (i % 2) * 10 - 5
            offset_y = (i // 2) * 10 - 5
            
            # Draw player circle
            pygame.draw.circle(self.screen, color, (x + offset_x, y + offset_y), 12)
            pygame.draw.circle(self.screen, BLACK, (x + offset_x, y + offset_y), 12, 2)
            
            # Draw player number
            text = self.small_font.render(str(i + 1), True, WHITE)
            text_rect = text.get_rect(center=(x + offset_x, y + offset_y))
            self.screen.blit(text, text_rect)
    
    def draw_dice(self):
        """Draw the dice"""
        dice_x, dice_y = 750, 400
        dice_size = 60
        
        # Draw dice background
        dice_rect = pygame.Rect(dice_x, dice_y, dice_size, dice_size)
        pygame.draw.rect(self.screen, WHITE, dice_rect)
        pygame.draw.rect(self.screen, BLACK, dice_rect, 3)
        
        # Draw dice dots
        dot_positions = {
            1: [(0, 0)],
            2: [(-1, -1), (1, 1)],
            3: [(-1, -1), (0, 0), (1, 1)],
            4: [(-1, -1), (1, -1), (-1, 1), (1, 1)],
            5: [(-1, -1), (1, -1), (0, 0), (-1, 1), (1, 1)],
            6: [(-1, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (1, 1)]
        }
        
        dots = dot_positions.get(self.dice_value, [(0, 0)])
        for dot_x, dot_y in dots:
            dot_screen_x = dice_x + dice_size // 2 + dot_x * 12
            dot_screen_y = dice_y + dice_size // 2 + dot_y * 12
            pygame.draw.circle(self.screen, BLACK, (dot_screen_x, dot_screen_y), 4)
    
    def draw_ui(self):
        """Draw the user interface"""
        # Title
        title_text = self.title_font.render("Eels & Escalators", True, BLUE)
        self.screen.blit(title_text, (700, 50))
        
        # Current player
        if self.game_state == "playing":
            player_names = list(self.players.keys())
            current_name = player_names[self.current_player]
            current_color = self.players[current_name]['color']
            
            player_text = self.subtitle_font.render(f"Current: {current_name}", True, current_color)
            self.screen.blit(player_text, (700, 100))
            
            # Player positions
            y_offset = 480
            pos_title = self.text_font.render("Positions:", True, BLACK)
            self.screen.blit(pos_title, (700, y_offset))
            
            for i, (name, player_data) in enumerate(self.players.items()):
                y = y_offset + 30 + i * 25
                pos_text = self.text_font.render(
                    f"{name}: {player_data['position']}", 
                    True, player_data['color']
                )
                self.screen.blit(pos_text, (700, y))
        
        # Draw buttons
        if self.game_state == "menu":
            menu_title = self.title_font.render("Choose Players:", True, BLACK)
            self.screen.blit(menu_title, (700, 100))
            
            for button in self.player_buttons:
                button.draw(self.screen)
        elif self.game_state == "playing":
            self.roll_button.draw(self.screen)
            self.new_game_button.draw(self.screen)
            self.draw_dice()
        elif self.game_state == "game_over":
            winner_text = self.title_font.render(f"{self.winner} Wins!", True, RED)
            self.screen.blit(winner_text, (700, 200))
            self.new_game_button.draw(self.screen)

    def roll_dice(self):
        if self.animation_active:
            return
        self.dice_value = random.randint(1, 6)

    def handle_click(self, pos):
        if self.game_state == "menu":
            for i, button in enumerate(self.player_buttons):
                if button.is_clicked(pos):
                    self.num_players = i + 2
                    self.setup_game()
                    self.game_state = "playing"
                    return
        elif self.game_state == "playing":
            if self.roll_button.is_clicked(pos):
                self.roll_dice()
            elif self.new_game_button.is_clicked(pos):
                self.game_state = "menu"
            else:
                # Start drag if player clicked
                for name, data in self.players.items():
                    x, y = data['x'], data['y']
                    if math.hypot(pos[0] - x, pos[1] - y) <= 15:
                        self.dragging_player = name
                        break

    def handle_mouse_event(self, event):
        if self.dragging_player:
            if event.type == pygame.MOUSEMOTION:
                self.players[self.dragging_player]['x'], self.players[self.dragging_player]['y'] = event.pos
            elif event.type == pygame.MOUSEBUTTONUP:
                # Snap to closest square
                px, py = event.pos
                closest = 1
                min_dist = float('inf')
                for pos in range(1, 101):
                    x, y = self.get_board_coordinates(pos)
                    dist = math.hypot(px - x, py - y)
                    if dist < min_dist:
                        min_dist = dist
                        closest = pos
                self.players[self.dragging_player]['position'] = closest
                self.update_player_positions()
                self.dragging_player = None
                self.pending_move = False

    def run(self):
        """Main game loop"""
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
                    self.handle_mouse_event(event)
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        self.handle_click(event.pos)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and self.game_state == "playing":
                        self.roll_dice()
            
            # Clear screen
            self.screen.fill(LIGHT_BLUE)
            
            # Draw game elements
            if self.game_state in ["playing", "game_over"]:
                self.draw_board()
                self.draw_players()
            
            self.draw_ui()
            
            # Update display
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()


def main():
    """Main function to start the game"""
    game = EelsAndEscalatorsGUI()
    game.run()


if __name__ == "__main__":
    main()
