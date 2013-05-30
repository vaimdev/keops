	var __orun_store = Ext.create('Ext.data.Store', {
		pageSize: 25,
		fields: {{ fields }},
		proxy: {
			type: 'ajax',
			url: '/orun/db/grid/',
			extraParams: {
				model: '{{ "%s.%s" % (model._meta.app_label, model._meta.model_name)|safe }}'
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
    orun.app.show(Ext.create("Ext.grid.Panel", {
	id: 'orun-app-form',
	title: '{{ model._meta.verbose_name_plural }}',
	columns: {{ json.dumps([extjs.grid_column(name, field) for name, field in form.form.base_fields.items() if name in fields])|safe }},
	store: __orun_store,
    layout: "fit", 
    dockedItems: [{
    	xtype: 'panel',
    	html: '<table class="header"><tr><td style="vertical-align: top; font-weight: bold; font-size: 16px;"><div style="font-size: 12px; font-weight: normal; margin-top: 5px;">Form help text</div></td><td style="text-align: right; vertical-align: bottom; width: 400px;"><div><input class="search-field" placeholder="Pesquisa" style="width: 100%" /></div></td></tr></table>'
    }, {
    	xtype: 'pagingtoolbar',
    	dock: 'bottom',
    	margin: '0 0 0 0',
    	style: 'background-color: #eee;',
    	store: __orun_store,
    	displayInfo: true
    },
    {
    	xtype: 'toolbar',
    	defaults: {
    		margin: '1 1 1 1'
    	},
    	items: [
	    	{ text: 'Criar' }, 
	    	{ text: 'Editar' }, 
	    	{ xtype: 'tbspacer', margin: '0 5 0 5' },
	    	{ text: 'Imprimir' },
	    	{ text: 'Registro', 
	    		menu: { xtype: 'menu', 
	    			items: [{ text: 'Duplicar' }, { text: 'Excluir'}] 
	    		} 
	    	},
	    	{ text: 'Mais' },
	    	{ xtype: 'tbspacer', margin: '0 5 0 5' }
    	]
    }],
    listeners: {
    	itemdblclick: function() {
    		alert('dbl click');
    	}
    },
    viewConfig: {
    },
    selModel: Ext.create("Ext.selection.CheckboxModel")}));
