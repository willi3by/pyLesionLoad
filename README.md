# Brain Lesion Load Toolbox

This toolbox provides functions to compute corticospinal tract lesion load in brain imaging data of stroke patients. Lesion load is an estimate of the impact of lesions in specific brain regions, most often the CST, which can be useful for predicting motor outcomes after stroke. 

## Installation

I recommend using a virtual/conda environment to avoid dependency conflicts. If you have anaconda installed, you can create a new environment with:

```bash
conda create -n lesion_load python=3.10
conda activate lesion_load
```

To install the toolbox, clone the repository, navigate to the directory, and install with pip:
```bash
git clone
cd pyLesionLoad
pip install -e .
```
## Before You Start

Currently, the toolbox only supports lesion files in NIfTI format (.nii or .nii.gz) that are aligned to the MNI template provided with the toolbox. Preprocessing steps may be added in future versions.

## Usage
To launch the GUI, use the following command:

```bash
python main.py
```
Currently, the GUI only supports the use of the CST template calculated from the HCP Aging Dataset (HCPA). Future updates will allow the use of other templates. There are 4 tabs in the GUI: 

Load Data: This tab is used to load a single lesion file aligned to the MNI template provided with the toolbox. After selecting the lesion, it will be overlayed on the MNI teamplate for visual inspection. This step must be completed first before the next tabs can be used.

Choose Metric: This tab allows you to choose the lesion load metrics to be computed on the loaded lesion. The available metrics are Grid Split Subsections, Radial Split Subsections, Weighted Lesion Load, and Maximum Weighted Lesion Load. More details can be found in the related manuscript. You can also export these values to a CSV file.

Visualization: This tab provides a 3D visualization of the lesion and the CST template. It also provides visualizations for each lesion load metric. The subsection metrics will show the individual subsections affected by the lesion. The weighted lesion load metrics show the weighted lesion load per slice along the z-axis (inferior to superior). 

Batch Processing: This tab allows you to process multiple lesion files at once. You can select multiple lesion files, and the toolbox will compute the selected metrics for each file and export the results to a CSV file.

## Example Data

An example lesion file is provided in the main folder (example_lesion.nii.gz). You can use this file to test the toolbox and see how it works. The values that you should get for the example lesion are:
| Metric                     | Value          |
|----------------------------|----------------|
| Grid Split Subsections    | 18.75          |
| Radial Split Subsections    | 25.00          |
| Weighted Lesion Load       | 781.2621          |
| Maximum Weighted Lesion Load | 79.7143          |

## Contact
For any questions or issues, please contact the author at brady.williamson@uc.edu

