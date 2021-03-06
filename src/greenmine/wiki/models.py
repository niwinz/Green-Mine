from django.db import models
from .fields import WikiField

class WikiPage(models.Model):
    project = models.ForeignKey('scrum.Project', related_name='wiki_pages')
    slug = models.SlugField(max_length=500, db_index=True)
    content = WikiField(blank=False, null=True)
    owner = models.ForeignKey("auth.User", related_name="wiki_pages", null=True)

    watchers = models.ManyToManyField('auth.User',
        related_name='wikipage_watchers', null=True)

    created_date = models.DateTimeField(auto_now_add=True)

    @models.permalink
    def get_absolute_url(self):
        return ('wiki-page', (),
            {'pslug': self.project.slug, 'wslug': self.slug})

    @models.permalink
    def get_view_url(self):
        return ('wiki-page', (),
            {'pslug': self.project.slug, 'wslug': self.slug})

    @models.permalink
    def get_edit_url(self):
        return ('wiki-page-edit', (),
            {'pslug': self.project.slug, 'wslug': self.slug})

    @models.permalink
    def get_delete_url(self):
        return ('wiki-page-delete', (),
            {'pslug': self.project.slug, 'wslug': self.slug})

    @models.permalink
    def get_history_view_url(self):
        return ('wiki-page-history', (),
            {'pslug': self.project.slug, 'wslug': self.slug})



class WikiPageHistory(models.Model):
    wikipage = models.ForeignKey("WikiPage", related_name="history_entries")
    content = WikiField(blank=True, null=True)
    created_date = models.DateTimeField()
    owner = models.ForeignKey("auth.User", related_name="wiki_page_historys")

    # TODO: fix this permalink. this implementation is bad for performance.

    @models.permalink
    def get_history_view_url(self):
        return ('wiki-page-history-view', (),
            {'pslug': self.wikipage.project.slug, 'wslug': self.wikipage.slug, 'hpk': self.pk})


class WikiPageAttachment(models.Model):
    wikipage = models.ForeignKey('WikiPage', related_name='attachments')
    owner = models.ForeignKey("auth.User", related_name="wikifiles")
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now_add=True)
    attached_file = models.FileField(upload_to="files/wiki",
        max_length=500, null=True, blank=True)
