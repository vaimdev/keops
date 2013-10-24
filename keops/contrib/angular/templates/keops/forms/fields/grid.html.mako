<div remoteitem style="max-height: 200px; overflow: auto;" name="${field.name}">
	<%
        related = field.field.target_attr.related
        model = related.model
        list_fields = field.field.target_attr.list_fields
        fields = [ model._meta.get_field(f) for f in list_fields if related.field.name != f ]
	%>
	<table class="grid-field">
		<thead>
		<tr>
		% for f in fields:
			<th>${f.verbose_name}</th>
		% endfor
			<th style="width: 10px;"></th>
		</tr>
		</thead>
		<tbody>
		<tr ui-table-row ng-repeat="item in form.item.${field.name}|filter:tableRowFilter" ng-click="form.write && showDetail('${field.field.target_attr.model._meta}', '${field.name}', item)">
		% for f in fields:
			<td>{{item.${f.name}}}</td>
        % endfor
			<td>
				<button class="btn btn-default" ng-show="form.write" tooltip="%s" ng-click="item.__state__ = 'deleted'"><i class="icon-remove"></i></button>
			</td>
		</tr>
		</tbody>
	</table>
</div>