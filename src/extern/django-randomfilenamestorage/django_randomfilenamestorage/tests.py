from __future__ import with_statement

from contextlib import contextmanager

import errno
import os
import posixpath
import re
import shutil
import stat
import warnings

try:
    from warnings import catch_warnings
except ImportError:
    def catch_warnings():
        original_filters = warnings.filters
        try:
            yield
        finally:
            warnings.filters = original_filters

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import TemporaryUploadedFile
from django.test import TestCase
from django.utils.functional import LazyObject

import django_randomfilenamestorage.storage
from django_randomfilenamestorage.storage import (
    RandomFilenameMetaStorage, RandomFilenameFileSystemStorage,
    SafeFileSystemStorage, DEFAULT_LENGTH
)


class StubStorage(object):
    def __init__(self, tries=1):
        self._exists_count = 0
        self._tries = tries

    def exists(self, *args, **kwargs):
        # Return False until exists() has been called *tries* times.
        self._exists_count += 1
        return self._exists_count < self._tries


class StubSafeStorage(StubStorage):
    def __init__(self, uniquify_names=False, *args, **kwargs):
        # Support uniquify_names as an argument
        self._save_count = 0
        super(StubSafeStorage, self).__init__(*args, **kwargs)

    def _save(self, name, *args, **kwargs):
        # Raise errno.EEXIST until _save() has been called *tries* times.
        self._save_count += 1
        if self._save_count < self._tries:
            raise OSError(errno.EEXIST, os.strerror(errno.EEXIST))
        return name


class StubBrokenStorage(StubStorage):
    def _save(self, *args, **kwargs):
        raise OSError(errno.ENOENT, os.strerror(errno.ENOENT))


def stub_random_string(*args, **kwargs):
    stub_random_string.count += 1
    return str(stub_random_string.count)


class RandomFilenameTestCase(TestCase):
    def assertFilename(self, name, original, length=DEFAULT_LENGTH):
        dirname, pathname = posixpath.split(original)
        if dirname:
            dirname += posixpath.sep
        root, ext = posixpath.splitext(pathname)
        regexp = re.compile(r'%s[0-9a-z]{%d}%s$' % (re.escape(dirname),
                                                    length,
                                                    re.escape(ext)))
        self.assertTrue(regexp.match(name), '%r is invalid.' % name)

    def test_class(self):
        StorageClass = RandomFilenameMetaStorage(storage_class=StubStorage)
        with patch(settings, RANDOM_FILENAME_LENGTH=NotImplemented):
            storage = StorageClass()
            self.assertFilename(storage.get_available_name(''), '')
        StorageClass = RandomFilenameMetaStorage(storage_class=StubStorage,
                                                 length=5)
        with patch(settings, RANDOM_FILENAME_LENGTH=NotImplemented):
            storage = StorageClass()
            self.assertFilename(storage.get_available_name(''), '', length=5)
            storage = StorageClass(randomfilename_length=10)
            self.assertFilename(storage.get_available_name(''), '', length=10)

    def test_init(self):
        StorageClass = RandomFilenameMetaStorage(storage_class=StubStorage)
        with patch(settings, RANDOM_FILENAME_LENGTH=NotImplemented):
            storage = StorageClass()
            self.assertFilename(storage.get_available_name(''), '')
            storage = StorageClass(randomfilename_length=10)
            self.assertFilename(storage.get_available_name(''), '', length=10)
        with patch(settings, RANDOM_FILENAME_LENGTH=5):
            storage = StorageClass()
            self.assertFilename(storage.get_available_name(''), '', length=5)
            storage = StorageClass(randomfilename_length=20)
            self.assertFilename(storage.get_available_name(''), '', length=20)

    def test_get_available_name(self):
        with media_root():
            storage = RandomFilenameFileSystemStorage(
                randomfilename_length=DEFAULT_LENGTH
            )
            self.assertFilename(storage.get_available_name(''), '')
            self.assertFilename(storage.get_available_name('foo'), 'foo')
            self.assertFilename(storage.get_available_name('foo.txt'),
                                'foo.txt')
            self.assertFilename(storage.get_available_name('foo/bar'),
                                'foo/bar')
            self.assertFilename(storage.get_available_name('foo/bar.txt'),
                                'foo/bar.txt')

    def test_get_available_name_retry(self):
        # With retries
        StorageClass = RandomFilenameMetaStorage(storage_class=StubStorage)
        storage = StorageClass(tries=2)
        stub_random_string.count = 0
        with patch(django_randomfilenamestorage.storage,
                   random_string=stub_random_string):
            self.assertEqual(storage.get_available_name('name.txt'), '2.txt')

        # Without retries
        StorageClass = RandomFilenameMetaStorage(storage_class=StubStorage)
        storage = StorageClass(tries=2)
        stub_random_string.count = 0
        with patch(django_randomfilenamestorage.storage,
                   random_string=stub_random_string):
            self.assertEqual(storage.get_available_name('name.txt',
                                                        retry=False),
                             '1.txt')

    def test_save(self):
        with media_root():
            storage = RandomFilenameFileSystemStorage(
                randomfilename_length=DEFAULT_LENGTH
            )
            name1 = storage.save('foo/bar.txt', ContentFile('Hello world!'))
            storage.delete(name1)
            self.assertFilename(name1, 'foo/bar.txt')
            name2 = storage.save('foo/bar.txt', ContentFile('Hello world!'))
            storage.delete(name2)
            self.assertFilename(name2, 'foo/bar.txt')
            self.assertNotEqual(name1, name2)

    def test_save_exception(self):
        with media_root():
            storage = RandomFilenameFileSystemStorage(
                randomfilename_length=DEFAULT_LENGTH
            )
            name = storage.save('foo/bar.txt', ContentFile('Hello world!'))
            self.assertRaises(IOError, storage.save,
                              name + posixpath.sep,
                              ContentFile('Hello world!'))

    def test_save_broken(self):
        StorageClass = RandomFilenameMetaStorage(
            storage_class=StubBrokenStorage
        )
        storage = StorageClass()
        self.assertRaises(OSError, storage._save, 'name.txt')

    def test_save_safe_storage(self):
        StorageClass = RandomFilenameMetaStorage(storage_class=StubSafeStorage)
        storage = StorageClass(tries=3)
        stub_random_string.count = 0
        with patch(django_randomfilenamestorage.storage,
                   random_string=stub_random_string):
            # stub_random_string() is called 4 times, when attempting
            # to save three times.
            self.assertEqual(storage._save('name.txt'), '2.txt')

    def test_save_no_uniquify(self):
        StorageClass = RandomFilenameMetaStorage(storage_class=StubSafeStorage,
                                                 uniquify_names=False)
        storage = StorageClass(tries=2)
        with patch(django_randomfilenamestorage.storage):
            self.assertRaises(OSError, storage._save, 'name.txt')

    def test_save_broken_retry(self):
        StorageClass = RandomFilenameMetaStorage(storage_class=StubSafeStorage)
        class BrokenStorage(StorageClass):
            def get_available_name(self, name):
                return super(BrokenStorage, self).get_available_name(name)

        storage = BrokenStorage(tries=3)
        stub_random_string.count = 0
        with patch(django_randomfilenamestorage.storage,
                   random_string=stub_random_string):
            with catch_warnings():
                warnings.simplefilter('ignore')
                # stub_random_string() is called four times, when attempting
                # to save three times
                self.assertEqual(storage._save('name.txt'), '4.txt')


class SafeFileSystemStorageTestCase(TestCase):
    def test_init(self):
        storage = SafeFileSystemStorage()
        self.assertTrue(storage.uniquify_names)
        storage = SafeFileSystemStorage(uniquify_names=True)
        self.assertTrue(storage.uniquify_names)
        storage = SafeFileSystemStorage(uniquify_names=False)
        self.assertFalse(storage.uniquify_names)

    def test_save(self):
        with media_root():
            storage = SafeFileSystemStorage()
            # Save one copy
            content = 'Hello world!'
            name = storage.save('hello.txt', ContentFile(content))
            self.assertEqual(name, 'hello.txt')
            self.assertEqual(open(storage.path(name)).read(), content)
            # Save another, which should be renamed
            content = 'Hello.'
            name = storage._save('hello.txt', ContentFile(content))
            self.assertTrue(name in ('hello_.txt', 'hello_1.txt'),
                            "%r is not 'hello_.txt' or 'hello_1.txt'" % name)
            self.assertEqual(open(storage.path(name)).read(), content)

    def test_save_no_uniquify(self):
        with media_root():
            storage = SafeFileSystemStorage(uniquify_names=False)
            # Save one copy
            content = 'Hello world!'
            name = storage.save('hello.txt', ContentFile(content))
            self.assertEqual(name, 'hello.txt')
            self.assertEqual(open(storage.path(name)).read(), content)
            # Save another, which should throw an exception
            content = 'Hello.'
            self.assertRaises(OSError,
                              storage._save, 'hello.txt', ContentFile(content))

    def test_save_tempfile(self):
        with media_root():
            storage = SafeFileSystemStorage()
            content = 'Hello world!'
            f = TemporaryUploadedFile(name='filename',
                                      content_type='text/plain',
                                      size=len(content),
                                      charset='utf-8')
            f.write(content)
            f.seek(0)
            name = storage.save('hello.txt', f)
            self.assertEqual(name, 'hello.txt')
            self.assertEqual(open(storage.path(name)).read(), content)

    def test_save_permissions(self):
        with media_root():
            with patch(settings, FILE_UPLOAD_PERMISSIONS=stat.S_IRUSR):
                storage = SafeFileSystemStorage()
                content = 'Hello world!'
                name = storage.save('hello.txt', ContentFile('Hello world!'))
                self.assertTrue(os.access(storage.path(name), os.R_OK))
                self.assertFalse(os.access(storage.path(name), os.W_OK))
                self.assertFalse(os.access(storage.path(name), os.X_OK))


@contextmanager
def patch(namespace, **values):
    """Patches `namespace`.`name` with `value` for (name, value) in values"""
    originals = {}
    if isinstance(namespace, LazyObject):
        if namespace._wrapped is None:
            namespace._setup()
        namespace = namespace._wrapped
    for (name, value) in values.iteritems():
        try:
            originals[name] = getattr(namespace, name)
        except AttributeError:
            originals[name] = NotImplemented
        if value is NotImplemented:
            if originals[name] is not NotImplemented:
                delattr(namespace, name)
        else:
            setattr(namespace, name, value)
    try:
        yield
    finally:
        for (name, original_value) in originals.iteritems():
            if original_value is NotImplemented:
                if values[name] is not NotImplemented:
                    delattr(namespace, name)
            else:
                setattr(namespace, name, original_value)


@contextmanager
def media_root(dirname='test_media/'):
    if os.path.exists(dirname):
        raise Exception('Cannot run tests safely, %r already exists!' %
                        dirname)
    try:
        with patch(settings, MEDIA_ROOT=dirname):
            yield
    finally:
        shutil.rmtree(dirname, ignore_errors=True)
