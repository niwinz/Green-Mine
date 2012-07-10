# -*- coding: utf-8 -*-

GM_SCRUM_STATES = {
    'open': {
        'name': 'Open',
        'is_finished': False,
        'task_states': [
            ('open', 'Open'),
        ]
    },
    'progress': {
        'name': 'In progress',
        'is_finished': False,
        'task_states': [
            ('progress', 'In progress'),
            ('needs_info', 'Needs info'),
            ('posponed', 'Posponed'),
        ]
    },
    'completed': {
        'name': 'Ready for test',
        'is_finished': True,
        'task_states': [
            ('completed', 'Ready for test'),
            ('workaround', 'Workaround'),
        ]
    },
    'closed': {
        'name': 'Closed',
        'is_finished': True,
        'task_states': [
            ('closed', 'Closed'),
        ]
    },
}
