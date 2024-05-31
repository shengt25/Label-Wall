import ezdxf
import open3d as o3d
import numpy as np
from sklearn.neighbors import KDTree
import json
import argparse
import os


# INTERPOLATE FUNCTIONS
def interpolate_line(start, end, density=100):
    """
    Interpolate points between two points.
    :param start: point(x, y, z)
    :param end: point(x, y, z)
    :param density: number of points per unit length
    :return: list of interpolated points
    """
    length = np.linalg.norm(end - start)
    num_points = int(length * density)
    return [start + t * (end - start) for t in np.linspace(0, 1, num_points)]


def interpolate_arc(center, radius, start_angle, end_angle, density=100):
    """
    Interpolate points on an arc. (Not tested yet)
    """
    start_angle_rad = np.radians(start_angle)
    end_angle_rad = np.radians(end_angle)
    theta = end_angle_rad - start_angle_rad
    length = abs(theta) * radius
    num_points = int(length * density)
    angles = np.radians(np.linspace(start_angle, end_angle, num_points))
    return [center + radius * np.array([np.cos(a), np.sin(a), 0]) for a in angles]


def interpolate_lwpolyline(points, density=100):
    """
    Interpolate points on a polyline.
    :param points: A list of points: [(x, y, z), (x, y, z), (x, y, z), ...]
    :param density: number of points per unit length
    :return: list of interpolated points
    """
    interpolated_points = []
    for i in range(len(points) - 1):
        interpolated_points.extend(interpolate_line(np.array(points[i][:3]), np.array(points[i + 1][:3]), density))
    return interpolated_points


# MAIN FUNCTIONS
def dxf_extract(filepath, extract_option):
    """Extract entities from a dxf file based on the given options."""
    # load dxf file
    doc = ezdxf.readfile(filepath)
    msp = doc.modelspace()
    entities = {}
    for entity in msp:
        # 1. traverse layers
        for layer, entity_types in extract_option.items():
            if entity.dxf.layer == layer:
                # 2. traverse entity types
                for entity_type, line_types in entity_types.items():
                    if entity.dxftype() == entity_type:
                        # 3. traverse line types
                        for line_type in line_types:
                            if entity.dxf.linetype == line_type:
                                # 4. add to dictionary list
                                if entity_type not in entities:
                                    entities[entity_type] = [entity]
                                else:
                                    entities[entity_type].append(entity)
                break  # break the loop if the layer is found
    return entities


def entities2pcd(dxf_entities, density=100):
    """Convert entities to point cloud object."""
    points = []
    # traverse entities
    for entity_type, entities in dxf_entities.items():
        # line
        if entity_type == "LINE":
            for line in entities:
                start = line.dxf.start
                end = line.dxf.end
                points.extend(interpolate_line(start, end, density))

        # lwpolyline
        elif entity_type == "LWPOLYLINE":
            for lwpolyline in entities:
                points.extend(interpolate_lwpolyline(lwpolyline.get_points(), density))

        elif entity_type == "ARC":
            raise RuntimeWarning("ARC not supported yet")

        else:
            raise RuntimeWarning(f"Entity type {entity_type} not supported")

    points_np = np.array(points)
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(points_np)
    return pcd


def label_wall(pcd, pcd_mask, distance_threshold=0.05, preview_mode=False, preview_sample_rate=0.01):
    """
    Label the wall points in the point cloud, ignoring the z-axis.
    :param pcd: point cloud of all points
    :param pcd_mask: point cloud of the flattened mask
    :param distance_threshold: distance threshold for considering a point close to the mask
    :param preview_mode: preview mode, only process a subset of points for faster visualization
    :param preview_sample_rate: percentage of points to sample in preview mode
    :return: labeled point cloud object (either full or sampled based on preview mode)
    """
    points = np.asarray(pcd.points)
    points_color = np.asarray(pcd.colors)
    points_mask = np.asarray(pcd_mask.points)

    # initialize colors if the point cloud does not have any
    if points_color.shape[0] == 0:
        points_color = np.zeros((len(points), 3))

    # sampling indices for preview mode
    if preview_mode:
        indices = np.random.choice(len(points), int(len(points) * preview_sample_rate), replace=False)
        sampled_points = points[indices]
        sampled_colors = points_color[indices]
    else:
        sampled_points = points
        sampled_colors = points_color
        indices = np.arange(len(points))  # Use all indices if not in preview mode

    # use KD-Tree for efficient distance calculations (on the XY coordinates only
    tree = KDTree(points_mask[:, :2])  # Consider only XY coordinates
    close_indices = tree.query_radius(sampled_points[:, :2], r=distance_threshold)

    # color the close points green
    for idx_array, point_idx in zip(close_indices, range(len(indices))):
        if len(idx_array) > 0:
            sampled_colors[point_idx] = [0.0, 1.0, 0.0]

    if preview_mode:
        # create a new point cloud for preview mode
        preview_pcd = o3d.geometry.PointCloud()
        preview_pcd.points = o3d.utility.Vector3dVector(sampled_points)
        preview_pcd.colors = o3d.utility.Vector3dVector(sampled_colors)
        return preview_pcd
    else:
        # update colors in the original point cloud
        pcd.colors = o3d.utility.Vector3dVector(sampled_colors)
        return pcd


if __name__ == "__main__":
    # define arguments parser
    parser = argparse.ArgumentParser(description="Label wall points in a point cloud based on a dxf format mask.")

    # position args
    parser.add_argument("dxf_file", type=str, help="path to input dxf file")
    parser.add_argument("ply_file", type=str, help="path to input ply file")

    # optional args
    parser.add_argument("-o", type=str, metavar='out.ply',
                        help="path to save labeled ply file, otherwise the output ply file will be saved as *_label.ply")
    parser.add_argument("-c", type=str, metavar='config.json',
                        help="config file for dxf extraction configuration (in json format)")
    parser.add_argument("-t", action="store_true", help="test with a fast visualization, without saving ply")
    parser.add_argument("-v", action="store_true", help="visualize result")

    # parse arguments
    args = parser.parse_args()
    dxf_filepath = args.dxf_file
    room_ply_filepath = args.ply_file

    if args.t:
        print("Test mode, not saving the labeled point cloud")

    if args.v:
        visualize_result = True
    else:
        visualize_result = False

    if args.c:
        config_file = args.c
    else:
        config_file = "default.config"

    if not os.path.exists(config_file):
        raise FileNotFoundError("Config file not found, please specify one or put default.config with the script.")
    dxf_extract_config = json.load(open(config_file))
    print(f"Using config {config_file}: {dxf_extract_config}")

    # prepare data
    print("Loading data...")
    entities = dxf_extract(dxf_filepath, dxf_extract_config)
    pcd_wall_mask = entities2pcd(entities)
    pcd_room = o3d.io.read_point_cloud(room_ply_filepath)

    if args.t:
        print("Test start:")
        print("(1/3) Please check wall mask generated by dxf file")
        o3d.visualization.draw_geometries([pcd_wall_mask])
        print("(2/3) Please check alignment of wall mask and room")
        o3d.visualization.draw_geometries([pcd_wall_mask, pcd_room])
        pcd_labeled = label_wall(pcd_room, pcd_wall_mask, preview_mode=True)
        print("(3/3) Please check labeled point cloud (1% sampled)")
        o3d.visualization.draw_geometries([pcd_labeled, pcd_wall_mask])
        print("Test finished. (ply file not saved)")

    else:
        if args.o:
            save_ply_filepath = args.o
        else:
            save_ply_filepath = room_ply_filepath[:-4] + "_label.ply"
            if os.path.exists(save_ply_filepath):
                i = 0
                while os.path.exists(save_ply_filepath):
                    i += 1
                    save_ply_filepath = room_ply_filepath[:-4] + f"_label_{i}.ply"
            print(f"Output file not specified, will be saved to {save_ply_filepath}")

        print("Labeling, please wait...")
        pcd_labeled = label_wall(pcd_room, pcd_wall_mask)
        o3d.io.write_point_cloud(save_ply_filepath, pcd_labeled)
        print(f"Done, saved to {save_ply_filepath}")
        if visualize_result:
            print("Visualizing labeled result")
            o3d.visualization.draw_geometries([pcd_labeled, pcd_wall_mask])