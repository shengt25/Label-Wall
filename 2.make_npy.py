import numpy as np
import open3d as o3d
import argparse
import os
from util.visualize_npy import visualize_npy


def create_npy(original_pcd, mask_pcd, fg_label=2, bg_label=12):
    original_points = np.asarray(original_pcd.points)
    original_colors = np.asarray(original_pcd.colors) * 255  # Scale colors by 255 in original point cloud

    mask_points = np.asarray(mask_pcd.points)
    mask_colors = np.asarray(mask_pcd.colors)

    # check if the mask is the same as the original
    if original_points.shape[0] != mask_points.shape[0]:
        raise ValueError("The number of points in the original and mask point clouds must be the same.")

    # init all points to background label
    labels = np.full((original_points.shape[0], 1), bg_label)

    # set green point to label fg_label
    green_mask = np.all(mask_colors == [0, 1, 0], axis=1)
    labels[green_mask] = fg_label

    # Concatenate XYZRGBL
    labeled_npy_pcd = np.hstack((original_points, original_colors, labels))

    return labeled_npy_pcd


def main():
    parser = argparse.ArgumentParser(description="Label wall points in a point cloud based on a dxf format mask.")
    parser.add_argument("--ply", type=str, help="Path to the original point cloud file")
    parser.add_argument("--mask", type=str, help="Path to the mask point cloud file")

    parser.add_argument("--save-path", type=str, help="Path to save the labeled point cloud file (optional)")
    parser.add_argument("--vis", action="store_true", help="vis the labeled point cloud")
    parser.add_argument("--fg-label", type=int, default=2, help="Foreground label (default: 2)")
    parser.add_argument("--bg-label", type=int, default=12, help="Background label (default: 12)")

    args = parser.parse_args()

    ply_file = args.ply
    mask_file = args.mask

    original_pcd = o3d.io.read_point_cloud(ply_file)
    mask_pcd = o3d.io.read_point_cloud(mask_file)

    npy_pcd = create_npy(original_pcd, mask_pcd, fg_label=args.fg_label, bg_label=args.bg_label)

    if args.save_path:
        save_npy_file = os.path.join(args.save_path, os.path.basename(ply_file)[:-4] + "_labeled.npy")
    else:
        save_npy_file = ply_file[:-4] + "_labeled.npy"

    np.save(save_npy_file, npy_pcd)
    print(f"Saved labeled point cloud to {save_npy_file}")

    if args.vis:
        visualize_npy(npy_pcd, fg_label=args.fg_label)


if __name__ == "__main__":
    main()
