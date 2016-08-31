"""
base adapter class
"""

from flume import moment

class adapter(object):
    """
    Adapter base class used to define the required adapter methods
    """

    def read(self):
        """
        return a generator of points from this adapter
        """
        pass

    def write(self, points):
        """
        write the points provided through this adapter
        """
        pass

    def eof(self):
        """
        finalize any necessary things in the adapter (used only on write)
        """
        pass

    def optimize(self, child):
        """
        optimize is called before `read` even executes and gives the underlying
        adapter the ability to optimize certain downstream operations within the
        adapter's engine and remove those underlying nodes with
        `node.remove_node()` you can also traverse from this child downward by
        following the `.child`
        member.
        """
        pass

    def process_time_field(self, points, time_field):
        if time_field is None:
            time_field = 'time'

        for point in points:
            if time_field in point:
                point.time = moment.date(point[time_field])
                if time_field != 'time':
                    del point[time_field]

        return points
