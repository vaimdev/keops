<div ng-show="form.write && !form.readonly.${field.name}">
	<input type="text" class="form-control input-sm form-date-field" ng-model="form.item.${field.name}_0" date-picker name="${field.name}_0" id="${field.auto_id}_0">
	<input type="text" class="form-control input-sm form-date-field" ng-model="form.item.${field.name}_1" date-picker name="${field.name}_1" id="${field.auto_id}_1">
</div>