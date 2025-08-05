# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError


class OecCotisationHistory(models.Model):
    _name = 'oec.cotisation.history'
    _description = 'Historique des cotisations'
    _order = 'date desc'

    cotisation_id = fields.Many2one('oec.cotisation', string="Cotisation", required=True, ondelete='cascade')
    user_id = fields.Many2one('res.users', string="Utilisateur", required=True, default=lambda self: self.env.user)
    date = fields.Datetime(string="Date", required=True, default=fields.Datetime.now)
    action_type = fields.Selection([
        ('created', 'Création'),
        ('submitted', 'Soumission'),
        ('validated', 'Validation'),
        ('rejected', 'Rejet'),
        ('payment_submitted', 'Paiement soumis'),
        ('payment_validated', 'Paiement validé'),
        ('payment_rejected', 'Paiement rejeté'),
        ('accounting_submitted', 'Comptabilisation'),
        ('modified', 'Modification'),
        ('state_changed', 'Changement d\'état'),
    ], string="Type d'action", required=True)

    old_state = fields.Selection([
        ('draft', 'Brouillon'),
        ('waiting_validation', 'En attente de validation par le CROEC'),
        ('validated', 'Validée & Attente de paiement'),
        ('rejected', 'Déclaration à revoir'),
        ('payment_submitted', 'Paiement soumis'),
        ('payment_validated', 'Paiement validé'),
        ('rejected_payment', 'Paiement à revoir'),
        ('comptabilise', 'Comptabilisé'),
    ], string="Ancien état")

    new_state = fields.Selection([
        ('draft', 'Brouillon'),
        ('waiting_validation', 'En attente de validation par le CROEC'),
        ('validated', 'Validée & Attente de paiement'),
        ('rejected', 'Déclaration à revoir'),
        ('payment_submitted', 'Paiement soumis'),
        ('payment_validated', 'Paiement validé'),
        ('rejected_payment', 'Paiement à revoir'),
        ('comptabilise', 'Comptabilisé'),
    ], string="Nouvel état")

    description = fields.Text(string="Description")
    reject_motif = fields.Text(string="Motif de rejet")
    old_total = fields.Float(string="Ancien montant total")
    new_total = fields.Float(string="Nouveau montant total")

    # Champs pour les modifications de données
    field_changed = fields.Char(string="Champ modifié")
    old_value = fields.Text(string="Ancienne valeur")
    new_value = fields.Text(string="Nouvelle valeur")

    # Données de contexte
    ip_address = fields.Char(string="Adresse IP")
    user_agent = fields.Text(string="User Agent")


class OecCotisationMotif(models.Model):
    _name = 'oec.cotisation.motif'

    name = fields.Char(string="Motif")


class OecCotisationReject(models.TransientModel):
    _name = 'oec.cotisation.reject'

    reject_type = fields.Selection(string="Type de rejet", selection='_get_reject_types',
                                   default='document_non_conforme')
    oec_cotisation_id = fields.Many2one(comodel_name='oec.cotisation')
    reject_motif = fields.Many2one(comodel_name="oec.cotisation.motif", string="Motif de rejet")

    @api.model
    def _get_reject_types(self):
        return [
            ('document_non_conforme', _("Document non conforme")),
            ('periode_differente', _("Période déclaration différente de la période du document")),
            ('amount_differente', _("Montant différent avec celui déclaré"))
        ]

    def confirm(self):
        cotisation = self.oec_cotisation_id
        template = self.env.ref('mandat_cotisation_management.email_template_cotisation_rejected')
        email = self.env.ref('base.user_admin').email
        template.with_context(email_from=email, email_to=cotisation.partner_id.email).send_mail(cotisation.id,
                                                                                                force_send=True)

        # Créer l'entrée d'historique
        cotisation._create_history_entry(
            action_type='rejected',
            old_state=cotisation.state,
            new_state='rejected',
            description=f"Cotisation rejetée - Type: {dict(self._get_reject_types())[self.reject_type]}",
            reject_motif=self.reject_motif.name if self.reject_motif else ''
        )

        cotisation.write({
            'state': 'rejected',
            'reject_motif': self.reject_motif,
            'reject_type': self.reject_type})
        return True


class OecCotisationPaymentReject(models.TransientModel):
    _name = 'oec.cotisation.payment.reject'

    reject_type = fields.Selection(string="Type de rejet", selection='_get_payment_reject_types',
                                   default='document_non_conforme')
    oec_cotisation_id = fields.Many2one(comodel_name='oec.cotisation')
    reject_motif = fields.Text(string="Motif de rejet de paiement")

    @api.model
    def _get_payment_reject_types(self):
        return [
            ('document_non_conforme', _("Document non conforme")),
            ('amount_differente', _("Montant différent avec celui déclaré"))
        ]

    def confirm(self):
        cotisation = self.oec_cotisation_id
        template = self.env.ref('mandat_cotisation_management.email_template_cotisation_rejected_payment')
        email = self.env.ref('base.user_admin').email
        template.with_context(email_from=email, email_to=cotisation.partner_id.email).send_mail(cotisation.id,
                                                                                                force_send=True)

        # Créer l'entrée d'historique
        cotisation._create_history_entry(
            action_type='payment_rejected',
            old_state=cotisation.state,
            new_state='rejected_payment',
            description=f"Paiement rejeté - Type: {dict(self._get_payment_reject_types())[self.reject_type]}",
            reject_motif=self.reject_motif
        )

        cotisation.write({
            'state': 'rejected_payment',
            'reject_payment_motif': self.reject_motif,
            'reject_payment_type': self.reject_type})
        return True


class OecCotisation(models.Model):
    _name = 'oec.cotisation'
    _description = 'Cotisation'

    # Champ pour l'historique
    history_ids = fields.One2many('oec.cotisation.history', 'cotisation_id', string="Historique")
    history_count = fields.Integer(string="Nombre d'entrées d'historique", compute='_compute_history_count')

    mode_registration = fields.Selection(string="Mode", related="partner_id.mode_registration", store=True)
    year = fields.Selection(selection=[(str(num), str(num)) for num in range(2018, (datetime.now().year) + 1)],
                            string="Année", required=True)
    partner_id = fields.Many2one(string="Expert comptable", comodel_name="res.partner")
    date_inscription = fields.Date(string="Date d'inscription", related="partner_id.date_inscription", store=True)
    name = fields.Char(string='Nom', related="partner_id.name")
    prenom = fields.Char(string='Prénom', related="partner_id.second_name")
    adresse = fields.Char(string='Adresse', related="partner_id.street")
    number_members = fields.Integer(string="Nombre de membres de l'ordre exerçant dans la structure (A)")
    amount_member = fields.Float(string="Montant par membre de l'ordre (B)")
    amount_member_c = fields.Float(string="Cotisation de la personne morale (C)")
    number_members_2 = fields.Integer(string="Nombre de membres non exonéré")
    number_members_50 = fields.Integer(string="Nombre de membres bénéficiares de 50% de remise")
    number_members_exo = fields.Integer(string="Nombre de membres exonérés")
    amount_member_2 = fields.Float(string="Montant par membre de l'ordre (E)")
    total_f = fields.Float(string="Sous total (D*E) = (F)")
    total_g = fields.Float(string="Total cotisation fixe (G)")
    total_g_2 = fields.Float(string="Total cotisation fixe (G)")
    ca = fields.Float(string="Chiffre d'affaires")
    total_h = fields.Float(string="Total cotisation variable (H)")
    mandat_number = fields.Integer(string="Nombre de mandats")
    s_office_number = fields.Integer(string="Nombre de bureaux secondaires")
    total_i = fields.Float(string="Total cotisation fixe de CAC et/ou audit (I)")
    total_i2 = fields.Float(string="Total cotisation fixe de bureaux secondaires")
    total_j = fields.Float(string="Total cotisation IFOEC (J)")
    total = fields.Float(string="Total (G)+(H)+(I)+(J)")
    member_ids = fields.One2many(comodel_name="oec.member", inverse_name="cotisation_id", string="Membres de l'ordre")
    attestation_ca = fields.Binary(string="Attestation de CA")
    state = fields.Selection(string="Etat", selection='_get_status', default='draft')
    reject_type = fields.Selection(string="Type de rejet", selection='_get_reject_types',
                                   default='document_non_conforme')
    justif_file = fields.Binary(string="Justif", attachment=True)
    justif_filename = fields.Char(string='Justif filename')
    reject_motif = fields.Text(string="Motif de rejet")
    reject_payment_type = fields.Selection(string="Type de rejet de paiement", selection='_get_reject_types',
                                           default='document_non_conforme')
    reject_payment_motif = fields.Text(string="Motif de rejet de paiement")
    justif_ca_file = fields.Binary(string="Justif CA", attachment=True)
    justif_ca_filename = fields.Char(string='Justif filename CA')
    date_open = fields.Date(string="Date d'ouverture", compute='_get_date_open', store=True)
    diff = fields.Integer(string="Diff", compute='_get_diff')
    mandat_number_real = fields.Integer(related="partner_id.mandat_number", string="Nombre de mandats déclarés",
                                        store=True)
    numero_cheque = fields.Char(string='Numéro de chèque')
    amount_cheque = fields.Float(string="Montant du chèque")
    modalite_payment = fields.Selection(string="Type de rejet", selection='_get_modalites_payment', default='cheque')
    justificatif = fields.Binary(string="Justificatif du paiement", attachment=True)
    justificatif_filename = fields.Char(string='Justificatif filename paiement')
    discount = fields.Selection(string="Remise", selection='_get_discount', default='0%')
    due_date = fields.Date(string="Date d'échéance", required=True)
    declaration_date = fields.Date(string="Date de déclaration", required=False)
    payment_validation_date = fields.Date(string="Date de validation du paiement")
    declaration_veracite = fields.Boolean(
        string="Je déclare sur l'honneur que les informations communiquées sont exactes.",
        help="L'utilisateur confirme l'exactitude des informations fournies."
    )

    @api.depends('history_ids')
    def _compute_history_count(self):
        for record in self:
            record.history_count = len(record.history_ids)

    def _create_history_entry(self, action_type, old_state=None, new_state=None, description=None, reject_motif=None,
                              field_changed=None, old_value=None, new_value=None):
        """Créer une entrée d'historique"""
        history_vals = {
            'cotisation_id': self.id,
            'action_type': action_type,
            'old_state': old_state,
            'new_state': new_state,
            'description': description,
            'reject_motif': reject_motif,
            'field_changed': field_changed,
            'old_value': str(old_value) if old_value is not None else None,
            'new_value': str(new_value) if new_value is not None else None,
            'old_total': self.total,
            'new_total': self.total,
        }

        # Obtenir l'adresse IP et user agent du contexte si disponible
        request = self.env.context.get('request')
        if request:
            history_vals['ip_address'] = request.httprequest.environ.get('REMOTE_ADDR')
            history_vals['user_agent'] = request.httprequest.environ.get('HTTP_USER_AGENT')

        self.env['oec.cotisation.history'].create(history_vals)

    @api.model
    def create(self, vals):
        """Surcharge pour créer l'historique à la création"""
        result = super(OecCotisation, self).create(vals)
        result._create_history_entry(
            action_type='created',
            new_state=result.state,
            description=f"Cotisation créée pour l'année {result.year}"
        )
        return result

    def write(self, vals):
        """Surcharge pour suivre les modifications"""
        for record in self:
            old_values = {}

            # Sauvegarder les anciennes valeurs des champs importants
            important_fields = ['state', 'total', 'ca', 'number_members', 'amount_member', 'mandat_number', 'discount']
            for field in important_fields:
                if field in vals:
                    old_values[field] = getattr(record, field)

            # Exécuter la modification
            result = super(OecCotisation, record).write(vals)

            # Créer les entrées d'historique pour les modifications
            for field, old_value in old_values.items():
                new_value = vals[field]
                if old_value != new_value:
                    field_label = record._fields[field].string

                    if field == 'state':
                        record._create_history_entry(
                            action_type='state_changed',
                            old_state=old_value,
                            new_state=new_value,
                            description=f"Changement d'état: {dict(record._get_status())[old_value]} → {dict(record._get_status())[new_value]}"
                        )
                    else:
                        record._create_history_entry(
                            action_type='modified',
                            field_changed=field_label,
                            old_value=old_value,
                            new_value=new_value,
                            description=f"Modification du champ '{field_label}'"
                        )

            return result

    def view_history(self):
        """Action pour afficher l'historique"""
        return {
            'name': _('Historique de la cotisation'),
            'type': 'ir.actions.act_window',
            'res_model': 'oec.cotisation.history',
            'view_mode': 'tree,form',
            'domain': [('cotisation_id', '=', self.id)],
            'context': {'default_cotisation_id': self.id},
            'target': 'current',
        }

    @api.constrains('declaration_veracite')
    def _check_declaration(self):
        for record in self:
            if not record.declaration_veracite:
                raise ValidationError("Veuillez cocher la déclaration sur l'honneur.")

    @api.model
    def _get_modalites_payment(self):
        return [
            ('cheque', _("Chèque")),
            ('virement', _("Virement")),
            ('en_ligne', _("En ligne"))
        ]

    @api.depends('year')
    def _get_date_open(self):
        for record in self:
            if record.year:
                record.date_open = datetime(year=int(record.year), month=1, day=1)

    @api.depends('date_open', 'date_inscription')
    def _get_diff(self):
        for record in self:
            if record.date_open and record.date_inscription:
                record.diff = (
                                      record.date_open.year - record.date_inscription.year) * 12 + record.date_open.month - record.date_inscription.month
            else:
                record.diff = None

    @api.model
    def _get_status(self):
        return [
            ('draft', _("Brouillon")),
            ('waiting_validation', _("En attente de validation par le CROEC")),
            ('validated', _("Validée & Attente de paiement")),
            ('rejected', _("Déclaration à revoir")),
            ('payment_submitted', _("Paiement soumis")),
            ('payment_validated', _("Paiement validé")),
            ('rejected_payment', _("Paiement à revoir")),
            ('comptabilise', _("Comptabilisé")),
        ]

    @api.model
    def _get_reject_types(self):
        return [
            ('document_non_conforme', _("Document non conforme")),
            ('periode_differente', _("Période déclaration différente de la période du document")),
            ('amount_differente', _("Montant différent avec celui déclaré"))
        ]

    @api.model
    def _get_payment_reject_types(self):
        return [
            ('document_non_conforme', _("Document non conforme")),
            ('amount_differente', _("Montant différent avec celui déclaré"))
        ]

    @api.model
    def _get_discount(self):
        return [
            ('0%', _("0%")),
            ('50%', _("50%")),
            ('100%', _("100%")),
        ]

    def button_in_progress(self):
        template = self.env.ref('mandat_cotisation_management.email_template_cotisation_to_validate')
        email = self.env.ref('base.user_admin').email
        template.with_context(email_from=email, email_to=email).send_mail(self.id, force_send=True)
        template = self.env.ref('mandat_cotisation_management.email_template_cotisation_to_validate_ec')
        template.with_context(email_from=email, email_to=self.partner_id.email).send_mail(self.id, force_send=True)

        self._create_history_entry(
            action_type='submitted',
            old_state=self.state,
            new_state='waiting_validation',
            description="Cotisation soumise pour validation"
        )

        self.write({'state': 'waiting_validation'})

    def button_validate(self):
        self._create_history_entry(
            action_type='validated',
            old_state=self.state,
            new_state='validated',
            description="Cotisation validée par le CROEC"
        )

        self.write({'state': 'validated'})
        template = self.env.ref('mandat_cotisation_management.email_template_cotisation_validated')
        email = self.env.ref('base.user_admin').email
        template.with_context(email_from=email, email_to=self.partner_id.email).send_mail(self.id, force_send=True)
        return True

    def button_reject(self):
        return {
            'name': _("Rejet"),
            'view_mode': 'form',
            'res_model': 'oec.cotisation.reject',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': {
                'default_oec_cotisation_id': self.id
            }
        }

    def button_waiting_payment_validation(self):
        self._create_history_entry(
            action_type='payment_submitted',
            old_state=self.state,
            new_state='payment_submitted',
            description="Paiement soumis pour validation"
        )

        self.write({'state': 'payment_submitted'})
        template = self.env.ref('mandat_cotisation_management.email_template_cotisation_to_validate_payment')
        email = self.env.ref('base.user_admin').email
        template.with_context(email_from=email, email_to=email).send_mail(self.id, force_send=True)

    def button_payment_validate(self):
        self._create_history_entry(
            action_type='payment_validated',
            old_state=self.state,
            new_state='payment_validated',
            description="Paiement validé"
        )

        self.write({'state': 'payment_validated'})
        self.payment_validation_date = fields.Date().today()
        template = self.env.ref('mandat_cotisation_management.email_template_cotisation_validated_payment')
        email = self.env.ref('base.user_admin').email
        template.with_context(email_from=email, email_to=self.partner_id.email).send_mail(self.id, force_send=True)
        return True

    def button_payment_reject(self):
        return {
            'name': _("Rejet de paiement"),
            'view_mode': 'form',
            'res_model': 'oec.cotisation.payment.reject',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': {
                'default_oec_cotisation_id': self.id
            }
        }

    def button_accounting_submit(self):
        self._create_history_entry(
            action_type='accounting_submitted',
            old_state=self.state,
            new_state='comptabilise',
            description="Cotisation comptabilisée"
        )

        self.write({'state': 'comptabilise'})


class OecConfiguration(models.Model):
    _name = 'oec.configuration'

    amount_member = fields.Float(string=u"Montant par membre de l'ordre")
    cotisation_morale = fields.Float(string=u"Cotisation de la personne morale")
    amount_member_ifoec = fields.Float(string=u"Montant par membre de l'OEC IFOEC")


class OecMember(models.Model):
    _name = 'oec.member'
    _description = 'Membre'

    name = fields.Char(string='Nom')
    prenom = fields.Char(string='Prénom')
    adresse = fields.Char(string='Adresse')
    cotisation_id = fields.Many2one(comodel_name='oec.cotisation')