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
    
    confirmDeleteRecord: function(url) {
    	var me = this;
        Ext.Msg.confirm(gettext('Confirm'), gettext('Confirm delete record?'),
            function(sender) {
                if (sender == 'yes') me.deleteRecord(url);
            });
    },

    deleteRecord: function(url) {
        var form = this.getForm();
        var params = { pk: this.pk, model: this.store.proxy.extraParams.model };
        this.doAjax(url, params, 'DELETE');
    },

    doAjax: function(url, params, method) {
        if (!method) method = 'POST';
        var me = this;
        var form = this.getForm();
        me.setLoading(true);
        var success = function (data) {
        	var msg = Ext.decode(data.responseText);
        	if (msg.success) {
        		if (msg.data && msg.data.pk) form.pk = msg.data.pk;
        		if (method == 'DELETE') {
        			if ((me.store.currentPage == 1) || (me.store.currentPage == (me.store.totalCount - 1))) me.store.load();
        			else if (me.store.currentPage < me.store.totalCount) me.store.nextPage();
        			else me.store.previousPage();
        		}
        		else {
	        		//me.setState('read');
	        		app.msg(msg.label, msg.msg);
	        		me.getForm().loadRecord(msg);
	        		//me.clearDetailsChange();
        		}
        	}
        	else if (msg.data) {
        		me.getForm().loadRecord(msg);
        	}
        	else {
        		Ext.Msg.alert(gettext('Error'), msg.msg);
        	}
        }
        keops.app.submit(me, url, params, me.submitSuccess, null, null, method);
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
