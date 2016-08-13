"""
gnuplot unit tests
"""
import unittest
import mock

from bunch import Bunch
from robber import expect

from flume.sinks.views import Gnuplot
from flume import moment


class GnuplotTest(unittest.TestCase):

    @mock.patch('tempfile.mkdtemp')
    @mock.patch('blessings.Terminal')
    @mock.patch('subprocess.Popen')
    @mock.patch('flume.sinks.views.Gnuplot.write')
    def test_can_render_a_simple_barchart_with_dumb_terminal(self,
                                                             mock_write,
                                                             mock_popen,
                                                             mock_terminal,
                                                             mock_mkdtemp):
        mock_mkdtemp.return_value = '/tmp'
        mock_terminal.return_value = Bunch(width=100, height=50)

        view = Gnuplot()
        view.render('barchart', {
            '2016': [('January', 10), ('Febuary', 20), ('April', 5)]
        })

        expect(mock_write.call_args_list).to.eq([
            mock.call('set terminal dumb size 100, 50\n'),
            # 25 comes from 20 * 1.25 we're doing 25% padding of the y value height
            mock.call('set yrange [0:25]\n'),
            # default 0.8 boxwidth
            mock.call('set boxwidth 0.8\n'),
            # default fill style
            mock.call('set style fill solid\n'),
            mock.call('set style data histogram\n'),
            mock.call('set style histogram cluster gap 1\n'),
            mock.call('plot "/tmp/2016.dat" using 2:xtic(1) title "2016"\n')
        ])


    @mock.patch('tempfile.mkdtemp')
    @mock.patch('blessings.Terminal')
    @mock.patch('subprocess.Popen')
    @mock.patch('flume.sinks.views.Gnuplot.write')
    def test_can_render_a_simple_linechart_with_dumb_terminal(self,
                                                              mock_write,
                                                              mock_popen,
                                                              mock_terminal,
                                                              mock_mkdtemp):
        mock_mkdtemp.return_value = '/tmp'
        mock_terminal.return_value = Bunch(width=100, height=50)

        view = Gnuplot()
        view.render('linechart', {
            'series1': [('0', 10), ('1', 20), ('2', 5)]
        })

        expect(mock_write.call_args_list).to.eq([
            mock.call('set terminal dumb size 100, 50\n'),
            # 25 comes from 20 * 1.25 we're doing 25% padding of the y value height
            mock.call('set yrange [0:25]\n'),
            mock.call('plot "/tmp/series1.dat" using 1:2 with linespoints title "series1"\n')
        ])


    @mock.patch('tempfile.mkdtemp')
    @mock.patch('blessings.Terminal')
    @mock.patch('subprocess.Popen')
    @mock.patch('flume.sinks.views.Gnuplot.write')
    def test_can_render_a_simple_timechart_with_dumb_terminal(self,
                                                              mock_write,
                                                              mock_popen,
                                                              mock_terminal,
                                                              mock_mkdtemp):
        mock_mkdtemp.return_value = '/tmp'
        mock_terminal.return_value = Bunch(width=100, height=50)

        view = Gnuplot()
        view.render('timechart', {
            'series1': [
                (moment.date('2016-01-01T00:00:00.000Z'), 10),
                (moment.date('2016-01-01T00:00:01.000Z'), 20),
                (moment.date('2016-01-01T00:00:02.000Z'), 5)
            ]
        })

        expect(mock_write.call_args_list).to.eq([
            mock.call('set terminal dumb size 100, 50\n'),
            # 25 comes from 20 * 1.25 we're doing 25% padding of the y value height
            mock.call('set yrange [0:25]\n'),
            mock.call('set xdata time\n'),
            mock.call('set format x "%Y/%d/%m-%H:%M:%S"\n'),
            mock.call('set timefmt "%Y/%d/%m-%H:%M:%S"\n'),
            mock.call('plot "/tmp/series1.dat" using 1:2 with linespoints title "series1"\n')
        ])

    @mock.patch('tempfile.mkdtemp')
    @mock.patch('blessings.Terminal')
    @mock.patch('subprocess.Popen')
    @mock.patch('flume.sinks.views.Gnuplot.write')
    def test_can_call_render_multiple_times_for_a_simple_barchart_with_dumb_terminal(self,
                                                                                     mock_write,
                                                                                     mock_popen,
                                                                                     mock_terminal,
                                                                                     mock_mkdtemp):
        mock_mkdtemp.return_value = '/tmp'
        mock_terminal.return_value = Bunch(width=100, height=50)

        view = Gnuplot()
        view.render('barchart', {
            '2016': [('January', 10), ('Febuary', 20), ('April', 5)]
        })

        view.render('barchart', {
            '2016': [('January', 10), ('Febuary', 10), ('April', 10)]
        })

        expect(mock_write.call_args_list).to.eq([
            mock.call('set terminal dumb size 100, 50\n'),
            # 25 comes from 20 * 1.25 we're doing 25% padding of the y value height
            mock.call('set yrange [0:25]\n'),
            # default 0.8 boxwidth
            mock.call('set boxwidth 0.8\n'),
            # default fill style
            mock.call('set style fill solid\n'),
            mock.call('set style data histogram\n'),
            mock.call('set style histogram cluster gap 1\n'),
            mock.call('plot "/tmp/2016.dat" using 2:xtic(1) title "2016"\n'),
            mock.call('exit\n'),
            mock.call('set terminal dumb size 100, 50\n'),
            # 25 comes from 20 * 1.25 we're doing 25% padding of the y value height
            mock.call('set yrange [0:12.5]\n'),
            # default 0.8 boxwidth
            mock.call('set boxwidth 0.8\n'),
            # default fill style
            mock.call('set style fill solid\n'),
            mock.call('set style data histogram\n'),
            mock.call('set style histogram cluster gap 1\n'),
            mock.call('plot "/tmp/2016.dat" using 2:xtic(1) title "2016"\n')
        ])


    @mock.patch('tempfile.mkdtemp')
    @mock.patch('subprocess.Popen')
    @mock.patch('flume.sinks.views.Gnuplot.write')
    def test_can_render_a_simple_barchart_with_x11_terminal(self,
                                                            mock_write,
                                                            mock_popen,
                                                            mock_mkdtemp):
        mock_mkdtemp.return_value = '/tmp'

        view = Gnuplot(terminal='x11')
        view.render('barchart', {
            '2016': [('January', 10), ('Febuary', 20), ('April', 5)]
        })

        expect(mock_write.call_args_list).to.eq([
            mock.call('clear\n'),
            mock.call('set terminal x11 size 1280, 1024\n'),
            # 25 comes from 20 * 1.25 we're doing 25% padding of the y value height
            mock.call('set yrange [0:25]\n'),
            # default 0.8 boxwidth
            mock.call('set boxwidth 0.8\n'),
            # default fill style
            mock.call('set style fill solid\n'),
            mock.call('set style data histogram\n'),
            mock.call('set style histogram cluster gap 1\n'),
            mock.call('plot "/tmp/2016.dat" using 2:xtic(1) title "2016"\n')
        ])


    @mock.patch('tempfile.mkdtemp')
    @mock.patch('subprocess.Popen')
    @mock.patch('flume.sinks.views.Gnuplot.write')
    def test_can_render_a_simple_linechart_with_x11_terminal(self,
                                                             mock_write,
                                                             mock_popen,
                                                             mock_mkdtemp):
        mock_mkdtemp.return_value = '/tmp'

        view = Gnuplot(terminal='x11')
        view.render('linechart', {
            'series1': [('0', 10), ('1', 20), ('2', 5)]
        })

        expect(mock_write.call_args_list).to.eq([
            mock.call('clear\n'),
            mock.call('set terminal x11 size 1280, 1024\n'),
            # 25 comes from 20 * 1.25 we're doing 25% padding of the y value height
            mock.call('set yrange [0:25]\n'),
            mock.call('plot "/tmp/series1.dat" using 1:2 with linespoints title "series1"\n')
        ])


    @mock.patch('tempfile.mkdtemp')
    @mock.patch('subprocess.Popen')
    @mock.patch('flume.sinks.views.Gnuplot.write')
    def test_can_render_a_simple_timechart_with_x11_terminal(self,
                                                             mock_write,
                                                             mock_popen,
                                                             mock_mkdtemp):
        mock_mkdtemp.return_value = '/tmp'

        view = Gnuplot(terminal='x11')
        view.render('timechart', {
            'series1': [
                (moment.date('2016-01-01T00:00:00.000Z'), 10),
                (moment.date('2016-01-01T00:00:01.000Z'), 20),
                (moment.date('2016-01-01T00:00:02.000Z'), 5)
            ]
        })

        expect(mock_write.call_args_list).to.eq([
            mock.call('clear\n'),
            mock.call('set terminal x11 size 1280, 1024\n'),
            # 25 comes from 20 * 1.25 we're doing 25% padding of the y value height
            mock.call('set yrange [0:25]\n'),
            mock.call('set xdata time\n'),
            mock.call('set format x "%Y/%d/%m-%H:%M:%S"\n'),
            mock.call('set timefmt "%Y/%d/%m-%H:%M:%S"\n'),
            mock.call('plot "/tmp/series1.dat" using 1:2 with linespoints title "series1"\n')
        ])

    @mock.patch('tempfile.mkdtemp')
    @mock.patch('subprocess.Popen')
    @mock.patch('flume.sinks.views.Gnuplot.write')
    def test_can_call_render_multiple_times_for_a_simple_barchart_with_x11_terminal(self,
                                                                                    mock_write,
                                                                                    mock_popen,
                                                                                    mock_mkdtemp):
        mock_mkdtemp.return_value = '/tmp'

        view = Gnuplot(terminal='x11')
        view.render('barchart', {
            '2016': [('January', 10), ('Febuary', 20), ('April', 5)]
        })

        view.render('barchart', {
            '2016': [('January', 10), ('Febuary', 10), ('April', 10)]
        })

        expect(mock_write.call_args_list).to.eq([
            mock.call('clear\n'),
            mock.call('set terminal x11 size 1280, 1024\n'),
            # 25 comes from 20 * 1.25 we're doing 25% padding of the y value height
            mock.call('set yrange [0:25]\n'),
            # default 0.8 boxwidth
            mock.call('set boxwidth 0.8\n'),
            # default fill style
            mock.call('set style fill solid\n'),
            mock.call('set style data histogram\n'),
            mock.call('set style histogram cluster gap 1\n'),
            mock.call('plot "/tmp/2016.dat" using 2:xtic(1) title "2016"\n'),
            mock.call('clear\n'),
            mock.call('set terminal x11 size 1280, 1024\n'),
            # 25 comes from 20 * 1.25 we're doing 25% padding of the y value height
            mock.call('set yrange [0:12.5]\n'),
            # default 0.8 boxwidth
            mock.call('set boxwidth 0.8\n'),
            # default fill style
            mock.call('set style fill solid\n'),
            mock.call('set style data histogram\n'),
            mock.call('set style histogram cluster gap 1\n'),
            mock.call('plot "/tmp/2016.dat" using 2:xtic(1) title "2016"\n')
        ])
