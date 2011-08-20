from errno import EEXIST, EISDIR, ENOENT, ENOTDIR
import itertools
import os
import posixpath
try:
    set
except NameError:
    from sets import Set as set
import urlparse

from django.conf import settings
from django.core.files.storage import Storage
from django.db import IntegrityError

from django_dbstorage.models import File


class DatabaseStorage(Storage):
    def __init__(self, location=None, base_url=settings.MEDIA_URL,
                 uniquify_names=True):
        self.set_location(location)
        self.base_url = base_url
        self.uniquify_names = uniquify_names

    def _open(self, name, mode='rb'):
        name = self._name(name)
        try:
            return File.objects.open(name=name, mode=mode)
        except File.DoesNotExist:
            raise OSError(ENOENT, os.strerror(ENOENT))

    def _save(self, name, content):
        name = self._name(name)
        if name.endswith(posixpath.sep):
            raise OSError(EISDIR, os.strerror(EISDIR))
        if not name:
            raise OSError(ENOENT, os.strerror(ENOENT))
        # Extract the data from content
        data = content.read()
        # Save to the database.
        while True:
            try:
                File.objects.create(name=posixpath.normpath(name), data=data)
            except IntegrityError:
                # File exists. We need a new file name.
                if not self.uniquify_names:
                    raise OSError(EEXIST, os.strerror(EEXIST))
                name = self.get_available_name(name)
            else:
                # OK, the file save worked. Break out of the loop.
                break
        return name

    def get_available_name(self, name):
        """
        Returns a filename that's free on the target storage system, and
        available for new content to be written to.
        """
        name = self._name(name)
        dir_name, file_name = posixpath.split(name)
        file_root, file_ext = os.path.splitext(file_name)
        # If the filename already exists, add an underscore and a number (before
        # the file extension, if one exists) to the filename until the generated
        # filename doesn't exist.
        count = itertools.count(1)
        while self.exists(name):
            # file_ext includes the dot.
            name = os.path.join(dir_name, "%s_%s%s" %
                                (file_root, count.next(), file_ext))
        return name

    def delete(self, name):
        """
        Deletes the specified file from the storage system.
        """
        name = self._name(name)
        File.objects.filter(name=name).delete()

    def exists(self, name):
        """
        Returns True if a file referened by the given name already exists in the
        storage system, or False if the name is available for a new file.
        """
        name = self._name(name)
        return bool(File.objects.filter(name=name).count())

    def listdir(self, path):
        """
        Lists the contents of the specified path, returning a 2-tuple of lists;
        the first item being directories, the second item being files.
        """
        path = self._name(path)
        if path and not path.endswith(posixpath.sep):
            path += posixpath.sep
        directories, files = set(), []
        entries = File.objects.filter(name__startswith=path)
        entries = entries.values_list('name', flat=True)
        if not entries and path:
            # Pretend empty directories don't exist, except for the root.
            raise OSError(ENOTDIR, os.strerror(ENOTDIR))
        for entry in entries:
            entry = entry[len(path):]
            bits = entry.split(posixpath.sep)
            if len(bits) == 1:
                files.append(bits[0])
            else:
                directories.add(bits[0])
        # Sort the directories and files
        directories = list(directories)
        directories.sort()
        files.sort()
        return directories, files

    def _name(self, name):
        name = name.lstrip(os.path.sep)
        new_name = os.path.normpath(name)
        if new_name == os.path.curdir:
            new_name = ''
        if self.location:
            new_name = os.path.join(self.location, new_name)
        if name.endswith(os.path.sep):
            # Preserve trailing slash for directories.
            new_name += os.path.sep
        # Convert os.path.sep into posixpath.sep
        new_name.replace(os.path.sep, posixpath.sep)
        return new_name

    def size(self, name):
        """
        Returns the total size, in bytes, of the file specified by name.
        """
        return self._open(name).size

    def url(self, name):
        """
        Returns an absolute URL where the file's contents can be accessed
        directly by a web browser.
        """
        if self.base_url is None:
            raise ValueError("This file is not accessible via a URL.")
        return urlparse.urljoin(self.base_url, name).replace('\\', '/')

    def set_location(self, location):
        if location:
            location = os.path.normpath(location).strip(os.path.sep)
            location = location.replace(os.path.sep, posixpath.sep)
        if not location:
            location = ''
        else:
            location += posixpath.sep
        self.location = location


class NonUniquifyingDatabaseStorage(DatabaseStorage):
    def __init__(self, location=None, base_url=None):
        return super(NonUniquifyingDatabaseStorage, self).__init__(
            location=location, base_url=base_url, uniquify_names=False
        )
