var ui = angular.module('ui.keops', []);

ui.directive('multiplechoice', function() {
    return {
        restrict: 'A',
        replace: true,
        transclude: true,
        template: '<div>' +
            '<div class="multiplechoice">' +
            '<div style="display: table;">' +
            '<label style="display: table-cell"></label>' +
            '<button class="btn" style="margin-left: 10px;">' + gettext('Add') + '</button>' +
            '</div>' +
            '<div>' +
            '<hr/>' +
            '<div class="multiplechoice-items">' +
            '<table style="padding: 5px 0 5px 4px; width: 100%; table-layout: fixed;">' +
            '<tr>' +
            '<td style="width: 1px; padding-right: 10px;"><i style="cursor: pointer" title="' + gettext('Remove item') + '" class="icon-remove"></a></td>' +
            '<td><a style="display: block;">{{item.__str__}}</a></td>' +
            '</tr>' +
            '</table></div>' +
            '</div>',
        require: 'ngModel',
        compile: function(element, attrs) {
            var tr = angular.element(element.find('tr')[0]);
            console.log(attrs);
            tr.attr('ng-repeat', "item in " + attrs.ngModel);
            var label = angular.element(element.find('label')[0]);
            label.html(attrs.label);
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

