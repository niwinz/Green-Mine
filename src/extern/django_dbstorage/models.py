from errno import EBADF
import os

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from StringIO import _complain_ifclosed

from django.conf import settings
from django.db import models

from django_dbstorage.fields import Base64Field


__all__ = ['File']

class FileManager(models.Manager):
    def open(self, name, mode):
        f = self.get(name=name)
        f.mode = mode
        return f


class File(models.Model):
    """Model for treating rows in the database as file streams."""

    name = models.CharField(max_length=getattr(settings, 'PATH_MAX', 100),
                            primary_key=True, editable=False)
    data = Base64Field(blank=True, editable=False)
    size = models.PositiveIntegerField(editable=False)

    objects = FileManager()

    def __init__(self, *args, **kwargs):
        mode = kwargs.pop('mode', 'r+b')
        super(File, self).__init__(*args, **kwargs)
        self._closed = False
        self._file = StringIO()
        self._file.write(self.data)
        self._file.seek(0)
        self.encoding = None
        self.errors = None
        self.mode = mode
        self.newlines = None
        self.softspace = 0

    def __unicode__(self):
        output = '%r, mode %r' % (self.name, self.mode)
        if self.closed:
            output = 'closed ' + output
        return output

    def __iter__(self):
        return self

    def next(self):
        _complain_ifclosed(self.closed)
        r = self._file.readline()
        if not r:
            raise StopIteration
        return r

    def open(self, mode=None):
        """open([mode]) -> None. """
        if self._file is None:
            raise ValueError("The file cannot be reopened.")
        self._closed = False
        self._file.seek(0)
        if mode:
            self.mode = mode

    def close(self):
        """close() -> None.  Flushes and releases resources held."""
        if not self.closed:
            if not self._isreadonly():
                self.flush()
            self._closed = True

    def _get_closed(self):
        return self._closed or self._file is None
    closed = property(_get_closed)

    def isatty(self):
        """isatty() -> False."""
        _complain_ifclosed(self.closed)
        return False

    def seek(self, offset, whence=0):
        """
        seek(offset[, whence]) -> None.  Move to new file position.

        Argument offset is a byte count.  Optional argument whence defaults to
        0 (offset from start of file, offset should be >= 0); other values are 1
        (move relative to current position, positive or negative), and 2 (move
        relative to end of file, usually negative, but allows seeking beyond
        the end of a file).
        """
        _complain_ifclosed(self.closed)
        return self._file.seek(offset, whence)

    def tell(self):
        """
        tell() -> current file position, an integer (may be a long integer).
        """
        _complain_ifclosed(self.closed)
        return self._file.tell()

    def read(self, size=-1):
        """read([size]) -> read at most size bytes, returned as a string."""
        _complain_ifclosed(self.closed)
        return self._file.read(size)

    def readline(self):
        """readline() -> next line from the file, as a string."""
        _complain_ifclosed(self.closed)
        return self._file.readline()

    def readlines(self):
        """readlines() -> list of strings, each a line from the file."""
        _complain_ifclosed(self.closed)
        return self._file.readlines()

    def truncate(self, size=None):
        """
        truncate([size]) -> None.  Truncate the file to at most size bytes.

        Size defaults to the current file position, as returned by tell().
        """
        _complain_ifclosed(self.closed)
        _complain_ifreadonly(self._isreadonly())
        position = self._file.tell()
        try:
            if size is not None:
                self._file.seek(size)
            return self._file.truncate()
        finally:
            self._file.seek(position)

    def write(self, str):
        """
        write(str) -> None.  Write string str to file.

        Note that due to buffering, flush() or close() are needed before
        the database reflects the data written.
        """
        _complain_ifclosed(self.closed)
        _complain_ifreadonly(self._isreadonly())
        return self._file.write(str)

    def writelines(self, iterable):
        """
        writelines(iterable) -> None.  Write the iterable of strings to file.

        Note that newlines are not added.  This is equalivalent to calling
        write() for each string in the iterable.
        """
        _complain_ifclosed(self.closed)
        _complain_ifreadonly(self._isreadonly())
        return self._file.writelines(iterable)

    def flush(self):
        """flush() -> None.  Flush the internal I/O buffer."""
        _complain_ifclosed(self.closed)
        _complain_ifreadonly(self._isreadonly())
        self.save()

    def save_base(self, *args, **kwargs):
        self.data = self._file.getvalue()
        self.size = self._size()
        super(File, self).save_base(*args, **kwargs)

    def _size(self):
        """_size() -> current file size, an integer (may be a long integer)."""
        position = self._file.tell()
        try:
            self._file.seek(0, 2)
            return self._file.tell()
        finally:
            self._file.seek(position)

    def _isreadonly(self):
        """_isreadonly() -> true or false.  True if mode is readonly."""
        return not ('+' in self.mode or 'w' in self.mode or 'a' in self.mode)


def _complain_ifreadonly(readonly):
    if readonly:
        raise IOError(EBADF, os.strerror(EBADF))
