import pygame, math, random, time, copy
pygame.init()

random.seed(time.time())
#Window Settings
size = [600,900]
blocksize = size[1]/25
screen = pygame.display.set_mode(size,pygame.RESIZABLE)
pygame.display.set_caption("Pytris")

bag = ["i","j","l","o","s","t","z"]
_next : list = []
#Scores
score : int = 0
btb : int = 0
combo : int = 0
placed : int = 0
raiseCombo : int = 0
raiseBtb : int = 0
sdf : int = 1
show_text : int = 0
show_type : int = ""

wait : int = 0

tick : int = 100

#Sounds
minoPlace = pygame.mixer.Sound("tetris\\resources\\minoPlace.mp3")
minoMove = pygame.mixer.Sound("tetris\\resources\\minoMove.mp3")
minoRotate = pygame.mixer.Sound("tetris\\resources\\minoRotate.mp3")
minoKickRotateFail = pygame.mixer.Sound("tetris\\resources\\minoRotateFail.mp3")
Tspin = pygame.mixer.Sound("tetris\\resources\\Tspin.mp3")

perfectClear = pygame.mixer.Sound("tetris\\resources\\perfectClear.mp3")

lineErase = pygame.mixer.Sound("tetris\\resources\\lineErase.mp3")
bigAttack = pygame.mixer.Sound("tetris\\resources\\bigAttack.mp3")

combo1,combo2 = pygame.mixer.Sound("tetris\\resources\\combo1.mp3"), pygame.mixer.Sound("tetris\\resources\\combo2.mp3")
combo3,combo4 = pygame.mixer.Sound("tetris\\resources\\combo3.mp3"), pygame.mixer.Sound("tetris\\resources\\combo4.mp3")
combo5,combo6 = pygame.mixer.Sound("tetris\\resources\\combo5.mp3"), pygame.mixer.Sound("tetris\\resources\\combo6.mp3")
bigCombo = pygame.mixer.Sound("tetris\\resources\\bigCombo.mp3")

minoHold = pygame.mixer.Sound("tetris\\resources\\minoHold.mp3")

gameOver = pygame.mixer.Sound("tetris\\resources\\gameOver.mp3")
restart = pygame.mixer.Sound("tetris\\resources\\restart.mp3")



#First Bag Randomizer
for i in range(5):
    picked = random.choice(bag)
    _next.append(picked)
    bag.remove(picked)

def drawBlock(x, y, color, blockSize=blocksize, edge=1, edgeColor=(0, 0, 0), onlyEdge=False):
    block = [blockSize*x,(23-y)*blockSize,blockSize,blockSize]
    if not onlyEdge:
        pygame.draw.rect(screen, color, block, 0)
    pygame.draw.rect(screen, edgeColor, block, edge)

def makeGrid(color, width, blockSize=blocksize):
    for i in range(25):
        pygame.draw.line(screen, color, [0, blockSize*i], [blockSize*10, blockSize*i], width)
    for i in range(11):
        pygame.draw.line(screen, color,[i*blockSize,0],[i*blockSize, 24*blockSize], width)

def draw_shadow(mino, field):
    # Calculate the maximum drop distance
    max_drop = calculate_max_drop(mino, field)
    
    # Draw the shadow piece at the maximum drop position
    for x, y in mino.state:
        if mino.minoType=="i":
            drawBlock(x, y - max_drop, color=(0,0,0), edgeColor=(72,209,204), onlyEdge=True)
        if mino.minoType=="j":
            drawBlock(x, y - max_drop, color=(0,0,0), edgeColor=(106,90,205), onlyEdge=True)
        if mino.minoType=="l":
            drawBlock(x, y - max_drop, color=(0,0,0), edgeColor=(255,140,0), onlyEdge=True)
        if mino.minoType=="o":
            drawBlock(x, y - max_drop, color=(0,0,0), edgeColor=(230,230,20), onlyEdge=True)
        if mino.minoType=="s":
            drawBlock(x, y - max_drop, color=(0,0,0), edgeColor=(173,255,47), onlyEdge=True)
        if mino.minoType=="t":
            drawBlock(x, y - max_drop, color=(0,0,0), edgeColor=(138,43,226), onlyEdge=True)
        if mino.minoType=="z":
            drawBlock(x, y - max_drop, color=(0,0,0), edgeColor=(220,20,60), onlyEdge=True)

def calculate_max_drop(mino, field):
    max_drop = len(field.stacked)  # Start with the maximum possible drop (grid height)
    
    # Check each block in the Tetrmino to determine the lowest safe drop
    for x, y in mino.state:
        drop_distance = 0
        while (y - drop_distance > 0) and not field.stacked[y - drop_distance - 1][x]:
            drop_distance += 1
        max_drop = min(max_drop, drop_distance)
    
    return max_drop

def pickMino():
    global bag, _next
    
    if len(bag) != 0:
        picked = random.choice(bag)
        _next.append(picked)
        bag.remove(picked)
        return _next.pop(0)
    
    bag = ["i","j","l","o","s","t","z"]
    picked = random.choice(bag)
    _next.append(picked)
    bag.remove(picked)
    
    return _next.pop(0)

class tetrminos:
    kicktable = [[(0, 0),(-1, 0),(-1,+1),( 0,-2),(-1,-2)],[(0, 0),(+1, 0),(+1,-1),( 0,+2),(+1,+2)],
                 [( 0, 0),(+1, 0),(+1,-1),( 0,+2),(+1,+2)],[( 0, 0),(-1, 0),(-1,+1),( 0,-2),(-1,-2)],
                 [(0, 0),(+1, 0),(+1,+1),( 0,-2),(+1,-2)],[( 0, 0),(-1, 0),(-1,-1),( 0,+2),(-1,+2)],
                 [( 0, 0),(-1, 0),(-1,-1),( 0,+2),(-1,+2)],[(0, 0),(+1, 0),(+1,+1),( 0,-2),(+1,-2)]]
    Ikicktable = [[( 0, 0),(-2, 0),(+1, 0),(-2,-1),(+1,+2)],[( 0, 0),(+2, 0),(-1, 0),(+2,+1),(-1,-2)],
                  [( 0, 0),(-1, 0),(+2, 0),(-1,+2),(+2,-1)],[( 0, 0),(+1, 0),(-2, 0),(+1,-2),(-2,+1)],
                  [( 0, 0),(+2, 0),(-1, 0),(+2,+1),(-1,-2)],[( 0, 0),(-2, 0),(+1, 0),(-2,-1),(+1,+2)],
                  [( 0, 0),(+1, 0),(-2, 0),(+1,-2),(-2,+1)],[( 0, 0),(-1, 0),(+2, 0),(-1,+2),(+2,-1)]]
    kicktable180 = [[(0,0),(0,1),(1,1),(-1,1),(1,0),(-1,0)],
                    [(0,0),(0,-1),(-1,-1),(1,-1),(-1,0),(1,0)],
                    [(0,0),(1,0),(1,2),(1,1),(0,2),(0,1)],
                    [(0,0),(-1,0),(-1,2),(-1,1),(0,2),(0,1)]]
    SRSstate = {"i" : [ [ (4,21),(3,21),(5,21),(6,21)], [ (4,21),(4,22),(4,20),(4,19) ], [ (4,21),(2,21),(3,21),(5,21) ],[ (4,21),(4,20),(4,22),(4,23) ] ],
                "j" : [ [ (4,21),(3,21),(5,21),(3,22) ], [ (4,21),(4,22),(5,22),(4,20) ], [ (4,21),(3,21),(5,21),(5,20) ], [ (4,21),(4,22),(4,20),(3,20) ] ],
                "l" : [ [ (4,21),(5,21),(3,21),(5,22) ], [ (4,21),(4,22),(4,20),(5,20) ], [ (4,21),(3,21),(5,21),(3,20) ], [ (4,21),(4,20),(4,22),(3,22) ] ],
                "o" : [ [ (4,21),(5,21),(4,22),(5,22) ], [ (4,21),(5,21),(4,22),(5,22) ], [ (4,21),(5,21),(4,22),(5,22) ], [ (4,21),(5,21),(4,22),(5,22) ] ],
                "s" : [ [ (4,21),(3,21),(4,22),(5,22) ], [ (4,21),(4,22),(5,21),(5,20) ], [ (4,21),(5,21),(4,20),(3,20) ], [ (4,21),(3,21),(3,22),(4,20) ] ],
                "t" : [ [ (4,21),(3,21),(5,21),(4,22) ], [ (4,21),(4,22),(4,20),(5,21) ], [ (4,21),(3,21),(5,21),(4,20) ], [ (4,21),(4,22),(4,20),(3,21) ] ],
                "z" : [ [(4,21),(4,22),(3,22),(5,21) ], [ (4,21),(5,21),(5,22),(4,20) ], [ (4,21),(3,21),(4,20),(5,20) ], [ (4,21),(4,22),(3,20),(3,21) ] ] }
    hold=""
    tspined=False
    mTspined=False
    def __init__(self, minoType, rotate=0):
        self.minoType=minoType
        self.rotate = rotate
        self.block = copy.deepcopy(tetrminos.SRSstate[minoType])
        self.state = copy.deepcopy(self.block[self.rotate])
        
    def update(self):
        for i in self.state:
            x,y=i
            if self.minoType=="i":
                drawBlock(x,y,(72,209,204), edgeColor=(62,199,194))
            if self.minoType=="j":
                drawBlock(x,y,(106,90,205), edgeColor=(96,80,195))
            if self.minoType=="l":
                drawBlock(x,y,(255,140,0), edgeColor=(245,130,0))
            if self.minoType=="o":
                drawBlock(x,y,(230,230,20), edgeColor=(220,220,10))
            if self.minoType=="s":
                drawBlock(x,y,(173,255,47), edgeColor=(163,245,37))
            if self.minoType=="t":
                drawBlock(x,y,(138,43,226), edgeColor=(128,33,216))
            if self.minoType=="z":
                drawBlock(x,y,(220,20,60), edgeColor=(210,10,50))

    def turn(self, n): #if n==0->left, n==1->right, n==2->180
        global wait
        failed=False
        temp=copy.deepcopy(self.rotate)
        if n==0:
            self.rotate +=-1
        if n==1:
            self.rotate +=1
        if n==2:
            self.rotate += 2
        self.rotate = self.rotate%4

        for i in range(5):
            if self.minoType == "i":

                if n != 2:
                    kick=self.Ikicktable[2*((self.rotate-n)%4)-n+1][i]
                else:
                    kick=self.kicktable180[(self.rotate-2)%4][i]

            else:
                if n != 2:
                    kick=self.kicktable[2*((self.rotate-n)%4)-n+1][i]
                else:
                    kick=self.kicktable180[(self.rotate-2)%4][i]

            x,y=kick
            self.state = self.block[self.rotate]

            for x1,y1 in self.state:
                if not 0<=x1+x<=9 or not 0<=y1+y:
                    failed=True
                    break

                if field.stacked[y1+y][x1+x]:
                    failed=True
                    break

            if failed==True:
                failed=False

                if i==4:
                    self.rotate=temp
                    self.state = self.block[self.rotate]
                    minoKickRotateFail.play()
                    return 0

                continue

            else:
                wait=1
                minoRotate.play()

                for i in range(4):
                    for j in range(4):
                        x1,y1 = self.block[i][j]
                        self.block[i][j] = (x1+x,y1+y)

                self.state = self.block[self.rotate]
                if self.minoType == "t":
                    tx,ty = self.state[0]
                    tspinCount=0

                    for tx1, ty1 in [(-1,-1),(1,-1),(-1,1),(1,1)]:

                        if not 0<=ty+ty1<=9 or not 0<=tx+tx1<=9 or field.stacked[ty+ty1][tx+tx1]:
                            tspinCount+=1

                    mtx,mty=self.state[3]

                    if self.rotate%2==0:

                        if (not 0<=mtx+1<=9 or field.stacked[mty][mtx+1]) and (not 0<=mtx-1<=9 or field.stacked[mty][mtx-1]):

                            if tspinCount>=3:
                                tetrminos.tspined=True
                                Tspin.play()
                                print("tspin")

                        else:
                            if (not 0<=mtx+1<=9 or field.stacked[mty][mtx+1]) or (not 0<=mtx-1<=9 or field.stacked[mty][mtx-1]):

                                if tspinCount>=3:

                                    tetrminos.mTspined=True
                                    Tspin.play()
                                    print("mini-tspin")
                                
                    else:

                        if field.stacked[mty+1][mtx] and (mty-1<0 or field.stacked[mty-1][mtx]):

                            if tspinCount>=3:

                                tetrminos.tspined=True
                                Tspin.play()
                                print("tspin")

                        else:

                            if field.stacked[mty+1][mtx] or (mty-1<0 or field.stacked[mty-1][mtx]):

                                if tspinCount>=3:

                                    tetrminos.mTspined=True
                                    Tspin.play()
                                    print("min-tspin")

                    if not (self.tspined or self.mTspined):
                        minoRotate.play()

                return 0

    def move(self,n): # Right=1,Left=0
        global wait
        minoMove.play()
        for i in range(4):
            x1,y1 = self.state[i]
            if not 0<=x1+2*n-1<=9 or field.stacked[y1][x1+2*n-1]:
                return -1

        wait=1
        for i in range(4):
            for j in range(4):
                x1,y1 = self.block[i][j]
                self.block[i][j] = (x1+2*n-1,y1)
                self.state = self.block[self.rotate]

    def holdmino(self):
        global bag,_next
        temp = copy.deepcopy(tetrminos.hold)
        tetrminos.hold = self.minoType
        del self

        if temp == "":
            mino1.minoType = _next[0]
            mino1.rotate = 0
            mino1.block = copy.deepcopy(tetrminos.SRSstate[mino1.minoType])
            mino1.state = copy.deepcopy(mino1.block[mino1.rotate])

            if len(bag) != 0:
                picked = random.choice(bag)
                _next.append(picked)
                bag.remove(picked)
                _next.pop(0)

            else:
                bag = ["i","j","l","o","s","t","z"]
                picked = random.choice(bag)
                _next.append(picked)
                bag.remove(picked)
                _next.pop(0)

        else:
            mino1.minoType = temp
            mino1.rotate = 0
            mino1.block = copy.deepcopy(tetrminos.SRSstate[mino1.minoType])
            mino1.state = copy.deepcopy(mino1.block[mino1.rotate])
        mino1.state = mino1.block[mino1.rotate]
                    


class field:
    stacked = [ [0 for x in range(10) ] for y in range(25) ]
    gravity=0.1
    count = 0
    def __init__(self):
        pass
    
    def update(self):
        global placed

        lineErased = 0
        erased=1
        toErase = []

        for i in range(len(self.stacked)):
            for j in range(len(self.stacked[i])):
                if self.stacked[i][j]=="i":
                    drawBlock(j,i,(72,209,204), edgeColor=(62,199,194))
                elif self.stacked[i][j]=="j":
                    drawBlock(j,i,(106,90,205), edgeColor=(96,80,195))
                elif self.stacked[i][j]=="l":
                    drawBlock(j,i,(255,140,0), edgeColor=(245,130,0))
                elif self.stacked[i][j]=="o":
                    drawBlock(j,i,(230,230,20), edgeColor=(220,220,10))
                elif self.stacked[i][j]=="s":
                    drawBlock(j,i,(173,255,47), edgeColor=(163,245,37))
                elif self.stacked[i][j]=="t":
                    drawBlock(j,i,(138,43,226), edgeColor=(128,33,216))
                elif self.stacked[i][j]=="z":
                    drawBlock(j,i,(220,20,60), edgeColor=(210,10,50))
                elif self.stacked[i][j]=="garbage":
                    drawBlock(j,i,(128,128,128), edgeColor=(118,118,118))
                else:
                    erased*=0

            if erased:
                lineErased+=1
                toErase.append(i)
                self.stacked.append([0 for x in range(10)])

            erased=1
        for idx,i in enumerate(toErase):
            self.stacked.pop(i-idx)
        if placed:
            self.scoring(lineErased)

    def scoring(self,lineErased):
        global score
        global btb, combo, raiseCombo, raiseBtb
        global show_text, show_type
        global placed
        if lineErased == 0:
            minoPlace.play()
        if lineErased > 0:
            isPC = 1
            for k in self.stacked:
                for l in k:
                    if l:
                        isPC *= 0
            if isPC:
                perfectClear.play()
                print("Perfect Clear!")
                score += 10
            if combo == 0:
                if not isPC:
                    lineErase.play()
            if raiseCombo:
                combo += 1
                if combo == 1 and not isPC:
                    combo1.play()
                elif combo == 2 and not isPC:
                    combo2.play()
                elif combo == 3 and not isPC:
                    combo3.play()
                elif combo == 4 and not isPC:
                    combo4.play()
                elif combo == 5 and not isPC:
                    combo5.play()
                elif combo == 6 and not isPC:
                    combo6.play()
                elif combo >= 7 and not isPC:
                    bigCombo.play()

            if raiseCombo + combo == 0:
                raiseCombo = 1

        if tetrminos.tspined == True:
            print("tspin")
            score += lineErased * 2 + int(math.log(2 + btb, 3)) + combo

            if raiseBtb:
                btb += 1
            if raiseBtb + btb == 0:
                raiseBtb = 1

            tetrminos.tspined = False

        elif tetrminos.mTspined == True:

            print("mtspin")
            score += (lineErased - 1) + int(math.log(2 + btb, 3)) + int((abs(combo - 4) + combo - 4) / 3)

            if raiseBtb:
                btb += 1
            if raiseBtb + btb == 0:
                raiseBtb = 1

            tetrminos.mTspined = False

        else:
            if lineErased == 4:

                score += 4 + combo + int(math.log(2 + btb, 3))

                if raiseBtb:
                    btb += 1
                if raiseBtb + btb == 0:
                    raiseBtb = 1

            elif lineErased == 3:

                score += 2 + int(combo / 2) + int(math.log(2 + btb, 3))

                btb = 0
                raiseBtb = 0
                show_type.strip("btb")

            elif lineErased == 2:

                score += 1 + int(combo / 4) + int(math.log(2 + btb, 3))

                btb = 0
                raiseBtb = 0
                show_type.strip("btb")

            elif lineErased == 1:

                score += 0 + int((combo + 4) / 6) + int(math.log(2 + btb, 3))

                btb = 0
                raiseBtb = 0
                show_type.strip("btb")

            else:

                combo = 0
                raiseCombo = 0
                show_type.strip("combo")

        if btb + combo:

            show_text = 1

            if btb:
                show_type += "btb"
            if combo:
                show_type += "combo"

        else:
            show_text = 0

        placed = False
                
    
    def fall(self,mino):
        global mino1, placed, wait
        self.count+=self.gravity

        if wait == 1:
            wait = 0
            self.count = 0
            return 0
        
        if self.count>=1:
            for i in mino.state:
                x,y=i
                if y-1<0 or self.stacked[y-1][x]:
                    if (self.gravity<1 and self.count>=40*self.gravity) or (self.gravity>=1 and self.count>=40*self.gravity) or self.gravity>=20:
                        placed=True
                        for j in mino.state:
                            x,y=j
                            self.stacked[y][x]=mino.minoType
                        del mino
                        mino1 = tetrminos(pickMino())
                        
                        mino1.state = mino1.block[mino1.rotate]
                        
                        self.count=0
##                        if self.gravity>=20:
##                            self.gravity=0.1
                        for i in mino1.state:
                            x,y=i
                            if self.stacked[y][x]:
                                gameOver.play()
                                close=False
                                while not close:
                                    clock.tick(tick)
                                    for event in pygame.event.get():
                                        if event.type == pygame.QUIT:
                                            close=True
                                    gameover_font = pygame.font.SysFont("None", 80)
                                    gameover_text = gameover_font.render('Game Over',True,(255,255,255))
                                    screen.blit(gameover_text,(0,0))
                                    pygame.display.update()
                                    pygame.display.flip()
                                pygame.quit()
                    return 0
            else:
                tetrminos.tspined=False
                tetrminos.mTspined=False
                for idx,i in enumerate(mino.block):
                    for jdx,j in enumerate(i):
                        x,y=j
                        mino.block[idx][jdx] = (x,y-1)
                self.count=0
                if self.gravity>=20:
                    self.fall(mino)
                return 1
            
    def attack(self,nline,isCheese):
        if isCheese:
            for i in range(nline):
                garbage=["garbage" for _ in range(10)]
                garbage[random.randint(0,9)] = 0
                self.stacked.insert(0,garbage.copy())
                
        else:
            garbage=["garbage" for _ in range(10)]
            garbage[random.randint(0,9)] = 0
            for i in range(nline):
                self.stacked.insert(0,garbage.copy())
                

mino1 = tetrminos(pickMino())
mino1.move(1)
mino1.move(0)
            



done = False
clock = pygame.time.Clock()
Field = field()

#User Settings
arr : int = 15
das : int = 0.5
tempArr : int = 0
tempDas : int = 0
grav : int = 0.05

while not done:
    clock.tick(tick)

    keyboard = pygame.key.get_pressed()

    for event in pygame.event.get():#Key Inputs
        if event.type == pygame.QUIT:
            done = True

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                mino1.turn(1)
                wait=1

            elif event.key == pygame.K_LCTRL:
                mino1.turn(0)
                wait=1

            elif event.key == pygame.K_a:
                mino1.turn(2)
                wait=1

            elif event.key == pygame.K_LSHIFT:
                minoHold.play()
                mino1.holdmino()

            elif event.key == pygame.K_RIGHT:
                mino1.move(1)
                wait=1

            elif event.key == pygame.K_LEFT:
                mino1.move(0)
                wait=1

            elif event.key == pygame.K_r:
                #resetting bags
                restart.play()

                del mino1

                bag = ["i","j","l","o","s","t","z"]
                _next=[]

                for i in range(6):
                    picked = random.choice(bag)
                    _next.append(picked)
                    bag.remove(picked)

                mino1=tetrminos(_next.pop())
                tetrminos.hold=""
                field.stacked = [[0 for x in range(10)] for x in range(25)]
                mino1.state = mino1.block[mino1.rotate]
                #resetting variables
                score = 0
                btb, combo, raiseCombo, raiseBtb = 0, 0, 0, 0
                placed, show_text, show_type = True, False, ""

            elif event.key == pygame.K_t:
                Field.attack(10,True)
            elif event.key == pygame.K_g:
                Field.attack(4,False)
            else:
                pass

            if event.key == pygame.K_SPACE:
                field.gravity = 20
                Field.fall(mino1)
                field.gravity = grav


    if keyboard[pygame.K_DOWN]:
        field.gravity = sdf

    if not keyboard[pygame.K_DOWN]:
        field.gravity = grav

    if keyboard[pygame.K_RIGHT]:
        tempArr+=1

        if tempArr>=arr:
            tempDas+=das

            if tempDas>=1:
                mino1.move(1)
                tempDas=0

    elif pygame.key.get_pressed()[pygame.K_LEFT]:
        tempArr+=1

        if tempArr>=arr:
            tempDas+=das

            if tempDas>=1:
                mino1.move(0)
                tempDas=0

    else:
        tempArr=0
        tempDas=0
    #Screen Settings
    screen.fill((0,0,0))
    makeGrid((128,128,128),1,blocksize)
    font = pygame.font.SysFont("None", 40)
    text = font.render("Next",True,(255,255,255))
    screen.blit(text,(blocksize*10+20,20))
    for i in range(5):
        font = pygame.font.SysFont("None", 50)
        color = (255,255,255)
        
        if _next[i]=="i":
            color=(72,209,204)
        elif _next[i]=="j":
            color=(106,90,205)
        elif _next[i]=="l":
            color=(255,140,0)
        elif _next[i]=="o":
            color=(230,230,20)
        elif _next[i]=="s":
            color=(173,255,47)
        elif _next[i]=="t":
            color=(138,43,226)
        elif _next[i]=="z":
            color=(220,20,60)
        else:
            pass
        
        text = font.render(_next[i].upper(),True,color)
        screen.blit(text,(blocksize*10+20,35*(i+2)))
        
    font = pygame.font.SysFont("None",40)
    text = font.render("Hold",True,(255,255,255))
    screen.blit(text,(blocksize*10+100,20))

    font = pygame.font.SysFont("None",50)
    color=(255,255,255)
    
    if tetrminos.hold=="i":
        color=(72,209,204)
    elif tetrminos.hold=="j":
        color=(106,90,205)
    elif tetrminos.hold=="l":
        color=(255,140,0)
    elif tetrminos.hold=="o":
        color=(230,230,20)
    elif tetrminos.hold=="s":
        color=(173,255,47)
    elif tetrminos.hold=="t":
        color=(138,43,226)
    elif tetrminos.hold=="z":
        color=(220,20,60)
    else:
        pass
    
    text=font.render(tetrminos.hold.upper(),True,color)
    screen.blit(text,(blocksize*10+100,60))
    
    font = pygame.font.SysFont("None",40)
    text = font.render("Score",True,(255,255,255))

    
    screen.blit(text,(blocksize*10+100, 100))
    font = pygame.font.SysFont("None",50)
    
    text=  font.render(str(score),True,(255,255,255))
    screen.blit(text,(blocksize*10+100, 140))

    if show_text:
        show_text-=1/tick
        
        if show_type.find("btb") != -1:
            font = pygame.font.SysFont("None",30)
            text = font.render("B2B:"+str(btb),True,(128,128,128))
            screen.blit(text,(blocksize*10+60, 250))
            
        if show_type.find("combo") != -1:
            font = pygame.font.SysFont("None",30)
            text = font.render("Combo:"+str(combo),True,(64,64,64))
            screen.blit(text,(blocksize*10+60, 270))
    
    draw_shadow(mino1,Field)
    Field.fall(mino1)
    Field.update()
    mino1.update()
    
    pygame.display.flip()

pygame.quit()
    
