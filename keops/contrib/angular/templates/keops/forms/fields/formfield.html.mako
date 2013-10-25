<%
	ro = (field.field.widget.attrs.get('readonly') and ' ng-init="form.readonly.' + field.name + '=true"') or ''
%>
% if isinstance(field.field, forms.GridField):
	<td colspan="2"><%include file="/keops/forms/fields/grid.html.mako"/></td>
% else:
	<td class="form-label-cell">${field.label_tag()}</td>
	<td class="form-field-cell"${ro}>
		<%include file="/keops/forms/fields/widget.html.mako"/>
		<%include file="/keops/forms/fields/span.html.mako"/>
	</td>
% endif