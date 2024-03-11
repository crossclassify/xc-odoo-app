from odoo import http, models, _

class DashboardController(http.Controller):

    @http.route('/cc_smart_2fa/get_setup_data', type='json', auth='user')
    def get_setup_data(self):
        settings = http.request.env['cc_smart_2fa'].sudo().search([], limit=1)
        if settings:
            return {
                'apikey': settings.apikey,
                'siteId': settings.siteId,
            }
        return {}

    @http.route('/cc_smart_2fa/set_setup_data', type='json', auth='user')
    def set_setup_data(self, apikey, siteId):
        settings = http.request.env['cc_smart_2fa'].sudo().search([], limit=1)
        if not settings:
            settings = http.request.env['cc_smart_2fa'].sudo().create({})
        settings.write({
            'apikey': apikey,
            'siteId': siteId,
        })
        return True
