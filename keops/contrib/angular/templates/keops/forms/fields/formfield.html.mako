% if isinstance(field.field, forms.GridField):
	<td colspan="2"><%include file="/keops/forms/fields/grid.html.mako"/></td>
% else:
	<td class="form-label-cell">${field.label_tag()}</td><td class="form-field-cell"><%include file="/keops/forms/fields/widget.html.mako"/></td>
% endif