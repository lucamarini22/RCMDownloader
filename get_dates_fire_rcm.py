import os
import glob

def get_dates_fire_rcm(fire_folder: str, ext: str = ".tif" ,sep: str = "_"):
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
        get_dates_fire_rcm('./tif_images_donnie_creef_20230622_20230703_not_convex_polygon')
    print(unique_dates_fire)
    print(unique_dates_fire_per_satellite)
