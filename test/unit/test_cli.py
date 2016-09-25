import json
import unittest


from flume import cli
from flume.exceptions import FlumeException
from test.unit.util import redirect
from robber import expect


class CLITest(unittest.TestCase):
    """
    verifies the CLI works as expected
    """

    def test_fails_when_executing_an_inexistent_method_flume_program(self):
        with redirect() as io:
            with self.assertRaisesRegexp(NameError,
                                         'name \'invalid\' is not defined'):
                cli.main(['invalid()'])

    def test_fails_when_given_invalid_adapter_name(self):
        with redirect() as io:
            with self.assertRaisesRegexp(FlumeException,
                                         '"foo" adapter not registered'):
                cli.main(['emit(limit=1) | write("foo")'])

    def test_executing_a_flume_program_that_writes(self):
        with redirect() as io:
            cli.main(['emit(limit=1, start="2016-01-01") | write("stdio")'])
            expect(io.exit).to.eq(0)
            expect(json.loads(io.stdout)).to.eq({
                'time': '2016-01-01T00:00:00.000Z'
            })

    def test_executing_a_flume_program_that_reads(self):
        with redirect(input='{"time": "2016-01-01T00:00:00.000Z"}\n') as io:
            cli.main(['read("stdio") | write("stdio")'])
            expect(io.exit).to.eq(0)
            expect(json.loads(io.stdout)).to.eq({
                'time': '2016-01-01T00:00:00.000Z'
            })

    def test_implicit_sink_can_be_none(self):
        with redirect() as io:
            cli.main(['--implicit-sink', 'None',
                      'read("stdio")'])
            expect(io.exit).to.eq(0)
            expect(io.stdout).to.eq('')

    def test_implicit_sink_can_be_changed(self):
        with redirect() as io:
            cli.main(['--implicit-sink', 'write("stdio", format="csv")',
                      'emit(limit=1,start="2016-01-01")'])
            expect(io.exit).to.eq(0)
            expect(io.stdout).to.eq('time\r\n' +
                                    '2016-01-01T00:00:00.000Z\r\n')

    def test_executing_a_flume_program_in_debug_mode(self):
        with redirect() as io:
            cli.main(['--implicit-sink', 'None',
                      '-d',
                      'emit(limit=1, start="2016-01-01")'])
            expect(io.exit).to.eq(0)
            expect(io.stdout).to.eq('')

        expect(io.stderr).to.match(
            '.* - DEBUG - <flume.sources.emit.emit object at .*> has started\n' +
            '.* - DEBUG - <flume.sources.emit.emit object at .*> pushing 1 points\n' +
            '.* - DEBUG - <flume.sources.emit.emit object at .*> is done\n' +
            '.* - DEBUG - <flume.sources.emit.emit object at .*> pushing 1 points\n')
