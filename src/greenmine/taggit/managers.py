# -*- coding: utf-8 -*-
from __future__ import absolute_import

from django.contrib.contenttypes.generic import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models.fields.related import ManyToManyRel, RelatedField, add_lazy_relation
from django.db.models.related import RelatedObject
from django.utils.text import capfirst
from django.utils.translation import ugettext_lazy as _

from django.db import connection, models
from django.db.models.query import QuerySet
from django.utils.translation import ugettext_lazy as _
qn = connection.ops.quote_name

from .forms import TagField
from .models import TaggedItem, GenericTaggedItemBase, Tag
from .utils import require_instance_manager


class TaggableRel(ManyToManyRel):
    def __init__(self):
        self.related_name = None
        self.limit_choices_to = {}
        self.symmetrical = True
        self.multiple = True
        self.through = None


class TagManager(models.Manager):

    def tags_for_queryset(self, queryset, counts=True, min_count=None):
        """
        Based on django-testing

        Obtain a list of tags associated with instances of a model
        contained in the given queryset.

        If ``counts`` is True, a ``count`` attribute will be added to
        each tag, indicating how many times it has been used against
        the Model class in question.

        If ``min_count`` is given, only tags which have a ``count``
        greater than or equal to ``min_count`` will be returned.
        Passing a value for ``min_count`` implies ``counts=True``.
        """

        compiler = queryset.query.get_compiler(using='default')
        extra_joins = ' '.join(compiler.get_from_clause()[0][1:])
        where, params = queryset.query.where.as_sql(
            compiler.quote_name_unless_alias, compiler.connection
        )

        if where:
            extra_criteria = 'AND %s' % where
        else:
            extra_criteria = ''
        return self._get_usage(queryset.model, counts, min_count, extra_joins, extra_criteria, params)


    def _get_usage(self, model, counts=False, min_count=None, extra_joins=None, extra_criteria=None, params=None):
        """
        Perform the custom SQL query for ``usage_for_model`` and
        ``usage_for_queryset``.
        """
        if min_count is not None: counts = True

        model_table = qn(model._meta.db_table)
        model_pk = '%s.%s' % (model_table, qn(model._meta.pk.column))

        query = """
        SELECT DISTINCT %(tag)s.id, %(tag)s.name%(count_sql)s
        FROM
            %(tag)s
            INNER JOIN %(tagged_item_alias)s
                ON %(tag)s.id = %(tagged_item)s.tag_id
            INNER JOIN %(model)s
                ON %(tagged_item)s.object_id = %(model_pk)s
            %%s
        WHERE %(tagged_item)s.content_type_id = %(content_type_id)s
            %%s
        GROUP BY %(tag)s.id, %(tag)s.name
        %%s
        ORDER BY %(tag)s.name ASC""" % {
            'tag': qn(Tag._meta.db_table),
            'count_sql': counts and (', COUNT(%s)' % model_pk) or '',
            'tagged_item_alias': qn(TaggedItem._meta.db_table) + " tagged_item_alias",
            'tagged_item': "tagged_item_alias",
            'model': model_table,
            'model_pk': model_pk,
            'content_type_id': ContentType.objects.get_for_model(model).pk,
        }

        min_count_sql = ''
        if min_count is not None:
            min_count_sql = 'HAVING COUNT(%s) >= %%s' % model_pk
            params.append(min_count)

        cursor = connection.cursor()

        cursor.execute(query % (extra_joins, extra_criteria, min_count_sql), params)
        tags = []
        for row in cursor.fetchall():
            t = Tag(*row[:2])
            if counts:
                t.count = row[2]
            tags.append(t)

        return tags

class TaggableManager(RelatedField):
    def __init__(self, verbose_name=_("Tags"),
        help_text=_("A comma-separated list of tags."), through=None, blank=False):
        self.through = through or TaggedItem
        self.rel = TaggableRel()
        self.verbose_name = verbose_name
        self.help_text = help_text
        self.blank = blank
        self.editable = True
        self.unique = False
        self.creates_table = False
        self.db_column = None
        self.choices = None
        self.serialize = False
        self.null = True
        self.creation_counter = models.Field.creation_counter
        models.Field.creation_counter += 1

    def __get__(self, instance, model):
        if instance is not None and instance.pk is None:
            raise ValueError("%s objects need to have a primary key value "
                "before you can access their tags." % model.__name__)
        manager = _TaggableManager(
            through=self.through, model=model, instance=instance
        )
        return manager

    def contribute_to_class(self, cls, name):
        self.name = self.column = name
        self.model = cls
        cls._meta.add_field(self)
        setattr(cls, name, self)
        if not cls._meta.abstract:
            if isinstance(self.through, basestring):
                def resolve_related_class(field, model, cls):
                    self.through = model
                    self.post_through_setup(cls)
                add_lazy_relation(
                    cls, self, self.through, resolve_related_class
                )
            else:
                self.post_through_setup(cls)

    def post_through_setup(self, cls):
        self.use_gfk = (
            self.through is None or issubclass(self.through, GenericTaggedItemBase)
        )
        self.rel.to = self.through._meta.get_field("tag").rel.to
        if self.use_gfk:
            tagged_items = GenericRelation(self.through)
            tagged_items.contribute_to_class(cls, "tagged_items")

    def save_form_data(self, instance, value):
        getattr(instance, self.name).set(*value)

    def formfield(self, form_class=TagField, **kwargs):
        defaults = {
            "label": capfirst(self.verbose_name),
            "help_text": self.help_text,
            "required": not self.blank
        }
        defaults.update(kwargs)
        return form_class(**defaults)

    def value_from_object(self, instance):
        if instance.pk:
            return self.through.objects.filter(**self.through.lookup_kwargs(instance))
        return self.through.objects.none()

    def related_query_name(self):
        return self.model._meta.module_name

    def m2m_reverse_name(self):
        return self.through._meta.get_field_by_name("tag")[0].column

    def m2m_target_field_name(self):
        return self.model._meta.pk.name

    def m2m_reverse_target_field_name(self):
        return self.rel.to._meta.pk.name

    def m2m_column_name(self):
        if self.use_gfk:
            return self.through._meta.virtual_fields[0].fk_field
        return self.through._meta.get_field('content_object').column

    def db_type(self, connection=None):
        return None

    def m2m_db_table(self):
        return self.through._meta.db_table

    def extra_filters(self, pieces, pos, negate):
        if negate or not self.use_gfk:
            return []
        prefix = "__".join(["tagged_items"] + pieces[:pos-2])
        cts = map(ContentType.objects.get_for_model, _get_subclasses(self.model))
        if len(cts) == 1:
            return [("%s__content_type" % prefix, cts[0])]
        return [("%s__content_type__in" % prefix, cts)]

    def bulk_related_objects(self, new_objs, using):
        return []


class _TaggableManager(models.Manager):
    def __init__(self, through, model, instance):
        self.through = through
        self.model = model
        self.instance = instance

    def get_query_set(self):
        return self.through.tags_for(self.model, self.instance)

    def _lookup_kwargs(self):
        return self.through.lookup_kwargs(self.instance)

    @require_instance_manager
    def add(self, *tags):
        str_tags = set([
            t
            for t in tags
            if not isinstance(t, self.through.tag_model())
        ])
        tag_objs = set(tags) - str_tags
        # If str_tags has 0 elements Django actually optimizes that to not do a
        # query.  Malcolm is very smart.
        existing = self.through.tag_model().objects.filter(
            name__in=str_tags
        )
        tag_objs.update(existing)

        for new_tag in str_tags - set(t.name for t in existing):
            tag_objs.add(self.through.tag_model().objects.create(name=new_tag))

        for tag in tag_objs:
            self.through.objects.get_or_create(tag=tag, **self._lookup_kwargs())

    @require_instance_manager
    def set(self, *tags):
        self.clear()
        self.add(*tags)

    @require_instance_manager
    def remove(self, *tags):
        self.through.objects.filter(**self._lookup_kwargs()).filter(
            tag__name__in=tags).delete()

    @require_instance_manager
    def clear(self):
        self.through.objects.filter(**self._lookup_kwargs()).delete()

    def most_common(self):
        return self.get_query_set().annotate(
            num_times=models.Count(self.through.tag_relname())
        ).order_by('-num_times')

    @require_instance_manager
    def similar_objects(self):
        lookup_kwargs = self._lookup_kwargs()
        lookup_keys = sorted(lookup_kwargs)
        qs = self.through.objects.values(*lookup_kwargs.keys())
        qs = qs.annotate(n=models.Count('pk'))
        qs = qs.exclude(**lookup_kwargs)
        qs = qs.filter(tag__in=self.all())
        qs = qs.order_by('-n')

        # TODO: This all feels like a bit of a hack.
        items = {}
        if len(lookup_keys) == 1:
            # Can we do this without a second query by using a select_related()
            # somehow?
            f = self.through._meta.get_field_by_name(lookup_keys[0])[0]
            objs = f.rel.to._default_manager.filter(**{
                "%s__in" % f.rel.field_name: [r["content_object"] for r in qs]
            })
            for obj in objs:
                items[(getattr(obj, f.rel.field_name),)] = obj
        else:
            preload = {}
            for result in qs:
                preload.setdefault(result['content_type'], set())
                preload[result["content_type"]].add(result["object_id"])

            for ct, obj_ids in preload.iteritems():
                ct = ContentType.objects.get_for_id(ct)
                for obj in ct.model_class()._default_manager.filter(pk__in=obj_ids):
                    items[(ct.pk, obj.pk)] = obj

        results = []
        for result in qs:
            obj = items[
                tuple(result[k] for k in lookup_keys)
            ]
            obj.similar_tags = result["n"]
            results.append(obj)
        return results


def _get_subclasses(model):
    subclasses = [model]
    for f in model._meta.get_all_field_names():
        field = model._meta.get_field_by_name(f)[0]
        if (isinstance(field, RelatedObject) and
            getattr(field.field.rel, "parent_link", None)):
            subclasses.extend(_get_subclasses(field.model))
    return subclasses
