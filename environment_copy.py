# %%
import pygame
import numpy as np
import copy
import time

# %%
def rotate(vecs, theta):
    rmatrix=np.array([[np.cos(theta), -np.sin(theta)],[np.sin(theta),np.cos(theta)]])
    vecs=np.array(vecs)
    if vecs.shape==(2,):
        vecs=vecs.reshape(-1,1)
    return np.around(rmatrix@vecs,5)
print(rotate([1, 0],np.pi/4))

# %%
def mag(v):
    return(np.sum(v**2)**0.5)

# %%
def normalise(v_set):
    v_set=np.array(v_set)
    mag_v=np.sum(np.square(v_set),axis=0)**0.5
    v_set=v_set/mag_v
    return np.around(v_set,5)
#print(normalise(np.array([[5],[0]])))

# %%
def column(v):
    return np.reshape(v,(-1,1))

# %%
# Define the car's properties
car_width = 8
car_length = 1.6*car_width
trailer_width=50
trailer_length=80
car_speed = 0.08
car_rotation_speed = 0.007
red=(255,0,0)
blue=(0,0,255)
black=(0,0,0)
white=(255,255,255)
car_color = blue
obstacle_size=6
obstacle_coverage=0.1


screen_width = 300
screen_height = 300

n_obs = int(obstacle_coverage*screen_width*screen_height/(4*obstacle_size**2))

# Define the starting position and orientation of the car
car_pos=np.array([[screen_width/2],[screen_height/2]])
prev_car_pos=copy.deepcopy(car_pos)
car_x = screen_width/2 - car_width/2
car_y = screen_height/2 - car_length/2
car_rotation = 0
prev_car_rotation=0
car_frame = np.array([[np.cos(car_rotation), np.cos(car_rotation+np.pi/2) ], [np.sin(car_rotation), np.sin(car_rotation+np.pi/2)]])
prev_car_frame=copy.deepcopy(car_frame)
size_mag=(((car_width/2)**2 + (car_length)**2)**0.5)
#trailer_joint=car_pos-car_dir*car_length/5
car_vel=np.array([[0],[0]])

# %%
def gcar(scaled_dir,pos):
    v=scaled_dir
    return [pos+rotate(v,np.arctan(car_width/(2*car_length)))*size_mag/car_length, pos+rotate(v,np.pi/2)*car_width/(2*car_length),pos+rotate(v,-np.pi/2)*car_width/(2*car_length), pos+rotate(v,-np.arctan(car_width/(2*car_length)))*size_mag/car_length]

# %%
def totuplelist(points):
    points_copy = []
    for i in points:
        points_copy.append(tuple(np.transpose(i)[0]))
    return points_copy

# %%
def toarray(points):
    points_copy = []
    for i in points:
        points_copy.append(np.array(i))
    return np.array(points_copy)
#print(toarray([(1,0),(2,0)]))

# %%
def gencar(cframe, pos):
    f=cframe
    top_right=np.array([[car_length],[car_width/2]])
    top_left=np.array([[0],[car_width/2]])
    bottom_left=np.array([[0],[-car_width/2]])
    bottom_right=np.array([[car_length],[-car_width/2]])

    return np.array([f@top_right+pos, f@top_left+pos, f@bottom_left+pos, f@bottom_right+pos])
#print(gencar(np.array([[0,-1],[1,0]]),np.array([[0],[0]])))

# %%
def rendercar(screen):
    car_points = gencar(car_frame,car_pos)
    car_points_copy=totuplelist(car_points)
    pygame.draw.polygon(screen, (255,255,255),totuplelist(gencar(prev_car_frame,prev_car_pos)))
    pygame.draw.polygon(screen, car_color, car_points_copy)
    line_end=car_pos+(car_length)*column(car_frame[:, 0])
    line_start = car_pos+(car_length/2)*column(car_frame[:, 0])
    pygame.draw.line(screen, white, (line_start[0][0],line_start[1][0]), (line_end[0][0],line_end[1][0]))
    
    return car_points

# %%
def convcollisioncheck(poly1,poly2): #poly1 and 2 should be np arrays of vertices of the convex polygons
    n1=len(poly1)
    n2=len(poly2)
    sidevecs=[]
    for i in range(n1):
        if i<n1-1:
            side1 = poly1[i]-poly1[i+1]
        else:
            side1 = poly1[i]-poly1[0]
        sidecap1 = side1/(np.sum(np.square(side1), axis=0))**0.5
        #print(np.sum(np.square(side1),axis=0))
        sidevecs.append(sidecap1)
    for i in range(n2):
        if i < n2-1:
            side2 = poly2[i]-poly2[i+1]
        else:
            side2 = poly2[i]-poly2[0]
        sidecap2 = side2/(np.sum(np.square(side2), axis=0))**0.5
        # print(np.sum(np.square(side1),axis=0))
        sidevecs.append(sidecap2)
    proj1=[]
    proj2=[]
    collision=True
    for i in range(len(sidevecs)):
        for vertex1 in poly1:
            #print(vertex1.shape, sidevecs[i].shape)
            proj1.append(np.dot(vertex1.T,sidevecs[i])[0][0])
        for vertex2 in poly2:
            proj2.append(np.dot(vertex2.T, sidevecs[i])[0][0])
        proj1=sorted(proj1)
        proj2=sorted(proj2)
        # print("proj1", proj1)
        # print("proj2", proj2)
        if proj1[-1]>proj2[-1]:
            if proj2[-1]<proj1[0]:
                collision=False
                break
        elif proj1[-1]<proj2[-1]:
            if proj1[-1]<proj2[0]:
                collision=False
                break
        proj1=[]
        proj2=[]
    return collision

# %%
# poly1 and 2 should be np arrays of vertices of the rectangles. 
#This function works only for rectangles but needs only half the calculations of the other
def rectcollisioncheck(poly1, poly2):
    n1 = len(poly1)
    n2 = len(poly2)
    sidevecs = []
    for i in range(2):
        side1 = poly1[i]-poly1[i+1]
        sidecap1 = side1/(np.sum(np.square(side1), axis=0))**0.5
        # print(np.sum(np.square(side1),axis=0))
        sidevecs.append(sidecap1)
    for i in range(2):
        side2 = poly2[i]-poly2[i+1]
        sidecap2 = side2/(np.sum(np.square(side2), axis=0))**0.5
        # print(np.sum(np.square(side1),axis=0))
        sidevecs.append(sidecap2)
    proj1 = []
    proj2 = []
    collision = True
    for i in range(len(sidevecs)):
        for vertex1 in poly1:
            #print(vertex1.shape, sidevecs[i].shape)
            proj1.append(np.dot(vertex1.T, sidevecs[i])[0][0])
        for vertex2 in poly2:
            proj2.append(np.dot(vertex2.T, sidevecs[i])[0][0])
        proj1 = sorted(proj1)
        proj2 = sorted(proj2)
        # print("proj1", proj1)
        # print("proj2", proj2)
        if proj1[-1] > proj2[-1]:
            if proj2[-1] < proj1[0]:
                collision = False
                break
        elif proj1[-1] < proj2[-1]:
            if proj1[-1] < proj2[0]:
                collision = False
                break
        proj1 = []
        proj2 = []
    return collision

# %%
def genobstacle(choice, point):
    point=column(point)
    squares=[]
    if choice==1: #inverted L
        # squares.append([tuple(point),tuple(point+np.array([5,0])),tuple(point+np.array([5,5])),totuplelist(point+np.array([0,5]))])
        squares.append([point,point+column([2*obstacle_size,0]),point+column([2*obstacle_size,obstacle_size]),point+column([0,obstacle_size])])
        point = point+column([obstacle_size, obstacle_size])
        squares.append([point,point+column([obstacle_size,0]),point+column([obstacle_size,2*obstacle_size]),point+column([0,2*obstacle_size])])
    elif choice==2: #I shape
        # squares.append([tuple(point),tuple(point+np.array([5,0])),tuple(point+np.array([5,5])),tuple(point+np.array([0,5]))])
        squares.append([point,point+column([obstacle_size,0]),point+column([obstacle_size,4*obstacle_size]),point+column([0,4*obstacle_size])])
    if choice==3: #Rotated Z
        # squares.append([tuple(point),tuple(point+np.array([5,0])),tuple(point+np.array([5,5])),tuple(point+np.array([0,5]))])
        squares.append([point,point+column([obstacle_size,0]),point+column([obstacle_size,2*obstacle_size]),point+column([0,2*obstacle_size])])
        point = point+column([obstacle_size, obstacle_size])
        squares.append([point,point+column([obstacle_size,0]),point+column([obstacle_size,2*obstacle_size]),point+column([0,2*obstacle_size])])
    elif choice==4: #Rotated T
        # squares.append([tuple(point),tuple(point+np.array([5,0])),tuple(point+np.array([5,5])),tuple(point+np.array([0,5]))])
        squares.append([point,point+column([obstacle_size,0]),point+column([obstacle_size,3*obstacle_size]),point+column([0,3*obstacle_size])])
        point = point+column([-obstacle_size, obstacle_size])
        squares.append([point,point+column([obstacle_size,0]),point+column([obstacle_size,obstacle_size]),point+column([0,obstacle_size])])        
    return np.array(squares)

# %%
def obsfield():
    choices=[1,2,3,4]
    xcoords=np.arange(screen_width)
    ycoords=np.arange(screen_height)
    obstacles=[]
    for i in range(n_obs):
        obstacles.append(genobstacle(np.random.choice(choices),[np.random.choice(xcoords),np.random.choice(ycoords)]))
    return obstacles

# %%
def render_obs(screen, obstacles):
    for obstacle in obstacles:
        for square in obstacle:
            pygame.draw.polygon(screen,(0,0,0),totuplelist(square))

# %%
def checkactivecoll(screen, car, obs):
    anycoll=[]
    for obstacle in obs:
        coll=[]
        for sq in obstacle:
            coll.append(rectcollisioncheck(car, sq))
        if any(coll):
            for sq in obstacle:
                pygame.draw.polygon(screen, (0,255,0),totuplelist(sq))
        else:
            for sq in obstacle:
                pygame.draw.polygon(screen, (0, 0, 0), totuplelist(sq))
            anycoll.append(True)
    #return(any(anycoll))

# %%
def val_check(car, obs):
    validity=True
    coll_index=[]
    for pt in car:
        pt=np.reshape(pt,(-1,))
        if pt[0]<0 or pt[0]>screen_width or pt[1]<0 or pt[1]>screen_height:
            #print('x')
            validity=False

    for o in range(len(obs)):
        obstacle=obs[o]
        coll = []
        for sq in obstacle:
            coll.append(rectcollisioncheck(car, sq))
        if any(coll):
            # for sq in obstacle:
            #     pygame.draw.polygon(screen, (0, 255, 0), totuplelist(sq))
            coll_index.append(o)
            validity=False
        # else:
        #     for sq in obstacle:
        #         pygame.draw.polygon(screen, (0, 0, 0), totuplelist(sq))
            
    return validity,coll_index
print(val_check(gencar(car_frame,car_pos),[]))

# %%
def findneighbourscar(curr_pos,curr_orientation):
    max_steering_angle=60
    orientation_list=[]
    pos_list=[]
    num_neighbours=1 #Neighbours per quadrant
    discretization_len=5
    #exs=[60]
    steering_angle_list = list(range(0,max_steering_angle+1, int(max_steering_angle/num_neighbours)-1))
    #print('steering_angle_list:', steering_angle_list)
    if 0 not in steering_angle_list:
        steering_angle_list.append(0)
    count=0
    for steering_angle in steering_angle_list:
        i=steering_angle
        if i!=0:
            #print("Steering angle:",i)

            r= (car_width/2)+car_length/(np.tan(i*np.pi/180))

        else:
            r= np.inf
        turning_arc_angle=discretization_len/r
        if i==0:
            orientation_list.append(np.around(curr_orientation,5))
            pos_list.append(np.around(curr_pos+ discretization_len*curr_orientation@column([-1,0]),5))
            orientation_list.append(np.around(curr_orientation,5))
            pos_list.append(np.around(curr_pos+ discretization_len*curr_orientation@column([1,0]),5))
            
            
        else:
            pos_list.append(np.around(curr_pos+ 2*r*np.sin(turning_arc_angle/2)*
                            curr_orientation@column([np.cos(turning_arc_angle/2),np.sin(turning_arc_angle/2)]),5))
            orientation_list.append(rotate(curr_orientation,turning_arc_angle))
            pos_list.append(np.around(curr_pos+ 2*r*np.sin(turning_arc_angle/2)*
                            curr_orientation@column([np.cos(turning_arc_angle/2),-np.sin(turning_arc_angle/2)]),5))
            orientation_list.append(np.around(rotate(curr_orientation,-turning_arc_angle),5))
            pos_list.append(np.around(curr_pos+ 2*r*np.sin(turning_arc_angle/2)*
                            curr_orientation@column([-np.cos(turning_arc_angle/2),np.sin(turning_arc_angle/2)]),5))
            orientation_list.append(np.around(rotate(curr_orientation,-turning_arc_angle),5))
            pos_list.append(np.around(curr_pos+ 2*r*np.sin(turning_arc_angle/2)*
                            curr_orientation@column([-np.cos(turning_arc_angle/2),-np.sin(turning_arc_angle/2)]),5))
            orientation_list.append(np.around(rotate(curr_orientation,turning_arc_angle),5))
            # print("dist:", np.sum((2*r*np.sin(turning_arc_angle/2) *
            #                        curr_orientation@column([-np.cos(turning_arc_angle/2), -np.sin(turning_arc_angle/2)]))**2)**0.5)  # )
            # print("arc length:",2*r*turning_arc_angle/2)
        count+=1
    return orientation_list, pos_list
o,p=findneighbourscar(column([0,0]),np.array([[1,0],[0,1]]))
#print(180*np.arctan2(o[0][1,0],o[0][0,0])/np.pi)
print(o)

# %%
def rmatrixtoangle(orientation):
    angle=np.arctan2(orientation[1][0],orientation[0][0])
    if angle>np.pi:
        angle-=2*np.pi
    return np.round(angle,5)
#print(rmatrixtoangle([[0,-1],[1,0]]))

# %%
def angletormatrix(angle):
    return np.around(np.array([[np.cos(angle), np.sin(-angle)],[np.sin(angle),np.cos(angle)]]),5)

# curr_state=(1,2,np.pi/2)
# print([angletormatrix(curr_state[2]),column([curr_state[0],curr_state[1]])])

# %%
def heuristic1(state1, state2): #states are 3 element tuples of pos and angle
    dist=((state1[0]-state2[0])**2+(state1[1]-state2[1])**2)**0.5

    return dist

# %%
def astarcar(start, end, obs, min_error): #start and end are [orientation, pos]
    g_value_table={}
    f_value_table={}
    parent_table={}
    count=0
    start_state=(start[1][0][0],start[1][1][0],rmatrixtoangle(start[0]))
    #print(start_state)
    curr=start
    curr_state=start_state
    end_state = (end[1][0][0], end[1][1][0], rmatrixtoangle(end[0]))
    #print(end_state)
    g_value_table[start_state]=0
    parent_table[start_state]=None
    f_value_table[start_state]=heuristic1(start_state,end_state)
    priority_list=[]
    priority_list.append([start_state,heuristic1(start_state,end_state)])
    endflag=False

    while min_error<heuristic1(curr_state,end_state) and len(f_value_table)>0 and count<10000:
        if not endflag:    
            print("curr_state:", curr_state)
            count+=1
            nbrs_o,nbrs_p=findneighbourscar(curr[1],curr[0])
            #print(nbrs_p)
            for i in range(len(nbrs_o)):
                if val_check(gencar(nbrs_o[i],nbrs_p[i]), obs)[0]:
                    nbr_state=(nbrs_p[i][0][0],nbrs_p[i][1][0], rmatrixtoangle(nbrs_o[i]))
                    g=g_value_table[curr_state]+heuristic1(curr_state,nbr_state)
                    if heuristic1(nbr_state, end_state) < min_error:
                        parent_table[end_state] = curr_state
                        print("going into end condition")
                        endflag=True
                        break
                    if not(nbr_state in g_value_table) or g<g_value_table[nbr_state]:
                        g_value_table[nbr_state]=g
                        f = g+heuristic1(nbr_state, end_state)
                        f_value_table[nbr_state]=f
                        parent_table[nbr_state]=curr_state
            next_state=min(f_value_table, key=f_value_table.get)
            del f_value_table[next_state]
            print(f_value_table)
            curr=[angletormatrix(next_state[2]),column([next_state[0],next_state[1]])]
            
            curr_state=next_state
        else:
            break
    #print("parent_table",parent_table)
    path=[]
    i=end_state
    path.append(end_state)
    global pt
    pt = parent_table
    while parent_table[i]!=None:
        path.append(parent_table[i])
        i = parent_table[i]
    return path

start_o=angletormatrix(0)
start_p=column([100,100])
end_o = angletormatrix(0)
end_p = column([150, 150])
start=[start_o, start_p]
end=[end_o, end_p]

print(astarcar(start, end, [], 1))
    


# %%
print(len(pt))
print(pt)


# %%
# Initialize Pygame
pygame.init()

# Set the dimensions of the screen
screen = pygame.display.set_mode((screen_width, screen_height))
obs=obsfield()
screen.fill(white)
obs=[]
#render_obs(screen,obs)

#print(type(screen))
# Main game loop

running = True
count=0
old_coll_indices=[]
while running:
    if count>4000000:
        count=0
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
    # Handle input
    prev_car_frame=copy.deepcopy(car_frame)
    prev_car_pos=copy.deepcopy(car_pos)
    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP]:
        car_vel = column(car_frame[:, 0])*car_speed
        car_pos += car_vel
    if keys[pygame.K_DOWN]:
        car_vel = -column(car_frame[:, 0])*car_speed
        car_pos += car_vel
    if keys[pygame.K_RIGHT]:
        car_frame = rotate(car_frame, car_rotation_speed)
    if keys[pygame.K_LEFT]:
        car_frame = rotate(car_frame, -car_rotation_speed)
    

    # Draw the car on the screen
    car=rendercar(screen)
    if count%50==0: #check collisions only 1 in 50 iterations
        val, coll_indices=val_check(car, obs)
        #start=time.time()
        if len(old_coll_indices)!=0 or len(coll_indices)!=0:
            #temp_indices=set(coll_indices)-set(old_coll_indices)
            for c in coll_indices:#list(temp_indices):
                for sq in obs[c]:
                    pygame.draw.polygon(screen, (0, 255, 0), totuplelist(sq))
            #print(coll_indices, old_coll_indices)
            temp_indices = set(old_coll_indices)-set(coll_indices)
            for c in list(temp_indices):
                for sq in obs[c]:
                    pygame.draw.polygon(screen, (0, 0, 0), totuplelist(sq))
        old_coll_indices = coll_indices.copy()
        ors, pos=findneighbourscar(car_pos, car_frame)
        if int(count/50)%2==0:
            screen.fill(white)
        #print("No. of neighbours:",len(ors))
        for i in range(len(ors)):
            if int(i/4)%2==0:
                temp_color=0 +100 #/(i+1)
            else:
                temp_color=0
            pygame.draw.polygon(screen, (temp_color,temp_color,temp_color), totuplelist(gencar(ors[i],pos[i])))
            #print(pos[i]-car_pos)
        

    
        #print(time.time()-start)
        # start=time.time()
        # render_obs(screen,obs)
        # for c in coll_indices:
        #     for sq in obs[c]:
        #         pygame.draw.polygon(screen, (0, 255, 0), totuplelist(sq))
        # print(time.time()-start)


        
    
    # Update the display
    count+=1
    pygame.display.flip()

# Quit Pygame
pygame.quit()