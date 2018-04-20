''' utilities to manage bluepyopt job on nsg portal '''
import logging
import os.path
import tarfile
import xml.etree.ElementTree
import time
import requests
from lxml import objectify

L = logging.getLogger(__name__)
KEY = 'Application_Fitting-DA5A3D2F8B9B4A5D964D4D2285A49C57'
URL = 'https://nsgr.sdsc.edu:8443/cipresrest/v1'
TOOL = 'BLUEPYOPT_TG'


def launch_opt(user, password, job_zip, n_cores=10, n_nodes=2, runtime=0.5):
    ''' launch an optimization with job_zip description on nsg portal '''
    L.info('launch_opt(%s, xxx, %s, %d, %d , %d)', user, job_zip, n_cores,
           n_nodes, runtime)
    headers = {'cipres-appkey': KEY}
    payload = {
        'tool': TOOL,
        'metadata.statusEmail': 'false',
        'vparam.number_cores_': str(n_cores),
        'vparam.number_nodes_': str(n_nodes),
        'vparam.runtime_': str(runtime),
        'vparam.filename_': 'init.py'
    }
    files = {'input.infile_': open(job_zip, 'rb')}

    r = requests.post(
        '{}/job/{}'.format(URL, user),
        auth=(user, password),
        data=payload,
        headers=headers,
        files=files)
    r.raise_for_status()
    root = xml.etree.ElementTree.fromstring(r.text)
    return root.find('selfUri/url').text


def check_job_status(job_url, user, password):
    ''' return job status and output_url if COMPLETED '''
    L.info('Check_job_status(%s, %s, xxxx)', job_url, user)
    headers = {'cipres-appkey': KEY}
    r = requests.get(job_url, auth=(user, password), headers=headers)
    r.raise_for_status()
    root = xml.etree.ElementTree.fromstring(r.text)
    job_status = root.find('jobStage').text
    output_url = None
    if job_status == 'COMPLETED':
        output_url = root.find('resultsUri/url').text
    return job_status, output_url


def wait_completion(job_url, user, password, polling_interval=30):
    ''' check every polling_interval seconds if job is COMPLETED and returns output_url'''
    while True:
        job_status, output_url = check_job_status(job_url, user, password)
        if job_status == 'COMPLETED':
            return output_url
        L.info("waiting %d s", polling_interval)
        time.sleep(polling_interval)


def download_output(output_url, user, password, tmp_dir):
    ''' download checkpoint.pkl from output_url into tmp_dir
    '''
    L.info('download_output(%s, %s, xxx, %s)', output_url, user, tmp_dir)
    headers = {'cipres-appkey': KEY}
    r = requests.get(output_url, headers=headers, auth=(user, password))
    r.raise_for_status()
    results = objectify.fromstring(str(r.text))
    d_url = [
        jobfile.downloadUri.url for jobfile in results.jobfiles.iterchildren()
        if jobfile.filename == 'output.tar.gz'
    ][0]
    r = requests.get(d_url, auth=(user, password), headers=headers)
    r.raise_for_status()
    output_tar = os.path.join(tmp_dir, 'output.tar.gz')
    L.debug('output_tar: %s', output_tar)
    with open(output_tar, 'wb') as fd:
        for chunk in r.iter_content():
            fd.write(chunk)
    f = tarfile.open(output_tar)
    tar_info = [
        member_info for member_info in f.getmembers()
        if 'checkpoint.pkl' in member_info.name
    ][0]
    checkpoint_path = os.path.join(tmp_dir, 'checkpoint.pkl')
    L.debug('checkpoint_path: %s', checkpoint_path)
    with open(checkpoint_path, 'wb') as checkpoint:
        file_checkpoint = f.extractfile(tar_info)
        checkpoint.write(file_checkpoint.buffer)
    return checkpoint_path
