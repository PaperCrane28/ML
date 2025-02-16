import numpy as np
import random
import pygame
import sys
import time

#Q-Learning Implementation
class QLearningAgent:
    def __init__(self, state_space, action_space, learning_rate=0.1, discount_factor=0.9, epsilon=1.0, epsilon_decay=0.995, min_epsilon=0.01):
        self.state_space = state_space
        self.action_space = action_space
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.min_epsilon = min_epsilon
        self.q_table = np.zeros(state_space + (action_space,))

    def choose_action(self, state):
        if random.uniform(0, 1) < self.epsilon:
            return random.choice(range(self.action_space))
        return np.argmax(self.q_table[state])

    def update_q_values(self, state, action, reward, next_state):
        best_next_action = np.argmax(self.q_table[next_state])
        td_target = reward + self.discount_factor * self.q_table[next_state][best_next_action]
        td_error = td_target - self.q_table[state][action]
        self.q_table[state][action] += self.learning_rate * td_error

    def decay_epsilon(self):
        if self.epsilon > self.min_epsilon:
            self.epsilon *= self.epsilon_decay

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 400, 400
GRID_SIZE = 20
GRID_WIDTH, GRID_HEIGHT = SCREEN_WIDTH // GRID_SIZE, SCREEN_HEIGHT // GRID_SIZE

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

class SnakeGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.reset()

    def reset(self):
        self.snake = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = random.choice(['up', 'down', 'left', 'right'])
        self.food = self.spawn_food()
        self.score = 0

    def spawn_food(self):
        while True:
            food = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
            if food not in self.snake:
                return food

    def step(self, action):
        # Update direction based on action
        if action == 0 and self.direction != 'down':
            self.direction = 'up'
        elif action == 1 and self.direction != 'up':
            self.direction = 'down'
        elif action == 2 and self.direction != 'right':
            self.direction = 'left'
        elif action == 3 and self.direction != 'left':
            self.direction = 'right'

        # Move snake
        head = self.snake[0]
        if self.direction == 'up':
            new_head = (head[0], head[1] - 1)
        elif self.direction == 'down':
            new_head = (head[0], head[1] + 1)
        elif self.direction == 'left':
            new_head = (head[0] - 1, head[1])
        elif self.direction == 'right':
            new_head = (head[0] + 1, head[1])

        # Check for collision
        reward = -1
        if new_head[0] < 0 or new_head[0] >= GRID_WIDTH or new_head[1] < 0 or new_head[1] >= GRID_HEIGHT or new_head in self.snake:
            return -10, True

        self.snake.insert(0, new_head)
        if new_head == self.food:
            reward = 10
            self.food = self.spawn_food()
            self.score += 1
        else:
            self.snake.pop()

        return reward, False

    def render(self):
        self.screen.fill(WHITE)
        for segment in self.snake:
            pygame.draw.rect(self.screen, GREEN, pygame.Rect(segment[0] * GRID_SIZE, segment[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(self.screen, RED, pygame.Rect(self.food[0] * GRID_SIZE, self.food[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE))
        pygame.display.flip()

    def get_state(self):
        head = self.snake[0]
        state = [
            int(head[0] < self.food[0]),  # Food is to the right
            int(head[0] > self.food[0]),  # Food is to the left
            int(head[1] < self.food[1]),  # Food is below
            int(head[1] > self.food[1]),  # Food is above
            int(self.direction == 'up'),
            int(self.direction == 'down'),
            int(self.direction == 'left'),
            int(self.direction == 'right')
        ]
        return tuple(state)

# Main game loop
def main():
    game = SnakeGame()
    agent = QLearningAgent(state_space=(2, 2, 2, 2, 2, 2, 2, 2), action_space=4)

    episodes = 1000
    for episode in range(episodes):
        game.reset()
        state = game.get_state()
        total_reward = 0

        while True:
            action = agent.choose_action(state)
            reward, done = game.step(action)
            next_state = game.get_state()
            agent.update_q_values(state, action, reward, next_state)
            state = next_state
            total_reward += reward

            game.render()
            agent.decay_epsilon()

            #The waiting time between each step
            time.sleep(0.1)

            if done:
                break

        print(f"Episode {episode + 1}: Total Reward: {total_reward}")

if __name__ == "__main__":
    main()
    pygame.quit()
    sys.exit()