import contextlib
with contextlib.redirect_stdout(None):
    import pygame
import numpy
import copy
import _thread
import sys
import time
import queue
from calculation import *
from pygame.locals import *
from draw import *

from OpenGL.GL import *
from OpenGL.GLU import *
q = queue.Queue()
numpy.set_printoptions(suppress=True) #prevent scientific notation

def windowInput(q): #Thread to switch between pygame window and command shell
    global consoling
    consoling = True
    while True:
        command = input(">>> ").split(" ")
        q.put(command)

def CreateVertexMatrix(pasangan_point, matrix): #Fill matrix with user's input
    print("Masukkan nilai point:")
    for i in range(pasangan_point):
        matrix[i][0], matrix[i][1] = map(float, input().split(","))

# --------------------- INTERFACE AWAL ---------------------------------------
bintang = "***************************************************\n"
welcome = "**Selamat Datang di Program Transformasi Geometri**\n"
msg = "Program ini digunakan untuk visualisasi transformasi\ngeometri terhadap objek 2D/3D. Untuk memulai\nprogram, pilih mode yang ingin dijalankan.\n"
def typing(str): #Simulated typing
    for letter in str:
        sys.stdout.write(letter)
        sys.stdout.flush()
        time.sleep(0.0075)
typing(bintang)
typing(welcome)
typing(bintang)
print(msg)

#Choose between 2D/3D
pilihan = input("Mode yang ingin dijalankan (2D/3D): ")
while(not pilihan == "2D" and not pilihan == "3D"):
    pilihan = input("Input salah. Pilih antara 2D/3D: ")
print()

#Ask and create matrix based on user's input if choice is 2D
if(pilihan == "2D"):
    dim = 2
    pasangan_point = int(input("Masukkan jumlah pasangan/tuple point: "))
    matrix = numpy.zeros((pasangan_point, 3)) #Bentuk matrix 3 * pasangan_point
    CreateVertexMatrix(pasangan_point, matrix)
    print()
    print("Matrix yang dihasilkan: ")
    print(matrix)
    print()
else:
    dim = 3
    matrix = numpy.array([[1, -1, -1],
                           [1, 1, -1],
                           [-1, 1, -1],
                           [-1, -1, -1],
                           [1, -1, 1],
                           [1, 1, 1],
                           [-1, -1, 1],
                           [-1, 1, 1]])

matrix_result = copy.deepcopy(matrix)

view_mat = IdentityMat44()

# --------------------- Pygame Window Initialization and glView Initialization ---------------------------------------
pygame.init() #Initialize pygame window
pygame.display.set_caption('Transformasi Geometri ' + str(pilihan)) #Set pygame window name
display = (800,600) #Create pygame window with 800 x 600 resolution
screen = pygame.display.set_mode(display, DOUBLEBUF|OPENGL)

glMatrixMode(GL_PROJECTION)
gluPerspective(45, (display[0]/display[1]), 0.1, 50.0)

view_mat = IdentityMat44()
glMatrixMode(GL_MODELVIEW)
glLoadIdentity()
glTranslatef(0, 0, -15)
glGetFloatv(GL_MODELVIEW_MATRIX, view_mat) #ngisi view_mat dengan matrix di stack modelview
glLoadIdentity()

_thread.start_new_thread(windowInput,(q,))

tx = 0
ty = 0
tz = 0
ry = 0
rx = 0
rz = 0
command = [""] * 5 #Initialize list command with empty string

while True:
    command[0] = ""
    #Bagian command
    if not q.empty():
        command = q.get()

    if command[0] == "translate":
        dx = float(command[1])
        dy = float(command[2])
        if dim == 2:
            dz = 0
        else:
            dz = float(command[3])
        matrix_result = translate(matrix_result,dx,dy,dz)

    elif command[0] == "dilate":
        k = float(command[1])
        matrix_result = dilate(matrix_result, k)

    elif command[0] == "rotate":
        deg = float(command[1])
        a = float(command[2])
        b = float(command[3])
        matrix_result = rotate(matrix_result, deg, a, b)

    elif command[0] == "reflect":
        param = command[1]
        matrix_result = reflect(matrix_result, dim, param)

    elif command[0] == "shear":
        param = command[1]
        k = float(command[2])
        matrix_result = shear(matrix_result, dim, param, k)

    elif command[0] == "stretch":
        param = command[1]
        k = float(command[2])
        matrix_result = stretch(matrix_result, dim, param, k)

    elif command[0] == "custom":
        a = float(command[1])
        b = float(command[2])
        c = float(command[3])
        d = float(command[4])
        if dim == 2:
            e = 0
            f = 0
            g = 0
            h = 0
            i = 0
        else:
            e = float(command[5])
            f = float(command[6])
            g = float(command[7])
            h = float(command[8])
            i = float(command[9])
        matrix_result = custom(matrix_result, dim, a, b, c, d, e, f, g, h, i)

    elif command[0] == "multiple":
        n = int(command[1])
        matrix_result = multiple(matrix_result, dim, n, consoling)

    elif command[0] == "reset":
        matrix_result = copy.deepcopy(matrix)

    elif command[0] == "exit":
        sys.exit(0)

    #Event in pygame window
    events = pygame.event.get()
    for event in events:
        #If Esc key is pressed, exit program
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()

        #If keyboard key is pressed down
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                quit()

            if   event.key == pygame.K_p:
                print("Printing matrix...")
                print(matrix_result)
                print()
                sys.stdout.write(">>> ")
                sys.stdout.flush()

            if   event.key == pygame.K_a:     tx =  0.1 #if key a is pressed
            elif event.key == pygame.K_d:     tx = -0.1 #if key d is pressed
            elif event.key == pygame.K_q:     ty =  0.1 #if key q is pressed
            elif event.key == pygame.K_e:     ty = -0.1 #if key e is pressed
            elif event.key == pygame.K_w:     tz =  0.1 #if key w is pressed
            elif event.key == pygame.K_s:     tz = -0.1 #if key s is pressed
            elif event.key == pygame.K_RIGHT: ry =  1.0 #if right anchor key is pressed
            elif event.key == pygame.K_LEFT:  ry = -1.0 #if left anchor key is pressed
            elif event.key == pygame.K_UP:    rx = -1.0 #if up anchor key is pressed
            elif event.key == pygame.K_DOWN:  rx =  1.0 #if down anchor key is pressed
            elif event.key == pygame.K_c:     rz = -1.0 #if c anchor key is pressed
            elif event.key == pygame.K_x:     rz =  1.0 #if x anchor key is pressed

        #If keyboard key is let go
        elif event.type == pygame.KEYUP:
            if   event.key == pygame.K_a     and tx > 0: tx = 0
            elif event.key == pygame.K_d     and tx < 0: tx = 0
            elif event.key == pygame.K_q     and ty > 0: ty = 0
            elif event.key == pygame.K_e     and ty < 0: ty = 0
            elif event.key == pygame.K_w     and tz > 0: tz = 0
            elif event.key == pygame.K_s     and tz < 0: tz = 0
            elif event.key == pygame.K_RIGHT and ry > 0: ry = 0.0
            elif event.key == pygame.K_LEFT  and ry < 0: ry = 0.0
            elif event.key == pygame.K_UP    and rx < 0: rx = 0.0
            elif event.key == pygame.K_DOWN  and rx > 0: rx = 0.0
            elif event.key == pygame.K_c     and rz < 0: rz = 0.0
            elif event.key == pygame.K_x     and rz > 0: rz = 0.0

    glPushMatrix()
    glLoadIdentity()

    glTranslatefKw(tx,ty,tz)#translate by tx,ty,tz
    glRotationfKw(rx,1, 0, 0)
    glRotationfKw(ry,0, 1, 0)
    glRotationfKw(rz,0, 0, 1)

    glMultMatrixf(view_mat)
    glGetFloatv(GL_MODELVIEW_MATRIX, view_mat)
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

    if pilihan == "2D":
        Draw2D(matrix_result)
    else:
        Cube(matrix_result)
    Axis()
    glPopMatrix()

    pygame.display.flip()
    pygame.time.wait(10)
