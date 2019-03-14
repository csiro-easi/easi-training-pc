import requests
import getpass
import json
import time
import logging
import datetime
import boto3
from math import ceil
import multiprocessing as mp
import shutil

import fiona
import shapely
import shapely.geometry

import cgi
import os

import pprint


#logging.getLogger().addHandler(logging.StreamHandler())

logging.basicConfig(level=logging.INFO, filename='./ingest.log', filemode='w',
                    format='%(asctime)s - %(levelname)s - %(message)s')

console = logging.StreamHandler()
console.setLevel(logging.INFO)
# set a format which is simpler for console use
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
# tell the handler to use this format
console.setFormatter(formatter)
# add the handler to the root logger
logging.getLogger('').addHandler(console)

'''
coords = [[[ 112.582024, -10.282572],
           [112.582024, -44.013406],
           [ 153.8587, -44.013406],
           [ 153.8587, -10.282572],
           [ 112.582024, -10.282572]]]
'''

def login(user):

    url = 'https://lpdaacsvc.cr.usgs.gov/appeears/api/'
    # login
    password = getpass.getpass()

    response = requests.post(url+'login', auth=(user, password))
    token_response = response.json()
    if ('token' not in token_response):
        raise RuntimeError ('Unsuccessful logon! Cause - {}'.format(token_response['message']))

    token = token_response['token']
    # output token expiration

    return token


def logout(token):

    url = 'https://lpdaacsvc.cr.usgs.gov/appeears/api/'
    response = requests.post(url+'logout',
                    headers={'Authorization': 'Bearer {0}'.format(token)})

    return response


def list_tasks(token):

    url = 'https://lpdaacsvc.cr.usgs.gov/appeears/api/'

    response = requests.get( url+'task', headers={'Authorization': 'Bearer {0}'.format(token)})
    task_list = response.json()

    return task_list


def check_status(token, task_id):

    url = 'https://lpdaacsvc.cr.usgs.gov/appeears/api/'

    response = requests.get(url+'status/{0}'.format(task_id),
                headers={'Authorization': 'Bearer {0}'.format(token)})
    status_response = response.json()

    return status_response


def get_bundle(task_id):

    url = 'https://lpdaacsvc.cr.usgs.gov/appeears/api/'

    response = requests.get(url+'bundle/{0}'.format(task_id))
    bundle_response = response.json()

    return bundle_response


def delete_task(token, task_id):

    url = 'https://lpdaacsvc.cr.usgs.gov/appeears/api/'
    response = requests.delete( url+'task/{0}'.format(task_id),
                    headers={'Authorization': 'Bearer {0}'.format(token)})

    return response


def submit_query(token, startDate, endDate, product, coords, layers=None, projection_name='geographic',
        file_type='geotiff', task_name=None):

    if (task_name is None):
        task_name = 'My_Task'

    task_type = 'area'
    url = 'https://lpdaacsvc.cr.usgs.gov/appeears/api/'


    # get list of products and check if request product is available
    response = requests.get(url+'product')
    product_response = response.json()
    avail_products = {p['ProductAndVersion']: p for p in product_response}
    if (product not in avail_products):
        raise RuntimeError (
            'Requested product  - {} not in list of available - {}'.format(product, ', '.join(avail_products.keys())))

    # get layers for the product
    response = requests.get(url+'product/{0}'.format(product))
    layer_response = response.json()
    layers = layer_response.keys()

    # formulate query
    date_object = [ { "startDate": startDate, "endDate": endDate } ]
    layer_object = [ {"product": product, "layer": ilayer} for ilayer in layers]
    ftr = { "type": "Feature", "properties": {}, "geometry": { "type": "Polygon", "coordinates": coords } }
    # needs to be GeoJSON
    geo_object = { "type": "FeatureCollection", "filename": "none", "features": [ftr] }
    output_object = { "format": { "type" : file_type }, "projection": projection_name }

    # query/ task object
    task_object = { "task_type": task_type, "task_name": task_name,
                    "params": {  "dates": date_object, "layers": layer_object,
                                 "geo": geo_object, "output": output_object }
                  }

    # submit task
    response = requests.post(url+'task', json=task_object, headers={'Authorization': 'Bearer {0}'.format(token)})
    task_response = response.json()

    if ('task_id' not in task_response):
        raise RuntimeError ('Error in task submission.  Message {}'.format(task_response['message']))

    # return task_id
    return task_response['task_id']


def download_file(nargs):

    task_id, ifile, dest_dir, S3_bucket  = nargs

    url = 'https://lpdaacsvc.cr.usgs.gov/appeears/api/'
    img_ext = ['tif','nc']

    file_id = ifile['file_id']

    response = requests.get(url+'bundle/{0}/{1}'.format(task_id, file_id), stream=True)
    content_disposition = cgi.parse_header(response.headers['Content-Disposition'])[1]

    filename = os.path.basename(content_disposition['filename'])
    # example filename  MCD43A4.006_Nadir_Reflectance_Band6_doy2016336_aid0001.tif

    if (ifile['file_type'] in img_ext):

        # output setup for images <dest dir>/Product/Date
        # get product
        prod = filename.split('_')[0]
        # get day of year
        date = (filename.split('doy')[-1]).split('_')[0]
        filename = ('_'.join(filename.split('_')[0:-2])) + '_' + date + '.' + ifile['file_type']

        # output file name example MCD43A4.006_Nadir_Reflectance_Band6_2016336.tif
        odir = os.path.join(dest_dir, prod, date)
    else:

        # xml files etc go to the main <dest dir>
        odir = dest_dir

    filepath = os.path.join(odir, filename)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    if (os.path.isfile(filepath)):
        # file already exists on output dir
        logging.info('Skiping file %s',filepath)
        return

    logging.info('Downloading file %s', filepath)
    with open(filepath, 'wb') as f:
        for data in response.iter_content(chunk_size=8192):
            f.write(data)

    # push to S3 if required
    if (S3_bucket is not None):
        # Copy data files to S3
        s3 = boto3.client('s3')
        key = os.path(prod,date,filename)
        s3.upload_file(filepath, S3_bucket, key)
        # Remove local copy of file
        os.remove(filepath)

    # return prod, date, filepath (which is path + filename), mayber write this to file
    # { 'prod' : { doy : filepath } }   eg { 'MCD43A4.006' : { '2016001' : '<prod>/doy/sr.tif' } } or
    # { 'prod' : 'MCD43A4.006', 'doy': '2016001', 'file': <prod>/<doy/sr.tif' }

    return


def download_bundle_mp(token, dest_dir, task_ids=None, S3_bucket=None, img_ext=['tif','nc'], ncores=None):


    if (ncores is None):
        ncores = mp.cpu_count()

    logging.info('Using  %s cores', str(ncores))
    pool = mp.Pool(processes=ncores)

    # check status - find all tasks with
    task_list = list_tasks(token)

    # if task_id supplied check task is in list
    if (task_ids is not None):
        task_ids_list = [ix['task_id'] for ix in task_list ]
        if (all(ix in task_ids_list for ix in task_ids) == False):
            msg = 'Requested task(s) not found.  Requested -{} Available- {}'
            raise RuntimeError ( msg.format(', '.join(task_ids), ', '.join(task_ids_list)) )
        task_list = [itask for itask in task_list if itask['task_id'] in task_ids]

    # if task not supplied download all

    processing_task_list = list(reversed(task_list))

    while (len(processing_task_list) != 0):

        # scan list of tasks and see if any are ready to be downloaded
        # if so commmence download
        for itask in processing_task_list:

            task_id = itask['task_id']
            status_response = check_status(token, task_id)
            logging.info(status_response)

            if ("status" in status_response.keys()):

                if (status_response['status'] == 'done'):

                    # get the bundle
                    bundle_response = get_bundle(task_id)

                    # for each file in the bundle download
                    datasets = [(task_id, ifile, dest_dir, S3_bucket) for ifile in bundle_response['files'] ]
                    print(len(bundle_response['files']))
                    res = pool.map(download_file, datasets)

                    # res will have [ { 'prod' : 'MCD43A4.006', 'doy': '2016001', 'file': <prod>/<doy/sr.tif' } ]

                    processing_task_list.remove(itask)

        if (len(processing_task_list) != 0):
            logging.info('Waiting for task(s) to complete...sleeping 5 sec')
            time.sleep(5)


    '''
    for itask in reversed(task_list):

        task_id = itask['task_id']
        bcomplete = False

        while (bcomplete is False):
           # check status of task, is it ready for downloading

            status_response = check_status(token, task_id)

            if ("status" in status_response.keys()):

                bcomplete = True
                # get the bundle

                bundle_response = get_bundle(task_id)

                # for each file in the bundle download
                datasets = [(task_id, ifile, dest_dir, S3_bucket) for ifile in bundle_response['files'] ]
                res = pool.map(download_file, datasets)

            else:

                # the option of not sleeping
                logging.info('Waiting for task to complete...sleeping 5 sec')
                time.sleep(5)

        logging.info(status_response)
    '''

    return # res will have [ { 'prod' : 'MCD43A4.006', 'doy': '2016001', 'file': <prod>/<doy/sr.tif' } ]


def download_bundle(token, dest_dir, task_ids=None, S3_bucket=None, img_ext=['tif','nc']):

    url = 'https://lpdaacsvc.cr.usgs.gov/appeears/api/'

    # check status - find all tasks with
    response = requests.get( url+'task', headers={'Authorization': 'Bearer {0}'.format(token)})
    task_list = response.json()

    # if task_id supplied check task is in list
    if (task_ids is not None):
        task_ids_list = [ix['task_id'] for ix in task_list ]
        if (all(ix in task_ids_list for ix in task_ids) == False):
            msg = 'Requested task(s) not found.  Requested -{} Available- {}'
            raise RuntimeError ( msg.format(', '.join(task_ids), ', '.join(task_ids_list)) )
        task_list = task_list[task_ids]

    # if task not supplied download all

    for itask in reversed(task_list):

        task_id = itask['task_id']
        bcomplete = False

        while (bcomplete is False):
           # check status of task, is it ready for downloading
            response = requests.get(url+'status/{0}'.format(task_id),
                        headers={'Authorization': 'Bearer {0}'.format(token)})
            status_response = response.json()

            if ("status" in status_response.keys()):

                bcomplete = True
                # get the bundle
                response = requests.get(url+'bundle/{0}'.format(task_id))
                bundle_response = response.json()

                # for each file in the bundle download
                for ifile in bundle_response['files']:

                    file_id = ifile['file_id']

                    response = requests.get(url+'bundle/{0}/{1}'.format(task_id, file_id), stream=True)
                    content_disposition = cgi.parse_header(response.headers['Content-Disposition'])[1]

                    filename = os.path.basename(content_disposition['filename'])
                    # example filename  MCD43A4.006_Nadir_Reflectance_Band6_doy2016336_aid0001.tif

                    if (ifile['file_type'] in img_ext):

                        # output setup for images <dest dir>/Product/Date
                        # get product
                        prod = filename.split('_')[0]
                        # get day of year
                        date = (filename.split('doy')[-1]).split('_')[0]
                        filename = ('_'.join(filename.split('_')[0:-2])) + '_' + date + ifile['file_type']

                        # output file name example MCD43A4.006_Nadir_Reflectance_Band6_2016336.tif
                        odir = os.path.join(dest_dir, prod, date)
                    else:

                        # xml files etc go to the main <dest dir>
                        odir = dest_dir

                    filepath = os.path.join(odir, filename)
                    os.makedirs(os.path.dirname(filepath), exist_ok=True)

                    if (os.path.isfile(filepath)):
                        # file already exists on output dir
                        logging.info('Skiping file %s',filepath)
                        continue

                    logging.info('Downloading file %s', filepath)
                    with open(filepath, 'wb') as f:
                        for data in response.iter_content(chunk_size=8192):
                            f.write(data)

                   # push to S3 if required


            else:

                # the option of not sleeping
                logging.info('Waiting for task to complete...sleeping 5 sec')
                time.sleep(5)

        logging.info(status_response)

    return


def date_range(startDate, endDate, dayDelta=90):

    #date_list = [ ( d1+(ix*delta), min(d2,d1+((ix+1)*delta)) ) for ix in range( ceil((d2-d1)/delta) ) ]

    d1 = datetime.datetime.strptime(startDate, '%m-%d-%Y')
    d2 = datetime.datetime.strptime(endDate, '%m-%d-%Y')
    delta = datetime.timedelta(days=dayDelta)
    day1 = datetime.timedelta(days=1)
    print(day1)

    nint = ceil((d2-d1)/delta)
    date_list = []
    for ix in range(nint):
        if (ix == 0):
            s1 = d1+(ix*delta)
        else:
            s1 = e1+day1
        e1 = min(s1+delta,d2)
        date_list.append( ( s1.strftime('%m-%d-%Y'), e1.strftime('%m-%d-%Y') ) )

    return date_list


# need to pass parameter - number of dates of imagery
# to process in a batch
def ingest(list_of_file, S3_bucket_in ):


    # s3_grouped_scenes = [unique_scenes_list[i:i+CHUNK] for i in range(0, nuniq, CHUNK)]

    # copy from s3 to local instance

    # get metadata

    # index

    # ingest

    # clean up

    '''
        logging.info('Preparing')
        logging.info(scene_tmp_loc_list)
        #usgsls_prepare_ama_mc.main(scene_tmp_loc_list)

        logging.info('Indexing')
        #logging.info(str_scenes_list)
        str_scene_list = ' '.join(scene_tmp_loc_list)
        cmdline = 'datacube dataset add --auto-match ' + str_scene_list
        logging.info(cmdline)
        os.system(cmdline)

        logging.info('Ingesting')
        tmpfile = workingdir + '/' + 'group'+str(cg)+'.txt'
        cmdline = 'datacube -v ingest -c ' +  ingestyaml  +  ' --executor multiproc 36 2> ' + tmpfile
        logging.info(cmdline)
        #os.system(cmdline)
        out = os.popen(cmdline).read()
        #logging.debug('Ingestion details')
        #with open(tmpfile) as f:
            #read_data = f.read()
        #logging.debug(read_data)
        logging.info('Ingestion results')
        logging.info(out)

        for tmpdir in scene_tmp_loc_list:
            shutil.rmtree(tmpdir)
    '''

    return



def grab_modis():

    coords = [[[ 112.582024, -10.282572],
               [ 112.582024, -44.013406],
               [ 153.8587, -44.013406],
               [ 153.8587, -10.282572],
               [ 112.582024, -10.282572]]]

    product_list = ['MCD43A4.006', 'MOD13Q1.006']

    # date MM-DD-YYYY
    startDate = '01-01-2016'
    endDate = '05-01-2018'
    # in days
    dayDelta = 90
    task_prefix = 'AU'
    dest_dir = '/g/data1/k88'
    download = True
    s3_bucket = 'digiscape-MODIS-o'
    user = 'mikec'

    download = False

    # serivice applies restrictions on task size, need to split
    # large queries into smaller sub queries
    date_list = date_range(startDate, endDate)

    token = login(user)

    # loop over product loop, over date
    task_id_list = []
    for product in product_list:
        for idate in date_list:
            task_name = task_prefix + '_' + product + '_' + idate[0] + '_' + idate[1]
            task_id = submit_query(token, idate[0], idate[1], product, coords,  task_name=task_name)
            task_id_list.append(task_id)

    if (download):
        download_bundle_mp(token, dest_dir, task_ids=task_id_list, S3_bucket=None)
        for task_id in task_id_list:
            delete_task(token, task_id)

    logout(token)

    # ingest
    # # res will have [ { 'prod' : 'MCD43A4.006', 'doy': '2016001', 'file': <prod>/<doy/sr.tif' } ]
    # for each product a ingest config file, ie. modis_mcd43a4_albers.yaml
    # ingest(list_of_file, S3_bucket_in )

    # s3_grouped_scenes = [unique_scenes_list[i:i+CHUNK] for i in range(0, nuniq, CHUNK)]

    # copy from s3 to local instance

    product = list(set([ilist['prod'] for ilist in result_list]))

    # get metadata

    '''
        logging.info('Preparing')
        logging.info(scene_tmp_loc_list)
        #usgsls_prepare_ama_mc.main(scene_tmp_loc_list)
    '''

    # index

    '''
        logging.info('Indexing')
        #logging.info(str_scenes_list)
        str_scene_list = ' '.join(scene_tmp_loc_list)
        cmdline = 'datacube dataset add --auto-match ' + str_scene_list
        logging.info(cmdline)
        os.system(cmdline)
    '''

    # ingest

    '''
        logging.info('Ingesting')
        tmpfile = workingdir + '/' + 'group'+str(cg)+'.txt'
        cmdline = 'datacube -v ingest -c ' +  ingestyaml  +  ' --executor multiproc 36 2> ' + tmpfile
        logging.info(cmdline)
        #os.system(cmdline)
        out = os.popen(cmdline).read()
        #logging.debug('Ingestion details')
        #with open(tmpfile) as f:
            #read_data = f.read()
        #logging.debug(read_data)
        logging.info('Ingestion results')
        logging.info(out)
    '''

    # clean up

    '''
        for tmpdir in scene_tmp_loc_list:
            shutil.rmtree(tmpdir)
    '''

    return



if __name__ == '__main__':


    user = 'mikec'

    token = login(user)

    print(token)


    coords = [[[ 112.582024, -10.282572],
               [ 112.82024, -44.013406],
               [ 153.8587, -44.013406],
               [ 153.8587, -10.282572],
               [ 112.582024, -10.282572]]]

    product = 'MOD13Q1.006'

    # date MM-DD-YYYY
    startDate = '01-01-2017'
    endDate = '01-30-2017'
    dest_dir = '/g/data1/k88/MODIS_F/'


    date_list = date_range(startDate, endDate, dayDelta=90)

    print(date_list)

    '''

    grab_modis()

    '''




    #task_id = submit_query(token, startDate, endDate, product, coords)



    task_id = 'e4d8988d-3cd7-46cf-a187-affdafcd4816'

    print(task_id)

    #task_list = list_tasks(token)

    #task_ids = [itask['task_id'] for itask in task_list]

    download_bundle_mp(token, dest_dir)#, task_ids=task_ids) #[task_id]) #, S3_bucket=None, img_ext=['tif','nc'], ncores=None):


    response = logout(token)

    print(response)






    '''

    #shpfile = './data/wa_poly.shp'
    dest_dir = '/g/data1/k88/MODIS_D/'
    download = True
    submit = False

    #shpfid = fiona.open(shpfile, 'r')
    #shp = list(shpfid)
    #pprint.pprint(shp)
    #shpfid.close()

    #password = getpass.getpass()
    password = 'CxCc7Q2KrOPIyDkYz4BZ'
    response = requests.post('https://lpdaacsvc.cr.usgs.gov/appeears/api/login', auth=('mikec', password))
    token_response = response.json()
    print(token_response)

    token = token_response['token']


    if (submit == True):
        task_type = 'area'
        # date MM-DD-YYYY
        startDate = '08-02-2016'
        endDate = '12-01-2016'
        product_id = 'MCD43A4.006'
        #nb = 7

        #layer_name = ['Nadir_Reflectance_Band'+str(ix+1) for ix in list(range(nb))]
        layer_name = ['Nadir_Reflectance_Band1', 'Nadir_Reflectance_Band2', 'Nadir_Reflectance_Band3',
                      'Nadir_Reflectance_Band4', 'Nadir_Reflectance_Band5', 'Nadir_Reflectance_Band6',
                      'Nadir_Reflectance_Band7']

        projection_name = 'geographic'
        file_type = 'geotiff'

        date_object = { "startDate": startDate, "endDate": endDate }
        #layer_object = { "product": product_id, "layer": layer_name }

        layer_object = [ {"product": product_id, "layer": ilayer} for ilayer in layer_name]

        # or shape file
        #coords = shp[0]["geometry"]["coordinates"]
        # all of aus

        coords = [[[ 112.582024, -10.282572],
                   [ 112.582024, -44.013406],
                   [ 153.8587, -44.013406],
                   [ 153.8587, -10.282572],
                   [ 112.582024, -10.282572]]]
        ftr = { "type": "Feature", "properties": {}, "geometry": { "type": "Polygon", "coordinates": coords } }
        # needs to be GeoJSON
        geo_object = { "type": "FeatureCollection", "filename": "none", "features": [ftr] }
        #geo_object = shp[0]

        output_object = { "format": { "type" : file_type }, "projection": projection_name }

        task_object = { "task_type": task_type,
                        "task_name": "Test_MODIS",
                        "params": {
                            "dates": [date_object],
                            "layers": layer_object,
                            "geo": geo_object,
                            "output": output_object }
                      }

        # convert dict to json string
        task_json = json.dumps(task_object, indent=4, sort_keys=True)
        #pprint.pprint(task_json)

        # submit task

        # query string
        response = requests.post(
                'https://lpdaacsvc.cr.usgs.gov/appeears/api/task',
                #params=task,
                #json=task_json,
                json=task_object,
                headers={'Authorization': 'Bearer {0}'.format(token)})
        task_response = response.json()
        print(task_response)


    if download == True:
        # list submitted tasks

        response = requests.get(
                'https://lpdaacsvc.cr.usgs.gov/appeears/api/task',
                headers={'Authorization': 'Bearer {0}'.format(token)})

        #pprint.pprint(type(response.json()))
        # returns list of dict
        task_list = response.json()

        # check status - find all tasks with

        for itask in reversed(task_list):
            print(itask)
            task_id = itask['task_id']
            bcomplete = False
            while (bcomplete is False):
                response = requests.get(
                        'https://lpdaacsvc.cr.usgs.gov/appeears/api/status/{0}'.format(task_id),
                        headers={'Authorization': 'Bearer {0}'.format(token)})
                status_response = response.json()
                if ("status" in status_response.keys()):
                    print('Conmplete')
                    # task complete - ready for download
                    print(status_response["status"])
                    bcomplete = True
                    # get the bundle
                    response = requests.get('https://lpdaacsvc.cr.usgs.gov/appeears/api/bundle/{0}'.format(task_id))
                    bundle_response = response.json()
                    print('###Bundle')
                    pprint.pprint(bundle_response)
                    # for each file in the bundle download
                    for ifile in bundle_response['files']:
                        file_id = ifile['file_id']
                        response = requests.get(
                            'https://lpdaacsvc.cr.usgs.gov/appeears/api/bundle/{0}/{1}'.format(task_id, file_id),
                            stream=True)
                        content_disposition = cgi.parse_header(response.headers['Content-Disposition'])[1]
                        #print('### Content Disposition')
                        #print(content_disposition)
                        filename = os.path.basename(content_disposition['filename'])
                        ext = filename.split('.')[-1]
                        if (ext == 'tif'):
                            # get product
                            prod = filename.split('_')[0]
                            # get day of year
                            date = (filename.split('doy')[-1]).split('_')[0]
                            filename = ('_'.join(filename.split('_')[0:-2])) + '_' + date + '.tif'
                            # <dest dir>/Product/Date
                            odir = os.path.join(dest_dir, prod, date)
                        else:
                            odir = dest_dir
                        filepath = os.path.join(odir, filename)
                        os.makedirs(os.path.dirname(filepath), exist_ok=True)
                        if (os.path.isfile(filepath)):
                            print('Skiping file ' + filepath)
                            continue
                        print('Downloading file ' +  filepath)
                        with open(filepath, 'wb') as f:
                            for data in response.iter_content(chunk_size=8192):
                                f.write(data)


                else:
                    print('Waiting for task to complete...sleeping 5 sec')
                    time.sleep(5)
            print(status_response)

    # delete tasks
    '''

    '''
    for itask in task_list:
        print(itask)
        task_id = itask['task_id']
        print(task_id)
        response = requests.delete(
            'https://lpdaacsvc.cr.usgs.gov/appeears/api/task/{0}'.format(task_id),
            headers={'Authorization': 'Bearer {0}'.format(token)})
        print(response.status_code)
    '''











