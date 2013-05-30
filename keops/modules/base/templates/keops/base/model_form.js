	var __orun_store = Ext.create('Ext.data.Store', {
		pageSize: 1,
		fields: {{ fields|safe }},
		proxy: {
			type: 'ajax',
			url: '/orun/db/read/',
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
    orun.app.show(Ext.create("Ext.form.Panel", {
    autoScroll: true,
    title: '{{ form_title }}',
    store: __orun_store,
    border: false, 
    layout: "column",
    defaults: { padding: "5 0 0 8" },
    items: {{ items|safe }},
    dockedItems: [{
    	xtype: 'panel',
    	html: '<table class="header"><tr><td style="vertical-align: top; font-weight: bold; font-size: 15px;">Full record description<div style="font-size: 11px; font-weight: normal; margin-top: 5px; text-shadow: none;">Help text for this form.</div></td><td style="text-align: right; vertical-align: bottom; width: 400px;"><div><input class="search-field" placeholder="Pesquisa" style="width: 100%" /></div></td></tr></table>'
    }, {
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
    }, {
    	xtype: 'pagingtoolbar',
    	style: 'background-color: #eee;',
    	store: __orun_store,
    	dock: 'bottom'
    }]}));
