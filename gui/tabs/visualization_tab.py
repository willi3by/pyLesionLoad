from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QPushButton, QLabel
)
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from visualization.brain_visualizer import BrainVisualizer
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import numpy as np
from glob import glob
from natsort import natsorted


class VisualizationTab(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.t1_image_path = 'data/mni_icbm152_t1_tal_nlin_asym_09c_bet.nii.gz'

        # Main horizontal layout for two halves
        main_layout = QHBoxLayout()

        # Left side: Brain visualization
        left_layout = QVBoxLayout()

        # VTK widget for brain visualization
        self.main_vtk_widget = QVTKRenderWindowInteractor(self)
        left_layout.addWidget(self.main_vtk_widget)

        # Button to trigger visualization
        visualize_button = QPushButton("Visualize Brain with Lesion")
        visualize_button.clicked.connect(self.visualize_brain)
        left_layout.addWidget(visualize_button)

        # Right side: 2x2 grid for plots and VTK widgets
        right_layout = QGridLayout()

        # Create labels for the plots
        labels = [
            QLabel("Grid Split Percent Subsections > 5% Damage"),
            QLabel("Radial Split Percent Subsections > 5% Damage"),
            QLabel("Weighted Lesion Load AUC"),
            QLabel("Max Weighted Lesion Load"),
        ]

        # Create VTK widgets for the top two plots
        self.top_left_vtk_widget = QVTKRenderWindowInteractor(self)
        self.top_right_vtk_widget = QVTKRenderWindowInteractor(self)

        # Create matplotlib plot canvases for the bottom two plots
        self.bottom_left_plot = FigureCanvas(plt.figure())
        self.bottom_right_plot = FigureCanvas(plt.figure())

        # Add labels and widgets to the grid layout
        right_layout.addWidget(labels[0], 0, 0)
        right_layout.addWidget(self.top_left_vtk_widget, 1, 0)  # Top-left VTK

        right_layout.addWidget(labels[1], 0, 1)
        right_layout.addWidget(self.top_right_vtk_widget, 1, 1)  # Top-right VTK

        right_layout.addWidget(labels[2], 2, 0)
        right_layout.addWidget(self.bottom_left_plot, 3, 0)  # Bottom-left plot

        right_layout.addWidget(labels[3], 2, 1)
        right_layout.addWidget(self.bottom_right_plot, 3, 1)  # Bottom-right plot

        # Add both halves to the main layout
        main_layout.addLayout(left_layout, 1)
        main_layout.addLayout(right_layout, 1)

        self.setLayout(main_layout)

        # Initialize VTK widgets to prevent visual glitches
        self.initialize_vtk_widgets()

    def initialize_vtk_widgets(self):
        """Ensure VTK widgets are initialized and rendered to prevent glitches."""
        for vtk_widget in [self.main_vtk_widget, self.top_left_vtk_widget, self.top_right_vtk_widget]:
            vtk_widget.GetRenderWindow().Render()  # Initialize render window

    def visualize_brain(self):
        """Render the brain visualization in the VTK widgets."""
        # Left window (tract visualization)
        if self.parent.lesion_side == "Left":
            tracts_path = 'data/left_cst.trk'
        if self.parent.lesion_side == "Right":
            tracts_path = 'data/right_cst.trk'

        main_brain_visualizer = BrainVisualizer(
            self.t1_image_path,
            self.main_vtk_widget,
            tracts_path=tracts_path,
            overlay_mesh=self.parent.overlay_image  # Pass the overlay image
    )
        main_brain_visualizer.visualize()

        # Top-left window (grid-based volumetric regions)
        if self.parent.lesion_side == "Left":
            grid_regions = natsorted(glob('data/grid_16ths/sxHCPA_CST_Left*'))

        if self.parent.lesion_side == "Right":
            grid_regions = natsorted(glob('data/grid_16ths/sxHCPA_CST_Right*'))
        
        grid_affected_regions = [x for x,y in zip(grid_regions, self.parent.grid_subsections_injured) if y]

        top_left_visualizer = BrainVisualizer(
            self.t1_image_path, 
            self.top_left_vtk_widget, 
            regions_list=grid_affected_regions
        )
        top_left_visualizer.visualize()

        # Top-right window (radial-based volumetric regions)
        if self.parent.lesion_side == "Left":
            radial_regions = natsorted(glob('data/radial_16ths/left*'))

        if self.parent.lesion_side == "Right":
            radial_regions = natsorted(glob('data/radial_16ths/right*'))
        
        radial_affected_regions = [x for x,y in zip(radial_regions, self.parent.radial_subsections_injured) if y]

        top_right_visualizer = BrainVisualizer(
            self.t1_image_path, 
            self.top_right_vtk_widget, 
            regions_list=radial_affected_regions
        )
        top_right_visualizer.visualize()

        # Update the bottom plots
        self.update_density_line_plots()

    def update_density_line_plots(self):
        """Update the plots with example data."""
        # Example for the bottom-left plot
        x = np.arange(self.parent.overlay_image.shape[2])  # Assuming this is your x-axis data
        y = self.parent.lesion_load_by_slice  # Assuming this is your y-axis data
        max_index = np.argmax(y)
        max_value = y[max_index]

        ax1 = self.bottom_left_plot.figure.add_subplot(111)
        ax1.clear()
        ax1.plot(x, y)
        ax1.set_title("Weighted Lesion Load by Slice")
        ax1.fill_between(x, y, color='skyblue', alpha=0.4)

        self.bottom_left_plot.draw()

        # Example for the bottom-right plot
        ax2 = self.bottom_right_plot.figure.add_subplot(111)
        ax2.clear()
        ax2.plot(x, y)
        circle = Circle((x[max_index], max_value), radius=5, color='red', fill=False, lw=2)  # radius and color can be adjusted
        ax2.add_patch(circle)
        ax2.set_title("Max Weighted Lesion Load")
        self.bottom_right_plot.draw()
