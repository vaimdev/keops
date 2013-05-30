Ext.define('Orun.form.field.ComboBox', {
    extend: 'Ext.form.field.ComboBox',
    alias: 'widget.dbcombobox',
    
    buttonSearchTitle: 'Search',
    buttonOpenTitle: 'Open Resource',
    buttonSearchVisible: false,
    buttonOpenVisible: false,
    
    initComponent: function() {
    	this.store = this.createStore();
        this.triggerAction = 'all';
        if (this.buttonSearchVisible)
	    	this.trigger2Cls = Ext.baseCSSPrefix + 'form-search-trigger';
	    if (this.buttonOpenVisible)
	    	this.trigger3Cls = Ext.baseCSSPrefix + 'form-open-trigger';
        this.callParent(arguments);
    },
    
    afterRender: function(){
        this.callParent();
        if (this.buttonSearchVisible)
	        this.triggerEl.item(1).dom.title = this.buttonSearchTitle;
	    if (this.buttonOpenVisible)
	        this.triggerEl.item(2).dom.title = this.buttonOpenTitle;
        /*.menu = Ext.create('Ext.menu.Menu', {
        	items: [
        		{ text: 'Teste' },
        		{ text: 'Teste1' }
        	]
        })*/;
    },

    
    onTrigger2Click: function(sender) {
    	var me = this;
		me.setLoading(true);
    	Orun.Ajax.request('form/searchlookup', { field: this.storeFilter }, 
    		function(data) {
    			_e = eval(data.responseText); _e.caller = me;
    		},
    		null,
    		function() {
    			me.setLoading(false); 
    		});
    },
    
    setKeyValue: function(key) {
    	var me = this;
    	Orun.Ajax.request('db/lookup', { model: this.storeModel, pk: key, emptyrow: '0' },
    	function(data) {
    		d = Ext.decode(data.responseText).items;
    		if (d.length > 0) me.setValue(d);
    	});
    },

    onTrigger3Click: function(sender) {
        if (this.relatedForm) eval(this.relatedForm);
    },
    
    createStore: function() {
    	var me = this;
    	var store = Ext.create('Ext.data.Store', {
    		fields: me.storeFields,
    		targetComponent: me,
            listeners: {
                load: function(data) {
                    //if (!this.targetComponent.isDirty())
                    //this.targetComponent.reset();
                }
            },
    		totalProperty: me.storeTotalProperty,
    		proxy: {
    			type: 'ajax',
    			url: me.storeUrl,
    			extraParams: {
    				model: me.storeModel,
    				command: me.command,
    				fields: me.displayFields
    			},
    			reader: {
    				type: 'json',
    				root: me.storeRoot
    			}
    		}
    	});
        if (this.storeFilter) store.proxy.extraParams.field = Ext.encode(this.storeFilter);
        return store;
    },
    
    setValue: function(value) {
    	var me = this;
    	if (value instanceof Array) {
    		if ((value.length > 0) && !Ext.isDefined(value[0].dirty)) {
	    		me.store.removeAll();
	    		me.store.isLoaded = true;
	    		me.store.add(value[0]);
                me.lastQuery = value[0].text;
	    		value = value[0].id;
    		}
    	}
    	//else if (!value && this.store.isLoaded) { this.doQuery('', true, true); }
        this.callParent([value]);
    }
});

Ext.define('Orun.grid.Panel', {
    extend: 'Ext.grid.Panel',
    alias: 'widget.dbgrid',

    initComponent: function() {
    	var me = this;
    	me.storeRoot = 'items';
    	me.store = me.createStore();
    	this.store.proxy.extraParams.linkField = this.linkField;
    	this.clearChanges();
		for (c in this.columns) {
			var col = this.columns[c];
			if (col.summaryType == 'sum') {
		        col.summaryRenderer = function(value, summaryData, dataIndex) {
		        	value = parseFloat(value);
		            return Ext.util.Format.number(Ext.util.Format.number(value, ',0.00')); 
		        }
			}
		}
        this.selModel = this.createSelModel();
		this.callParent(arguments);
		if (this.editOnDblClick) this.on('itemdblclick', function() { me.doEditAction(arguments); });
	},
    
    createSelModel: function() {
        return Ext.create("Ext.selection.CheckboxModel");
    },
	
	clearChanges: function() {
    	this.store._newRecords = [];
    	this.store._updatedRecords = [];
    	this.store._removedRecords = [];
	},
	
    _doAction: function() {
        var form = this.up("form");
        if (form.state == 'browse') form.changeState("edit");
    },

	doAddAction: function(sender) {
		this._doAction();
		this.up("form").showDetail(this, "insert");
	},
	
	doEditAction: function(sender) {
        var sel = this.getSelectionModel().getSelection();
        if (sel.length > 0) {
            this._doAction();
            this.up("form").showDetail(this, "edit");
        }
	},
	
	doDeleteAction: function(sender) {
		this._doAction();
		var sel = this.getSelectionModel().getSelection();
		for (i in sel) this.store.remove(sel[i]);
	},
	
	prepareDirtyData: function(dirtyData, action) {
		var ret = [];
		for (i in dirtyData) ret.push({ action: action, pk: dirtyData[i].data.pk, data: dirtyData[i].raw });
		return ret;
	},
	
	getDirtyData: function() {
		var ret = this.prepareDirtyData(this.store._removedRecords, 'DELETE');
		ret = ret.concat(this.prepareDirtyData(this.store._newRecords, 'INSERT'));
		ret = ret.concat(this.prepareDirtyData(this.store._updatedRecords, 'UPDATE'));
		return { model: this.storeModel, fieldName: this.fieldName, linkField: this.linkField, data: ret};
	},
	
	setMasterValue: function(value) {
		var me = this;
		this.masterValue = value;
		me.store.proxy.extraParams.masterValue = value;
		if (value) me.store.load();
		else me.store.loadRecords([]);
	},
	
	sync: function(success, failure) {
		// sync store to server
		for (i in this.store._removedRecords) {
			var record = this.store._removedRecords[i];
			var data = { pk: record.data.pk };
			data.model = this.storeModel;
			this.up("form").ajaxRequest('db/destroy', data, success, failure);
		}
		for (i in this.store._newRecords) {
			var record = this.store._newRecords[i];
			var data = record.raw;
			data._model = this.storeModel;
			if (data[this.linkField] == undefined)
				data[this.linkField] = this.up('form').getForm().pk;
			this.up("form").ajaxRequest('db/save', data, success, failure);
		}
		for (i in this.store._updatedRecords) {
			var record = this.store._updatedRecords[i];
			var data = record.raw;
			data._model = this.storeModel;
			data.pk = record.data.pk;
			for (fk in this.storeForeignKeys) delete data[this.storeForeignKeys[fk]];
			this.up("form").ajaxRequest('db/save', data, success, failure);
		}
	},
	
    createStore: function() {
    	var me = this;
    	return Ext.create('Ext.data.Store', {
    		fields: me.storeFields,
    		listeners: {
    			add: function(store, records) {
    				this._newRecords.push(records[0]);
					me.getView().getFeature(0).refresh();
    			},
    			update: function(store, record) {
    				if (this._updatedRecords.indexOf(record) == -1) this._updatedRecords.push(record);
					me.getView().getFeature(0).refresh();
    			},
    			remove: function(store, record) {
    				this._removedRecords.push(record);
					me.getView().getFeature(0).refresh();
    			},
    			load: function() {
    				this._newRecords = [];
    				this._updatedRecords = [];
    				this._removedRecords = [];
    			}
    		},
    		//autoLoad: true,
    		proxy: {
    			type: 'ajax',
    			noCache: false,
    			url: me.storeUrl,
    			extraParams: {
    				model: me.storeModel
    			},
    			reader: {
    				type: 'json',
    				root: me.storeRoot,
    				id: 'pk'
    			}
    		}
    	});
    }
});

Ext.grid.column.Column.override({
    initComponent: function() {
    	var me = this;
		if (typeof(me.renderer) === 'string')
			me.renderer = eval('_=' + me.renderer);
		this.callParent(arguments);
	}
});
