% if isinstance(field.field, forms.ModelChoiceField):
	<%include file="/keops/forms/fields/modelchoice.html.mako"/>
% elif isinstance(field.field, forms.ChoiceField):
	<%include file="/keops/forms/fields/choice.html.mako"/>
% elif isinstance(field.field, forms.BooleanField):
	<%include file="/keops/forms/fields/boolean.html.mako"/>
% elif isinstance(field.field, forms.DateField):
	<%include file="/keops/forms/fields/date.html.mako"/>
% elif isinstance(field.field, forms.DateTimeField):
	<%include file="/keops/forms/fields/datetime.html.mako"/>
% else:
	<%include file="/keops/forms/fields/input.html.mako"/>
% endif
<%include file="/keops/forms/fields/span.html.mako"/>