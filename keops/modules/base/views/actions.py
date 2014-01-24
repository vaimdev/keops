from keops.admin import ModelAdmin
from keops.admin import site


def response_form(request, action, *args, **kwargs):
    view_type = kwargs.get('view_type') or action.view_type
    state = request.GET.get('state', action.state or 'read')
    if action.view:
        pass
    else:
        # Auto detect ModelAdmin
        model = action.model.content_type.model_class()
        try:
            admin = model._meta.admin.model_admin
        except:
            raise
            # Auto create ModelAdmin
            admin = type(model.__name__ + 'Admin', (ModelAdmin,), {'model': model})(model, site)
            model.add_to_class('_admin', admin)
        return admin.view(request, view_type=view_type, action=action, state=state, **action.get_context())


def admin_action(request):
    return site.dispatch_action(request)
