odoo.define('internship_management_module.registration_controls',
    function (require) {
'use strict';
$("#mode_registration").change(function() {
    if ($(this).val() == "pm") {
    $('#pp').show();
    }else{
  	$('#pp').hide();
  }

});

$("#mode_registration").trigger("change");

$("#mode_registration_inscription").change(function() {

if ($(this).val() == "pm") {
    $('#pp').show();
    $('#ppm').show();
  }else{
  	$('#pp').hide();
  	$('#ppm').hide();
  }

});

$("#mode_registration_inscription").trigger("change");


$("#diplome").change(function() {
if ($(this).val() == "autre") {
	$('#cin_maroc').hide();
    $('#country').show();
    $('#cin_autre').show();
  }else if ($(this).val() == "francais"){
  	$('#country').hide();
  	$('#cin_maroc').hide();
  	$('#cin_autre').show();
  }else{
  	$('#country').hide();
  	$('#cin_maroc').show();
  	$('#cin_autre').hide();
  }

});

$("#diplome").trigger("change");

$("#diplome").change(function() {
if ($(this).val() == "autre") {
	$('#cin_maroc').hide();
    $('#country').show();
    $('#cin_autre').show();
  }else if ($(this).val() == "francais"){
  	$('#country').hide();
  	$('#cin_maroc').hide();
  	$('#cin_autre').show();
  }else{
  	$('#country').hide();
  	$('#cin_maroc').show();
  	$('#cin_autre').hide();
  }

});

$("#diplome").trigger("change");

$("#had_difficulties_courses").change(function() {
if ($(this).val() == "yes") {
	$('#remarks_difficulties_courses').show();
  }else{
  	$('#remarks_difficulties_courses').hide();
  }

});

$("#had_difficulties_courses").trigger("change");


$("#had_difficulties_works").change(function() {
if ($(this).val() == "yes") {
	$('#remarks_difficulties_works').show();
  }else{
  	$('#remarks_difficulties_works').hide();
  }

});

$("#had_difficulties_works").trigger("change");

$("#cs_decision").change(function() {
if ($(this).val() == "rejet") {
	$('#apprciation_cs').text("Motif de rejet");
  }else{
  	$('#apprciation_cs').text("Appréciation du contrôleur de stage");
  }

});

$("#cs_decision").trigger("change");

});
