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
    	xtype: 'pagingtoolbar',
    	dock: 'bottom',
    	margin: '0 0 0 0',
    	style: 'background-color: #eee;',
    	store: __store,
    	displayInfo: true
    }, {
    	xtype: 'panel',
    	itemId: 'form-header',
        bodyCls: 'toolbar-header',
        border: false,
        frame: false,
        items: [{
            layout: {
                type: 'hbox',
                align: 'stretch'
            },
            border: false, frame: false, bodyStyle: 'background: transparent',
            items: [{
                xtype: 'container',
                flex: 1,
                border: false, frame: false, bodyStyle: 'background: transparent',
                items: [{
                    xtype: 'label',
                    style: 'font-weight: normal',
                    itemId: 'form-label',
                    html: '<b>{{ form.title|capfirst }}</b>'
                }, {
                    xtype: 'label',
                    text: '{{ form.help_text }}'
                }]
            }, {
                xtype: 'container',
                items: [
                {
                xtype: 'searchfield',
                style: 'background-color: #ffffff',
                emptyText: '{{ _("search")|capfirst }}',
                store: __store,
                width: 330
            }, {
                        xtype: 'panel',
                        border: false, frame: false, bodyStyle: 'background: transparent',
                        rtl: true,
                        items: [{
                            xtype: 'button',
                            handler: function() { window.location.href = '#action={{ action.pk }}&view_type=list'; },
                            text: '{{ _("list")|capfirst }}'
                        }, {
                            xtype: 'button',
                            handler: function() { window.location.href = '#action={{ action.pk }}&view_type=form'; },
                            text: '{{ _("form")|capfirst }}'
                        }]
                    }]
        }]
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
                    { text: '{{ _("create")|capfirst }}', itemId: 'btn-create', handler: function() { window.location.href = '#action={{ action.pk }}&view_type=form&state=create'; } },
                    { text: '{{ _("edit")|capfirst }}', disabled: true, itemId: 'btn-edit', handler: function() { console.log('not implemented'); } },
                    { xtype: 'tbspacer', margin: '0 5 0 5' },
                    { text: '{{ _("print")|capfirst }}', itemId: 'btn-print' },
                    { text: '{{ _("record")|capfirst }}', itemId: 'btn-record',
                        menu: { xtype: 'menu',
                            items: [{ text: '{{ _("duplicate")|capfirst }}' }, { text: '{{ _("delete")|capfirst }}'}]
                        }
                    },
                    { text: '{{ _("more")|capfirst }}' },
                    { xtype: 'tbspacer', margin: '0 5 0 5' }
                ]
            }]
    }],
    listeners: {
    	itemdblclick: function (sender, record, item, index, e, eOpts) {
    		window.location = '#action={{ action.pk }}&view_type=form&pk=' + record.raw.pk;
    	}
    },
    viewConfig: {
    },
    selModel: Ext.create("Ext.selection.CheckboxModel")}));
