# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=line-too-long
# pylint: disable=invalid-name

import unittest
from xhoundpi.config import setup_configparser

class test_config(unittest.TestCase):

    def test_config_defaults(self):
        parser = setup_configparser()
        config = parser.parse('')
        self.assertEqual(config.config, 'xhoundpi.conf')
        self.assertEqual(config.buffer_capacity, 1000)
        self.assertEqual(config.log_config_file, 'logconf.yml')
        self.assertFalse(config.mock_gnss)
        self.assertEqual(config.gnss_mock_input, 'data/gnss_mock_input.hex')
        self.assertEqual(config.gnss_mock_output, 'data/gnss_mock_output.hex')
        self.assertEqual(config.metrics_logger_freq, 1)

    def test_config_cli_overrides_long_version(self):
        parser = setup_configparser()
        config = parser.parse(' '.join([
            '--config /etc/xhound/xhound.conf',
            '--buffer-capacity 10',
            '--mock-gnss',
            '--gnss-mock-input /tmp/gnss-mock-in.bin',
            '--gnss-mock-output /tmp/gnss-mock-out.bin',
            '--log-config-file configlog.yml',
            '--metrics-logger-freq 3',
            ]), config_file_contents='')
        self.assertEqual(config.config, '/etc/xhound/xhound.conf')
        self.assertEqual(config.buffer_capacity, 10)
        self.assertEqual(config.mock_gnss, True)
        self.assertEqual(config.gnss_mock_input, '/tmp/gnss-mock-in.bin')
        self.assertEqual(config.gnss_mock_output, '/tmp/gnss-mock-out.bin')
        self.assertEqual(config.log_config_file, 'configlog.yml')
        self.assertEqual(config.metrics_logger_freq, 3)

    def test_config_overrides_allsources(self):
        parser = setup_configparser()
        config = parser.parse('--gnss-mock-output /tmp/gnss-mock-in.bin', config_file_contents='log-config-file=configlog.yml', env_vars={'XHOUNDPI_CONFIG': 'config.conf'})
        self.assertEqual(config.config, 'config.conf')
        self.assertEqual(config.gnss_mock_output, '/tmp/gnss-mock-in.bin')
        self.assertEqual(config.log_config_file, 'configlog.yml')

    def test_config_source_superseding(self):
        parser = setup_configparser()
        config = parser.parse(
            '--gnss-mock-input gnss_in_cli.bin',
            config_file_contents='gnss-mock-input=gnss_in_config.bin log-config-file=configlog.yml config=config_file.conf'.replace(' ', '\n'),
            env_vars={'XHOUNDPI_GNSS_MOCK_INPUT': 'gnss_in_env.bin', 'XHOUNDPI_CONFIG': 'config_env.conf'})
        self.assertEqual(config.config, 'config_env.conf')
        self.assertEqual(config.gnss_mock_input, 'gnss_in_cli.bin')
        self.assertEqual(config.log_config_file, 'configlog.yml')
