import os
from typing import Tuple, List
import glob

def get_dates_fire_rcm(
    fire_folder: str, 
    ext: str = ".tif",
    sep: str = "_"
) -> Tuple[List[str], List[str]]:
    """Given a folder containing images downloaded from RCM and processed with 
    SNAP, it gets the unique dates of acquisition of the images, both in 
    general and also related to each satellite. 

    Args:
        fire_folder (str): folder containing images downloaded from RCM and 
          processed with SNAP.
        ext (str, optional): extension of processed images. Defaults to ".tif".
        sep (str, optional): separator. Defaults to "_".

    Returns:
        Tuple[List[str], List[str]]: list of unique dates of acquisition of the
          images without specifying which satellite acquired the image, and 
          list of unique dates of acquisition of the images with corresponding 
          satellite that acquired the image.
          
    """
    assert os.path.isdir(fire_folder)
    fire_imgs_paths = glob.glob(
        os.path.join(fire_folder, "*" + ext)
    )
    unique_dates_fire = set()
    unique_dates_fire_per_satellite = set()

    for path_fire_img in fire_imgs_paths:
        filename = os.path.basename(path_fire_img)
        tokens = filename.split(sep)
        satellite = tokens[0]
        date = tokens[5]
        unique_dates_fire.add(date)
        unique_dates_fire_per_satellite.add(satellite + sep + date)

    unique_dates_fire = list(unique_dates_fire)
    unique_dates_fire_per_satellite = list(unique_dates_fire_per_satellite)
    
    unique_dates_fire.sort()
    unique_dates_fire_per_satellite.sort()
    return unique_dates_fire, unique_dates_fire_per_satellite


if __name__ == "__main__":
    unique_dates_fire, unique_dates_fire_per_satellite = \
        get_dates_fire_rcm('./tif_images_donnie_creef_20230622_20230710_not_convex_polygon')
    print(unique_dates_fire)
    print(unique_dates_fire_per_satellite)
