{% load i18n %}
	var __header = '<table style="width: 100%"><tr><td style="vertical-align: top; font-size: 13px;"><a style="font-weight: bold" href="#action={{ action.pk }}&view_type=list">{{ form.label|capfirst }}</a> %s<div style="font-size: 11px; font-weight: normal; margin-top: 5px; text-shadow: none;">{{ form.help_text }}</div></td><td style="text-align: right; vertical-align: bottom; width: 400px;">{% include "keops/forms/search_header.html" %}</td></tr></table>';
	var __store = Ext.create('Ext.data.Store', {
		pageSize: 1,
		fields: {{ fields|safe }},
		proxy: {
			type: 'ajax',
			url: '{% url 'keops.views.db.read' %}',
			extraParams: {
				{% if pk %}pk: "{{ pk }}",{% endif %}
				model: '{{ model_name }}'
			},
			reader: {
				type: 'json',
				root: 'items',
				id: 'pk',
				totalProperty: 'total'
			}
		},
		autoLoad: true,
		listeners: {
			load: function() {
				var form = this._form;
				if (form) {
					var r = this.data.first();
					form.loadRecord(r);
					h = form.dockedItems.items[0].items.items[0];
					form.pk = r.raw.pk;
					h.update(__header.replace('%s', '/ ' + r.raw.__str__));
					//form
				}
			}
		}
    });
// form
    var __form = Ext.create("Keops.form.ModelForm", {
    autoScroll: true,
    border: false,
    layout: "column",
    submitUrl: '{% url 'keops.views.db.submit' %}',
    defaults: { padding: "5 0 0 8" },
    items: {{ items|safe }},
    store: __store,
    trackResetOnLoad: true,
    stateChange: function (state) {
    	
    },
    dockedItems: [{
    	xtype: 'panel',
    	itemId: 'form-header',
        bodyCls: 'toolbar-header',
        border: false,
        frame: false,
        items: [
            {
                xtype: 'container',
                border: false,
                frame: false,
                html: __header.replace('%s', '')
            },
            {
    	xtype: 'panel',
        layout: 'hbox',
        bodyStyle: 'background: transparent',
        border: false,
        frame: false,
    	defaults: {
    		margin: '1 1 1 1',
            xtype: 'button'
    	},
    	items: [
	    	{ text: '{{ _("create")|capfirst }}', itemId: 'btn-create', handler: function() { this.up('form').newRecord(); } },
	    	{ text: '{{ _("edit")|capfirst }}', itemId: 'btn-edit', handler: function() { this.up('form').editRecord(); } },
	    	{ text: '{{ _("save")|capfirst }}', hidden: true, itemId: 'btn-save', cls: 'x-btn-red-button', overCls: 'btn-red-button-over', handler: function() { this.up('form').saveRecord(); } },
	    	{ text: '{{ _("cancel")|capfirst }}', hidden: true, itemId: 'btn-cancel', handler: function() { this.up('form').cancelChanges(); } },
	    	{ xtype: 'tbspacer', margin: '0 5 0 5' },
	    	{ text: '{{ _("print")|capfirst }}' },
	    	{ text: '{{ _("record")|capfirst }}',
	    		menu: { xtype: 'menu', 
	    			items: [{ text: '{{ _("duplicate")|capfirst }}' }, { text: '{{ _("delete")|capfirst }}'}]
	    		} 
	    	},
	    	{ text: '{{ _("more")|capfirst }}' },
	    	{ xtype: 'tbspacer', margin: '0 5 0 5' }
    	]
    }]}, {
    	xtype: 'pagingtoolbar',
    	bodyStyle: 'background-color: #eee;',
    	store: __store,
    	dock: 'bottom'
    }]});
    __store._form = __form;
    keops.app.show(__form);
    __form.setState('read');
