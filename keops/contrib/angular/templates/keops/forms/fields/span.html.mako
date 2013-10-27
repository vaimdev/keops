<%!
	from django.utils.translation import ugettext as _
	from django.utils.text import capfirst
%>
<%
	ro = (field.field.widget.attrs.get('readonly') and ' || form.readonly.' + field.name) or ''
%>
% if isinstance(field.field, forms.DecimalField):
	<span ng-show="!form.write${ro}">{{form.item.${field.name}|number:2}}</span>
% elif isinstance(field.field, forms.ModelMultipleChoiceField):
% elif isinstance(field.field, forms.ModelChoiceField):
	<%
		url = field.field.target_attr.get_resource_url()
	%>
	% if url:
		<a style="cursor: pointer" ng-show="!form.write${ro}" ng-bind="form.item.${field.name}.text" ng-click="openResource('${url}', 'pk=' + form.item.${field.name}.id, ${field.name})"></a>
	% else:
        <a ng-show="!form.write${ro}" ng-bind="form.item.${field.name}.text"></a>
    % endif
% elif isinstance(field.field, forms.ChoiceField):
    <span ng-show="!form.write${ro}" ng-bind="form.item.${field.name}.text"></span>
% elif isinstance(field.field, forms.DateField):
	<span ng-show="!form.write${ro}">{{form.item.${field.name} | dateFrom}}</span>
% elif isinstance(field.field, forms.DateTimeField):
	<span ng-show="!form.write${ro}">{{form.item.${field.name} | dateFromNow}}</span>
% elif isinstance(field.field.widget, forms.Textarea):
    <span ng-show="!form.write${ro}" class="text-field-span">{{form.item.${field.name}}}</span>
% elif isinstance(field.field, forms.BooleanField):
	<span ng-show="!form.write${ro}" ng-bind="form.item.${field.name} ? '${_('yes')|capfirst}': '${_('no')|capfirst}'"></span>
% else:
	<span ng-show="!form.write${ro}">{{form.item.${field.name}}}</span>
% endif