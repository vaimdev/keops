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

ui.directive('datePicker', function($locale) {
    return {
        restrict: 'A',
        require : 'ngModel',
        link: function(scope, element, attrs, controller) {
            attrs.uiMaskStore = 1;
            var el = element.datepicker({
                todayBtn: true,
                todayHighlight: true,
                autoclose: true,
                forceParse: false,
                language: document.documentElement.lang,
                format: attrs.format || $locale.DATETIME_FORMATS.mediumDate.toLowerCase()
            }).on('changeDate', function() {
                    controller.$setViewValue(el.val());
                    scope.$apply();
                });
            controller.$render = function () {
                el.datepicker('update', controller.$viewValue);
            };
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

ui.directive('decimal', function($filter) {
    return {
        restrict: 'A',
        require : 'ngModel',
        link : function (scope, element, attrs, controller) {

            var precision = attrs.uiMoneyPrecision || 2;

//            $(function() {
                var thousands = attrs.uiMoneyThousands || django.get_format('THOUSAND_SEPARATOR');
                var decimal = attrs.uiMoneyDecimal || django.get_format('DECIMAL_SEPARATOR');
                var symbol = attrs.uiMoneySymbol;
                var negative = attrs.uiMoneyNegative || true;
                var el = element.maskMoney({symbol: symbol, thousands: thousands, decimal: decimal, precision: precision, allowNegative: negative, allowZero: true}).
                bind('keyup blur', function(event) {
                        controller.$setViewValue(element.val().replace(RegExp('\\' + thousands, 'g'), '').replace(RegExp('\\' + decimal, 'g'), '.'));
                        scope.$apply();
                    }
                );
//            });

            controller.$render = function () {
                if (controller.$viewValue) element.val($filter('number')(controller.$viewValue, precision));
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

ui.directive('combobox', function($location) {
    return {
        restrict: 'A',
        require : 'ngModel',
        link: function(scope, element, attrs, controller) {
            var url = attrs.lookupUrl;
            var multiple = attrs['multiple'];
            var allowCreate = attrs.comboboxShowCreate;
            if (url) {
                var cfg = {
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
                            if (!multiple && (page === 1)) {
                                data.data.splice(0, 0, {id: null, text: gettext('---------')});
                            };
                            if (allowCreate && !more) data.data.push({id: {}, text: '<b><i>' + gettext('Create new...') + '</i></b>'});
                            return { results: data.data, more: more };
                        }
                    }
                };
                if (multiple) cfg['multiple'] = true;
                cfg['escapeMarkup'] = function (m) { return m; };
                var el = element.select2(cfg);
            }
            else
            var el = element.select2();
            controller.$render = function () {
                if (typeof controller.$viewValue === 'object')
                element.select2('data', controller.$viewValue);
                else
                element.select2('val', controller.$viewValue);
            };
            el.attr('tooltip', 'test');
            el.on('change', function () {
                scope.$apply(function () {
                    var data = el.select2('data');
                    if (data.id === null) controller.$setViewValue('');
                    else if (typeof data.id === 'object') {
                        window.open(window.location.pathname + '#/' + allowCreate);
                        controller.$setViewValue(''); el.select2('data', '');

                    }
                    else controller.$setViewValue(data);
                    console.log(data);
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

ui.directive('dynamic', function ($compile) {
    return {
        restrict: 'A',
        replace: true,
        link: function (scope, ele, attrs) {
            scope.$watch(attrs.dynamic, function(html) {
                ele.html(html);
                $compile(ele.contents())(scope);
            });
        }
    };
});
