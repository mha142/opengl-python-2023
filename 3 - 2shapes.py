import pygame as pg 
from OpenGL.GL import *
import numpy as np
from OpenGL.GL.shaders import compileProgram, compileShader
import pyrr
#draw a box  
#convert from local to global coordinated and vice versa
#draw a bounding box 
#move the bounding box 
class Cube: #this cube object holds the position and angle withwhich to draw an object 

    def __init__(self, position, eulers):
        self.position = np.array(position, dtype=np.float32)
        self.eulers = np.array(eulers, dtype=np.float32)

class App:

    def __init__(self):
        pg.init()
        pg.display.set_mode((640, 480), pg.OPENGL|pg.DOUBLEBUF)
        self.clock = pg.time.Clock()
        glClearColor(0.1, 0.2, 0.2, 1)
        glEnable(GL_DEPTH_TEST)
        self.shader = self.createShader(b'vertex_shader.txt', b'fragment_shader.txt')
        glUseProgram(self.shader)
        self.triangle = Triangle()
        self.quad = Quad()
        self.cube1 = Cube(
            #position = [0, 0, -3], #-3 (negative means put the object infront of the camera)
            position = [0, 0, -2], #-3 (negative means put the object infront of the camera)
            eulers = [0, 0, 0]
        )

        self.cube2 = Cube(
            #position = [0, 0, -3], #-3 (negative means put the object infront of the camera)
            position = [2, 0, -5], #-3 (negative means put the object infront of the camera)
            eulers = [0, 0, 0]
        )

        projection_transform = pyrr.matrix44.create_perspective_projection(
            fovy = 45, aspect = 640/480, 
            near = 0.1, far = 10, dtype=np.float32
        )
        #model_transform = pyrr.matrix44.create_from_translation(pyrr.Vector3([1, 0, 0]))
        glUniformMatrix4fv(
            glGetUniformLocation(self.shader, "projection"), 
            1, GL_FALSE, projection_transform
        )

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
        running = True
        while(running):
            for event in pg.event.get():
                if(event.type == pg.QUIT):
                    running = False
            #update cube 
            #[0] means the rotation around the z axis = roll 
            #[1] means the rotation around the x axis = pitch
            #[2] means the rotation around the y axis = yaw
            #self.cube.eulers[2] +=0.2 #[2] means the rotation around the 
            #if (self.cube.eulers[2] > 360):
            #    self.cube.eulers[2] -= 360

            #refresh screen 
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
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
                m2 = pyrr.matrix44.create_from_translation(vec = self.cube1.position, dtype=np.float32) 
            )
            triagnle2_transform = pyrr.matrix44.create_identity(dtype=np.float32)
            triagnle2_transform = pyrr.matrix44.multiply( #translation
                m1 = triagnle2_transform,
                m2 = pyrr.matrix44.create_from_translation(vec = self.cube2.position, dtype=np.float32) 
            )

            quad_transform = pyrr.matrix44.create_from_translation(pyrr.Vector3([-1, 0, -3]), dtype=np.float32) 



            glUniformMatrix4fv(self.modelMatrixLocation, 1, GL_FALSE, triagnle1_transform) 
            glBindVertexArray(self.triangle.vao)#the current model that we will draw
            glDrawArrays(GL_TRIANGLES, 0, self.triangle.vertex_count) ########
            #GL_LINE_LOOP
            glUniformMatrix4fv(self.modelMatrixLocation, 1, GL_FALSE, triagnle2_transform) 
            glBindVertexArray(self.triangle.vao)#the current model that we will draw
            glDrawArrays(GL_TRIANGLES, 0, self.triangle.vertex_count) ########


            glUniformMatrix4fv(self.modelMatrixLocation, 1, GL_FALSE, quad_transform) 
            glBindVertexArray(self.quad.vao)#the current model that we will draw
            glDrawArrays(GL_LINE_LOOP, 0, self.quad.vertex_count) ########
            pg.display.flip()
            #timing
            self.clock.tick(60)
        self.quit()

    def quit(self):
        self.triangle.destroy()
        glDeleteProgram(self.shader)
        pg.quit()

class Triangle:

    def __init__(self):
            #x, y, z, r, g, b
        self.vertices = (
            -0.5, -0.5, 0.0, 1.0, 0.0, 0.0, 
             0.5, -0.5, 0.0, 0.0, 1.0, 0.0, 
             0.0,  0.5, 0.0, 0.0, 0.0, 1.0
        )

        self.vertices = np.array(self.vertices, dtype=np.float32)
        self.vertex_count = len(self.vertices) // 6 # 6 is the number of numbers in each row #the result is 3
        self.vao = glGenVertexArrays(1)#### make 1 slot only so make it two 
        glBindVertexArray(self.vao)###
        self.vbo = glGenBuffers(1)##### make 1 slot only so make it two
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)######
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW) ########ship the data to the graphics card
        
        glEnableVertexAttribArray(0)#attribute 0 is position 
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(0)) #describe how attribute 0 is laid out in the vbo
        glEnableVertexAttribArray(1) #attribute 1 is color
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(12)) #each vertex has 6 numbers  x 4 bytes = 24, the color attribute starts at position 12 (after 3 number = 3 numbers x 4 bytes = 12)

    #free the memory
    def destroy(self):
        glDeleteVertexArrays(1, (self.vao, ))
        glDeleteBuffers(1, (self.vbo, ))

class Quad:

    def __init__(self):
        #x, y, z
        self.vertices = (
            -0.5, 0.5, 0.0, #top left
            0.5, 0.5, 0.0, #top right
            0.5, -0.5, 0.0, #bottom right
            -0.5, -0.5, 0.0 #bottom left
        )

        self.vertices = np.array(self.vertices, dtype=np.float32)
        self.vertex_count = len(self.vertices) // 3 # 6 is the number of numbers in each row #the result is 3
        self.vao = glGenVertexArrays(1)#### make 1 slot only so make it two 
        glBindVertexArray(self.vao)###
        self.vbo = glGenBuffers(1)#####
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)######
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW) ########ship the data to the graphics card
        
        glEnableVertexAttribArray(0)#attribute 0 is position 
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 12, ctypes.c_void_p(0)) #describe how attribute 0 is laid out in the vbo
        #each vertex has 3 numbers x 4 bytes = 12 
    #free the memory
    def destroy(self):
        glDeleteVertexArrays(1, (self.vao, ))
        glDeleteBuffers(1, (self.vbo, ))





if __name__ == "__main__":
    myApp = App()