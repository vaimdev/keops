{% load i18n %}
	var __store = Ext.create('Ext.data.Store', {
		pageSize: 25,
		fields: {{ fields|safe }},
		proxy: {
			type: 'ajax',
			url: '{% url 'keops.views.db.grid' %}',
			extraParams: {
				model: '{{ model_name }}'
			},
			reader: {
				type: 'json',
				root: 'items',
				id: 'pk',
				totalProperty: 'total'
			}
		},
		autoLoad: true
    });
// form
    keops.app.show(Ext.create("Ext.grid.Panel", {
	id: 'keops-app-form',
	columns: {{ items|safe }},
	store: __store,
    layout: "fit", 
    dockedItems: [{
    	xtype: 'panel',
        border: false,
    	html: '<table class="header"><tr><td style="vertical-align: top; font-weight: bold; font-size: 13px;"><span style="font-weight: normal;">{{ form.title|capfirst }}</span></td><td style="text-align: right; vertical-align: bottom; width: 400px;">{% include "keops/forms/search_header.html" %}</td></tr></table>'
    }, {
    	xtype: 'pagingtoolbar',
    	dock: 'bottom',
    	margin: '0 0 0 0',
    	style: 'background-color: #eee;',
    	store: __store,
    	displayInfo: true
    },
    {
    	xtype: 'toolbar',
    	defaults: {
    		margin: '1 1 1 1'
    	},
    	items: [
	    	{ text: '{% trans 'Create' %}' }, 
	    	{ text: '{% trans 'Edit' %}' }, 
	    	{ xtype: 'tbspacer', margin: '0 5 0 5' },
	    	{ text: '{% trans 'Print' %}' },
	    	{ text: '{% trans 'Record' %}', 
	    		menu: { xtype: 'menu', 
	    			items: [{ text: 'Duplicar' }, { text: 'Excluir'}] 
	    		} 
	    	},
	    	{ text: 'Mais' },
	    	{ xtype: 'tbspacer', margin: '0 5 0 5' }
    	]
    }],
    listeners: {
    	itemdblclick: function (sender, record, item, index, e, eOpts) {
    		window.location = '#action={{ action.pk }}&view_type=form&pk=' + record.raw.pk;
    		console.log(record.raw.pk);
    	}
    },
    viewConfig: {
    },
    selModel: Ext.create("Ext.selection.CheckboxModel")}));
