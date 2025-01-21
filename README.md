# pyLesionLoad
Tool to assess and visualize lesion load in stroke patients

# Instructions

Download/clone folder, download data from https://osf.io/xq6gk/, and place data folder in the app folder. Then run python main.py

Alternatively, go to Releases and download the zip file pyLesionLoad.zip, unzip, and run the app. Currently there is only a Mac version that has been tested on MacOS 15.1.1. Testing on other operating systems is underway.

On the first page of the app, click "Select NIfTI File" and choose the test lesion in this directory (test_lesion.nii). This should overlay the lesion on the axial brain on this tab. Then, navigate to the metrics tab, select all metrics, and click Calculate Metics. This will calculate the 4 metrics currently implemented. Finally, go to the visualization tab and click Visualize Brain with Lesion. This should populate the visualization windows on this tab. 
