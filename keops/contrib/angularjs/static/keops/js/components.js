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
            var maskStore = attrs['uiMaskStore'];

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

ui.directive('datePicker', function() {
    return {
        restrict: 'A',
        //require : 'ngModel',
        link: function(scope, element, attrs, controller) {
            element.datepicker({
                dateFormat: attrs.dateFormat,
                onSelect: function(dateText, datepicker) {
                    scope.date = dateText;
                    scope.$apply();
                }
            });
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
