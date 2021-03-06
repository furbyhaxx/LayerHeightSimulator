import numpy as np
import trimesh
import os
from pathlib import Path

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


input_file = "input/fels_full.stl"

config = {
    'slice_start': 5,
    'slice_end': 810,
    'layer_height': 5.0,
    'export': {
        'stl': False,  # export stl file
        'single_slices_in_stl': True,
        'export_both': False,
        # should stl file contain a single body for each slice or be combined into one body?
        # False needs OpenSCAD and is much slower
        'png': False,  # export png for each slice
        'svg': True,  # export svg for each slice
        'dxf': True,  # export dxf for each slice
    }
}

# END CONFIG
############################

project_name = Path(input_file).stem
output_folder = f'./output/{project_name}/'

mesh = trimesh.load(input_file)
bounds = mesh.bounding_box.extents  # array(x,y,z)

if not os.path.exists(f'{output_folder}/'):
    os.makedirs(f'{output_folder}/')

current = config['slice_start']
meshes = []
# slice_end = config['slice_end'] + config['layer_height']

while current < config['slice_end']:
    # origin = mesh.centroid.copy()
    # origin[2] = origin[2] + current
    slice = mesh.section(plane_origin=[0, 0, current], plane_normal=[0, 0, config['layer_height']])

    if slice is not None:
        slice2d, to_3D = slice.to_planar()
        if config['export']['png']:
            if not os.path.exists(f'{output_folder}/png/'):
                os.makedirs(f'{output_folder}/png/')
            save_png(slice2d, f'{output_folder}/png/{current}.png')

        if config['export']['dxf']:
            if not os.path.exists(f'{output_folder}/dxf/'):
                os.makedirs(f'{output_folder}/dxf/')
            slice2d.export(f'{output_folder}/dxf/{current}.dxf')

        if config['export']['svg']:
            if not os.path.exists(f'{output_folder}/svg/'):
                os.makedirs(f'{output_folder}/svg/')
            slice2d.export(f'{output_folder}/svg/{current}.svg')

        # slice_2D.export('output/svg/' + str(current) + '.svg')
        extrusion = slice2d.extrude(height=config['layer_height'] + 0.05)

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

    current = current + config['layer_height']

if config['export']['stl'] and config['export']['single_slices_in_stl'] or config['export']['export_both']:
    print("Generating single bodies in STL")
    combined = trimesh.util.concatenate(meshes)
    combined.export(f'{output_folder}/{project_name}_bodies.stl')
if config['export']['stl'] and not config['export']['single_slices_in_stl'] or config['export']['export_both']:
    print("Combining bodies in STL")
    comb2 = meshes[0].union(meshes[1:], engine='scad', debug=True)
    comb2.export(f'{output_folder}/{project_name}_combined.stl')

# combined = trimesh.util.concatenate(meshes)
# combined.export('output/fels2.stl')
