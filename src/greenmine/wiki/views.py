# -*- coding: utf-8 -*-

from __future__ import absolute_import

from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify
from django.shortcuts import get_object_or_404

from ..core.utils.slug import slugify_uniquely
from ..core.generic import GenericView
from ..core.decorators import login_required
from ..scrum.models import Project

from .models import WikiPage, WikiPageHistory
from .forms import WikiPageEditForm


class WikiPageView(GenericView):
    menu = ['wiki']
    template_path = 'wiki-page.html'

    @login_required
    def get(self, request, pslug, wslug):
        project = get_object_or_404(Project, slug=pslug)

        self.check_role(request.user, project, [
            ('project', 'view'),
            ('wiki', 'view'),
        ])

        try:
            wikipage = project.wiki_pages.get(slug=slugify(wslug))
        except WikiPage.DoesNotExist:
            return self.render_redirect(reverse('wiki-page-edit',
                args=[project.slug, slugify(wslug)]))

        context = {
            'project': project,
            'wikipage': wikipage,
        }
        return self.render_to_response(self.template_path, context)


class WikiPageEditView(GenericView):
    menu = ['wiki']
    template_path = 'wiki-page-edit.html'

    @login_required
    def get(self, request, pslug, wslug):
        project = get_object_or_404(Project, slug=pslug)

        self.check_role(request.user, project, [
            ('project', 'view'),
            ('wiki', ('view', 'create', 'edit')),
        ])

        try:
            wikipage = project.wiki_pages.get(slug=slugify(wslug))
        except WikiPage.DoesNotExist:
            wikipage = None

        form = WikiPageEditForm(instance=wikipage)

        context = {
            'form': form,
            'project': project,
        }

        return self.render_to_response(self.template_path, context)

    @login_required
    def post(self, request, pslug, wslug):
        project = get_object_or_404(Project, slug=pslug)

        self.check_role(request.user, project, [
            ('project', 'view'),
            ('wiki', ('view', 'create', 'edit')),
        ])

        try:
            wikipage = project.wiki_pages.get(slug=slugify(wslug))
        except WikiPage.DoesNotExist:
            wikipage = None

        form = WikiPageEditForm(request.POST, instance=wikipage)
        if not form.is_valid():
            return self.render_json_errors(form.errors)

        wikipage_new = form.save(commit=False)

        if wikipage is not None:
            old_wikipage = WikiPage.objects.get(pk=wikipage.pk)
            history_entry = WikiPageHistory(
                wikipage = old_wikipage,
                content = old_wikipage.content,
                owner = old_wikipage.owner,
                created_date = old_wikipage.created_date,
            )
            history_entry.save()

        if not wikipage_new.slug:
            wikipage_new.slug = slugify_uniquely(wslug, wikipage_new.__class__)

        if not wikipage_new.project_id:
            wikipage_new.project = project

        wikipage_new.owner = request.user
        wikipage_new.save()

        return self.render_json({'redirect_to': wikipage_new.get_view_url()})


class WikiPageHistoryView(GenericView):
    menu = ['wiki']
    template_path = 'wiki-page-history-view.html'

    @login_required
    def get(self, request, pslug, wslug, hpk):
        project = get_object_or_404(Project, slug=pslug)

        self.check_role(request.user, project, [
            ('project', 'view'),
            ('wiki', 'view'),
        ])

        wikipage = get_object_or_404(project.wiki_pages, slug=wslug)
        history_entry = get_object_or_404(wikipage.history_entries, pk=hpk)

        context = {
            'project': project,
            'wikipage': wikipage,
            'history_entry': history_entry,
        }
        return self.render_to_response(self.template_path, context)


class WikipageDeleteView(GenericView):
    template_path = 'wiki-page-delete.html'

    def get_context(self):
        project = get_object_or_404(Project, slug=self.kwargs['pslug'])

        self.check_role(self.request.user, project, [
            ('project', 'view'),
            ('wiki', ('view', 'delete')),
        ])

        wikipage = get_object_or_404(project.wiki_pages, slug=self.kwargs['wslug'])

        context = {
            'project': project,
            'wikipage': wikipage,
        }
        return context

    @login_required
    def get(self, request, **kwargs):
        context = self.get_context()
        return self.render_to_response(self.template_path, context)

    @login_required
    def post(self, request, **kwargs):
        context = self.get_context()
        context['wikipage'].history_entries.all().delete()
        context['wikipage'].delete()

        return self.render_redirect(reverse('wiki-page',
            args = [context['project'].slug, 'home']))
