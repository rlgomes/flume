"""
base adapter class
"""

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
