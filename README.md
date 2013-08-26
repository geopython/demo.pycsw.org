demo.pycsw.org
==============

This is the setup for http://demo.pycsw.org

    # virtualenv /path/to/dir
    # source /path/to/dir/bin/activate
    cd /path/to/dir
    git clone https://github.com/geopython/demo.pycsw.org.git .
    # install deps
    pip install -e .
    pip install -r requirements.txt
    # install pycsw source
    git clone https://github.com/geopython/pycsw.git src/pycsw && cd $_
    python setup.py build
    python setup.py install
    # setup data
    cd ../..
    # update server.home, server.url and repository.database in pycsw/cite/cite.cfg
    # update server.home, server.url and repository.database in pycsw/gisdata/gisdata.cfg
    # update server.home, server.url and repository.database in pycsw/services/services.cfg
    # setup gisdata database and load records
    pycsw-admin.py -c setup_db -f pycsw/gisdata/gisdata.cfg
    pycsw-admin.py -c load_records -f pycsw/gisdata/gisdata.cfg -p `python -c 'import gisdata; print gisdata.GOOD_METADATA'` -r
    # setup services database
    pycsw-admin.py -c setup_db -f pycsw/services/services.cfg
    # setup www
    cp src/pycsw/csw.wsgi pycsw/
    sudo ln -s httpd.d/demo.pycsw.org /etc/apache2/sites-available/
    sudo /usr/sbin/apache2ctl graceful
    # setup viewer
    git clone git@github.com:opengeo/gxp.git && cd $_
    # setup GXP dependencies
    git submodule init
    git submodule update
    cd ..
    # use local patch of GXP's catalogue widget
    cp www/viewer/CatalogueSearchPanel.js www/gxp/src/script/widgets/
