from betdex.connection import BetDexConnection


class Endpoints:
    """
    Base for the endpoint groups: holds the ``Connection`` they send through.

    :param conn: Connection to send through.
    """

    def __init__(self, conn: BetDexConnection) -> None:
        """
        Create the group; see the class docstring for parameters.
        """
        self.conn = conn