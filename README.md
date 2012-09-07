demo.pycsw.org
==============

This is the setup for demo.pycsw.org

    # virtualenv /path/to/dir
    # source /path/to/dir/bin/activate
    cd /path/to/dir
    git clone https://github.com/geopython/demo.pycsw.org.git .
    # install deps
    pip install -r requirements.txt
    # install pycsw source
    mkdir src && cd $_
    git clone https://github.com/geopython/pycsw.git pycsw && cd $_
    python setup.py build
    python setup.py install
    # setup data
    cp data/cite/records.db ../../pycsw/cite/
    cd ../..
    # update server.home, server.url and repository.database in pycsw/cite/cite.cfg
    # update server.home, server.url and repository.database in pycsw/gisdata/gisdata.cfg
    pycsw-admin.py -c setup_db -f pycsw/gisdata/gisdata.cfg
    pycsw-admin.py -c load_records -f pycsw/gisdata/gisdata.cfg -p `python -c 'import gisdata; print gisdata.GOOD_METADATA'` -r
    # setup web
    cp src/pycsw/csw.wsgi pycsw/
    ln -s httpd.d/demo.pycsw.org /etc/apache2/sites-available/
    sudo /usr/sbin/apache2ctl graceful