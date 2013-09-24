var ui = angular.module('ui.keops', []);

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

