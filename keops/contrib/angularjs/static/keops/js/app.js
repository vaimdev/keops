angular.module('keopsApp', ['ngRoute', 'ui.bootstrap']).config(
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
