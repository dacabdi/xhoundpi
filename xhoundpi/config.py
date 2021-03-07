"""Configuration parser and provider"""

import configargparse

def setup_configparser() -> configargparse.ArgumentParser:
    """Sets up the configuration parser, provides command usage, etc."""
    parser = configargparse.Parser(
        auto_env_var_prefix="XHOUNDPI_",
        add_config_file_help=False,)
    parser.add('--config', metavar='FILE', default='xhoundpi.conf', dest='config',
        is_config_file=True, env_var="XHOUNDPI_CONFIG", help='config file path')
    parser.add('--log', default='xhoundpi.log', dest='log', metavar='FILE',
        help='logs file path')
    parser.add('--verbose', dest='verbose', action='store_true',
        help='verbose logging execution')
    parser.add('--buffer-capacity', dest='buffer_capacity', type=int,
        help='internal buffers capacity limit')
    parser.add('--mock-gnss', dest='mock_gnss', action='store_true',
        help='mock gnss message io')
    parser.add('--gnss-mock-input', default="data/gnss_mock_input.hex", dest='gnss_mock_input',
        type=str,help='input file for gnss mock serial data')
    parser.add('--gnss-mock-output', default="data/gnss_mock_output.hex", dest='gnss_mock_output',
        type=str, help='output file for gnss mock serial data')
    return parser
