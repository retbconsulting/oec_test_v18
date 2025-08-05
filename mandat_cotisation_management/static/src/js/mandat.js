odoo.define('mandat_cotisation_management.calculate_total_associe', function (require) {
    'use strict';

    var $ = require('jquery');

    function updateNumberAssocies() {
        $('#number_associes').val(+$('#number_associes_ec').val() + +$('#number_salaries_ec').val());
    }

    function updateEffectifAudit() {
        $('#effectif_audit').val(+$('#directeurs_mission').val() + +$('#responsables_mission').val() + +$('#auditeurs').val() + +$('#autres_cas').val());
    }

    function updateBudgetTempsSelonNorme() {
        var total = +$('#capitaux_propres').val() + +$('#resultat_exercice').val() + +$('#total_actif').val() + +$('#produit_exploitation').val() + +$('#produit_financie').val() + +$('#leasing_restant').val();
        if (total <= 5000000) {
            $('#budget_temps_selon_norme').val(40);
        } else if (total > 5000000 && total <= 25000000) {
            $('#budget_temps_selon_norme').val((total - 5000000) / (25000000 - 5000000) * (100 - 40) + 40);
        } else if (total > 25000000 && total <= 50000000) {
            $('#budget_temps_selon_norme').val((total - 25000000) / (50000000 - 25000000) * (180 - 100) + 100);
        } else if (total > 50000000 && total <= 120000000) {
            $('#budget_temps_selon_norme').val((total - 50000000) / (120000000 - 50000000) * (280 - 180) + 180);
        } else if (total > 120000000 && total <= 250000000) {
            $('#budget_temps_selon_norme').val((total - 120000000) / (250000000 - 120000000) * (400 - 280) + 280);
        } else if (total > 250000000 && total <= 450000000) {
            $('#budget_temps_selon_norme').val((total - 250000000) / (450000000 - 250000000) * (520 - 400) + 400);
        } else if (total > 450000000 && total <= 700000000) {
            $('#budget_temps_selon_norme').val((total - 450000000) / (700000000 - 450000000) * (640 - 520) + 520);
        } else if (total > 700000000 && total <= 900000000) {
            $('#budget_temps_selon_norme').val((total - 700000000) / (900000000 - 700000000) * (750 - 640) + 640);
        } else {
            $('#budget_temps_selon_norme').val(750);
        }
    }

    function toggleLettreInformation() {
        if (+$("#budget_temps_selon_norme").val() > +$("#budget_retenu_effort").val()) {
            $('#lettre_information').show();
            $('#lettre_information2').show();
        } else {
            $('#lettre_information').hide();
            $('#lettre_information2').hide();
        }
    }

    $("#number_associes_ec").change(updateNumberAssocies).trigger("change");
    $("#number_salaries_ec").change(updateNumberAssocies).trigger("change");

    $("#directeurs_mission").change(updateEffectifAudit).trigger("change");
    $("#responsables_mission").change(updateEffectifAudit).trigger("change");
    $("#auditeurs").change(updateEffectifAudit).trigger("change");
    $("#autres_cas").change(updateEffectifAudit).trigger("change");

    $("#budget_temps_selon_norme").change(toggleLettreInformation).trigger("change");
    $("#budget_retenu_effort").change(toggleLettreInformation).trigger("change");

    $("#total_actif").change(updateBudgetTempsSelonNorme).trigger("change");
    $("#capitaux_propres").change(updateBudgetTempsSelonNorme).trigger("change");
    $("#resultat_exercice").change(updateBudgetTempsSelonNorme).trigger("change");
    $("#produit_exploitation").change(updateBudgetTempsSelonNorme).trigger("change");
    $("#produit_financie").change(updateBudgetTempsSelonNorme).trigger("change");
    $("#leasing_restant").change(updateBudgetTempsSelonNorme).trigger("change");
});
