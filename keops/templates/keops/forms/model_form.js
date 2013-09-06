{% load i18n %}
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
        {% if state != 'create' %}
		autoLoad: true,
        {% endif %}
		listeners: {
            beforeload: function() {
                this._form.setLoading(keops.msgs.loading);
            },
			load: function() {
				var form = this._form;
				if (form) {
					var r = this.data.first();
                    if (r) {
                        form.loadRecord(r);
                        form.pk = r.raw.pk;
                        form.setLabelText(r.raw.__str__);
                        form.setState('read');
                    }
                    else form.setState(null);
                    form.setLoading(false);
				}
			}
		}
    });
// form
    var __form = Ext.create("Keops.form.ModelForm", {
    autoScroll: true,
    border: false,
    layout: "column",
	storeFields: {{ fields|safe }},
    submitUrl: '{% url 'keops.views.db.submit' %}',
    defaults: { padding: "5 0 0 8" },
    items: {{ items|safe }},
    store: __store,
    trackResetOnLoad: true,

    formTitle: '{{ form.title|capfirst }}',
    formLabel: '{{ form.label|capfirst }}',
    newText: '{{ _('new')|capfirst }}',

    stateChange: function (state) {
    	
    },
    dockedItems: [{
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
                //html: '<table style="width: 100%"><tr><td style="vertical-align: top; font-size: 13px;"><a style="font-weight: bold" href="#action={{ action.pk }}&view_type=list"><label id="form-label">{{ form.label|capfirst }}</label></a> %s<div style="font-size: 11px; font-weight: normal; margin-top: 5px; text-shadow: none;">{{ form.help_text }}</div></td><td style="text-align: right; vertical-align: bottom; width: 400px;">{% include "keops/forms/search_header.html" %}</td></tr></table>'//__header.replace('%s', '')
            }, {
                xtype: 'container',
                items: [
                {
                xtype: 'triggerfield',
                style: 'background-color: #ffffff',
                emptyText: '{{ _("search")|capfirst }}',
                width: 230,
                onTriggerClick: function() {
                    window.location.href = '#action={{ action.pk }}&view_type=list&' + Ext.Object.toQueryString({q: this.getValue()});
                },
                trigger1Cls: Ext.baseCSSPrefix + 'form-search-trigger'
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
                    { text: '{{ _("create")|capfirst }}', itemId: 'btn-create', handler: function() { this.up('form').newRecord(); } },
                    { text: '{{ _("edit")|capfirst }}', itemId: 'btn-edit', handler: function() { this.up('form').editRecord(); } },
                    { text: '{{ _("save")|capfirst }}', hidden: true, itemId: 'btn-save', cls: 'x-btn-red-button', overCls: 'btn-red-button-over', handler: function() { this.up('form').saveRecord(); } },
                    { text: '{{ _("cancel")|capfirst }}', hidden: true, itemId: 'btn-cancel', handler: function() { this.up('form').cancelChanges(); } },
                    { xtype: 'tbspacer', margin: '0 5 0 5' },
                    { text: '{{ _("print")|capfirst }}', itemId: 'btn-print' },
                    { text: '{{ _("record")|capfirst }}', itemId: 'btn-record',
                        menu: { xtype: 'menu',
                            items: [{ text: '{{ _("duplicate")|capfirst }}' }, { text: '{{ _("delete")|capfirst }}'}]
                        }
                    },
                    { text: '{{ _("more")|capfirst }}', itemId: 'btn-more' },
                    { xtype: 'tbspacer', margin: '0 5 0 5' }
                ]
            }]
    }, {
    	xtype: 'pagingtoolbar',
    	bodyStyle: 'background-color: #eee;',
    	store: __store,
    	dock: 'bottom'
    }]});
    __store._form = __form;
{% if state == 'create' %}
__form.newRecord();
{% else %}
__form.setState(null);
{% endif %}
    keops.app.show(__form);
