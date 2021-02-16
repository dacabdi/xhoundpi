import unittest
from xhoundpi.config import setup_configparser

class test_config(unittest.TestCase):

    def test_config_defaults(self):
        parser = setup_configparser()
        config = parser.parse('')
        self.assertEqual(config.config, 'xhoundpi.conf')
        self.assertEqual(config.log, 'xhoundpi.log')
        self.assertFalse(config.verbose)

    def test_config_cli_overrides_long_version(self):
        parser = setup_configparser()
        config = parser.parse('--verbose --config /etc/xhound/xhound.conf --log /var/log/xhound.log', config_file_contents='')
        self.assertEqual(config.config, '/etc/xhound/xhound.conf')
        self.assertEqual(config.log, '/var/log/xhound.log')
        self.assertTrue(config.verbose)

    def test_config_overrides_allsources(self):
        parser = setup_configparser()
        config = parser.parse('--log somelogfile.log', config_file_contents='verbose=no', env_vars={'XHOUNDPI_CONFIG': 'config.conf'})
        self.assertEqual(config.config, 'config.conf')
        self.assertEqual(config.log, 'somelogfile.log')
        self.assertFalse(config.verbose)

    def test_config_source_superseding(self):
        parser = setup_configparser()
        config = parser.parse(
            '--log log_cli.log',
            config_file_contents='log=log_file.log verbose=true config=config_file.conf'.replace(' ', '\n'),
            env_vars={'XHOUNDPI_LOG': 'log_env.log', 'XHOUNDPI_CONFIG': 'config_env.conf'})
        self.assertEqual(config.config, 'config_env.conf')
        self.assertEqual(config.log, 'log_cli.log')
        self.assertTrue(config.verbose)