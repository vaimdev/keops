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
	<div ng-show="!form.write${ro}" class="form-long-field"><label class="m2m-tag" ng-repeat="item in form.item.${field.name}">{{item.text}}</label></div>
% elif isinstance(field.field, forms.ModelChoiceField):
	<%
		url = field.field.target_attr.get_resource_url()
	%>
	% if url:
		<a style="cursor: pointer" ng-show="!form.write${ro}" ng-bind="${form_field}.text" ng-click="openResource('${url}', 'pk=' + ${form_field}.id, ${field.name})"></a>
	% else:
        <a ng-show="!form.write${ro}" ng-bind="${form_field}.text"></a>
    % endif
% elif isinstance(field.field, forms.ChoiceField):
    <span ng-show="!form.write${ro}" ng-bind="${form_field}.text"></span>
% elif isinstance(field.field, forms.DateField):
	<span ng-show="!form.write${ro}">{{${form_field} | dateFrom}}</span>
% elif isinstance(field.field, forms.DateTimeField):
	<span ng-show="!form.write${ro}">{{${form_field} | dateFromNow}}</span>
% elif isinstance(field.field.widget, forms.Textarea):
    <span ng-show="!form.write${ro}" class="text-field-span">{{${form_field}}}</span>
% elif isinstance(field.field, forms.BooleanField):
	<span ng-show="!form.write${ro}" ng-bind="${form_field} ? '${_('yes')|capfirst}': '${_('no')|capfirst}'"></span>
% else:
	<span ng-show="!form.write${ro}">{{${form_field}}}</span>
% endif