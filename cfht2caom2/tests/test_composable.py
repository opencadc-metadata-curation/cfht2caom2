# -*- coding: utf-8 -*-
# ***********************************************************************
# ******************  CANADIAN ASTRONOMY DATA CENTRE  *******************
# *************  CENTRE CANADIEN DE DONNÉES ASTRONOMIQUES  **************
#
#  (c) 2020.                            (c) 2020.
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

import os
import shutil
import warnings

from astropy.io import fits
from astropy.utils.exceptions import AstropyUserWarning
from collections import deque
from datetime import datetime
from hashlib import md5
from tempfile import TemporaryDirectory

from mock import Mock, patch

from cadcdata import FileInfo
from caom2utils import data_util
from caom2 import SimpleObservation, Algorithm, Instrument
from caom2pipe import astro_composable as ac
from caom2pipe import caom_composable as cc
from caom2pipe import data_source_composable as dsc
from caom2pipe import manage_composable as mc
from cfht2caom2 import composable, cfht_name, metadata
import test_fits2caom2_augmentation

TEST_DIR = f'{test_fits2caom2_augmentation.TEST_DATA_DIR}/composable_test'


@patch('cfht2caom2.metadata.CFHTCache._try_to_append_to_cache')
@patch('caom2pipe.astro_composable.check_fits')
@patch('caom2utils.data_util.get_local_headers_from_fits')
@patch('cadcutils.net.ws.WsCapabilities.get_access_url')
@patch('caom2pipe.client_composable.CAOM2RepoClient')
def test_run_by_builder(
    repo_mock, access_mock, util_headers_mock, fits_mock, cache_mock
):
    util_headers_mock.side_effect = ac.make_headers_from_file
    # files are valid FITS
    fits_mock.return_value = True

    test_fqn = os.path.join(TEST_DIR, 'test_files')
    if not os.path.exists(test_fqn):
        os.mkdir(test_fqn)
    try:
        access_mock.return_value = 'https://localhost'
        # should attempt to run MetaVisit
        repo_mock.return_value.read.side_effect = _mock_repo_read
        repo_mock.return_value.create.side_effect = Mock()
        getcwd_orig = os.getcwd
        os.getcwd = Mock(return_value=TEST_DIR)
        try:
            # execution
            test_result = composable._run_by_builder()
            assert test_result == 0, 'wrong result'
        finally:
            os.getcwd = getcwd_orig

        assert repo_mock.return_value.read.called, 'repo read not called'
        assert repo_mock.return_value.create.called, 'repo create not called'
    finally:
        _cleanup(TEST_DIR)


@patch('caom2utils.data_util.get_local_headers_from_fits')
@patch('cfht2caom2.metadata.CFHTCache._try_to_append_to_cache')
@patch('caom2pipe.astro_composable.check_fits')
@patch('caom2pipe.client_composable.CAOM2RepoClient')
@patch('caom2pipe.client_composable.StorageClientWrapper')
@patch('caom2pipe.client_composable.CadcTapClient')
def test_run_store(
    tap_mock, data_client_mock, repo_client_mock, check_fits_mock, cache_mock,
        headers_mock,
):
    test_dir_fqn = os.path.join(
        test_fits2caom2_augmentation.TEST_DATA_DIR, 'store_test'
    )
    getcwd_orig = os.getcwd
    get_local_orig = data_util.get_local_file_headers
    os.getcwd = Mock(return_value=test_dir_fqn)
    repo_client_mock.return_value.read.side_effect = _mock_repo_read_not_none
    data_client_mock.return_value.info.side_effect = (
        _mock_get_file_info
    )
    headers_mock.side_effect = ac.make_headers_from_file
    check_fits_mock.return_value = True
    try:
        # execution
        test_result = composable._run_by_builder()
        assert test_result == 0, 'wrong result'
    finally:
        os.getcwd = getcwd_orig
        data_util.get_local_file_headers = get_local_orig

    assert data_client_mock.return_value.put.called, 'expect a file put'
    data_client_mock.return_value.put.assert_called_with(
        test_dir_fqn, 'ad:CFHT/1000003f.fits.fz', 'default'
    ), 'wrong put_file args'


@patch('cfht2caom2.metadata.CFHTCache._try_to_append_to_cache')
@patch('caom2pipe.astro_composable.check_fits')
@patch('caom2pipe.client_composable.CAOM2RepoClient')
@patch('caom2pipe.client_composable.StorageClientWrapper')
@patch('caom2pipe.client_composable.CadcTapClient')
def test_run_store_retry(
    tap_mock, data_client_mock, repo_client_mock, check_fits_mock, cache_mock
):
    test_dir_fqn = os.path.join(
        test_fits2caom2_augmentation.TEST_DATA_DIR, 'store_retry_test'
    )
    test_failure_dir = os.path.join(
        test_fits2caom2_augmentation.TEST_DATA_DIR,
        'store_retry_test/failure',
    )
    test_success_dir = os.path.join(
        test_fits2caom2_augmentation.TEST_DATA_DIR, 'store_retry_test/success'
    )
    for ii in [test_failure_dir, test_success_dir]:
        if not os.path.exists(ii):
            os.mkdir(ii)
    test_failure_fqn = os.path.join(test_failure_dir, '1000003f.fits.fz')
    test_success_fqn = os.path.join(test_success_dir, '1000003f.fits.fz')

    try:
        getcwd_orig = os.getcwd
        get_local_orig = data_util.get_local_file_headers
        os.getcwd = Mock(return_value=test_dir_fqn)
        repo_client_mock.return_value.read.side_effect = (
            _mock_repo_read_not_none
        )
        data_client_mock.return_value.info.side_effect = (
            _mock_get_file_info
        )
        data_client_mock.return_value.put.side_effect = OSError
        data_util.get_local_headers_from_fits = Mock(
            side_effect=_mock_header_read
        )
        check_fits_mock.return_value = True
        try:
            # execution
            test_result = composable._run_by_builder()
            assert test_result == -1, 'all the puts should fail'
        finally:
            os.getcwd = getcwd_orig
            data_util.get_local_file_headers = get_local_orig

        assert data_client_mock.return_value.put.called, 'expect a file put'
        data_client_mock.return_value.put.assert_called_with(
            f'{test_dir_fqn}/new', 'ad:CFHT/1000003f.fits.fz', 'default'
        ), 'wrong put_file args'
        assert os.path.exists(test_failure_fqn), 'expect failure move'
        success_content = os.listdir(test_success_dir)
        assert len(success_content) == 0, 'should be no success files'
    finally:
        if os.path.exists(test_failure_fqn):
            test_new_fqn = os.path.join(test_dir_fqn, 'new/1000003f.fits.fz')
            shutil.move(test_failure_fqn, test_new_fqn)
        _cleanup(test_dir_fqn)


@patch('cfht2caom2.metadata.CFHTCache._try_to_append_to_cache')
@patch('caom2utils.data_util.get_local_headers_from_fits')
@patch(
    'caom2pipe.data_source_composable.ListDirTimeBoxDataSource.'
    'get_time_box_work',
    autospec=True,
)
@patch('caom2pipe.execute_composable.OrganizeExecutes.do_one')
def test_run_state(
    run_mock,
    get_work_mock,
    util_headers_mock,
    cache_mock,
):
    try:
        util_headers_mock.side_effect = ac.make_headers_from_file
        run_mock.return_value = 0
        get_work_mock.side_effect = _mock_dir_listing
        getcwd_orig = os.getcwd
        os.getcwd = Mock(return_value=TEST_DIR)

        # it's a WIRCAM file
        test_obs_id = '2281792'
        test_f_name = f'{test_obs_id}p.fits.fz'
        try:
            # execution
            test_result = composable._run_state()
            assert test_result == 0, 'mocking correct execution'
        finally:
            os.getcwd = getcwd_orig

        assert run_mock.called, 'should have been called'
        args, kwargs = run_mock.call_args
        test_storage = args[0]
        assert isinstance(test_storage, cfht_name.CFHTName), type(test_storage)
        assert (
            test_storage.obs_id == test_obs_id
        ), f'wrong obs id {test_storage.obs_id}'
        assert test_storage.file_name == test_f_name, 'wrong file name'
        assert test_storage.fname_on_disk == test_f_name, 'wrong fname on disk'
        assert test_storage.url is None, 'wrong url'
        assert test_storage.external_urls is None, 'wrong external urls'
        assert test_storage.file_uri == f'ad:CFHT/{test_f_name}', 'wrong uri'
    finally:
        _cleanup(TEST_DIR)


@patch('cfht2caom2.metadata.CFHTCache._try_to_append_to_cache')
@patch('caom2pipe.client_composable.CAOM2RepoClient')
@patch('caom2pipe.client_composable.CadcTapClient')
@patch('caom2pipe.client_composable.StorageClientWrapper')
def test_run_by_builder_hdf5_first(
    data_mock, tap_mock, repo_mock, cache_mock
):
    # create a new observation with an hdf5 file, just using scrape
    # to make sure the observation is writable to an ams service
    #
    # also make sure the SCRAPE task works, so ensure
    # there's no need for credentials, or CADC library clients

    test_obs_id = '2384125p'
    test_dir = f'{test_fits2caom2_augmentation.TEST_DATA_DIR}/hdf5_test'
    fits_fqn = f'{test_dir}/{test_obs_id}.fits.header'
    hdf5_fqn = f'{test_dir}/2384125z.hdf5'
    actual_fqn = f'{test_dir}/logs/{test_obs_id}.xml'
    expected_hdf5_only_fqn = f'{test_dir}/hdf5_only.expected.xml'

    # clean up existing observation
    if os.path.exists(actual_fqn):
        os.unlink(actual_fqn)
    if os.path.exists(fits_fqn):
        os.unlink(fits_fqn)

    # make sure expected files are present
    if not os.path.exists(hdf5_fqn):
        shutil.copy(
            f'{test_fits2caom2_augmentation.TEST_DATA_DIR}/'
            f'multi_plane/2384125z.hdf5',
            hdf5_fqn,
        )

    _common_execution(test_dir, actual_fqn, expected_hdf5_only_fqn)


@patch('cfht2caom2.metadata.CFHTCache._try_to_append_to_cache')
@patch('caom2utils.data_util.get_local_headers_from_fits')
@patch('caom2pipe.astro_composable.check_fits')
@patch('caom2pipe.client_composable.CAOM2RepoClient')
@patch('caom2pipe.client_composable.CadcTapClient')
@patch('caom2pipe.client_composable.StorageClientWrapper')
def test_run_by_builder_hdf5_added_to_existing(
    data_mock, tap_mock, repo_mock, fits_check_mock, header_mock, cache_mock
):
    try:
        warnings.simplefilter('ignore', category=AstropyUserWarning)
        fits_check_mock.return_value = True
        header_mock.side_effect = ac.make_headers_from_file

        # add to an existing observation with an hdf5 file, just using scrape
        # to make sure the observation is writable to an ams service, and the
        # 'p' metadata gets duplicated correctly

        test_obs_id = '2384125p'
        test_dir = f'{test_fits2caom2_augmentation.TEST_DATA_DIR}/hdf5_test'
        hdf5_fqn = f'{test_dir}/2384125z.hdf5'
        fits_fqn = f'{test_dir}/{test_obs_id}.fits.header'
        actual_fqn = f'{test_dir}/logs/{test_obs_id}.xml'
        expected_fqn = f'{test_dir}/all.expected.xml'
        expected_hdf5_only_fqn = f'{test_dir}/hdf5_only.expected.xml'

        # make sure expected files are present
        if not os.path.exists(actual_fqn):
            if not os.path.exists(os.path.join(test_dir, 'logs')):
                os.mkdir(os.path.join(test_dir, 'logs'))
            shutil.copy(expected_hdf5_only_fqn, actual_fqn)
        if not os.path.exists(fits_fqn):
            shutil.copy(
                f'{test_fits2caom2_augmentation.TEST_DATA_DIR}/multi_plane/'
                f'{test_obs_id}.fits.header',
                fits_fqn,
            )

        # clean up unexpected files
        if os.path.exists(hdf5_fqn):
            os.unlink(hdf5_fqn)

        _common_execution(test_dir, actual_fqn, expected_fqn)
    finally:
        _cleanup(test_dir)


@patch('cadcutils.net.ws.WsCapabilities.get_access_url')
@patch('caom2pipe.execute_composable.CaomExecute._caom2_store')
@patch('caom2pipe.execute_composable.CaomExecute._visit_meta')
@patch('caom2pipe.data_source_composable.TodoFileDataSource.get_work')
@patch('caom2pipe.client_composable.CAOM2RepoClient')
@patch('caom2pipe.client_composable.StorageClientWrapper')
def test_run_ingest(
        data_client_mock,
        repo_client_mock,
        data_source_mock,
        meta_visit_mock,
        caom2_store_mock,
        access_url_mock,
):
    access_url_mock.return_value = 'https://localhost:8080'
    temp_deque = deque()
    test_f_name = '1319558w.fits.fz'
    temp_deque.append(test_f_name)
    data_source_mock.return_value = temp_deque
    repo_client_mock.return_value.read.return_value = None
    data_client_mock.return_value.get_head.return_value = [
        {'INSTRUME': 'WIRCam'},
    ]

    data_client_mock.return_value.info.return_value = FileInfo(
        id=test_f_name,
        file_type='application/fits',
        md5sum='abcdef',
    )

    cwd = os.getcwd()
    with TemporaryDirectory() as tmp_dir_name:
        os.chdir(tmp_dir_name)
        test_config = mc.Config()
        test_config.working_directory = tmp_dir_name
        test_config.task_types = [mc.TaskType.INGEST]
        test_config.logging_level = 'INFO'
        test_config.collection = 'CFHT'
        test_config.proxy_file_name = 'cadcproxy.pem'
        test_config.proxy_fqn = f'{tmp_dir_name}/cadcproxy.pem'
        test_config.features.supports_latest_client = False
        test_config.use_local_files = False
        mc.Config.write_to_file(test_config)
        with open(test_config.proxy_fqn, 'w') as f:
            f.write('test content')
        getcwd_orig = os.getcwd
        os.getcwd = Mock(return_value=tmp_dir_name)
        try:
            test_result = composable._run_by_builder()
            assert test_result is not None, 'expect result'
            assert test_result == 0, 'expect success'
            assert repo_client_mock.return_value.read.called, 'read called'
            assert data_client_mock.return_value.info.called, 'info'
            assert (
                data_client_mock.return_value.info.call_count == 1
            ), 'wrong number of info calls'
            data_client_mock.return_value.info.assert_called_with(
                f'ad:CFHT/{test_f_name}',
            )
            assert (
                data_client_mock.return_value.get_head.called
            ), 'get_head should be called'
            assert (
                data_client_mock.return_value.get_head.call_count == 1
            ), 'wrong number of get_heads'
            data_client_mock.return_value.get_head.assert_called_with(
                f'ad:CFHT/{test_f_name}',
            )
            assert meta_visit_mock.called, '_visit_meta call'
            assert meta_visit_mock.call_count == 1, '_visit_meta call count'
            assert caom2_store_mock.called, '_caom2_store call'
            assert caom2_store_mock.call_count == 1, '_caom2_store call count'
        finally:
            os.getcwd = getcwd_orig
            os.chdir(cwd)


def _cleanup(test_dir_fqn):
    for ii in [
        f'{test_dir_fqn}/logs',
        f'{test_dir_fqn}/logs_0',
        f'{test_dir_fqn}/metrics',
        f'{test_dir_fqn}/rejected',
    ]:
        if os.path.exists(ii):
            for entry in os.scandir(ii):
                os.unlink(entry.path)
            os.rmdir(ii)


def _common_execution(test_dir, actual_fqn, expected_fqn):
    # set up mocks
    getcwd_orig = os.getcwd
    os.getcwd = Mock(return_value=test_dir)
    try:
        # execution
        test_result = composable._run_by_builder()
        assert test_result == 0, 'wrong result'
    finally:
        os.getcwd = getcwd_orig
    assert os.path.exists(actual_fqn), f'expect {actual_fqn}'
    compare_result = mc.compare_observations(actual_fqn, expected_fqn)
    if compare_result is not None:
        raise AssertionError(compare_result)


def _mock_repo_create(arg1):
    # arg1 is an Observation instance
    act_fqn = f'{TEST_DIR}/{arg1.observation_id}.xml'
    ex_fqn = f'{TEST_DIR}/{arg1.observation_id}.expected.xml'
    mc.write_obs_to_file(arg1, act_fqn)
    result = cc.compare(ex_fqn, act_fqn, arg1.observation_id)
    if result is not None:
        assert False, result
    pass


def _mock_repo_read(arg1, arg2):
    return None


def _mock_repo_read_not_none(arg1, arg2):
    return SimpleObservation(
        observation_id='TEST_OBS_ID',
        collection='TEST',
        algorithm=Algorithm(name='exposure'),
        instrument=Instrument(name=metadata.Inst.MEGAPRIME.value),
    )


def _mock_repo_update(ignore1):
    return None


def _mock_get_file_info(file_id):
    if '_prev' in file_id:
        return FileInfo(
            id=file_id,
            size=10290,
            md5sum='md5:{}'.format(md5('-37'.encode()).hexdigest()),
            file_type='image/jpeg',
            lastmod=datetime(
                year=2019, month=3, day=4, hour=19, minute=5
            ),
        )
    else:
        return FileInfo(
            id=file_id,
            size=665345,
            md5sum='md5:a347f2754ff2fd4b6209e7566637efad',
            file_type='application/fits',
            lastmod=datetime(
                year=2019, month=3, day=4, hour=19, minute=5
            ),
        )


def _mock_dir_listing(
    arg1, output_file='', data_only=True, response_format='arg4'
):
    return [
        dsc.StateRunnerMeta(
            os.path.join(
                os.path.join(TEST_DIR, 'test_files'), '2281792p.fits.fz'
            ),
            '2019-10-23T16:27:19.000',
        ),
    ]


def _mock_header_read(file_name):
    x = """SIMPLE  =                    T / 
BITPIX  =                  -32 / Bits per pixel
NAXIS   =                    2 / Number of dimensions
NAXIS1  =                 2048 /
NAXIS2  =                 2048 /
INSTRUME= 'WIRCam  '           /
END
"""
    # TODO return data_util.make_headers_from_string(x)
    delim = '\nEND'
    extensions = [e + delim for e in x.split(delim) if e.strip()]
    headers = [fits.Header.fromstring(e, sep='\n') for e in extensions]
    return headers
