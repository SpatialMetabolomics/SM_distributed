from mock import patch
import json
import numpy as np
from cStringIO import StringIO

from engine.imzml_txt_converter import ImzmlTxtConverter, ImageBounds, encode_coord_line, encode_data_line
from engine.test.util import sm_config, ds_config


def test_image_bounds_update():
    image_bounds = ImageBounds()
    image_bounds.update(-1, -50)
    image_bounds.update(100, 500)

    assert image_bounds.min_x == -1
    assert image_bounds.max_x == 100
    assert image_bounds.min_y == -50
    assert image_bounds.max_y == 500


def test_image_bounds_to_json():
    image_bounds = ImageBounds()
    image_bounds.update(-10, -30)
    image_bounds.update(10, 30)

    assert image_bounds.to_json() == json.dumps({'x': {'min': -10, 'max': 10},
                                                 'y': {'min': -30, 'max': 30}})


def test_encode_data_line():
    mzs, ints = np.array([100.031, 200.059]), np.array([100.01, 10.01])
    assert encode_data_line(3, mzs, ints, decimals=2) == '3|100.03 200.06|100.01 10.01'


def test_encode_coord_line():
    assert encode_coord_line(99, 500, 100) == '99,500,100'
    assert encode_coord_line(-99, -500, -100) == '-99,-500,-100'


@patch('engine.imzml_txt_converter.ImzMLParser')
def test_imzml_txt_converter_parse_save_spectrum(MockImzMLParser, sm_config, ds_config):
    mock_parser = MockImzMLParser.return_value
    mock_parser.coordinates = [[1, 1], [1, 2]]
    mock_parser.getspectrum.side_effect = [(np.array([100., 200.]), np.array([100., 10.])),
                                           (np.array([100., 200.]), np.array([100., 10.]))]

    converter = ImzmlTxtConverter(sm_config, ds_config, '', '', '')
    converter.parser = mock_parser
    converter.txt_file = StringIO()
    converter.coord_file = StringIO()

    for i, (x, y) in enumerate(mock_parser.coordinates):
        converter.parse_save_spectrum(i, x, y)

    sp_lines = converter.txt_file.getvalue().split('\n')
    assert sp_lines[0] == '0|100.0 200.0|100.0 10.0'
    assert sp_lines[1] == '1|100.0 200.0|100.0 10.0'

    coord_lines = converter.coord_file.getvalue().split('\n')
    assert coord_lines[0] == '0,1,1'
    assert coord_lines[1] == '1,1,2'
