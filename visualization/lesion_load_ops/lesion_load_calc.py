import ants
import numpy as np
from natsort import natsorted
from glob import glob


def get_lesion_side(lesion):
        # Threshold or apply a segmentation method to identify the lesion
    # Assuming a simple thresholding method, adjust this as needed
    lesion_mask = lesion > 0  # Assuming non-zero values represent lesion tissue
    
    # Compute the centroid (center of mass) of the lesion
    lesion_coordinates = np.argwhere(lesion_mask)  # Get the indices of the lesion
    centroid = np.mean(lesion_coordinates, axis=0)  # Compute the center of mass
    
    # Extract the x-coordinate (the first dimension)
    x_coord = centroid[0]

    # Define the threshold for left vs. right (e.g., image center)
    image_center_x = lesion.shape[0] // 2  # Assuming the x-axis is the left-right axis

    # Determine the side based on the x-coordinate of the centroid
    if x_coord < image_center_x:
        side = 'Left'
    else:
        side = 'Right'

    return side

def extract_lesion_load_cramer(base_path, tract_subsection_prefix, lesion):
    glob_path = base_path + tract_subsection_prefix + '*'
    all_subsections = natsorted(glob(glob_path))
    all_subsection_perc = []
    for f in all_subsections:
        subsection = ants.image_read(f)
        overlap = lesion * subsection
        perc_damage = (overlap.sum() / subsection.sum()) * 100
        all_subsection_perc.append(perc_damage)
    subsections_injured = np.array(all_subsection_perc) > 5
    total_subsections_injured = np.sum(subsections_injured)
    perc_subsections_injured = (total_subsections_injured/16)*100
    return perc_subsections_injured, subsections_injured

def calculate_prob_weighted_lesion_load(path_to_tract, lesion_data, return_max = False):
    tract = ants.image_read(path_to_tract)
    tract_data = tract.numpy()
    overlap = tract_data * lesion_data
    slice_weights = [np.count_nonzero(tract_data[...,i]) for i in range(tract_data.shape[-1])]
    max_area = np.max(slice_weights)
    lesion_load = []
    for i in range(overlap.shape[-1]):
        s = np.sum(overlap[...,i])
        if slice_weights[i] == 0:
            weighted_s = 0
        else:
            weighted_s = s * (max_area / slice_weights[i])
        lesion_load.append(weighted_s)
    if return_max:
        return np.max(lesion_load), lesion_load
    else:
        lesion_load_auc = np.trapz(lesion_load)
        return lesion_load_auc, lesion_load