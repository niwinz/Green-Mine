Green-Mine
==========

Project management web application build on top of Django.

Currently there is no stable version, but the project is already usable. All contributions and bug fixes is welcome.

Features:
---------

* Multi project.
* Backlog view. (with user stories assignation drag & drop)
* Dashboard view. (with tasks drag & drop)
* Tasks / Bugs separate view.
* Wiki (now only supports markdown, but planned add suport to rst)
* Questions (simple formum like view for make questions to product owner)

Todo / Under development:
-------------------------

* Permission sistem based on simple roles (partialy implemented).
* Project export / import.
* RestructuredText for wiki.
* Product map grouped by categories (SCRUM)
* Higlight new changes introduced by product owner.
* Backlog story points visual limit.

Developers How-To:
------------------

As a first step, download the latest version of the repository and follow the instructions::
    
    git clone git://github.com/niwibe/Green-Mine.git greenmine
    cd greenmine/src
    python manage.py syncdb
    python manage.py loaddata initial_users

The ``initial_users`` fixture, by default inserts two users: ``andrei`` and ``juanfran``. These users
have superuser flag set to ``True`` and password is ``123123``.

For run tests::
    
    python manage.py test -v2 greenmine


Requirements:
-------------

Django is included in a git repository and all other requirements are listed on ``requirements.txt`` file.


License:
--------

BSD License. You can see full license text on ``LICENSE`` file.
