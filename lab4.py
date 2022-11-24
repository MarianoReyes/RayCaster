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

model = Obj('./mask.obj')

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

# shaders

fragment_shader = """
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

fragment_shader2 = """
#version 460

vec2 iResolution = vec2(2, 2);
layout (location = 0) out vec4 fragColor;
in vec2 fragCoord;
uniform float iTime;
 
mat2 move(in float a) {
    float c = cos(a);
    float s = sin(a);
    return mat2(c, -s, s, -c);
}

float map(in vec3 st) {
    st.xy *= move(iTime * 0.3);
    st.xz *= move(iTime * 0.5);
    vec3 p = st * 2.0 + iTime;
    return length(st + vec3(sin(iTime * 0.5))) + sin(p.x + sin(p.y + sin(p.z))) * 0.5 - 2.0;
}

void main() {
    vec2 st = fragCoord / iResolution.xy - vec2(1.0, 0.5);

    vec3 col = vec3(0.0);
    float dist = 2.5;

    for (int i = 0; i <= 4; i++) {
        vec3 st = vec3(0.0, 0.0, 1.0) + normalize(vec3(st, -1.0)) * dist;
        float rz = map(st);
        float f = clamp((rz - map(st + 0.1)) * 0.5, -0.5, 1.0);
        vec3 l = vec3(0.1, 0.3, 0.4) + vec3(4.0, 2.5, 2.5) * f;
        col = col * l + smoothstep(5.0, 2.0, rz) * 0.4 * l;
        dist += min(rz, iTime);
    }

    fragColor = vec4(col,1.0);
}
"""

fragment_shader3 = """
#version 460

precision highp float;
vec2 iResolution = vec2(2, 2);
layout (location = 0) out vec4 fragColor;
in vec2 fragCoord;
uniform float iTime;


mat2 rot(float a) {
    float c = cos(a), s = sin(a);
    return mat2(c,s,-s,c);
}

const float pi = acos(-1.0);
const float pi2 = pi*2.0;

vec2 pmod(vec2 p, float r) {
    float a = atan(p.x, p.y) + pi/r;
    float n = pi2 / r;
    a = floor(a/n)*n;
    return p*rot(-a);
}

float box( vec3 p, vec3 b ) {
    vec3 d = abs(p) - b;
    return min(max(d.x,max(d.y,d.z)),0.0) + length(max(d,0.0));
}

float ifsBox(vec3 p) {
    for (int i=0; i<5; i++) {
        p = abs(p) - 1.0;
        p.xy *= rot(iTime*0.3);
        p.xz *= rot(iTime*0.1);
    }
    p.xz *= rot(iTime);
    return box(p, vec3(0.4,0.8,0.3));
}

float map(vec3 p, vec3 cPos) {
    vec3 p1 = p;
    p1.x = mod(p1.x-5., 10.) - 5.;
    p1.y = mod(p1.y-5., 10.) - 5.;
    p1.z = mod(p1.z, 16.)-8.;
    p1.xy = pmod(p1.xy, 5.0);
    return ifsBox(p1);
}

void main() {
    vec2 p = (fragCoord.xy * 2.0 - iResolution.xy) / min(iResolution.x, iResolution.y);

    vec3 cPos = vec3(0.0,0.0, -3.0 * iTime);
    // vec3 cPos = vec3(0.3*sin(iTime*0.8), 0.4*cos(iTime*0.3), -6.0 * iTime);
    vec3 cDir = normalize(vec3(0.0, 0.0, -1.0));
    vec3 cUp  = vec3(sin(iTime), 1.0, 0.0);
    vec3 cSide = cross(cDir, cUp);

    vec3 ray = normalize(cSide * p.x + cUp * p.y + cDir);

    // Phantom Mode https://www.shadertoy.com/view/MtScWW by aiekick
    float acc = 0.0;
    float acc2 = 0.0;
    float t = 0.0;
    for (int i = 0; i < 99; i++) {
        vec3 pos = cPos + ray * t;
        float dist = map(pos, cPos);
        dist = max(abs(dist), 0.02);
        float a = exp(-dist*3.0);
        if (mod(length(pos)+24.0*iTime, 30.0) < 3.0) {
            a *= 2.0;
            acc2 += a;
        }
        acc += a;
        t += dist * 0.5;
    }

    vec3 col = vec3(acc * 0.01, acc * 0.011 + acc2*0.002, acc * 0.012+ acc2*0.005);
    fragColor = vec4(col, 1.0 - t * 0.03);
}
"""

fragment_shader4 = """
#version 460

vec2 iResolution = vec2(2, 2);
layout (location = 0) out vec4 fragColor;
in vec2 fragCoord;
uniform float iTime;
float gTime;

mat2 rot(float a) {
	float c = cos(a), s = sin(a);
	return mat2(c,s,-s,c);
}

float sdBox( vec3 p, vec3 b )
{
	vec3 q = abs(p) - b;
	return length(max(q,0.0)) + min(max(q.x,max(q.y,q.z)),0.0);
}

float box(vec3 pos, float scale) {
	pos *= scale;
	float base = sdBox(pos, vec3(.4,.4,.1)) /1.5;
	pos.xy *= 5.;
	pos.y -= 3.5;
	pos.xy *= rot(.75);
	float result = -base;
	return result;
}

float box_set(vec3 pos, float iTime) {
	vec3 pos_origin = pos;
	pos = pos_origin;
	pos .y += sin(gTime * 0.4) * 2.5;
	pos.xy *=   rot(.8);
	float box1 = box(pos,2. - abs(sin(gTime * 0.4)) * 1.5);
	pos = pos_origin;
	pos .y -=sin(gTime * 0.4) * 2.5;
	pos.xy *=   rot(.8);
	float box2 = box(pos,2. - abs(sin(gTime * 0.4)) * 1.5);
	pos = pos_origin;
	pos .x +=sin(gTime * 0.4) * 2.5;
	pos.xy *=   rot(.8);
	float box3 = box(pos,2. - abs(sin(gTime * 0.4)) * 1.5);	
	pos = pos_origin;
	pos .x -=sin(gTime * 0.4) * 2.5;
	pos.xy *=   rot(.8);
	float box4 = box(pos,2. - abs(sin(gTime * 0.4)) * 1.5);	
	pos = pos_origin;
	pos.xy *=   rot(.8);
	float box5 = box(pos,.5) * 6.;	
	pos = pos_origin;
	float box6 = box(pos,.5) * 6.;	
	float result = max(max(max(max(max(box1,box2),box3),box4),box5),box6);
	return result;
}

float map(vec3 pos, float iTime) {
	vec3 pos_origin = pos;
	float box_set1 = box_set(pos, iTime);

	return box_set1;
}


void main() {
	vec2 p = (fragCoord.xy * 2. - iResolution.xy) / min(iResolution.x, iResolution.y);
	vec3 ro = vec3(0., -0.2 ,iTime * 4.);
	vec3 ray = normalize(vec3(p, 1.5));
	ray.xy = ray.xy * rot(sin(iTime * .03) * 5.);
	ray.yz = ray.yz * rot(sin(iTime * .05) * .2);
	float t = 0.1;
	vec3 col = vec3(0.);
	float ac = 0.0;


	for (int i = 0; i < 99; i++){
		vec3 pos = ro + ray * t;
		pos = mod(pos-2., 4.) -2.;
		gTime = iTime -float(i) * 0.01;
		
		float d = map(pos, iTime);

		d = max(abs(d), 0.01);
		ac += exp(-d*23.);

		t += d* 0.55;
	}

	col = vec3(ac * 0.02);

	col +=vec3(0.,0.2 * abs(sin(iTime)),0.5 + sin(iTime) * 0.2);


	fragColor = vec4(col ,1.0 - t * (0.02 + 0.02 * sin (iTime)));
}

/** SHADERDATA
{
	"title": "Octgrams",
	"description": "Lorem ipsum dolor",
	"model": "person"
}
*/
"""

compiled_vertex_shader = compileShader(vertex_shader, GL_VERTEX_SHADER)
compiled_fragment_shader = compileShader(fragment_shader, GL_FRAGMENT_SHADER)
compiled_fragment_shader2 = compileShader(fragment_shader2, GL_FRAGMENT_SHADER)
compiled_fragment_shader3 = compileShader(fragment_shader3, GL_FRAGMENT_SHADER)
compiled_fragment_shader4 = compileShader(fragment_shader4, GL_FRAGMENT_SHADER)

# compilar shaders

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

glUseProgram(shader)


# a partir de aca es logica para cargar objetos
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
    translate = glm.translate(i, glm.vec3(0, -0, 0))
    rotate = glm.rotate(i, glm.radians(angle), vector)
    scale = glm.scale(i, glm.vec3(13, 13, 13))

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


# se corre el programa

glClearColor(0.0, 0.0, 0.0, 1.0)
r = 0
cambiar = False
numero_shader = 0
shaders = [shader, shader2, shader3, shader4]
shader_actual = shader
vector = glm.vec3(0, 1, 0)

prev_time = pygame.time.get_ticks()

running = True
while running:
    glClear(GL_COLOR_BUFFER_BIT)

    # con esto se cambia de textura
    if cambiar == True:
        glUseProgram(shaders[numero_shader])
        shader_actual = shaders[numero_shader]
        cambiar = False

    color1 = random.random()
    color2 = random.random()
    color3 = random.random()

    color = glm.vec3(color1, color2, color3)
    glUniform3fv(
        glGetUniformLocation(shader_actual, "color"),
        1,
        glm.value_ptr(color)
    )

    time = (pygame.time.get_ticks() - prev_time) / 1000
    #time = pygame.time.get_ticks()
    glUniform1f(
        glGetUniformLocation(shader_actual, "time"),
        time
    )

    glDrawElements(GL_TRIANGLES, len(faces_data), GL_UNSIGNED_INT, None)

    calculateMatrix(r, vector)

    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_0:
                numero_shader = 0
                cambiar = True
            if event.key == pygame.K_1:
                numero_shader = 1
                cambiar = True
            if event.key == pygame.K_2:
                numero_shader = 2
                cambiar = True
            if event.key == pygame.K_3:
                numero_shader = 3
                cambiar = True

    keys = pygame.key.get_pressed()
    if keys[pygame.K_RIGHT]:
        vector = glm.vec3(0, 1, 0)
        r += 0.5
    if keys[pygame.K_LEFT]:
        vector = glm.vec3(0, 1, 0)
        r -= 0.5
