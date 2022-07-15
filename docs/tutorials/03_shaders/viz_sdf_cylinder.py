"""
===============================================================================
Make a Cylinder using polygons vs SDF
===============================================================================
This tutorial is intended to show two ways of primitives creation with the use
of polygons, and SDFs. We will use cylinders as an example since they have a
simpler polygonal representation. Hence, it allows us to see better the
difference between using one or the other method.

For the cylinder representation with polygons, we will use cylinder actor
implementation on FURY, and for the visualization using SDFs, we will
implement shader code to create the cylinder and use a box actor to put our
implementation inside.

We start by importing the necessary modules:
"""

from fury import actor, window
from fury.shaders import compose_shader, shader_to_actor, attribute_to_actor

import numpy as np

###############################################################################
# Cylinder using polygons
# ================
# Polygons-based modeling, use smaller components namely triangles or polygons
# to represent 3D objects. Each polygon is defined by the position of its
# vertices and its connecting edges. In order to get a better representation
# of an object, it may be necessary to increase the number of polygons in the
# model, which is translated into the use of more space to store data and more
# rendering time to display the object.
#
# Now we define some properties of our actors, use them to create a set of
# cylinders, and add them to the scene.

centers = np.array([[-3.2, .9, .4], [-3.5, -.5, 1], [-2.1, 0, .4],
                    [-.2, .9, .4], [-.5, -.5, 1], [.9, 0, .4],
                    [2.8, .9, 1.4], [2.5, -.5, 2], [3.9, 0, 1.4]])
dirs = np.array([[-.2, .9, .4], [-.5, -.5, 1], [.9, 0, .4], [-.2, .9, .4],
                 [-.5, -.5, 1], [.9, 0, .4], [-.2, .9, .4], [-.5, -.5, 1],
                 [.9, 0, .4]])
colors = np.array([[1, 0, 0], [1, 0, 0], [1, 0, 0], [0, 1, 0], [0, 1, 0],
                   [0, 1, 0], [0, 0, 1], [0, 0, 1], [0, 0, 1]])

###############################################################################
# In order to see how cylinders are made, we set different resolutions (number
# of sides used to define the bases of the cylinder) to see how it changes the
# surface of the primitive.

radius = .5
height = 1

cylinders_8 = actor.cylinder(centers[:3], dirs[:3], colors[:3], radius=radius,
                             heights=height, capped=True, resolution=8)
cylinders_16 = actor.cylinder(centers[3: 6], dirs[3: 6], colors[3: 6],
                              radius=radius, heights=height, capped=True,
                              resolution=16)
cylinders_32 = actor.cylinder(centers[6: 9], dirs[6: 9], colors[6: 9],
                              radius=radius, heights=height, capped=True,
                              resolution=32)

###############################################################################
# Next, we set up a new scene to add and visualize the actors created.

scene = window.Scene()

scene.add(cylinders_8)
scene.add(cylinders_16)
scene.add(cylinders_32)

interactive = False

if interactive:
    window.show(scene)

window.record(scene, size=(600, 600), out_path='viz_poly_cylinder.png')

###############################################################################
# Visualize the surface geometry representation for the object.

cylinders_8.GetProperty().SetRepresentationToWireframe()
cylinders_16.GetProperty().SetRepresentationToWireframe()
cylinders_32.GetProperty().SetRepresentationToWireframe()

if interactive:
    window.show(scene)

###############################################################################
# Then we clean the scene to render the boxes.

window.record(scene, size=(600, 600), out_path='viz_poly_cylinder_geom.png')

scene.clear()

###############################################################################
# Cylinder using SDF
# ================
# We will use the ray marching algorithm to render the SDF primitive using
# shaders. Signed Distance Functions (SDFs) are mathematical functions that
# determine the distance from a point in space to a surface. Ray marching is
# a technique where you step along a ray in order to find intersections with
# solid geometry. Objects in the scene are defined by SDF, and because we
# don’t use polygonal meshes it is possible to define perfectly smooth
# surfaces and allows a faster rendering in comparison to polygon-based
# modeling.

###############################################################################
# Now we create cylinders using box actor and SDF implementation on shaders.
# For this, we first create a box actor.

box_actor = actor.box(centers=centers, directions=dirs, colors=colors,
                      scales=(height, radius*2, radius*2))

box_actor.GetProperty().SetRepresentationToWireframe()
scene.add(box_actor)

if interactive:
    window.show(scene)

window.record(scene, size=(600, 600), out_path='viz_sdf_cylinder_box.png')

scene.clear()

###############################################################################
# Now we use attribute_to_actor to link a NumPy array, with the centers and
# directions data, with a vertex attribute. We do this to pass the data to
# the vertex shader, with the corresponding attribute name.

rep_directions = np.repeat(dirs, 8, axis=0)
rep_centers = np.repeat(centers, 8, axis=0)
rep_radii = np.repeat(np.repeat(radius, 9), 8, axis=0)
rep_heights = np.repeat(np.repeat(height, 9), 8, axis=0)

attribute_to_actor(box_actor, rep_centers, 'center')
attribute_to_actor(box_actor, rep_directions, 'direction')
attribute_to_actor(box_actor, rep_radii, 'radius')
attribute_to_actor(box_actor, rep_heights, 'height')

###############################################################################
# Then we have the shader code implementation corresponding to vertex and
# fragment shader. Here we are passing data to the fragment shader through
# the vertex shader.
#
# Vertex shaders perform basic processing of each individual vertex.

sdf_cylinder_vert_dec = \
'''

in vec3 center;
in vec3 direction;
in float height;
in float radius;

out vec4 vertexMCVSOutput;
out vec3 centerWCVSOutput;
out vec3 directionVSOutput;
out float heightVSOutput;
out float radiusVSOutput;

'''

sdf_cylinder_vert_impl = \
'''

vertexMCVSOutput = vertexMC;
centerWCVSOutput = center;
directionVSOutput = direction;
heightVSOutput = height;
radiusVSOutput = radius;

'''

###############################################################################
# Fragment shaders are used to define the colors of each pixel being processed,
# the program runs on each of the pixels that the object occupies on the screen.
#
# Vertex shaders also allow us to have control over details of position,
# movement, lighting, and color in a scene. In this case, we are using vertex
# shader not just to define the colors of the cylinders but to manipulate its
# position in world space, rotation with respect to the box, and lighting of
# the scene.

sdf_cylinder_frag_dec = \
'''

in vec4 vertexMCVSOutput;

in vec3 centerWCVSOutput;
in vec3 directionVSOutput;
in float heightVSOutput;
in float radiusVSOutput;

uniform mat4 MCVCMatrix;


// A rotation matrix is used to transform our position vectors in order to
// align the direction of cylinder with respect to the box
mat4 rotationMatrix(vec3 u, vec3 v)
{
    // Cross product is the first step to find R
    vec3 w = cross(u, v);
    float wn = length(w);

    // Check that cross product is OK and vectors u, v are not collinear
    // (norm(w)>0.0)
    if(isnan(wn) || wn < 0.0)
    {
        float normUV = length(u - v);
        // This is the case of two antipodal vectors:
        // ** former checking assumed norm(u) == norm(v)
        if(normUV > length(u))
            return mat4(-1);
        return mat4(1);
    }

    // if everything ok, normalize w
    w = w / wn;

    // vp is in plane of u,v,  perpendicular to u
    vec3 vp = (v - dot(u, v) * u);
    vp = vp / length(vp);
    
    // (u vp w) is an orthonormal basis
    mat3 Pt = mat3(u, vp, w);
    mat3 P = transpose(Pt);

    float cosa = clamp(dot(u, v), -1, 1);
    float sina = sqrt(1 - pow(cosa, 2));

    mat3 R = mat3(mat2(cosa, sina, -sina, cosa));
    mat3 Rp = Pt * (R * P);

    // make sure that you don't return any Nans
    bool anyNanCheckRp0 = any(isnan(Rp[0]));
    bool anyNanCheckRp1 = any(isnan(Rp[1]));
    bool anyNanCheckRp2 = any(isnan(Rp[2]));
    if(anyNanCheckRp0 || anyNanCheckRp1 || anyNanCheckRp2)
        return mat4(1);

    return mat4(Rp);
}


// SDF for the cylinder
float sdCylinder( vec3 p, float r, float h )
{
    vec2 d = abs(vec2(length(p.xz),p.y)) - vec2(r,h);
    return min(max(d.x,d.y),0.0) + length(max(d,0.0));
}

// This is used on calculations for surface normals of the cylinder
float map( in vec3 position )
{
    mat4 rot = rotationMatrix(normalize(directionVSOutput), normalize(vec3(0, 1, 0)));

    // this allows us to accommodate more than one object in the world space
    vec3 pos = (rot*vec4(position - centerWCVSOutput, 0.0)).xyz;

    // distance to the cylinder
    return sdCylinder(pos, radiusVSOutput, heightVSOutput/2);
}
  
  
// We need surface normals when doing lighting of the scene
vec3 calculateNormal( in vec3 position )
{
    vec2 e = vec2(0.001, 0.0);
    return normalize( vec3( map(position + e.xyy) - map(position - e.xyy),
                            map(position + e.yxy) - map(position - e.yxy),
                            map(position + e.yyx) - map(position - e.yyx)));
}


// Ray Marching
float castRay( in vec3 ro, vec3 rd )
{
    float t = 0.0;
    for(int i=0; i < 4000; i++){
        vec3 position = ro + t * rd;
        float  h = map(position);
        t += h;
           if ( t > 20.0 || h < 0.001) break;
    }
    return t;
}
'''

sdf_cylinder_frag_impl = \
'''

vec3 point = vertexMCVSOutput.xyz;

// ray origin
vec4 ro = -MCVCMatrix[3] * MCVCMatrix;  // camera position in world space

vec3 col = vertexColorVSOutput.rgb;

// ray direction
vec3 rd = normalize(point - ro.xyz);

// light direction
vec3 ld = normalize(ro.xyz - point);

ro += vec4((point - ro.xyz),0.0);

float t = castRay(ro.xyz, rd);

if(t < 20.0)
{
    vec3 position = ro.xyz + t * rd;
    vec3 norm = calculateNormal(position);
    float lightAttenuation = dot(ld, norm);
    
    // calculate the diffuse factor and diffuse color
    df = max(0, lightAttenuation);
    diffuse = df * diffuseColor * lightColor0;
        
    // calculate the specular factor and specular color
    sf = pow(df, specularPower);
    specular = sf * specularColor * lightColor0;
    
    // Blinn-Phong illumination model
    fragOutput0 = vec4(ambientColor + diffuse + specular, opacity);
}
else{
    discard;
}
'''

###############################################################################
# Finally, we add shader code implementation to the box_actor. We use
# shader_to_actor to apply our implementation to the shader creation process,
# this function joins our code to the shader template that FURY has by default.

shader_to_actor(box_actor, "vertex", impl_code=sdf_cylinder_vert_impl,
                decl_code=sdf_cylinder_vert_dec)
shader_to_actor(box_actor, "fragment", decl_code=sdf_cylinder_frag_dec)
shader_to_actor(box_actor, "fragment", impl_code=sdf_cylinder_frag_impl,
                block="light")

box_actor.GetProperty().SetRepresentationToSurface()
scene.add(box_actor)

if interactive:
    window.show(scene)

window.record(scene, size=(600, 600), out_path='viz_sdf_cylinder.png')
