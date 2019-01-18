import threading
from networktables import NetworkTables

class ConnectTable(object):

    def __init__(self, **kwargs):

        tableName = kwargs.get('tableName', 'SmartDashboard')
        server = kwargs.get('server', '10.55.49.2')

        cond = threading.Condition()
        notified = [False]
        self.Connected = False

        def connectionListener(connected, info):
            print(info, '; Connected=%s' % connected)
            with cond:
                notified[0] = True
                cond.notify()

        NetworkTables.initialize(server='10.55.49.2')
        NetworkTables.addConnectionListener(connectionListener, immediateNotify=True)

        with cond:
            print("Waiting")
            if not notified[0]:
                cond.wait()
            else:
                self.Connected = True

        print("Connected!")

        self.Table = NetworkTables.getTable(tableName)