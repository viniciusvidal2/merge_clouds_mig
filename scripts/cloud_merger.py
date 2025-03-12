import open3d as o3d
import numpy as np
import argparse
import os
from copy import deepcopy
import pyvista as pv


class CloudMerger:
    def __init__(self, input_clouds_paths: list, input_clouds_types: list, clouds_folder: str, merged_cloud_name: str) -> None:
        """Initializes the CloudMerger class with the output path and the input point clouds paths and types.

        Args:
            input_clouds_paths (list): input point clouds paths
            input_clouds_types (list): input point clouds types, wether sonar or sfm
            clouds_folder (str): folder where the point clouds are stored
            merged_cloud_name (str): name of the merged point cloud
        """
        self.input_clouds_paths = input_clouds_paths
        self.input_clouds_types = input_clouds_types
        self.merged_cloud = o3d.geometry.PointCloud()
        self.output_path = os.path.join(clouds_folder, merged_cloud_name)

    def process_sonar_cloud(self, cloud: o3d.geometry.PointCloud) -> o3d.geometry.PointCloud:
        """Processes the sonar point cloud by removing the noise and the ground plane.

        Args:
            cloud (o3d.geometry.PointCloud): input sonar point cloud

        Returns:
            o3d.geometry.PointCloud: processed sonar point cloud
        """
        # Flip the point cloud in z direction
        cloud.points = o3d.utility.Vector3dVector(
            np.array(cloud.points) * np.array([1, 1, -1]))

        # Calculate the normals, flipping towards positive z
        cloud.estimate_normals(
            search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=30))
        cloud.normals = o3d.utility.Vector3dVector(
            np.array(cloud.normals) * np.array([1, 1, -1]))

        # Return a copy of it
        return deepcopy(cloud)

    def process_sfm_cloud(self, cloud: o3d.geometry.PointCloud) -> o3d.geometry.PointCloud:
        """Processes the sfm point cloud by removing the noise and the ground plane.

        Args:
            cloud (o3d.geometry.PointCloud): input sfm point cloud

        Returns:
            o3d.geometry.PointCloud: processed sfm point cloud
        """
        # Calculate the normals, flipping towards positive z
        cloud.estimate_normals(
            search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=30))
        cloud.normals = o3d.utility.Vector3dVector(
            np.array(cloud.normals) * np.array([1, 1, -1]))

        # Return a copy of it
        return deepcopy(cloud)

    def merge_clouds(self) -> bool:
        """Merges the point clouds properly into a single point cloud object.

        Returns:
            bool: true if the point clouds were merged successfully
        """
        # If output directory does not exist, call an error
        if not os.path.exists(os.path.dirname(self.output_path)):
            print(
                f"Error: output directory {os.path.dirname(self.output_path)} does not exist")
            return False

        if len(self.input_clouds_paths) == 0:
            print("Error: no input point clouds were provided")
            return False

        for c_path, c_type in zip(self.input_clouds_paths, self.input_clouds_types):
            # Load the point cloud
            cloud = o3d.io.read_point_cloud(c_path)
            if cloud is None:
                print(f"Error: could not load point cloud from {c_path}")
                return False

            # Merge the point cloud according to the type
            if c_type == "sonar":
                self.merged_cloud += self.process_sonar_cloud(cloud)
            elif c_type == "sfm":
                self.merged_cloud += self.process_sfm_cloud(cloud)
            else:
                print(
                    f"Error: unknown point cloud type {c_type} for point cloud {c_path}")
                return False

        # Save the merged point cloud
        if not self.save_merged_cloud():
            return False

        return True

    def save_merged_cloud(self) -> bool:
        """Saves the merged point cloud to the output path.

        Returns:
            bool: true if the point cloud was saved successfully
        """
        # Save the merged point cloud
        if not o3d.io.write_point_cloud(self.output_path, self.merged_cloud):
            print(
                f"Error: could not save the merged point cloud to {self.output_path}")
            return False

        return True

    def get_merged_cloud(self) -> o3d.geometry.PointCloud:
        """Returns the merged point cloud.

        Returns:
            o3d.geometry.PointCloud: merged point cloud
        """
        return self.merged_cloud

    def get_merged_cloud_pyvista(self) -> pv.PolyData:
        """Returns the merged point cloud as a PyVista object.

        Returns:
            pv.PolyData: merged point cloud as a PyVista object
        """
        points = np.asarray(self.merged_cloud.points)
        polydata = pv.PolyData(points)
        if self.merged_cloud.has_colors():
            colors = (np.asarray(self.merged_cloud.colors)
                      * 255).astype(np.uint8)
            polydata.point_data["RGB"] = colors
        if self.merged_cloud.has_normals():
            normals = np.asarray(self.merged_cloud.normals)
            polydata.point_data["Normals"] = normals

        return polydata

    def get_merged_cloud_bytes(self) -> bytes:
        """Returns the merged point cloud as bytes.

        Returns:
            bytes: merged point cloud as bytes
        """
        with open(self.output_path, "rb") as f:
            return f.read()


if __name__ == "__main__":
    root_path = os.path.dirname(os.path.abspath(__file__))
    # Parse the arguments
    parser = argparse.ArgumentParser(
        description="Merge point clouds into a single point cloud")
    parser.add_argument("--output_path", type=str,
                        default=os.path.join(root_path, "merged_cloud.ply"), required=False,
                        help="path to save the merged point cloud")
    parser.add_argument("--input_clouds_paths", type=list,
                        default=[os.path.join(root_path, "barragem.ply"), os.path.join(root_path, "espigao.ply")], required=False,
                        help="list of paths to the input point clouds")
    parser.add_argument("--input_clouds_types", type=list,
                        default=["sonar", "sfm"], required=False,
                        help="list of types of the input point clouds")
    args = parser.parse_args()

    # Create the input point clouds data dictionary and the output path
    input_clouds_data = {
        "paths": args.input_clouds_paths,
        "types": args.input_clouds_types
    }
    output_path = args.output_path

    # Merge the point clouds
    cloud_merger = CloudMerger(
        output_path, input_clouds_data['paths'], input_clouds_data['types'])
    if cloud_merger.merge_clouds(input_clouds_data, output_path):
        print("Point clouds merged successfully")
    else:
        print("Error: could not merge the point clouds")
