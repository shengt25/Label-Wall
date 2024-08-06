import open3d as o3d
import numpy as np
import sys


def ply2npy(file_path):
    pcd = o3d.io.read_point_cloud(file_path)
    points = np.asarray(pcd.points)
    colors = np.asarray(pcd.colors)

    # XYZRGBL
    output_data = np.zeros((points.shape[0], 7))

    # XYZ
    output_data[:, 0:3] = points

    # set all colors to 200 (gray)
    output_data[:, 3:6] = 200

    # Set label for foreground and background
    fg_label = 2
    bg_label = 12

    # if the point is green, set the label
    is_green = np.all(colors == [0.0, 1.0, 0.0], axis=1)
    output_data[:, 6] = np.where(is_green, fg_label, bg_label)

    # save
    np.save(file_path.replace(".ply", ".npy"), output_data)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Error, please check parameter: <path_to_ply_file>")
        sys.exit(1)

    file_path = sys.argv[1]
    ply2npy(file_path)
    print("Conversion completed, saved to", file_path.replace(".ply", ".npy"))
