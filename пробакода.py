import pygame
import math


WIDTH, HEIGHT = 1000, 800
FPS = 60
SEGMENT_DISTANCE = 15  
NUM_SEGMENTS = 40      
RIB_WIDTH = 40         


BLACK = (0, 0, 0)
WHITE = (220, 220, 220)

class SkeletonNode:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 0

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Скелет следует за курсором")
    clock = pygame.time.Clock()

    
    segments = [SkeletonNode(WIDTH // 2, HEIGHT // 2) for _ in range(NUM_SEGMENTS)]

    running = True
    while running:
        screen.fill(BLACK)
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

       
        segments[0].x = mouse_pos[0]
        segments[0].y = mouse_pos[1]

        for i in range(1, NUM_SEGMENTS):
            dx = segments[i-1].x - segments[i].x
            dy = segments[i-1].y - segments[i].y

            
            angle = math.atan2(dy, dx)
            segments[i].angle = angle

            
            dist = math.hypot(dx, dy)
            if dist > SEGMENT_DISTANCE:
                segments[i].x = segments[i-1].x - math.cos(angle) * SEGMENT_DISTANCE
                segments[i].y = segments[i-1].y - math.sin(angle) * SEGMENT_DISTANCE

        
        for i in range(NUM_SEGMENTS):
            curr = segments[i]

           
            if i < NUM_SEGMENTS - 1:
                nxt = segments[i+1]
                pygame.draw.line(screen, WHITE, (curr.x, curr.y), (nxt.x, nxt.y), 2)

           
            rib_len = max(5, RIB_WIDTH * (1 - i / NUM_SEGMENTS))

            
            perp_angle = curr.angle + math.pi / 2

            start_rib_x = curr.x + math.cos(perp_angle) * rib_len
            start_rib_y = curr.y + math.sin(perp_angle) * rib_len
            end_rib_x = curr.x - math.cos(perp_angle) * rib_len
            end_rib_y = curr.y - math.sin(perp_angle) * rib_len

            pygame.draw.line(screen, WHITE, (start_rib_x, start_rib_y), (end_rib_x, end_rib_y), 1)

            
            if i % 6 == 0 and i > 0 and i < NUM_SEGMENTS - 10:
                leg_len = rib_len * 1.5
                for side in [-1, 1]:
                    
                    knee_angle = perp_angle * side + (math.sin(pygame.time.get_ticks() * 0.005 + i) * 0.5)
                    knee_x = curr.x + math.cos(perp_angle * side) * rib_len
                    knee_y = curr.y + math.sin(perp_angle * side) * rib_len

                    foot_x = knee_x + math.cos(perp_angle * side + 0.5) * leg_len
                    foot_y = knee_y + math.sin(perp_angle * side + 0.5) * leg_len

                    
                    pygame.draw.lines(screen, WHITE, False, [(curr.x, curr.y), (knee_x, knee_y), (foot_x, foot_y)], 1)
                    
                    pygame.draw.circle(screen, WHITE, (int(foot_x), int(foot_y)), 2)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()