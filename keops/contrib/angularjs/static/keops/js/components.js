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

ui.directive('uiMask', function() {
    return {
        restrict: 'A',
        require : 'ngModel',
        link : function (scope, element, attrs, controller) {
            var maskStore = attrs.uiMaskStore;

            $(function() {
                element.mask(attrs['uiMask']);
                return element.bind('keyup blur', function(event) {
                    if (maskStore)
                        return controller.$setViewValue(element.val());
                    else
                        return controller.$setViewValue(element.mask());
                });
            });
        }
    }
});

ui.directive('uiMoney', function($filter) {
    return {
        restrict: 'A',
        require : 'ngModel',
        link : function (scope, element, attrs, ngModel) {

            var precision = attrs.uiMoneyPrecision || 2;
            $(function() {
                var thousands = attrs.uiMoneyThousands;
                var decimal = attrs.uiMoneyDecimal;
                var symbol = attrs.uiMoneySymbol;
                var negative = attrs.uiMoneyNegative;
                element.maskMoney({symbol: symbol, thousands: thousands, decimal: decimal, precision: precision, allowNegative: negative, allowZero: true});
            });

            ngModel.$render = function () {
                if (ngModel.$viewValue) {
                element.val($filter('number')(ngModel.$viewValue, precision));
                }
            };
        }
    }
});

ui.directive('datePicker', function() {
    return {
        restrict: 'A',
        require : 'ngModel',
        link: function(scope, element, attrs, controller) {
            var el = element.datepicker({
                dateFormat: attrs.dateFormat,
                showOn: 'button',
                onSelect: function(dateText, datepicker) {
                    controller.$setViewValue(dateText);
                }
            });
            el = el.next('.ui-datepicker-trigger');
            el.addClass('btn').html('<i class="icon-calendar"></i>');
        }
    }
});

ui.directive('dateTimePicker', function() {
    return {
        restrict: 'A',
        //require : 'ngModel',
        link: function(scope, element, attrs, controller) {
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

var s = $.fn.select2.defaults.formatNoMatches();
$.fn.select2.defaults.formatNoMatches = function () { return s + ' <a style="margin-left: 20px;" class="btn btn-info">' + gettext('Create New...') + '</a>'; },

ui.directive('combobox', function() {
    return {
        restrict: 'A',
        require : 'ngModel',
        link: function(scope, element, attrs, ngModel, controller) {
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

            ngModel.$render = function () {
                if (typeof ngModel.$viewValue === 'object')
                element.select2('data', ngModel.$viewValue);
                else
                element.select2('val', ngModel.$viewValue);
            };
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
        // TODO adjust to get current locale short date time format
        if (dateString) {
            var fmt = $locale.DATETIME_FORMATS.mediumDate.toUpperCase();
            var m = moment(dateString, fmt)
            return m.format('LL') + ' (' + m.fromNow() + ')';
        }
        else return '';
    };
});
