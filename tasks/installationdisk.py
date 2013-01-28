from __future__ import absolute_import
from tasks.celery import celery, logger
import urllib2
import os
import re
import time

match_disk = re.compile('.*\.(iso|img|dvd)$')

@celery.task()
def delete_file(path):
    try:
        os.remove(path)
    except Exception as e:
        return {'args': {'msg': e.strerror}}

@celery.task()
def list_files(path):
    ret = {'disks': []}
    for name in os.listdir(path):
        file_path = os.path.join(path, name)
        if os.path.isfile(file_path) and match_disk.search(name):
            total_bytes = os.path.getsize(file_path)
            disk = {'filename': name, 'total_bytes': total_bytes}
            ret['disks'].append(disk)
    return ret

@celery.task()
def download_file(url, path):
    file_name = url.split('/')[-1]
    file_path = os.path.join(path, file_name)
    stream = urllib2.urlopen(url)
    io = open(file_path, 'wb')
    meta = stream.info()
    file_size = int(meta.getheaders("Content-Length")[0])

    celery.current_task.update_state(state='PROGRESS', meta=
        {
            'total_bytes': file_size,
            'percent': 0.0,
            'total_bytes_dl': 0
        })

    file_size_dl = 0
    block_sz = 8192

    now = time.time()
    while True:
        buf = stream.read(block_sz)
        if not buf: break

        file_size_dl += len(buf)
        io.write(buf)

        if (time.time() - now) > 5:
            celery.current_task.update_state(state='PROGRESS', meta=
                {
                    'total_bytes': file_size,
                    'percent': file_size_dl * 100. / file_size,
                    'total_bytes_dl': file_size_dl
                })
            now = time.time()

    celery.current_task.update_state(state='COMPLETE', meta=
        {
            'total_bytes': file_size,
            'percent': file_size_dl * 100. / file_size,
            'total_bytes_dl': file_size_dl
        })
    io.close()
    return {
            'total_bytes': file_size,
            'percent': 100.0,
            'total_bytes_dl': file_size_dl
        }
