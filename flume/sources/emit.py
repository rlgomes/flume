"""
emit source
"""

import time
import sched

from flume import moment, node, Point


class emit(node):

    name = 'emit'

    MAX_BUFFER = 1024

    def __init__(self,
                 limit=-1,
                 every='1s',
                 points=None,
                 start=None,
                 end=moment.end()):

        node.__init__(self,
                      limit=limit,
                      every=every,
                      points=points,
                      start=start,
                      end=end)
        self.limit = limit
        self.every = every
        self.start = moment.date(start) if start is not None else None
        self.end = moment.date(end)

        if points is None:
            self.points = None
        else:
            self.points = []

            for elem in points:
                point = Point(**elem)

                if 'time' in point:
                    point.time = moment.date(point.time)

                self.points.append(point)

    def loop(self):
        current_time = None

        if self.points is not None:
            self.push(self.points)

        else:
            count = 0

            if self.start is not None and self.start < moment.now():
                # emit the historical points first
                current_time = self.start
                buffered = []

                while current_time < moment.now():
                    count += 1

                    # done when we reach the limit
                    if self.limit != -1 and count > self.limit:
                        break

                    point = Point(time=current_time)
                    buffered.append(point)

                    if len(buffered) > emit.MAX_BUFFER:
                        self.push(buffered)
                        buffered = []

                    every = moment.duration(self.every, current_time)
                    current_time += every

                if len(buffered) > 0:
                    self.push(buffered)
                    buffered = []

            if moment.now() < self.end and count < self.limit:
                # continue into real time
                scheduler = sched.scheduler(time.time, time.sleep)
                every = moment.duration(self.every)
                every_seconds = every.total_seconds()

                if current_time is None:
                    if self.start is not None:
                        current_time = self.start
                    else:
                        current_time = moment.now()

                def push_point(current_time, count):
                    """
                    internal push point function
                    """
                    point = Point(time=current_time)
                    self.push([point])

                    count += 1
                    current_time += every

                    # done when we reach the limit
                    if self.limit != -1 and count >= self.limit:
                        return

                    # done when we've passed the `end`
                    if point.time > self.end:
                        return

                    scheduler.enter(every_seconds,
                                    1,
                                    push_point,
                                    (current_time, count))
            
                scheduler.enter(every_seconds,
                                1,
                                push_point,
                                (current_time, count))
                scheduler.run()
