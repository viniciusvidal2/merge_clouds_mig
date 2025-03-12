import streamlit as st
from stpyvista import stpyvista as vtki
import pyvista as pv
import os
from scripts.cloud_merger import CloudMerger

CLOUDS_DIRECTORY = "/app/clouds"
MERGED_CLOUD_NAME = "merged_cloud.ply"


def add_cloud_load_section(cloud_id: int) -> None:
    """Add a point cloud load section with a file uploader and checkboxes to select the type of point cloud

    Args:
        cloud_id (int): id of the point cloud
    """
    # Add two collumns to split between file upload and checkboxes
    file_col, cb_col = st.columns(2)

    # Path field and buttons to the right to add the file.
    # Checkboxes to see if it is from drone or sonar
    with file_col:
        cloud = st.file_uploader("Choose a file",
                                 type=["pcd", "ply"],
                                 key=f"file_uploader_{cloud_id}",
                                 label_visibility="collapsed")
    with cb_col:
        st.checkbox("Drone", key=f"drone_{cloud_id}")
        st.checkbox("Sonar", key=f"sonar_{cloud_id}")
    if cloud:
        cloud_key = f"cloud_{cloud_id}"
        st.session_state.uploaded_cloud_paths[cloud_key] = save_cloud_to_path(
            cloud, cloud_key)


def save_cloud_to_path(uploaded_file: bytes, filename: str) -> str:
    """Save the uploaded file in a specified directory with a custom name.

    Args:
        uploaded_file (UploadedFile): Streamlit uploaded file object.
        filename (str, optional): Custom filename, without the file extension.

    Returns:
        str: Full path to the saved file.
    """
    os.makedirs(CLOUDS_DIRECTORY, exist_ok=True)

    file_path = os.path.join(CLOUDS_DIRECTORY, filename + ".ply")
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getvalue())

    return file_path


def get_cloud_paths() -> list:
    """Get the paths of the clouds from the file uploaders

    Returns:
        list: list of cloud paths
    """
    return [cp for cp in st.session_state.uploaded_cloud_paths.values()]


def get_cloud_types() -> list:
    """Get the types of the clouds from the checkboxes

    Returns:
        list: list of cloud types
    """
    cloud_types = []
    for cloud_id in range(1, st.session_state.clouds_count + 1):
        drone = st.session_state[f"drone_{cloud_id}"]
        sonar = st.session_state[f"sonar_{cloud_id}"]
        if drone:
            cloud_types.append("sfm")
        elif sonar:
            cloud_types.append("sonar")
        else:
            cloud_types.append(None)

    return cloud_types


def reset_session_state() -> None:
    """Clear the session state of the uploaded clouds. 
    Starts the variables we use to control the flow.
    """
    # Start control variables
    st.session_state.uploaded_cloud_paths = {}
    st.session_state.clouds_count = 0
    # Remove any clouds left in clouds folder
    for c in os.listdir(CLOUDS_DIRECTORY):
        if c.endswith(".ply"):
            os.remove(os.path.join(CLOUDS_DIRECTORY, c))
    # Start xserver for pyvista to work in docker
    st.session_state.xserver = True
    pv.start_xvfb()


def main():
    """Main function to run the stream
    """
    # Init the session state or reset it if needed
    if "clouds_count" not in st.session_state \
            and "uploaded_cloud_paths" not in st.session_state \
            and "xserver" not in st.session_state:
        reset_session_state()

    # Init application
    st.title("SAESC - SAE Scene Creator")
    st.subheader("Create your own SAE scene with this simple app")
    st.header("Load the point clouds")

    # Create the sections to load the point clouds and clean the state
    add_col, clean_col = st.columns(2)
    with add_col:
        if st.button("Add Cloud"):
            st.session_state.clouds_count += 1
    with clean_col:
        st.button("Clean Clouds", on_click=lambda: reset_session_state())

    if st.session_state.clouds_count > 0:
        for cloud_id in range(1, st.session_state.clouds_count + 1):
            add_cloud_load_section(cloud_id)

    # Creating the merged cloud if we have any inputs
    if len(st.session_state.uploaded_cloud_paths) > 0 and st.session_state.clouds_count > 0:
        # Create the scene with the plotter
        if st.button("Create Scene"):
            st.write("Creating scene")
            merger = CloudMerger(input_clouds_paths=get_cloud_paths(),
                                 input_clouds_types=get_cloud_types(),
                                 clouds_folder=CLOUDS_DIRECTORY,
                                 merged_cloud_name=MERGED_CLOUD_NAME)
            if merger.merge_clouds():
                st.write("Clouds were merged, check the result:")
                merged_cloud_pyvista = merger.get_merged_cloud_pyvista()
                plotter = pv.Plotter(window_size=[1000, 1000])
                plotter.add_mesh(mesh=merged_cloud_pyvista,
                                 scalars=merged_cloud_pyvista.point_data["RGB"], rgb=True)
                plotter.add_text(f"Merged Cloud", position="upper_left")
                plotter.view_isometric()
                plotter.background_color = 'black'
                vtki(plotter, key=f"plotter")

            # Download the merged cloud
            merged_cloud = merger.get_merged_cloud_bytes()
            st.download_button("Download merged cloud and Clear session!", merged_cloud,
                               MERGED_CLOUD_NAME, "Download the merged cloud")


if __name__ == "__main__":
    main()
