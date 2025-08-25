from PyQt6.QtWidgets import QMainWindow, QTabWidget, QVBoxLayout, QWidget
from gui.tabs.general_tab import GeneralTab
from gui.tabs.metrics_tab import MetricsTab
from gui.tabs.visualization_tab import VisualizationTab

class BrainNetworkAnalysisGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(100, 100, 1200, 800)
        self.setWindowTitle('Brain Lesion Load Tool')
        self.overlay_nii_image = None
        self.overlay_image = None
        self.lesion_load_by_slice = None
        self.auc_wll = None
        self.max_wll = None
        self.lesion_side = None
        self.grid_lesion_load = None
        self.grid_subsections_injured = None
        self.radial_lesion_load = None
        self.radial_subsections_injured = None



        # Create the main tab widget
        self.tabs = QTabWidget()
        self.tabs.addTab(GeneralTab(self), "Load Data")
        self.tabs.addTab(MetricsTab(self), "Choose Metrics")
        self.tabs.addTab(VisualizationTab(self), "Visualization")

        # Set layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.tabs)

        # Set central widget
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)
