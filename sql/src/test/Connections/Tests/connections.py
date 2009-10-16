import os, time, sys
from MonetDBtesting import process

def remote_server_start(x,s):
    sys.stdout.write('\nserver %d%d\n' % (x,s))
    sys.stderr.write('\nserver %d%d\n' % (x,s))
    sys.stderr.flush()
    sys.stderr.write('#remote mserver\n')
    sys.stdout.flush()
    sys.stderr.flush()
    port = os.getenv('MAPIPORT', '50000')
    srv = process.server('sql', mapiport = int(port) + 1,
                         dbname = '%s_test1' % os.getenv('TSTDB'),
                         stdin = process.PIPE)
    time.sleep(5)                      # give server time to start
    return srv

def server_start(x,s):
    sys.stdout.write('\nserver %d%d\n' % (x,s))
    sys.stderr.write('\nserver %d%d\n' % (x,s))
    sys.stderr.flush()
    sys.stderr.write('#mserver\n')
    sys.stdout.flush()
    sys.stderr.flush()
    srv = process.server('sql', stdin = process.PIPE)
    time.sleep(5)                      # give server time to start
    return srv

def server_stop(srv):
    srv.communicate()

def client_load_file(clt, port, file):
    f = open(file, 'r')
    for line in f:
        line = line.replace('port_num5', str(port+2))
        line = line.replace('port_num', str(port+1))
        clt.stdin.write(line)
    f.close()


def client(x,s, c, file):
    sys.stdout.write('\nserver %d%d, client %d\n' % (x,s,c))
    sys.stderr.write('\nserver %d%d, client %d\n' % (x,s,c))
    sys.stderr.flush()
    sys.stderr.write('#client%d\n' % x)
    sys.stdout.flush()
    sys.stderr.flush()
    clt = process.client('sql', stdin = process.PIPE)
    port = int(os.getenv('MAPIPORT', '50000'))
    client_load_file(clt, port, file)
    clt.communicate()


def clients(x):
    s = 0
    s += 1; srv = server_start(x,s)
    s += 1; remote_srv = remote_server_start(x,s)
    c = 0
    c += 1; client(x, s, c, os.path.join(os.getenv('RELSRCDIR'), '..', 'connections_syntax.sql'))
    c += 1; client(x, s, c, os.path.join(os.getenv('RELSRCDIR'), '..', 'connections_semantic.sql'))
    c += 1; client(x, s, c, os.path.join(os.getenv('RELSRCDIR'), '..', 'connections_default_values.sql'))
    server_stop(remote_srv)
    server_stop(srv)

def main():
    x = 0
    x += 1; clients(x)

main()
