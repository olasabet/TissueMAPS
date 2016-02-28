import os
import re
import logging
import pandas as pd
from cached_property import cached_property
from natsort import natsorted
from . import utils
from .metadata import ImageFileMapping
from .formats import Formats
from .readers import JsonReader
from .errors import RegexError

logger = logging.getLogger(__name__)


class PlateSource(object):
    '''
    Class that serves as a repository for source files belonging to one or more
    acquisitions of a plate. These files are generated by microscopes and
    contain the actual images and/or related metadata.

    See also
    --------
    :py:class:`tmlib.plate.Plate`
    '''

    PLATE_SOURCE_DIR_FORMAT = 'plate_{index:0>2}'

    def __init__(self, plate_source_dir, acquisition_mode):
        '''
        Initialize an instance of class PlateSource.

        Parameters
        ----------
        plate_source_dir: str
            absolute path to the directory that contains the source files
            for a particular plate
        acquisition_mode: str
            acquisition mode, i.e. whether separate acquisitions relate to the
            same marker as part of a time series experiment or another marker
            as part of a multiplexing experiment
            (options: ``{"series", "multiplexing"}``)

        Returns
        -------
        tmlib.source.PlateSource

        Raises
        ------
        OSError
            when `plate_source_dir` does not exist
        '''
        self.plate_source_dir = plate_source_dir
        if not os.path.exists(self.plate_source_dir):
            raise OSError(
                    'Directory does not exist: %s' % self.plate_source_dir)

    @property
    def dir(self):
        '''
        Returns
        -------
        str
            absolute path to the root folder of the plate acquisitions
        '''
        return self.plate_source_dir

    @property
    def index(self):
        '''
        Each `plate` has a zero-based index, depending on the order in which
        plates were added to the experiment.
        It is encoded in the name of the folder and is retrieved from
        it using a regular expression.

        Returns
        -------
        int
            zero-based plate index

        Raises
        ------
        RegexError
            when `index` cannot not be determined from folder name
        '''
        folder_name = os.path.basename(self.dir)
        regexp = utils.regex_from_format_string(self.PLATE_SOURCE_DIR_FORMAT)
        match = re.search(regexp, folder_name)
        if not match:
            raise RegexError(
                    'Can\'t determine plate index from folder "%s".'
                    % folder_name)
        return int(match.group('index'))

    def _is_acquistion_dir(self, folder):
        format_string = PlateAcquisition.ACQUISITION_DIR_FORMAT
        regexp = utils.regex_from_format_string(format_string)
        return True if re.match(regexp, folder) else False

    @property
    def acquisitions(self):
        '''
        A plate can be acquired 1 to *n* times, where *n* is the number of
        image acquisitions. Files are grouped per acquisition.

        Returns
        -------
        List[tmlib.acquisition.PlateAcquisition]
            files belonging to different image acquisitions
        '''
        acquisition_dirs = [
            os.path.join(self.dir, d)
            for d in os.listdir(self.dir)
            if os.path.isdir(os.path.join(self.dir, d)) and
            self._is_acquistion_dir(d)
        ]
        acquisition_dirs = natsorted(acquisition_dirs)
        return [PlateAcquisition(d) for d in acquisition_dirs]

    def add_acquisition(self):
        '''
        Add a new plate acquisition, i.e. create a new subdirectory in
        `plate_source_dir`.

        Returns
        -------
        tmlib.source.PlateAcquisition
            configured plate acquisition object
        '''
        new_index = len(self.acquisitions)
        name = PlateAcquisition.ACQUISITION_DIR_FORMAT.format(index=new_index)
        acquisition_dir = os.path.join(self.dir, name)
        logging.debug('create directory for new acquisition: %s',
                      acquisition_dir)
        os.mkdir(acquisition_dir)
        return PlateAcquisition(acquisition_dir)

    @property
    def image_mapping_file(self):
        '''
        Returns
        -------
        str
            absolute path to the file that contains the mapping from the
            originally acquired image files generated by the microscope
            to the final image files that contain the extracted images
        '''
        return os.path.join(self.dir, 'image_file_mapper.json')

    @property
    def image_mapping(self):
        '''
        Returns
        -------
        List[tmlib.metadata.ImageFileMapping]
            key-value pairs that map the location of individual planes within
            the original files to *Image* elements in the OMEXML
        '''
        image_mapping = list()
        with JsonReader(self.dir) as reader:
            hashmap = reader.read(self.image_mapping_file)
        for element in hashmap:
            image_mapping.append(ImageFileMapping(**element))
        return image_mapping


class PlateAcquisition(object):

    '''
    Class that serves as a container for all files of a plate that
    are part of the same image acquisition process.

    Files are separated by acquisitions, because microscopes usually generate
    separate metadata files for each acquisition.
    '''

    ACQUISITION_DIR_FORMAT = 'acquisition_{index:0>2}'

    OMEXML_DIR_NAME = 'omexml'
    IMAGE_DIR_NAME = 'images'
    METADATA_DIR_NAME = 'metadata'

    def __init__(self, acquisition_dir):
        '''
        Parameters
        ----------
        acquisition_dir: str
            absolute path to the acquisition folder

        Returns
        -------
        tmlib.source.PlateAcquisition

        See also
        --------
        :py:class:`tmlib.cfg.UserConfiguration`
        '''
        self.acquisition_dir = acquisition_dir

    @property
    def dir(self):
        '''
        Returns
        -------
        str
            absolute path to the acquisition folder
        '''
        return self.acquisition_dir

    @property
    def index(self):
        '''
        An *acquisition* has a zero-based `index` based on the order in which
        acquisitions were added.
        It is encoded in the name of the *acquisition* folder and is retrieved
        from it using a regular expression.

        Returns
        -------
        int
            zero-based acquisition index

        Raises
        ------
        RegexError
            when `index` cannot not be determined from folder name
        '''
        folder_name = os.path.basename(self.dir)
        regexp = utils.regex_from_format_string(self.ACQUISITION_DIR_FORMAT)
        match = re.search(regexp, folder_name)
        if not match:
            raise RegexError(
                    'Can\'t determine cycle id number from folder "%s" '
                    'using format "%s" provided by the configuration settings.'
                    % (folder_name, self.CYCLE_DIR_FORMAT))
        return int(match.group('index'))

    @utils.autocreate_directory_property
    def image_dir(self):
        '''
        Returns
        -------
        str
            absolute path to directory that contains the image files

        Note
        ----
        Directory is autocreated if it doesn't exist.
        '''
        return os.path.join(self.dir, self.IMAGE_DIR_NAME)

    @utils.autocreate_directory_property
    def metadata_dir(self):
        '''
        Returns
        -------
        str
            absolute path to directory that contains metadata files

        Note
        ----
        Directory is autocreated if it doesn't exist.
        '''
        return os.path.join(self.dir, self.METADATA_DIR_NAME)

    @utils.autocreate_directory_property
    def omexml_dir(self):
        '''
        Returns
        -------
        str
            absolute path to directory that contains the extracted OMEXML files
            for each acquired image in `image_dir`

        Note
        ----
        Directory is autocreated if it doesn't exist.
        '''
        return os.path.join(self.dir, self.OMEXML_DIR_NAME)

    @cached_property
    def omexml_files(self):
        '''
        Returns
        -------
        List[str]
            names of *OMEXML* files in `omexml_dir`

        Raises
        ------
        OSError
            when no OMEXML files are found in `omexml_dir`
        '''
        files = [
            f for f in os.listdir(self.omexml_dir)
            if f.endswith('.ome.xml')
        ]
        files = natsorted(files)
        if not files:
            raise OSError('No XML files found in "%s"' % self.omexml_dir)
        return files

    @property
    def _supported_image_file_extensions(self):
        return Formats().supported_extensions

    @cached_property
    def image_files(self):
        '''
        Returns
        -------
        List[str]
            names of image files in `image_dir`

        Raises
        ------
        OSError
            when no images files are found in `image_dir`

        Warning
        -------
        Only files with supported file extensions are considered.

        See also
        --------
        :py:class:`tmlib.formats.Formats`
        '''
        files = [
            f for f in os.listdir(self.image_dir)
            if not os.path.isdir(os.path.join(self.image_dir, f))
            and os.path.splitext(f)[1] in self._supported_image_file_extensions
        ]
        files = natsorted(files)
        if not files:
            raise OSError('No image files found in "%s"' % self.image_dir)
        return files

    @cached_property
    def additional_files(self):
        '''
        Returns
        -------
        List[str]
            names of files in `metadata_dir`
        '''
        files = [
            f for f in os.listdir(self.metadata_dir)
            if not os.path.isdir(os.path.join(self.metadata_dir, f))
        ]
        return files

    @property
    def image_metadata_file(self):
        '''
        Returns
        -------
        str
            name of the HDF5 file contains acquisition-specific image metadata
        '''
        return 'image_metadata.h5'

    @property
    def image_metadata(self):
        '''
        Returns
        -------
        pandas.DataFrame
            image metadata
        '''
        filename = os.path.join(self.dir, self.image_metadata_file)
        store = pd.HDFStore(filename)
        metadata = store.select('metadata')
        store.close()
        return metadata

    @property
    def image_mapping_file(self):
        '''
        Returns
        -------
        str
            name of the file that contains key-value pairs for mapping
            the images stored in the original image files to the
            the OME *Image* elements in `image_metadata`
        '''
        return 'image_file_mapping.json'

    @property
    def image_mapping(self):
        '''
        Returns
        -------
        List[tmlib.metadata.ImageFileMapping]
            key-value pairs to map the location of individual planes within the
            original files to the *Image* elements in the OMEXML
        '''
        image_mapping = list()
        with JsonReader(self.dir) as reader:
            hashmap = reader.read(self.image_mapping_file)
        for element in hashmap:
            image_mapping.append(ImageFileMapping(**element))
        return image_mapping
