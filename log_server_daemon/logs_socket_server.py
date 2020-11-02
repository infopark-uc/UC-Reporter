import pickle
import logging
import logging.handlers
import socketserver
import struct


class LogRecordStreamHandler(socketserver.StreamRequestHandler):
    """Handler for a streaming logging request.

    This basically logs the record using whatever logging policy is
    configured locally.
    """

    def handle(self):
        """
        Handle multiple requests - each expected to be a 4-byte length,
        followed by the LogRecord in pickle format. Logs the record
        according to whatever policy is configured locally.
        """
        while True:
            chunk = self.connection.recv(4)
            if len(chunk) < 4:
                break
            slen = struct.unpack('>L', chunk)[0]
            chunk = self.connection.recv(slen)
            while len(chunk) < slen:
                chunk = chunk + self.connection.recv(slen - len(chunk))
            obj = self.unPickle(chunk)
            record = logging.makeLogRecord(obj)
            self.handleLogRecord(record)

    def unPickle(self, data):
        return pickle.loads(data)

    def handleLogRecord(self, record):

        UCREPORTER_LOG_FILE_SIZE = 2048000
        UCREPORTER_LOG_FILE_COUNT = 5

        # if a name is specified, we use the named logger rather than the one
        # implied by the record.
        if record.name is not None:
            loggerName = record.name
        elif self.server.logname is not None:
            loggerName = self.server.logname
        else:
            loggerName = record.module
        logger = logging.getLogger(loggerName)
        # N.B. EVERY record gets logged. This is because Logger.handle
        # is normally called AFTER logger-level filtering. If you want
        # to do filtering, do it at the client end to save wasting
        # cycles and network bandwidth!

        if len(logger.handlers) > 0:

            console_output = "handlers are already exists in Logger " + loggerName
            print(loggerName + ": " + console_output)
            logger.debug(console_output)

        else:
            console_output = "no any handlers in Logger " + loggerName + " - create new one"
            print(loggerName + ": " + console_output)

            rotate_file_handler = logging.handlers.RotatingFileHandler("../logs/" + loggerName + ".log",
                                                                            maxBytes=UCREPORTER_LOG_FILE_SIZE,
                                                                            backupCount=UCREPORTER_LOG_FILE_COUNT)
            #rotate_file_handler.setLevel(logging.DEBUG)
            formatter = logging.Formatter('%(asctime)s %(name)s - %(levelname)s: %(message)s')
            rotate_file_handler.setFormatter(formatter)
            logger.addHandler(rotate_file_handler)

            syslog_handler = logging.handlers.SysLogHandler(facility="local5")
            logger.addHandler(syslog_handler)

            logger.info(console_output)
            console_output = "New handler was created in Logger " + loggerName
            print(loggerName + ": " + console_output)
            logger.info(console_output)

        logger.handle(record)

class LogRecordSocketReceiver(socketserver.ThreadingTCPServer):
    """
    Simple TCP socket-based logging receiver suitable for testing.
    """

    allow_reuse_address = True

    def __init__(self, host='localhost',
                 port=logging.handlers.DEFAULT_TCP_LOGGING_PORT,
                 handler=LogRecordStreamHandler):
        socketserver.ThreadingTCPServer.__init__(self, (host, port), handler)
        self.abort = 0
        self.timeout = 1
        self.logname = None

    def serve_until_stopped(self):
        import select
        abort = 0
        while not abort:
            rd, wr, ex = select.select([self.socket.fileno()],
                                       [], [],
                                       self.timeout)
            if rd:
                self.handle_request()
            abort = self.abort

def main():
    logging.basicConfig(
        format='%(relativeCreated)5d %(name)-15s %(levelname)-8s %(message)s')
    tcpserver = LogRecordSocketReceiver()
    print('About to start TCP server...')
    tcpserver.serve_until_stopped()

if __name__ == '__main__':
    main()