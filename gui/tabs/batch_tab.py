from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QGroupBox, QGridLayout, QCheckBox,
    QPushButton, QFileDialog, QLabel, QMessageBox
)
from PyQt6.QtCore import Qt
import csv
import os
import ants
import numpy as np

from lesion_load_ops.lesion_load_calc import compute_metrics   # our helper with NumPy overlays


class BatchTab(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent

        # Main layout
        layout = QVBoxLayout()

        # Group box for metrics selection
        metrics_group = QGroupBox("Select Metrics to Calculate")
        metrics_layout = QGridLayout()

        self.metrics = [
            "Grid Split Percent Subsections > 5% Damage",
            "Radial Split Percent Subsections > 5% Damage",
            "Weighted Lesion Load AUC",
            "Max Weighted Lesion Load"
        ]

        self.checkboxes = []
        for i, metric_name in enumerate(self.metrics):
            checkbox = QCheckBox(metric_name)
            checkbox.setStyleSheet("color: black; font-weight: bold;")
            metrics_layout.addWidget(checkbox, i // 2, i % 2)
            self.checkboxes.append(checkbox)

        metrics_group.setLayout(metrics_layout)
        layout.addWidget(metrics_group)

        # Label to show selected files
        self.files_label = QLabel("No files selected")
        self.files_label.setStyleSheet("color: yellow;")
        layout.addWidget(self.files_label)

        # Buttons
        select_button = QPushButton("Select Lesion Files")
        select_button.clicked.connect(self.select_files)
        layout.addWidget(select_button)

        calc_button = QPushButton("Calculate Batch Metrics")
        calc_button.clicked.connect(self.calculate_batch_metrics)
        layout.addWidget(calc_button)

        export_button = QPushButton("Export Results to CSV")
        export_button.clicked.connect(self.export_to_csv)
        layout.addWidget(export_button)

        self.setLayout(layout)

        # Storage for file list and results
        self.files = []
        self.results = {}  # { filename: {metric: value} }

        # Reference T1 for resampling
        self.t1_image_path = "data/mni_icbm152_t1_tal_nlin_asym_09c_bet.nii.gz"
        self.t1_img = ants.image_read(self.t1_image_path)

    def load_overlay(self, file_path: str) -> np.ndarray:
        """Load a NIfTI mask, resample to T1 space, return as NumPy array (int)."""
        nii_img = ants.image_read(file_path)
        nii_img = ants.resample_image_to_target(nii_img, self.t1_img)
        return nii_img

    def select_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select Lesion Files", "", "NIfTI Files (*.nii *.nii.gz);;All Files (*)"
        )
        if files:
            self.files = files
            self.files_label.setText(f"{len(files)} files selected")

    def calculate_batch_metrics(self):
        if not self.files:
            QMessageBox.warning(self, "No Files", "Please select lesion files first.")
            return

        selected_metrics = [cb.text() for cb in self.checkboxes if cb.isChecked()]
        if not selected_metrics:
            QMessageBox.warning(self, "No Metrics", "Please select at least one metric.")
            return

        self.results = {}
        for file_path in self.files:
            lesion_name = os.path.basename(file_path)
            print(f"Processing {lesion_name} ...")

            # Load overlay as NumPy array
            overlay_image = self.load_overlay(file_path)

            # Compute metrics
            _, file_results = compute_metrics(selected_metrics, overlay_image)

            self.results[lesion_name] = file_results
            print(f"Finished {lesion_name}: {file_results}")

        QMessageBox.information(self, "Done", "Batch metrics calculation complete!")

    def export_to_csv(self):
        if not self.results:
            QMessageBox.warning(self, "No Results", "Please calculate metrics before exporting.")
            return

        file_path, _ = QFileDialog.getSaveFileName(self, "Save Metrics", "", "CSV Files (*.csv)")
        if not file_path:
            return

        # Collect headers
        metrics = set()
        for file_results in self.results.values():
            metrics.update(file_results.keys())
        metrics = sorted(metrics)

        # Write CSV
        with open(file_path, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Filename"] + metrics)
            for fname, file_results in self.results.items():
                row = [fname]
                for m in metrics:
                    value = file_results.get(m, "N/A")
                    if isinstance(value, float):
                        row.append(f"{value:.4f}")
                    else:
                        row.append(value)
                writer.writerow(row)

        QMessageBox.information(self, "Exported", f"Results exported to {file_path}")
