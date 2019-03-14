import requests
import getpass
import json
import time

import fiona
import shapely
import shapely.geometry

import cgi
import os

import pprint

if __name__ == '__main__':

    #shpfile = './data/wa_poly.shp'
    dest_dir = '/g/data1/k88/MODIS_E/'
    download = True
    submit = True

    #shpfid = fiona.open(shpfile, 'r')
    #shp = list(shpfid)
    #pprint.pprint(shp)
    #shpfid.close()

    #password = getpass.getpass()
    response = requests.post('https://lpdaacsvc.cr.usgs.gov/appeears/api/login', auth=('mikec', password))
    token_response = response.json()
    print(token_response)

    token = token_response['token']


    if (submit == True):
        task_type = 'area'
        # date MM-DD-YYYY
        startDate = '12-02-2016'
        endDate = '02-01-2017'
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

        '''
        coords = [[[-104.29394567012787, 43.375488325953484],
                   [-104.29394567012787, 44.562011763453484],
                   [-103.17334020137787, 44.562011763453484],
                   [-103.17334020137787, 43.375488325953484],
                   [-104.29394567012787, 43.375488325953484]]]
        '''
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
        task = {
                'task_type' : 'point',
                'task_name': 'my-task',
                'startDate': '01-01-2010',
                'endDate': '01-31-2010',
                'layer': 'MOD11A1.006,LST_Day_1km',
                'coordinate': '42,-72'
        }
        print('### Here')
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
    for itask in task_list:
        print(itask)
        task_id = itask['task_id']
        print(task_id)
        response = requests.delete(
            'https://lpdaacsvc.cr.usgs.gov/appeears/api/task/{0}'.format(task_id),
            headers={'Authorization': 'Bearer {0}'.format(token)})
        print(response.status_code)
    '''











