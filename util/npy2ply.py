import numpy as np
import open3d as o3d
import os
import sys


def npy2pcd(npy_pcd, fg_label=2):
    # Nx7: XYZRGBL
    points = npy_pcd[:, :3]
    colors = npy_pcd[:, 3:6] / 255.0
    labels = npy_pcd[:, 6]

    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(points)
    pcd.colors = o3d.utility.Vector3dVector(colors)

    mask_colors = np.full_like(colors, 0.8)
    mask_colors[labels == fg_label] = [0, 1, 0]

    mask_pcd = o3d.geometry.PointCloud()
    mask_pcd.points = o3d.utility.Vector3dVector(points)
    mask_pcd.colors = o3d.utility.Vector3dVector(mask_colors)

    return pcd, mask_pcd


def main():
    if len(sys.argv) == 2:
        npy_file = sys.argv[1]
        fg_label = 2
    elif len(sys.argv) == 3:
        npy_file = sys.argv[1]
        fg_label = int(sys.argv[2])
    else:
        print("Usage: python npy2ply.py <npy_file> [fg_label]")
        sys.exit(1)

    npy_pcd = np.load(npy_file)
    pcd, mask_pcd = npy2pcd(npy_pcd, fg_label)

    o3d.io.write_point_cloud(npy_file[:-4] + ".ply", pcd)
    o3d.io.write_point_cloud(npy_file[:-4] + "_mask.ply", mask_pcd)
    print(f"Converted {npy_file} to {npy_file[:-4]}.ply and {npy_file[:-4]}_mask.ply")


if __name__ == "__main__":
    main()
