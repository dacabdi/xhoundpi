"""Configuration parser and provider"""

import configargparse

def setup_configparser() -> configargparse.ArgumentParser:
    """Sets up the configuration parser, provides command usage, etc."""
    parser = configargparse.Parser(
        auto_env_var_prefix="XHOUNDPI_",
        add_config_file_help=False,)
    parser.add('--config', metavar='FILE', default='xhoundpi.conf', dest='config',
        is_config_file=True, env_var="XHOUNDPI_CONFIG", help='config file path')
    parser.add('--log', default='xhoundpi.log', dest='log', metavar='FILE', help='logs file path')
    parser.add('--verbose', dest='verbose', action='store_true', help='verbose logging execution')
    parser.add('--buffer-capacity', dest='buffer_capacity', type=int, help='internal buffers capacity limit')
    return parser
