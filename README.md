# demo.pycsw.org

This is the setup for http://demo.pycsw.org

```bash
BASEDIR=/path/to/dir
mkdir $BASEDIR
cd $BASEDIR
git clone https://github.com/geopython/demo.pycsw.org.git .
virtualenv $BASEDIR
. bin/$BASEDIR  # yes, that's a period
git clone https://github.com/geopython/demo.pycsw.org.git .
# install deps
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
sudo ln -s httpd.d/demo.pycsw.org /etc/apache2/sites-available/
sudo /usr/sbin/apache2ctl graceful
# setup viewer
cd www
git clone git@github.com:boundlessgeo/gxp.git && cd $_
# setup GXP dependencies
git submodule init
git submodule update
cd ..
# use local patch of GXP's catalogue widget
cp viewer/CatalogueSearchPanel.js gxp/src/script/widgets/
```
