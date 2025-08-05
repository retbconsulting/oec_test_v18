odoo.define('mandat_cotisation_management.calculate_total', ['require', 'jquery', 'web.ajax'], function (require) {
    'use strict';

    var $ = require('jquery');
    var ajax = require('web.ajax');

    $(document).ready(function() {
        $("#member_number").change(function() {
            $('#total_g').val($('#member_number').val() * $('#member_amount').val());
            if ($('#total_g_2').length) {
                $('#total').val(+$('#total_g_2').val() + +$('#total_h').val() + +$('#total_i').val() + +$('#total_j').val());

                var nStr = $('#total').val();
                nStr += '';
                var x = nStr.split('.');
                var x1 = x[0];
                var x2 = x.length > 1 ? '.' + x[1] : '';
                var rgx = /(\d+)(\d{3})/;
                while (rgx.test(x1)) {
                    x1 = x1.replace(rgx, '$1' + ' ' + '$2');
                }
                $('#label_total').text(x1 + x2 + ' DH');
            }
        });
    });
});
