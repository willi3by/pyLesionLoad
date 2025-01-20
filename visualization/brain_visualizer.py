import vedo
import nibabel as nib
import numpy as np
from scipy import ndimage
from skimage import measure
from visualization.streamline_ops import process_streamlines, get_direction_color
import os

class BrainVisualizer:
    def __init__(self, t1_image_path, vtk_widget, regions_list=None, tracts_path=None, overlay_mesh=None):
        self.t1_image_path = t1_image_path
        self.vtk_widget = vtk_widget
        self.regions_list = regions_list
        self.tracts_path = tracts_path
        self.overlay_mesh = overlay_mesh
        self.plotter = vedo.Plotter(qt_widget=vtk_widget)

    def add_overlay_mesh(self, overlay_data, center_of_mass):
        """Visualize the overlay data as a 3D mesh."""
        # Extract surface mesh using marching cubes
        verts, faces, _, _ = measure.marching_cubes(overlay_data, level=0.5, step_size=1)
        
        # Create the overlay surface mesh
        overlay_surface = vedo.Mesh([verts, faces]).color("red").opacity(0.6)
        overlay_surface.pos(-center_of_mass[0], -center_of_mass[1], -center_of_mass[2])
        
        # Add the overlay mesh to the plotter
        self.plotter.add(overlay_surface)

    def visualize(self):
        # Load T1-weighted image
        t1_image = nib.load(self.t1_image_path)
        t1_data = t1_image.get_fdata()
        affine = t1_image.affine

        # Create brain surface mesh
        brain_mask = ndimage.gaussian_filter(t1_data.astype(float), sigma=3.0)
        brain_mask[brain_mask < 65.0] = 0
        verts, faces, _, _ = measure.marching_cubes(brain_mask, level=0.5, step_size=1)
        brain_surface = vedo.Mesh([verts, faces]).color("gray").opacity(0.1)
        center_of_mass = np.mean(verts, axis=0)
        brain_surface.pos(-center_of_mass[0], -center_of_mass[1], -center_of_mass[2])
        self.plotter.add(brain_surface)

        # Add tracts if specified
        if self.tracts_path:
            centered_streamlines, _, _ = process_streamlines(self.tracts_path, affine, center_of_mass)
            for streamline in centered_streamlines:
                color = get_direction_color(streamline)
                self.plotter.add(vedo.Tube(streamline, r=0.5).color(color))
        
        if self.overlay_mesh is not None:
            self.add_overlay_mesh(self.overlay_mesh, center_of_mass)

        # Add volumetric regions as meshes
        if self.regions_list:
            colors_list = [
                "red", "blue", "green", "yellow", "purple", "orange",
                "cyan", "magenta", "lime", "pink", "teal", "brown",
                "gold", "gray", "indigo", "maroon"
            ]  # A list of 16 distinct colors
            for i, region_file in enumerate(self.regions_list):
                # region_path = os.path.join(self.regions_path, region_file)
                region_data = nib.load(region_file).get_fdata()

                # Extract surface mesh using marching cubes
                verts, faces, _, _ = measure.marching_cubes(region_data, level=0.5, step_size=1)
                color = colors_list[i % len(colors_list)]  # Cycle through colors
                region_surface = vedo.Mesh([verts, faces]).color(color).opacity(0.9)
                region_surface.pos(-center_of_mass[0], -center_of_mass[1], -center_of_mass[2])
                self.plotter.add(region_surface)

        # Show the plot
        self.plotter.show(axes=0, title="Brain Visualization")

