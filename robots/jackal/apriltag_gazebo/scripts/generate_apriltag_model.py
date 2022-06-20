import os
import sys

path = input("Enter the folder's name: ")
tag_id = input("Enter the apriltag's ID: ")
pose = input("Enter the pose: ")

# Check if folder already exists
if os.path.isdir(path):
    print("Folder already exists.")
    sys.exit()

# Create folders
os.mkdir(path)
os.mkdir(path + "/materials")
os.mkdir(path + "/meshes")
os.mkdir(path + "/materials/textures")

# Create sdf file
with open(path + '/model.sdf', 'w') as f:
    f.write("<?xml version=\"1.0\"?> \n"
            "<sdf version=\"1.5\"> \n"
            "  <model name=\"apriltag_" + tag_id + "\"> \n"
            "    <pose>" + pose + "</pose> \n"
            "    <static>true</static> \n"
            "    <link name='link'> \n"
            "      <collision name='collision'> \n"
            "        <geometry> \n"
            "          <box> \n"
            "            <size>1 1 1</size> \n"
            "          </box> \n"
            "        </geometry> \n"
            "      </collision> \n"
            "      <visual name='visual'> \n"
            "        <pose>0 0 0 0 0 0</pose> \n"
            "        <geometry> \n"
            "          <mesh> \n"
            "            <uri>model://apriltag_" + tag_id + "/meshes/apriltag_" + tag_id + ".dae</uri> \n"
            "          </mesh> \n"
            "        </geometry> \n"
            "      </visual> \n"
            "    </link> \n"
            "  </model> \n"
            "</sdf>")

# Create model.config file
with open(path + '/model.config', 'w') as f:
    f.write("<?xml version=\"1.0\"?> \n"
            "<model> \n"
            "    <name>apriltag_" + tag_id + "</name> \n"
            "    <version>1.0</version> \n"
            "    <sdf version=\"1.5\">model.sdf</sdf> \n"
            "    <author> \n"
            "        <name>My name</name> \n"
            "        <email>name@email.address</email> \n"
            "    </author> \n"
            "    <description> \n"
            "        describe your model \n"
            "    </description> \n"
            "</model>")

# Create meshes/.dae file
with open(path + '/meshes/apriltag_' + tag_id + '.config', 'w') as f:
    f.write("<?xml version='1.0' encoding='utf-8'?> \n"
            "<COLLADA xmlns=\"http://www.collada.org/2005/11/COLLADASchema\" version=\"1.4.1\" xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\"> \n"
            "  <asset> \n"
            "    <contributor> \n"
            "      <author>Blender User</author> \n"
            "      <authoring_tool>Blender 3.2.0 commit date:2022-06-08, commit time:10:22, hash:e05e1e369187</authoring_tool> \n"
            "    </contributor> \n"
            "    <created>2022-06-13T16:19:44</created> \n"
            "    <modified>2022-06-13T16:19:44</modified> \n"
            "    <unit name=\"meter\" meter=\"1\"/> \n"
            "    <up_axis>Z_UP</up_axis> \n"
            "  </asset> \n"
            "  <library_cameras> \n"
            "    <camera id=\"Camera-camera\" name=\"Camera\"> \n"
            "      <optics> \n"
            "        <technique_common> \n"
            "          <perspective> \n"
            "            <xfov sid=\"xfov\">39.59775</xfov> \n"
            "            <aspect_ratio>1.777778</aspect_ratio> \n"
            "            <znear sid=\"znear\">0.1</znear> \n"
            "            <zfar sid=\"zfar\">100</zfar> \n"
            "          </perspective> \n"
            "        </technique_common> \n"
            "      </optics> \n"
            "      <extra> \n"
            "        <technique profile=\"blender\"> \n"
            "            <shiftx sid=\"shiftx\" type=\"float\">0</shiftx> \n"
            "            <shifty sid=\"shifty\" type=\"float\">0</shifty> \n"
            "            <dof_distance sid=\"dof_distance\" type=\"float\">10</dof_distance> \n"
            "        </technique> \n"
            "      </extra> \n"
            "    </camera> \n"
            "  </library_cameras> \n"
            "  <library_lights> \n"
            "    <light id=\"Light-light\" name=\"Light\"> \n"
            "      <technique_common> \n"
            "        <point> \n"
            "          <color sid=\"color\">1000 1000 1000</color> \n"
            "          <constant_attenuation>1</constant_attenuation> \n"
            "          <linear_attenuation>0</linear_attenuation> \n"
            "          <quadratic_attenuation>0.00111109</quadratic_attenuation> \n"
            "        </point> \n"
            "      </technique_common> \n"
            "      <extra> \n"
            "        <technique profile=\"blender\"> \n"
            "          <type sid=\"type\" type=\"int\">0</type> \n"
            "          <flag sid=\"flag\" type=\"int\">0</flag> \n"
            "          <mode sid=\"mode\" type=\"int\">1</mode> \n"
            "          <gamma sid=\"blender_gamma\" type=\"float\">1</gamma> \n"
            "          <red sid=\"red\" type=\"float\">1</red> \n"
            "          <green sid=\"green\" type=\"float\">1</green> \n"
            "          <blue sid=\"blue\" type=\"float\">1</blue> \n"
            "          <shadow_r sid=\"blender_shadow_r\" type=\"float\">0</shadow_r> \n"
            "          <shadow_g sid=\"blender_shadow_g\" type=\"float\">0</shadow_g> \n"
            "          <shadow_b sid=\"blender_shadow_b\" type=\"float\">0</shadow_b> \n"
            "          <energy sid=\"blender_energy\" type=\"float\">1000</energy> \n"
            "          <dist sid=\"blender_dist\" type=\"float\">29.99998</dist> \n"
            "          <spotsize sid=\"spotsize\" type=\"float\">75</spotsize> \n"
            "          <spotblend sid=\"spotblend\" type=\"float\">0.15</spotblend> \n"
            "          <att1 sid=\"att1\" type=\"float\">0</att1> \n"
            "          <att2 sid=\"att2\" type=\"float\">1</att2> \n"
            "          <falloff_type sid=\"falloff_type\" type=\"int\">2</falloff_type> \n"
            "          <clipsta sid=\"clipsta\" type=\"float\">0.04999995</clipsta> \n"
            "          <clipend sid=\"clipend\" type=\"float\">30.002</clipend> \n"
            "          <bias sid=\"bias\" type=\"float\">1</bias> \n"
            "          <soft sid=\"soft\" type=\"float\">3</soft> \n"
            "          <bufsize sid=\"bufsize\" type=\"int\">2880</bufsize> \n"
            "          <samp sid=\"samp\" type=\"int\">3</samp> \n"
            "          <buffers sid=\"buffers\" type=\"int\">1</buffers> \n"
            "          <area_shape sid=\"area_shape\" type=\"int\">1</area_shape> \n"
            "          <area_size sid=\"area_size\" type=\"float\">0.1</area_size> \n"
            "          <area_sizey sid=\"area_sizey\" type=\"float\">0.1</area_sizey> \n"
            "          <area_sizez sid=\"area_sizez\" type=\"float\">1</area_sizez> \n"
            "        </technique> \n"
            "      </extra> \n"
            "    </light> \n"
            "  </library_lights> \n"
            "  <library_effects> \n"
            "    <effect id=\"Material-effect\"> \n"
            "      <profile_COMMON> \n"
            "        <newparam sid=\"apriltag_" + tag_id + "_png-surface\"> \n"
            "          <surface type=\"2D\"> \n"
            "            <init_from>apriltag_" + tag_id + "_png</init_from> \n"
            "          </surface> \n"
            "        </newparam> \n"
            "        <newparam sid=\"apriltag_" + tag_id + "_png-sampler\"> \n"
            "          <sampler2D> \n"
            "            <source>apriltag_" + tag_id + "_png-surface</source> \n"
            "          </sampler2D> \n"
            "        </newparam> \n"
            "        <technique sid=\"common\"> \n"
            "          <lambert> \n"
            "            <emission> \n"
            "              <color sid=\"emission\">0 0 0 1</color> \n"
            "            </emission> \n"
            "            <diffuse> \n"
            "              <texture texture=\"apriltag_" + tag_id + "_png-sampler\" texcoord=\"UVMap\"/> \n"
            "            </diffuse> \n"
            "            <index_of_refraction> \n"
            "              <float sid=\"ior\">1.45</float> \n"
            "            </index_of_refraction> \n"
            "          </lambert> \n"
            "        </technique> \n"
            "      </profile_COMMON> \n"
            "    </effect> \n"
            "  </library_effects> \n"
            "  <library_images> \n"
            "    <image id=\"apriltag_" + tag_id + "_png\" name=\"apriltag_" + tag_id + "_png\"> \n"
            "      <init_from>apriltag_" + tag_id + ".png</init_from> \n"
            "    </image> \n"
            "  </library_images> \n"
            "  <library_materials> \n"
            "    <material id=\"Material-material\" name=\"Material\"> \n"
            "      <instance_effect url=\"#Material-effect\"/> \n"
            "    </material> \n"
            "  </library_materials> \n"
            "  <library_geometries> \n"
            "    <geometry id=\"Cube-mesh\" name=\"Cube\"> \n"
            "      <mesh> \n"
            "        <source id=\"Cube-mesh-positions\"> \n"
            "          <float_array id=\"Cube-mesh-positions-array\" count=\"24\">0.5 0.5 -0.5 0.5 -0.5 -0.5 0.5 0.5 0.5 0.5 -0.5 0.5 -0.5 0.5 -0.5 -0.5 -0.5 -0.5 -0.5 0.5 0.5 -0.5 -0.5 0.5</float_array> \n"
            "          <technique_common> \n"
            "            <accessor source=\"#Cube-mesh-positions-array\" count=\"8\" stride=\"3\"> \n"
            "              <param name=\"X\" type=\"float\"/> \n"
            "              <param name=\"Y\" type=\"float\"/> \n"
            "              <param name=\"Z\" type=\"float\"/> \n"
            "            </accessor> \n"
            "          </technique_common> \n"
            "        </source> \n"
            "        <source id=\"Cube-mesh-normals\"> \n"
            "          <float_array id=\"Cube-mesh-normals-array\" count=\"30\">0 1 0 0 0 1 -1 0 0 0 -1 0 1 0 0 0 0 -1 0 1 0 -1 0 0 0 -1 0 1 0 0</float_array> \n"
            "          <technique_common> \n"
            "            <accessor source=\"#Cube-mesh-normals-array\" count=\"10\" stride=\"3\"> \n"
            "              <param name=\"X\" type=\"float\"/> \n"
            "              <param name=\"Y\" type=\"float\"/> \n"
            "              <param name=\"Z\" type=\"float\"/> \n"
            "            </accessor> \n"
            "          </technique_common> \n"
            "        </source> \n"
            "        <source id=\"Cube-mesh-map-0\"> \n"
            "          <float_array id=\"Cube-mesh-map-0-array\" count=\"72\">0.475066 0.5 0.4502915 0.5247746 0.4502915 0.5 0.4502915 0.5247746 0.425517 0.5495489 0.425517 0.5247746 0.4502915 0.4504511 0.425517 0.4752256 0.425517 0.4504511 0.425517 0.5 0.4007426 0.5247746 0.4007426 0.5 0.9991486 0.001822054 8.51393e-4 0.9999052 8.51393e-4 0.001821994 0.4502915 0.4752256 0.425517 0.5 0.425517 0.4752256 0.475066 0.5 0.475066 0.5247746 0.4502915 0.5247746 0.4502915 0.5247746 0.4502915 0.5495489 0.425517 0.5495489 0.4502915 0.4504511 0.4502915 0.4752256 0.425517 0.4752256 0.425517 0.5 0.425517 0.5247746 0.4007426 0.5247746 0.9991486 0.001822054 1.001736 0.9999052 8.51393e-4 0.9999052 0.4502915 0.4752256 0.4502915 0.5 0.425517 0.5</float_array> \n"
            "          <technique_common> \n"
            "            <accessor source=\"#Cube-mesh-map-0-array\" count=\"36\" stride=\"2\"> \n"
            "              <param name=\"S\" type=\"float\"/> \n"
            "              <param name=\"T\" type=\"float\"/> \n"
            "            </accessor> \n"
            "          </technique_common> \n"
            "        </source> \n"
            "        <vertices id=\"Cube-mesh-vertices\"> \n"
            "          <input semantic=\"POSITION\" source=\"#Cube-mesh-positions\"/> \n"
            "        </vertices> \n"
            "        <triangles material=\"Material-material\" count=\"12\"> \n"
            "          <input semantic=\"VERTEX\" source=\"#Cube-mesh-vertices\" offset=\"0\"/> \n"
            "          <input semantic=\"NORMAL\" source=\"#Cube-mesh-normals\" offset=\"1\"/> \n"
            "          <input semantic=\"TEXCOORD\" source=\"#Cube-mesh-map-0\" offset=\"2\" set=\"0\"/> \n"
            "          <p>4 0 0 2 0 1 0 0 2 2 1 3 7 1 4 3 1 5 6 2 6 5 2 7 7 2 8 1 3 9 7 3 10 5 3 11 0 4 12 3 4 13 1 4 14 4 5 15 1 5 16 5 5 17 4 6 18 6 6 19 2 6 20 2 1 21 6 1 22 7 1 23 6 7 24 4 7 25 5 7 26 1 8 27 3 8 28 7 8 29 0 9 30 2 9 31 3 9 32 4 5 33 0 5 34 1 5 35</p> \n"
            "        </triangles> \n"
            "      </mesh> \n"
            "    </geometry> \n"
            "  </library_geometries> \n"
            "  <library_visual_scenes> \n"
            "    <visual_scene id=\"Scene\" name=\"Scene\"> \n"
            "      <node id=\"Camera\" name=\"Camera\" type=\"NODE\"> \n"
            "        <matrix sid=\"transform\">0.6859207 -0.3240135 0.6515582 7.358891 0.7276763 0.3054208 -0.6141704 -6.925791 0 0.8953956 0.4452714 4.958309 0 0 0 1</matrix> \n"
            "        <instance_camera url=\"#Camera-camera\"/> \n"
            "      </node> \n"
            "      <node id=\"Light\" name=\"Light\" type=\"NODE\"> \n"
            "        <matrix sid=\"transform\">-0.2908646 -0.7711008 0.5663932 4.076245 0.9551712 -0.1998834 0.2183912 1.005454 -0.05518906 0.6045247 0.7946723 5.903862 0 0 0 1</matrix> \n"
            "        <instance_light url=\"#Light-light\"/> \n"
            "      </node> \n"
            "      <node id=\"Cube\" name=\"Cube\" type=\"NODE\"> \n"
            "        <matrix sid=\"transform\">1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1</matrix> \n"
            "        <instance_geometry url=\"#Cube-mesh\" name=\"Cube\"> \n"
            "          <bind_material> \n"
            "            <technique_common> \n"
            "              <instance_material symbol=\"Material-material\" target=\"#Material-material\"> \n"
            "                <bind_vertex_input semantic=\"UVMap\" input_semantic=\"TEXCOORD\" input_set=\"0\"/>  \n"
            "              </instance_material> \n"
            "            </technique_common> \n"
            "          </bind_material> \n"
            "        </instance_geometry> \n"
            "      </node> \n"
            "    </visual_scene> \n"
            "  </library_visual_scenes> \n"
            "  <scene> \n"
            "    <instance_visual_scene url=\"#Scene\"/> \n"
            "  </scene> \n"
            "</COLLADA> \n")
  
