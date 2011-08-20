from __future__ import with_statement

from contextlib import contextmanager
import errno
from StringIO import StringIO

from django.conf import settings
from django.test import TestCase
from django.template import loader
from django.utils.functional import LazyObject

from django_dbstorage import views
from django_dbstorage.models import File
from django_dbstorage.storage import (DatabaseStorage,
                                      NonUniquifyingDatabaseStorage)


class FileTestCase(TestCase):
    def setUp(self):
        File.objects.all().delete()

    def test_init(self):
        f = File(name='hello.txt')
        self.assertEqual(f.name, 'hello.txt')
        self.assertEqual(f.data, '')
        self.assertEqual(f.closed, False)
        self.assertEqual(f.encoding, None)
        self.assertEqual(f.errors, None)
        self.assertEqual(f.mode, 'r+b')
        self.assertEqual(f.newlines, None)
        self.assertEqual(f.softspace, 0)

    def test_create(self):
        f = File.objects.create(name='hello.txt')
        self.assertEqual(f.name, 'hello.txt')
        self.assertEqual(f.data, '')
        self.assertEqual(f.closed, False)
        self.assertEqual(f.encoding, None)
        self.assertEqual(f.errors, None)
        self.assertEqual(f.mode, 'r+b')
        self.assertEqual(f.newlines, None)
        self.assertEqual(f.softspace, 0)

    def test_get(self):
        File.objects.create(name='hello.txt', data='Hello world!')
        f = File.objects.get(name='hello.txt')
        self.assertEqual(f.data, 'Hello world!')

    def test_unicode(self):
        f = File.objects.create(name='hello.txt', data='Hello world!')
        self.assertEqual(repr(f), "<File: 'hello.txt', mode 'r+b'>")
        f.close()
        self.assertEqual(repr(f), "<File: closed 'hello.txt', mode 'r+b'>")

    def test_iter_next(self):
        data = ['Hello world!\n', 'Salut monde!\n']
        f = File.objects.create(name='hello.txt', data=''.join(data))
        for line, expected in zip(f, data):
            self.assertEqual(line, expected)

    def test_open(self):
        f = File.objects.create(name='hello.txt')
        self.assertFalse(f.closed)
        self.assertEqual(f.mode, 'r+b')
        # Reopen in the file in read-only mode
        f.open(mode='r')
        self.assertEqual(f.mode, 'r')
        # Reopen the file after moving the cursor
        f.seek(15)
        self.assertEqual(f.tell(), 15)
        f.open()
        self.assertEqual(f.mode, 'r')
        self.assertEqual(f.tell(), 0)
        # Reopen the file after closing
        f.close()
        self.assertTrue(f.closed)
        f.open()
        self.assertFalse(f.closed)
        # Attempt to reopen the file after seriously closing
        f.close()
        f._file = None
        self.assertRaises(ValueError, f.open)

    def test_close(self):
        f = File.objects.create(name='hello.txt')
        self.assertFalse(f.closed)
        f.close()
        self.assertTrue(f.closed)
        self.assertRaises(ValueError, f.isatty)
        self.assertRaises(ValueError, f.seek, 0)
        self.assertRaises(ValueError, f.tell)
        self.assertRaises(ValueError, f.read)
        self.assertRaises(ValueError, f.readline)
        self.assertRaises(ValueError, f.readlines)
        self.assertRaises(ValueError, f.truncate)
        self.assertRaises(ValueError, f.write, '')
        self.assertRaises(ValueError, f.writelines, [''])
        self.assertRaises(ValueError, f.flush)

    def test_isatty(self):
        f = File.objects.create(name='hello.txt')
        self.assertFalse(f.isatty())

    def test_seek_tell(self):
        f = File.objects.create(name='hello.txt', data='Hello world!')
        self.assertEqual(f.tell(), 0)
        f.seek(5)
        self.assertEqual(f.tell(), 5)
        f.seek(3, 1)
        self.assertEqual(f.tell(), 8)
        f.seek(0, 2)
        self.assertEqual(f.tell(), 12)
        f.seek(-2, 2)
        self.assertEqual(f.tell(), 10)

    def test_read(self):
        f = File.objects.create(name='hello.txt', data='Hello world!')
        self.assertEqual(f.read(1), 'H')
        self.assertEqual(f.read(), 'ello world!')

    def test_readline(self):
        f = File.objects.create(name='hello.txt',
                                data='Hello world!\nSalut monde!\n')
        self.assertEqual(f.readline(), 'Hello world!\n')
        self.assertEqual(f.readline(), 'Salut monde!\n')

    def test_readlines(self):
        f = File.objects.create(name='hello.txt',
                                data='Hello world!\nSalut monde!\n')
        self.assertEqual(f.readlines(), ['Hello world!\n',
                                         'Salut monde!\n'])

    def test_truncate(self):
        f = File.objects.create(name='hello.txt', data='Hello world!')
        self.assertEqual(f.read(5), 'Hello')
        f.truncate()
        self.assertEqual(f.read(), '')
        f.seek(0)
        self.assertEqual(f.read(), 'Hello')
        f.seek(10)
        f.truncate(1)
        self.assertEqual(f.tell(), 10)
        f.seek(0)
        self.assertEqual(f.read(), 'H')

    def test_write(self):
        f = File.objects.create(name='hello.txt')
        f.write('Hello ')
        f.write('world!\n')
        print >>f, 'Salut monde!'
        f.flush()
        self.assertEqual(f.data, 'Hello world!\nSalut monde!\n')

    def test_writelines(self):
        f = File.objects.create(name='hello.txt')
        f.writelines(['Hello world!\n', 'Salut monde!\n'])
        f.flush()
        self.assertEqual(f.data, 'Hello world!\nSalut monde!\n')

    def test_flush(self):
        f = File.objects.create(name='hello.txt',
                                data='Hello world!\n')
        f.seek(0, 2)
        print >>f, 'Salut monde!'
        f.flush()
        f = File.objects.get(name='hello.txt')
        self.assertEqual(f.read(), 'Hello world!\nSalut monde!\n')

    def test_size(self):
        f = File.objects.create(name='hello.txt', data='Hello world!')
        self.assertEqual(f._size(), 12)
        f.seek(5)
        f.truncate()
        self.assertEqual(f._size(), 5)

    def test_readonly(self):
        f = File.objects.create(name='hello.txt', data='Hello world!')
        f.mode = 'rb'
        self.assertFalse(f.isatty())
        self.assertEqual(f.tell(), 0)
        self.assertEqual(f.read(), 'Hello world!')
        f.seek(0)
        self.assertEqual(f.readline(), 'Hello world!')
        f.seek(0)
        self.assertEqual(f.readlines(), ['Hello world!'])
        self.assertRaises(IOError, f.truncate)
        self.assertRaises(IOError, f.write, '')
        self.assertRaises(IOError, f.writelines, [''])
        self.assertRaises(IOError, f.flush)


class DatabaseStorageTestCase(TestCase):
    def setUp(self):
        File.objects.all().delete()

    def test_init(self):
        s = DatabaseStorage()
        self.assertEqual(s.base_url, settings.MEDIA_URL)
        s = DatabaseStorage(base_url='/media/')
        self.assertEqual(s.base_url, '/media/')
        s = DatabaseStorage(base_url=None)
        self.assertEqual(s.base_url, None)
        s = DatabaseStorage()
        self.assertEqual(s.location, '')
        s = DatabaseStorage(location='media/')
        self.assertEqual(s.location, 'media/')

    def test_open(self):
        content = StringIO('Hello world!')
        s = DatabaseStorage()
        self.assertRaises(OSError, s.open, name='hello.txt')
        s.save(name='hello.txt', content=content)
        f = s.open(name='hello.txt')
        self.assertEqual(f.read(), content.getvalue())
        self.assertRaises(IOError, f.truncate)
        f = s.open(name='hello.txt', mode='r+b')
        self.assertEqual(f.read(), content.getvalue())
        f.truncate()

    def test_save(self):
        content = StringIO('Hello world!')
        s = DatabaseStorage()
        self.assertRaises(OSError, s.save, name='', content=content)
        self.assertRaises(OSError, s.save, name='/', content=content)
        self.assertRaises(OSError, s.save, name='hello/', content=content)
        self.assertEqual(s.save(name='hello.txt', content=content),
                         'hello.txt')
        self.assertEqual(s.save(name='hello.txt', content=content),
                         'hello_1.txt')
        self.assertEqual(s.save(name='/hello.txt', content=content),
                         'hello_2.txt')
        # Do not allow the storage layer to retry, if not unique.
        self.assertEqual(s._save(name='hello.txt', content=content),
                         'hello_3.txt')
        self.assertEqual(s.save(name='/hello/goodbye.txt', content=content),
                         'hello/goodbye.txt')
        # Try to save hello.txt, but without uniquify_names
        s = DatabaseStorage(uniquify_names=False)
        self.assertRaises(OSError, s._save, name='hello.txt', content=content)
        try:
            s._save(name='hello.txt', content=content)
        except OSError, e:
            self.assertEqual(e.errno, errno.EEXIST)

    def test_get_available_name(self):
        content = StringIO('Hello world!')
        s = DatabaseStorage()
        self.assertEqual(s.get_available_name('hello.txt'), 'hello.txt')
        s.save(name='hello.txt', content=content)
        self.assertEqual(s.get_available_name('hello.txt'), 'hello_1.txt')

    def test_delete(self):
        content = StringIO('Hello world!')
        s = DatabaseStorage()
        s.delete('hello.txt')
        s.save(name='hello.txt', content=content)
        s.delete('hello.txt')
        self.assertFalse(s.exists('hello.txt'))

    def test_exists(self):
        content = StringIO('Hello world!')
        s = DatabaseStorage()
        self.assertFalse(s.exists('hello.txt'))
        s.save(name='hello.txt', content=content)
        self.assertTrue(s.exists('hello.txt'))

    def test_listdir(self):
        content = StringIO('')
        english = StringIO('Hello world!')
        french = StringIO('Salut monde!')
        s = DatabaseStorage()
        self.assertEqual(s.listdir(''), ([], []))
        self.assertEqual(s.listdir('/'), ([], []))
        s.save(name='hello.txt', content=english)
        s.save(name='salut.txt', content=french)
        self.assertEqual(s.listdir(''), ([], ['hello.txt', 'salut.txt']))
        self.assertEqual(s.listdir('/'), ([], ['hello.txt', 'salut.txt']))
        s.save(name='hello/en.txt', content=english)
        s.save(name='hello/fr.txt', content=french)
        s.save(name='hello/docs/README', content=content)
        self.assertEqual(s.listdir(''), (['hello'],
                                         ['hello.txt', 'salut.txt']))
        self.assertEqual(s.listdir('/'), (['hello'],
                                          ['hello.txt', 'salut.txt']))
        self.assertEqual(s.listdir('hello'), (['docs'], ['en.txt', 'fr.txt']))
        self.assertEqual(s.listdir('/hello'), (['docs'], ['en.txt', 'fr.txt']))
        self.assertEqual(s.listdir('hello/docs'), ([], ['README']))
        self.assertEqual(s.listdir('/hello/docs'), ([], ['README']))
        self.assertRaises(OSError, s.listdir, 'goodbye')
        self.assertRaises(OSError, s.listdir, '/goodbye')

    def test_name(self):
        s = DatabaseStorage()
        self.assertEqual(s._name(''), '')
        self.assertEqual(s._name('.'), '')
        self.assertEqual(s._name('/'), '')
        self.assertEqual(s._name('//'), '')
        self.assertEqual(s._name('hello'), 'hello')
        self.assertEqual(s._name('/hello'), 'hello')
        self.assertEqual(s._name('//hello'), 'hello')
        self.assertEqual(s._name('hello/'), 'hello/')
        self.assertEqual(s._name('hello//'), 'hello/')
        self.assertEqual(s._name('hello/goodbye'), 'hello/goodbye')
        self.assertEqual(s._name('hello//goodbye'), 'hello/goodbye')

    def test_name_location(self):
        s = DatabaseStorage(location='root')
        self.assertEqual(s._name(''), 'root/')
        self.assertEqual(s._name('.'), 'root/')
        self.assertEqual(s._name('hello.txt'), 'root/hello.txt')
        self.assertEqual(s._name('/hello.txt'), 'root/hello.txt')
        self.assertEqual(s._name('hello/'), 'root/hello/')
        s = DatabaseStorage(location='root/')
        self.assertEqual(s._name(''), 'root/')
        self.assertEqual(s._name('.'), 'root/')
        self.assertEqual(s._name('hello.txt'), 'root/hello.txt')
        self.assertEqual(s._name('/hello.txt'), 'root/hello.txt')
        self.assertEqual(s._name('hello/'), 'root/hello/')
        s = DatabaseStorage(location='/root/')
        self.assertEqual(s._name(''), 'root/')
        self.assertEqual(s._name('.'), 'root/')
        self.assertEqual(s._name('hello.txt'), 'root/hello.txt')
        self.assertEqual(s._name('/hello.txt'), 'root/hello.txt')
        self.assertEqual(s._name('hello/'), 'root/hello/')

    def test_size(self):
        content = StringIO('Hello world!')
        s = DatabaseStorage()
        self.assertRaises(OSError, s.size, name='hello.txt')
        s.save(name='hello.txt', content=content)
        self.assertEqual(s.size(name='hello.txt'), len(content.getvalue()))

    def test_url(self):
        s = DatabaseStorage()
        s.base_url = None
        self.assertRaises(ValueError, s.url, name='hello.txt')
        s = DatabaseStorage(base_url='/media/')
        self.assertEqual(s.url(name='hello.txt'), '/media/hello.txt')
        self.assertEqual(s.url(name='/hello.txt'), '/hello.txt')

    def test_set_location(self):
        s = DatabaseStorage()
        self.assertEqual(s.location, '')
        s.set_location(None)
        self.assertEqual(s.location, '')
        s.set_location('')
        self.assertEqual(s.location, '')
        s.set_location('/')
        self.assertEqual(s.location, '')
        s.set_location('root')
        self.assertEqual(s.location, 'root/')
        s.set_location('root/')
        self.assertEqual(s.location, 'root/')
        s.set_location('root//')
        self.assertEqual(s.location, 'root/')
        s.set_location('/root/')
        self.assertEqual(s.location, 'root/')


class NonUniquifyingDatabaseStorageTestCase(TestCase):
    def setUp(self):
        File.objects.all().delete()

    def test_save(self):
        content = StringIO('Hello world!')
        s = NonUniquifyingDatabaseStorage()
        self.assertEqual(s._save(name='hello.txt', content=content),
                         'hello.txt')
        self.assertRaises(OSError, s._save, name='hello.txt', content=content)
        try:
            s._save(name='hello.txt', content=content)
        except OSError, e:
            self.assertEqual(e.errno, errno.EEXIST)


class ViewsTestCase(TestCase):
    urls = 'django_dbstorage.test_urls'

    def create(self, filename, content):
        f = StringIO(content)
        self.storage = DatabaseStorage()
        self.storage.save(name=filename, content=f)

    def assertRedirect(self, response, location):
        self.assertEqual(response.status_code, 301, response.content)
        self.assertEqual(response['Location'], location)

    def test_is_dir(self):
        self.assertTrue(views.is_dir(''))
        self.assertTrue(views.is_dir('.'))
        self.assertTrue(views.is_dir('..'))
        self.assertTrue(views.is_dir('/'))
        self.assertTrue(views.is_dir('dir/'))
        self.assertFalse(views.is_dir('file'))

    def _validate_path(self, path):
        class request:
            pass
        request.path = '/root/' + path
        return views.validate_path(request, path)

    def test_validate_path(self):
        self.assertEqual(self._validate_path(''), '')
        self.assertEqual(self._validate_path('hello%20world'), 'hello world')
        self.assertRedirect(self._validate_path('./hello%20world'),
                            '/root/hello%20world')
        self.assertRedirect(self._validate_path('.'), '/root/')
        self.assertRedirect(self._validate_path('/'), '/root/')
        self.assertRedirect(self._validate_path('./'), '/root/')
        self.assertEqual(self._validate_path('dir/'), 'dir/')
        self.assertEqual(self._validate_path('file'), 'file')
        self.assertRedirect(self._validate_path('dir/.'), '/root/dir/')
        self.assertRedirect(self._validate_path('dir/../DIR/'), '/root/DIR/')
        self.assertRedirect(self._validate_path('dir/../dir/..'), '/root/')
        self.assertRedirect(self._validate_path('../dir/'), '/dir/')
        self.assertRedirect(self._validate_path('../../dir/'), '/dir/')

    def test_urls(self):
        self.create('hello.txt', 'Hello')
        response = self.client.get('/urls/hello.txt')
        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.content, 'Hello')
        self.assertEqual(response['Content-Type'], 'text/plain')

    def test_urls_redirect(self):
        self.create('hello.txt', 'Hello')
        response = self.client.get('/urls/dir/../hello.txt')
        self.assertEqual(response.status_code, 301, response.content)
        self.assertEqual(response['Location'],
                         'http://testserver/urls/hello.txt')

    def test_urls_404(self):
        response = self.client.get('/urls/404')
        self.assertEqual(response.status_code, 404, response.content)

    def test_urls_index(self):
        response = self.client.get('/urls/')
        self.assertEqual(response.status_code, 404, response.content)

    def test_serve(self):
        self.create('hello.txt', 'Hello')
        response = self.client.get('/serve/hello.txt')
        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.content, 'Hello')
        self.assertEqual(response['Content-Type'], 'text/plain')

    def test_serve_404(self):
        response = self.client.get('/serve/404')
        self.assertEqual(response.status_code, 404, response.content)

    def test_serve_index(self):
        response = self.client.get('/serve/')
        self.assertEqual(response.status_code, 404, response.content)

    def test_indexes(self):
        self.create('hello.txt', 'Hello')
        with disable_templates():
            response = self.client.get('/indexes/')
        self.assertEqual(response.status_code, 200, response.content)
        self.assertContains(response, 'hello.txt')

    def test_indexes_subdir(self):
        self.create('hello/world.txt', 'Hello world')
        with disable_templates():
            response = self.client.get('/indexes/')
        self.assertEqual(response.status_code, 200, response.content)
        self.assertContains(response, 'hello')
        response = self.client.get('/indexes/hello')
        self.assertEqual(response.status_code, 404, response.content)
        with disable_templates():
            response = self.client.get('/indexes/hello/')
        self.assertEqual(response.status_code, 200, response.content)
        self.assertContains(response, 'world.txt')

    def test_indexes_404(self):
        response = self.client.get('/indexes/hello/')
        self.assertEqual(response.status_code, 404, response.content)

    def test_root_exists(self):
        self.create('root/hello.txt', 'Hello')
        response = self.client.get('/root/hello.txt')
        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.content, 'Hello')
        self.assertEqual(response['Content-Type'], 'text/plain')

    def test_root_404(self):
        self.create('hello.txt', 'Hello')
        response = self.client.get('/root/hello.txt')
        self.assertEqual(response.status_code, 404, response.content)

    def test_root_indexes(self):
        self.create('root/hello.txt', 'Hello')
        with disable_templates():
            response = self.client.get('/root/')
        self.assertEqual(response.status_code, 200, response.content)
        self.assertContains(response, 'hello.txt')


@contextmanager
def disable_templates():
    """Disables TEMPLATE_LOADERS and user-defined templates."""
    with patch(loader, template_source_loaders=None):
        with patch(settings, TEMPLATE_LOADERS=[]):
            yield


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
