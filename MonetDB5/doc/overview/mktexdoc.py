# The contents of this file are subject to the MonetDB Public
# License Version 1.0 (the "License"); you may not use this file
# except in compliance with the License. You may obtain a copy of
# the License at
# http://monetdb.cwi.nl/Legal/MonetDBLicense-1.0.html
# 
# Software distributed under the License is distributed on an "AS
# IS" basis, WITHOUT WARRANTY OF ANY KIND, either express or
# implied. See the License for the specific language governing
# rights and limitations under the License.
# 
# The Original Code is the Monet Database System.
# 
# The Initial Developer of the Original Code is CWI.
# Portions created by CWI are Copyright (C) 1997-2004 CWI.
# All Rights Reserved.
# 
# Contributor(s):
# 		Martin Kersten <Martin.Kersten@cwi.nl>
# 		Peter Boncz <Peter.Boncz@cwi.nl>
# 		Niels Nes <Niels.Nes@cwi.nl>
# 		Stefan Manegold  <Stefan.Manegold@cwi.nl>

import sys, os, string

if len(sys.argv) != 3:
    print '''\
Usage: %s srcdir dstdir

where srcdir is the top of the MonetDB source directory tree, and
dstdir is the top of the installation tree.''' % sys.argv[0]
    sys.exit(1)

doctype= 'tex'
srcdir = sys.argv[1]
dstdir = sys.argv[2]

# Here a hack to make this work on Windows:
# The command name cannot have any spaces, not even quoted, so we
# can't use (as we used to) os.path.join(dstdir, 'bin', 'Mx') for the
# value of mx.  Instead we add the bin directory to the beginning of
# the command search path.  We assume there is a PATH in the
# environment, but that doesn't seem like to big an assumption.
os.environ['PATH'] = os.path.join(dstdir, 'bin') + os.pathsep + os.environ['PATH']
mx = 'Mx'

# figure out a place for temporary files
import tempfile
tmpdir = tempfile.gettempdir()

def copyfile(srcfile, dstfile):
    print 'copyfile', srcfile, dstfile
    f = open(srcfile, 'rb')
    data = f.read()
    f.close()
    f = open(dstfile, 'wb')
    f.write(data)
    f.close()

def unlink(file):
    try:
        os.unlink(file)
    except os.error:
        pass

def runMx(srcdir, base, dstdir, suffix='' ):
    print 'runMx', srcdir, base, dstdir
    cwd = os.getcwd()
    print cwd, '->', srcdir
    os.chdir(srcdir)
    cmd = '%s "-R%s" -H1 -t -B "%s" 2>&1' % (mx, tmpdir, base + '.mx')
    print cmd
    f = os.popen(cmd, 'r')
    dummy = f.read()                    # discard output
    f.close()
    print srcdir, '->', cwd
    os.chdir(cwd)
    srcfile = os.path.join(tmpdir, base + '.body.'+doctype)
    if not os.path.exists(srcfile):
        srcfile = os.path.join(tmpdir, base + '.' + doctype)
    if not os.path.exists(dstdir):
        os.makedirs(dstdir)
    copyfile(srcfile, os.path.join(dstdir, base + '.' +doctype))
    unlink(os.path.join(tmpdir, base + '.' + doctype))

def removedir(dir):
    """Remove DIR recursively."""
    print 'removedir',dir
    if not os.path.exists(dir):
        return
    names = os.listdir(dir)
    for name in names:
        fn = os.path.join(dir, name)
        if os.path.isdir(fn):
            removedir(fn)
        else:
            os.remove(fn)
    os.rmdir(dir)

removedir(os.path.join(dstdir, 'doc'))

#for f in ['monet', 'mil', 'mel']:
#    runMx(os.path.join(srcdir, 'doc'), f, os.path.join(dstdir, 'doc', ''Services'))

#for f in ['monet.gif']:
#   d = string.split(f,'.')[0]
#   copyfile(os.path.join(srcdir, 'doc', f),
#            os.path.join(dstdir, 'doc', 'Services', d, f))


runMx(os.path.join(srcdir, 'src', 'gdk'), 'gdk',
  os.path.join(dstdir, 'doc', 'Services'))
for f in ['bat.gif', 'bat1.gif', 'bat2.gif']:
   copyfile(os.path.join(srcdir, 'src', 'gdk', f),
            os.path.join(dstdir, 'doc', 'Services', f))

#these files should be linked
for f in ['mal_atom',
    'mal_box',
    'mal_client',
    'mal_debugger',
    'mal_function',
    'mal_import',
    'mal_instruction',
    'mal_interpreter',
    'mal_linker',
    'mal',
    'mal_namespace',
    'mal_optimizer',
    'mal_parser',
    'mal_profiler',
    'mal_properties',
    'mal_resolve',
    'mal_scenario',
    'mal_scope',
    'mal_session',
    'mal_stack',
    'mal_startup',
    'mal_type',
    'mal_xml',
	]:
    runMx(os.path.join(srcdir, 'src', 'mal'), f,
          os.path.join(dstdir, 'doc', 'MAL'))

#these GDK files should be linked
for f in ['gdk',
    'gdk_align',
	]:
    runMx(os.path.join(srcdir, 'src', 'gdk'), f,
          os.path.join(dstdir, 'doc', 'GDK'))

runMx(os.path.join(srcdir, 'src', 'tools'), 'Mserver',
      os.path.join(dstdir, 'doc', 'tools'))

# client documentation
runMx(os.path.join(srcdir, 'src', 'mapi', 'clients', 'C'), 'Mapi',
      os.path.join(dstdir, 'doc', 'APIs'), 'C')

runMx(os.path.join(srcdir, 'src', 'mapi', 'clients', 'C'), 'MapiClient',
      os.path.join(dstdir, 'doc', 'tools'))


#for f in ['aggrX3', 'aggr', 'alarm', 'algebra', 'arith', 'ascii_io', 'bat',
#          'blob', 'counters', 'decimal', 'enum', 'kernel',
#          'lock', 'mmath', 'monettime', 'pcl', 'radix', 'streams', 'str', 'sys',
#          'tcpip', 'trans', 'unix', 'url', 'xtables']:
#    runMx(os.path.join(srcdir, 'src', 'modules', 'plain'), f,
#          os.path.join(dstdir, 'doc', 'www', 'Modules'))

#for f in ['HowToStart', 'HowToStart-Win32.txt']:
#    copyfile(os.path.join(srcdir, f),
#             os.path.join(dstdir, 'doc', 'www', f))

