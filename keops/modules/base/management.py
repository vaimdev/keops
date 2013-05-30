from copy import copy
from django.contrib.contenttypes.models import ContentType
from .models import Module, BaseModel
from django.db import DEFAULT_DB_ALIAS, router
from django.db.models import get_app, get_apps, get_models, signals
from django.utils.encoding import smart_text
from django.utils import six
from django.utils.six.moves import input

def update_models(app, created_models, verbosity=2, db=DEFAULT_DB_ALIAS, **kwargs):
    """
    Creates content types for models in the given app, removing any model
    entries that no longer have a matching model class.
    """
    ContentType.objects.clear_cache()
    app_models = get_models(app)
    if not app_models:
        return
    # They all have the same app_label, get the first one.
    app_label = app_models[0]._meta.app_label
    
    if not router.allow_syncdb(db, ContentType.objects.using(db).get(app_label=app_label, model=app_models[0]._meta.model_name).model_class()):
        return

    app_models = dict(
        (model._meta.model_name, model)
        for model in app_models
    )

    # Register module
    mod_name = '.'.join(app.__name__.split('.')[:-1])
    module = Module.objects.using(db).filter(app_label=app_label)
    if module:
        module = module[0]
    else:
        from keops.db import scripts
        scripts.install(mod_name, db, False)
        module = Module.objects.using(db).get(app_label=app_label)

    # Get all the content types
    content_types = dict(
        (ct.content_type.model, ct)
        for ct in BaseModel.objects.using(db).filter(module=module)
    )
    to_remove = [
        ct
        for (model_name, ct) in six.iteritems(content_types)
        if model_name not in app_models
    ]

    cts = [
        BaseModel.objects.using(db).create(
            module=module,
            content_type=ContentType.objects.using(db).get(app_label=app_label, model=model_name),
            #app_label=app_label,
        )
        for (model_name, model) in six.iteritems(app_models)
        if model_name not in content_types
    ]
    #BaseModel.objects.using(db).bulk_create(cts)
    if verbosity >= 2:
        for ct in cts:
            print("Adding base model '%s | %s'" % (ct.app_label, ct.model))

    # Confirm that the content type is stale before deletion.
    if to_remove:
        if kwargs.get('interactive', False):
            content_type_display = '\n'.join([
                '    %s | %s' % (ct.app_label, ct.model)
                for ct in to_remove
            ])
            ok_to_delete = input("""The following model are stale and need to be deleted:

%s

Any objects related to these content types by a foreign key will also
be deleted. Are you sure you want to delete these content types?
If you're unsure, answer 'no'.

    Type 'yes' to continue, or 'no' to cancel: """ % content_type_display)
        else:
            ok_to_delete = False

        if ok_to_delete == 'yes':
            for ct in to_remove:
                if verbosity >= 2:
                    print("Deleting stale content type '%s | %s'" % (ct.app_label, ct.model))
                ct.delete()
        else:
            if verbosity >= 2:
                print("Stale content types remain.")

signals.post_syncdb.connect(update_models)
