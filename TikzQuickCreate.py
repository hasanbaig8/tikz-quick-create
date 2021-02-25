import pygame
from collections import OrderedDict
import subprocess
#standard pygame set up commands
wScreen = 800
hScreen = 800

screen = pygame.display.set_mode((wScreen,hScreen))

run = True
isActiveLine = False
activeLinePos = (0,0)
tikzText = r"" #holds our text that we generate

#list of vertices and edges of graphs on screen and for Tikz initally empty
vertices = []
edges = []
circles = []
lines = []

def redrawScreen(): #redraws the screen
    screen.fill((200,200,200)) #backgound colour
    for circle in circles:
        pygame.draw.circle(screen,(255,0,0), (circle[0],circle[1]), 10) #draws each fixed vertex on screen
    pygame.draw.circle(screen,(0,255,0), snap_coord, 10) #draws cursor circle
    for line in lines:
        pygame.draw.line(screen, (0,0,255), line[0], line[1]) #draws each edge on screen
    if isActiveLine:
        pygame.draw.line(screen, (0,0,255), activeLinePos, snap_coord) #draws temp line for new edge
    drawGridlines() 
    pygame.display.update()

def genText():
    global tikzText
    tikzText = r""
    tikzText+= r"\begin{tikzpicture}" #needed in LaTeX to show in tikzpicture environment
    for edge in edges: #adds LaTeX code for edges
        tikzText += "\n"
        tikzText += r"\draw[-, thick] (" + str(edge[0][0]) + "," + str(edge[0][1])+") -- (" + str(edge[1][0]) + "," + str(edge[1][1])+") node[right] {};"

    tikzText += "\n"
    for vertex in vertices: #adds LaTeX code for vertices
        tikzText += "\n"
        tikzText+= r"\node[fill, circle,color = red, minimum size = 0.05cm] at (" + str(vertex[0]) + "," + str(vertex[1])+ r"){};"
    tikzText+="\n"
    tikzText+= r"\end{tikzpicture}"#needed in LaTeX to close tikzpicture environment

def outputText(): #spits out the now-generated LaTeX
    print(tikzText)

def drawGridlines():#draws grey grid
    for i in range(40): 
        pygame.draw.line(screen, (100,100,100), (0,10+20 * i), (800,10+20*i))
        pygame.draw.line(screen, (100,100,100), (10+20 * i,0), (10+20*i,800))
        
genText()
outputText()

def snapToGrid(mousePos): #snaps mouse to grid, ensures graph looks clean etc.
    if 0 < mousePos[0] < wScreen and 0 < mousePos[1] < hScreen:
        return (round((mousePos[0])/20)*20,round((mousePos[1])/20)*20)

def posTransform(pos): #takes in mouse coordinate, spits out corresponding position on Tikz grid
    return (round(((pos[0] - 400)/40)*2)/2,round(((-pos[1] + 400)/40)*2)/2)



def write_to_clipboard(output): #use this for copying to clipboard, improves efficiency when typing notes
    process = subprocess.Popen(
        'pbcopy', env={'LANG': 'en_US.UTF-8'}, stdin=subprocess.PIPE)
    process.communicate(output.encode('utf-8'))
snap_coord = (0,0)

start_ticks=0

def connectAll(): #connects all vertices together, useful for making fully connected graphs
    for i in range(len(circles) - 1):
        for j in range(i,len(circles)):
            lines.append((circles[i],circles[j]))
            edges.append((posTransform(circles[i]), posTransform(circles[j])))

while run:
    start_ticks=pygame.time.get_ticks()
    cooldownTracker = 0
    pos = tuple(pygame.mouse.get_pos())
    pygame.mouse.set_visible(False)
    snap_coord = snapToGrid(pos)# save snapped coordinates to variable
    if snap_coord == None:
        snap_coord = (0,0)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE: #space key clears everything
                vertices = []
                edges = []
                circles = []
                lines = []
            if event.key == pygame.K_p: #'p' for print, spits out latex and copies to clipboard
                genText()
                outputText()
                write_to_clipboard(tikzText)
            if event.key == pygame.K_c: #'c' for connect, connects all vertices
                connectAll()
            if event.key == pygame.K_ESCAPE: #if you start an edge accidentally, can 'escape'
                isActiveLine = False
        if event.type == pygame.MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[0]: # adds vertex those displayed on screen and those to be in LaTeX 
            vertices.append(posTransform(snap_coord))
            v_dict = OrderedDict((x, True) for x in vertices).keys()
            vertices = list(v_dict)
            circles.append(snap_coord)
            c_set = set(tuple(x) for x in circles)
            circles = [ list(x) for x in c_set ]
        if event.type == pygame.MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[2]: #creates new active line
            isActiveLine = not(isActiveLine)
            if not(isActiveLine):
                lines.append((activeLinePos, snap_coord))
                edges.append((posTransform(activeLinePos), posTransform(snap_coord)))
            activeLinePos = snap_coord
    
    redrawScreen() #redraw screen at each refresh

pygame.quit()
quit()
