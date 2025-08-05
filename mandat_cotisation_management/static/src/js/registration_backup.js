odoo.define('mandat_cotisation_management.calculate_total', function (require) {
    'use strict';

    var $ = require('jquery');

    function formatNumber(nStr) {
        nStr += '';
        var x = nStr.split('.');
        var x1 = x[0];
        var x2 = x.length > 1 ? '.' + x[1] : '';
        var rgx = /(\d+)(\d{3})/;
        while (rgx.test(x1)) {
            x1 = x1.replace(rgx, '$1' + ' ' + '$2');
        }
        return x1 + x2;
    }

    function updateTotal() {
        var total = +$('#total_g_2').val() + +$('#total_h').val() + +$('#total_i').val() + +$('#total_j').val();
        $('#total').val(total);
        $('#label_total').text(formatNumber(total) + ' DH');
    }

    function updateTotalG() {
        $('#total_g').val($('#member_number').val() * $('#member_amount').val());
        if ($('#total_g_2').length) {
            updateTotal();
        }
    }

    function updateTotalF() {
        var totalF = $('#number_member_d').val() * $('#amount_member_e').val();
        $('#total_f').val(totalF);
        $('#label_total_f').text(formatNumber(totalF) + ' DH');
    }

    function updateTotalG2() {
        var totalG2 = +($('#number_member_d').val() * $('#amount_member_e').val()) +
                      +($('#number_members_50').val() * $('#amount_member_e').val() * 0.5) +
                      +$('#amount_member_c').val();
        $('#total_g_2').val(totalG2);
        $('#label_total_g_2').text(formatNumber(totalG2) + ' DH');
    }

    function updateTotalH() {
        var totalH = +$('#ca_amount_1').val() + +$('#ca_amount_2').val();
        $('#total_h').val(totalH);
        $('#label_total_h').text(formatNumber(totalH) + ' DH');
    }

    function updateCaAmount() {
        $('#ca_amount').val($('#ca_amount').val().replaceAll(/\s/g, ''));
        if ($('#ca_amount').val() >= 50000000) {
            $('#l_ca_section_2, #ca_section_2').show();
            $('#ca_plafond_1').text("50 000 000");

            var caPlafond2 = formatNumber($('#ca_amount').val());
            $('#ca_plafond_2').text(caPlafond2);
            var caAmount1 = (50000000 * 0.0025).toFixed(2);
            $('#ca_amount_1').val(caAmount1);
            $('#label_ca_1').text(formatNumber(caAmount1) + ' DH');

            var caAmount2 = ((+$('#ca_amount').val() - 50000000) * 0.0015).toFixed(2);
            $('#ca_amount_2').val(caAmount2);
            $('#label_ca_2').text(formatNumber(caAmount2) + ' DH');
        } else {
            $('#l_ca_section_2, #ca_section_2').hide();
            var caPlafond1 = formatNumber($('#ca_amount').val());
            $('#ca_plafond_1').text(caPlafond1);
            var caAmount1 = ($('#ca_amount').val() * 0.0025).toFixed(2);
            $('#ca_amount_1').val(caAmount1);
            $('#label_ca_1').text(formatNumber(caAmount1) + ' DH');

            $('#ca_amount_2').val(0);
            $('#label_ca_2').text(formatNumber(0) + ' DH');
        }
        updateTotalH();
        updateTotal();
    }

    function updateTotalI() {
        var totalI = $('#number_mandat').val() * 200;
        $('#total_i').val(totalI);
        $('#label_total_i').text(formatNumber(totalI) + ' DH');
        updateTotal();
    }

    function updateDiscount() {
        var totalF = (+($('#number_member_d').val() * $('#amount_member_e').val()) +
                      +($('#number_members_50').val() * $('#amount_member_e').val() * 0.5));
        $('#total_f').val(totalF);
        $('#label_total_f').text(formatNumber(totalF) + ' DH');

        var totalJ = (+$('#number_member_d').val() + +$('#number_members_50').val()) * 1500;
        $('#total_j').val(totalJ);
        $('#label_total_j').text(formatNumber(totalJ) + ' DH');

        var discount = $('#discount').val();
        var commentText = '';
        if (discount == '50%') {
            commentText = "(Inscrit entre le 1er décembre " + (parseInt($("#year").val()) - 1).toString() + " et 30 novembre " + (parseInt($("#year").val()) - 2).toString() + ")";
        } else if (discount == '100%') {
            commentText = "(Inscrit à partir du 1er décembre " + (parseInt($("#year").val()) - 1).toString() + ")";
        } else {
            commentText = "(Inscrit avant le 30 novembre " + (parseInt($("#year").val()) - 2).toString() + ")";
        }
        $('#comment_remise').text(commentText);

        updateTotalG2();
        updateTotal();
    }

    function updateYear() {
        var discount = $('#discount').val();
        if (discount == '50%') {
            $('#comment_remise').text("(Inscrit entre le 1er décembre " + (parseInt($("#year").val()) - 1).toString() + " et 30 novembre " + (parseInt($("#year").val()) - 2).toString() + ")");
        } else if (discount == '100%') {
            $('#comment_remise').text("(Inscrit à partir du 1er décembre " + (parseInt($("#year").val()) - 1).toString() + ")");
        } else {
            $('#comment_remise').text("(Inscrit avant le 30 novembre " + (parseInt($("#year").val()) - 2).toString() + ")");
        }

        $('.comment_exo').text("(Inscrit à partir du 1er décembre " + (parseInt($("#year").val()) - 1).toString() + ")");
        $('#comment_50').text("(Inscrit entre le 1er décembre " + (parseInt($("#year").val()) - 1).toString() + " et 30 novembre " + (parseInt($("#year").val()) - 2).toString() + ")");
        $('.comment_noexo').text("(Inscrit avant le 30 novembre " + (parseInt($("#year").val()) - 2).toString() + ")");
    }

    function toggleJustifCaComment() {
        if (!$('#justif_ca').val()) {
            $('#comment_justif_ca').hide();
        } else {
            $('#comment_justif_ca').show();
        }
    }

    function updateLabelMembersExo() {
        $('#label_members_exo').text(formatNumber($('#number_members_exo').val()));
    }

    function toggleEdiMode() {
        if ($('#contactChoice1').is(':checked')) {
            $('#edi_mode').show();
        } else {
            $('#edi_mode').hide();
        }
    }

    function initialize() {
        $("#member_number").change(updateTotalG).trigger("change");
        $("#member_amount").change(updateTotalG).trigger("change");
        $("#number_member_d").change(updateTotalF).trigger("change");
        $("#number_members_50").change(updateTotalF).trigger("change");
        $("#amount_member_e").change(updateTotalF).trigger("change");
        $("#amount_member_c").change(updateTotalG2).trigger("change");
        $("#ca_amount").change(updateCaAmount).trigger("change");
        $("#number_mandat").change(updateTotalI).trigger("change");
        $("#discount").change(updateDiscount).trigger("change");
        $("#year").change(updateYear).trigger("change");
        $("#justif_ca").change(toggleJustifCaComment).trigger("change");
        $("#number_members_exo").change(updateLabelMembersExo).trigger("change");
        $("#contactChoice1").change(toggleEdiMode).trigger("change");
        $("#contactChoice2").change(toggleEdiMode).trigger("change");
    }

    $(document).ready(initialize);
});
