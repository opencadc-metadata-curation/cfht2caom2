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
from cfht2caom2 import CFHTName


def test_is_valid():
    assert CFHTName(file_name='anything', instrument='SITELLE').is_valid()
    test_subject = CFHTName(
        file_name='2463796o.fits.fz', instrument='MegaCam', scheme='ad'
    )
    assert test_subject.obs_id == '2463796', 'wrong obs id'
    assert test_subject.file_id == '2463796o', 'wrong file id'
    assert test_subject.file_uri == 'ad:CFHT/2463796o.fits.fz', 'wrong uri'
    assert test_subject.source_names == [], 'not local'
    assert test_subject.is_simple, 'should be simple'

    test_subject = CFHTName(
        file_name='1944968p.fits.fz', instrument='SITELLE', scheme='cadc'
    )
    assert test_subject.obs_id == '1944968p', 'wrong obs id'
    assert test_subject.file_id == '1944968p', 'wrong file id'
    assert test_subject.file_uri == 'cadc:CFHT/1944968p.fits.fz', 'wrong uri'
    assert not test_subject.is_simple, 'should be composite'

    test_subject = CFHTName(
        file_name='2460503p.fits.gz', instrument='ESPaDOnS'
    )
    assert test_subject.obs_id == '2460503p', 'wrong obs id'
    assert test_subject.file_id == '2460503p', 'wrong file id'
    assert test_subject.file_uri == 'ad:CFHT/2460503p.fits.gz', 'wrong uri'
    assert not test_subject.is_simple, 'should be composite'

    test_subject = CFHTName(
        file_name='2452990p.fits.fz', instrument='MegaPrime'
    )
    assert test_subject.simple_by_suffix, 'should be simple'
    assert test_subject.obs_id == '2452990', 'wrong obs id'
    assert test_subject.file_id == '2452990p', 'wrong file id'
    assert test_subject.file_uri == 'ad:CFHT/2452990p.fits.fz', 'wrong uri'
    assert test_subject.is_simple, 'should be simple'

    test_subject = CFHTName(file_name='2384125z.hdf5', instrument='SITELLE')
    assert not test_subject.simple_by_suffix, 'should be derived'
    assert test_subject.obs_id == '2384125p', 'wrong obs id'
    assert test_subject.file_id == '2384125z', 'wrong file id'
    assert test_subject.file_uri == 'ad:CFHT/2384125z.hdf5', 'wrong uri'
    assert not test_subject.is_simple, 'should be derived'

    test_subject = CFHTName(file_name='2384125p.fits.fz', instrument='SITELLE')
    assert not test_subject.simple_by_suffix, 'should be derived'
    assert test_subject.obs_id == '2384125p', 'wrong obs id'
    assert test_subject.file_id == '2384125p', 'wrong file id'
    assert test_subject.file_uri == 'ad:CFHT/2384125p.fits.fz', 'wrong uri'
    assert not test_subject.is_simple, 'should be derived'

    test_subject = CFHTName(
        file_name='979412p.fits.fz', instrument='MegaPrime'
    )
    assert test_subject.simple_by_suffix, 'should be simple'
    assert test_subject.obs_id == '979412', 'wrong obs id'
    assert test_subject.file_id == '979412p', 'wrong file id'
    assert test_subject.file_uri == 'ad:CFHT/979412p.fits.fz', 'wrong uri'
    assert test_subject.is_simple, 'should be simple'

    test_subject = CFHTName(
        file_name='979412b.fits.fz', instrument='MegaPrime'
    )
    assert not test_subject.simple_by_suffix, 'should not be simple by suffix'
    assert test_subject.obs_id == '979412b', 'wrong obs id'
    assert test_subject.file_id == '979412b', 'wrong file id'
    assert test_subject.file_uri == 'ad:CFHT/979412b.fits.fz', 'wrong uri'
    assert test_subject.is_simple, 'should be simple'

    test_subject = CFHTName(
        file_name='2003A.frpts.z.36.00.fits.fz', instrument='MegaPrime'
    )
    assert not test_subject.simple_by_suffix, 'should not be simple by suffix'
    assert test_subject.obs_id == '2003A.frpts.z.36.00', 'wrong obs id'
    assert test_subject.file_id == '2003A.frpts.z.36.00', 'wrong file id'
    assert (
        test_subject.file_uri == 'ad:CFHT/2003A.frpts.z.36.00.fits.fz'
    ), 'wrong uri'
    assert not test_subject.is_master_cal, 'should not be master cal'
    assert not test_subject.is_simple, 'should be derived'

    test_subject = CFHTName(file_name='2455409p.fits', instrument='SPIRou')
    assert not test_subject.simple_by_suffix, 'should not be simple by suffix'
    assert test_subject.obs_id == '2455409p', 'wrong obs id'
    assert test_subject.file_id == '2455409p', 'wrong file id'
    assert test_subject.file_uri == 'ad:CFHT/2455409p.fits', 'wrong uri'
    assert not test_subject.is_master_cal, 'should not be master cal'
    assert not test_subject.is_simple, 'should be derived'

    test_subject = CFHTName(
        file_name='2238502i.fits.fz', instrument='ESPaDOnS'
    )
    assert test_subject.obs_id == '2238502', 'wrong obs id'

    test_subject = CFHTName(
        file_name='2602045r.fits.fz', instrument='SPIRou', scheme='cadc'
    )
    assert test_subject.obs_id == '2602045', 'wrong obs id'
    assert test_subject.product_id == '2602045r', 'wrong product id'
    assert (
        test_subject.file_uri == 'cadc:CFHT/2602045r.fits.fz'
    ), 'wrong file uri'
    assert (
        test_subject.thumb_uri == 'cadc:CFHT/2602045r_preview_256.jpg'
    ), 'wrong thumb uri'
    assert (
        test_subject.prev_uri == 'cadc:CFHT/2602045r_preview_1024.jpg'
    ), 'wrong preview uri'
    assert (
            test_subject.zoom_uri ==
            'cadc:CFHT/2602045r_preview_zoom_1024.jpg'
    ), 'wrong zoom uri'
