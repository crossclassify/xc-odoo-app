from odoo import models, fields

class XCSmart2FA(models.Model):
    _name = 'cc_smart_2fa'
    _description = 'XCSmart2FA'

    apikey = fields.Char(string='API Key')
    siteId = fields.Char(string='Site ID')