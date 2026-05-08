# ***********************************************************************
# ******************  CANADIAN ASTRONOMY DATA CENTRE  *******************
# *************  CENTRE CANADIEN DE DONNÉES ASTRONOMIQUES  **************
#
#  (c) 2025.                            (c) 2025.
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
#  : 4 $
#
# ***********************************************************************
#

"""
CFHT Cardinality:

CW - 02-01-20
The CADC page describing file types:
http://www.cadc-ccda.hia-iha.nrc-cnrc.gc.ca/en/cfht/extensions.html

For Espadons, Sitelle and Spirou there are derived observations made up from
several exposures. These derived observations are given the ‘p’ ending to
distinguish them from the simple observations that are based on a single
exposure.

For WIRcam, based on the CAOM model the o and g are included as separate
artifacts of the same plane because they correspond to different groups of
raw pixels on the detector. This has caused much trouble for the need to
connect them in etransfer. For SPIRou we did some combining of file types
within a plane e.g. ‘v’ within ‘e’, and CFHT say they would prefer to keep
them separate so we should do that.


Conversation with CW/SF 02-01-19:
- SITELLE - has hdf5 files, but there is currently no way of extracting WCS
            information from them
          - there will be (eventually) a fits file for every hdf5 file
          - copy the fits wcs to the hdf5 wcs, depending on the order of
            arrival of the files
- SPIROU - no hdf5 files, but there are two file types that have binary table
           extensions that won't support cut-outs
- WIRCam - no hdf5 files
         - 'g' are cubes of guide window(s)
- 'p' files:
    - MegaCam/WIRCam - 'p' is a processed file that is an additional plane to
            a SimpleObservation
    - SITELLE - 'p' is processed + Derived - a different observation
    - SPIROU/Espadons - 'p' is polarized + Derived, a different observation
    - there are other processed files for single exposures
    - users want 'p' files

- conclusion - one plane / file, because users want to see one row / file in
  the query results

  JJK - slack - 01-04-20
  CFHT files are independent, in that, for example, a user does not require a
  'p' file to understand the content of a 'b' file. Given this independence,
  it is acceptable to map one plane / file.

  SF - slack - 02-04-20
  - MegaCam - the logic should be probably be 2 planes: p and o for science.
            - all cfht exposures are sorted by EXPNUM if i understand their
            data acquisition. b,f,d,x should be 1 plane observations.
            - my assumption is that the b,f,d,x have no reason to have a
            processed equivalent.

  Typical science with the actual data - more or less what Elixir does:
    - do something like: p = (o - <b>) / ( <f - <b> > )
    - where <x> is the average of a bunch of x frames


CFHT Energy:

slack - 08-01-20
- PD - Well, espadons is a special case because using bounds allows one to
define "tiles" and then the SODA cutout service can extract the subset of
tiles that overlap the desired region. That's the best that can be done
because it is not possible to create a CoordFunction1D to say what the
wavelength of each pixel is
- PD - Bounds provides more detail than range and enables a crude tile-based
cutout operation later. If the coverage had significant gaps (eg SCUBA or
-SCUBA2 from JCMT) then the extra detail in bounds would enable better
discovery (as the gaps would be captured in the plane metadata). In the case
of espadons I don't think the gaps are significant (iirc, espadons is an
eschelle spectrograph but I don't recall whether the discontinuity between
eschelle was a small gap or an overlap)
- PD - So: bounds provides more detail and it can in principle improve data
discovery (if gaps) and enable extraction of subsections of the spectrum via
the SODA service. Espadons was one of the use cases that justified having
bounds there
- SF - ok now that is clearer, i think we need the information that is
contained in bounds, gaps need to be captured. so keep bounds. if you decide
to remove range, then advanced users would have to dig in the info to
understand range is first and last bounds if i understand correctly.
- SF - 19-03-24 - from the Spanish VO filter service, take the CFHT/Megaprime.<filter>  , not _sdss or _fil, and
not CFHT/Megacam.

CFHT WCS:
- CW - 28-04-20
- These raw SITELLE observations have a weird data format where 2048x2048
  images from the two interferometer arms (which are images of the same single
  field) are stitched together into a single 2048x4100ish image. So there is
  no contiguous wcs describing the raw data and in any case nobody wants to
  cut out of it.

SITELLE 'v' files:
- SF - 02-07-20
- the v files are not raw, they were derived from others, and the data
  reduction pipeline - based on orbs - probably did not do proper header
  copy/paste
- so ok to assume sequence number (RUN_ID, which is not in 'v' headers)
  == observationID minus suffix

SF 22-12-20
- as a general rule, fix typos from header metadata in CAOM2 records

SF 12-04-21
- SPIRou 'r' files are 'ramp' files, and should be 'RAW' for caom2:
  https://www.cfht.hawaii.edu/Instruments/SPIRou/FileStructure.php

"""

import logging
import math
import os

from astropy import units
from astropy.io import fits
from enum import Enum
from re import match

from caom2 import Axis, Chunk, DataProductType
from caom2 import CoordAxis2D, CoordRange2D, RefCoord, SpatialWCS, Coord2D
from caom2 import TemporalWCS, CoordAxis1D, CoordFunction1D, CoordError
from caom2 import CalibrationLevel, ProductType, ObservationIntentType
from caom2 import DerivedObservation
from caom2utils.caom2blueprint import update_artifact_meta
from caom2utils.blueprints import ObsBlueprint
from caom2utils.wcs_parsers import FitsWcsParser
from caom2utils.data_util import get_local_file_headers
from caom2pipe import astro_composable as ac
from caom2pipe import caom_composable as cc
from caom2pipe import manage_composable as mc
from caom2pipe import translate_composable as tc
from cfht2caom2 import cfht_name as cn
from cfht2caom2 import metadata as md
from cfht2caom2.espadons_energy_augmentation import get_energy_resolving_power

__all__ = ['factory', 'InstrumentType']


def cfht_time_helper(ip):
    return ac.get_datetime_mjd(mc.make_datetime(ip))


class ProvenanceType(Enum):
    """The different types of header values that identify provenance
    information. Used to specify different functions for
    execution."""

    COMMENT = 'COMMENT'
    FILENAME = 'FILENAM'
    IMCMB = 'IMCMB'
    UNDEFINED = 'UNDEFINED'  # hdf5 file support


class CFHTValueRepair(mc.ValueRepairCache):

    VALUE_REPAIR = {
        'observation.type': {
            'FRPTS': 'FRINGE',
            'scatter': 'FLAT',
        },
        # SF - 22-12-20 - fix the CAOM values, leave the headers be
        'observation.target_position.coordsys': {'FKS': 'FK5'},
        # CW
        # If no or "open" filter then set filter name to
        # null
        'chunk.energy.bandpass_name': {
            'NONE': 'none',
            'Open': 'none',
        },
        # PD 17-10-22
        #
        # if I change the CUNIT to /m it passes.
        # in VOUnit (https://www.ivoa.net/documents/VOUnits/20140523/VOUnits-REC-1.0-20140523.pdf)
        # the table on A.4 (page 33) shows this is division and FITS and VOUnit agree on /m... a few lines down,
        # "sym raised to power y" differs between FITS and VOU and I tried all the syntaxes in note (9) but none
        # of them worked.... so looks like wcslib only considers "division" syntax for this unit.
        #
        # which over-rides this:
        #
        # PD 08-04-20
        # the correct way to express "inverse meter" is
        # either  m**-1 or m^-1
        #
        # we support both exponentiations but convert ^
        # to ** so I guess at that time we thought ** was
        # the more common style.
        'chunk.energy.axis.axis.cunit': {
            '1 / m': '/m',
        },
        'chunk.position.coordsys': {'FKS': 'FK5'},
        'chunk.position.equinox': {'200.0': '2000.0'},
    }

    def __init__(self):
        self._value_repair = CFHTValueRepair.VALUE_REPAIR
        self._key = None
        self._values = None
        self._logger = logging.getLogger(self.__class__.__name__)


class AuxiliaryType(cc.TelescopeMapping2):
    value_repair = CFHTValueRepair()

    def __init__(self, cfht_name, clients, reporter, observation, config):
        super().__init__(cfht_name, clients, reporter, observation, config)
        # keep because of MegaCam/MegaPrime
        self._name = cfht_name.instrument.value
        self._chunk = None
        self._part = None
        self._plane = None
        self._extension = None
        self._instrument_start_date = mc.make_datetime('1979-01-01 00:00:00')

    @property
    def chunk(self):
        return self._chunk

    @chunk.setter
    def chunk(self, value):
        self._chunk = value

    @property
    def extension(self):
        return self._extension

    @extension.setter
    def extension(self, value):
        self._extension = value

    @property
    def observation(self):
        return self._observation

    @observation.setter
    def observation(self, value):
        self._observation = value

    @property
    def part(self):
        return self._part

    @part.setter
    def part(self, value):
        self._part = value

    @property
    def plane(self):
        return self._plane

    @plane.setter
    def plane(self, value):
        self._plane = value

    def accumulate_blueprint(self, bp):
        """Configure the telescope-specific ObsBlueprint at the CAOM model
        Observation level.

        This code captures the portion of the TDM->CAOM model mapping, where
        the relationship is one or many elements of the TDM are required to set
        individual elements of the CAOM model. If the mapping cardinality is 1:1
        generally, use add_attribute. If the mapping cardinality is n:1 use
        the set method to reference a function call.
        """
        self._logger.debug('Begin accumulate_blueprint.')
        super().accumulate_blueprint(bp)
        bp.set('Observation.intent', 'get_obs_intent()')
        bp.set('Observation.metaRelease', 'get_meta_release()')
        bp.add_attribute('Observation.sequenceNumber', 'EXPNUM')
        bp.set_default('Observation.sequenceNumber', self._storage_name.sequence_number)
        bp.set('Observation.type', 'get_obs_type()')
        bp.set_default('Observation.algorithm.name', None)
        bp.set('Observation.environment.elevation', 'get_environment_elevation()')
        bp.set('Observation.environment.humidity', 'get_obs_environment_humidity()')
        # title is select title from runid_title where proposal_id = 'runid'
        # this obtained from cache.yml now
        bp.clear('Observation.proposal.id')
        bp.add_attribute('Observation.proposal.id', 'RUNID')
        bp.clear('Observation.proposal.pi')
        bp.add_attribute('Observation.proposal.pi', 'PI_NAME')
        bp.set('Observation.proposal.project', 'get_proposal_project()')
        bp.set('Observation.proposal.title', 'get_proposal_title()')
        bp.set('Observation.instrument.name', self._storage_name.instrument.value)
        bp.set('Observation.instrument.keywords', 'get_instrument_keywords()')
        bp.set('Observation.target.standard', 'get_target_standard()')
        bp.clear('Observation.target_position.coordsys')
        bp.add_attribute('Observation.target_position.coordsys', 'OBJRADEC')
        bp.clear('Observation.target_position.equinox')
        bp.add_attribute('Observation.target_position.equinox', 'OBJEQN')
        bp.add_attribute('Observation.target_position.equinox', 'OBJEQUIN')
        bp.set('Observation.target_position.point.cval1', 'get_target_position_cval1()')
        bp.set('Observation.target_position.point.cval2', 'get_target_position_cval2()')
        bp.set('Observation.telescope.name', 'CFHT 3.6m')
        x, y, z = ac.get_geocentric_location('cfht')
        bp.set('Observation.telescope.geoLocationX', x)
        bp.set('Observation.telescope.geoLocationY', y)
        bp.set('Observation.telescope.geoLocationZ', z)

        # caom2wircam.default
        # caom2wircamdetrend.default
        bp.set('Plane.dataProductType', DataProductType.IMAGE)
        calibration_level = CalibrationLevel.CALIBRATED
        if self._storage_name.simple and '_' not in self._storage_name.file_id:
            calibration_level = CalibrationLevel.RAW_STANDARD
        bp.set('Plane.calibrationLevel', calibration_level)
        bp.set('Plane.dataRelease', 'get_plane_data_release()')
        bp.set('Plane.metaRelease', 'get_meta_release()')
        bp.add_attribute('Plane.provenance.lastExecuted', 'PROCDATE')
        bp.set_default('Plane.provenance.producer', 'CFHT')
        bp.set('Plane.provenance.project', 'STANDARD PIPELINE')
        bp.clear('Plane.provenance.runID')
        bp.add_attribute('Plane.provenance.runID', 'CRUNID')
        bp.set('Plane.provenance.version', 'get_provenance_version()')

        bp.set('Artifact.productType', 'get_product_type()')
        bp.set('Artifact.releaseType', 'data')

    def get_environment_elevation(self, ext):
        elevation = mc.to_float(self._headers[ext].get('TELALT'))
        if elevation is not None and not (0.0 <= elevation <= 90.0):
            self._logger.info(
                f'Setting elevation to None for '
                f'{self._storage_name.file_name} because the value is {elevation}.'
            )
            elevation = None
        return elevation

    def get_provenance_keywords(self, ext):
        pass

    def get_provenance_name(self, ext):
        pass

    def get_provenance_project(self, ext):
        pass

    def get_provenance_reference(self, ext):
        pass

    def get_instrument_keywords(self, ext):
        inst_mode = self._headers[ext].get('INSTMODE')
        if inst_mode is not None:
            inst_mode = f'INSTMODE={inst_mode}'
        temp = self._headers[ext].get('SITSTEP')
        sit_step = None
        if temp is not None:
            sit_step = f'SITSTEP={temp}'
        temp = self._headers[ext].get('SITSTEPS')
        sit_steps = None
        if temp is not None:
            sit_steps = f'SITSTEPS={temp}'
        result = ','.join(filter(None, (inst_mode, sit_step, sit_steps)))
        if 'Unknown' in result:
            result = 'Unknown'
        return result

    def get_meta_release(self, ext):
        """Release dates can be very long in the past, so don't worry about checking that they're logical, only that
        they're a valid date."""
        # order set from:
        # caom2IngestWircam.py, l777
        # caom2IngestEspadons.py, l625
        # caom2IngestMegadetrend.py, l445
        for keyword in ['MET_DATE', 'DATE-OBS', 'DATE-OB1', 'DATE', 'REL_DATE', 'TVSTART']:
            result = self._headers[ext].get(keyword)
            if result in ['1970-00-01', '1970-00-01T0:00:00'] or result is None:
                continue
            else:
                break
        return result

    def get_obs_environment_humidity(self, ext):
        result = self._headers[ext].get('RELHUMID')
        if result is not None and result < 0.0:
            self._logger.warning(f'RELHUMID invalid value {result}.')
            result = None
        return result

    def get_obs_intent(self, ext):
        # CW
        # Determine Observation.intent = obs.intent = "science" or
        # "calibration" phot & astr std & acquisitions/align are calibration.
        # from caom2IngestWircam.py, l731
        result = ObservationIntentType.CALIBRATION
        # use the direct keyword access so specialization doesn't break the following if condition
        obs_type = self._headers[ext].get('OBSTYPE')
        if obs_type is None:
            # no 'OBSTYPE' keyword, so fits2caom2 will set the value to
            # science
            result = None
        elif obs_type == 'OBJECT':
            run_id = self._get_run_id(ext)
            if run_id is not None and len(run_id) >= 4 and run_id[3].lower() != 'q':
                result = ObservationIntentType.SCIENCE
        return result

    def get_obs_type(self, ext):
        return self._headers[ext].get('OBSTYPE')

    def get_plane_data_release(self, ext):
        """Release dates can be very long in the past, so don't worry about checking that they're logical, only that
        they're a valid date."""

        # order set from:
        # caom2IngestWircam.py, l756
        #
        # from http://www.cfht.hawaii.edu/en/science/QSO/
        #
        # "The proprietary period of QSO data extends by default to 1 year + 1
        # month starting at the end of the QSO semester. For instance, data
        # taken for the 2009B semester (August 1 - January 31) will have a
        # default release date set to 02/28/2011. The extra month is allowed
        # because of possible delays in the data reduction distribution of
        # observations carried out near the end of a semester. If an extension
        # is requested during the Phase 1 period and is approved by TAC, a new
        # date will be set for this program through the QSO system. This
        # release date for the QSO data is indicated in the fits headers by
        # the keyword REL_DATE."

        # From Chris Usher at CFHT, 28-04-26:
        # have Q and E programs always use the immediate release logic even if REL_DATE already exists
        # It is always the case that these programs should be immediate release, which means if something else ended
        # up as the REL_DATE, it was probably a mistake when the program was set up.

        run_id = self._get_run_id(ext)
        date_obs = self._headers[ext].get('DATE-OBS')
        rel_date = self._headers[ext].get('REL_DATE')

        def other_rel_dates():
            result = None
            obs_intent = self.get_obs_intent(ext)
            if obs_intent == ObservationIntentType.CALIBRATION:
                # from caom2IngestMegacamdetrend.py, l445
                result = self._headers[ext].get('DATE')
                if result is None:
                    result = self._headers[ext].get('TVSTART')
            if result is None and run_id is not None:
                self._logger.warning(f'REL_DATE not in header. Derive from RUNID {run_id}.')
                semester = mc.to_int(run_id[0:2])
                rel_year = 2000 + semester + 1
                if run_id[2] == 'A':
                    result = f'{rel_year}-08-31T00:00:00'
                else:
                    rel_year += 1
                    result = f'{rel_year}-02-28T00:00:00'
            return result

        if run_id is None:
            if rel_date is None:
                result = other_rel_dates()
            else:
                result = rel_date
        else:
            if run_id == 'SMEARING' or run_id == 'setup':
                result = self._headers[ext].get('DATE')
            elif len(run_id) >= 4 and run_id != '17BE' and(run_id[3].lower() == 'e' or run_id[3].lower() == 'q'):
                # 17BE - a well-known default value that indicates the past
                if date_obs is not None:
                    result = f'{date_obs}T00:00:00'
            else:
                if rel_date is None:
                    result = other_rel_dates()
                else:
                    result = rel_date
        return result

    def get_product_type(self, ext):
        result = ProductType.SCIENCE
        obs_type = self.get_obs_intent(ext)
        if obs_type == ObservationIntentType.CALIBRATION:
            result = ProductType.CALIBRATION
        if self._storage_name.suffix in ['g', 'm', 'w', 'y']:
            result = ProductType.CALIBRATION
        if '_diag' in self._storage_name.file_name:
            # SF 16-03-23
            # record them as catalogues,  artifact of the *p ones - same behaviour as for the preview images
            result = ProductType.AUXILIARY

        # The goal is to make all file types easily findable by archive users,
        # which means having each file type show as a row in the search
        # results. With the search results limitation, a single file must be
        # owned by a plane, as that is how it gets displayed in the search
        # results. The planes must also contain plane-level metadata for the
        # search to find. Plane-level metadata is only calculated for science
        # or calibration artifacts, so any file types that might conceivably
        # be auxiliary product types are labeled as calibration, so that
        # plane-level metadata is calculated.
        #
        # Confirm the goal is find-ability in conversation with CW, SF on
        # 27-01-20.

        return result

    def get_proposal_project(self, ext):
        result = None
        pi_name = self._headers[ext].get('PI_NAME')
        if pi_name is not None and 'CFHTLS' in pi_name:
            result = 'CFHTLS'
        else:
            run_id = self._headers[ext].get('RUNID')
            if run_id is not None:
                result = md.cache.get_program(run_id)
        return result

    def get_proposal_title(self, ext):
        result = None
        run_id = self._headers[ext].get('RUNID')
        if run_id is not None and len(run_id) >= 4:
            result = md.cache.get_title(run_id)
        return result


    def get_provenance_version(self, ext):
        result = self._headers[ext].get('IIWIVER')
        if result is None:
            result = self._headers[ext].get('ORBSVER')
            if result is None:
                result = self._headers[ext].get('EL_SYS')
        return result

    def get_target_position_cval1(self, ext):
        ra, ignore_dec = self._get_ra_dec(ext)
        return ra

    def get_target_position_cval2(self, ext):
        ignore_ra, dec = self._get_ra_dec(ext)
        return dec

    def get_target_standard(self, ext):
        obs_type = self.get_obs_type(ext)
        run_id = self._get_run_id(ext)
        result = None
        if run_id is not None and len(run_id) >= 4:
            run_id_type = run_id[3].lower()
            if run_id_type == 'q' and obs_type == 'OBJECT':
                obj_name = self._headers[ext].get('OBJECT').lower()
                if self._storage_name.instrument is md.Inst.SITELLE:
                    if 'std' in obj_name:
                        result = True
                    else:
                        result = False
                else:
                    if (
                        'flat' in obj_name
                        or 'focus' in obj_name
                        or 'zenith' in obj_name
                    ):
                        result = False
                    else:
                        result = True
            else:
                result = False
        return result

    def get_time_resolution(self, ext):
        pass

    def _get_ra_dec(self, ext):
        obj_ra = self._headers[ext].get('OBJRA')
        obj_dec = self._headers[ext].get('OBJDEC')
        obj_ra_dec = self._headers[ext].get('OBJRADEC')
        if obj_ra_dec is not None:
            obj_ra_dec = obj_ra_dec.lower()
        ra = None
        dec = None
        if (
            obj_ra is not None
            and obj_dec is not None
            and obj_ra_dec is not None
        ):
            if obj_ra_dec == 'gappt' or obj_ra_dec == 'null':
                # SF 18-12-19
                # seb 4:01 PM
                # this is a flat. i have the impression in this case you can
                # ignore the ra/dec stuff
                self._logger.warning(
                    f'OBSRADEC is GAPPT for {self._storage_name.file_name}'
                )
            else:
                ra, dec = ac.build_ra_dec_as_deg(obj_ra, obj_dec, obj_ra_dec)
        return ra, dec

    def _get_run_id(self, ext):
        run_id = self._headers[ext].get('RUNID')
        if run_id is None:
            run_id = self._headers[ext].get('CRUNID')
        if run_id is not None:
            if len(run_id) < 3 or len(run_id) > 9 or run_id == 'CFHT':
                # a well-known default value that indicates the past, as
                # specified in
                # caom2IngestMegacam.py, l392
                # caom2IngestWircamdetrend.py, l314
                # caom2IngestEspadons.py, l522
                self._logger.warning(
                    f'Setting RUNID to default 17BE for '
                    f'{self._headers[ext].get("FILENAME")}.'
                )
                run_id = '17BE'
            else:
                run_id = run_id.strip()
        return run_id

    def _get_types(self, ext):
        dp_result = DataProductType.IMAGE
        pt_result = ProductType.SCIENCE
        obs_type = self.get_obs_intent(ext)
        if obs_type == ObservationIntentType.CALIBRATION:
            pt_result = ProductType.CALIBRATION
        if self._storage_name.suffix in ['m', 'w', 'y']:
            dp_result = DataProductType.AUXILIARY
            pt_result = ProductType.AUXILIARY
        return dp_result, pt_result

    def _get_gaia_target_id(self, ext):
        catalog_id = self._headers[ext].get('GAIAID')
        # catalog id looks like:
        # GAIAID  = 'Gaia DR2 470826482635704064'
        # should look like:
        # Gaia:DRX/SOURCE_ID
        # from JJK: 25-02-21
        # PD: 01-03-21
        # should be wary of upper-case letters in schemes, so use 'gaia'
        result = None
        if catalog_id is not None:
            if isinstance(catalog_id, int):
                catalog_dr = self._headers[ext].get('GAIADR')
                bits = catalog_dr.split()
                if len(bits) == 2:
                    result = mc.build_uri(
                        scheme=bits[0].lower(),
                        archive=bits[1],
                        file_name=str(catalog_id),
                    )
                else:
                    self._logger.warning(
                        f'Unexpected GAIADR value {catalog_dr}.'
                    )
            else:
                bits = catalog_id.split()
                if len(bits) == 3:
                    result = mc.build_uri(
                        scheme=bits[0].lower(),
                        archive=bits[1],
                        file_name=bits[2],
                    )
                else:
                    self._logger.warning(
                        f'Unexpected GAIAID value {catalog_id}.'
                    )
        return result

    def _find_derived_type(self, obs_id):
        """
        Determine how to identify Provenance.inputs.
        """
        result = False
        derived_type = ProvenanceType.UNDEFINED
        if cc.is_composite(self._headers):
            result = True
            derived_type = ProvenanceType.IMCMB
        else:
            file_type = self._headers[0].get('FILETYPE')
            if file_type is not None and 'alibrat' in file_type:
                result = True
                derived_type = ProvenanceType.COMMENT
        if not result and self._storage_name.derived:
            derived_type = ProvenanceType.FILENAME
        self._logger.info(f'Using {derived_type} to look for Plane.provenance.inputs.')
        return derived_type

    def update(self):
        """Called to fill multiple CAOM model elements and/or attributes, must
        have this signature for import_module loading and execution.

        This code captures the portion of the TDM->CAOM model mapping, where
        the relationship is multiple elements of the TDM are required to set
        multiple elements of the CAOM model (mapping cardinality n:n).

        :param observation A CAOM Observation model instance.
        """
        self._logger.debug('Begin update.')

        ingesting_hdf5 = False

        if self._storage_name.suffix == 'z':
            ingesting_hdf5 = True
            self._logger.info(
                f'Ingesting the hdf5 plane for {self._observation.observation_id}'
            )

        if self._storage_name.instrument is md.Inst.MEGACAM:
            # need the 'megacam' for the filter lookup at SVO, but there is
            # only a 'MegaPrime' instrument in the CAOM collection at CADC
            # see e.g. 2003A.frpts.z.36.00
            self._observation.instrument = cc.copy_instrument(
                self._observation.instrument, md.Inst.MEGAPRIME.value
            )

        if ingesting_hdf5:
            # avoid all the code that references undefined headers variable
            if not isinstance(self._observation, DerivedObservation):
                self._observation = cc.change_to_composite(self._observation, 'scan')
            self._logger.debug('Done hdf5 update.')
            return self._observation

        if (
            self._storage_name.instrument is md.Inst.SITELLE
            and self._storage_name.suffix == 'v'
        ):
            idx = 0
        else:
            idx = self._update_observation_metadata()
        self.extension = idx
        self.update_observation()
        for plane in self._observation.planes.values():
            if plane.product_id != self._storage_name.product_id:
                # do only the work for the applicable plane
                continue

            self.plane = plane
            for artifact in plane.artifacts.values():
                if artifact.uri != self._storage_name.file_uri:
                    continue
                update_artifact_meta(artifact, self._storage_name.file_info.get(self._storage_name.file_uri))

                for part in artifact.parts.values():
                    for chunk in part.chunks:
                        if chunk.time is not None and chunk.time.axis is not None and chunk.time.axis.function is not None:
                            if plane.calibration_level == CalibrationLevel.RAW_STANDARD:
                                time_delta = self.get_time_refcoord_delta_simple(idx)
                            else:
                                time_delta = self.get_time_refcoord_delta_derived(idx)

                            cc.undo_astropy_cdfix_call(chunk, time_delta)
                        self.part = part
                        self.chunk = chunk
                        self.update_chunk()

            derived_type = self._find_derived_type(self._observation.observation_id)
            if plane.provenance is not None:
                if derived_type is ProvenanceType.IMCMB:
                    cc.update_plane_provenance(
                        plane,
                        self._headers[1:],
                        derived_type.value,
                        self._storage_name.collection,
                        _repair_imcmb_provenance_value,
                        self._observation.observation_id,
                    )
                elif derived_type is ProvenanceType.COMMENT:
                    cc.update_plane_provenance_single(
                        plane,
                        self._headers,
                        derived_type.value,
                        self._storage_name.collection,
                        _repair_comment_provenance_value,
                        self._observation.observation_id,
                    )
                else:
                    cc.update_plane_provenance(
                        plane,
                        self._headers,
                        derived_type.value,
                        self._storage_name.collection,
                        _repair_filename_provenance_value,
                        self._observation.observation_id,
                    )
                # the derived plane itself is not considered one of the inputs
                delete_these = []
                for ip in plane.provenance.inputs:
                    if ip.get_product_id().endswith(self._storage_name.product_id):
                        delete_these.append(ip)
                for entry in delete_these:
                    plane.provenance.inputs.remove(entry)

            self.update_plane()

        InstrumentType.value_repair.repair(self._observation)
        self._logger.debug('Done update.')
        return self._observation

    @staticmethod
    def _semi_deep_copy_plane(
        from_plane, to_plane, from_artifact, to_artifact
    ):
        to_plane.calibration_level = from_plane.calibration_level
        to_plane.data_product_type = from_plane.data_product_type
        to_plane.data_release = from_plane.data_release
        to_plane.meta_producer = from_plane.meta_producer
        to_plane.meta_release = from_plane.meta_release
        for part in from_artifact.parts.values():
            to_artifact.parts.add(cc.copy_part(part))
            for chunk in part.chunks:
                to_artifact.parts[part.name].chunks.append(
                    cc.copy_chunk(chunk)
                )

    def make_axes_consistent(self):
        raise NotImplementedError

    def reset_energy(self):
        pass

    def reset_position(self):
        pass

    def track_invalid_date(self, value, key):
        # want to check for and track broken metadata, so None is an acceptable date
        if value is not None:
            self._logger.warning(f'Invalid date of {value} for {key}.')
            self._observable.rejected.record(mc.Rejected.BAD_METADATA, self._storage_name.file_name)

    def update_chunk(self):
        self.update_polarization()
        self.update_time()
        self.update_position()
        self.update_energy()
        self.reset_energy()
        self.reset_position()
        self.make_axes_consistent()

    def update_energy(self):
        pass

    def update_observation(self):
        if (
            self._observation.proposal is not None
            and self._observation.proposal.pi_name is None
        ):
            self._observation.proposal.pi_name = 'CFHT'

    def update_plane(self):
        if self._observation.algorithm.name == 'scan':
            self.plane.data_product_type = DataProductType.CUBE
            if self.plane.provenance is not None:
                self.plane.provenance.last_executed = mc.make_datetime(self._headers[self._extension].get('DATE'))

    def update_polarization(self):
        pass

    def update_position(self):
        raise NotImplementedError

    def update_time(self):
        raise NotImplementedError

    def _update_observation_metadata(self):
        return self._extension if self._extension is not None else 0

    def _update_plane_provenance(self):
        self._logger.debug(
            f'Begin _update_plane_provenance for {self._storage_name.obs_id}'
        )
        _, plane_uri = cc.make_plane_uri(
            self._storage_name.obs_id, f'{self._storage_name.obs_id}o', self._storage_name.collection
        )
        self.plane.provenance.inputs.add(plane_uri)
        self._logger.debug(
            f'End _update_plane_provenance for {self._storage_name.obs_id}'
        )

    def _use_existing_observation(self, bp):
        """Use values from an existing Observation to set Observation-level blueprint values."""
        if self._observation is not None:
            # for the cases where the blueprint keys are not the same as the Python class data member names
            x = {
                'ambientTemp': 'ambient_temp',
                'geoLocationX': 'geo_location_x',
                'geoLocationY': 'geo_location_y',
                'geoLocationZ': 'geo_location_z',
                'metaProducer': 'meta_producer',
                'metaRelease': 'meta_release',
                'observationID': 'observation_id',
                'pi': 'pi_name',
                'sequenceNumber': 'sequence_number',
            }
            for attribute in bp._plan:
                if attribute.startswith('Observation'):
                    attribute_names = attribute.split('.')
                    y = x.get(attribute_names[1], attribute_names[1])
                    if hasattr(self._observation, y):
                        attribute_ptr = getattr(self._observation, y)
                        if len(attribute_names) > 2:
                            z = x.get(attribute_names[2], attribute_names[2])
                            if hasattr(attribute_ptr, z):
                                attribute_ptr = getattr(attribute_ptr, z)
                                self._logger.debug(f'Reset blueprint value to {attribute_ptr} for {attribute}')
                                bp.clear(attribute)
                                bp.set(attribute, attribute_ptr)
                        else:
                            self._logger.debug(f'Reset blueprint value to {attribute_ptr} for {attribute}')
                            bp.clear(attribute)
                            bp.set(attribute, attribute_ptr)
                    else:
                        self._logger.warning(f'Did not find {attribute} in Observation.')


class InstrumentType(AuxiliaryType):

    def accumulate_spectral_chunk_blueprint(self, bp):
        # hard-coded values from:
        # - wcaom2archive/cfh2caom2/config/caom2megacam.default and
        # - wxaom2archive/cfht2ccaom2/config/caom2megacam.config
        #
        # Gemini is all range, make CFHT range too where possible
        bp.set('Chunk.energy.axis.axis.ctype', 'get_energy_ctype()')
        bp.set('Chunk.energy.axis.axis.cunit', 'get_energy_cunit()')
        bp.set('Chunk.energy.axis.error.rnder', 1.0)
        bp.set('Chunk.energy.axis.error.syser', 1.0)
        bp.set('Chunk.energy.axis.function.delta', 'get_energy_function_delta()')
        bp.set('Chunk.energy.axis.function.naxis', 'get_energy_function_naxis()')
        bp.set('Chunk.energy.axis.function.refCoord.pix', 'get_energy_function_pix()')
        bp.set('Chunk.energy.axis.function.refCoord.val', 'get_energy_function_val()')
        bp.clear('Chunk.energy.bandpassName')
        bp.add_attribute('Chunk.energy.bandpassName', 'FILTER')
        bp.set('Chunk.energy.resolvingPower', 'get_energy_resolving_power()')
        bp.set('Chunk.energy.specsys', 'TOPOCENT')
        bp.set('Chunk.energy.ssysobs', 'TOPOCENT')
        bp.set('Chunk.energy.ssyssrc', 'TOPOCENT')

    def accumulate_spatial_chunk_blueprint(self, bp):
        bp.set('Chunk.position.axis.axis1.cunit', 'deg')
        bp.set('Chunk.position.axis.axis2.cunit', 'deg')
        bp.set('Chunk.position.axis.error1.rnder', 0.0000278)
        bp.set('Chunk.position.axis.error1.syser', 0.0000278)
        bp.set('Chunk.position.axis.error2.rnder', 0.0000278)
        bp.set('Chunk.position.axis.error2.syser', 0.0000278)
        bp.clear('Chunk.position.coordsys')
        bp.add_attribute('Chunk.position.coordsys', 'RADECSYS')

    def accumulate_time_chunk_blueprint(self, bp):
        bp.set('Chunk.time.exposure', 'get_exptime()')
        bp.set('Chunk.time.resolution', 'get_exptime()')
        bp.set('Chunk.time.timesys', 'UTC')
        bp.set('Chunk.time.axis.axis.ctype', 'TIME')
        bp.set('Chunk.time.axis.axis.cunit', 'd')
        bp.set('Chunk.time.axis.error.rnder', 0.0000001)
        bp.set('Chunk.time.axis.error.syser', 0.0000001)
        bp.set('Chunk.time.axis.function.naxis', 1)

        if self._storage_name.raw_time:
            bp.set('Chunk.time.axis.function.delta', 'get_time_refcoord_delta_simple()')
            bp.set('Chunk.time.axis.function.refCoord.val', 'get_time_refcoord_val_simple()')
        else:
            bp.set('Chunk.time.axis.function.delta', 'get_time_refcoord_delta_derived()')
            bp.set('Chunk.time.axis.function.refCoord.val', 'get_time_refcoord_val_derived()')
        bp.set('Chunk.time.axis.function.refCoord.pix', 0.5)

    def get_bandpass_name(self, ext):
        pass

    def get_dec_deg_from_0th_header(self, ext):
        return self._headers[0].get('DEC_DEG')

    def get_energy_ctype(self, ext):
        result = None
        if self._has_energy(ext):
            result = self._headers[ext].get('CTYPE3', 'WAVE')
        return result

    def get_energy_cunit(self, ext):
        result = None
        if self._has_energy(ext):
            result = self._headers[ext].get('CUNIT3', 'Angstrom')
        return result

    def get_energy_function_delta(self, ext):
        result = None
        if self._has_energy(ext):
            filter_name = mc.get_keyword(self._headers, 'FILTER')
            temp, ignore = get_filter_md(filter_name, self._storage_name)
            result = ac.FilterMetadataCache.get_fwhm(temp)
        return result

    def get_energy_function_naxis(self, ext):
        return 1.0

    def get_energy_function_pix(self, ext):
        result = None
        if self._has_energy(ext):
            result = 1.0
        return result

    def get_energy_function_val(self, ext):
        result = None
        if self._has_energy(ext):
            filter_name = mc.get_keyword(self._headers, 'FILTER')
            temp, ignore = get_filter_md(filter_name, self._storage_name)
            result = ac.FilterMetadataCache.get_central_wavelength(temp)
        return result

    def get_energy_resolving_power(self, ext):
        result = None
        if self._has_energy(ext):
            delta = self.get_energy_function_delta(ext)
            val = self.get_energy_function_val(ext)
            result = None
            if delta is not None and val is not None:
                result = val / delta
        return result

    def get_exptime(self, ext):
        exptime = mc.to_float(self._headers[ext].get('EXPTIME'))
        # units are seconds
        if exptime is None:
            if self._storage_name.raw_time:
                # caom2IngestMegacaomdetrend.py, l438
                exptime = 0.0
        return exptime

    def get_time_refcoord_delta(self, ext):
        pass

    def get_time_refcoord_val(self, ext):
        pass

    def get_polarization_function_val(self, ext):
        lookup = {'I': 1, 'Q': 2, 'U': 3, 'V': 4, 'W': 5}
        result = 6
        temp = self._headers[ext].get('CMMTSEQ')
        if temp is not None:
            result = lookup.get(temp[0], result)
        return result

    def get_position_coordsys_from_0th_header(self, ext):
        return self._headers[ext].get('RADECSYS')

    def get_position_equinox_from_0th_header(self, ext):
        return self._headers[ext].get('EQUINOX')

    def get_ra_deg_from_0th_header(self, ext):
        return self._headers[0].get('RA_DEG')

    def get_time_refcoord_delta_derived(self, ext):
        tv_stop = self._headers[ext].get('TVSTOP')
        if tv_stop is None:
            # caom2IngestMegacamdetrend.py, l429
            # caom2IngestWircamdetrend.py, l422
            exp_time = 20.0
        else:
            mjd_obs = self.get_time_refcoord_val_derived(ext)
            temp = cfht_time_helper(tv_stop)
            if ac.is_good_date(temp, self._instrument_start_date, check_end_date=True):
                mjd_end = temp.value
                exp_time = mjd_end - mjd_obs
            else:
                self.track_invalid_date(tv_stop, 'Chunk.time.axis.function.refCoord.delta')
                # use the default value, as it's an ok value if TVSTOP is not defined
                exp_time = None
        return exp_time

    def get_time_refcoord_delta_simple(self, ext):
        # caom2IngestMegacam.py
        exp_time = self.get_exptime(ext)
        if exp_time is None:
            exp_time = mc.to_float(self._headers[ext].get('DARKTIME'))
        if exp_time is not None:
            # units are days for raw retrieval values
            exp_time = exp_time / 86400.0
        return exp_time

    def get_time_refcoord_val_derived(self, ext):
        mjd_obs = None
        # CW
        # caom2IngestWircamdetrend.py, l388
        # Time - set exptime as time of one image, start and stop dates
        # as one pixel so this means crval3 is not equal to exptime
        # if TVSTART not defined, use release_date as mjdstart
        for keyword in ['TVSTART', 'REL_DATE', 'DATE']:
            temp = self._headers[ext].get(keyword)
            if temp is None:
                continue
            mjd_obs = cfht_time_helper(temp)
            if ac.is_good_date(mjd_obs, self._instrument_start_date, True):
                break
        if mjd_obs is not None:
            mjd_obs = mjd_obs.value
        return mjd_obs

    def get_time_refcoord_val_simple(self, ext):
        result = self._get_mjd_obs(ext)
        if result is None:
            # from caom2IngestMegacam.py, l549
            for ii in ['DATE-OBS', 'DATE']:
                temp = self._headers[ext].get(ii)
                if temp is None:
                    continue
                result = cfht_time_helper(temp)
                if ac.is_good_date(result, self._instrument_start_date, True):
                    break
        if result is not None:
            result = result.value
        return result

    def get_time_resolution(self, ext):
        pass

    def _get_mjd_obs(self, ext):
        result = ac.to_mjd(self._headers[ext].get('MJD-OBS'))
        if not ac.is_good_date(result, self._instrument_start_date, True):
            result = None
        return result

    def _get_mjd_start(self, ext):
        mjd_obs = None
        for index, value in enumerate([self._get_mjd_obs(ext), 'DATE-OBS', 'DATE']):
            if index == 0:
                mjd_obs = value
            else:
                temp = self._headers[ext].get(value)
                if value == 'DATE-OBS':
                    temp2 = self._headers[ext].get('TIME-OBS')
                    if temp is not None and temp2 is not None:
                        temp = f'{temp}T{temp2}'
                mjd_obs = cfht_time_helper(temp)

            if ac.is_good_date(mjd_obs, self._instrument_start_date, True):
                if hasattr(mjd_obs, 'value'):
                    mjd_obs = mjd_obs.value
                break
        return mjd_obs

    def _get_run_id(self, ext):
        run_id = self._headers[ext].get('RUNID')
        if run_id is None:
            run_id = self._headers[ext].get('CRUNID')
        if run_id is not None:
            if len(run_id) < 3 or len(run_id) > 9 or run_id == 'CFHT':
                # a well-known default value that indicates the past, as
                # specified in
                # caom2IngestMegacam.py, l392
                # caom2IngestWircamdetrend.py, l314
                # caom2IngestEspadons.py, l522
                self._logger.warning(
                    f'Setting RUNID to default 17BE for '
                    f'{self._headers[ext].get("FILENAME")}.'
                )
                run_id = '17BE'
            else:
                run_id = run_id.strip()
        return run_id

    def _get_types(self, ext):
        dp_result = DataProductType.IMAGE
        pt_result = ProductType.SCIENCE
        obs_type = self.get_obs_intent(ext)
        if obs_type == ObservationIntentType.CALIBRATION:
            pt_result = ProductType.CALIBRATION
        if self._storage_name.suffix in ['m', 'w', 'y']:
            dp_result = DataProductType.AUXILIARY
            pt_result = ProductType.AUXILIARY
        return dp_result, pt_result

    def _has_energy(self, ext):
        obs_type = self.get_obs_type(ext)
        # from conversation with CW, SF
        # also from caom2IngestEspadons.py, l393, despite an existing example
        # with energy information
        return obs_type not in ['BIAS', 'DARK']

    def _get_gaia_target_id(self, ext):
        catalog_id = self._headers[ext].get('GAIAID')
        # catalog id looks like:
        # GAIAID  = 'Gaia DR2 470826482635704064'
        # should look like:
        # Gaia:DRX/SOURCE_ID
        # from JJK: 25-02-21
        # PD: 01-03-21
        # should be wary of upper-case letters in schemes, so use 'gaia'
        result = None
        if catalog_id is not None:
            if isinstance(catalog_id, int):
                catalog_dr = self._headers[ext].get('GAIADR')
                bits = catalog_dr.split()
                if len(bits) == 2:
                    result = mc.build_uri(
                        scheme=bits[0].lower(),
                        archive=bits[1],
                        file_name=str(catalog_id),
                    )
                else:
                    self._logger.warning(
                        f'Unexpected GAIADR value {catalog_dr}.'
                    )
            else:
                bits = catalog_id.split()
                if len(bits) == 3:
                    result = mc.build_uri(
                        scheme=bits[0].lower(),
                        archive=bits[1],
                        file_name=bits[2],
                    )
                else:
                    self._logger.warning(
                        f'Unexpected GAIAID value {catalog_id}.'
                    )
        return result

    def _update_observation_metadata(self):
        """
        Why this method exists:

        There are CFHT files that have almost no metadata in the primary HDU,
        but all the needed metadata in subsequent HDUs.

        It's not possible to apply extension
        numbers for non-chunk blueprint entries, so that means that to use the
        information captured in the blueprint, the header that's provided
        must be manipulated instead. There is only access to the header
        information in this extension of the fitscaom2 module (i.e. this file)
        during the execution of the 'update' step of fits2caom2 execution.
        Hence the self-referential implementation. Maybe it will result in an
        infinite loop and I'll be sad.
        """

        # notes to myself
        # - can only set blueprint extension stuff for chunk bits
        # - need to do the extension/header replacement here for the
        #   Observation, but the chunk level blueprint has been hosed by the
        #   previous settings
        # - the correct values are set in extension 1 for the chunk
        #   and need to be accessible as extension 0 for the observation, plane,
        #   artifact
        # - so then - do I need the blueprint before it's been modified?
        #   maybe instead of storing the blueprint I just call
        #   accumulate_blueprint?

        # and I'm back trying to figure out how to undo the doing ...
        # the first time through, the CD4_4 value is set from CDELT4,
        # the second time through, it is not, because

        # more notes to myself - why does this not work within the pipeline?
        # it should???

        # check for files with primary headers that have NO information
        # - e.g. 2445848a
        self._logger.debug(
            f'Begin _update_observation_metadata for '
            f'{self._storage_name.file_name}'
        )
        idx = 0
        run_id = self._headers[0].get('RUNID')
        if run_id is None:
            run_id = self._headers[0].get('CRUNID')
            # xor
            if (
                run_id is None
                and not (
                self._storage_name.instrument is md.Inst.SPIROU
                and self._storage_name.suffix == 'g'
            )
            ) or (
                run_id is not None
                and (
                    self._storage_name.instrument is md.Inst.SPIROU
                    and self._storage_name.suffix == 'g'
                )
            ):
                if len(self._headers) > 1:
                    idx = 1

                    self._logger.warning(
                        f'Resetting the header/blueprint relationship for '
                        f'{self._storage_name.file_name} in {self._observation.observation_id}'
                    )
                    if os.path.exists(self._storage_name.source_names[0]):
                        unmodified_headers = get_local_file_headers(self._storage_name.source_names[0])
                    elif self._clients is not None and self._clients.data_client is not None:
                        unmodified_headers = self._clients.data_client.get_head(self._storage_name.file_uri)

                    bp = ObsBlueprint(instantiated_class=self)
                    self.accumulate_blueprint(bp)
                    # TODO this is not a long-term implementation
                    # re-read the headers from disk, because the first pass
                    # through caom2gen will have modified the header content
                    # based on the original blueprint the execution goes
                    # through and sets the CDELT4 value, then from that sets
                    # the CD4_4 value. Then the second time through, the CD4_4
                    # value update is expressly NOT done, because the CD4_4
                    # value is already set from the first pass-through - need
                    # to figure out a way to fix this .... sigh
                    previous_headers = self._headers
                    self._headers = unmodified_headers[1:]
                    tc.add_headers_to_obs_by_blueprint(
                        self._observation,
                        unmodified_headers[1:],
                        bp,
                        self._storage_name.file_uri,
                        self._storage_name.product_id,
                    )
                    self._headers = previous_headers
                else:
                    self._logger.debug(
                        f'Cannot reset the header/blueprint relationship for '
                        f'{self._storage_name.file_name} in {self._observation.observation_id}'
                    )

        self._logger.debug(f'End _update_observation_metadata.')
        return idx

    def update_position(self):
        pass

    def update_time(self):
        pass


class EspadonsTemporal(InstrumentType):
    """
    Energy - NAXIS1
    Observable - NAXIS2 - set in espadons_energy_augmentation.py
    Spatial - NAXIS3, NAXIS4
    Time - NAXIS5
    Polarization - NAXIS6
    """
    def __init__(self, cfht_name, clients, reporter, observation, config):
        super().__init__(cfht_name, clients, reporter, observation, config)
        # SF 18-11-22 espadons is 2004
        self._instrument_start_time = mc.make_datetime('2004-01-01 00:00:00')

    def accumulate_spatial_chunk_blueprint(self, bp):
        super().accumulate_spatial_chunk_blueprint(bp)
        # constants from caom2espadons.config
        bp.set('Chunk.position.axis.axis1.ctype', 'RA---TAN')
        bp.set('Chunk.position.axis.axis2.ctype', 'DEC--TAN')
        bp.set('Chunk.position.axis.function.dimension.naxis1', 1)
        bp.set('Chunk.position.axis.function.dimension.naxis2', 1)
        bp.set('Chunk.position.axis.function.refCoord.coord1.pix', 1.0)
        bp.clear('Chunk.position.axis.function.refCoord.coord1.val')
        bp.add_attribute('Chunk.position.axis.function.refCoord.coord1.val', 'RA_DEG')
        bp.set('Chunk.position.axis.function.refCoord.coord2.pix', 1.0)
        bp.clear('Chunk.position.axis.function.refCoord.coord2.val')
        bp.add_attribute('Chunk.position.axis.function.refCoord.coord2.val', 'DEC_DEG')
        # CW
        # Fibre size is 1.6", i.e. 0.000444 deg
        bp.set('Chunk.position.axis.function.cd11', -0.000444)
        bp.set('Chunk.position.axis.function.cd12', 0.0)
        bp.set('Chunk.position.axis.function.cd21', 0.0)
        bp.set('Chunk.position.axis.function.cd22', 0.000444)

        bp.set('Chunk.position.equinox', 'get_chunk_position_equinox()')

    def accumulate_blueprint(self, bp):
        """Configure the ESPaDOnS-specific ObsBlueprint at the CAOM model
        Observation level.
        """
        super().accumulate_blueprint(bp)

        bp.configure_time_axis(5)
        self.accumulate_time_chunk_blueprint(bp)

        bp.add_attribute('Observation.target_position.coordsys', 'RADECSYS')

        bp.set('Plane.dataProductType', DataProductType.SPECTRUM)
        bp.set('Plane.provenance.keywords', 'get_provenance_keywords()')
        bp.set('Plane.provenance.lastExecuted', 'get_provenance_last_executed()')
        bp.set('Plane.provenance.name', 'get_provenance_name()')
        bp.set('Plane.provenance.project', 'get_provenance_project()')
        bp.set('Plane.provenance.reference', 'get_provenance_reference()')
        bp.set('Plane.provenance.version', 'get_provenance_version()')

        bp.set('Chunk.time.axis.function.delta', 'get_time_refcoord_delta()')
        bp.set('Chunk.time.axis.function.refCoord.val', 'get_time_refcoord_val()')

        self._logger.debug('Done accumulate_blueprint.')

    def get_chunk_position_equinox(self, ext):
        equinox = self._headers[ext].get('EQUINOX')
        if equinox:
            if equinox == 200.0:
                # SF - 22-12-20 - fix the CAOM values, leave the headers be
                equinox = 2000.0
        if equinox == 0.0:
            equinox = None
        return equinox

    def get_energy_resolving_power(self, ext):
        return get_energy_resolving_power(self._headers[ext])

    def get_exptime(self, ext):
        exptime = mc.to_float(self._headers[ext].get('EXPTIME'))
        if self._storage_name.suffix == 'p':
            # caom2IngestEspadons.py, l406
            exptime = 0.0
            polar_seq = mc.to_int(self._headers[ext].get('POLARSEQ'))
            for ii in range(1, polar_seq + 1):
                exptime += mc.to_float(self._headers[ext].get(f'EXPTIME{ii}'))
        # units are seconds
        if exptime is None:
            if self._storage_name.raw_time:
                # caom2IngestMegacaomdetrend.py, l438
                exptime = 0.0
        return exptime

    def get_obs_intent(self, ext):
        result = super().get_obs_intent(ext)
        obs_type = self.get_obs_type(ext)
        if obs_type in ['BIAS', 'FLAT']:
            result = ObservationIntentType.CALIBRATION
        return result

    def get_obs_type(self, ext):
        obs_type = mc.get_keyword(self._headers, 'OBSTYPE')
        obj = mc.get_keyword(self._headers, 'OBJECT')
        if 'flat' in obj.lower():
            obs_type = 'FLAT'
        return obs_type

    def get_provenance_keywords(self, ext):
        result = None
        if self._storage_name.suffix in ['i', 'p']:
            temp = self._headers[ext].get('REDUCTIO')
            if temp is not None:
                result = f'reduction={temp}'
        return result

    def get_provenance_last_executed(self, ext):
        result = None
        comments = self._headers[ext].get('COMMENT')
        if comments is not None:
            for comment in comments:
                if 'Upena processing date:' in comment:
                    result = comment.split('Upena processing date: ')[1]
                    result = mc.make_datetime(result)
                    break
                elif 'opera-' in comment:
                    result = comment.split('opera-')[1].split(' build date')[
                        0
                    ]
                    break
        return result

    def get_provenance_name(self, ext):
        result = 'TCS'  # ESPaDOnS
        comments = self._headers[ext].get('COMMENT')
        if comments is not None:
            for comment in comments:
                if 'Upena' in comment:
                    result = 'UPENA'
                    break
                elif 'opera-' in comment:
                    result = 'OPERA'
                    break
        return result

    def get_provenance_project(self, ext):
        result = 'STANDARD PIPELINE'
        if self.get_provenance_name(ext) == 'TCS':
            result = None
        return result

    def get_provenance_reference(self, ext):
        result = (
            'http://www.cfht.hawaii.edu/Instruments/Spectroscopy/Espadons/'
        )
        temp = self.get_provenance_name(ext)
        if temp == 'UPENA':
            result = 'http://www.cfht.hawaii.edu/Instruments/Upena/'
        return result

    def get_provenance_version(self, ext):
        result = None
        comments = self._headers[ext].get('COMMENT')
        if comments is not None:
            for comment in comments:
                if 'Upena version' in comment:
                    result = comment.split('Upena version')[1]
                    break
                elif 'opera-' in comment and 'build date' in comment:
                    result = comment.split(' build date')[0]
                    break
        return result

    def get_target_position_cval1(self, ext):
        ra = super().get_target_position_cval1(ext)
        if ra is None:
            ra = self._headers[ext].get('RA_DEG')
        return ra

    def get_target_position_cval2(self, ext):
        dec = super().get_target_position_cval2(ext)
        if dec is None:
            dec = self._headers[ext].get('DEC_DEG')
        return dec

    def get_time_refcoord_delta(self, ext):
        exptime = self.get_exptime(ext)
        return exptime / 86400.0  # units are d

    def get_time_refcoord_val(self, ext):
        """
        SF 18-11-22
        DATE-OBS is wrong, but the DATE is ok in the fits headers. so the chain rules of date check in the
        instrument.py could be added with something like
            && result_date > commissioning_date_of_instrument && result_date < today
        espadons is 2004.

        :param ext:
        :return:
        """
        mjd_obs = None
        if self._storage_name.suffix == 'p':
            mjd_start1 = self._headers[ext].get('MJDSTART1')
            mjd_date1 = self._headers[ext].get('MJDATE1')
            if mjd_start1 is not None or mjd_date1 is not None:
                # caom2IngestEspadons.py, l406
                if mjd_start1 is not None:
                    temp = mjd_start1
                else:
                    temp = mjd_date1
                mjd_obs = ac.to_mjd(temp)
        else:
            for index, value in enumerate([self._get_mjd_obs(ext), 'DATE-OBS', 'HSTTIME', 'DATE']):
                if index == 0:
                    mjd_obs = value
                else:
                    temp = self._headers[ext].get(value)
                    if value == 'DATE-OBS':
                        temp2 = self._headers[ext].get('TIME-OBS')
                        if temp is not None and temp2 is not None:
                            temp = f'{temp}T{temp2}'
                    if temp in ['1970-00-01', '1970-00-01T0:00:00', '1970-00-01T0:00:00.000']:
                        continue
                    mjd_obs = cfht_time_helper(temp)
                if ac.is_good_date(mjd_obs, self._instrument_start_date, True):
                    break
        if mjd_obs is None:
            self.track_invalid_date(None, 'Chunk.time.axis.function.refCoord.val')
        else:
            if hasattr(mjd_obs, 'value'):
                mjd_obs = mjd_obs.value
        return mjd_obs

    def make_axes_consistent(self):
        self._logger.debug('Begin make_axes_consistent')
        # the energyAxis set to None is here because the metadata-only ingest needs to pass the server-side
        # naxis + *Axis value checks
        #
        # this information will be temporarily mis-leading in the database, but the
        # espadons_energy_augmentation makes it correct and consistent
        self._chunk.naxis = None
        if self._chunk.energy is not None:
            self._chunk.energy_axis = None
        if self._chunk.time is not None:
            self._chunk.time_axis = None
        if self._chunk.polarization is not None:
            self._chunk.polarization_axis = None
        self._logger.debug('End make_axes_consistent')

    def reset_position(self):
        self._logger.debug('Begin reset_position')
        if self._chunk.position is not None:
            # conform to stricter WCS validation
            self._chunk.position_axis_1 = None
            self._chunk.position_axis_2 = None
            # CW - Ignore position wcs if missing spatial indicator keywords
            radecsys = self._headers[self._extension].get('RADECSYS')
            if not (
                (radecsys is None or radecsys.lower() != 'null')
                and self._headers[self._extension].get('RA_DEG') is not None
                and self._headers[self._extension].get('DEC_DEG') is not None
            ):
                cc.reset_position(self._chunk)
        self._logger.debug('End reset_position')

    def update_plane(self):
        super().update_plane()
        # caom2IngestEspadons.py, l714
        if self._storage_name.suffix == 'i':
            self._update_plane_provenance()
        self._logger.debug('End update_plane')


class EspadonsSpectralTemporal(EspadonsTemporal):
    def accumulate_blueprint(self, bp):
        super().accumulate_blueprint(bp)
        if self._storage_name.suffix is not None:
            bp.configure_energy_axis(1)
            # caom2IngestEspadons.py l636
            naxis1 = 213542
            # caom2IngestEspadons.py l639
            cdelt1 = 0.0031764
            # caom2IngestEspadons.py l638
            crval1 = 370.0
            if self._storage_name.suffix in ['a', 'c', 'f', 'o', 'x']:
                # bp.configure_energy_axis(4)
                bp.set('Chunk.energy.axis.axis.ctype', 'WAVE')
                bp.set('Chunk.energy.axis.axis.cunit', 'nm')
                bp.set('Chunk.energy.axis.range.start.pix', 0.5)
                bp.set('Chunk.energy.axis.range.start.val', crval1)
                bp.set('Chunk.energy.axis.range.end.pix', 1.5)
                bp.set('Chunk.energy.axis.range.end.val', crval1 + float(naxis1) * cdelt1)
                bp.set('Chunk.energy.specsys', 'TOPOCENT')
                bp.set('Chunk.energy.ssyssrc', 'TOPOCENT')
                bp.set('Chunk.energy.resolvingPower', 'get_energy_resolving_power()')
                bp.set('Chunk.energy.bandpassName', None)
            else:
                self.accumulate_spectral_chunk_blueprint(bp)
                bp.set('Chunk.energy.axis.function.delta', cdelt1)
                bp.set('Chunk.energy.axis.function.naxis', naxis1)
                bp.set('Chunk.energy.axis.function.refCoord.pix', 0.5)
                bp.set('Chunk.energy.axis.function.refCoord.val', crval1)

        self._logger.debug('Done accumulate_blueprint.')


class EspadonsSpatialSpectralTemporal(EspadonsSpectralTemporal):
    def accumulate_blueprint(self, bp):
        super().accumulate_blueprint(bp)
        bp.configure_position_axes((3, 4))
        self.accumulate_spatial_chunk_blueprint(bp)
        self._logger.debug('Done accumulate_blueprint.')


class EspadonsI(EspadonsTemporal):
    """
    There is no energy axis configuration in this class because chunk.energy is filled in by the
    espadons_energy_augmentation class. The augmentation requires access to the data on disk.
    """
    def accumulate_blueprint(self, bp):
        super().accumulate_blueprint(bp)
        bp.configure_position_axes((3, 4))
        self.accumulate_spatial_chunk_blueprint(bp)
        self._logger.debug('Done accumulate_blueprint.')


class EspadonsPolarization(EspadonsTemporal):
    """
    There is no energy axis configuration in this class because chunk.energy is filled in by the
    espadons_energy_augmentation class. The augmentation requires access to the data on disk.

    This file type is the reason the model supports multiple chunks in one part. There is one array with an energy
    dimension and then the other dimension are actually different quantities, so different things stored in
    different slices of the array, hence different chunks that are subsets of the array.
    """
    def accumulate_blueprint(self, bp):
        super().accumulate_blueprint(bp)
        bp.configure_position_axes((3, 4))
        self.accumulate_spatial_chunk_blueprint(bp)

        bp.configure_polarization_axis(6)
        # caom2IngestEspadons.py, l209
        bp.set('Chunk.polarization.axis.axis.ctype', 'STOKES')
        bp.set('Chunk.polarization.axis.function.delta', 1)
        bp.set('Chunk.polarization.axis.function.naxis', 1)
        bp.set('Chunk.polarization.axis.function.refCoord.pix', 1)
        bp.set('Chunk.polarization.axis.function.refCoord.val', 'get_polarization_function_val()')
        self._logger.debug('Done accumulate_blueprint.')


class MegaTemporal(InstrumentType):
    def __init__(self, cfht_name, clients, reporter, observation, config):
        super().__init__(cfht_name, clients, reporter, observation, config)
        # https://www.cfht.hawaii.edu/Instruments/Imaging/MegaPrime/ says 2008
        # but existing metadata has a minimum value of 2001-01-25 00:00:00 for 10Bm02.flat.z.36.01.fits
        self._instrument_start_date = mc.make_datetime('2001-01-24 00:00:00')

    @property
    def extension(self):
        return self._extension

    @extension.setter
    def extension(self, value):
        self._extension = value

    def accumulate_blueprint(self, bp):
        """Configure the MegaCam/MegaPrime-specific ObsBlueprint at the CAOM model
        Observation level.
        """
        super().accumulate_blueprint(bp)

        bp.configure_time_axis(3)
        self.accumulate_time_chunk_blueprint(bp)

        bp.add_attribute('Plane.provenance.lastExecuted', 'DATEPROC')
        bp.set_default('Plane.provenance.name', 'ELIXIR')
        bp.set_default('Plane.provenance.reference', 'http://www.cfht.hawaii.edu/Instruments/Elixir/')
        self._logger.debug('Done accumulate_blueprint.')

    def _find_derived_type(self, obs_id):
        if self._storage_name.suffix == 'p' and '_flag' not in self._storage_name.file_name:
            # 'p' files are processed and do have IMCMB inputs, but they are additional planes on Observations
            derived_type = ProvenanceType.FILENAME
        else:
            derived_type = super()._find_derived_type(obs_id)
        return derived_type

    def get_obs_type(self, ext):
        result = self._headers[ext].get('OBSTYPE')
        # SF 16-03-23
        # the flags ones are similar as 2003A.mask.0.36.02  of object type mask.
        if '_flag' in self._storage_name.file_id:
            result = 'MASK'
        return result

    def make_axes_consistent(self):
        # PD - in general, do not assign, unless the wcs
        # metadata is in the FITS header
        if self._chunk.time_axis is not None:
            self._chunk.time_axis = None
        if (
            self._chunk is not None
            and self._chunk.naxis is not None
            and self._chunk.naxis == 2
            and self._chunk.time is not None
            and self._chunk.position is None
            and self._chunk.polarization is None
        ):
            self._chunk.naxis = None

    def reset_position(self):
        # CW
        # Ignore position wcs if a calibration file (except 'x'
        # type calibration) and/or position info not in header
        # or binned 8x8
        ccdbin = self._headers[self._extension].get('CCDBIN1')
        radecsys = self._headers[self._extension].get('RADECSYS')
        ctype1 = self._headers[self._extension].get('CTYPE1')
        if (ccdbin is not None and ccdbin == 8) or radecsys is None or ctype1 is None:
            cc.reset_position(self._chunk)
            self._chunk.naxis = None

    def update_plane(self):
        super().update_plane()
        # caom2IngestMegacam.py, l142
        if self._storage_name.suffix == 'p' and '_flag' not in self._storage_name.file_id:
            self._update_plane_provenance()


class MegaSpectralRangeTemporal(MegaTemporal):

    def update_energy(self):
        # SGo - use range for energy with filter information
        filter_name = mc.get_keyword(self._headers, 'FILTER')
        filter_md, updated_filter_name = get_filter_md(filter_name, self._storage_name)
        cc.build_chunk_energy_range(self._chunk, updated_filter_name, filter_md)
        if self._chunk.energy is not None:
            self._chunk.energy.ssysobs = 'TOPOCENT'
            self._chunk.energy.ssyssrc = 'TOPOCENT'
            # values from caom2megacam.default, caom2megacamdetrend.default
            self._chunk.energy.axis.error = CoordError(1.0, 1.0)


class Mega(MegaSpectralRangeTemporal):
    def __init__(self, cfht_name, clients, reporter, observation, config):
        super().__init__(cfht_name, clients, reporter, observation, config)
        self._filter_name = None

    def accumulate_blueprint(self, bp):
        """Configure the MegaCam/MegaPrime-specific ObsBlueprint at the CAOM model
        Observation level.
        """
        super().accumulate_blueprint(bp)
        bp.configure_position_axes((1, 2))
        self.accumulate_spatial_chunk_blueprint(bp)

        bp.configure_observable_axis(6)

        self._logger.debug('Done accumulate_blueprint.')


class MegaFlag(MegaTemporal):
    """
    Use this class when adding an Artifact for a '*p_flag.fits' file to an existing Observation instance.
    """
    def accumulate_blueprint(self, bp):
        """Configure the MegaCam/MegaPrime-specific ObsBlueprint at the CAOM model
        Observation level.
        """
        super().accumulate_blueprint(bp)
        bp.set('Chunk.energy.axis.function.naxis', 1)
        self._use_existing_observation(bp)
        self._logger.debug('Done accumulate_blueprint.')


class SitelleTemporal(InstrumentType):
    def __init__(self, cfht_name, clients, reporter, observation, config):
        super().__init__(cfht_name, clients, reporter, observation, config)
        # https://www.cfht.hawaii.edu/Instruments/Sitelle/ says 2015-07-15 00:00:00.000
        # but existing metadata has a minimum value of 2015-07-08 05:27:09.146880 for 1819176o.fits
        self._instrument_start_date = mc.make_datetime('2015-07-07 00:00:00.000')

    def _find_derived_type(self, obs_id):
        if self._storage_name.suffix == 'z':
            derived_type = ProvenanceType.UNDEFINED
        else:
            derived_type = super()._find_derived_type(obs_id)
        return derived_type

    def accumulate_blueprint(self, bp):
        """Configure the Sitelle-specific ObsBlueprint at the CAOM model
        Observation level.
        """
        super().accumulate_blueprint(bp)

        bp.configure_time_axis(4)
        self.accumulate_time_chunk_blueprint(bp)

        data_product_type = DataProductType.IMAGE
        if self._storage_name.derived:
            data_product_type = DataProductType.CUBE
        bp.set('Plane.dataProductType', data_product_type)

        if self._storage_name.suffix == 'v':
            bp.set('Observation.intent', ObservationIntentType.SCIENCE)
            bp.set(
                'Observation.sequenceNumber',
                self._storage_name.product_id[:-1],
            )
            bp.clear('Plane.provenance.version')
            bp.add_attribute('Plane.provenance.version', 'PROGRAM')
            bp.set('Artifact.productType', ProductType.SCIENCE)

        if self._storage_name.suffix == 'z':
            bp.set('Artifact.productType', ProductType.SCIENCE)

        bp.add_attribute('Plane.provenance.lastExecuted', 'DATE')
        bp.set_default('Plane.provenance.name', 'ORBS')
        bp.set_default(
            'Plane.provenance.reference', 'http://ascl.net/1409.007'
        )

        bp.set('Chunk.time.axis.function.delta', 'get_time_refcoord_delta()')
        bp.set('Chunk.time.axis.function.refCoord.val', '_get_mjd_start()')

        self._logger.debug('End accumulate_blueprint.')

    def get_plane_data_release(self, ext):
        """Release dates can be very long in the past, so don't worry about checking that they're logical, only that
        they're a valid date."""
        if self._storage_name.suffix == 'v':
            # REL_DATE not in header, RUN_ID not in header, derive from
            # DATE-OBS
            result = None
            rel_date = self._headers[ext].get(
                'REL_DATE', self._headers[ext].get('DATE-OBS')
            )
            if rel_date:
                temp = ac.get_datetime_mjd(rel_date) + 1 * units.year
                temp.format = 'isot'
                result = temp.value
        else:
            result = super().get_plane_data_release(ext)
        return result

    def get_time_refcoord_delta(self, ext):
        delta = None
        exp_time = mc.to_float(self._headers[ext].get('EXPTIME'))
        if exp_time is None:
            exp_time = mc.to_float(self._headers[ext].get('DARKTIME'))
        if exp_time is not None:
            delta = exp_time / 86400.0
        return delta

    def make_axes_consistent(self):
        self._chunk.time_axis = None
        if (
            self._storage_name.suffix in ['a', 'o', 'x']
            and self._chunk.position is None
            and self._chunk.naxis is not None
            and self._chunk.naxis == 3
            and self._chunk.energy is not None
        ):
            self._chunk.energy_axis = 3

        # because SITELLE has the information from two
        # detectors amalgamated into one set of HDUs
        if self._chunk.naxis is not None and self._chunk.naxis <= 2:
            if self._chunk.position_axis_1 is None:
                self._chunk.naxis = None
            self._chunk.energy_axis = None
        else:
            self._chunk.energy_axis = 3

    def reset_energy(self):
        if self._chunk.energy_axis is not None:
            self._chunk.energy_axis = 3
        if (
            self._chunk.energy is not None
            and self._chunk.energy.axis is not None
            and self.chunk.energy.axis.function is not None
            and self.chunk.energy.axis.function.ref_coord.val == 0.0
            and self.chunk.energy.axis.function.ref_coord.pix == 0.5
            and self._chunk.energy.axis.function.naxis == 1
            and self._chunk.energy.axis.function.delta == 1e-10
        ):
            # stop 2270550c.fits from showing up as being in the Gamma Ray
            # energy band
            self._logger.warning(
                f'Setting energy to None for {self._storage_name.file_name} '
                f'because the presence of all the default values indicates '
                f'mis-leading metadata.'
            )
            cc.reset_energy(self._chunk)


class SitelleSpectralTemporal(SitelleTemporal):

    def _update_sitelle_plane(self):
        """for the SITELLE HDF5 files that do not have sufficient metadata in the hdf5 file to generate a stand-alone
        Plane record, if the 'p' plane already exists in the CAOM record, copy the 'p' Plane metadata to the 'z'
        plane"""
        self._logger.debug(f'Begin _update_sitelle_plane for {self._observation.observation_id}')
        if self._storage_name.suffix not in ['p', 'z']:
            return

        # create the identifiers to find the plane to copy from 'p', and the plane to copy to 'z'
        # handle the case where the current file being ingested is a 'p' file being added to an Observation with a
        # pre-existing 'z' plane, and the case where the current file being ingested is a 'z' file being added to
        # an Observation with a pre-existing 'p' plane.
        z_plane_key = self._storage_name.product_id.replace('p', 'z')
        p_plane_key = self._storage_name.product_id.replace('z', 'p')
        o_plane_key = self._storage_name.product_id.replace('z', 'o')
        temp_z_uri = self._storage_name.file_uri.replace('p', 'z', 1)
        z_artifact_key = f'{cn.CFHTName.remove_extensions(temp_z_uri)}.hdf5'

        # fix the plane-level information for the z plane
        z_plane = self._observation.planes.get(z_plane_key)
        if z_plane:
            if z_artifact_key in z_plane.artifacts.keys():
                if len(z_plane.artifacts[z_artifact_key].parts) != 0:
                    # skip for the 'z' artifacts where hdf5 file has sufficient metadata to describe its own WCS
                    return
                z_plane.data_product_type = DataProductType.CUBE
                z_plane.calibration_level = CalibrationLevel.CALIBRATED
                z_plane.meta_producer = mc.get_version('cfht2caom2')
                self._observation.meta_producer = z_plane.meta_producer
                z_plane.artifacts[z_artifact_key].meta_producer = z_plane.meta_producer
                p_plane = self._observation.planes.get(p_plane_key)
                if p_plane:
                    # replicate the plane-level information from the p plane to the z plane
                    temp = self._storage_name.file_uri.replace('.hdf5', '.fits.fz')
                    temp = temp.replace('z', 'p', 1)
                    if temp not in p_plane.artifacts.keys():
                        temp = self._storage_name.file_uri.replace('.hdf5', '.fits')
                    p_artifact_key = temp

                    self._logger.debug(f'Looking for artifact key: {p_artifact_key}.')
                    if p_artifact_key not in p_plane.artifacts.keys():
                        p_artifact_key = self._storage_name.file_uri.replace('z', 'p', 1).replace('.hdf5', '.fits')
                        if p_artifact_key not in p_plane.artifacts.keys():
                            p_artifact_key = (
                                self._storage_name.file_uri.replace('z', 'p', 1).replace('.hdf5', '.fits.header')
                            )
                            if p_artifact_key not in p_plane.artifacts.keys():
                                raise mc.CadcException(
                                    f'Unexpected extension name pattern for artifact URI {p_artifact_key} in '
                                    f'{self._observation.observation_id}.'
                                )
                    for part in p_plane.artifacts[p_artifact_key].parts.values():
                        z_plane.artifacts[z_artifact_key].parts.add(cc.copy_part(part))
                        for chunk in part.chunks:
                            z_plane.artifacts[z_artifact_key].parts[part.name].chunks.append(cc.copy_chunk(chunk))
                    z_plane.artifacts[z_artifact_key].meta_producer = p_plane.artifacts[p_artifact_key].meta_producer
                    z_plane.provenance = p_plane.provenance
                    z_plane.calibration_level = p_plane.calibration_level
                    z_plane.data_product_type = p_plane.data_product_type
                    z_plane.data_release = p_plane.data_release
                    z_plane.meta_producer = p_plane.meta_producer
                    z_plane.meta_release = p_plane.meta_release
                elif o_plane_key in self._observation.planes.keys():
                    self._logger.info(f'Copying release metadata from {o_plane_key}.')
                    o_plane = self._observation.planes[o_plane_key]
                    z_plane.data_release = o_plane.data_release
                    z_plane.meta_release = o_plane.meta_release

        self._logger.debug('End _update_sitelle_plane')

    def accumulate_blueprint(self, bp):
        """Configure the Sitelle-specific ObsBlueprint at the CAOM model
        Observation level.
        """
        super().accumulate_blueprint(bp)

        bp.configure_energy_axis(3)
        self.accumulate_spectral_chunk_blueprint(bp)

        bp.set('Chunk.energy.axis.function.naxis', 1.0)
        self._logger.debug('End accumulate_blueprint.')

    def get_energy_function_delta(self, ext):
        result = None
        if self._has_energy(ext):
            # units in file are nm, units in blueprint are Angstroms
            filter_bw = mc.to_float(self._headers[ext].get('FILTERBW'))
            if filter_bw is not None:
                result = 10.0 * filter_bw
        return result

    def get_energy_function_pix(self, ext):
        result = None
        if self._has_energy(ext):
            result = 0.5
        return result

    def get_energy_function_val(self, ext):
        result = None
        if self._has_energy(ext):
            # units in file are nm, units in blueprint are Angstroms
            filter_lb = mc.to_float(self._headers[ext].get('FILTERLB'))
            if filter_lb is not None:
                result = 10.0 * filter_lb
        return result

    def get_energy_resolving_power(self, ext):
        result = None
        if self._has_energy(ext):
            # from caom2IngestSitelle.py, l555+
            sitresol = self._headers[ext].get('SITRESOL')
            if sitresol is not None and sitresol > 0.0:
                result = sitresol
            if result is None:
                result = 1.0
                if self._storage_name.suffix in ['a', 'c', 'f', 'o', 'x']:
                    # from caom2IngestSitelle.py, l596
                    crval3 = mc.to_float(self._headers[ext].get('FILTERLB'))
                    cdelt3 = mc.to_float(self._headers[ext].get('FILTERBW'))
                    if crval3 is not None and cdelt3 is not None:
                        result = crval3 / cdelt3
        return result


class SitelleSpatialRangeSpectralTemporal(SitelleSpectralTemporal):

    def update_position(self):
        if self._chunk.position is None:
            self._logger.debug(
                f'Begin _update_position for {self._storage_name.obs_id}'
            )
            # from caom2IngestSitelle.py l894
            header = self._headers[self._extension]
            obs_ra = header.get('RA_DEG')
            obs_dec = header.get('DEC_DEG')
            if obs_ra is None or obs_dec is None:
                self._logger.error(
                    f'RA_DEG {obs_ra} DEC_DEG {obs_dec} for '
                    f'{self._storage_name.obs_id} are not set.'
                )
                return

            pix_scale2 = mc.to_float(header.get('PIXSCAL2'))
            pix_scale1 = mc.to_float(header.get('PIXSCAL1'))

            if pix_scale1 is None or pix_scale2 is None:
                self._logger.error(
                    f'PIXSCAL1 {pix_scale1} or PIXSCAL2 {pix_scale2} for '
                    f'{self._storage_name.obs_id} are not set.'
                )
                return

            delta_dec = (1024.0 * pix_scale2) / 3600.0
            obs_dec_bl = obs_dec - delta_dec
            obs_dec_tr = obs_dec + delta_dec

            # obs_dec_tr == obs_dec_tl
            delta_ra_top = (1024.0 * pix_scale1) / (
                3600.0 * (math.cos(obs_dec_tr * 3.14159 / 180.0))
            )
            delta_ra_bot = (1024.0 * pix_scale1) / (
                3600.0 * (math.cos(obs_dec_bl * 3.14159 / 180.0))
            )
            obs_ra_bl = obs_ra + delta_ra_bot
            obs_ra_tr = obs_ra - delta_ra_top

            axis = CoordAxis2D(Axis('RA', 'deg'), Axis('DEC', 'deg'))
            axis.range = CoordRange2D(
                Coord2D(RefCoord(0.5, obs_ra_bl), RefCoord(0.5, obs_dec_bl)),
                Coord2D(
                    RefCoord(2048.5, obs_ra_tr), RefCoord(2048.5, obs_dec_tr)
                ),
            )
            position = SpatialWCS(axis)
            position.coordsys = 'FK5'
            position.equinox = 2000.0
            self._chunk.position = position
            self._chunk.position_axis_1 = 1
            self._chunk.position_axis_2 = 2
            self._logger.debug(
                f'End _update_position for {self._storage_name.obs_id}'
            )


class SitelleSpatialFunctionSpectralTemporal(SitelleSpectralTemporal):

    def accumulate_blueprint(self, bp):
        """Configure the Sitelle-specific ObsBlueprint at the CAOM model
        Observation level.
        """
        super().accumulate_blueprint(bp)
        bp.configure_position_axes((1, 2))
        self.accumulate_spatial_chunk_blueprint(bp)


class SitelleHdf5(InstrumentType):
    def __init__(self, cfht_name, clients, reporter, observation, config):
        super().__init__(cfht_name, clients, reporter, observation, config)
        # https://www.cfht.hawaii.edu/Instruments/Sitelle/ says 2015-07-15 00:00:00.000
        # but existing metadata has a minimum value of 2015-07-08 05:27:09.146880 for 1819176o.fits
        self._instrument_start_date = mc.make_datetime('2015-07-07 00:00:00.000')

    def accumulate_blueprint(self, bp):
        """Configure the Sitelle-specific ObsBlueprint at the CAOM model
        Observation level.
        """
        bp.configure_position_axes((1, 2))
        bp.configure_time_axis(3)
        bp.configure_energy_axis(4)

        bp.set('Observation.metaRelease', (['OBS_DATE'], None))
        # Laurie Rousseau-Nepton - 12-08-22
        # 'SCIENCE' is ok with me
        bp.set('Observation.type', 'SCIENCE')

        bp.set('Observation.algorithm.name', (['program'], 'exposure'))
        bp.set('Observation.instrument.name', self._storage_name.instrument.value)

        bp.set('Observation.proposal.id', '_get_proposal_id()')
        bp.set('Observation.proposal.project', '_get_proposal_project()')
        bp.set('Observation.proposal.title', 'get_proposal_title()')

        bp.set('Observation.target.name', (['object_name'], None))
        bp.set('Observation.target_position.coordsys', (['RADESYS'], None))
        bp.set('Observation.target_position.point.cval1', (['target_x'], None))
        bp.set('Observation.target_position.point.cval2', (['target_y'], None))

        bp.set('Plane.calibrationLevel', CalibrationLevel.CALIBRATED)
        bp.set('Plane.dataProductType', DataProductType.CUBE)
        bp.set('Plane.dataRelease', '_get_plane_data_release()')
        bp.set('Plane.metaRelease', (['OBS_DATE'], None))

        bp.set('Plane.provenance.producer', 'CFHT')
        bp.set('Plane.provenance.project', 'STANDARD PIPELINE')
        bp.set('Plane.provenance.lastExecuted', (['DATE'], None))
        bp.set('Plane.provenance.name', 'ORBS')
        bp.set('Plane.provenance.reference', 'http://ascl.net/1409.007')

        bp.set('Artifact.productType', ProductType.SCIENCE)

        # energy
        bp.set('Chunk.energy.bandpassName', (['filter_name'], None))
        bp.set('Chunk.energy.resolvingPower', '_get_energy_resolving_power()')
        bp.set('Chunk.energy.specsys', 'TOPOCENT')
        bp.set('Chunk.energy.axis.axis.ctype', 'WAVE')
        bp.set('Chunk.energy.axis.axis.cunit', 'nm')
        bp.set('Chunk.energy.axis.range.start.pix', 0.5)
        bp.set('Chunk.energy.axis.range.start.val', (['filter_nm_min'], None))
        bp.set('Chunk.energy.axis.range.end.pix', 1.5)
        bp.set('Chunk.energy.axis.range.end.val', (['filter_nm_max'], None))

        # time
        bp.set('Chunk.time.exposure', '_get_exposure()')
        bp.set('Chunk.time.resolution', (['exposure_time'], None))
        bp.set('Chunk.time.timesys', 'UTC')
        bp.set('Chunk.time.axis.axis.ctype', 'TIME')
        bp.set('Chunk.time.axis.axis.cunit', 'd')
        bp.set('Chunk.time.axis.error.syser', 0.0000001)
        bp.set('Chunk.time.axis.error.rnder', 0.0000001)
        bp.set('Chunk.time.axis.function.naxis', 1)
        bp.set('Chunk.time.axis.function.delta', (['exposure_time'], None))
        bp.set('Chunk.time.axis.function.refCoord.pix', 0.5)
        bp.set('Chunk.time.axis.function.refCoord.val', '_get_datetime()')

        self._logger.debug('End accumulate_blueprint.')

    def _get_datetime(self, ext):
        result = None
        d = self._headers[ext].get('OBS_DATE')
        t = self._headers[ext].get('OBS_TIME')
        if d is not None and t is not None:
            result = cfht_time_helper(f'{d} {t}').value
        return result

    def _get_energy_resolving_power(self, ext):
        result = None
        # Laurie Rousseau-Nepton - 11-08-22
        # Resolving Power could be given at the central wavelength of the filter.
        # The formula is R = 1/lambda[nm]* (2*(STEP[nm]*(NAXIS3-zpd_index))/1.2067
        step = self._headers[ext].get('STEP')
        zpd_index = self._headers[ext].get('zpd_index')
        naxis_3 = self._headers[ext].get('step_nb')
        filter_max = self._headers[ext].get('filter_nm_max')
        filter_min = self._headers[ext].get('filter_nm_min')
        wl = None
        if filter_max is not None and filter_min is not None:
            wl = (filter_min + filter_max) / 2
        if step is not None and zpd_index is not None and naxis_3 is not None and wl is not None:
            result = 1 / wl * 2 * (step * (naxis_3 - zpd_index)) / 1.2067
        return result

    def _get_exposure(self, ext):
        # Laurie Rousseau-Nepton - 11-08-22
        # Int. Time could be the total (multiplied by the cube spectral dimension f.attrs.get(‘NAXIS3’)
        result = None
        exposure = self._headers[ext].get('exposure_time')
        naxis_3 = self._headers[ext].get('step_nb')
        if exposure is not None and naxis_3 is not None:
            result = exposure * naxis_3
        return result

    def _get_plane_data_release(self, ext):
        # Laurie Rousseau-Nepton - 11-08-22
        # It is always one year for all program except the LP P41 which is public right away.
        result = None
        d = self._headers[ext].get('OBS_DATE')
        if d is not None:
            program = self._headers[ext].get('PROGRAM')
            temp = cfht_time_helper(d)
            if program is None or program != 'LP P41':
                temp = temp + 1 * units.year
            temp.format = 'isot'
            result = temp.value
        return result

    def _get_proposal_id(self, ext):
        result = None
        image_path = self._headers[ext].get('image_list_path_2')
        if image_path is not None:
            bits = image_path.split('/')
            if len(bits) >= 5:
                result = bits[4]
        return result

    def _get_proposal_project(self, ext):
        # Laurie Rousseau-Nepton - 11-08-22
        result = None
        image_path = self._headers[ext].get('image_list_path_2')
        if image_path is not None:
            bits = image_path.split('/')
            if len(bits) >= 6:
                result = md.cache.get_program(bits[5])
        return result

    def update(self):
        self._logger.debug('Begin update.')

        if not isinstance(self._observation, DerivedObservation):
            # Laurie Rousseau-Nepton - 12-08-22
            # It could be the attrs(‘program’)
            program = self._headers[0].get('program')
            if program is not None:
                self._observation = cc.change_to_composite(self._observation, program.split()[-1])

        idx = 0
        self.extension = idx
        for plane in self._observation.planes.values():
            if plane.product_id != self._storage_name.product_id:
                # do only the work for the applicable plane
                continue

            self.plane = plane
            for artifact in plane.artifacts.values():
                if artifact.uri != self._storage_name.file_uri:
                    continue
                update_artifact_meta(artifact, self._storage_name.file_info.get(self._storage_name.file_uri))

                for part in artifact.parts.values():
                    for chunk in part.chunks:
                        self.update_chunk_position(chunk)
                        # there are no cutouts, so these values don't make sense
                        chunk.position_axis_1 = None
                        chunk.position_axis_2 = None
                        chunk.energy_axis = None
                        chunk.time_axis = None
                        if chunk.energy is not None and chunk.energy.axis is not None:
                            # need to set the function.naxis, otherwise axis construction
                            # fails, but energy is a range, not a function
                            chunk.energy.axis.function = None
            self.update_plane()

        InstrumentType.value_repair.repair(self._observation)
        self._logger.debug('Done update.')
        return self._observation

    def update_chunk_position(self, chunk):
        self._logger.debug(
            f'Begin update_position_function for {self._storage_name.obs_id}'
        )
        if chunk.position is not None:
            header = self._headers[self._extension]
            cd1_1 = header.get('CD1_1')
            if cd1_1 is None:
                hdr = fits.Header()
                SitelleHdf5._from_pc_to_cd(header, hdr)
                for kw in ['CDELT1', 'CDELT2', 'CRPIX1', 'CRPIX2', 'CRVAL1', 'CRVAL2',
                           'CTYPE1', 'CTYPE2', 'CUNIT1', 'CUNIT2', 'NAXIS', 'NAXIS1', 'NAXIS2',
                           'OBS_DATE', 'OBS_TIME', 'EQUINOX'
                           ]:
                    hdr[kw] = header.get(kw)
                wcs_parser = FitsWcsParser(
                    hdr, self._storage_name.obs_id, self._extension
                )
                wcs_parser.augment_position(chunk)
        self._logger.debug(
            f'End update_function_position for {self._storage_name.obs_id}'
        )

    @staticmethod
    def _from_pc_to_cd(from_header, to_header):
            cd1_1 = from_header.get('CD1_1')
            # caom2IngestSitelle.py, l745
            # CW
            # Be able to handle any of the 3 wcs systems used
            if cd1_1 is None:
                pc1_1 = from_header.get('PC1_1')
                if pc1_1 is not None:
                    cdelt1 = mc.to_float(from_header.get('CDELT1'))
                    if cdelt1 is None:
                        cd1_1 = mc.to_float(from_header.get('PC1_1'))
                        cd1_2 = mc.to_float(from_header.get('PC1_2'))
                        cd2_1 = mc.to_float(from_header.get('PC2_1'))
                        cd2_2 = mc.to_float(from_header.get('PC2_2'))
                    else:
                        cdelt2 = mc.to_float(from_header.get('CDELT2'))
                        cd1_1 = cdelt1 * mc.to_float(from_header.get('PC1_1'))
                        cd1_2 = cdelt1 * mc.to_float(from_header.get('PC1_2'))
                        cd2_1 = cdelt2 * mc.to_float(from_header.get('PC2_1'))
                        cd2_2 = cdelt2 * mc.to_float(from_header.get('PC2_2'))
                    to_header['CD1_1'] = cd1_1
                    to_header['CD1_2'] = cd1_2
                    to_header['CD2_1'] = cd2_1
                    to_header['CD2_2'] = cd2_2


class SitelleNoHdf5Metadata(SitelleSpatialFunctionSpectralTemporal):

    def accumulate_blueprint(self, bp):
        """Configure the Sitelle-specific ObsBlueprint at the CAOM model
        Observation level.
        """
        # Laurie Rousseau-Nepton - 12-08-22
        # 'SCIENCE' is ok with me
        bp.set('Observation.type', 'SCIENCE')

        bp.set('Plane.calibrationLevel', CalibrationLevel.CALIBRATED)
        bp.set('Plane.dataProductType', DataProductType.CUBE)

        bp.set('Plane.provenance.producer', 'CFHT')
        bp.set('Plane.provenance.project', 'STANDARD PIPELINE')
        bp.set('Plane.provenance.name', 'ORBS')
        bp.set('Plane.provenance.reference', 'http://ascl.net/1409.007')

        if self._storage_name.suffix == 'z':
            bp.set('Artifact.productType', ProductType.SCIENCE)
        self._logger.debug('End accumulate_blueprint.')

    def update(self):
        self._logger.debug('Begin update.')


        idx = 0
        self.extension = idx
        for plane in self._observation.planes.values():
            if plane.product_id != self._storage_name.product_id:
                # do only the work for the applicable plane
                continue
            self.plane = plane
            for artifact in plane.artifacts.values():
                if artifact.uri != self._storage_name.file_uri:
                    continue
                update_artifact_meta(artifact, self._storage_name.file_info.get(self._storage_name.file_uri))

        self._update_sitelle_plane()
        self._logger.debug('Done update.')
        return self._observation


class SitelleP(SitelleSpectralTemporal):

    def accumulate_blueprint(self, bp):
        """Configure the Sitelle-specific ObsBlueprint at the CAOM model
        Observation level.
        """
        super().accumulate_blueprint(bp)
        # caom2IngestSitelle.py l590
        bp.clear('Chunk.energy.axis.axis.ctype')
        bp.add_attribute('Chunk.energy.axis.axis.ctype', 'CTYPE3')
        bp.set_default('Chunk.energy.axis.axis.ctype', 'WAVE')

        bp.clear('Chunk.energy.axis.axis.cunit')
        bp.add_attribute('Chunk.energy.axis.axis.cunit', 'CUNIT3')
        bp.set_default('Chunk.energy.axis.axis.cunit', 'Angstrom')

        bp.clear('Chunk.energy.axis.function.naxis')
        bp.add_attribute('Chunk.energy.axis.function.naxis', 'NAXIS3')
        bp.set_default('Chunk.energy.axis.function.naxis', 1.0)

        bp.clear('Chunk.energy.axis.function.delta')
        bp.add_attribute('Chunk.energy.axis.function.delta', 'CDELT3')

        bp.clear('Chunk.energy.axis.function.refCoord.pix')
        bp.add_attribute('Chunk.energy.axis.function.refCoord.pix', 'CRPIX3')
        bp.set_default('Chunk.energy.axis.function.refCoord.pix', 0.5)

        bp.clear('Chunk.energy.axis.function.refCoord.val')
        bp.add_attribute('Chunk.energy.axis.function.refCoord.val', 'CRVAL3')

        bp.set('Chunk.energy.specsys', 'TOPOCENT')
        bp.set('Chunk.energy.ssysobs', 'TOPOCENT')
        bp.set('Chunk.energy.ssyssrc', 'TOPOCENT')

        self._logger.debug('End accumulate_blueprint.')

    def get_exptime(self, ext):
        exptime = mc.to_float(self._headers[ext].get('EXPTIME'))
        num_steps = self._headers[ext].get('STEPNB', 1)
        exptime = exptime * num_steps
        return exptime

    def get_time_refcoord_delta(self, ext):
        mjd_start = self._get_mjd_start(ext)
        mjd_end = mc.to_float(self._headers[ext].get('MJDEND'))
        # caom2IngestSitelle.py, l704
        if mjd_start is not None and mjd_end is not None:
            delta = mjd_end - mjd_start
        else:
            exp_time = self._headers[ext].get('EXPTIME')
            if exp_time is None:
                delta = mjd_start
        return delta

    def update_position(self):
        self._logger.debug(f'Begin update_position for {self._storage_name.obs_id}')
        header = self._headers[self._extension]
        cd1_1 = header.get('CD1_1')
        # caom2IngestSitelle.py, l745
        # CW
        # Be able to handle any of the 3 wcs systems used
        if cd1_1 is None:
            # SitelleHdf5._from_pc_to_cd(header, header)
            pc1_1 = header.get('PC1_1')
            if pc1_1 is not None:
                cdelt1 = mc.to_float(header.get('CDELT1'))
                if cdelt1 is None:
                    cd1_1 = mc.to_float(header.get('PC1_1'))
                    cd1_2 = mc.to_float(header.get('PC1_2'))
                    cd2_1 = mc.to_float(header.get('PC2_1'))
                    cd2_2 = mc.to_float(header.get('PC2_2'))
                else:
                    cdelt2 = mc.to_float(header.get('CDELT2'))
                    cd1_1 = cdelt1 * mc.to_float(header.get('PC1_1'))
                    cd1_2 = cdelt1 * mc.to_float(header.get('PC1_2'))
                    cd2_1 = cdelt2 * mc.to_float(header.get('PC2_1'))
                    cd2_2 = cdelt2 * mc.to_float(header.get('PC2_2'))
                header['CD1_1'] = cd1_1
                header['CD1_2'] = cd1_2
                header['CD2_1'] = cd2_1
                header['CD2_2'] = cd2_2

        wcs_parser = FitsWcsParser(
            header, self._storage_name.obs_id, self._extension
        )
        if self._chunk is None:
            self._chunk = Chunk()
        wcs_parser.augment_position(self._chunk)
        if self._chunk.position is not None and self._chunk.position.axis is not None:
            self._chunk.position.axis.error1 = CoordError(0.0000278, 0.0000278)
            self._chunk.position.axis.error2 = CoordError(0.0000278, 0.0000278)
        self._logger.debug(f'End update_position for {self._storage_name.obs_id}')

    def update(self):
        self._logger.debug('Begin update.')
        super().update()
        self._update_sitelle_plane()
        self._logger.debug('Done update.')
        return self._observation


class Spirou(InstrumentType):
    def __init__(self, cfht_name, clients, reporter, observation, config):
        super().__init__(cfht_name, clients, reporter, observation, config)
        # TODO self._header = headers[extension]
        self._header = None
        # https://www.cfht.hawaii.edu/Instruments/SPIRou/SPIRou_news.php says 2019-02-13 00:00:00.000
        # but existing metadata has a minimum value of 2018-04-25 02:12:03.942720 for 2401710o.fits
        self._instrument_start_date = mc.make_datetime('2018-04-24 00:00:00')

    @property
    def extension(self):
        return self._extension

    @extension.setter
    def extension(self, value):
        self._extension = value
        self._header = self._headers[value]

    def accumulate_blueprint(self, bp):
        """Configure the SPIRou-specific ObsBlueprint at the CAOM model Observation level.

        SF 03-03-23
        Add in WCS for 's' files, and spatial WCS for 'g' files.
        """
        super().accumulate_blueprint(bp)

        bp.set('Observation.target.targetID', '_get_gaia_target_id()')
        bp.add_attribute('Observation.target_position.coordsys', 'RADECSYS')

        # caom2spirou.default
        bp.set('Plane.dataProductType', DataProductType.SPECTRUM)
        if self._storage_name.suffix == 'r':
            pass
        elif self._storage_name.suffix in ['a', 'c', 'd', 'f', 'o', 'x']:
            bp.set('Plane.provenance.name', 'get_provenance_name()')
            bp.set(
                'Plane.provenance.reference', 'http://www.cfht.hawaii.edu/Instruments/SPIRou/'
            )
            bp.set('Plane.provenance.version', 'get_provenance_version()')
        else:
            bp.set('Plane.provenance.name', 'DRS')
            bp.set(
                'Plane.provenance.reference',
                'https://www.cfht.hawaii.edu/Instruments/SPIRou/SPIRou_pipeline.php',
            )
            bp.clear('Plane.provenance.version')
            bp.add_attribute('Plane.provenance.version', 'VERSION')

        bp.clear('Plane.provenance.lastExecuted')
        bp.add_attribute('Plane.provenance.lastExecuted', 'DRSPDATE')

    def _accumulate_spatial_chunk_blueprint(self, bp):
        # values from caom2spirou.default
        bp.configure_position_axes((1, 2))
        bp.set('Chunk.position.axis.axis1.ctype', 'RA---TAN')
        bp.set('Chunk.position.axis.axis2.ctype', 'DEC--TAN')
        bp.set('Chunk.position.axis.function.dimension.naxis1', 1)
        bp.set('Chunk.position.axis.function.dimension.naxis2', 1)
        bp.set('Chunk.position.axis.function.refCoord.coord1.pix', 1.0)
        bp.set('Chunk.position.axis.function.refCoord.coord2.pix', 1.0)
        bp.set('Chunk.position.axis.function.refCoord.coord1.val', 'get_ra_deg_from_0th_header()')
        bp.set('Chunk.position.axis.function.refCoord.coord2.val', 'get_dec_deg_from_0th_header()')
        bp.set('Chunk.position.axis.function.cd11', -0.00035833)
        bp.set('Chunk.position.axis.function.cd12', 0.0)
        bp.set('Chunk.position.axis.function.cd21', 0.0)
        bp.set('Chunk.position.axis.function.cd22', 0.00035833)
        bp.set('Chunk.position.coordsys', 'get_position_coordsys_from_0th_header()')
        bp.set('Chunk.position.equinox', 'get_position_equinox_from_0th_header()')
        self.accumulate_spatial_chunk_blueprint(bp)

    def _accumulate_spectral_chunk_blueprint(self, bp, axis_index):
        # from caom2IngestSpirou.py, l654
        # CW - Do energy stuff for raw and calibrated data
        # Initial numbers to be updated once have some reduced spectra
        # This was based on 50 orders of 4000 pix each covering 0.98 to 2.35
        # microns. New numbers based on reduced spectra 0.955 to 2.515 microns
        # TODO - should update old ones some time
        # naxis6 = 1
        # crpix6 = 0.5
        # crval6 = 955.0
        # cdelt6 = 1560.0
        #
        # other values from caom2spirou.default
        # SF - 21-06-22
        # https://doi.org/10.1117/12.2312317
        # In the end, it was decided that a stand-alone, InGaAs array system
        # was the best alternative for the detector. With a long-pass filter
        # starting at 0.98 μm, such a system is sensitive over the Y, J, and
        # H bands and so covers the bulk of the SPIRou wavelength range.
        #
        # use [0.98, 2.4], assume flat transmission
        bp.configure_energy_axis(axis_index)
        bp.set('Chunk.energy.axis.axis.ctype', 'WAVE')
        bp.set('Chunk.energy.axis.axis.cunit', 'nm')
        bp.set('Chunk.energy.axis.function.delta', 1560.0)
        bp.set('Chunk.energy.axis.function.naxis', 1)
        bp.set('Chunk.energy.axis.function.refCoord.pix', 0.5)
        bp.set('Chunk.energy.axis.function.refCoord.val', 955.0)
        bp.set('Chunk.energy.axis.error.rnder', 0.001)
        bp.set('Chunk.energy.axis.error.syser', 0.001)
        bp.set('Chunk.energy.resolvingPower', 73000.0)
        bp.set('Chunk.energy.specsys', 'TOPOCENT')
        bp.set('Chunk.energy.ssysobs', 'TOPOCENT')
        bp.set('Chunk.energy.ssyssrc', 'TOPOCENT')

    def get_exptime(self, ext):
        # caom2IngestSpirou.py, l530+
        if self._storage_name.simple:
            result = self._headers[ext].get('EXPTIME')
        else:
            result = self._headers[ext].get('DARKTIME')
        if result is None:
            self._logger.warning(
                f'No Time WCS refcoord.delta value for '
                f'{self._storage_name.file_uri}.'
            )
        return result

    def get_provenance_name(self, ext):
        result = None
        temp = self._headers[ext].get('RAMPSWV')
        if temp is not None:
            result = temp.split(' v')[0]
        return result

    def get_provenance_version(self, ext):
        result = None
        temp = self._headers[ext].get('RAMPSWV')
        if temp is not None:
            result = temp.split(' v')[1]
        return result

    def get_time_refcoord_delta(self, ext):
        # caom2IngestSpirou.py, l530+
        result = None
        if self._storage_name.suffix == 'r':
            temp = self._headers[ext].get('FRMTIME')
        elif self._storage_name.suffix == 'p':
            temp = self._headers[ext].get('TOTETIME')
        else:
            temp = self._headers[ext].get('DARKTIME')
        if temp is None:
            self._logger.warning(
                f'No Time WCS refcoord.delta value for '
                f'{self._storage_name.file_uri}.'
            )
        else:
            result = temp / (24.0 * 3600.0)
        return result

    def get_time_refcoord_naxis(self, ext):
        # caom2IngestSpirou.py, l557
        result = 1.0
        if self._storage_name.suffix == 'r':
            result = self._headers[ext].get('NREADS')
        if result is None:
            self._logger.warning(
                f'No Time WCS refcoord.naxis value for '
                f'{self._storage_name.file_uri}.'
            )
        return result

    def get_time_resolution(self, ext):
        # caom2IngestSpirou.py, l530+
        result = self.get_time_refcoord_delta(ext)
        if self._storage_name.suffix == 'r':
            result = result * (24.0 * 3600.0)
        else:
            result = self.get_exptime(ext)
        if result is None:
            self._logger.warning(
                f'No Time WCS resolution value for {self._storage_name.file_uri}.'
            )
        return result

    def make_axes_consistent(self):
        # stricter WCS validation
        self._chunk.naxis = None
        if self._chunk.energy is not None:
            self._chunk.energy_axis = None
        #     if self._observation.type == 'DARK':
        #         # caom2IngestSpirou.py, l514
        #         self._chunk.energy = None
        if self._chunk.time is not None:
            self._chunk.time_axis = None
        if self._chunk.position is not None:
            self._chunk.position_axis_1 = None
            self._chunk.position_axis_2 = None

    def update_observation(self):
        super().update_observation()
        if self._storage_name.suffix != 'r':
            cc.rename_parts(self._observation, self._headers)

    def update_plane(self):
        super().update_plane()
        # caom2IngestSpirou.py, l584
        if self._storage_name.suffix in ['e', 's', 't']:
            self._update_plane_provenance()


class SpirouTemporal(Spirou):

    def accumulate_blueprint(self, bp):
        super().accumulate_blueprint(bp)
        bp.configure_time_axis(3)
        super().accumulate_time_chunk_blueprint(bp)
        bp.set('Chunk.time.axis.function.delta', 'get_time_refcoord_delta()')
        bp.set('Chunk.time.axis.function.naxis', 'get_time_refcoord_naxis()')
        bp.set('Chunk.time.resolution', 'get_time_resolution()')


class SpirouSpectralTemporal(SpirouTemporal):

    def accumulate_blueprint(self, bp):
        super().accumulate_blueprint(bp)
        self._accumulate_spectral_chunk_blueprint(bp, 4)


class SpirouSpatialSpectralTemporal(SpirouSpectralTemporal):

    def accumulate_blueprint(self, bp):
        super().accumulate_blueprint(bp)
        self._accumulate_spatial_chunk_blueprint(bp)


class SpirouG(Spirou):

    def accumulate_blueprint(self, bp):
        """Configure the SPIRou-specific ObsBlueprint at the CAOM model
        Observation level.
        """
        super().accumulate_blueprint(bp)
        # SF 03-03-23 - use ETYPE, add Spatial WCS support
        bp.clear('Observation.type')
        bp.add_attribute('Observation.type', 'ETYPE')
        bp.set('Plane.dataProductType', DataProductType.IMAGE)

        self._accumulate_spatial_chunk_blueprint(bp)
        bp.set('Chunk.position.axis.function.refCoord.coord1.val', '_get_ra()')
        bp.set('Chunk.position.axis.function.refCoord.coord2.val', '_get_dec()')

        self._accumulate_spectral_chunk_blueprint(bp, 4)

    def _get_ra(self, ext):
        ra, dec = ac.build_ra_dec_as_deg(self._headers[0].get('RA'), self._headers[0].get('DEC'))
        return ra

    def _get_dec(self, ext):
        ra, dec = ac.build_ra_dec_as_deg(self._headers[0].get('RA'), self._headers[0].get('DEC'))
        return dec

    def update_plane(self):
        pass

    def update_time(self):
        self._logger.debug(
            f'Begin update_time for {self._storage_name.obs_id}'
        )
        # construct TemporalWCS for 'g' files from the CAOM2 pieces
        # because the structure of 'g' files is so varied, it's not
        # possible to hand over even part of the construction to the
        # blueprint.
        # SF - 22-09-20 - use ETIME

        ref_coord_val = mc.get_keyword(self._headers, 'DATE')
        ref_coord_mjd = cfht_time_helper(ref_coord_val).value

        if self._chunk.time is None:
            self._chunk.time = TemporalWCS(
                CoordAxis1D(Axis('TIME', 'd')), timesys='UTC'
            )
        if self._chunk.time.axis is None:
            self._chunk.time.axis = CoordAxis1D(
                axis=Axis('TIME', 'd'),
                error=None,
                range=None,
                bounds=None,
                function=None,
            )

        time_index = self._headers[0].get('ZNAXIS')
        if time_index is None or time_index == 0:
            time_index = self._headers[1].get('ZNAXIS')
            if time_index is None or time_index == 0:
                time_index = self._headers[0].get('NAXIS')
                if time_index is None or time_index == 0:
                    time_index = self._headers[1].get('NAXIS')
        naxis_key = f'ZNAXIS{time_index}'
        time_naxis = mc.get_keyword(self._headers, naxis_key)
        if time_naxis is None:
            naxis_key = f'NAXIS{time_index}'
            time_naxis = mc.get_keyword(self._headers, naxis_key)

        ref_coord = RefCoord(pix=0.5, val=mc.to_float(ref_coord_mjd))

        e_time = mc.get_keyword(self._headers, 'ETIME')
        if e_time is None:
            self._logger.warning(f'No exposure found for {self._storage_name.file_name}. No Temporal WCS.')
        else:
            self._chunk.time.exposure = e_time / 1000.0
            self._chunk.time.resolution = self._chunk.time.exposure
            time_delta = self._chunk.time.exposure / 86400.0
            self._chunk.time.axis.function = CoordFunction1D(
                naxis=time_naxis, delta=time_delta, ref_coord=ref_coord
            )
        self._logger.debug(f'End _update_time_g for {self._storage_name.obs_id}')


class SpirouPolarization(Spirou):

    def accumulate_blueprint(self, bp):
        """Configure the SPIRou-specific ObsBlueprint at the CAOM model
        Observation level.
        """
        super().accumulate_blueprint(bp)
        self._accumulate_spatial_chunk_blueprint(bp)
        self._accumulate_spectral_chunk_blueprint(bp, 3)

        bp.configure_polarization_axis(7)
        bp.set('Chunk.polarization.axis.axis.ctype', 'STOKES')
        bp.set('Chunk.polarization.axis.function.naxis', 1)
        bp.set('Chunk.polarization.axis.function.delta', 1.0)
        bp.set('Chunk.polarization.axis.function.refCoord.pix', 1.0)

    def get_exptime(self, ext):
        result = self._headers[ext].get('TOTETIME')
        if result is None:
            self._logger.warning(f'No get_exptime value for {self._storage_name.file_uri}.')
        return result

    def get_time_refcoord_delta(self, ext):
        # caom2IngestSpirou.py, l530+
        result = None
        temp = self.get_exptime(ext)
        if temp is None:
            self._logger.warning(f'No Time WCS refcoord.delta value for {self._storage_name.file_uri}.')
        else:
            result = temp / (24.0 * 3600.0)
        return result

    def get_time_refcoord_naxis(self, ext):
        # caom2IngestSpirou.py, l557
        return 1.0

    def update_polarization(self):
        self._logger.debug(f'Begin update_polarization for {self._storage_name.obs_id}')
        header = None
        for h in self._headers:
            if h.get('EXTNAME') == self.part.name:
                header = h
                break

        stokes_param = header.get('STOKES')
        if stokes_param is None:
            self._logger.warning(
                f'No STOKES value for HDU {self.part.name} in {self._storage_name.obs_id}. No polarization.'
            )
            self._chunk.polarization = None
            self._chunk.polarization_axis = None
        else:
            lookup = {
                'I': 1.0,
                'Q': 2.0,
                'U': 3.0,
                'V': 4.0,
                'W': 5.0,
            }
            crval = lookup.get(stokes_param, 0.0)
            if crval == 0.0:
                self._logger.warning(f'STOKES value is {crval}. No polarization.')
                self._chunk.polarization = None
                self._chunk.polarization_axis = None
            else:
                if (
                    self._chunk.polarization is not None
                    and self._chunk.polarization.axis is not None
                    and self._chunk.polarization.axis.function is not None
                ):
                    self._chunk.polarization.axis.function.ref_coord.val = crval
        # check with Dustin on what a polarization cut-out
        # looks like before deciding this is semi-ok
        self._chunk.naxis = None
        self._chunk.position_axis_1 = None
        self._chunk.position_axis_2 = None
        self._chunk.energy_axis = None
        self._chunk.time_axis = None
        self._chunk.polarization_axis = None
        self._logger.debug(f'End update_polarization for {self._storage_name.obs_id}')

    def update_time(self):
        self._logger.debug(f'Begin update_time for {self._storage_name.obs_id}')
        # TOTETIME is not in all the HDUs, so copy it from the HDUs that have
        # it, and use it everywhere - this matches existing CFHT SPIRou 'p'
        # behaviour

        def _find_keywords_in_header(header, lookup):
            values = []
            for keyword in header:
                if keyword.startswith(lookup) and len(keyword) > len(lookup):
                    values.append(header.get(keyword))
            return values

        header = None
        for h in self._headers:
            if h.get('EXTNAME') == self.part.name:
                header = h
                break

        tot_e_time = header.get('TOTETIME')

        lower = _find_keywords_in_header(header, 'MJDATE')
        upper = _find_keywords_in_header(header, 'MJDEND')

        if len(lower) > 0:
            for ii, entry in enumerate(lower):
                self._chunk.time = cc.build_temporal_wcs_append_sample(
                    self._chunk.time, entry, upper[ii]
                )

        if self._chunk.time is None:
            self._logger.warning(
                f'No chunk time metadata for {self._storage_name.obs_id}, part '
                f'{self.part.name}.'
            )
        elif tot_e_time is None:
            self._logger.warning(
                f'Cannot find time metadata for {self._storage_name.obs_id}, part '
                f'{self.part.name}.'
            )
        else:
            self._chunk.time.exposure = tot_e_time
            self._chunk.time.resolution = tot_e_time
        self._logger.debug(f'End update_time for {self._storage_name.obs_id}')


class WircamTemporal(InstrumentType):
    def __init__(self, cfht_name, clients, reporter, observation, config):
        super().__init__(cfht_name, clients, reporter, observation, config)
        # https://www.cfht.hawaii.edu/Instruments/Imaging/WIRCam/ says November 2006
        # but existing metadata has a minimum value of 2000-07-21 00:00:00 for mastertwilightflat_Ks_13Aw01_v200.fits
        self._instrument_start_date = mc.make_datetime('2000-07-20 00:00:00.000')

    def accumulate_blueprint(self, bp):
        """Configure the WIRCam-specific ObsBlueprint at the CAOM model
        Observation level.
        """
        super().accumulate_blueprint(bp)

        # caom2IngestWircam.py, l1063
        if self._storage_name.suffix == 'p':
            bp.set('Plane.provenance.keywords', 'skysubtraction=yes')
        elif self._storage_name.suffix == 's':
            bp.set('Plane.provenance.keywords', 'skysubtraction=no')
        bp.set('Plane.provenance.lastExecuted', 'get_provenance_last_executed()')
        bp.set_default('Plane.provenance.name', 'IIWI')
        bp.set_default(
            'Plane.provenance.reference',
            'http://www.cfht.hawaii.edu/Instruments/Imaging/WIRCam',
        )
        bp.set('Chunk.energy.bandpassName', 'get_bandpass_name()')

        self._logger.debug('Done accumulate_blueprint.')

    def get_bandpass_name(self, ext):
        wheel_a = self._headers[ext].get('WHEELADE')
        wheel_b = self._headers[ext].get('WHEELBDE')
        result = None
        if wheel_a == 'Open' and wheel_b != 'Open':
            result = wheel_b
        elif wheel_b == 'Open' and wheel_a != 'Open':
            result = wheel_a
        elif wheel_a == 'Open' and wheel_b == 'Open':
            result = 'Open'
        return result

    def get_obs_type(self, ext):
        result = super().get_obs_type(ext)
        # caom2IngestWircamdetrend.py, l369
        if 'weight' in self._storage_name.file_uri:
            result = 'WEIGHT'
        elif (
            'badpix' in self._storage_name.file_uri
            or 'hotpix' in self._storage_name.file_uri
            or 'deadpix' in self._storage_name.file_uri
        ):
            result = 'BPM'
        return result

    def get_provenance_last_executed(self, ext):
        result = self._headers[ext].get('PROCDATE')
        if result:
            # format like PROCDATE= '2019-11-27HST14:15:30'
            result = mc.make_datetime(result)
        return result

    def _update_plane_post(self):
        # complete the ingestion of the missing bits of a sky construct file
        self._logger.debug(f'Begin _update_plane_post for {self._observation.observation_id}')
        if self._storage_name.suffix not in ['p', 'y']:
            return

        # for some 'y' files, that don't have enough metadata on their own,
        # if the 'p' plane exists, and the 'y' plane exists,
        # copy the metadata to the 'y' plane, because the 'y' file
        # will not have enough metadata to fill these things in alone
        copy_to_key = self._storage_name.product_id
        copy_to_artifact_key = self._storage_name.file_uri
        if self._storage_name.suffix == 'p':
            copy_to_key = self._storage_name.product_id.replace('p', 'y')
            copy_to_artifact_key = self._storage_name.file_uri.replace(
                'p', 'y', 1
            )

        copy_from_key = self._storage_name.product_id
        copy_from_artifact_key = self._storage_name.file_uri
        if self._storage_name.suffix == 'y':
            copy_from_key = self._storage_name.product_id.replace('y', 'p')
            copy_from_artifact_key = self._storage_name.file_uri.replace(
                'y', 'p', 1
            )

        if (
            copy_to_key in self._observation.planes.keys()
            and copy_from_key in self._observation.planes.keys()
        ):
            copy_to_plane = self._observation.planes[copy_to_key]
            copy_from_plane = self._observation.planes[copy_from_key]
            if (
                copy_from_artifact_key in copy_from_plane.artifacts.keys()
                and copy_to_artifact_key in copy_to_plane.artifacts.keys()
            ):
                copy_from_artifact = copy_from_plane.artifacts[
                    copy_from_artifact_key
                ]
                copy_to_artifact = copy_to_plane.artifacts[
                    copy_to_artifact_key
                ]
                if copy_from_plane.provenance is not None:
                    copy_to_plane.provenance = cc.copy_provenance(
                        copy_from_plane.provenance
                    )
                    # set to None, because caom2IngestWircam.py sets only for
                    # 'p', 's' files: l1064, l1092
                    while len(copy_to_plane.provenance.keywords) > 0:
                        copy_to_plane.provenance.keywords.pop()
                InstrumentType._semi_deep_copy_plane(
                    copy_from_plane,
                    copy_to_plane,
                    copy_from_artifact,
                    copy_to_artifact,
                )
        self._logger.debug('End _update_plane_post')

    def make_axes_consistent(self):
        # position axis check is to determine if naxis should
        # be set
        # 'y' is auxOverride l345 caom2IngestWircam.py
        if (
            self._storage_name.suffix in ['d', 'f', 'g', 'o', 'y']
            and self._chunk.position is None
        ):
            # PD - 17-01-20
            #  This is a FLAT field exposure so the position
            #  is not relevant and only the energy and time is
            #  relevant for discovery. The easiest correct
            #  thing to do is to leave naxis, energyAxis, and
            #  timeAxis all null: the same plane metadata
            #  should be generated and that should be valid.
            #  The most correct thing to do would be to set
            #  naxis=2, positionAxis1=1, positionAxis2=2 (to
            #  indicate image) and then use a suitable
            #  coordinate system description that meant "this
            #  patch of the inside of the dome" or maybe some
            #  description of the pixel coordinate system
            #  (because wcs kind of treats the sky and the
            #  pixels as two different systems)... I don't
            #  know how to do that and it adds very minimal
            #  value (it allows Plane.position.dimension to be
            #  assigned a value).
            self._chunk.naxis = None
            self._chunk.position_axis_1 = None
            self._chunk.position_axis_2 = None
            self._chunk.energy_axis = None
            self._chunk.time_axis = None

        if self._chunk.naxis == 2:
            self._chunk.time_axis = None
            self._chunk.energy_axis = None

    def reset_position(self):
        if (
            self._chunk.position is not None
            and self._chunk.position.coordsys.lower() == 'null'
        ):
            cc.reset_position(self._chunk)
            self._chunk.naxis = None
            self._chunk.energy_axis = None
            self._chunk.time_axis = None

    def update_energy(self):
        filter_name = mc.get_keyword(self._headers, 'FILTER')
        filter_md, updated_filter_name = get_filter_md(filter_name, self._storage_name)
        cc.build_chunk_energy_range(
            self._chunk, updated_filter_name, filter_md
        )
        if self._chunk.energy is not None:
            self._chunk.energy.ssysobs = 'TOPOCENT'
            self._chunk.energy.ssyssrc = 'TOPOCENT'
            # values from caom2megacam.default, caom2megacamdetrend.default
            self._chunk.energy.axis.error = CoordError(1.0, 1.0)

    def update_plane(self):
        super().update_plane()
        # caom2IngestWircam.py, l193
        # CW 09-01-20
        # Only the 'o' is input
        if self._storage_name.suffix in ['p', 's']:
            self._update_plane_provenance()

    def update_position(self):
        pass

    def update_time(self):
        self._logger.debug(f'Begin update_time for {self._storage_name.obs_id}')
        self._chunk.time.axis.function.naxis = 1
        if self._observation.type in ['BPM', 'DARK', 'FLAT', 'WEIGHT']:
            self._chunk.naxis = None
        else:
            n_exp = self._headers[self._extension].get('NEXP')
            if n_exp is not None:
                # caom2IngestWircam.py, l843
                self._chunk.time.axis.function.naxis = mc.to_int(n_exp)
        self._logger.debug(f'End update_time for {self._storage_name.obs_id}')

    def update(self):
        super().update()
        self._update_plane_post()
        return self._observation


class WircamSpectralTemporal(WircamTemporal):

    def accumulate_blueprint(self, bp):
        """Configure the WIRCam-specific ObsBlueprint at the CAOM model
        Observation level.
        """
        super().accumulate_blueprint(bp)
        bp.configure_time_axis(3)
        self.accumulate_time_chunk_blueprint(bp)


class Wircam(WircamSpectralTemporal):

    def accumulate_blueprint(self, bp):
        """Configure the WIRCam-specific ObsBlueprint at the CAOM model
        Observation level.
        """
        super().accumulate_blueprint(bp)
        bp.configure_position_axes((1, 2))
        self.accumulate_spatial_chunk_blueprint(bp)


class WircamG(WircamTemporal):
    """suffix == 'g'"""

    def accumulate_blueprint(self, bp):
        """Configure the telescope-specific ObsBlueprint at the CAOM model Observation level.

        This code captures the portion of the TDM->CAOM model mapping, where the relationship is one or many elements
        of the TDM are required to set individual elements of the CAOM model. If the mapping cardinality is 1:1
        generally, use add_attribute. If the mapping cardinality is n:1 use the set method to reference a function
        call. """
        self._logger.debug('Begin accumulate_blueprint.')
        super().accumulate_blueprint(bp)
        # don't want GUIDE file Observation-level metadata
        self._use_existing_observation(bp)
        bp.configure_time_axis(3)

    def get_bandpass_name(self, ext):
        wheel_a = self._headers[ext].get('WHEELADE')
        wheel_b = self._headers[ext].get('WHEELBDE')
        result = None
        if wheel_a == 'Open' and wheel_b != 'Open':
            result = wheel_b
        elif wheel_b == 'Open' and wheel_a != 'Open':
            result = wheel_a
        elif wheel_a == 'Open' and wheel_b == 'Open':
            result = 'Open'
        return result

    def get_obs_type(self, ext):
        result = super().get_obs_type(ext)
        if result is None:
            result = 'GUIDE'
        return result

    def reset_energy(self):
        temp_bandpass_name = self._headers[self._extension].get('FILTER')
        if temp_bandpass_name == 'FakeBlank':
            cc.reset_energy(self._chunk)

    def update_position(self):
        """'g' file position handling."""
        self._logger.debug(f'Begin update_position for {self._storage_name.obs_id}')
        header = self._headers[self._extension]
        obj_name = header.get('OBJNAME')
        part_index = mc.to_int(self.part.name)
        if obj_name == 'zenith' or part_index >= 5:
            # SGo - the second clause is here, because there are only four
            # sets of position information in headers (RA/DEC of guide start
            # on arrays 1 2 3 4), and that's the only thing that is calculated
            # in the original code. Values for HDU 5+ are not written as part
            # of the override file, and thus default to 0, which fails
            # ingestion to the service.
            self._logger.warning(
                f'obj_name is {obj_name}. part_num is {part_index} No position for {self._storage_name.obs_id}'
            )
            cc.reset_position(self._chunk)
            return

        header = self._headers[part_index]
        cd1_1 = None
        cd2_2 = None
        if header.get('CRVAL2') is not None or self._headers[0].get('CRVAL2') is not None:
            cd1_1 = mc.to_float(header.get('PIXSCAL1')) / 3600.0
            cd2_2 = mc.to_float(header.get('PIXSCAL2')) / 3600.0

        if cd1_1 is None or cd2_2 is None:
            self._logger.warning(
                f'cd1_1 is {cd1_1}, cd2_2 is {cd2_2}, part_index is {part_index}. No position for this part for '
                f'{self._storage_name.obs_id}.'
            )
            cc.reset_position(self._chunk)
            return

        wcgd_ra = header.get(f'WCGDRA{self._part.name}')
        if wcgd_ra is None:
            wcgd_ra = self._headers[0].get(f'WCGDRA{self._part.name}')
        wcgd_dec = header.get(f'WCGDDEC{self._part.name}')
        if wcgd_dec is None:
            wcgd_dec = self._headers[0].get(f'WCGDDEC{self._part.name}')
        if wcgd_ra is None or wcgd_dec is None:
            self._logger.warning(f'WCGDRA{self._part.name} and WCGDDEC{self._part.name} are undefined. No position.')
            cc.reset_position(self._chunk)
            return
        cr_val1, cr_val2 = ac.build_ra_dec_as_deg(wcgd_ra, wcgd_dec, frame='fk5')
        if math.isclose(cr_val1, 0.0) and math.isclose(cr_val2, 0.0):
            self._logger.warning(f'WCGDRA{self._part.name} and WCGDDEC{self._part.name} are close to 0. No position.')
            cc.reset_position(self._chunk)
            return

        naxis_1 = header.get('ZNAXIS1')
        if naxis_1 is None:
            naxis_1 = header.get('NAXIS1')
        naxis_2 = header.get('ZNAXIS2')
        if naxis_2 is None:
            naxis_2 = header.get('NAXIS2')

        if mc.to_float(self._storage_name.obs_id) < 980000:
            cr_val2 *= 15.0

        # caom2IngestWircam.py, l367
        header['NAXIS1'] = naxis_1
        header['NAXIS2'] = naxis_2
        header['CRPIX1'] = naxis_1 / 2.0
        header['CRPIX2'] = naxis_2 / 2.0
        header['CRVAL1'] = cr_val1
        header['CRVAL2'] = cr_val2
        header['CD1_1'] = -1.0 * cd1_1
        header['CD1_2'] = 0.0
        header['CD2_1'] = 0.0
        header['CD2_2'] = cd2_2

        wcs_parser = FitsWcsParser(header, self._storage_name.obs_id, self._extension)
        if self._chunk is None:
            self._chunk = Chunk()
        wcs_parser.augment_position(self._chunk)
        if self._chunk.position is not None:
            self._chunk.naxis = 2
            self._chunk.position_axis_1 = 1
            self._chunk.position_axis_2 = 2
            if self._chunk.position.axis is not None:
                self._chunk.position.axis.error1 = CoordError(0.0000278, 0.0000278)
                self._chunk.position.axis.error2 = CoordError(0.0000278, 0.0000278)
        self._logger.debug(f'End update_position for {self._storage_name.obs_id}')

    def update_plane(self):
        if self._observation is not None:
            o_plane_id = self._storage_name.product_id.replace('g', 'o')
            if o_plane_id in self._observation.planes.keys():
                o_plane = self._observation.planes[o_plane_id]
                self._plane.data_release = o_plane.data_release
                self._plane.meta_release = o_plane.meta_release
                if o_plane.provenance is not None and self._plane.provenance is not None:
                    self._plane.provenance.run_id = o_plane.provenance.run_id

    def update_time(self):
        self._logger.debug(f'Begin update_time for {self._storage_name.obs_id}')
        # construct TemporalWCS for 'g' files from the CAOM2 pieces
        # because the structure of 'g' files is so varied, it's not
        # possible to hand over even part of the construction to the
        # blueprint.

        # SF - 07-05-20
        # so NAXIS here (where 'here' is a 'g' file) is ZNAXIS=3: time
        # sequence of images of the guiding camera => this means try
        # ZNAXIS* keyword values before trying NAXIS*, hence the header
        # lookup code

        ref_coord_val = ac.to_mjd(mc.get_keyword(self._headers, 'MJD-OBS'))
        part_index = mc.to_int(self.part.name)
        part_header = self._headers[part_index]

        if self._chunk.time is None:
            self._chunk.time = TemporalWCS(CoordAxis1D(Axis('TIME', 'd')), timesys='UTC')

        if self._chunk.time.axis is None:
            self._chunk.time.axis = CoordAxis1D(
                axis=Axis('TIME', 'd'),
                error=None,
                range=None,
                bounds=None,
                function=None,
            )

        if self._chunk.time.axis.error is None:
            self._chunk.time.axis.error = CoordError(rnder=0.0000001, syser=0.0000001)

        if self._chunk.time.axis.function is None and ref_coord_val is not None:
            ref_coord = RefCoord(pix=0.5, val=mc.to_float(ref_coord_val.value))

            time_index = part_header.get('ZNAXIS')
            if time_index is None:
                time_index = part_header.get('NAXIS')
            naxis_key = f'ZNAXIS{time_index}'
            time_naxis = part_header.get(naxis_key)
            if time_naxis is None:
                naxis_key = f'NAXIS{time_index}'
                time_naxis = part_header.get(naxis_key)

            # CW
            # Define time samples for guidecube data
            # Guiding time doesn't seem to match up very well, so just
            # say that use MJD-OBS gnaxis3 and WCPERIOD
            #
            # code from caom2IngestWircam.py, l876+
            wcgdra1_0 = self._headers[0].get('WCGDRA1')
            wc_period_0 = self._headers[0].get('WCPERIOD')
            wc_period = None
            if wcgdra1_0 is not None and wc_period_0 is not None:
                wc_period = wc_period_0
            else:
                wcgdra1_1 = self._headers[1].get('WCGDRA1')
                wc_period_1 = self._headers[1].get('WCPERIOD')
                if wcgdra1_1 is not None and wc_period_1 is not None:
                    wc_period = wc_period_1

            time_delta = None
            if wc_period is not None:
                if wc_period < 0.0:
                    wc_period = 100.0
                # caom2IngestWircam.py, l375
                self._chunk.time.exposure = wc_period / 1000.0
                self._chunk.time.resolution = self._chunk.time.exposure
                time_delta = self._chunk.time.exposure / 86400.0
            self._chunk.time.axis.function = CoordFunction1D(naxis=time_naxis, delta=time_delta, ref_coord=ref_coord)

        self._logger.debug(f'End update_time for {self._storage_name.obs_id}')


class WircamO(Wircam):

    def update_position(self):
        self._logger.debug(f'Begin update_position for {self._storage_name.obs_id}')
        part_index = mc.to_int(self.part.name)
        header = self._headers[part_index]
        ra_deg = header.get('RA_DEG')
        dec_deg = header.get('DEC_DEG')
        if self._chunk.position is None and ra_deg is not None and dec_deg is not None:
            self._logger.info(f'Adding position information for {self._storage_name.obs_id}')
            header['CTYPE1'] = 'RA---TAN'
            header['CTYPE2'] = 'DEC--TAN'
            header['CUNIT1'] = 'deg'
            header['CUNIT2'] = 'deg'
            header['CRVAL1'] = ra_deg
            header['CRVAL2'] = dec_deg
            wcs_parser = FitsWcsParser(header, self._storage_name.obs_id, self._extension)
            if self._chunk is None:
                self._chunk = Chunk()
            wcs_parser.augment_position(self._chunk)
            if self._chunk.position is not None:
                self._chunk.position_axis_1 = 1
                self._chunk.position_axis_2 = 2
        self._logger.debug(f'End update_position')


class Unsupported(AuxiliaryType):
    """This class is used to handle unsupported instrument types. It is the minimal information to make a file
    findable in the CAOM2 model."""

    def get_meta_release(self, ext):
        result = super().get_meta_release(ext)
        if result is None:
            for keyword in ['HSTTIME']:
                # 'Wed Jun 13 14:00:44 HST 1990'
                result = self._headers[ext].get(keyword)
                if result in ['1970-00-01', '1970-00-01T0:00:00'] or result is None:
                    continue
                else:
                    result = mc.make_datetime(result)
                    break
        return result


def _repair_comment_provenance_value(value, obs_id):
    logging.debug(f'Begin _repair_comment_provenance_value for {obs_id}')
    results = []
    # COMMENT headers with provenance:
    # COMMENT Scan member=2445653o st=174 iq=1.2200 bk=5.5214 ex=0.024000 ...
    # COMMENT Flat member=2445211f
    # COMMENT Standard member=2445849o
    if 'member=' in str(value):
        for entry in value:
            if 'Scan member' in entry:
                temp = str(entry).split('member=')
                prov_prod_id = temp[1].split()[0]
                prov_obs_id = cn.CFHTName.get_obs_id(file_id=prov_prod_id)
                # 0 - observation
                # 1 - plane
                results.append([prov_obs_id, prov_prod_id])
    logging.debug(f'End _repair_comment_provenance_value')
    return results


def _repair_filename_provenance_value(value, obs_id):
    logging.debug(f'Begin _repair_filename_provenance_value for {obs_id}')
    prov_obs_id = None
    prov_prod_id = None
    # some values require no repairing, because they look like:
    # FILENAME= '2460503p'
    # FILENAM1= '2460503o'           / Base filename at acquisition
    # FILENAM2= '2460504o'           / Base filename at acquisition
    #
    # skip values that look like this:
    # FILENAME= '2452990p39'         / Current filename after processing
    #
    # repair values that look like this:
    # FILENAME= '2401734o.fits'      / Base filename at acquisition
    temp = value.replace('.fits', '')
    if match('[0-9]{5,7}o', temp):
        prov_prod_id = temp
        prov_obs_id = temp[:-1]
    logging.debug(f'End _repair_filename_provenance_value')
    return prov_obs_id, prov_prod_id


def _repair_imcmb_provenance_value(value, obs_id):
    logging.debug(f'Begin _repair_imcmb_provenance_value for {obs_id}')
    prov_obs_id = None
    prov_prod_id = None
    # CFHT files contain other IMCMB headers that look like this - ignore
    # them here:
    # IMCMB_DT= 'FLIPS ver 3.0 - Elixir by CFHT - Wed Dec 4 2019 -  9:53:11'
    # IMCMB_AL= 'SIGMA   '
    # IMCMB_CA= 'MEDIAN  '
    # IMCMB_LS=                  3.5 / Lower threshold for clipping rejection
    # IMCMB_HS=                  3.5 / Lower clipping rejection threshold
    # IMCMB_FT= 'MASTER_DETREND_BIAS'
    # IMCMB_OP= '1DYMODEL_OVERSCAN'
    # IMCMB_NI=                   30 / Number of input files
    # IMCMB_DA=                    T / Dual amplifier A,B
    # IMCMB_IF= 'NAME BIAS_A MODE_A BIAS_B MODE_B' / Input file parameters
    if '.fits' in str(value):
        # input looks like:
        # '2463481b.fits[ccd39] 1231 1 1225 1' / Input file stats
        # or like:
        # '707809o00.fits 0 1569 0.341' / Input file stats
        temp = value.split('.fits')
        if '[' in value:
            prov_prod_id = temp[0]
        else:
            prov_prod_id = temp[0][:-2]
        prov_obs_id = cn.CFHTName.get_obs_id(file_id=prov_prod_id)
    logging.debug(f'End _repair_imcmb_provenance_value')
    return prov_obs_id, prov_prod_id


def get_filter_md(filter_name, storage_name):
    filter_md = md.filter_cache.get_svo_filter(storage_name.instrument.value, filter_name)
    if not md.filter_cache.is_cached(storage_name.instrument.value, filter_name):
        # want to stop ingestion if the filter name is not expected
        raise mc.CadcException(
            f'Could not find filter metadata for {filter_name} in {storage_name.file_uri}.'
        )
    # CW - 15-05-20
    # some flats like this have filter names like ‘i’, instead of ‘i.MP9701’. Even though there may only be a few of
    # these, we want zero so they don’t appear in the filters picklist and confuse users. If the header doesn’t have
    # the full filter name maybe you can hack it based on your knowledge of which i filter was used during this era.
    #
    # SGo - hence the reverse lookup of FILTER_REPAIR CACHE
    updated_filter_name = mc.reverse_lookup(filter_name, md.cache.get_from(md.FILTER_REPAIR_CACHE))
    if updated_filter_name is None:
        updated_filter_name = filter_name
    return filter_md, updated_filter_name


def is_mega_temporal(storage_name):
    # CW
    # Ignore energy wcs if some type of calibration file or filter='None' or 'Open' or there is no filter match
        # if not (
        #     self._filter_name is None
        #     or self._filter_name in ['Open', 'NONE']
        #     or ac.FilterMetadataCache.get_fwhm(filter_md) is None
        #     or self._observation.type in ['DARK']
        # ):
    headers = storage_name.metadata.get(storage_name.file_uri)
    filter_name = mc.get_keyword(headers, 'FILTER')
    filter_md, updated_filter_name = get_filter_md(filter_name, storage_name)
    obs_type = mc.get_keyword(headers, 'OBSTYPE')
    result = (
        updated_filter_name is None
        or updated_filter_name in ['Open', 'NONE']
        or ac.FilterMetadataCache.get_fwhm(filter_md) is None
        or obs_type is not None and obs_type == 'DARK' and '_flag' not in storage_name.file_uri
    )
    return result


def is_spirou_spectral_temporal(headers):
    result = True
    # from caom2IngestSpirou.py, l499+
    # CW - ignore position wcs if a calibration file
    ra_deg = mc.get_keyword(headers, 'RA_DEG')
    dec_deg = mc.get_keyword(headers, 'DEC_DEG')
    ra_dec_sys = mc.get_keyword(headers, 'RADECSYS')
    obs_type = mc.get_keyword(headers, 'OBSTYPE')
    if obs_type in ['OBJECT', 'ALIGN'] and not (
        ra_deg is None and dec_deg is None and (ra_dec_sys is None or ra_dec_sys.lower() == 'null')
    ):
        result = False
    return result


def is_wircam_spectral_temporal(storage_name):
    result = False
    headers = storage_name.metadata.get(storage_name.file_uri)
    obs_type = mc.get_keyword(headers, 'OBSTYPE')
    if (
        storage_name.suffix == 'f'
        or obs_type in ['BPM', 'DARK', 'FLAT', 'WEIGHT']
        or 'weight' in storage_name.file_uri
        or 'pix' in storage_name.file_uri
    ):
        result = True
    return result


def factory(cfht_name, clients, reporter, observation, config):
    if cfht_name.instrument is md.Inst.ESPADONS:
        if cfht_name.suffix in ['b', 'c', 'd', 'f', 'x']:
            # CW - Ignore position wcs if a calibration file - suffix list from caom2IngestEspadons.py, l389
            # 'b', 'd', 'c', 'f', 'x'
            temp = EspadonsSpectralTemporal(cfht_name, clients, reporter, observation, config)
        elif cfht_name.suffix == 'p':
            temp = EspadonsPolarization(cfht_name, clients, reporter, observation, config)
        elif cfht_name.suffix == 'i':
            temp = EspadonsI(cfht_name, clients, reporter, observation, config)
        else:
            temp = EspadonsSpatialSpectralTemporal(cfht_name, clients, reporter, observation, config)
    elif cfht_name.instrument in [md.Inst.MEGAPRIME, md.Inst.MEGACAM]:
        if '_diag' in cfht_name.file_name:
            # SF 16-03-23 record the diag ones as catalogues,  artifact of the *p ones - same behaviour as for the
            # preview images
            temp = AuxiliaryType(cfht_name, clients, reporter, observation, config)
        elif '_flag' in cfht_name.file_name:
            if observation is None:
                temp = MegaTemporal(cfht_name, clients, reporter, observation, config)
            else:
                temp = MegaFlag(cfht_name, clients, reporter, observation, config)
        elif cfht_name.suffix in ['b', 'd', 'l'] or is_mega_temporal(cfht_name):
            temp = MegaTemporal(cfht_name, clients, reporter, observation, config)
        elif cfht_name.suffix == 'f':
            temp = MegaSpectralRangeTemporal(cfht_name, clients, reporter, observation, config)
        else:
            temp = Mega(cfht_name, clients, reporter, observation, config)
    elif cfht_name.instrument is md.Inst.SITELLE:
        if cfht_name.hdf5:
            # if len(headers) > 0:
            if len(cfht_name.metadata.get(cfht_name.file_uri)) > 0:
                # len => could be an h5 file with no attrs, in which case the metadata gets copied from the 'p'
                # artifact
                temp = SitelleHdf5(cfht_name, clients, reporter, observation, config)
            else:
                temp = SitelleNoHdf5Metadata(cfht_name, clients, reporter, observation, config)
        else:
            if cfht_name.suffix == 'p':
                temp = SitelleP(cfht_name, clients, reporter, observation, config)
            elif cfht_name.suffix in ['a', 'o', 'x']:
                temp = SitelleSpatialRangeSpectralTemporal(cfht_name, clients, reporter, observation, config)
            elif cfht_name.suffix in ['f']:
                temp = SitelleSpectralTemporal(cfht_name, clients, reporter, observation, config)
            elif cfht_name.suffix in ['b', 'd']:
                # CW, SF 18-12-19 - SITELLE biases and darks have no energy, all other observation types do
                temp = SitelleTemporal(cfht_name, clients, reporter, observation, config)
            else:
                temp = SitelleSpatialFunctionSpectralTemporal(cfht_name, clients, reporter, observation, config)
    elif cfht_name.instrument is md.Inst.SPIROU:
        if cfht_name.suffix == 'g':
            temp = SpirouG(cfht_name, clients, reporter, observation, config)
        elif cfht_name.suffix == 'p':
            temp = SpirouPolarization(cfht_name, clients, reporter, observation, config)
        elif cfht_name.suffix == 'd':
            temp = SpirouTemporal(cfht_name, clients, reporter, observation, config)
        elif is_spirou_spectral_temporal(cfht_name.metadata.get(cfht_name.file_uri)):
            temp = SpirouSpectralTemporal(cfht_name, clients, reporter, observation, config)
        else:
            temp = SpirouSpatialSpectralTemporal(cfht_name, clients, reporter, observation, config)
    elif cfht_name.instrument is md.Inst.WIRCAM:
        if cfht_name.suffix == 'g':
            temp = WircamG(cfht_name, clients, reporter, observation, config)
        else:
            if is_wircam_spectral_temporal(cfht_name):
                temp = WircamSpectralTemporal(cfht_name, clients, reporter, observation, config)
            elif cfht_name.suffix == 'o':
                temp = WircamO(cfht_name, clients, reporter, observation, config)
            else:
                temp = Wircam(cfht_name, clients, reporter, observation, config)
    else:
        reporter._observable.rejected.record(mc.Rejected.NO_INSTRUMENT, cfht_name.file_name)
        logging.warning(f'Minimal mapping support for unexpected instrument {cfht_name.instrument}.')
        # SF - 05-06-25 - we do want to be transparent. If a file does not end up being properly ingested, making
        # them findable is still a chance for users to tell us what is wrong with them.
        temp = Unsupported(cfht_name, clients, reporter, observation, config)
    logging.debug(f'Created {temp.__class__.__name__} mapping.')
    return [temp]
