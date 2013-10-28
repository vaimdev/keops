<%
	ro = (field.field.widget.attrs.get('readonly') and ' ng-init="form.readonly.' + field.name + '=true"') or ''
%>
% if isinstance(field.field, forms.GridField):
	<td colspan="2" class="form-grid-cell"><%include file="/keops/templates/keops/forms/fields/grid.html.mako"/></td>
% else:
	<td class="form-label-cell"
	% if field.field.required:
		ng-class="form.item.${field.name} == '' ? 'has-error' : ''"
    % endif
			>${field.label_tag(attrs={'class': 'control-label'})}</td>
	<td class="form-field-cell"${ro}
	% if field.field.required:
		ng-class="form.item.${field.name} == '' ? 'has-error' : ''"
    % endif
			>
		<%include file="/keops/templates/keops/forms/fields/widget.html.mako"/>
		<%include file="/keops/templates/keops/forms/fields/span.html.mako"/>
	</td>
% endif