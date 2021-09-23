# -*- coding: utf-8 -*-
# ***********************************************************************
# ******************  CANADIAN ASTRONOMY DATA CENTRE  *******************
# *************  CENTRE CANADIEN DE DONNÉES ASTRONOMIQUES  **************
#
#  (c) 2019.                            (c) 2019.
#  Government of Canada                 Gouvernement du Canada
#  National Research Council            Conseil national de recherches
#  Ottawa, Canada, K1A 0R6              Ottawa, Canada, K1A 0R6
#  All rights reserved                  Tous droits réservés
#
#  NRC disclaims any warranties,        Le CNRC dénie toute garantie
#  expressed, implied, or               énoncée, implicite ou légale,
#  statutory, of any kind with          de quelque nature que ce
#  respect to the software,             soit, concernant le logiciel,
#  including without limitation         y compris sans restriction
#  any warranty of merchantability      toute garantie de valeur
#  or fitness for a particular          marchande ou de pertinence
#  purpose. NRC shall not be            pour un usage particulier.
#  liable in any event for any          Le CNRC ne pourra en aucun cas
#  damages, whether direct or           être tenu responsable de tout
#  indirect, special or general,        dommage, direct ou indirect,
#  consequential or incidental,         particulier ou général,
#  arising from the use of the          accessoire ou fortuit, résultant
#  software.  Neither the name          de l'utilisation du logiciel. Ni
#  of the National Research             le nom du Conseil National de
#  Council of Canada nor the            Recherches du Canada ni les noms
#  names of its contributors may        de ses  participants ne peuvent
#  be used to endorse or promote        être utilisés pour approuver ou
#  products derived from this           promouvoir les produits dérivés
#  software without specific prior      de ce logiciel sans autorisation
#  written permission.                  préalable et particulière
#                                       par écrit.
#
#  This file is part of the             Ce fichier fait partie du projet
#  OpenCADC project.                    OpenCADC.
#
#  OpenCADC is free software:           OpenCADC est un logiciel libre ;
#  you can redistribute it and/or       vous pouvez le redistribuer ou le
#  modify it under the terms of         modifier suivant les termes de
#  the GNU Affero General Public        la “GNU Affero General Public
#  License as published by the          License” telle que publiée
#  Free Software Foundation,            par la Free Software Foundation
#  either version 3 of the              : soit la version 3 de cette
#  License, or (at your option)         licence, soit (à votre gré)
#  any later version.                   toute version ultérieure.
#
#  OpenCADC is distributed in the       OpenCADC est distribué
#  hope that it will be useful,         dans l’espoir qu’il vous
#  but WITHOUT ANY WARRANTY;            sera utile, mais SANS AUCUNE
#  without even the implied             GARANTIE : sans même la garantie
#  warranty of MERCHANTABILITY          implicite de COMMERCIALISABILITÉ
#  or FITNESS FOR A PARTICULAR          ni d’ADÉQUATION À UN OBJECTIF
#  PURPOSE.  See the GNU Affero         PARTICULIER. Consultez la Licence
#  General Public License for           Générale Publique GNU Affero
#  more details.                        pour plus de détails.
#
#  You should have received             Vous devriez avoir reçu une
#  a copy of the GNU Affero             copie de la Licence Générale
#  General Public License along         Publique GNU Affero avec
#  with OpenCADC.  If not, see          OpenCADC ; si ce n’est
#  <http://www.gnu.org/licenses/>.      pas le cas, consultez :
#                                       <http://www.gnu.org/licenses/>.
#
#  $Revision: 4 $
#
# ***********************************************************************
#
import glob
import logging
import traceback

from astropy.io.votable import parse_single_table

from mock import patch

from cadcdata import FileInfo
from caom2utils import data_util
from cfht2caom2 import main_app, APPLICATION, COLLECTION, CFHTName
from cfht2caom2 import ARCHIVE
from cfht2caom2 import metadata as md
from caom2pipe import manage_composable as mc

import os
import sys

THIS_DIR = os.path.dirname(os.path.realpath(__file__))
TEST_DATA_DIR = os.path.join(THIS_DIR, 'data')
SINGLE_PLANE_DIR = os.path.join(TEST_DATA_DIR, 'single_plane')
PLUGIN = os.path.join(os.path.dirname(THIS_DIR), 'main_app.py')
TEST_FILES_DIR = '/test_files'


def pytest_generate_tests(metafunc):
    obs_id_list = glob.glob(f'{SINGLE_PLANE_DIR}/*.fits.header')
    metafunc.parametrize('test_name', obs_id_list)


@patch('caom2utils.data_util.get_local_headers_from_fits')
@patch('cfht2caom2.main_app.data_util.StorageClientWrapper')
@patch('cadcutils.net.ws.WsCapabilities.get_access_url')
@patch('cfht2caom2.metadata.CFHTCache._try_to_append_to_cache')
@patch('cfht2caom2.cfht_builder.CFHTBuilder.get_instrument')
@patch('caom2utils.data_util.StorageClientWrapper')
@patch('caom2pipe.astro_composable.get_vo_table')
def test_main_app(
    vo_mock,
    client_mock,
    inst_mock,
    cache_mock,
    access_url_mock,
    second_mock,
    local_headers_mock,
    test_name,
):
    # cache_mock there so there are no cache update calls - so the tests
    # work without a network connection
    access_url_mock.return_value = 'https://localhost'
    md.filter_cache.connected = True
    inst_mock.side_effect = _identify_inst_mock
    basename = os.path.basename(test_name)
    instrument = _identify_inst_mock(None, test_name)
    cfht_name = CFHTName(file_name=basename, instrument=instrument)
    obs_path = f'{SINGLE_PLANE_DIR}/{cfht_name.obs_id}.expected.xml'
    output_file = f'{SINGLE_PLANE_DIR}/{basename}.actual.xml'

    if os.path.exists(output_file):
        os.unlink(output_file)

    local = _get_local(basename)

    client_mock.return_value.info.side_effect = _get_file_info
    second_mock.return_value.info.side_effect = _get_file_info
    vo_mock.side_effect = _vo_mock
    # during cfht2caom2 operation, want to use astropy on FITS files
    # but during testing want to use headers and built-in Python file
    # operations
    local_headers_mock.side_effect = _local_headers

    # cannot use the --not_connected parameter in this test, because the
    # svo filter numbers will be wrong, thus the Spectral WCS will be wrong
    # as well
    sys.argv = (
        f'{APPLICATION} --no_validate --local {local} --observation '
        f'{COLLECTION} {cfht_name.obs_id} -o {output_file} --plugin {PLUGIN} '
        f'--module {PLUGIN} --lineage {_get_lineage(cfht_name)} '
        f'--resource-id ivo://cadc.nrc.ca/test'
    ).split()
    print(sys.argv)
    try:
        main_app.to_caom2()
    except Exception as e:
        logging.error(traceback.format_exc())
        raise e

    compare_result = mc.compare_observations(output_file, obs_path)
    if compare_result is not None:
        raise AssertionError(compare_result)
    # assert False  # cause I want to see logging messages


def _get_file_info(file_id):
    return FileInfo(
        id=file_id,
        file_type='application/fits',
        md5sum='abc',
    )


def _get_lineage(cfht_name):
    result = mc.get_lineage(
        ARCHIVE, cfht_name.product_id, f'{cfht_name.file_name}'
    )
    return result


def _get_local(test_name):
    if '2460503' in test_name:
        result = f'{TEST_FILES_DIR}/2460503p.fits'
    else:
        result = f'{SINGLE_PLANE_DIR}/{test_name}'
    return result


def _vo_mock(url):
    try:
        x = url.split('/')
        filter_name = x[-1].replace('&VERB=0', '')
        votable = parse_single_table(
            f'{TEST_DATA_DIR}/votable/{filter_name}.xml'
        )
        return votable, None
    except Exception as e:
        logging.error(f'get_vo_table failure for url {url}')


def _identify_inst_mock(ignore_headers, uri):
    lookup = {
        md.Inst.MEGAPRIME: [
            '2452990p',
            '979412b',
            '979412o',
            '979412p',
            '1927963f',
            '1927963o',
            '1927963p',
            '675258o',
            '2003A.frpts.z.36.00',
            '02Bm05.scatter.g.36.00',
            '1257365o',
            '1257365p',
            '02AE10.bias.0.36.00',
            '11Bm04.flat.z.36.02',
            '2463796o',
            '676000',
            '1013337',
            '2463857',
            '2004B.mask',
            '19Bm03.bias',
            '718955',
            '07Bm06.flat',
            '2463854',
            '03Am02.dark',
            '1000003',
            '03Am05.fringe',
            '1265044',
        ],
        md.Inst.ESPADONS: [
            '2460606',
            '769448b',
            '1605366x',
            '881395a',
            '2238502i',
            '2554967',
            '781920',
            '945987',
            '1001063b',
            '1001836x',
            '1003681',
            '1219059',
            '1883829c',
            '2460602a',
            '760296f',
            '881162d',
            '979339',
            '2460503p',
        ],
        md.Inst.SPIROU: [
            '2401727a',
            '2401712f',
            '2401728c',
            '2401734',
            '2401710d',
            '2513728g',
            '2515996g',
            '2455409p',
            '2602045r',
        ],
        md.Inst.WIRCAM: [
            '840066',
            '1019191',
            '786586',
            '1694261',
            '787191',
            '982871',
            '1979958',
            '2281792p',
            '2157095o',
            'weight',
            '2281792',
            '1681594',
            '981337',
            'master',
            '1706150',
            '1758254',
            '2462928',
            '1151210',
            'hotpix',
            '1007126',
            'dark_003s_',
        ],
    }
    result = md.Inst.SITELLE
    for key, value in lookup.items():
        for entry in value:
            if entry in uri:
                result = key
                break
        if result is not md.Inst.SITELLE:
            break
    return result


def _local_headers(fqn):
    from urllib.parse import urlparse
    from astropy.io import fits
    file_uri = urlparse(fqn)
    try:
        fits_header = open(file_uri.path).read()
        headers = data_util.make_headers_from_string(fits_header)
    except UnicodeDecodeError:
        hdulist = fits.open(fqn, memmap=True, lazy_load_hdus=True)
        hdulist.verify('fix')
        hdulist.close()
        headers = [h.header for h in hdulist]
    return headers
