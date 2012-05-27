# -*- coding: utf-8 -*-

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from greenmine.models import Profile, UserStory, Task, ProjectUserRole
from django.utils import timezone

@receiver(post_save, sender=User)
def user_post_save(sender, instance, created, **kwargs):
    """Create void user profile if instance is a new user. """
    if created and not Profile.objects.filter(user=instance).exists():
        Profile.objects.create(user=instance)


#@receiver(post_save, sender=UserStory)
#def us_post_save(sender, instance, created, **kwargs):
#    if created:
#        task = Task.objects.create(
#            subject = instance.subject,
#            description = instance.description,
#            owner = instance.owner,
#            milestone = instance.milestone,
#            project = instance.project,
#            user_story = instance,
#        )


@receiver(post_save, sender=Task)
def task_post_save(sender, instance, created, **kwargs):
    if instance.user_story:
        instance.user_story.modified_date = timezone.now()
        instance.user_story.save()


from greenmine.utils import normalize_tagname

@receiver(post_save, sender=UserStory)
def user_story_post_save(sender, instance, created, **kwargs):
    """
    Auto update meta_category_list on project instance for
    performance improvements.
    """

    if not instance.category or not instance.category.strip():
        return

    # TODO: remove accents from category string.
    category_str = normalize_tagname(instance.category)
    if category_str not in instance.project.meta_category_list:
        instance.project.meta_category_list.append(category_str)

    instance.project.save()



""" 
Email signals handlers. 
Abstraction layer for greenqueue. 
"""

from greenmine import signals
from greenmine.utils import set_token
from greenqueue import send_task
from django.conf import settings
from django.utils.translation import ugettext
from django.template.loader import render_to_string

@receiver(signals.mail_new_user)
def mail_new_user(sender, user, **kwargs):
    template = render_to_string("email/new.user.html", {
        "user": user,
        "token": set_token(user),
        'current_host': settings.HOST,
    })

    subject = ugettext("Greenmine: wellcome!")
    send_task("send-mail", args = [subject, template, [user.email]])

@receiver(signals.mail_recovery_password)
def mail_recovery_password(sender, user, **kwargs):
    template = render_to_string("email/forgot.password.html", {
        "user": user,
        "token": set_token(user),
        "current_host": settings.HOST,
    })
    subject = ugettext("Greenmine: password recovery.")
    send_task("send-mail", args = [subject, template, [user.email]])


@receiver(signals.mail_milestone_created)
def mail_milestone_created(sender, milestone, user, **kwargs):
    participants_ids = ProjectUserRole.objects\
        .filter(user=user, mail_milestone_created=True, project=milestone.project)\
        .values_list('user__pk', flat=True)

    participants = User.objects.filter(pk__in=participants_ids)

    emails_list = []
    subject = ugettext("Greenmine: sprint created")
    for person in participants:
        template = render_to_string("email/milestone.created.html", {
            "user": person,
            "current_host": settings.HOST,
            "milestone": milestone,
        })

        emails_list.append([subject, template, [person.email]])

    send_task("send-bulk-mail", args=[emails_list])

@receiver(signals.mail_userstory_created)
def mail_userstory_created(sender, us, user, **kwargs):
    participants_ids = ProjectUserRole.objects\
        .filter(user=user, mail_userstory_created=True, project=us.project)\
        .values_list('user__pk', flat=True)

    participants = User.objects.filter(pk__in=participants_ids)

    emails_list = []
    subject = ugettext("Greenmine: user story created")

    for person in participants:
        template = render_to_string("email/userstory.created.html", {
            "user": person,
            "current_host": settings.HOST,
            "us": us,
        })

        emails_list.append([subject, template, [person.email]])

    send_task("send-bulk-mail", args=[emails_list])
