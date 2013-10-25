<label class="form-long-field" style="cursor: pointer" ng-show="form.write && !form.readonly.${field.name}">
	<input type="checkbox" style="cursor: pointer" ng-model="form.item.${field.name}" name="${field.name}" id="${field.auto_id}" ${' '.join('%s="%s"' % (k, v) for k, v in field.field.widget.attrs.items())}>
</label>