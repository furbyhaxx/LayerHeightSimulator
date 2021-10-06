import trimesh
trimesh.util.attach_to_log()

input_file = "input/test_2d.dxf"

if 'dxf' in trimesh.available_formats():
    plane2d = trimesh.load(input_file)

    extrusion = plane2d.extrude(height=5.0)

    extrusion.export('output/2d_extrusion_test.stl')