import glob
import multiprocessing
import os
import subprocess
import sys
sys.path.append(r'C:\Users\lucamar\.snap\snap-python')
from osgeo import gdal
from snappy import ProductIO, HashMap, GPF

# Constants
ZIP_EXT = ".zip"
OUTPUT_FOLDER = r'\\ug.kth.se\dfs\home\l\u\lucamar\appdata\xp.V2\Desktop\tif_images_trial' #'./tif_images'
OUT_EXT = '.tif'
MULTIPROCESSING = True

def upload_to_gcloud(file):
    print('Upload to gcloud')
    file_name = file.split('/')[-1]
    id = file.split('/')[-2]
    upload_cmd = 'gsutil cp ' + file + ' gs://ai4wildfire/VNPPROJ5/'+id+'/' + file_name
    print(upload_cmd)
    os.system(upload_cmd)
    print('finish uploading' + file_name)


def upload_to_gee(file):
    print('start uploading to gee')
    file_name = file.split('/')[-1]
    id = file.split('/')[-2]
    date = file_name[6:16]
    time = file.split('/')[-1][17:21]
    time_start = date + 'T' + time[:2] + ':' + time[2:] + ':00'
    cmd = 'earthengine upload image --time_start ' + time_start + ' --asset_id=projects/proj5-dataset/assets/proj5_dataset/' + \
          id+'_'+file_name[:-4] + ' --pyramiding_policy=sample gs://ai4wildfire/VNPPROJ5/'+id+'/' + file_name
    print(cmd)
    subprocess.call(cmd.split())
    print('Uploading in progress for image ' + time_start)

def upload(file):
    upload_to_gcloud(file)
    upload_to_gee(file)

def upload_in_parallel(import_all=True, filepath='data/subset'):
    if import_all:
        file_list = glob.glob(os.path.join(filepath, 'CANADA', '*.tif'))
    else:
        log_path = 'log/sanity_check_gee*.log'
        log_list = glob.glob(log_path)
        log_list.sort()
        with open(log_list[-1]) as f:
            f = f.readlines()
        file_list = []
        for line in f:
            file_list.append(os.path.join(filepath, line.split('_')[1],line.split('_')[2].replace('\n', '')+'.tif'))

    results = []
    with multiprocessing.Pool(processes=8) as pool:
        for file in file_list:
            id = file.split('/')[-2]
            date = file.split('/')[-1][6:16]
            time = file.split('/')[-1][17:21]
            vnp_json = open(glob.glob(os.path.join('data/VNPL1', id, date, 'D', '*.json'))[0], 'rb')
            import json
            def get_name(json):
                return json.get('name').split('.')[2]
            vnp_time = list(map(get_name, json.load(vnp_json)['content']))
            if time not in vnp_time or 'IMG' not in file:
                continue
            result = pool.apply_async(upload, (file,))
            results.append(result)
        results = [result.get() for result in results if result is not None]

def upload_by_log(filepath='data/subset'):
    with open('log/error', 'r') as f:
        file = f.read().split('\n')

    def get_id(dir_str):
        return dir_str.split('/')[1]

    target_ids = list(map(get_id, file))

    def get_date(dir_str):
        return dir_str.split('/')[-1][:10]

    target_dates = list(map(get_date, file))
    for i, target_id in enumerate(target_ids):
        tif_list = glob.glob(os.path.join(filepath, target_id, 'VNPIMG' + target_dates[i] + '*.tif'))
        for tif_file in tif_list:
            os.system('geeadd delete --id '+'projects/proj5-dataset/assets/proj5_dataset/'+target_id+'_'+tif_file.split('/')[-1][:-4])
            upload(tif_file)

def sar_tc_sn(
    zip_path: str, 
    output_folder: str = OUTPUT_FOLDER, 
    out_ext: str = ".tif",
):
    name_zip = os.path.normpath(zip_path).replace(ZIP_EXT, '').split(os.path.sep)[-1]
    # load the Sentinel-1 image
    product = ProductIO.readProduct(zip_path)
    # create a HashMap to hold the parameters for the speckle filter
    speckle_parameters = HashMap()
    speckle_parameters.put('filter', 'Lee')
    speckle_parameters.put('filterSizeX', 3)
    speckle_parameters.put('filterSizeY', 3)
    speckle_parameters.put('dampingFactor', 2)
    speckle_parameters.put('windowSize', '7x7')
    speckle_parameters.put('estimateENL', 'true')
    speckle_parameters.put('enl', 1.0)
    speckle_parameters.put('numLooksStr', '1')
    speckle_parameters.put('targetWindowSizeStr', '3x3')
    speckle_parameters.put('sigmaStr', '0.9')
    speckle_parameters.put('anSize', '50')

    # create a HashMap to hold the parameters for the terrain correction
    terrain_parameters = HashMap()
    terrain_parameters.put('demName', 'SRTM 3Sec')
    terrain_parameters.put('pixelSpacingInMeter', 30.0)
    terrain_parameters.put('demResamplingMethod', 'BILINEAR_INTERPOLATION')
    terrain_parameters.put('imgResamplingMethod', 'BILINEAR_INTERPOLATION')
    terrain_parameters.put('mapProjection', 'WGS84(DD)')

    # apply the terrain correction
    terrain_corrected = GPF.createProduct('Terrain-Correction', terrain_parameters, product)

    # apply the speckle filter
    speckle_filtered = GPF.createProduct('Speckle-Filter', speckle_parameters, terrain_corrected)

    out_file_name = os.path.join(output_folder, name_zip + out_ext)
    # write the terrain-corrected image to a file
    ProductIO.writeProduct(
        speckle_filtered, 
        out_file_name, 
        'GeoTIFF'
    ) #-BigTIFF')
    print(f'Created file: {out_file_name}.')


if __name__=='__main__':
    # Folders paths
    folder_zips_path = r'\\ug.kth.se\dfs\home\l\u\lucamar\appdata\xp.V2\Desktop\trial' #'./downloads'
    # Assertion of existence of folders
    assert os.path.isdir(folder_zips_path)
    assert os.path.isdir(OUTPUT_FOLDER)
    
    num_processes = os.cpu_count()

    zip_paths = glob.glob(
        os.path.join(folder_zips_path, "*" + ZIP_EXT)
    )

    if MULTIPROCESSING:
        with multiprocessing.Pool(processes=num_processes) as pool:
            list(pool.imap_unordered(sar_tc_sn, zip_paths))
    else:
        for zip_path in zip_paths:
            sar_tc_sn(zip_path)
            # upload_in_parallel(True, 'data/*/imagery')
            # upload_by_log()
