<div ng-show="form.write">
	<input type="hidden" combobox ng-model="form.item.${field.name}" lookup-url="/db/lookup/?model=${str(model._meta)}&field=${field.name}" class="form-long-field" style="padding: 0;" id="${field.auto_id}" name="${field.name}" ${' '.join('%s="%s"' % (k, v) for k, v in field.field.widget.attrs.items())}>
</div>