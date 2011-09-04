from errno import EEXIST
import ntpath
import os
import posixpath
import random
import string
from warnings import warn

from django.conf import settings
from django.core.files.storage import (Storage, FileSystemStorage,
                                       locks, file_move_safe)


CHARACTERS = string.lowercase + string.digits
DEFAULT_LENGTH = 16


def random_string(length):
    return ''.join(random.choice(CHARACTERS) for i in xrange(length))


def RandomFilenameMetaStorage(storage_class, length=None, uniquify_names=True):
    class RandomFilenameStorage(storage_class):
        def __init__(self, *args, **kwargs):
            self.randomfilename_length = kwargs.pop('randomfilename_length',
                                                    length)
            if self.randomfilename_length is None:
                self.randomfilename_length = getattr(settings,
                                                     'RANDOM_FILENAME_LENGTH',
                                                     DEFAULT_LENGTH)
            # Do not uniquify filenames by default.
            self.randomfilename_uniquify_names = kwargs.pop('uniquify_names',
                                                            uniquify_names)
            # But still try to tell storage_class not to uniquify filenames.
            # This class will be the one that uniquifies.
            try:
                new_kwargs = dict(kwargs, uniquify_names=False)
                super(RandomFilenameStorage, self).__init__(*args,
                                                            **new_kwargs)
            except TypeError:
                super(RandomFilenameStorage, self).__init__(*args, **kwargs)

        def get_available_name(self, name, retry=True):
            # All directories have forward slashes, even on Windows
            name = name.replace(ntpath.sep, posixpath.sep)
            dir_name, file_name = posixpath.split(name)
            file_root, file_ext = posixpath.splitext(file_name)
            # If retry is True and the filename already exists, keep
            # on generating random filenames until the generated
            # filename doesn't exist.
            while True:
                file_prefix = random_string(self.randomfilename_length)
                # file_ext includes the dot.
                name = posixpath.join(dir_name, file_prefix + file_ext)
                if not retry or not self.exists(name):
                    return name

        def _save(self, name, *args, **kwargs):
            while True:
                try:
                    return super(RandomFilenameStorage, self)._save(name,
                                                                    *args,
                                                                    **kwargs)
                except OSError, e:
                    if e.errno == EEXIST:
                        # We have a safe storage layer
                        if not self.randomfilename_uniquify_names:
                            # A higher storage layer will rename
                            raise
                        # Attempt to get_available_name() without retrying.
                        try:
                            name = self.get_available_name(name,
                                                           retry=False)
                        except TypeError:
                            warn('Could not call get_available_name() '
                                 'on %r with retry=False' % self)
                            name = self.get_available_name(name)
                    else:
                        raise

    RandomFilenameStorage.__name__ = 'RandomFilename' + storage_class.__name__
    return RandomFilenameStorage


class SafeFileSystemStorage(FileSystemStorage):
    """
    Standard filesystem storage

    Supports *uniquify_names*, like other safe storage classes.

    Based on django.core.files.storage.FileSystemStorage.
    """
    def __init__(self, *args, **kwargs):
        self.uniquify_names = kwargs.pop('uniquify_names', True)
        super(SafeFileSystemStorage, self).__init__(*args, **kwargs)

    def _save(self, name, content):
        full_path = self.path(name)

        directory = os.path.dirname(full_path)
        if not os.path.exists(directory):
            os.makedirs(directory)
        elif not os.path.isdir(directory):
            raise IOError("%s exists and is not a directory." % directory)

        # There's a potential race condition between get_available_name and
        # saving the file; it's possible that two threads might return the
        # same name, at which point all sorts of fun happens. So we need to
        # try to create the file, but if it already exists we have to go back
        # to get_available_name() and try again.

        while True:
            try:
                # This file has a file path that we can move.
                if hasattr(content, 'temporary_file_path'):
                    file_move_safe(content.temporary_file_path(), full_path)
                    content.close()

                # This is a normal uploadedfile that we can stream.
                else:
                    # This fun binary flag incantation makes os.open throw an
                    # OSError if the file already exists before we open it.
                    fd = os.open(full_path,
                                 (os.O_WRONLY | os.O_CREAT | os.O_EXCL |
                                  getattr(os, 'O_BINARY', 0)))
                    try:
                        locks.lock(fd, locks.LOCK_EX)
                        for chunk in content.chunks():
                            os.write(fd, chunk)
                    finally:
                        locks.unlock(fd)
                        os.close(fd)
            except OSError, e:
                if e.errno == EEXIST:
                    # Ooops, the file exists. We need a new file name.
                    if not self.uniquify_names:
                        raise
                    name = self.get_available_name(name)
                    full_path = self.path(name)
                else:
                    raise
            else:
                # OK, the file save worked. Break out of the loop.
                break

        if settings.FILE_UPLOAD_PERMISSIONS is not None:
            os.chmod(full_path, settings.FILE_UPLOAD_PERMISSIONS)

        return name


RandomFilenameFileSystemStorage = RandomFilenameMetaStorage(
    storage_class=SafeFileSystemStorage,
)
