"""
reducer proc
"""

import copy

from flume import moment, node, Point, reducer
from flume import util


class reduce(node):

    name = 'reduce'

    def __init__(self,
                 every=moment.forever(),
                 reset=True,
                 by=None,
                 **fields):

        node.__init__(self,
                      every=every,
                      reset=reset,
                      **fields)

        self.every = every
        self.reset = reset

        if by is None:
            by = []

        self.by = by
        self.fields = fields

    def loop(self):
        results = {}
        fields = {}
        batch_start = None
        batch_end = None

        def init_results(results, fields, by_key, init_point, point):
            results[by_key] = init_point

            for by in self.by:
                results[by_key].set(by, point[by])

            if by_key not in fields:
                fields[by_key] = {}
                for (field, value) in self.fields.items():
                    fields[by_key][field] = copy.deepcopy(value)

        while self.running:
            points = self.pull()

            for point in points:
                by_key = ':'.join([util.u(point[by]) for by in self.by])

                if 'time' in point:
                    if batch_start is None:
                        batch_start = point.time

                        if self.every == moment.forever():
                            batch_end = moment.end()

                        else:
                            every = moment.duration(self.every, context=batch_start)
                            batch_end = batch_start + every

                        init_results(results, fields, by_key, Point(time=batch_start), point)

                    if point.time >= batch_end:
                        # lets make sure that we've had a single batch
                        # of data received and not multiple empty batches
                        gaps = int((point.time - batch_start).total_seconds()/every.total_seconds())

                        # if we reached the end of a batch then push
                        self.push(results.values())

                        # new batch
                        batch_start = batch_end
                        every = moment.duration(self.every, context=batch_start)
                        batch_end = batch_end + every

                        # XXX: to carry over any fields that were found in a
                        # batch but not found in a subsequent batch we should
                        # copy the existing results here to the new one

                        results = {}
                        init_results(results, fields, by_key, Point(time=batch_start), point)

                        # reset reducers
                        if self.reset:
                            for by_field_key in fields.keys():
                                for (_, value) in fields[by_field_key].items():
                                    if isinstance(value, reducer):
                                        value.reset()

                        if gaps > 1:
                            # generate empty batches since the last batch_start
                            for _ in range(1, gaps):
                                empty_results = {}
                                empty_fields = {}

                                for by_key in results:
                                    init_results(empty_results,
                                                 empty_fields,
                                                 by_key,
                                                 Point(time=batch_start),
                                                 point)

                                    fields_copy = fields[by_key].copy()
                                    for (key, value) in fields_copy.items():
                                        if isinstance(value, reducer):
                                            fields_copy[key] = value.result()

                                        else:
                                            fields_copy[key] = value

                                        empty_results[by_key][key] = fields_copy[key]

                                batch_start = batch_end
                                every = moment.duration(self.every, context=batch_start)
                                batch_end = batch_end + every

                                # if we reached the end of a batch then push
                                self.push(empty_results.values())

                            results = {}
                            init_results(results, fields, by_key, Point(time=batch_start), point)

                    if by_key not in results:
                        init_results(results, fields, by_key, Point(time=batch_start), point)

                else:
                    if by_key not in results:
                        init_results(results, fields, by_key, Point(), point)

                # update them reducers
                fields_copy = fields[by_key].copy()
                for (key, value) in fields_copy.items():
                    if isinstance(value, reducer):
                        value.update(point)
                        fields_copy[key] = value.result()

                    else:
                        if util.is_string(value):
                            fields_copy[key] = value.format(**point.json())

                        else:
                            fields_copy[key] = value

                    results[by_key][key] = fields_copy[key]

        self.push(results.values())
