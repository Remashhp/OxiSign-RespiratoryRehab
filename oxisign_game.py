import pygame
import time

# ==========================================
# Project: OxiSign - Smart Respiratory Trainer
# Module: Main UI & Breath Simulation
# Description: Gamified interface for breathing exercises using Pygame.
#              Current version simulates sensor input via mouse.
# ==========================================

# --- Core Initialization ---
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("OxiSign - AI Respiratory Analysis")

# ==========================================
# 1. UI Configuration & Color Palette
# Note: Colors selected for medical calming effect (Color Psychology).
# ==========================================
WHITE = (255, 255, 255)
OFF_WHITE = (245, 245, 250) 
BLUE = (0, 120, 255)        # Primary Brand Color
DARK_BLUE = (0, 50, 150)    # Header Text
SKY_BLUE = (135, 206, 235)  # Background Environment
BALLOON_COLOR = (255, 100, 100) 
BASKET_COLOR = (139, 69, 19)
GREEN = (0, 180, 0)         # Success Indicators
RED = (200, 0, 0)           # Target/Alert Indicators
GRAY = (100, 100, 100)
LIGHT_GRAY = (220, 220, 220)

# ==========================================
# 2. Physics & Gameplay Mechanics
# [HACKATHON NOTE]: These values calibrate the difficulty.
# ==========================================
balloon_y = HEIGHT - 100
balloon_radius = 40

# Lift Power: Represents the sensitivity of the virtual sensor.
# [HARDWARE INTEGRATION]: This logic needs to be replaced by 
# real-time airflow data mapping (e.g., analog value 0-1023 -> lift 0.0-5.0).
lift_power = 0.8        

# Target Step: Distance the balloon travels per successful breath cycle.
target_step = 120       
current_target_y = balloon_y - target_step

# ==========================================
# 3. Therapeutic Timing Settings
# Note: Durations can be adjusted based on Patient's COPD stage.
# ==========================================
INHALE_DURATION = 4.0    # Preparation phase (Rest)
EXHALE_DURATION = 10.0   # Active exertion phase (Blow)

# State Machine Constants
INHALE_PHASE = 0
EXHALE_PHASE = 1
current_phase = INHALE_PHASE
phase_start_time = time.time()

# ==========================================
# 4. Session Control
# ==========================================
REQUIRED_REPS = 3       # Total cycles for this session
current_reps = 0
game_finished = False

# Font Initialization for UI Elements
font_header = pygame.font.Font(None, 50)
font_label = pygame.font.Font(None, 35)
font_value = pygame.font.Font(None, 40)
font_small = pygame.font.Font(None, 28)

def draw_balloon(surface, x, y, radius):
    """
    Renders the balloon asset at the current physics position.
    """
    pygame.draw.circle(surface, BALLOON_COLOR, (x, int(y)), radius)
    basket_width = radius
    basket_height = radius // 2
    basket_x = x - basket_width // 2
    basket_y = y + radius + 10
    pygame.draw.rect(surface, BASKET_COLOR, (basket_x, int(basket_y), basket_width, basket_height))
    # Ropes
    pygame.draw.line(surface, GRAY, (x - radius//2, y + radius*0.8), (basket_x + 5, basket_y), 2)
    pygame.draw.line(surface, GRAY, (x + radius//2, y + radius*0.8), (basket_x + basket_width - 5, basket_y), 2)

def draw_result_card(surface, x, y, label, value, color):
    """
    Helper function to draw UI cards for the final dashboard.
    """
    pygame.draw.rect(surface, WHITE, (x, y, 300, 80), border_radius=10)
    pygame.draw.rect(surface, LIGHT_GRAY, (x, y, 300, 80), 2, border_radius=10)
    lbl_surf = font_label.render(label, True, GRAY)
    val_surf = font_value.render(value, True, color)
    surface.blit(lbl_surf, (x + 15, y + 15))
    surface.blit(val_surf, (x + 15, y + 45))

# ==========================================
# Main Application Loop
# ==========================================
running = True
clock = pygame.time.Clock()

while running:
    # Event Handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if not game_finished:
        # Determine active duration based on state
        if current_phase == INHALE_PHASE:
            current_duration = INHALE_DURATION
        else:
            current_duration = EXHALE_DURATION

        elapsed_time = time.time() - phase_start_time
        time_left = max(0, current_duration - elapsed_time)

        # --- Game Logic & State Management ---
        if current_phase == INHALE_PHASE:
            instruction_text = "INHALE (Relax...)" 
            phase_color = BLUE
            
            # Transition to Exhale when timer ends
            if time_left == 0:
                current_phase = EXHALE_PHASE
                phase_start_time = time.time()
                # Update next target height
                current_target_y = max(100, balloon_y - target_step)

        elif current_phase == EXHALE_PHASE:
            instruction_text = "EXHALE (Blow Steady...)"
            phase_color = GREEN
            
            # ---------------------------------------------------------
            # [HARDWARE TODO]: INPUT SENSOR INTEGRATION
            # Currently: Simulating airflow using Mouse Click (Left Button).
            # Future: Replace with `sensor_value = serial.read()`
            # ---------------------------------------------------------
            is_blowing = pygame.mouse.get_pressed()[0] 
            
            if is_blowing and balloon_y > current_target_y:
                balloon_y -= lift_power # Apply lift
            
            # Check for cycle completion
            cycle_done = False
            if balloon_y <= current_target_y + 2: # Tolerance margin
                balloon_y = current_target_y
                cycle_done = True
            elif time_left == 0:
                # Timeout logic can be added here (e.g., "Try Again")
                cycle_done = True

            if cycle_done:
                current_reps += 1
                if current_reps >= REQUIRED_REPS:
                    game_finished = True
                else:
                    # Loop back to Inhale phase
                    current_phase = INHALE_PHASE
                    phase_start_time = time.time()

        # --- Rendering / Drawing ---
        screen.fill(SKY_BLUE)
        
        # Draw Target Line only during active phase
        if current_phase == EXHALE_PHASE:
            pygame.draw.line(screen, RED, (0, current_target_y), (WIDTH, current_target_y), 3)
            target_label = font_small.render("Target Line", True, RED)
            screen.blit(target_label, (WIDTH - 150, current_target_y - 25))

        draw_balloon(screen, WIDTH // 2, balloon_y, balloon_radius)
        
        # UI Overlays
        timer_text = font_header.render(f"{time_left:.1f} s", True, phase_color)
        instr_label = font_value.render(instruction_text, True, phase_color)
        
        # Center elements
        screen.blit(instr_label, (WIDTH // 2 - instr_label.get_width() // 2, 50))
        screen.blit(timer_text, (WIDTH // 2 - timer_text.get_width() // 2, 100))
        
        reps_text = font_small.render(f"Reps: {current_reps} / {REQUIRED_REPS}", True, GRAY)
        screen.blit(reps_text, (20, 20))

    else:
        # ==========================================
        # AI Dashboard & Results
        # Description: Displays analysis after session completion.
        # ==========================================
        screen.fill(OFF_WHITE)
        
        title = font_header.render("AI Session Analysis", True, DARK_BLUE)
        subtitle = font_small.render("Based on airflow sensors & deep learning model", True, GRAY)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 40))
        screen.blit(subtitle, (WIDTH // 2 - subtitle.get_width() // 2, 80))

        # ---------------------------------------------------------
        # [INTEGRATION TODO]: MOCK DATA
        # These values are currently hardcoded for the demo.
        # Connect to the trained ML model to fetch real metrics.
        # ---------------------------------------------------------
        
        # Card 1: Breath Strength (Flow Rate)
        draw_result_card(screen, 80, 150, "Avg Breath Strength", "88% (Strong)", GREEN)
        
        # Card 2: Stability (Variance in flow)
        draw_result_card(screen, 80, 250, "Flow Stability", "94% (Steady)", BLUE)
        
        # Card 3: Volumetric Analysis
        draw_result_card(screen, 420, 150, "Lung Capacity Used", "2.1 Liters", DARK_BLUE)
        
        # Card 4: Physiological Feedback
        draw_result_card(screen, 420, 250, "Chest Expansion", "+5.2% Improved", GREEN) 

        # Footer / Final Recommendation
        pygame.draw.line(screen, LIGHT_GRAY, (50, 360), (750, 360), 2)
        
        final_verdict = font_value.render("Overall Health Status: EXCELLENT", True, DARK_BLUE)
        recommendation = font_small.render("Recommendation: Maintain current exercise level.", True, GRAY)
        
        screen.blit(final_verdict, (WIDTH // 2 - final_verdict.get_width() // 2, 400))
        screen.blit(recommendation, (WIDTH // 2 - recommendation.get_width() // 2, 440))

        # Decorative Element
        draw_balloon(screen, WIDTH // 2, 530, 30)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()