from __future__ import absolute_import
from tasks.celery import celery
import urllib2
import os

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

    while True:
        buf = stream.read(block_sz)
        if not buf: break

        file_size_dl += len(buf)
        io.write(buf)

        if ((file_size_dl * 100. / file_size) % 5) == 0:
            celery.current_task.update_state(state='PROGRESS', meta=
                {
                    'total_bytes': file_size,
                    'percent': file_size_dl * 100. / file_size,
                    'total_bytes_dl': file_size_dl
                })

    celery.current_task.update_state(state='COMPLETE', meta=
        {
            'total_bytes': file_size,
            'percent': file_size_dl * 100. / file_size,
            'total_bytes_dl': file_size_dl
        })
    io.close()
