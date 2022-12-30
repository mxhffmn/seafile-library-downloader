import argparse
import glob
import logging
import os
import shutil
import sys
import time

import requests

# define logger
logging.basicConfig(level="INFO", stream=sys.stdout, encoding='utf-8',
                    format='%(levelname)s | %(asctime)s | %(message)s')
logger = logging.getLogger('logger')

# parse arguments
parser = argparse.ArgumentParser(
    description='Downloads individual ZIP files for all folders of a Seafile library/repository.')
parser.add_argument(dest='auth_token', type=str,
                    help='the authentication token to use for all requests to the server')
parser.add_argument(dest='repo_id', type=str,
                    help='the repository ID to download')
parser.add_argument('--server', dest='server', type=str, default='cloud.seafile.com',
                    help='the server where the repository is located')
parser.add_argument('--save_dir', dest='save_dir', type=str, default='.',
                    help='the local directory to save the downloaded ZIP files to')
parser.add_argument('--sleep_time', dest='sleep_time', type=int, default=3,
                    help='the time interval (in seconds) to wait between consecutive requests for asking '
                         'if a ZIP file is ready to be downloaded')
parser.add_argument('--wait_time', dest='wait_time', type=int, default=300,
                    help='the total time to wait for a ZIP file to be created')
parser.add_argument('--remove_unknown', dest='remove_unknown', action='store_true', default=False,
                    help='if set all ZIP files in the output directory that do not match directories in the '
                         'Seafile library are removed after downloading is finished')

args = parser.parse_args()

logging.info(f'Starting download with parameters: {vars(args)}.')

# define common headers
headers = {
    'Authorization': f'Token {args.auth_token}',
    'Accept': 'application/json'
}

# get list of all subdirectories of target directory
resp_dir_list = requests.get(f'https://{args.server}/api/v2.1/repos/{args.repo_id}/dir/', allow_redirects=True,
                             headers=headers)
dir_list = resp_dir_list.json()['dirent_list']
dir_list_filtered = []
for dir_ent in dir_list:
    if dir_ent['type'] == 'dir':
        dir_list_filtered.append(dir_ent['name'])
logger.info('Requested list of all files in library.')

# create ZIP task for all subdirectories of target directory and download ZIPs
# dir_list_filtered = ['Dir_Name']
for dir_ent in dir_list_filtered:
    # create params
    params = [
        ('parent_dir', '/'),
        ('dirents', dir_ent)
    ]

    # create ZIP
    resp_zip_creation = requests.get(f'https://{args.server}/api/v2.1/repos/{args.repo_id}/zip-task/',
                                     allow_redirects=True,
                                     params=params,
                                     headers=headers)
    zip_token = resp_zip_creation.json()['zip_token']
    logger.info(f'Requested creation of ZIP for directory \'{dir_ent}\' with ZIP access token \'{zip_token}\'.')

    # watch progress
    sleep_times = 0
    while True:
        if sleep_times * args.sleep_time > args.wait_time:
            logger.warning(
                f'Waited {sleep_times * args.sleep_time} seconds to download directory \'{dir_ent}\'. '
                f'Skipping directory \'{dir_ent}\'.')
            break
        zip_progress_resp = requests.get(f'https://{args.server}/api/v2.1/query-zip-progress/',
                                         allow_redirects=True,
                                         params={'token': zip_token},
                                         headers=headers)
        zip_progress_data = zip_progress_resp.json()
        if 'zipped' not in zip_progress_data or 'total' not in zip_progress_data:
            logger.error(f'JSON payload not as expected: {zip_progress_resp.text}. '
                         f'This usually indicates that the size of the directory is too large.')
            logger.warning(f'Skipping directory \'{dir_ent}\'.')
            break
        else:
            if zip_progress_data['zipped'] == zip_progress_data['total']:
                # download ready -> write file
                logger.info(f'Downloading directory \'{dir_ent}\'...')

                final_zip_resp = requests.get(f'https://{args.server}/seafhttp/zip/{zip_token}',
                                              headers=headers, allow_redirects=True, stream=True)

                with open(f'{args.save_dir}/{dir_ent}.zip', 'wb') as f:
                    shutil.copyfileobj(final_zip_resp.raw, f)

                logger.info(f'Successfully downloaded directory \'{dir_ent}\'.')

                break
            else:
                logger.info(f'Requested progress of ZIP for directory \'{dir_ent}\' -> Not ready ({sleep_times + 1})')

        # wait
        time.sleep(args.sleep_time)
        sleep_times += 1

# check if there are old stored directories that need to be deleted
if args.remove_unknown:
    files = glob.glob(f'{args.save_dir}/*.zip', recursive=False)
    for file in files:
        # trim
        new_file_name = file.rsplit(os.sep)[-1].rstrip('.zip')
        if new_file_name not in dir_list_filtered:
            os.remove(new_file_name + '.zip')
            logger.info(f'Removed file \'{new_file_name}.zip\' as it seems to be obsolete.')

logger.info('Download(s) finished. Exiting.')
