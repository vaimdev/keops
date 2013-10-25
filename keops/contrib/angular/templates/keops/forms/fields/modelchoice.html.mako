<div ng-show="form.write">
	<input type="hidden" combobox ng-model="form.item.${field.name}" lookup-url="/db/lookup/?model=${str(field.field.target_attr.model._meta)}&field=${field.name}" class="form-long-field" style="padding: 0" id="${field.auto_id}" name="${field.name}">
</div>