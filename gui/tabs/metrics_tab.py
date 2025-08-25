from PyQt6.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QGridLayout, QCheckBox, QLabel, QPushButton, QFileDialog, QHBoxLayout
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
import csv
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
        
        # Store references to checkboxes and result labels
        self.checkboxes = []
        self.result_labels = {}

        # Create buttons and labels dynamically for each metric
        for i, (metric_name, image_path) in enumerate(self.metrics):
            # Vertical layout for each metric block
            v_layout = QVBoxLayout()
            
            # Checkbox for metric
            checkbox = QCheckBox(metric_name)
            checkbox.setStyleSheet("color: black; font-weight: bold;")
            v_layout.addWidget(checkbox)
            self.checkboxes.append(checkbox)
            
            # Image
            image_label = QLabel()
            pixmap = QPixmap(image_path)
            image_label.setPixmap(pixmap.scaled(250, 250, Qt.AspectRatioMode.KeepAspectRatio,
                                                Qt.TransformationMode.SmoothTransformation))
            image_label.setAlignment(Qt.AlignmentFlag.AlignTop)
            
            # Result label (for showing values next to the image)
            result_label = QLabel("Result: N/A")
            result_label.setStyleSheet("color: yellow; font-weight: bold;")
            self.result_labels[metric_name] = result_label
            
            # Horizontal layout for image + result text
            h_layout = QHBoxLayout()
            h_layout.addWidget(image_label)
            h_layout.addWidget(result_label)
            
            v_layout.addLayout(h_layout)
            v_layout.setSpacing(10)
            v_layout.setContentsMargins(0, 0, 0, 0)
            
            row, col = divmod(i, 2)
            grid_layout.addLayout(v_layout, row, col)
            grid_layout.setRowMinimumHeight(row, 300)

        group_box.setLayout(grid_layout)
        layout.addWidget(group_box)
        
        # Buttons
        calculate_button = QPushButton("Calculate Metrics")
        calculate_button.clicked.connect(self.calculate_metrics)
        layout.addWidget(calculate_button)

        export_button = QPushButton("Export Results to CSV")
        export_button.clicked.connect(self.export_to_csv)
        layout.addWidget(export_button)
        
        self.setLayout(layout)

    def calculate_metrics(self):
        print("Calculating metrics...")
        side = get_lesion_side(self.parent.overlay_image)
        self.parent.lesion_side = side

        for checkbox, (metric_name, _) in zip(self.checkboxes, self.metrics):
            if checkbox.isChecked():
                print(f"Calculating: {metric_name}")
                result_value = None

                if metric_name == "Grid Split Percent Subsections > 5% Damage":
                    tract_prefix = 'sxHCPA_CST_' + side
                    grid_lesion_load, grid_subsections_injured = extract_lesion_load_cramer(
                        'data/HCPA/grid_16ths/', tract_prefix, self.parent.overlay_nii_image
                    )
                    self.parent.grid_lesion_load = grid_lesion_load
                    self.parent.grid_subsections_injured = grid_subsections_injured
                    result_value = f"{grid_lesion_load:.4f}"

                elif metric_name == "Radial Split Percent Subsections > 5% Damage":
                    tract_prefix = side.lower()
                    radial_lesion_load, radial_subsections_injured = extract_lesion_load_cramer(
                        'data/HCPA/radial_16ths/', tract_prefix, self.parent.overlay_nii_image
                    )
                    self.parent.radial_lesion_load = radial_lesion_load
                    self.parent.radial_subsections_injured = radial_subsections_injured
                    result_value = f"{radial_lesion_load:.4f}"

                elif metric_name == "Weighted Lesion Load AUC":
                    tract = 'data/HCPA/HCPA_CST_Left_MNI.nii' if side == "Left" else 'data/HCPA/HCPA_CST_Right_MNI.nii'
                    auc_wll, lesion_load_by_slice = calculate_prob_weighted_lesion_load(
                        tract, self.parent.overlay_image, return_max=False
                    )
                    self.parent.auc_wll = auc_wll
                    self.parent.lesion_load_by_slice = lesion_load_by_slice
                    result_value = f"{auc_wll:.4f}"

                elif metric_name == "Max Weighted Lesion Load":
                    tract = 'data/HCPA/HCPA_CST_Left_MNI.nii' if side == "Left" else 'data/HCPA/HCPA_CST_Right_MNI.nii'
                    max_wll, lesion_load_by_slice = calculate_prob_weighted_lesion_load(
                        tract, self.parent.overlay_image, return_max=True
                    )
                    self.parent.max_wll = max_wll
                    self.parent.lesion_load_by_slice = lesion_load_by_slice
                    result_value = f"{max_wll:.4f}"

                # Update result label
                if result_value is not None:
                    self.result_labels[metric_name].setText(f"Result: {result_value}")

    def export_to_csv(self):
        # Open file dialog
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Metrics", "", "CSV Files (*.csv)")
        if not file_path:
            return
        
        # Collect results
        data = []
        for metric_name in self.result_labels:
            result_text = self.result_labels[metric_name].text().replace("Result: ", "")
            data.append([metric_name, result_text])
        
        # Write to CSV
        with open(file_path, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Metric", "Result"])
            writer.writerows(data)

        print(f"Results exported to {file_path}")
