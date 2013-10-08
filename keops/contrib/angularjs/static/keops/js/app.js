$.datepicker.setDefaults($.datepicker.regional[document.documentElement.lang]);

var keopsApp = angular.module('keopsApp', ['ngRoute', 'ngSanitize', 'ui.bootstrap', 'infinite-scroll', 'ui.keops']).config(
    function($routeProvider, $locationProvider) {
        $routeProvider.
            when('/action/:id/',
            {
                reloadOnSearch: false,
                templateUrl: function (params) {
                    if (params.view_type) var s = '&view_type=' + params.view_type
                    else var s = '';
                    if (params.query) s += '&query=' + params.query;
                    return '?action=' + params.id + s;
                }
            }).
            when('/action/:id/:view_type',
            {
                reloadOnSearch: false,
                templateUrl: function (params) {
                    if (params.view_type) var s = '&view_type=' + params.view_type
                    else var s = '';
                    if (params.query) s += '&query=' + params.query;
                    return '?action=' + params.id + s;
                }
            })

});


// SharedData factory
keopsApp.factory('SharedData', function($rootScope) {
    var sharedData = {};

    return sharedData;
});


// List factory/controller
keopsApp.factory('List', function($http, SharedData) {
    var List = function() {
        this.items = [];
        this.loading = false;
        this.start = 0;
        this.total = null;
        this.loaded = false;
        this.index = 0;
        SharedData.list = this;
    };

    List.prototype.nextPage = function(model, query) {
        if (this.loading || this.loaded) return;
        this.loading = true;

        var params = {
            model: model,
            start: this.start,
            limit: 25
        }

        if (query) params['query'] = query;

        var url = "/db/grid/?model=" + model + '&start=' + this.start;
        if (this.total === null) { params['total'] = 1; params['limit'] = 100; }
        $http({
            url: '/db/grid/',
            method: 'GET',
            params: params
        }).success(function(data) {
            if (this.total == null) this.total = data.total;
            for (var i=0; i < data.items.length; i++)
                this.items.push(data.items[i]);
            this.start = this.items.length;
            this.loading = false;
            this.loaded = this.items.length == this.total;
        }.bind(this));
    };

    List.prototype.query = function(model, query) {
        this.total = null;
        this.start = 0;
        this.loaded = false;
        this.items = [];
        this.nextPage(model, query);
    };

    return List;
});

keopsApp.controller('ListController', function($scope, $location, List) {
    $scope.list = new List();

    $scope.itemClick = function(url, search, index) {
        $scope.list.index = index;
        $location.path(url).search(search);
    };
});



// Form factory/controller
keopsApp.factory('Form', function($http, SharedData, $location){
    var Form = function() {
        this.item = {};
        this.loading = false;
        this.start = -1;
        this.total = null;
        this.loaded = false;
        this.write = false;
        this.model = null;
        this.element = null;
        this.pk = $location.search()['pk'];
        this.url = "/db/read/?limit=1&model=";
        if (SharedData.list) {
            this.start = SharedData.list.index - 1;
            this.total = SharedData.list.total;
        }
    };

    Form.prototype.nextPage = function() {
        if (this.loading || this.loaded) return;
        this.loading = true;
        var model = this.model;

        this.start++;
        var url = this.url + model + '&start=' + this.start;
        if (this.total === null) url += '&total';
        if (this.pk != null) url += '&pk=' + this.pk;
        $http.get(url).success(function(data) {
            if (this.total === null) this.total = data.total;
            this.item = data.items[0];
            if (!this.pk) $location.search('pk', this.item.pk);
            this.pk = null;
            this.loading = false;
            this.loaded = this.start == this.total - 1;
            this.masterChange();
            delete SharedData.list;
        }.bind(this));
    };

    Form.prototype.prevPage = function() {
        if (this.start === 0) return;
        this.loading = true;
        this.loaded = false;
        var model = this.model;

        this.start--;
        var url = this.url + model + '&start=' + this.start;
        $http.get(url).success(function(data) {
            if (this.total === null) this.total = data.total;
            this.item = data.items[0];
            $location.search('pk', this.item.pk);
            this.loading = false;
            this.masterChange();
        }.bind(this));
    };

    Form.prototype.masterChange = function () {
        // notify form remote items
        var formItem = this.item;
        formItem.items = {};
        items = this.element.find('[remoteitem]');
        remoteitems = [];
        for (var i = 0; i < items.length; i++) remoteitems.push(angular.element(items[i]).attr('name'));
        // make params
        data = { model: this.model, pk: this.item.pk, items: angular.toJson(remoteitems) };
        // load remote data
        $http({
            method: 'GET',
            url: '/db/read/items',
            params: data
        }).
        success(function (data) {
            for (var i = 0; i < items.length; i++) {
                var item = angular.element(items[i]);
                var name = item.attr('name');
                formItem[name] = data[name].items;
            }
        });
    };

    Form.prototype.initForm = function (model) {
        this.model = model;
        this.nextPage();
    };

    return Form;
});

keopsApp.controller('FormController', function($scope, $http, Form, $location, $element) {
    $scope.form = new Form();
    $scope.form.element = $element;

    $scope.search = function (url, search) {
        $location.path(url).search(search);
    };

    $scope.lookupData = function (url, model, query) {
        var promise = $http({
            method: 'GET',
            url: url,
            params: { query: query, model: model }
        })
            .then(function (response) { return response.data; });
        promise.$$v = promise;
        return promise
    };

    $scope.openResource = function (url, search) {
        $location.path(url).search(search).replace();
    };
});
