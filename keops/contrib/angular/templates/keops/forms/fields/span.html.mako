% if isinstance(field.field, forms.DecimalField):
	<span ng-show="!form.write">{{form.item.${field.name}|number:2}}</span>
% elif isinstance(field.field, forms.ModelChoiceField):
	<%
		url = field.field.target_attr.get_resource_url()
	%>
	% if url:
		<a style="cursor: pointer" ng-show="!form.write" ng-bind="form.item.${field.name}.text" ng-click="openResource('${url}', 'pk=' + form.item.${field.name}.id, ${field.name})"></a>
	% else:
        <a ng-show="!form.write" ng-bind="form.item.${field.name}.text"></a>
    % endif
% elif isinstance(field.field, forms.ChoiceField):
    <span ng-show="!form.write || form.readonly.${field.name}" ng-bind="form.item.${field.name}.text"></span>
% elif isinstance(field.field.widget, forms.Textarea):
    <span ng-show="!form.write || form.readonly.${field.name}" class="text-field-span">{{form.item.${field.name}}}</span>
% else:
	<span ng-show="!form.write">{{form.item.${field.name}}}</span>
% endif