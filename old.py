import numpy as np
import trimesh

# attach to logger so trimesh messages will be printed to console
trimesh.util.attach_to_log()


layer_height = 5.0  #mm
input_file = "input/fels_full.stl"
output_folder = "./output/fels_full/"

mesh = trimesh.load(input_file)
bounds = mesh.bounding_box.extents  # array(x,y,z)

# # get a single cross section of the mesh
# slice = mesh.section(plane_origin=mesh.centroid,
#                      plane_normal=[0,0,725])
#
# # the section will be in the original mesh frame
# # slice.show()
#
#
# # we can move the 3D curve to a Path2D object easily
# slice_2D, to_3D = slice.to_planar()
# slice_2D.show()

# if we wanted to take a bunch of parallel slices, like for a 3D printer
# we can do that easily with the section_multiplane method
# we're going to slice the mesh into evenly spaced chunks along z
# this takes the (2,3) bounding box and slices it into [minz, maxz]
z_extents = mesh.bounds[:,2]
# slice every .125 model units (eg, inches)
z_levels = np.arange(*z_extents, step=layer_height)

# find a bunch of parallel cross sections
sections = mesh.section_multiplane(plane_origin=mesh.bounds[0],
                                   plane_normal=[0,0,1],
                                   heights=z_levels)
# sections[1].export('output/test.svg')
# smesh = sections[1].extrude(height=5.0)
# smesh.export('output/test.stl')

meshes = []

for idx, item in enumerate(sections):
    if item is not None:
        # if idx == 1:
        #     meshes = np.array([item.extrude(height=layer_height)])
        # else:
        #     np.append(meshes, [item.extrude(height=layer_height)])
        extrusion = item.extrude(height=layer_height)

        center_mass = extrusion.center_mass
        translation = extrusion.get_center()  # box offset + plane offset
        translation[2] = idx * layer_height

        if type(extrusion) is list:
            for eitem in extrusion:
                eitem.apply_transform(translation)
                meshes.append(eitem)
        else:
            extrusion.apply_transform(translation)
            meshes.append(extrusion)

# meshes = np.array(meshes)

meshes2 = [trimesh.creation.box() for i in range(10)]

combined = trimesh.util.concatenate(meshes)
combined.export('output/fels.stl')

# def run():
#     input_file = "input/fels_full.stl"
#     # load a file by name or from a buffer
#     mesh = trimesh.load('input/fels_full.stl')
#     #mesh.show()
#     print(mesh.bounding_box.extents)
#
#
# # Press the green button in the gutter to run the script.
# if __name__ == '__main__':
#     run()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
