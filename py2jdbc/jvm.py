# -*- coding: utf8 -*-
import os
from platform import machine
import sys
from ctypes.util import find_library

platform = sys.platform
CP_SEP = ';' if platform == 'win32' else ':'

if platform == 'win32':
    try:
        # noinspection PyUnresolvedReferences
        import _winreg as winreg
    except ImportError:
        # noinspection PyUnresolvedReferences
        import winreg

mach = machine()
proc = {
    'x86_64': 'amd64',
    'i786': 'i386',
    'ia64': 'i64',
}.get(mach, mach)

libfile = {
    'darwin': 'libjvm.jnilib',
    'win32': 'jvm.dll',
}.get(platform, 'libjvm.so')


def find_libfile(path):
    """
    Given a path, look for a JVM dynamic link library
    file recursing down directories.

    :param path: the root path to start searching.
    :return: the full path to the JVM dyanmic link library or None if not found
    """
    path = os.path.realpath(path)
    for root, _, names in os.walk(path):
        if libfile in names:
            return os.path.join(root, libfile)


def find_libjvm():
    """
    Search for the JVM dyanmic link library using various methods

    :return: a full path to a JVM dynamic link library or raise RuntimeError
        if not found.
    """
    # first, try the ctypes utility
    path = find_library('jvm')
    if path:
        return path

    # try a PY2JDBC_JAVA_HOME environment variable
    py2jdbc_home = os.getenv('PY2JDBC_JAVA_HOME')
    if py2jdbc_home and os.path.exists(py2jdbc_home):
        path = find_libfile(py2jdbc_home)
        if path:
            return path

    # try the JAVA_HOME environment variable
    java_home = os.getenv('JAVA_HOME')
    if java_home and os.path.exists(java_home):
        path = find_libfile(java_home)
        if path:
            return path

    # try the JDK_HOME environment variable
    jdk_home = os.getenv('JDK_HOME')
    if jdk_home and os.path.exists(jdk_home):
        path = find_libfile(jdk_home)
        if path:
            return path

    if platform == 'darwin':
        # I've been told this works on most iOS systems
        path = find_libfile('/System/Library/Frameworks/JavaVM.framework/Libraries')
        if path:
            return path
    elif platform == 'win32':
        # On Windows, look for the current version of JRE installed.
        with winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r'SOFTWARE\JavaSoft\Java Runtime Environment'
        ) as jre_key:
            version = winreg.QueryValueEx(jre_key, 'CurrentVersion')[0]
            with winreg.OpenKey(jre_key, version) as version_key:
                path = winreg.QueryValueEx(version_key, 'RuntimeLib')[0]
                if path:
                    return path
    else:   # linux?
        # search some common locations
        for root in ('/usr/lib/jvm', '/usr/java'):
            if not os.path.exists(root):
                continue
            for child in sorted(os.listdir(root)):
                path = os.path.realpath(os.path.join(root, child))
                if not os.path.isdir(path):
                    continue
            root = os.path.realpath(root)
            path = find_libfile(root)
            if path:
                # look for a reasonable path
                for java_name in ('jre', 'jdk', 'java'):
                    if '/{java_name}/lib/{proc}/'.format(
                        java_name=java_name,
                        proc=proc
                    ) in path:
                        return path


def get_classpath(*paths):
    """
    Generate a reasonable default Java classpath.

    :param paths: paths to search (if directory) or append (if file)
    :return: a platform appropriate classpath
    """
    cp = os.getenv('CLASSPATH')
    cp = cp.split(CP_SEP) if cp else []
    for path in paths:
        if os.path.isdir(path):
            for fn in os.listdir(path):
                fn = os.path.realpath(os.path.join(path, fn))
                if os.path.isfile(fn) and fn.endswith('.jar'):
                    cp.append(fn)
        elif os.path.isfile(path):
            cp.append(path)
    return CP_SEP.join(cp)
