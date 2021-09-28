import numpy as np
import trimesh

trimesh.util.attach_to_log()

def save_png(slice_2D, file):
    import matplotlib.pyplot as plt
    # keep plot axis scaled the same
    plt.axes().set_aspect('equal', 'datalim')
    # hardcode a format for each entity type
    eformat = {'Line0': {'color': 'g', 'linewidth': 1},
               'Line1': {'color': 'y', 'linewidth': 1},
               'Arc0': {'color': 'r', 'linewidth': 1},
               'Arc1': {'color': 'b', 'linewidth': 1},
               'Bezier0': {'color': 'k', 'linewidth': 1},
               'Bezier1': {'color': 'k', 'linewidth': 1},
               'BSpline0': {'color': 'm', 'linewidth': 1},
               'BSpline1': {'color': 'm', 'linewidth': 1}}
    for entity in slice_2D.entities:
        # if the entity has it's own plot method use it
        if hasattr(entity, 'plot'):
            entity.plot(slice_2D.vertices)
            continue
        # otherwise plot the discrete curve
        discrete = entity.discrete(slice_2D.vertices)
        # a unique key for entities
        e_key = entity.__class__.__name__ + str(int(entity.closed))

        fmt = eformat[e_key].copy()
        if hasattr(entity, 'color'):
            # if entity has specified color use it
            fmt['color'] = entity.color
        plt.plot(*discrete.T, **fmt)
        plt.savefig(file)

def move(extrusion, distance):
    distance = float(distance)
    translation = np.eye(4)
    translation[2, 3] = distance
    new_transform = np.dot(extrusion.primitive.transform.copy(),
                           translation.copy())
    extrusion.primitive.transform = new_transform


input_file = "input/fels_full.stl"
output_folder = "./output/fels_full/"

mesh = trimesh.load(input_file)
bounds = mesh.bounding_box.extents  # array(x,y,z)

slice_start = 0
slice_end = 725
layer_height = 5.0  #mm

current = slice_start

meshes = []

while current < slice_end:
    # origin = mesh.centroid.copy()
    # origin[2] = origin[2] + current
    slice = mesh.section(plane_origin=[0, 0, current], plane_normal=[0, 0, layer_height])

    if slice is not None:
        slice2d, to_3D = slice.to_planar()
        # save_png(slice2d, f'output/png/{current}.png')
        # slice2d.export(f'output/png/{current}.png')
        # slice_2D.export('output/svg/' + str(current) + '.svg')
        extrusion = slice2d.extrude(height=layer_height)

        if type(extrusion) is list:
            tmp_meshes = []
            for eitem in extrusion:
                # eitem.slide(current)
                # eitem.export(f'output/png/{current}-{idy}.png')
                tmp_meshes.append(eitem)
            tmp_combined = trimesh.util.concatenate(tmp_meshes)
            tmp_combined.apply_transform(to_3D)
            meshes.append(tmp_combined)
        else:
            # extrusion.slide(current)
            extrusion.apply_transform(to_3D)
            meshes.append(extrusion)

    current = current + layer_height

combined = trimesh.util.concatenate(meshes)
combined.export('output/fels_comb.stl')

# combined = trimesh.util.concatenate(meshes)
# combined.export('output/fels2.stl')
