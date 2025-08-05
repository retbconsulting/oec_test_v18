# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError

class OecMandatDeclaration(models.Model):
    _name = 'oec.mandat.declaration'
    _description = 'Déclaration du mandat'
    
    @api.model
    def _get_yes_no(self):
        return [
            ('1', 'Oui'),
            ('2','Non')
        ]

    name = fields.Char(string='Mandant numéro')
    partner_id = fields.Many2one(string="Expert comptable", comodel_name="res.partner")
    state = fields.Selection(string="Etat", selection='_get_status', default='draft')
    oec_mandat_ids = fields.One2many(comodel_name="oec.mandat", inverse_name="mandat_declaration_id", string="Mandats")
    mandats_number = fields.Integer(string='Nombre de mandats', compute="_get_mandats_number", store=True)
    
    nombre_bureaux = fields.Char(string="Nombre de bureaux")
    reseau_appartenance = fields.Char(string="Réseau d'appartenance (2)")
    audit_legal = fields.Integer(string='Nombre de mandats (Audit légal)', compute="_get_mandats_number", store=True)
    audit_contractuel = fields.Integer(string='Nombre de mandats (Audit contractuel)', compute="_get_mandats_number", store=True)
    autres_missions_legales = fields.Integer(string='Nombre de mandats (Autres missions légales)', compute="_get_mandats_number", store=True)
    autres_missions_echeances = fields.Integer(string='Nombre de mandats (Autres missions liées)', compute="_get_mandats_number", store=True)
    
    poids_ca = fields.Integer(string="Poids de l'audit dans le CA du cabinet")
    number_pages = fields.Integer(string="Nombre de pages d'annexes jointes")
    effectif_audit = fields.Integer(string="Effectif moyen des salariés d'audit", compute="_get_effectif_audit", store=True)
    directeurs_mission = fields.Integer(string="Directeurs de mission ou adjoints")
    responsables_mission = fields.Integer(string="Responsables de mission ou adjoints")
    auditeurs = fields.Integer(string="Auditeurs débutants ou confirmés")
    autres_cas = fields.Integer(string="Autres le cas échéant (à préciser)")
    sous_traitance = fields.Selection(string="Recours à la sous-traitance", selection='_get_yes_no', default='1')
    
    number_associes = fields.Integer(string="Nombre d'associés", compute="_get_number_associes", store=True)
    number_associes_ec = fields.Integer(string="Nombre d'E.C associés membres de l'Ordre")
    number_salaries_ec = fields.Integer(string="Nombre d'E.C salariés membres de l'Ordre")
    list_associes_signature = fields.Many2many(comodel_name='res.partner',relation='declaration_associe',string="Nombre d'associés")
    date_start = fields.Date(string="Date début")
    date_end = fields.Date(string="Date fin")

    @api.constrains('poids_ca')
    def _check_value(self):
        if self.poids_ca > 100 or self.poids_ca < 0:
            raise ValidationError("La valeur du Poids de l'audit dans le CA du cabinet doit être un pourcentage entre 0 et 100")
    
    @api.depends('oec_mandat_ids')
    def _get_mandats_number(self):
        for declaration in self:
            declaration.mandats_number = len(declaration.oec_mandat_ids)
            declaration.audit_legal = len(declaration.mapped('oec_mandat_ids').filtered(lambda r:r.nature_mission == '1'))
            declaration.audit_contractuel = len(declaration.mapped('oec_mandat_ids').filtered(lambda r:r.nature_mission == '2'))
            declaration.autres_missions_legales = len(declaration.mapped('oec_mandat_ids').filtered(lambda r:r.nature_mission == '3'))
            declaration.autres_missions_echeances = len(declaration.mapped('oec_mandat_ids').filtered(lambda r:r.nature_mission == '4'))
    
    @api.depends('directeurs_mission', 'responsables_mission', 'auditeurs', 'autres_cas')
    def _get_effectif_audit(self):
        for declaration in self:
            declaration.effectif_audit = declaration.directeurs_mission + declaration.responsables_mission + declaration.auditeurs + declaration.autres_cas
    
    @api.depends('number_associes_ec', 'number_salaries_ec')
    def _get_number_associes(self):
        for declaration in self:
            declaration.number_associes = declaration.number_associes_ec + declaration.number_salaries_ec
   
    @api.model
    def _get_status(self):
        return [
            ('draft', _("Brouillon")),
            ('in_progress', _("En attente de validation")),
            ('validated', _("Validée")),
        ]
        
    def button_in_progress(self):
        '''template = self.env.ref('mandat_cotisation_management.email_template_cotisation_to_validate')
        email = self.env.ref('base.user_admin').email
        template.with_context(email_from=email,email_to=email).send_mail(self.id,force_send=True)
        template = self.env.ref('mandat_cotisation_management.email_template_cotisation_to_validate_ec')
        template.with_context(email_from=email,email_to=self.partner_id.email).send_mail(self.id,force_send=True)'''
        self.write({'state': 'in_progress'})
        
    def button_validate(self):
        self.write({'state': 'validated'})
        '''template = self.env.ref('mandat_cotisation_management.email_template_cotisation_validated')
        email = self.env.ref('base.user_admin').email
        template.with_context(email_from=email,email_to=self.partner_id.email).send_mail(self.id,force_send=True)'''
        return True

class OecMandat(models.Model):

    _name = 'oec.mandat'
    _description = 'Mandat'

    name = fields.Char(string='Numéro')
    partner_id = fields.Many2one(string="Expert comptable", related="mandat_declaration_id.partner_id")
    secteur_activite = fields.Selection(string="Secteur d'activité", selection='_get_secteurs_activite', default='1')
    forme_juridique = fields.Selection(string="Forme juridique", selection='_get_formes_juridiques', default='1')
    entite_ape = fields.Selection(string="Entité APE", selection='_get_yes_no', default='1')
    in_group = fields.Selection(string="Appartenance à un groupe", selection='_get_yes_no', default='1')
    nombre_autres_entite_groupe = fields.Selection(string="Audit d'autres entités du groupe", selection='_get_yes_no', default='1')
    capitaux_propres = fields.Float(string="Capitaux propres (KMAD)")
    resultat_exercice = fields.Float(string="Résultat de l'exercice (KMAD)")
    total_actif = fields.Float(string="Total Actif (KMAD)")
    produit_exploitation = fields.Float(string="Produits d'exploitation (KMAD)")
    produit_financie = fields.Float(string="Produits financiers (KMAD)")
    leasing_restant = fields.Float(string="Leasign restant à payer (KMAD)")
    honoraires_dernier_exercice_clos = fields.Float(string="Honoraires/dernier exercice clos")
    
    nature_mission = fields.Selection(string="Nature de la mission", selection='_get_natures_missions', default='1')
    date_designation = fields.Date(string="Date de désignation")
    mode_designation = fields.Char(string="Mode de désignation (1)")
    exercces_couverts_par_le_mandat = fields.Char(string="Exercices couverts par le mandat")
    co_cac = fields.Char(string="Co-CAC")
    coCac = fields.Many2one(comodel_name='res.partner', string="Co-CAC")
    dernier_exercice_control = fields.Char(string="Dernier exercice contrôlé")
    nombre_reserves_pour_limitation = fields.Integer(string="Nombre de réserves pour limitations")
    nombre_reserves_pour_incertitudes = fields.Integer(string="Nombre de réserves pour incertitudes")
    nombre_reserves_pour_desacord = fields.Integer(string="Nombre de réserves pour désaccord")
    nombre_observation = fields.Integer(string="Nombre d'observations ")
    associe_signataire = fields.Char(string="Associé signataire")
    associeSignataire = fields.Many2one(comodel_name='res.partner', string="Associé Signataire")
    
    budget_temps_selon_norme = fields.Float(string="Budget temps selon Norme")
    budget_retenu_effort = fields.Float(string="Budget retenu lors de l'offre (2)")
    budget_temps_realises = fields.Float(string="Budget temps réalisé")
    temps_passe_associe = fields.Float(string="Temps passé par l'associé signataire")
    autres_missions_realises = fields.Char(string="Autres missions réalisées")
    honoraires_autres_mission = fields.Float(string="Honoraires des autres missions")
    rapport_opinion = fields.Integer(string="Rapport d'opinion")
    rapport_controle_interne = fields.Integer(string="Rapport de contrôle interne (ou lettre)")
    rapport_detaille_comptes = fields.Integer(string="Rapport détaillé sur les comptes")
    rapport_special = fields.Integer(string="Rapport spécial")
    autres_rapports = fields.Integer(string="Autres rapports")
    
    mandat_declaration_id = fields.Many2one(comodel_name="oec.mandat.declaration", string="Déclaration du mandat")
    
    
    @api.model
    def _get_secteurs_activite(self):
        return [
            ('1', 'Agriculture / Agroalimentaire'),
            ('2','Bois/Papier/ Carton/Imprimerie'),
            ('3','Chimie/Parachimie'),
            ('5','Edition/Communication/Multimédia'),
            ('6','Etudes et Conseils'),
            ('7','Machine et équipements'),
            ('8','Plastique/Caoutchouc'),
            ('9','Textile/Habillement/Chaussure'),
            ('10','Banque/Assurance'),
            ('11','BTP/ Matériaux de construction'),
            ('12','Commerce/Négoce/Distribution'),
            ('13','Electronique/Electricité'),
            ('14','Industrie pharmaceutique'),
            ('15','Informatique/Télécoms'),
            ('16','Métallurgie/Travail du Metal'),
            ('17','Services aux entreprises'),
            ('18','Transport et Logistique'),
            ('19','Autres')
        ]
        
    @api.model
    def _get_formes_juridiques(self):
        return [
            ('1', 'SA'),
            ('2','SARL'),
            ('3','SAS'),
            ('4','SARL AU'),
            ('5','SNC'),
            ('6','SCA'),
            ('7','SCS'),
            ('8','Association'),
            ('9','Coopérative'),
            ('10','Fond collectif'),
            ('11','OPVC'),
            ('12','OPCI'),
            ('13','Mutuelle'),
            ('14','Autres')
        ] 
    
    @api.model
    def _get_natures_missions(self):
        return [
            ('1', 'Audit légal'),
            ('2','Audil contractuel'),
            ('3','Autres missions légales'),
            ('4','Autres missions liées')
        ] 
    
    @api.model
    def _get_yes_no(self):
        return [
            ('1', 'Oui'),
            ('2','Non')
        ] 
    
    @api.model
    def create(self, vals):
        if not vals.get('name') or vals['name'] == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('oec.mandat') or _('New')
        return super(OecMandat, self).create(vals)
    
class ResPartner(models.Model):

    _inherit = 'res.partner'
    list_associes_signature_declaration = fields.Many2many(comodel_name='oec.mandat.declaration',relation='declaration_associe',string="Associés")
