# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _

ORG_ROLE_CHOICES = (
    ('owner', _(u'Owner')),
    ('developer', _(u'Developer')),
)

MARKUP_TYPE = (
    ('md', _(u'Markdown')),
    ('rst', _('Restructured Text')),
)

US_STATUS_CHOICES = (
    ('open', _(u'New')),
    ('progress', _(u'In progress')),
    ('completed', _(u'Ready for test')),
    ('closed', _(u'Closed')),
)

TASK_PRIORITY_CHOICES = (
    (1, _(u'Low')),
    (3, _(u'Normal')),
    (5, _(u'High')),
)


TASK_TYPE_CHOICES = (
    ('bug', _(u'Bug')),
    ('task', _(u'Task')),
)

TASK_STATUS_CHOICES = US_STATUS_CHOICES + (
    ('workaround', _(u"Workaround")),
    ('needinfo', _(u"Needs info")),
    ('posponed', _(u"Posponed")),
)

POINTS_CHOICES = (
    (-1, u'?'),
    (0, u'0'),
    (-2, u'1/2'),
    (1, u'1'),
    (2, u'2'),
    (3, u'3'),
    (5, u'5'),
    (8, u'8'),
    (10, u'10'),
    (15, u'15'),
    (20, u'20'),
    (40, u'40'),
)


TASK_COMMENT = 1
TASK_STATUS_CHANGE = 2
TASK_PRIORITY_CHANGE = 3
TASK_ASSIGNATION_CHANGE = 4

TASK_CHANGE_CHOICES = (
    (TASK_COMMENT, _(u"Task comment")),
    (TASK_STATUS_CHANGE, _(u"Task status change")),
    (TASK_PRIORITY_CHANGE, _(u"Task prioriy change")),
    (TASK_ASSIGNATION_CHANGE, _(u"Task assignation change")),
)
