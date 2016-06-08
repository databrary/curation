import psycopg2

class DB(object):
    _conn = None
    _cur = None

    def __init__(self, host, database, user, password, port):
        self._host = host
        self._database = database
        self._user = user
        self._password = password
        self._port = port
        self._conn = psycopg2.connect(host=self._host, database=self._database, user=self._user, password=self._password, port=self._port)
        self._cur = self._conn.cursor()

    def __del__(self):
        return self._conn.close()

    def query(self, query, params=None):
        '''returns results whole'''
        self._cur.execute(query, params)
        return self._cur.fetchall()

    def querytocsv(self, query, outputfile, params=None):
        '''returns results to a specified csv file'''
        output = "COPY ({0}) TO STDOUT WITH CSV HEADER".format(query)
        with open(outputfile, 'w') as f:
            self._cur.copy_expert(output, f)
