Ext.define('Keops.form.ModelForm', {
	extend: 'Ext.form.Panel',
	alias: 'widget.modelform',
    newText: 'New',

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
        me.btnCreate = this.queryById('btn-create');
    	me.btnEdit = this.queryById('btn-edit');
    	me.btnSave = this.queryById('btn-save');
    	me.btnCancel = this.queryById('btn-cancel');
    	me.btnPrint = this.queryById('btn-print');
    	me.btnRecord = this.queryById('btn-record');
    	me.btnMore = this.queryById('btn-more');
    },
    
    newRecord: function () {
        var fields = this.storeFields;
        var values = {};
    	this.getForm().getFields().each(
    	function(item)
    	{
            if (fields.indexOf(item.name) > -1) values[item.name] = null;
    	});
        values = this.store.add([values]);
        this.loadRecord(values[0]);
    	this.setState('create');
    },

    editRecord: function () {
    	this.setState('write');
    },

    saveRecord: function () {
        // Only submit modified data
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
        var f = this.store.first();
        if (f && f.raw.pk) {
            this.loadRecord(f);
            this.setState('read');
            this.setLabelText(f.raw.__str__);
        }
        else {
            this.setState(null);
            this.getForm().reset();
        }
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

    setLabelText: function(s) {
        if (!this._labelForm) this._labelForm = this.queryById('form-label');
        if (this._labelForm) this._labelForm.update('<b>' + this.formTitle + '</b>/' + (s || ''));
    },

    setState: function (state) {
        console.log('set sate', state);
    	this._state = state;
        if (!state) {
            read = true;
            this.btnCreate.setVisible(true);
            this.btnEdit.setVisible(false);
            this.btnSave.setVisible(false);
            this.btnCancel.setVisible(false);
            this.btnPrint.setVisible(false);
            this.btnRecord.setVisible(false);
            this.btnMore.setVisible(false);
        }
    	else if (state == 'read') read = true; else read = false;
        if (state) {
            this.btnCreate.setVisible(read);
            this.btnEdit.setVisible(read);
            this.btnSave.setVisible(!read);
            this.btnCancel.setVisible(!read);
            this.btnPrint.setVisible(read);
            this.btnRecord.setVisible(read);
            this.btnMore.setVisible(read);
        }
        if (state == 'create') this.setLabelText(this.newText)
        else if (!state) this.setLabelText('');
        fields = this.storeFields;
    	this.getForm().getFields().each(
    	function(item) 
    	{
            if ((fields.indexOf(item.name) > -1) && item.setReadOnly) item.setReadOnly(read);
    	});
    }
});
