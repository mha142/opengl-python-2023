import pygame as pg 
from OpenGL.GL import *
import numpy as np
from OpenGL.GL.shaders import compileProgram, compileShader
import pyrr
#seperate head from face 
#load them using the obj loader 
#transform them 

#convert from local to global coordinated and vice versa

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
        pg.init()
        pg.display.set_mode((640, 480), pg.OPENGL|pg.DOUBLEBUF)
        self.clock = pg.time.Clock()
        glClearColor(0.1, 0.2, 0.2, 1)
        glEnable(GL_DEPTH_TEST)
        self.shader = self.createShader(b'vertex_shader.txt', b'fragment_shader.txt')
        glUseProgram(self.shader)
        self.mesh = Mesh("basic_sphere.obj")
        x_center, y_center, z_center, x_size, y_size, z_size = self.mesh.return_cube_info()
        #self.quad = Quad()
        self.cube1 = Cube(
            #position = [0, 0, -3], #-3 (negative means put the object infront of the camera)
            position = [-1, 0, -6], #chnage the cube and the model position
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

        projection_transform = pyrr.matrix44.create_perspective_projection(
            fovy = 45, aspect = 640/480, 
            near = 0.01, far = 10, dtype=np.float32
        )
        #model_transform = pyrr.matrix44.create_from_translation(pyrr.Vector3([1, 0, 0]))
        #glUniformMatrix4fv(
        #    glGetUniformLocation(self.shader, "projection"), 
        #    1, GL_FALSE, projection_transform
        #)
        self.projection_location = glGetUniformLocation(self.shader, "projection")
        glUniformMatrix4fv(self.projection_location, 1, GL_FALSE, projection_transform)
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
            glBindVertexArray(self.mesh.vao)#the current model that we will draw
            glDrawArrays(GL_TRIANGLES, 0, self.mesh.vertex_count) ########
            #GL_LINE_LOOP
            
            #draw triangle 2
            glUniformMatrix4fv(self.modelMatrixLocation, 1, GL_FALSE, triagnle2_transform) #triagnle2_transform
            glBindVertexArray(self.mesh.vao)#the current model that we will draw
            glDrawArrays(GL_TRIANGLES, 0, self.mesh.vertex_count) ########


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

            #GL_POINTS
            pg.display.flip()
            #timing
            self.clock.tick(60)
        self.quit()

    def quit(self):
        self.mesh.destroy()
        glDeleteProgram(self.shader)
        pg.quit()

class Mesh:

    def __init__(self, filepath):
        self.vertices = self.loadMesh(filepath)
        '''   
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
        '''

        self.vertices = np.array(self.vertices, dtype=np.float32)
        
        #x, y, z, u, v
        self.vertex_count = len(self.vertices) // 5 # 6 is the number of numbers in each row #the result is 3
        self.vao = glGenVertexArrays(1)#### make 1 slot only so make it two 
        glBindVertexArray(self.vao)###
        self.vbo = glGenBuffers(1)##### make 1 slot only so make it two
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)######
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW) ########ship the data to the graphics card
        
        glEnableVertexAttribArray(0)#attribute 0 is position 
        #3 = the numbers in each row,// 20 = 5 numbers x 4 bytes ,// 0 = the position attribute starts at location 0  
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 20, ctypes.c_void_p(0)) #describe how attribute 0 is laid out in the vbo
        glEnableVertexAttribArray(1) #attribute 1 is color
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 20, ctypes.c_void_p(12)) #each vertex has 6 numbers  x 4 bytes = 24, the color attribute starts at position 12 (after 3 number = 3 numbers x 4 bytes = 12)
    
    def loadMesh(self, filepath):
        #raw, unassemebled data
        v = []
        vt = []

        vertices = []

        with open(filepath, "r") as f:
            line = f.readline()
            while line:
                firstSpace = line.find(" ")
                flag = line[0:firstSpace]

                if flag =="v":
                    line = line.replace("v ", "")
                    #[x, y, z]
                    line = line.split(" ")
                    l = [float(x) for x in line]
                    v.append(l)
                elif flag =="vt":
                    line = line.replace("vt ", "")
                    #[u, v]
                    line = line.split(" ")
                    l = [float(x) for x in line]
                    vt.append(l)
                elif flag =="f":
                    #face has 3 or more vertices in v/vt form
                    line = line.replace("f ", "")
                    line = line.replace('\n', "")#replace the end of the file 
                    #[../.. ../.. ../..]
                    line = line.split(" ")
                    faceVertices = []
                    faceTextures = []
                    for vertex in line:
                        #vertex form will be like this >> v/vt
                        #[vt, vn]
                        l = vertex.split("/")
                        position = int(l[0]) - 1 # -1 cuz python index starts from 0 and f 1/1 for example means the first vertex and the first texture beacuse the indexing in the obj file starts from 1 not 0 like python 
                        faceVertices.append(v[position])
                        texture = int(l[1]) - 1 
                        faceTextures.append(vt[texture])
                    #[0, 1, 2, 3] -> [0, 1, 2, 0, 2, 3]
                    triangles_in_face = len(line) - 2 
                    vertex_order = []
                    for i in range(triangles_in_face):
                        vertex_order.append(0)
                        vertex_order.append(i + 1) # 1 + 1
                        vertex_order.append(i + 2) #1 + 2
                    for i in vertex_order:
                        for x in faceVertices[i]:
                            vertices.append(x)#loading x y z
                        for x in faceTextures[i]:
                            vertices.append(x)#loading u v
                #read next line
                line = f.readline()
        return vertices

     
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



class Quad:

    def __init__(self):
        #x, y, z
        self.vertices = (
           -0.5,  0.5, 0.0, #top left
            0.5,  0.5, 0.0, #top right
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