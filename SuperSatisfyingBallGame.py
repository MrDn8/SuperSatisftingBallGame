import pygame
import math
import random
import colorsys

pygame.init()

# =====================
# SCREEN
# =====================
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h

UI_HEIGHT = HEIGHT // 3
GAME_HEIGHT = HEIGHT - UI_HEIGHT

screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# =====================
# HELPERS
# =====================
def random_color():
    return (random.randint(0,255), random.randint(0,255), random.randint(0,255))

def rainbow(h):
    r,g,b = colorsys.hsv_to_rgb(h,1,1)
    return (int(r*255), int(g*255), int(b*255))

def rotate(x,y,cx,cy,a):
    s,c = math.sin(a), math.cos(a)
    x -= cx
    y -= cy
    return (x*c - y*s + cx, x*s + y*c + cy)

# =====================
# ARENA
# =====================
CENTER = (WIDTH//2, GAME_HEIGHT//2)
RADIUS = min(WIDTH, GAME_HEIGHT)//3

# =====================
# BALLS
# =====================
ball_radius = 18
balls = []

def create_ball():
    return {
        "x": WIDTH//2,
        "y": GAME_HEIGHT//2,
        "vx": random.choice([-6,-5,5,6]),
        "vy": random.choice([-6,-5,5,6]),
        "trail":[]
    }

balls.append(create_ball())

# =====================
# SETTINGS
# =====================
trail_on = False
glow_on = False
outline_on = False
rainbow_on = False
paused = False
collision_on = False
spin_on = False
hole_mode = False

trail_styles = ["dots","lines","sparkle","neon"]

rainbow_h = 0
spin_angle = 0
spin_speed = 0.02

hole_angle = 0
hole_size = 50

gravity_levels = [-0.5,-0.2,0,0.2,0.5]
g_i = 2
gravity = gravity_levels[g_i]

speed_levels = [0.5,1,1.5,2,3]
s_i = 1
speed = speed_levels[s_i]

# COLORS
ball_color = (255,0,0)
circle_color = (255,255,255)

# =====================
# UI HELPER
# =====================
def B(i,row):
    return pygame.Rect(20+(i*180), GAME_HEIGHT+20+(row*80),160,60)

trail_btn = B(0,0)
glow_btn = B(1,0)
outline_btn = B(2,0)
rainbow_btn = B(3,0)

add_btn = B(0,1)
rem_btn = B(1,1)
pause_btn = B(2,1)
restart_btn = B(3,1)

gravity_btn = B(0,2)
speed_btn = B(1,2)
hole_btn = B(2,2)
spin_btn = B(3,2)

collision_btn = B(0,3)

# 🔥 NEW COLOR BUTTONS
ball_color_btn = B(0,4)
circle_color_btn = B(1,4)

font = pygame.font.SysFont(None, 28)

# =====================
# LOOP
# =====================
running = True
while running:
    screen.fill((0,0,0))

    pygame.draw.rect(screen,(20,20,20),(0,GAME_HEIGHT,WIDTH,UI_HEIGHT))

    if rainbow_on:
        rainbow_h = (rainbow_h + 0.002)%1

    if spin_on:
        spin_angle += spin_speed

    # =====================
    # EVENTS
    # =====================
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running=False

        if e.type == pygame.MOUSEBUTTONDOWN:
            x,y = e.pos

            if trail_btn.collidepoint(x,y):
                trail_on = not trail_on

            if glow_btn.collidepoint(x,y): glow_on = not glow_on
            if outline_btn.collidepoint(x,y): outline_on = not outline_on
            if rainbow_btn.collidepoint(x,y): rainbow_on = not rainbow_on

            if add_btn.collidepoint(x,y): balls.append(create_ball())
            if rem_btn.collidepoint(x,y) and len(balls)>1: balls.pop()

            if pause_btn.collidepoint(x,y): paused = not paused

            if restart_btn.collidepoint(x,y):
                balls=[create_ball()]

            if gravity_btn.collidepoint(x,y):
                g_i=(g_i+1)%len(gravity_levels)
                gravity=gravity_levels[g_i]

            if speed_btn.collidepoint(x,y):
                s_i=(s_i+1)%len(speed_levels)
                speed=speed_levels[s_i]

            if hole_btn.collidepoint(x,y):
                hole_mode = not hole_mode
                hole_angle=random.random()*math.pi*2
                hole_size=random.randint(30,90)

            if spin_btn.collidepoint(x,y):
                spin_on = not spin_on

            if collision_btn.collidepoint(x,y):
                collision_on = not collision_on

            # 🎲 NEW COLOR BUTTONS
            if ball_color_btn.collidepoint(x,y):
                ball_color = random_color()

            if circle_color_btn.collidepoint(x,y):
                circle_color = random_color()

    # =====================
    # PHYSICS
    # =====================
    if not paused:
        for b in balls:

            b["vy"] += gravity

            x,y=b["x"],b["y"]
            if spin_on:
                x,y=rotate(x,y,*CENTER,-spin_angle)

            b["x"] += b["vx"]*speed
            b["y"] += b["vy"]*speed

            dx=b["x"]-CENTER[0]
            dy=b["y"]-CENTER[1]
            dist=math.sqrt(dx*dx+dy*dy)

            if dist+ball_radius>=RADIUS:

                if hole_mode:
                    ang=math.atan2(dy,dx)
                    diff=abs((ang-hole_angle+math.pi)%(2*math.pi)-math.pi)
                    if diff<hole_size/RADIUS:
                        balls.remove(b)
                        hole_angle=random.random()*math.pi*2
                        hole_size=random.randint(30,90)
                        break

                nx,ny=dx/dist,dy/dist
                dot=b["vx"]*nx+b["vy"]*ny

                b["vx"]-=2*dot*nx
                b["vy"]-=2*dot*ny

                b["vx"]*=1.01
                b["vy"]*=1.01

            if spin_on:
                b["x"],b["y"]=rotate(b["x"],b["y"],*CENTER,spin_angle)

            if trail_on:
                b["trail"].append((b["x"],b["y"]))
                if len(b["trail"])>40:
                    b["trail"].pop(0)

    # =====================
    # COLLISION
    # =====================
    if collision_on:
        for i in range(len(balls)):
            for j in range(i+1,len(balls)):
                a,b=balls[i],balls[j]
                dx=a["x"]-b["x"]
                dy=a["y"]-b["y"]
                d=math.sqrt(dx*dx+dy*dy)
                if d==0: continue
                if d<ball_radius*2:
                    nx,ny=dx/d,dy/d
                    dvx=a["vx"]-b["vx"]
                    dvy=a["vy"]-b["vy"]
                    dot=dvx*nx+dvy*ny
                    if dot<0:
                        a["vx"]-=dot*nx
                        a["vy"]-=dot*ny
                        b["vx"]+=dot*nx
                        b["vy"]+=dot*ny

    # =====================
    # DRAW ARENA
    # =====================
    col = rainbow(rainbow_h) if rainbow_on else circle_color
    pygame.draw.circle(screen,col,CENTER,RADIUS,5)

    if hole_mode:
        pygame.draw.arc(screen,(0,0,0),
            (CENTER[0]-RADIUS,CENTER[1]-RADIUS,RADIUS*2,RADIUS*2),
            hole_angle-hole_size/RADIUS,
            hole_angle+hole_size/RADIUS,8)

    # =====================
    # DRAW BALLS
    # =====================
    for b in balls:

        c = rainbow(rainbow_h) if rainbow_on else ball_color

        if glow_on:
            for r in range(25,5,-5):
                pygame.draw.circle(screen,(255,255,255),(int(b["x"]),int(b["y"])),r)

        if outline_on:
            pygame.draw.circle(screen,(255,255,255),(int(b["x"]),int(b["y"])),ball_radius+2,2)

        pygame.draw.circle(screen,c,(int(b["x"]),int(b["y"])),ball_radius)

        if trail_on:
            for i,p in enumerate(b["trail"]):
                f=i/max(1,len(b["trail"]))
                size=max(2,int(ball_radius*f))
                tc=rainbow((rainbow_h+i*0.02)%1) if rainbow_on else ball_color
                tc=(int(tc[0]*f),int(tc[1]*f),int(tc[2]*f))
                pygame.draw.circle(screen,tc,(int(p[0]),int(p[1])),size)

    # =====================
    # UI DRAW (UPDATED)
    # =====================
    buttons = [
        (trail_btn,"Trail"),
        (glow_btn,"Glow"),
        (outline_btn,"Outline"),
        (rainbow_btn,"Rainbow"),
        (add_btn,"+"),
        (rem_btn,"-"),
        (pause_btn,"Pause"),
        (restart_btn,"Reset"),
        (gravity_btn,"Gravity"),
        (speed_btn,"Speed"),
        (hole_btn,"Hole"),
        (spin_btn,"Spin"),
        (collision_btn,"Collision"),
        (ball_color_btn,"Ball Color"),
        (circle_color_btn,"Arena Color")
    ]

    for r,t in buttons:
        pygame.draw.rect(screen,(80,80,80),r)
        screen.blit(font.render(t,True,(255,255,255)),(r.x+10,r.y+15))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()