Ext.define('Keops.form.ModelForm', {
	extend: 'Ext.form.Panel',
	alias: 'widget.modelform',

    initComponent: function () {
        var me = this;
        me.layout = 'column';
        me.autoScroll = true;
    	//me.bodyStyle = 'background: #F1F1F1';
    	me.defaults = { margin: '5 5 0 8' };
    	//me.store = me.createStore();
        //if (me.liveObject) me.store.proxy.extraParams.form = me.id;
    	//me.dockedItems[2].store = me.store;
        me.callParent(arguments);
        me.pagingToolbar = this.down('pagingtoolbar'); 
    	//me.state = null;
    	me._state = 'read';
    },
    
    newRecord: function () {
    	this.setState('create');
    },

    editRecord: function () {
    	this.setState('write');
    },

    saveRecord: function () {
    	var form = this.getForm();
    	params = { model: this.store.proxy.extraParams.model, pk: this.pk };
    	params.data = Ext.encode(form.getFieldValues(true));
    	keops.app.submit(this, this.submitUrl, params, this.submitSuccess);
    },
    
    submitSuccess: function (response) {
    	this.setState('read');
    	data = Ext.decode(response.responseText);
    	this.getForm().setValues(data.data);
    },
    
    cancelChanges: function () {
    	this.store.load({ params: { id: this.store.first().raw.pk } });
    	this.setState('read');
    },
    
    render: function() {
        this.callParent(arguments);
        var me = this;
        var map = new Ext.util.KeyMap(this.el.dom, [ 
            { key: 33, fn: function(k, e) { e.preventDefault(); me.pagingToolbar.movePrevious(); return false; } }, 
            { key: 34, fn: function(k, e) { e.preventDefault(); me.pagingToolbar.moveNext(); return false; } } ,
            { key: 27, fn: function(k, e) { e.preventDefault(); me.cancelChanges(); return false; } } ,
            { key: Ext.EventObject.F3, fn: function(k, e) { e.preventDefault(); me.searchRecord(); return false; } } ,
            { key: 'P', ctrl: true, fn: function(k, e) { e.preventDefault(); me.printDialog(); return false; } },
            { key: 'L', ctrl: true, fn: function(k, e) { e.preventDefault(); return false; } },
            { key: 'E', ctrl: true, fn: function(k, e) { e.preventDefault(); me.editRecord(); return false; } }
        ]);
    },

    
    setState: function (state) {
    	this._state = state;
    	if (state == 'read') read = true; else read = false;
		this.queryById('btn-create').setVisible(read);
    	this.queryById('btn-edit').setVisible(read);
    	this.queryById('btn-save').setVisible(!read);
    	this.queryById('btn-cancel').setVisible(!read);
    	this.getForm().getFields().each(
    	function(item) 
    	{
            if (item.setReadOnly) item.setReadOnly(read);
    	});
    }
});
