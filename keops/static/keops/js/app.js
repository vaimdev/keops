$.datepicker.setDefaults($.datepicker.regional[document.documentElement.lang]);

var getval = function (val) {
    if ((val == null) || (val == '')) return null;
    else return val;
};

var keopsApp = angular.module('keopsApp', ['ngRoute', 'ngSanitize', 'ngCookies', 'ui.bootstrap', 'infinite-scroll', 'ui.keops'], function ($routeProvider, $locationProvider, $httpProvider) {

    var interceptor = ['$rootScope', '$q', function (scope, $q) {

        function success(response) {
            // check ajax response is html document
            if ((typeof response.data === 'string') && (response.data.substring(0, 5) == '<!DOC')) {
                window.document.write(response.data);
                // check html document is login form
                var el = window.document.getElementsByName('next')[0];
                $(el).val(window.location);
                return;
            }
            return response;
        }

        function error(response) {
            // check error status
            return $q.reject(response);

        }

        return function (promise) {
            return promise.then(success, error);
        }

    }];
$httpProvider.responseInterceptors.push(interceptor);
}).config(
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
            }).
            when('/menulist/:id',
            {
                templateUrl: function (params) {
                    return '?menulist=' + params.id;
                }
            }).
            when('/accounts/password/change/',
            {
                templateUrl: function (params) {
                    return '/admin/accounts/password/change/';
                }
            }).
            when('/history/:model/:id',
            {
                templateUrl: function (params) {
                    return '/admin/history/?model=' + params.model + '&pk=' + params.id;
                }
            }).
            when('/report/:option',
            {
                templateUrl: function (params) {
                    console.log('report', params);
                    return '/report/' + params.option + '/?' + $.param(params);
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
        this.q = query;
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
    $scope.selection = 0;

    $scope.itemClick = function(url, search, index) {
        $scope.list.index = index;
        $location.path(url).search(search);
    };

    $scope.toggleCheckAll = function() {
        var c = $('#action-toggle')[0].checked;
        $('.action-select').each(function () { $(this).checked = true; $(this).prop('checked', c); });
        $scope.selection = $('.action-select:checked').length;
    };

    $scope.selectItem = function(item) {
        if (item) {
            item._selected_action = true;
            $scope.$apply();
        }
        $('#action-toggle').prop('checked', $('.action-select:not(:checked)').length === 0);
        $scope.selection = $('.action-select:checked').length;
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
        this.readonly = null;
        this.pk = $location.search()['pk'];
        this.url = "/db/read/?limit=1&model=";
        if (SharedData.list) {
            this.start = SharedData.list.index - 1;
            this.total = SharedData.list.total;
        }
    };

    Form.prototype.newItem = function (pk) {
        var params = {model: this.model};
        var url = '/db/new/';
        if (pk) {
            params['action'] = 'duplicate_selected';
            params['pk'] = pk;
            url = '/admin/action/';
        }
        $http({
            method: 'POST',
            url: url,
            params: params
        }).success(function(data) {
                this.write = true;
                this.item = data;
                this.item.__str__ = gettext('<New>')
            }.bind(this));
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
        var items = this.element.find('[remoteitem]');
        var remoteitems = [];
        for (var i = 0; i < items.length; i++) remoteitems.push(angular.element(items[i]).attr('name'));
        // make params
        var data = { model: this.model, pk: this.item.pk, items: angular.toJson(remoteitems) };
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
                if (data[name].items) formItem[name] = data[name].items;
                else formItem[name] = data[name];
            }
        });
    };

    Form.prototype.cancel = function () {
        this.write = false;
        this.refresh();
    };

    Form.prototype.refresh = function () {
        var pk = $location.search()['pk'];
        if (pk)
        $http({
            method: 'GET',
            url: '/db/read',
            params: { limit: 1, model: this.model, pk: $location.search()['pk'] }
        }).success(function (data) {
                jQuery.extend(this.item, data.items[0]);
                this.masterChange();
            }.bind(this));
    };

    Form.prototype.getGridFields = function () {
        var items = this.element.find('[grid-field]');
        var r = {};
        // check item changes
        for (var i = 0; i < items.length; i++) {
            var item = angular.element(items[i]);
            var name = item.attr('name');
            r[name] = this.item[name];
        };
        return r;
    };

    Form.prototype.initForm = function (model) {
        this.model = model;
        this.nextPage();
    };

    return Form;
});

keopsApp.controller('FormController', function($scope, $http, Form, $location, $element, $modal, $timeout, $sce) {
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
        return promise;
    };

    $scope.openResource = function (url, search) {
        $location.path(url).search(search).replace();
    };

    $scope.fieldChangeCallback = function (field) {
        var v = $scope.form.item[field];
        $http({
            method: 'GET',
            url: '/db/field/change',
            params: { model: $scope.form.model, field: field, value: v }
        }).
            success(function (data) {
                jQuery.extend($scope.form.item, data.values);
            });
    };

    $scope.showDetail = function (model, detail, item) {
        var field = $scope.form.item[detail];
        var options = {
            controller: 'DialogController',
            resolve: {
                data: function () {
                    form = { item: {} }
                    if (item) {
                        jQuery.extend(form.item, item);
                        form.ref = item;
                    }
                    form.field = field;
                    form.instance = $scope.form;
                    return form;
                }
            },
            templateUrl: '/admin/detail/?model=' + model + '&field=' + detail
        };
        var dialog = $modal.open(options);

        dialog.result.then(function (form) {
            form.instance.nestedDirty = true;
            if (form.ref) {
                if (!form.item.__state__) form.item.__state__ = 'modified';
                jQuery.extend(form.ref, form.item);
            }
            else {
                form.item.__state__ = 'created';
                form.field.push(form.item);
            }
        }, function () {
        });
    };

    $scope.alerts = [];

    $scope.addAlert = function(type, msg) {
        msg = $sce.trustAsHtml(msg);
        if (type == 'error') type = 'danger';
        $scope.alerts.push({type: type, msg: msg, timer: $timeout(function() {
            //$scope.alerts.splice(0, 1);
            }, 10000)
        });
    };

    $scope.closeAlert = function(index) {
        var alert = $scope.alerts[index];
        $timeout.cancel(alert.timer);
        $scope.alerts.splice(index, 1);
    };

    $scope.confirmDelete = function (message) {
        var options = {
            controller: 'DialogController',
            resolve: {
                data: function () {
                    return $scope.form;
                }
            },
            templateUrl: '/static/keops/html/confirm_delete.html'
        };
        var dialog = $modal.open(options);

        dialog.result.then(function (form) {
            $http({
                method: 'POST',
                url: '/admin/action/?action=delete_selected',
                params: { pk: form.item.pk, model: form.model }
            }).success(function (data) {
                    for (var i in data) {
                        var i = data[i];
                    $scope.addAlert(i.alert, i.message);
                    }
                    if (data[data.length-1].success) $scope.form.nextPage();
                }).error(function (data) {
                    window.open('error').document.write(data);
                });
        }, function () {
        });
    };

    $scope.sum = function (item, attr) {
        var r = 0;
        for (var i in item) {
            if (attr) r += parseFloat(item[i][attr]);
            else r += item[i];
        }
        return r;
    };

    $scope.tableRowFilter = function (obj) {
        return obj.__state__ !== 'deleted';
    };

    $scope.submit = function () {
        var form = this.dataForm;
        if (form.$dirty || $scope.form.nestedDirty) {
            var data = {};
            for (var i in form) {
                if (i[0] !== '$') {
                    var el = form[i];
                    var v = $scope.form.item[i];
                    if (el.$dirty) {
                        if (typeof v === 'object') {
                            if (v.length) {
                                var r = [];
                                for (var n in v) r.push(v[n].id);
                                data[el.$name] = r;
                            }
                            else data[el.$name] = v['id'];

                        }
                        else data[el.$name] = v;
                    }
                }
            };
            // detect nested grid fields
            var nested = $scope.form.getGridFields();
            for (var n in nested) {
                var nestedData = [];
                for (i = 0; i < nested[n].length; i++) {
                    var obj = {};
                    var item = nested[n][i];
                    if (item.__state__ === 'deleted') obj.action = 'DELETE';
                    else if (item.__state__ === 'modified') obj.action = 'UPDATE';
                    else if (item.__state__ === 'created') obj.action = 'CREATE';
                    if (obj.action) {
                        obj.data = {};
                        jQuery.extend(obj.data, item);
                        for (var x in obj.data) {
                            var v = obj.data[x];
                            if (typeof v === 'object')
                                obj.data[x] = v.id;
                        };
                        nestedData.push(obj);
                    };
                };
                if (nestedData.length > 0) data[n] = nestedData;
            };
            console.log(data);
            return $http.post(
                '/db/submit/', { model: this.form.model, pk: this.form.item.pk, data: data }
            ).
            success(function (data, status, headers, config) {
                    console.log(data);

                $scope._evalData(data);

                }.bind(this)).
                error(function (data) {
                    window.open('error').document.write(data);
                });
        }
        else $scope.addAlert('error', gettext('No pending data to submit!'))
    }

    $scope.adminAction = function(action, data) {
        $scope.alerts.length = 0;
        var params = {model: this.model};
        var url = '/admin/action/';
        var pk = this.form.pk;
        params['action'] = action;
        params['pk'] = this.form.pk;
        params['model'] = this.form.model;
        params['data'] = data;
        $http.post(url, params).success(function(data) {
                $scope._evalData(data);
            });
    };

    $scope._evalData = function(data) {
        for (var i in data) {
            i = data[i];
            var s = i.message;
            if (i.success && (typeof i.message === 'object')) {
                $scope.form.nestedDirty = false;
                form.$setPristine();
                $scope.form.write = false;
                jQuery.extend($scope.form.item, data.data);
            }
            else if (!i.success) {
                $scope.addAlert(i.alert, s);
            }
            else $scope.addAlert(i.alert, s);
        }
    };

});

keopsApp.controller('MenuController', function($scope, $http, Form, $location, $modal, $route) {
    $scope.closedMenuClick = function (url) {
        $location.path(url);
    }

    $scope.showDialog = function (template) {
        template = template.replace('/', '=');
        var options = {
            controller: 'DialogController',
            resolve: {
                data: function () {
                    return null
                }
            },
            templateUrl: '?' + template
        };
        var dialog = $modal.open(options);
    };

    $scope.itemClick = function (url, dialog) {
        if (dialog) $scope.showDialog(url)
        else $location.url(url);
    }
});

keopsApp.controller('DialogController', function($scope, $http, Form, $location, $modalInstance, data) {
    $scope.form = data;
    $scope.gettext = gettext;

    $scope.ok = function () {
        var v = true;
        if ($scope.form) v = $scope.form;
        $modalInstance.close(v);
        console.log('detail', this.detailForm);
    }

    $scope.cancel = function () {
        $modalInstance.dismiss(false);
    }

    $scope.submit = function () {
        if (this.detailForm.$invalid)
        console.log(this.detailForm);
        else $scope.ok();
    }
});

keopsApp.run(function($rootScope, $http, $cookies){
    $http.defaults.headers.post['X-CSRFToken'] = $cookies.csrftoken;
});
