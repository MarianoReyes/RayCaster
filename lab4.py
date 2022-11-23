import pygame
import glm
import random
import numpy as np
from obj import *
from OpenGL.GL import *
from OpenGL.GL.shaders import *

pygame.init()

screen = pygame.display.set_mode(
    (800, 600),
    pygame.OPENGL | pygame.DOUBLEBUF
)

model = Obj('./cajaybarril.obj')

vertex_shader = """
#version 460
layout (location = 0) in vec3 position;
layout (location = 1) in vec3 vertexColor;

uniform mat4 matrix;

out vec3 ourColor;
out vec2 fragCoord;

void main()
{
    gl_Position = matrix * vec4(position, 1.0f);
    ourColor = vertexColor;
    fragCoord = gl_Position.xy;
}
"""

fragment_shader = """
#version 460
layout (location = 0) out vec4 fragColor;

uniform vec3 color;

in vec3 ourColor;

void main()
{
    //fragColor = vec4(color, 1.0f);
    fragColor = vec4(ourColor, 1.0f);
}
"""

fragment_shader2 = """
#version 460
layout (location = 0) out vec4 fragColor;

uniform vec3 color;
in vec3 ourColor;

void main()
{
    //fragColor = vec4(ourColor, 1.0f);
    fragColor = vec4(color, 1.0f);

}
"""

fragment_shader3 = """
#version 460
layout (location = 0) out vec4 fragColor;

uniform vec3 color;
in vec3 ourColor;

void main()
{
    //fragColor = vec4(ourColor, 1.0f);
    fragColor = vec4(color, 1.0f);

}
"""

fragment_shader4 = """
#version 460
layout (location = 0) out vec4 fragColor;

uniform vec3 color;
in vec3 ourColor;

void main()
{
    //fragColor = vec4(ourColor, 1.0f);
    fragColor = vec4(color, 1.0f);

}
"""

compiled_vertex_shader = compileShader(vertex_shader, GL_VERTEX_SHADER)
compiled_fragment_shader = compileShader(fragment_shader, GL_FRAGMENT_SHADER)
compiled_fragment_shader2 = compileShader(fragment_shader2, GL_FRAGMENT_SHADER)
compiled_fragment_shader3 = compileShader(fragment_shader3, GL_FRAGMENT_SHADER)
compiled_fragment_shader4 = compileShader(fragment_shader4, GL_FRAGMENT_SHADER)

shader = compileProgram(
    compiled_vertex_shader,
    compiled_fragment_shader
)

shader2 = compileProgram(
    compiled_vertex_shader,
    compiled_fragment_shader2
)

shader3 = compileProgram(
    compiled_vertex_shader,
    compiled_fragment_shader3
)

shader4 = compileProgram(
    compiled_vertex_shader,
    compiled_fragment_shader4
)

glUseProgram(shader2)

vertex = []
for ver in model.vertices:
    for v in ver:
        vertex.append(v)

vertex_data = np.array(vertex, dtype=np.float32)

faces = []
for face in model.faces:
    for f in face:
        faces.append(int(f[0])-1)

faces_data = np.array(faces, dtype=np.int32)


vertex_array_object = glGenVertexArrays(1)
glBindVertexArray(vertex_array_object)

vertex_buffer_object = glGenBuffers(1)
glBindBuffer(GL_ARRAY_BUFFER, vertex_buffer_object)
glBufferData(
    GL_ARRAY_BUFFER,  # tipo de datos
    vertex_data.nbytes,  # tamaño de los datos en bytes
    vertex_data,  # puntero a la data
    GL_STATIC_DRAW  # tipo de uso de la data
)

glVertexAttribPointer(
    0,
    3,
    GL_FLOAT,
    GL_FALSE,
    3 * 4,
    ctypes.c_void_p(0)
)

glEnableVertexAttribArray(0)


element_buffer_object = glGenBuffers(1)
glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, element_buffer_object)
glBufferData(GL_ELEMENT_ARRAY_BUFFER, faces_data.nbytes,
             faces_data, GL_STATIC_DRAW)


def calculateMatrix(angle, vector):

    i = glm.mat4(1)
    translate = glm.translate(i, glm.vec3(0, 0, -5))
    rotate = glm.rotate(i, glm.radians(angle), vector)
    scale = glm.scale(i, glm.vec3(1, 1, 1))

    """ translate = glm.translate(i, glm.vec3(0, -1, -15))
    rotate = glm.rotate(i, glm.radians(angle), vector)
    scale = glm.scale(i, glm.vec3(0.6, 0.6, 0.6)) """

    model = translate * rotate * scale

    view = glm.lookAt(
        glm.vec3(0, 0, 5),
        glm.vec3(0, 0, 0),
        glm.vec3(0, 1, 0)
    )

    projection = glm.perspective(
        glm.radians(45),
        1600 / 1200,
        0.1,
        1000
    )

    glViewport(0, 0, 800, 600)

    matrix = projection * view * model

    glUniformMatrix4fv(
        glGetUniformLocation(shader, "matrix"),
        1,
        GL_FALSE,
        glm.value_ptr(matrix)
    )


running = True

glClearColor(0.0, 1.0, 1.0, 1.0)
r = 0
changeShader = False
shaderIndex = 0
shaders = [shader2, shader3, shader4]
currentShader = shader2
vector = glm.vec3(0, 1, 0)

prev_time = pygame.time.get_ticks()

while running:
    glClear(GL_COLOR_BUFFER_BIT)

    if changeShader:
        glUseProgram(shaders[shaderIndex])
        currentShader = shaders[shaderIndex]
        changeShader = False

    color1 = random.random()
    color2 = random.random()
    color3 = random.random()

    color = glm.vec3(color1, color2, color3)
    glUniform3fv(
        glGetUniformLocation(currentShader, "color"),
        1,
        glm.value_ptr(color)
    )

    time = (pygame.time.get_ticks() - prev_time) / 1000
    #time = pygame.time.get_ticks()
    glUniform1f(
        glGetUniformLocation(currentShader, "time"),
        time
    )

    glDrawElements(GL_TRIANGLES, len(faces_data), GL_UNSIGNED_INT, None)

    calculateMatrix(r, vector)

    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                shaderIndex = 0
                changeShader = True
            if event.key == pygame.K_2:
                shaderIndex = 1
                changeShader = True
            if event.key == pygame.K_3:
                shaderIndex = 2
                changeShader = True

    keys = pygame.key.get_pressed()
    if keys[pygame.K_RIGHT]:
        vector = glm.vec3(0, 1, 0)
        r += 0.5
    if keys[pygame.K_LEFT]:
        vector = glm.vec3(0, 1, 0)
        r -= 0.5
    if keys[pygame.K_UP]:
        vector = glm.vec3(1, 0, 0)
        r += 0.5
    if keys[pygame.K_DOWN]:
        vector = glm.vec3(1, 0, 0)
        r -= 0.5
