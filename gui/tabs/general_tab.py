from PyQt6.QtWidgets import QWidget, QHBoxLayout, QGroupBox, QVBoxLayout, QPushButton, QFileDialog, QSlider
from PyQt6.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import nibabel as nib
import numpy as np
import ants


class GeneralTab(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        
        layout = QHBoxLayout()  # Left-right layout for the main window

        # Group for file selection (on the left side)
        file_selection_group = QGroupBox("File Selection")
        file_selection_layout = QVBoxLayout()
        self.select_button = QPushButton("Select NIfTI file")
        self.select_button.clicked.connect(self.select_nii_file)
        file_selection_layout.addWidget(self.select_button)
        file_selection_group.setLayout(file_selection_layout)
        
        layout.addWidget(file_selection_group)  # This will be placed on the left side

        # Create a layout for the right side where the image and slider will go (Vertical layout)
        right_layout = QVBoxLayout()

        # Create matplotlib figure and canvas for displaying the MRI image
        self.figure = Figure(figsize=(6, 6))  # Set initial figure size to reduce white space
        self.canvas = FigureCanvas(self.figure)
        
        right_layout.addWidget(self.canvas)  # Add the canvas to the right layout

        # Add the slider at the bottom of the right section
        self.axial_slider = QSlider(Qt.Orientation.Horizontal)
        self.axial_slider.setRange(10, 100)  # Default range, will change after loading T1
        self.axial_slider.valueChanged.connect(self.update_axial_view)
        
        right_layout.addWidget(self.axial_slider)  # Move the slider to the bottom of the right section

        layout.addLayout(right_layout)  # This will be placed on the right side

        self.setLayout(layout)

        # Load the default T1 image
        self.t1_image_path = "data/mni_icbm152_t1_tal_nlin_asym_09c_bet.nii.gz"
        self.t1_data = nib.load(self.t1_image_path).get_fdata()

        # Set initial slider range based on T1 data
        self.axial_slider.setRange(10, self.t1_data.shape[2] - 20)

        # Set default slice to 90 (if within range)
        self.axial_slider.setValue(90)

        self.parent.overlay_image = None

        # Display the default slice (slice 90) on startup
        self.update_axial_view(90)

    def select_nii_file(self):
        # Open file dialog to select NIfTI file
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Open NIfTI file", "", "NIfTI Files (*.nii *.nii.gz)")
        if file_path:
            self.load_nii_file(file_path)

    def load_nii_file(self, file_path):
        # Load the NIfTI file using nibabel
        nii_img = ants.image_read(file_path)
        t1_img = ants.image_read(self.t1_image_path)
        nii_img = ants.resample_image_to_target(nii_img, t1_img)
        self.parent.overlay_nii_image = nii_img
        self.parent.overlay_image = nii_img.numpy().astype(int)

        # Update the display with the current slice
        self.update_axial_view(self.axial_slider.value())

    def update_axial_view(self, slice_index):
        if self.t1_data is None:
            return

        # Get the axial slice from the T1 data
        t1_slice = self.t1_data[:, :, slice_index]

        # Clear previous figure content
        self.figure.clear()

        # Create a subplot to display the image
        ax = self.figure.add_subplot(111)

        # Show the T1 slice in grayscale
        ax.imshow(t1_slice.T, cmap='gray', origin='lower')

        if self.parent.overlay_image is not None:
            # Get the overlay slice (binary mask)
            overlay_slice = self.parent.overlay_image[:, :, slice_index]

            # Show the overlay as red on top of the T1 slice
            ax.imshow(overlay_slice.T, cmap='Reds', origin='lower', alpha=0.5)

        # Optional: Add title, labels, etc.
        ax.set_title(f"Slice {slice_index}")
        ax.axis('off')  # Hide axes

        # Adjust the figure layout to remove white space
        self.figure.tight_layout(pad=0.0, h_pad=0.0, w_pad=0.0)

        # Redraw the canvas to update the figure
        self.canvas.draw()


