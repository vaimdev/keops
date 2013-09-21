
var ui = angular.module('ui.keops', []);

ui.directive('multiplechoice', function() {
    console.log('test');
    return {
        restrict: 'A',
        replace: true,
        transclude: true,
        template: '<div>' +
            '<div class="multiplechoice">' +
            '<div>' +
            '<button class="btn" style="margin-right: 10px;">Add</button>' +
            '<button class="btn">Remove</button>' +
            '</div>' +
            '<div>' +
            '<hr/>' +
            '<a style="margin-left: 5px; font-size: 10px">Select all</a>' +
            '<hr/>' +
            '<div class="multiplechoice-items">' +
            '<table style="padding: 5px 0 5px 4px; width: 100%">' +
            '<tr><td style="width: 20px;"><input type="checkbox"></td>' +
            '<td><a style="display: block;">object 1</a></td></tr>' +
            '<tr><td><input type="checkbox"></td><td>object 2</td></tr>' +
            '</table></div><div style="font-size: 11px;"><i>Field info.</i></div></div>',
        //require: 'ngModel',
        link: function (scope, element, attrs) {
            var selectAll = angular.element(element.find('a')[0]);
            selectAll.on('click', function () {
                var items = element.find('input');
                var ca = false;
                for (var i = 0; i < items.length; i++) {
                    if (!items[i].checked) {
                        ca = true;
                        break;
                    }
                }
                for (var i = 0; i < items.length; i++) items[i].checked = ca;

            });
            console.log(element.find('input'));
        }
    }
});

ui.directive('combobox', function() {
    return {
        restrict: 'A',
        require : 'ngModel',
        link : function (scope, element, attrs, ngModelCtrl) {
            $(function() {
                element.autocomplete({
                    source: function (request, response) {
                        $.ajax({
                             url: "/db/lookup/?model=base.module",
                             data: { query: request.term },
                             dataType: "json",
                             success: function() {
                                 return response(arguments[0]);
                             },
                             error: function () {
                                 response([]);
                             }
                        });
                    },
                    change: function (e, ui) {
                        if (!ui.item) $(this).val('');
                    }
                }).on('autocompleteselect', function (e, ui) {
                        e.preventDefault();

                        this.value = ui.item.label;
                        this.rawValue = ui.item.value;
                    });
            });
        }
    }
});

