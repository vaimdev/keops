<%
	ro = ((field.field.widget.attrs.get('readonly') or form.readonly) and ' ng-init="form.readonly.' + field.name + '=true"') or ''
%>
% if isinstance(field.field, forms.GridField):
	<td colspan="2" class="form-grid-cell"><%include file="/keops/forms/fields/grid.html.mako"/></td>
% else:
	<td class="form-label-cell"
	% if field.field.required:
		ng-class="!dataForm.${field.name}.$valid ? 'has-error' : ''"
    % endif
			>${field.label_tag(label_suffix='', attrs={'class': 'control-label'})}</td>
	<td class="form-field-cell"${ro}
	% if field.field.required:
		ng-class="!dataForm.${field.name}.$valid ? 'has-error' : ''"
    % endif
			>
		<%include file="/keops/forms/fields/widget.html.mako"/>
		<%include file="/keops/forms/fields/span.html.mako"/>
		% if field.help_text and not isinstance(field.field, forms.BooleanField):
			<p class="help">${field.help_text}</p>
		% endif
	</td>
% endif