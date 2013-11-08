<%!
	from django.utils.translation import ugettext as _
	from django.utils.text import capfirst
%>
<%
	related = field.field.target_attr.related
	model = related.model
	list_fields = field.field.target_attr.list_fields
	fields = [ model._meta.get_field(f) for f in list_fields if related.field.name != f ]
	disp = {f.name: {'name': (isinstance(f, models.ForeignKey) or f.choices) and (f.name + '.text') or f.name, 'style': isinstance(f, (models.IntegerField, models.DecimalField)) and 'text-align: right;' or '', 'filter': isinstance(f, (models.IntegerField, models.DecimalField)) and '|number:2' or ''} for f in fields }
%>
<div remoteitem grid-field style="max-height: 200px; overflow: auto;" name="${field.name}">
	<legend class="field-label" style="display: inline-block; padding-right: 10px;">${field.label}</legend>
	<a ng-show="form.write" class="btn btn-sm btn-default" ng-click="showDetail('${field.field.target_attr.model._meta}', '${field.name}')">${_('add') | capfirst}</a>
	<table class="table table-hover table-condensed">
		<thead>
		<tr>
		% for f in fields:
			<th style="${disp[f.name]['style']}">${f.verbose_name|capfirst}</th>
		% endfor
			<th style="width: 10px;"></th>
		</tr>
		</thead>
		<tbody>
		<tr ui-table-row ng-repeat="item in form.item.${field.name}|filter:tableRowFilter" ng-click="form.write && showDetail('${field.field.target_attr.model._meta}', '${field.name}', item)">
		% for f in fields:
			<td style="${disp[f.name]['style']}">

				{{item.${disp[f.name]['name']}${disp[f.name]['filter']}}}
			</td>
        % endfor
			<td style="padding-right: 5px;">
				<button class="close" ng-show="form.write" tooltip="${_('remove item')|capfirst}" ng-click="item.__state__ = 'deleted'">&times;</button>
			</td>
		</tr>
		</tbody>
	</table>
</div>