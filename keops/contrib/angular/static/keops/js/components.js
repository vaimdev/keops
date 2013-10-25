var ui = angular.module('ui.keops', []);

ui.directive('ngEnter', function() {
    return function(scope, element, attrs) {
        element.bind("keydown keypress", function(event) {
            if (event.which === 13) {
                event.preventDefault();
                scope.$apply(function () {
                    scope.$eval(attrs.ngEnter);
                });
            }
        });
    };
});

ui.directive('datePicker', function() {
    return {
        restrict: 'A',
        require : 'ngModel',
        link: function(scope, element, attrs, controller) {
            attrs.uiMaskStore = 1;
            var el = element.datepicker({
                dateFormat: attrs.dateFormat,
                showOn: 'button',
                onSelect: function(dateText, datepicker) {
                    controller.$setViewValue(dateText);
                }
            });
            el.next('.ui-datepicker-trigger').addClass('btn btn-sm btn-default').html('<span class="glyphicon glyphicon-calendar"></span>');
        }
    }
});

ui.directive('dateTimePicker', function() {
    return {
        restrict: 'A',
        //require : 'ngModel',
        link: function(scope, element, attrs, controller) {
            attrs.uiMaskStore = 1;
            var el = element.datetimepicker({
                dateFormat: attrs.dateFormat,
                timeFormat: attrs.timeFormat,
                alwaysSetTime: false,
                showOn: 'button',
                onSelect: function(dateText, datepicker) {
                    scope.date = dateText;
                    scope.$apply();
                }
            });
            el = el.next('.ui-datepicker-trigger');
            el.addClass('btn').html('<i class="icon-calendar"></i>');
        }
    }
});


ui.directive('uiMask', function() {
    return {
        restrict: 'A',
        require : 'ngModel',
        link : function (scope, element, attrs, ngModel) {
            var maskStore = attrs.uiMaskStore;

            $(function() {
                element.mask(attrs['uiMask']);
                return element.bind('keyup blur', function(event) {
                    if (maskStore)
                        return ngModel.$setViewValue(element.val());
                    else
                        return ngModel.$setViewValue(element.mask());
                });
            });
        }
    }
});

ui.directive('uiMoney', function($filter) {
    return {
        restrict: 'A',
        require : 'ngModel',
        link : function (scope, element, attrs, ngModel, controller) {

            var precision = attrs.uiMoneyPrecision || 2;
            $(function() {
                var thousands = attrs.uiMoneyThousands;
                var decimal = attrs.uiMoneyDecimal;
                var symbol = attrs.uiMoneySymbol;
                var negative = attrs.uiMoneyNegative;
                element.maskMoney({symbol: symbol, thousands: thousands, decimal: decimal, precision: precision, allowNegative: negative, allowZero: true}).
                bind('keyup blur', function(event) {
                        ngModel.$setViewValue(element.val().replace(RegExp('\\' + thousands, 'g'), '').replace(RegExp('\\' + decimal, 'g'), '.'));
                    }
                );
            });

            ngModel.$render = function () {
                if (ngModel.$viewValue) element.val($filter('number')(ngModel.$viewValue, precision));
                else element.val('');
            };
        }
    }
});

ui.directive('uiTable', function() {
    return {
        restrict: 'A',
        require : 'ngModel',
        link: function(scope, element, attrs, controller) {
            if (attrs.ngChange)
            scope.$on('rowChange', function (event) {
                scope.$eval(attrs.ngChange);
            })
        }
    }
});

ui.directive('uiTableRow', function() {
    return {
        restrict: 'A',
        link: function(scope, element, attrs, controller) {
            if (scope.$last) scope.last = true;
            for (var i in scope.item)
            scope.$watch('item.' + i, function() {
                scope.$emit('rowChange');
            });
        }
    }
});

//var s = $.fn.select2.defaults.formatNoMatches();
//$.fn.select2.defaults.formatNoMatches = function () { return s + ' <a style="position: absolute; right: 10px; cursor: pointer;">' + gettext('Create...') + '</a>'; },

ui.directive('combobox', function() {
    return {
        restrict: 'A',
        require : 'ngModel',
        link: function(scope, element, attrs, controller) {
            var url = attrs.lookupUrl;

            if (url) {
                var el = element.select2({
                    ajax: {
                        url: url,
                        dataType: 'json',
                        quietMillis: 500,
                        data: function (term, page) {
                            return {
                                query: term,
                                limit: 10,
                                start: page - 1
                            }
                        },
                        results: function (data, page) {
                            var more = (page * 10) < data.total;
                            return { results: data.data, more: more };
                        }
                    }
                });
            }
            else
            var el = element.select2();
            controller.$render = function () {
                if (typeof controller.$viewValue === 'object')
                element.select2('data', controller.$viewValue);
                else
                element.select2('val', controller.$viewValue);
            };
            el.on('change', function () {
                scope.$apply(function () {
                    controller.$setViewValue(el.select2('data'));
                });
            });
        }
    }
});

ui.filter('dateFromNow', function ($locale) {
    return function (dateString) {
        // TODO adjust to get current locale short date time format
        if (dateString) {
            var fmt = $locale.DATETIME_FORMATS.mediumDate.toUpperCase() + ' ' + $locale.DATETIME_FORMATS.shortTime;
            var m = moment(dateString, fmt)
            return m.format('LLLL') + ' (' + m.fromNow() + ')';
        }
        else return '';
    };
});

ui.filter('dateFrom', function ($locale) {
    return function (dateString) {
        if (dateString) {
            var fmt = $locale.DATETIME_FORMATS.mediumDate.toUpperCase();
            var m = moment(dateString, fmt);
            return m.format('LL') + ' (' + m.fromNow() + ')';
        }
        else return '';
    };
});
