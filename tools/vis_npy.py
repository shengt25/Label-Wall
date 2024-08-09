import open3d as o3d
import numpy as np
import sys


def visualize_npy(npy_pcd, fg_label=2):
    points = npy_pcd[:, :3]
    colors = npy_pcd[:, 3:6] / 255.0
    labels = npy_pcd[:, 6]

    original_pcd = o3d.geometry.PointCloud()
    original_pcd.points = o3d.utility.Vector3dVector(points)
    original_pcd.colors = o3d.utility.Vector3dVector(colors)

    # create point cloud with label
    labeled_pcd = o3d.geometry.PointCloud()
    labeled_pcd.points = o3d.utility.Vector3dVector(points)

    # color the points with the label fg_label green
    green_color = np.array([0, 1, 0])
    labeled_colors = np.copy(colors)
    labeled_colors[labels == fg_label] = green_color

    labeled_pcd.colors = o3d.utility.Vector3dVector(labeled_colors)

    # move the labeled point cloud to the right
    translation = np.array([1.5 * (np.max(points[:, 0]) - np.min(points[:, 0])), 0, 0])
    labeled_pcd.translate(translation)

    # visualize the original and labeled point clouds
    o3d.visualization.draw_geometries([original_pcd, labeled_pcd])


def main():
    if len(sys.argv) == 2:
        npy_file = sys.argv[1]
        fg_label = 2
    elif len(sys.argv) == 3:
        npy_file = sys.argv[1]
        fg_label = int(sys.argv[2])
    else:
        print("Usage: python vis_npy.py <npy_file> [fg_label]")
        sys.exit(1)

    npy_pcd = np.load(npy_file)
    visualize_npy(npy_pcd, fg_label)


if __name__ == "__main__":
    main()
