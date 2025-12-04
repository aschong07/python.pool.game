# 2D Pool Game – ECE160 Final Project

**OVERVIEW:**

This project is a 2D pool game built in Python using Pygame for an ECE160 final project.
It simulates a simplified game of 8-ball with:

-Player vs Player(local multiplayer)
-Player VS AI (Easy & Hard)
-Basic pool physics (bounces,friction, ball collisions)
-Pocket detection and win/lose conditions
-Simple UI, mmenu system, and a win screen with confetti animation

All logic (physics, rules, AI, and UI) is implemented manually in python without any external game engine beyong Pygame.

---

**FEATURES**

**Game Modes:**

- **Player vs Player (PvP)**
  - Two human players share one keyboard/mouse.
  - Each player enters their name at the start.
  - First legal potted ball assigns solids vs stripes.
  - Turn continues if you pot your own ball; turn switches on a miss or foul.

- **Player vs AI**
  - Human is Player 1 ("YOU") and AI (Easy Ai or Hard AI)
  - AI only shoots when all balls are stopped.
  - AI follows the same rules (fouls, ball-in-hand, 8-ball rules).

---

**Table, Balls & Physics**

- Rectangular table with defined playable bounds and a colored surface.
- Six Pockets:
  - Top: left, middle, right  
  - Bottom: left, middle, right
- 16 total balls:
  - 1 cue ball (white)
  - 7 solid balls (various colors)
  - 7 striped balls (same colors with a stripe)
  - 1 black 8-ball (center of the rack)
- Physics:
  - Velocity-based movement
  - Wall bounces with velocity inversion
  - Friction that gradually slows balls and snaps very small velocities to zero
  - Ball–ball collisions using elastic collision math and overlap resolution

---

**AI (Easy & Hard)**

-Easy AI
  - Picks a random valid target from its group (or any ball on an open table)
  - Adds random error to its shot angle and uses moderate power
  - Intentionally imprecise to feel “easy”

- Hard AI
  - Picks a target ball
  - Chooses the **closest pocket** for that ball
  - Calculates a **ghost-ball position** so the cue ball hits the object ball at the right angle toward that pocket
  - Uses higher power with less randomness to simulate a stronger opponent

The AI obeys:
- Turn rules (switching on misses and fouls)
- Group ownership (solids vs stripes)
- 8-ball conditions (only aims at 8-ball when group is cleared)

---

**Pocket Detection & Rules**

- For each ball and each pocket, the game checks the distance:
  - If `distance(ball, pocket) < pocket_radius`, the ball is considered pocketed.
- Behavior when pocketed:
  - **Cue ball** → scratch: moved off-screen, velocity cleared, opponent gets **ball in hand**.
  - **Solid / Stripe** → ball’s `alive` flag set to `False`, and type recorded (`"solid"` or `"stripe"`).
  - **8-ball** → game checks whether the current player has cleared all their group balls to determine win/loss.
- A list `potted_this_turn` records what was sunk during a single turn and is used to:
  - Assign groups on an open table (first legal pot)
  - Decide whether a turn continues or switches
  - Detect fouls and early 8-ball pots
  - Trigger the win screen

---

**UI & UX**

- **Main Menu**
  - “Play vs AI”
  - “Freeplay (PvP)”
  - AI difficulty selection: Easy / Hard
- **In-Game UI**
  - Top-center text:
    - Current player name
    - Group (Solids/Stripes) when assigned
    - Extra instructions like “(Place Cue Ball)” on ball-in-hand
  - Display of:
    - `Player 1: Solids | Player 2: Stripes` once groups are set
  - Buttons:
    - **Menu** – return to main menu
    - **Quit** – exit game
- **Cue UI**
  - Cue stick rotates around the cue ball based on mouse position.
  - Power is proportional to the distance from the cue ball to the mouse.
  - A power label (`Power: XX%`) appears near the cue ball.
  - A short **strike animation** plays before the cue ball is launched.
- **Win Screen**
  - Dark overlay over the table
  - “YOU WIN!” gold text with drop shadow
  - Winner’s name displayed (e.g., “Player 1 win!”)
  - Confetti particle system
  - Press ENTER, ESC, or click to return to menu

---

## Controls

- **Mouse Movement** – Aim the cue (when it’s your turn and the cue ball is stopped).
- **Left Mouse Click**
  - When aiming: triggers the cue strike (shoots the cue ball).
  - When cue ball is in hand: place the cue ball at the clicked location (if valid).
- **ESC / Window Close Button**
  - In game: handled through menu/quit buttons and win screen input.
  - On win screen: returns to menu or quits depending on context.

---
**FILE/CODE STRUCTURE**

All code is in a single Python file_ (e.g., `pool_game.py`) and is organized into logical sections:

- **Global Setup**
  - Pygame initialization, window, FPS, colors
  - Table bounds and pocket coordinates
  - Global constants (ball radius, friction, power multiplier, etc.)

- **Classes**
  - `Ball` – handles position, velocity, drawing, and movement with wall collisions.
  - `Cue` – handles aiming, power, strike animation, and converting power/angle to velocity.
  - `Confetti` – used for the win screen celebration particles.
  - `Button` – general-purpose UI button used in menus and in-game.

- **Core Functions**
  - `create_balls()` – creates the cue ball and racks the 15 object balls in a triangle with the 8-ball in the center.
  - `check_collisions(balls, cue_ball_in_hand)` – ball–ball collision resolution with elastic physics.
  - `check_pockets(balls)` – checks for any balls that have fallen into pockets and returns what was potted.
  - `get_ai_shot(balls, difficulty, my_group)` – calculates AI shot angle and power based on difficulty and group.
  - `ai_place_ball(balls)` – places the cue ball in a valid location after a foul during AI’s ball-in-hand.
  - `check_win_condition(balls, player_group)` – determines if a player has legally won (all group balls cleared + 8-ball).
  - `show_win_screen(screen, winner_name, confetti_particles)` – handles the victory screen and confetti animation.
  - `menu()` – handles the main menu and AI difficulty selection, returns configuration for the game.
  - `run_game(config)` – main game loop: updates physics, UI, turns, rules, AI, and win conditions.
  - `main()` – wrapper loop that lets the player return to the menu and replay or quit.

---

## How to Run

### Requirements

- **Python 3.8+** (recommended)
- **Pygame**

Install Pygame with git bash insert command:
pip install pygame
