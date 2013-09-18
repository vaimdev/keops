var keopsApp = angular.module('keopsApp', ['ngRoute', 'ui.bootstrap', 'infinite-scroll']).config(
    function($routeProvider, $locationProvider) {
            $routeProvider.
                    when('/action/:id', {
                            templateUrl: function(params) {
                                if (params.view_type) var s = '&view_type=' + params.view_type
                                else var s = '';
                                return '?action=' + params.id + s;
                            }
                    });

});

keopsApp.factory('List', function($http){
    var List = function() {
        this.items = [];
        this.busy = false;
        this.after = '';
    };

    List.prototype.nextPage = function(model) {
        if (this.busy) return;
        this.busy = true;

        var url = "/db/grid/?model=" + model;
        $http.get(url).success(function(data) {
            for (var i=0; i < data.items.length; i++)
                this.items.push(data.items[i]);
            console.log(this.items);
            this.busy = false;
        }.bind(this));
    };
    return List;
})

keopsApp.controller('ListController', function($scope, List) {
    $scope.list = new List();
})
