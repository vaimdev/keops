
var keops = { siteName: '', htmlMenu: '', menuName: '', msgs: {} };

Ext.Loader.setConfig({
    enabled: true
});

Ext.application({
    views: [
        'MainView'
    ],
    appFolder: '/static/keops/app',
    autoCreateViewport: true,
    name: 'Keops'
});

(function(){
    var loadPage = function(url){
    	if (url) {
    	
    	// prevent reload form
    	keops.app.setLoading(gettext('Loading...'));
    	Ext.Ajax.request({
    		url: '?' + url,
    		success: function(response) {
    			try {
  					eval(response.responseText);
  				}
  				catch (err)
  				{
  					console.log(response.responseText);
                    throw err;
  				}
    		},
    		callback: function(response) {
    			keops.app.setLoading(false);
    		}
    	});
    	};
    }

    var getHashValue = function() {
        var arr = window.location.hash.split("#");
        var hasValue = arr[1];
        if (typeof hasValue == "undefined") {
            return false;
        }
        var hashLen = hasValue.indexOf("?");
        if(hashLen>0){
            hasValue = hasValue.substring(0,hashLen);
        }
        return hasValue;
    }

    //hash change event listener
    var onHashChange = function(event) {
        var lastHash = getHashValue();
        (function watchHash() {
            var hash = getHashValue();
            if (hash !== lastHash) {
                event();
                lastHash = hash;
            }
            var t = setTimeout(watchHash, 100);

        })();

    } 
    
    onHashChange(function() {
        var url = getHashValue();
        loadPage(url);
    });
})();

Ext.define('Keops.tree.Menu', {
    extend: 'Ext.tree.Panel',
    alias: 'widget.treemenu',
    listeners: {
    	itemclick: function(node, e) {
    		window.location.href = e.data.href;
    	}
    }
});
