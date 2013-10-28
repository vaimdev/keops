<div ng-show="form.write && !form.readonly.${field.name}">
	${field.as_widget(attrs={'ng-model': 'form.item.' + field.name, 'date-picker': 'date-picker'})}
</div>