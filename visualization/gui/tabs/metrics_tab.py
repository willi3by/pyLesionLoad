from PyQt6.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QGridLayout, QCheckBox, QLabel, QPushButton
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
from lesion_load_ops.lesion_load_calc import *

class MetricsTab(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        
        # Layout for the entire tab
        layout = QVBoxLayout()
        
        # Group box for metrics
        group_box = QGroupBox("Metric Options")
        
        # Grid layout for the metric buttons and images
        grid_layout = QGridLayout()
        
        # Example metric names and their image paths
        self.metrics = [
            ("Grid Split Percent Subsections > 5% Damage", "gui/Grid_subsections.png"),
            ("Radial Split Percent Subsections > 5% Damage", "gui/Radial_subsections.png"),
            ("Weighted Lesion Load AUC", "gui/WLL.png"),
            ("Max Weighted Lesion Load", "gui/Max_WLL.png")
        ]
        
        # Store references to checkboxes
        self.checkboxes = []

        # Create buttons and labels dynamically for each metric
        for i, (metric_name, image_path) in enumerate(self.metrics):
            # Vertical layout for each metric's checkbox and image
            v_layout = QVBoxLayout()
            
            # Create checkbox for metric name
            checkbox = QCheckBox(metric_name)
            checkbox.setStyleSheet("color: white;")  # Make text white
            
            # Add checkbox to vertical layout
            v_layout.addWidget(checkbox)
            
            # Store the checkbox reference
            self.checkboxes.append(checkbox)
            
            # Create label for image
            label = QLabel()
            pixmap = QPixmap(image_path)
            
            # Enlarge the image (e.g., 300x300) and keep aspect ratio with smooth transformation
            label.setPixmap(pixmap.scaled(300, 300, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            
            # Align the image to the top of the cell
            label.setAlignment(Qt.AlignmentFlag.AlignTop)
            
            # Add label to vertical layout
            v_layout.addWidget(label)
            
            # Reduce space between items in the vertical layout
            v_layout.setSpacing(10)  # Remove spacing between checkbox and label
            
            # Optional: Adjust margins to reduce padding around the layout
            v_layout.setContentsMargins(0, 0, 0, 0)  # No margins around the layout
            
            # Calculate the grid position (2x2 grid)
            row, col = divmod(i, 2)  
            grid_layout.addLayout(v_layout, row, col)  # Add the vertical layout to the grid
            
            # Set minimum height for grid cells to avoid large gaps
            grid_layout.setRowMinimumHeight(row, 350)  # Ensure the row has enough height for the images

        # Add grid layout to the group box
        group_box.setLayout(grid_layout)
        
        # Add group box to the main layout
        layout.addWidget(group_box)
        
        # Create "Calculate Metrics" button
        calculate_button = QPushButton("Calculate Metrics")
        calculate_button.clicked.connect(self.calculate_metrics)  # Connect the button to the function
        
        # Add the button to the layout
        layout.addWidget(calculate_button)
        
        # Set the main layout for the widget
        self.setLayout(layout)

    def calculate_metrics(self):
        # Function to calculate metrics when the button is pressed
        print("Calculating metrics...")
        side = get_lesion_side(self.parent.overlay_image)
        self.parent.lesion_side = side

        # Loop through checkboxes and check if they are selected
        for checkbox, (metric_name, _) in zip(self.checkboxes, self.metrics):
            if checkbox.isChecked():
                print(f"Calculating: {metric_name}")
                if metric_name == "Grid Split Percent Subsections > 5% Damage":
                    tract_prefix = 'sxHCPA_CST_' + side
                    grid_lesion_load, grid_subsections_injured = extract_lesion_load_cramer(
                        'data/grid_16ths/', tract_prefix, self.parent.overlay_nii_image
                    )
                    self.parent.grid_lesion_load = grid_lesion_load
                    self.parent.grid_subsections_injured = grid_subsections_injured
                    print(grid_subsections_injured)
                    print(grid_lesion_load)

                elif metric_name == "Radial Split Percent Subsections > 5% Damage":
                    tract_prefix = side.lower() 
                    radial_lesion_load, radial_subsections_injured = extract_lesion_load_cramer(
                        'data/radial_16ths/', tract_prefix, self.parent.overlay_nii_image
                    )
                    self.parent.radial_lesion_load = radial_lesion_load
                    self.parent.radial_subsections_injured = radial_subsections_injured
                    print(radial_lesion_load)

                elif metric_name == "Weighted Lesion Load AUC":
                    if side == "Left":
                        tract = 'data/HCPA_CST_Left_MNI.nii'
                    if side == "Right":
                        tract = 'data/HCPA_CST_Right_MNI.nii'
                    
                    auc_wll, lesion_load_by_slice = calculate_prob_weighted_lesion_load(
                        tract, self.parent.overlay_image, return_max=False
                    )
                    self.parent.auc_wll = auc_wll
                    self.parent.lesion_load_by_slice = lesion_load_by_slice
                    print(auc_wll)

                elif metric_name == "Max Weighted Lesion Load":
                    if side == "Left":
                        tract = 'data/HCPA_CST_Left_MNI.nii'
                    if side == "Right":
                        tract = 'data/HCPA_CST_Right_MNI.nii'
                    
                    max_wll, lesion_load_by_slice = calculate_prob_weighted_lesion_load(
                        tract, self.parent.overlay_image, return_max=True
                    )
                    self.parent.max_wll = max_wll
                    self.parent.lesion_load_by_slice = lesion_load_by_slice
                    print(max_wll)
