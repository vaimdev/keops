
Ext.define('Keops.view.MainView', {
    extend: 'Ext.container.Viewport',

    layout: {
        type: 'border'
    },
    minWidth: 960,
    minHeight: 700,
    autoScroll: true,

    initComponent: function() {
        var me = this;

		keops.app = this;
        Ext.applyIf(me, {
            items: [
                {
                    xtype: 'panel',
                    region: 'west',
                    split: true,
                    id: 'left-menu',
                    width: 230,
                    layout: {
                        hideCollapseTool: false,
                        sequence: false,
                        activeOnTop: true,
                        type: 'accordion'
                    },
                    collapsible: true,
                    title: keops.menuName ? keops.menuName : 'Menu',
                    items: keops.menu
                },
                {
                    xtype: 'panel',
                    region: 'center',
                    autoScroll: true,
                    layout: 'fit',
                    id: 'app-content'
                },
                {
                    xtype: 'panel',
                    region: 'north',
                    baseCls: 'app-header',
                    html: '<div class="site-name">' + keops.siteName + '<span style="font-size: x-small; position: absolute; right: 5px;"><a href="http://www.katrid.com" target="_blank">katrid.com</a></span></div>',
                    id: 'app-header',
                    bodyPadding: '0 0 0 10',
                    title: ''
                },
                {
                    xtype: 'panel',
                    region: 'north',
                    height: 38,
                    id: 'app-menu',
                    bodyBorder: false,
                    border: false,
                    bodyCls: 'x-panel-header-default',
                    title: ''
                }
            ]
        });

        me.callParent(arguments);
    },

    loader: {
        loadMask: gettext('Loading...')
    },
    
    show: function(item) {
    	var c = Ext.getCmp('app-content');
    	if (c.items.length > 0) c.items.items[0].destroy();
    	c.add(item);
    },

    showError: function(msg) {
        Ext.Msg.show({title: gettext('Error'), msg: msg, buttons: Ext.Msg.OK, icon: Ext.MessageBox.ERROR});
    },
    
    submit: function(form, url, params, success, failure, callback, method) {
        var me = this;
        if (!method) method = 'POST'
        if (form) form.setLoading(true);
        else form = keops.app;
    	if (!success) success = function () {};
        if (!failure) failure = function (data) { me.showError(data.status.toString() + ' - ' + gettext(data.statusText) + '<br/>' + data.responseText); console.log(data); };
        if (!callback) callback = function () { form.setLoading(false); };

        if (method == 'DELETE') {
            url += '?' + Ext.urlEncode(params);
            params = null;
        }

    	Ext.Ajax.request({
    		url: url,
    		scope: form,
    		params: params,
    		method: method,
    		success: success,
            failure: failure,
            callback: callback
    	});
    }
});