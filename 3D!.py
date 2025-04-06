import pygame, math, random

pygame.init()
pixels = [1000, 1000]

screen = pygame.display.set_mode(pixels)
pygame.display.set_caption("3D!")

clock = pygame.time.Clock()
tick = 60

move_speed = 0.3
rotation_speed = 1 / math.pi / 50
playerPos = [0, 0, -5, 0, 0]


class projection:
    def __init__(self, fov=math.pi / 2):
        self.fov = fov
        self.projDistance = 1000 / math.tan(self.fov / 2)

    def project(self, pos, dx=0.1): # pos = [x,y,z] where pos is normalized
        if pos[2] == 0:
            pos[2] = dx
        return (self.projDistance / abs(pos[2]) * pos[0],
                self.projDistance / abs(pos[2]) * pos[1])

    @staticmethod
    def rotate_x(point, theta):
        y_new = point[1] * math.cos(theta) - point[2] * math.sin(theta)
        z_new = point[1] * math.sin(theta) + point[2] * math.cos(theta)
        return [point[0], y_new, z_new]

    @staticmethod
    def rotate_y(point, theta):
        x_new = point[0] * math.cos(theta) + point[2] * math.sin(theta)
        z_new = -point[0] * math.sin(theta) + point[2] * math.cos(theta)
        return [x_new, point[1], z_new]

    @staticmethod
    def normalized(pos = (0,0,0)):
        x, y, z = pos
        normalizedPos = [x - playerPos[0], y - playerPos[1], z - playerPos[2]]
        normalizedPos = projection.rotate_y(normalizedPos, playerPos[3])
        normalizedPos = projection.rotate_x(normalizedPos, playerPos[4])
        return normalizedPos


proj = projection()


class line:
    def __init__(self, start, end):
        self.x1, self.y1, self.z1 = start
        self.x2, self.y2, self.z2 = end

    def show(self):
        p1 = [self.x1, self.y1, self.z1]
        p2 = [self.x2, self.y2, self.z2]
        normP1 = projection.normalized(p1)
        normP2 = projection.normalized(p2)

        if normP1[2] <= 0 and normP2[2] <= 0:
            return
        if normP1[2] <= 0 or normP2[2] <= 0:
            normP1, normP2 = self.cutLine(normP1, normP2)

        proj_p1 = proj.project(normP1)
        proj_p2 = proj.project(normP2)

        px1, py1 = proj_p1
        px2, py2 = proj_p2
        pygame.draw.line(screen, (0, 0, 0), [px1 + pixels[0] / 2, -py1 + pixels[1] / 2],
                         [px2 + pixels[0] / 2, -py2 + pixels[1] / 2], 1)

    @staticmethod
    def cutLine(P1,P2,dx = 0.1):
        x1,y1,z1 = P1 ; x2,y2,z2 = P2
        # as z1!=z2, ZeroDivisionError will not be raised
        a1 = (x1-x2)/(z1-z2)
        a2 = (y1-y2)/(z1-z2)
        fx = lambda z: a1*(z-z1) + x1
        fy = lambda z: a2*(z-z1) + y1
        if z1<0:
            return [fx(dx), fy(dx), dx], P2
        if z2<0:
            return P1, [fx(dx),fy(dx),dx]

lines = [] # list of lines to show

class triangle(line):
    def __init__(self,P1,P2,P3):
        self.P1 = P1
        self.P2 = P2
        self.P3 = P3

class cube(line):
    def __init__(self,x,y,z,length):
        self.x = x
        self.y = y
        self.z = z
        self.length = length
        offsets = [(-0.5, -0.5, -0.5), (-0.5, -0.5, 0.5), (-0.5, 0.5, -0.5), (-0.5, 0.5, 0.5),
                   (0.5, -0.5, -0.5), (0.5, -0.5, 0.5), (0.5, 0.5, -0.5), (0.5, 0.5, 0.5)]

        # Create lines between all combinations of points that form the edges of the cube
        edge_indices = [(0, 1), (0, 2), (0, 4), (1, 3), (1, 5), (2, 3),
                        (2, 6), (3, 7), (4, 5), (4, 6), (5, 7), (6, 7)]

        for start, end in edge_indices:
            start_point = (self.x + self.length * offsets[start][0],
                           self.y + self.length * offsets[start][1],
                           self.z + self.length * offsets[start][2])
            end_point = (self.x + self.length * offsets[end][0],
                         self.y + self.length * offsets[end][1],
                         self.z + self.length * offsets[end][2])
            lines.append(line(start_point, end_point))



stop = False

for i in range(5):
    for j in range(5):
        cube(i,random.randint(-1,1), j, 1)

while not stop:
    pygame.mouse.set_pos([500, 500])
    pygame.mouse.get_rel()
    pygame.mouse.set_visible(False)

    
    clock.tick(tick)
    for event in pygame.event.get():
        keys = pygame.key.get_pressed()
        if event.type == pygame.QUIT or keys[pygame.K_ESCAPE]:
            stop = True
            try:
                pygame.quit()
            except:
                pass
        rx, ry = pygame.mouse.get_rel()
        playerPos[3] -= rx * rotation_speed
        if -math.pi / 2 <= playerPos[4] - ry * rotation_speed <= math.pi / 2:
            playerPos[4] -= ry * rotation_speed

        if keys[pygame.K_a]:
            playerPos[0] -= math.cos(playerPos[3]) * move_speed
            playerPos[2] -= math.sin(playerPos[3]) * move_speed
        if keys[pygame.K_d]:
            playerPos[0] += math.cos(playerPos[3]) * move_speed
            playerPos[2] += math.sin(playerPos[3]) * move_speed
        if keys[pygame.K_w]:
            playerPos[0] += -math.sin(playerPos[3]) * move_speed
            playerPos[2] += math.cos(playerPos[3]) * move_speed
        if keys[pygame.K_s]:
            playerPos[0] -= -math.sin(playerPos[3]) * move_speed
            playerPos[2] -= math.cos(playerPos[3]) * move_speed
        if keys[pygame.K_SPACE]:
            playerPos[1] += move_speed
        if keys[pygame.K_LSHIFT]:
            playerPos[1] -= move_speed

    screen.fill((255, 255, 255))

    for i in lines:
        i.show()

    pygame.display.flip()
