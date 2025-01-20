import numpy as np
from dipy.tracking.streamline import Streamlines
from dipy.io.streamline import load_tractogram

def center_streamlines(streamlines, surface_center):
    centered_streamlines = []
    for streamline in streamlines:
        centered_streamlines.append(streamline - surface_center)  # Subtract surface center
    return Streamlines(centered_streamlines)

def transform_streamlines(streamlines, affine):
    transformed_streamlines = []
    for streamline in streamlines:
        homogeneous_coords = np.c_[streamline, np.ones((len(streamline), 1))]  # Add homogeneous coordinate
        voxel_coords = (np.linalg.inv(affine) @ homogeneous_coords.T).T
        transformed_streamlines.append(voxel_coords[:, :3])  # Take the first 3 columns as voxel coordinates
    return Streamlines(transformed_streamlines)

import numpy as np

def get_direction_color(streamline):
    # Calculate the direction vector from the first point to the last point of the streamline
    direction = streamline[-1] - streamline[0]
    
    # Normalize the direction vector (unit vector)
    direction = direction / np.linalg.norm(direction)
    
    # Apply a square root smoothing function to each component for a more gradual gradient
    smooth_r = (np.sqrt(np.abs(direction[0])))  # Red (X-axis component)
    smooth_g = (np.sqrt(np.abs(direction[1])))  # Green (Y-axis component)
    smooth_b = (np.sqrt(np.abs(direction[2])))  # Blue (Z-axis component)
    
    # Combine the smoothed components into the final color
    color = np.array([smooth_r, smooth_g, smooth_b])
    
    # Ensure that the color values are within the valid range [0, 1]
    color = np.clip(color, 0, 1)
    
    return color


def streamline_bounding_sphere(streamline):
    """
    Estimate a bounding sphere for a streamline using the center and standard deviation
    of the distances from the center to all points in the streamline, with an optional shrink factor.
    """
    # Calculate the center of the streamline (centroid)
    center = np.mean(streamline, axis=0)
    
    # Calculate the distance from the center to each point in the streamline
    distances = np.linalg.norm(streamline - center, axis=1)
    
    # Set a default radius based on the standard deviation (mean + std_dev)
    radius = np.mean(distances)
    
    # Apply a shrink factor to reduce the radius further
    shrink_factor = 0.8  # Shrink the radius by 50%
    radius *= shrink_factor

    return center, radius

def process_streamlines(file, affine, brain_surface_center):
    streamlines = load_tractogram(file, "same", bbox_valid_check=False).streamlines
    transformed_streamlines = transform_streamlines(streamlines, affine)
    centered_streamlines = center_streamlines(transformed_streamlines, brain_surface_center)
    centers = []
    radii = []
    for s in centered_streamlines:
        center, radius = streamline_bounding_sphere(s)
        centers.append(center)
        radii.append(radius)
    return centered_streamlines, centers, radii


