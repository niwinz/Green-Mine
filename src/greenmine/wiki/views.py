from greenmine.base.utils.slugify import slugify_uniquely as slugify
from greenmine.core.generic import GenericView
from greenmine.core.decorators import login_required, staff_required
from django.shortcuts import get_object_or_404
from greenmine.scrum.models import *
from greenmine.wiki.models import *
from greenmine.wiki.forms import *

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
        if form.is_valid():
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
            return self.render_redirect(wikipage_new.get_view_url())

        context = {
            'form': form,
            'project': project,
        }
        return self.render_to_response(self.template_path, context)


class WikiPageHistory(GenericView):
    menu = ['wiki']
    template_path = 'wiki-page-history.html'

    @login_required
    def get(self, request, pslug, wslug):
        project = get_object_or_404(Project, slug=pslug)

        self.check_role(request.user, project, [
            ('project', 'view'),
            ('wiki', 'view'),
        ])

        wikipage = get_object_or_404(project.wiki_pages, slug=wslug)

        context = {
            'entries': wikipage.history_entries.order_by('created_date'),
            'wikipage': wikipage,
            'project': project,
        }

        return self.render_to_response(self.template_path, context)


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
