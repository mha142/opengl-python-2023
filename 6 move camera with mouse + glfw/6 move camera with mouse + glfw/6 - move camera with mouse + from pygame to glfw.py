#import pygame as pg
import glfw 
from OpenGL.GL import *
import numpy as np
from OpenGL.GL.shaders import compileProgram, compileShader
import pyrr
from camera import Camera

#load any 2 objects
#seperate the head and face 
#load the face and head objects
# do procrustes to move the first cube to the second cube  

#convert from local to global coordinated and vice versa


cam = Camera()
WIDTH, HEIGHT = 1280, 720
lastX, lastY = WIDTH / 2, HEIGHT / 2
first_mouse = True


class Cube: #this cube object holds the position and angle withwhich to draw an object 

    def __init__(self, position, eulers, center, length):
        self.position = np.array(position, dtype=np.float32)
        self.eulers = np.array(eulers, dtype=np.float32)
        self.center = np.array(center, dtype=np.float32)
        self.length = np.array(length, dtype=np.float32)
        centerPosX = center[0]  #position[0]
        centerPosY = center[1] #position[1]
        centerPosZ = center[2] #position[2]
        length_x = length[0]
        length_y = length[1]
        length_z = length[2]
        #edgeLength = 1
    #def drawCube(self, centerPosX, centerPosY, centerPosZ, edgeLength):
        #halfSideLength = edgeLength * 0.5
        halfSideLength_x = length_x * 0.5
        halfSideLength_y = length_y * 0.5
        halfSideLength_z = length_z * 0.5
        
        self.vertices = (
            #front face
            #x, y, z
            centerPosX - halfSideLength_x, centerPosY + halfSideLength_y, centerPosZ + halfSideLength_z, #top left = 0
            centerPosX + halfSideLength_x, centerPosY + halfSideLength_y, centerPosZ + halfSideLength_z, #top right = 1
            centerPosX + halfSideLength_x, centerPosY - halfSideLength_y, centerPosZ + halfSideLength_z, #bottom right = 2
            centerPosX - halfSideLength_x, centerPosY - halfSideLength_y, centerPosZ + halfSideLength_z, #bottom left = 3

            #back face
            centerPosX - halfSideLength_x, centerPosY + halfSideLength_y, centerPosZ - halfSideLength_z, #top left = 4
            centerPosX + halfSideLength_x, centerPosY + halfSideLength_y, centerPosZ - halfSideLength_z, #top right = 5
            centerPosX + halfSideLength_x, centerPosY - halfSideLength_y, centerPosZ - halfSideLength_z, #bottom right = 6
            centerPosX - halfSideLength_x, centerPosY - halfSideLength_y, centerPosZ - halfSideLength_z, #bottom left = 7

        )

        self.vertices = np.array(self.vertices, dtype=np.float32)
        self.vertex_count = len(self.vertices) // 3 # 3 is the number of numbers in each row #the result is 3
        
        self.vao = glGenVertexArrays(1)#### make 1 slot only #we need to make 2 slots 
        glBindVertexArray(self.vao)###
        
        self.vbo = glGenBuffers(1)#####
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)######
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW) ########ship the data to the graphics card
        
        glEnableVertexAttribArray(0)#attribute 0 is position 
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3 * 4, ctypes.c_void_p(0)) #describe how attribute 0 is laid out in the vbo
        #each vertex has 3 numbers x 4 bytes = 12 
        
        #lines that connect between the vertices
        
        #maha's indices
        self.lines = (
            0,1,   1,2,   2,3,   3,0,
			4,5,   5,6,   6,7,   7,4,
			0,4,   1,5,   3,7,   2,6
        )
        '''
        self.lines = (
            0,1,   1,3,   3,2,   2,0,
			4,5,   5,7,   7,6,   6,4,
			0,4,   1,5,   3,7,   2,6
        )
        '''
        self.lines = np.array(self.lines, dtype=np.float32)
        
        #tutorial has only one vao, but if I take this vao out then nothing is drawn!
        self.vao2 = glGenVertexArrays(1)#### make 1 slot only 
        glBindVertexArray(self.vao2)###
 
        #we need to create gpu memory to hold the indices, so we need to create a buffer 
        self.ibo = glGenBuffers(1)#####
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ibo)######
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.lines.nbytes, self.lines, GL_STATIC_DRAW) ########ship the data to the graphics card
        
        #we don't need this with GL_ELEMENT_ARRAY_BUFFER
        #glEnableVertexAttribArray(0)#attribute 0 is position 
        #glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3 * 4, ctypes.c_void_p(0)) #describe how attribute 0 is laid out in the vbo
        #each vertex has 3 numbers x 4 bytes = 12 (stride) ..........(0) is the offset
          
        
    #free the memory 
    def destroy(self):
        glDeleteVertexArrays(1, (self.vao, ))
        glDeleteBuffers(1, (self.vbo, ))
        glDeleteVertexArrays(1, (self.vao2, ))
        glDeleteBuffers(1, (self.ibo, ))


class App:

    def __init__(self):
        #initialize pygame
        #pg.init()
        #pg.display.set_mode((640, 480), pg.OPENGL|pg.DOUBLEBUF)
        #self.clock = pg.time.Clock()
        #initialize glfw
        if not glfw.init():
            raise Exception("glfw can't be initialized!")
        #creating the window 
        self.window = glfw.create_window(WIDTH, HEIGHT, "My  OpenGL Window", None, None) #1280, 720 #
        #check if the window was created
        if not self.window:
            glfw.terminate()
            raise Exception("glfw can't be created")
        #set the window's position
        glfw.set_window_pos(self.window, 400, 200)
        glfw.set_window_size_callback(self.window, self.window_resize)
        glfw.set_cursor_pos_callback(self.window, self.mouse_look_callback)
        glfw.set_cursor_enter_callback(self.window, self.mouse_enter_callback)

        #make the context current
        glfw.make_context_current(self.window)
        glClearColor(0.1, 0.2, 0.2, 1)
        glEnable(GL_DEPTH_TEST)
        self.shader = self.createShader(b'vertex_shader.txt', b'fragment_shader.txt')
        glUseProgram(self.shader)
        self.triangle = Triangle()
        x_center, y_center, z_center, x_size, y_size, z_size = self.triangle.return_cube_info()
        self.cube1 = Cube(
            #position = [0, 0, -3], #-3 (negative means put the object infront of the camera)
            position = [0, 0, -2], #chnage the cube position in this line
            eulers = [0, 0, 0],
            center = [x_center, y_center, z_center],
            length = [x_size, y_size, z_size]
        )

        self.cube2 = Cube(
            #position = [0, 0, -3], #-3 (negative means put the object infront of the camera)
            position = [2, 0, -5], #-3 (negative means put the object infront of the camera)
            eulers = [0, 0, 0],
            center = [x_center, y_center, z_center],
            length = [x_size, y_size, z_size]
        )

        projection = pyrr.matrix44.create_perspective_projection(
            fovy = 45, aspect = WIDTH/HEIGHT, 
            near = 0.1, far = 10, dtype=np.float32
        )
        
        #eye, target, up
        #view = pyrr.matrix44.create_look_at(pyrr.Vector3([0, 2, 16]), pyrr.Vector3([0, 0, 0]), pyrr.Vector3([0, 1, 0]))
        #we comment the view out cuz it will be recalculated in every frame


        self.projection_location = glGetUniformLocation(self.shader, "projection") 
        glUniformMatrix4fv(self.projection_location, 1, GL_FALSE, projection)

        self.view_location =  glGetUniformLocation(self.shader, "view")
        #glUniformMatrix4fv(self.view_location, 1, GL_FALSE, view)


        self.modelMatrixLocation = glGetUniformLocation(self.shader, "model")
        self.mainLoop()

    def createShader(self, vertexFilepath, fragmentFilepath):
        with open(vertexFilepath, 'r') as f:
            vertex_src = f.readlines()

        with open(fragmentFilepath, 'r') as f:
            fragment_src = f.readlines()

        shader = compileProgram(
            compileShader(vertex_src, GL_VERTEX_SHADER),
            compileShader(fragment_src, GL_FRAGMENT_SHADER)
        )

        return shader


    def mainLoop(self):
        #pygame
        '''
        running = True
        while(running):
            for event in pg.event.get():
                if(event.type == pg.QUIT):
                    running = False
        '''  
        #GLFW
        while not glfw.window_should_close(self.window):
            glfw.poll_events()
            #refresh screen 
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)#this line and after it are for both glfw and pygame 
            view = cam.get_view_matrix()
            glUniformMatrix4fv(self.view_location, 1, GL_FALSE, view)

            #draw the triangle
            glUseProgram(self.shader)

            triagnle1_transform = pyrr.matrix44.create_identity(dtype=np.float32)
            #rotation
            #model_transform = pyrr.matrix44.multiply(  #rotation
            #    m1 = model_transform,
            #    m2 = pyrr.matrix44.create_from_eulers(
            #    eulers = np.radians(self.cube.eulers), 
            #    dtype=np.float32
            #    ) 
            #)
            triagnle1_transform = pyrr.matrix44.multiply( #translation
                m1 = triagnle1_transform,
                #m2 = pyrr.matrix44.create_from_translation(vec = self.cube1.position, dtype=np.float32) 
                m2 = pyrr.matrix44.create_from_translation(pyrr.Vector3([-1, 0, -3]), dtype=np.float32) 
            )
            triagnle2_transform = pyrr.matrix44.create_identity(dtype=np.float32)
            triagnle2_transform = pyrr.matrix44.multiply( #translation
                m1 = triagnle2_transform,
                m2 = pyrr.matrix44.create_from_translation(vec = self.cube2.position, dtype=np.float32) 
            )
            
            cube1_transform = pyrr.matrix44.create_from_translation(vec = self.cube1.position, dtype=np.float32) 
            cube2_transform = pyrr.matrix44.create_from_translation(vec = self.cube2.position, dtype=np.float32) 

            #quad_transform = pyrr.matrix44.create_from_translation(pyrr.Vector3([-1, 0, -3]), dtype=np.float32) 
            #draw triangle 1
            glUniformMatrix4fv(self.modelMatrixLocation, 1, GL_FALSE, cube1_transform) 
            glBindVertexArray(self.triangle.vao)#the current model that we will draw
            glDrawArrays(GL_TRIANGLES, 0, self.triangle.vertex_count) ########
            #GL_LINE_LOOP
            
            #draw triangle 2
            glUniformMatrix4fv(self.modelMatrixLocation, 1, GL_FALSE, triagnle2_transform) #triagnle2_transform
            glBindVertexArray(self.triangle.vao)#the current model that we will draw
            glDrawArrays(GL_TRIANGLES, 0, self.triangle.vertex_count) ########


            #glUniformMatrix4fv(self.modelMatrixLocation, 1, GL_FALSE, quad_transform) 
            #glBindVertexArray(self.quad.vao)#the current model that we will draw
            #glDrawArrays(GL_LINE_LOOP, 0, self.quad.vertex_count) ########

            #draw cube 1
            glUniformMatrix4fv(self.modelMatrixLocation, 1, GL_FALSE, cube1_transform) 
            glBindVertexArray(self.cube1.vao)#the current model that we will draw
            #glDrawArrays(GL_LINE_LOOP, 0, self.cube1.vertex_count) ######## 
            glDrawElements(GL_LINES, 24, GL_UNSIGNED_INT, self.cube1.lines)
            
            #draw cube 2
            glUniformMatrix4fv(self.modelMatrixLocation, 1, GL_FALSE, cube2_transform) 
            glBindVertexArray(self.cube2.vao)#the current model that we will draw
            #glDrawArrays(GL_LINE_LOOP, 0, self.cube1.vertex_count) ######## 
            glDrawElements(GL_LINES, 24, GL_UNSIGNED_INT, self.cube2.lines)

            #pg.display.flip()
            #timing
            #self.clock.tick(60)
            glfw.swap_buffers(self.window)

        self.quit()

    def quit(self):
        self.triangle.destroy()
        glDeleteProgram(self.shader)
        glfw.terminate()
    
    def window_resize(self, window, width, height):
        glViewport(0, 0, width, height)
        projection = pyrr.matrix44.create_perspective_projection_matrix(45, width / height, 0.1, 100)
        glUniformMatrix4fv(self.projection_location, 1, GL_FALSE, projection)

    #this function will be called everytime the mouse moves inside the window
    def mouse_look_callback(self, window, xpos, ypos):
        global lastX, lastY

        if first_mouse:
            lastX = xpos
            lastY = ypos

        xoffset = xpos - lastX
        yoffset = lastY - ypos # we do this inverted because y axis increasee from bottom to top and the mouse coordinates start from top to bottom 

        lastX = xpos
        lastY = ypos
        cam.process_mouse_movement(xoffset, yoffset)
        
    #this function will be called everytime the mouse enters the window
    def mouse_enter_callback(self, window, entered):
        global first_mouse

        if entered:
            first_mouse = False
        else:
            first_mouse = True


class Triangle:

    def __init__(self):
            #x, y, z, r, g, b
        #self.vertices = (
        #    -0.5, -0.5, 0.0, 1.0, 0.0, 0.0, 
        #     0.5, -0.5, 0.0, 0.0, 1.0, 0.0, 
        #     0.0,  0.5, 0.0, 0.0, 0.0, 1.0
        #)
        self.vertices = (
            -0.5, -0.5, -0.5, 1.0, 0.0, 0.0,
             0.5, -0.5, -0.5, 1.0, 0.0, 0.0,
             0.0,  0.5,  0.0, 1.0, 0.0, 0.0,

            -0.5, -0.5,  0.5, 0.0, 1.0, 0.0,
             0.5, -0.5,  0.5, 0.0, 1.0, 0.0,
             0.0,  0.5,  0.0, 0.0, 1.0, 0.0,

            -0.5, -0.5, -0.5, 0.0, 0.0, 1.0,
            -0.5, -0.5,  0.5, 0.0, 0.0, 1.0,
             0.0,  0.5,  0.0, 0.0, 0.0, 1.0,

            -0.5, -0.5, -0.5, 0.0, 0.9, 1.0,
             0.5, -0.5,  0.5, 0.0, 0.9, 1.0,
             0.0,  0.5,  0.0, 0.0, 0.9, 1.0,

             -0.5, -0.5, -0.5, 0.0, 0.0, 0.0,
             0.5, -0.5,   0.5, 0.0, 0.0, 0.0,
             0.0,  0.5,   0.0, 0.0, 0.0, 0.0,

             -0.5, -0.5, 0.5, 1.0, 1.0, 1.0,
             -0.5, -0.5, -0.5, 1.0, 1.0, 1.0,
              0.0,  0.5,  0.0, 1.0, 1.0, 1.0
        )

        self.vertices = np.array(self.vertices, dtype=np.float32)
        
        # vertex_count = num of vertecies
        self.vertex_count = len(self.vertices) // 6 # 6 is the number of numbers in each row #the result is 3
        self.vao = glGenVertexArrays(1)#### make 1 slot only so make it two 
        glBindVertexArray(self.vao)###
        self.vbo = glGenBuffers(1)##### make 1 slot only so make it two
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)######
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW) ########ship the data to the graphics card
        
        glEnableVertexAttribArray(0)#attribute 0 is position 
        #3 = the numbers in each row,// 24 = 3 numbers x 4 bytes ,// 0 = the position attribute starts at location 0  
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(0)) #describe how attribute 0 is laid out in the vbo
        glEnableVertexAttribArray(1) #attribute 1 is color
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(12)) #each vertex has 6 numbers  x 4 bytes = 24, the color attribute starts at position 12 (after 3 number = 3 numbers x 4 bytes = 12)

    #free the memory
    def destroy(self):
        glDeleteVertexArrays(1, (self.vao, ))
        glDeleteBuffers(1, (self.vbo, ))

    def return_cube_info(self):
        x = self.vertices[::6]
        y = self.vertices[1::6]
        z = self.vertices[2::6]
        #find maximum of each coordinate 
        x_max = np.max(x)
        y_max = np.max(y)
        z_max = np.max(z)
        #find minimum of each coordinate 
        x_min = np.min(x)
        y_min = np.min(y)
        z_min = np.min(z)
        #compute the size of the object in each coordinate max-min
        x_size = x_max - x_min
        y_size = y_max - y_min
        z_size = z_max - z_min
        #compute the centre of the object 
        x_center = (x_min + x_max)/2
        y_center = (y_min + y_max)/2
        z_center = (z_min + z_max)/2
        return x_center, y_center, z_center, x_size, y_size, z_size


if __name__ == "__main__":
    myApp = App()