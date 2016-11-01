# Copyright 2016 Markus D. Herrmann, University of Zurich
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
'''Jterator module for combining channel from two grayscale images into one.'''
import numpy as np
import mahotas as mh
import logging
import collections

logger = logging.getLogger(__name__)

VERSION = '0.0.1'

Output = collections.namedtuple('Output', ['output_image', 'figure'])


def main(input_image_1, input_image_2, weight_1, weight_2, plot=False):
    '''Combines two grayscale images, such that the resulting combined image
    is a weighted sum of `input_mask_1` and `input_image_2`.

    Parameters
    ----------
    input_mask_1: numpy.ndarray[numpy.uint8 or numpy.uint16]
        2D unsigned integer array
    input_mask_2: numpy.ndarray[numpy.uint8 or numpy.uint16]
        2D unsigned integer array

    Returns
    -------
    jtmodules.combine_channels.Output

    Raises
    ------
    ValueError
        when `weight_1` or `weight_2` are not positive integers
    ValueError
        when `input_image_1` and `input_image_2` don't have the same dimensions
        and data type and if they don't have unsigned integer type
    '''
    if not isinstance(weight_1, int):
        raise TypeError('Weight #1 must have integer type.')
    if not isinstance(weight_2, int):
        raise TypeError('Weight #2 must have integer type.')
    if weight_1 < 1:
        raise ValueError('Weight #1 must be a positive integer.')
    if weight_2 < 1:
        raise ValueError('Weight #2 must be a positive integer.')
    logger.info('weight for first image: %d', weight_1)
    logger.info('weight for second image: %d', weight_2)

    if input_image_1.shape != image02.shape:
        raise ValueError('The two images must have identical dimensions.')
    if input_image_1.dtype != image02.dtype:
        raise ValueError('The two images must have identical data type.')

    if input_image_1.dtype == np.uint8:
        max_val = 2**8 - 1
    elif input_image_1.dtype == np.uint16:
        max_val = 2**16 - 1
    else:
        raise ValueError('The two images must have unsigned integer type.')

    logger.info('cast images to type float for arythmetics')
    img_1 = mh.stretch(input_image_1, 0, 1, float)
    img_2 = mh.stretch(input_image_2, 0, 1, float)
    logger.info('combine images using the provided weights')
    combined_image = img_1 * weight_1 + img_2 * weight_2
    logger.info('cast combined image back to correct data type')
    combined_image = mh.stretch(combined_image, 0, max_val, input_image_1.dtype)

    output_mask = combined_image
    if plot:
        from jtlib import plotting
        plots = [
            plotting.create_intensity_image_plot(input_image_1, 'ul'),
            plotting.create_intensity_image_plot(input_image_2, 'ur'),
            plotting.create_intensity_image_plot(combined_image, 'll')
        ]
        figure = plotting.create_figure(plots, title='combined mask')
    else:
        figure = str()

    return Output(output_mask, figure)


