var keopsApp = angular.module('keopsApp', ['ngRoute', 'ui.bootstrap', 'infinite-scroll', 'ui.keops']).config(
    function($routeProvider, $locationProvider) {
            $routeProvider.
                    when('/action/:id', {
                            templateUrl: function(params) {
                                if (params.view_type) var s = '&view_type=' + params.view_type
                                else var s = '';
                                if (params.query) s += '&query=' + params.query;
                                return '?action=' + params.id + s;
                            }
                    });

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

    List.prototype.nextPage = function(model) {
        if (this.loading || this.loaded) return;
        this.loading = true;

        var url = "/db/grid/?model=" + model + '&start=' + this.start;
        if (this.total === null) url += '&total=1&limit=200'
        else url += '&limit=25';
        $http.get(url).success(function(data) {
            if (this.total == null) this.total = data.total;
            for (var i=0; i < data.items.length; i++)
                this.items.push(data.items[i]);
            this.start = this.items.length;
            this.loading = false;
            this.loaded = this.items.length == this.total;
        }.bind(this));
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
keopsApp.factory('Form', function($http, SharedData){
    var Form = function() {
        this.item = {};
        this.loading = false;
        this.start = -1;
        this.total = null;
        this.loaded = false;
        this.write = false;
        this.url = "/db/read/?limit=1&model=";
        if (SharedData.list) {
            this.start = SharedData.list.index - 1;
            this.total = SharedData.list.total;
        }
    };

    Form.prototype.nextPage = function(model) {
        if (this.loading || this.loaded) return;
        this.loading = true;

        this.start++;
        var url = this.url + model + '&start=' + this.start;
        if (this.total === null) url += '&total=1'
        $http.get(url).success(function(data) {
            if (this.total === null) this.total = data.total;
            this.item = data.items[0];
            this.loading = false;
            this.loaded = this.start == this.total - 1;
        }.bind(this));
    };

    Form.prototype.prevPage = function(model) {
        if (this.start === 0) return;
        this.loading = true;
        this.loaded = false;

        this.start--;
        var url = this.url + model + '&start=' + this.start;
        $http.get(url).success(function(data) {
            if (this.total === null) this.total = data.total;
            this.item = data.items[0];
            console.log(this.items);
            this.loading = false;
        }.bind(this));
    };
    return Form;
});

keopsApp.controller('FormController', function($scope, $http, Form, limitToFilter, $location) {
    $scope.form = new Form();

    $scope.lookupData = function (model, query) {
        return $http({ method: 'GET', url: '/db/lookup/', params: { model: model, query: query } }).then(
            function (response) {
                return limitToFilter(response.data.items, 15);
            });
    };

    $scope.search = function (url, query) {
        console.log(url + query);
        $location.path(url).search(query);
    };
});
