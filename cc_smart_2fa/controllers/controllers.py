from odoo import http, models, _
import pyotp
import time 

class DashboardController(http.Controller):

    @http.route('/cc_smart_2fa/get_setup_data', type='json', auth='user')
    def get_setup_data(self):
        settings = http.request.env['cc_smart_2fa'].sudo().search([], limit=1)
        if settings:
            return {
                'apikey': settings.apikey,
                'siteId': settings.siteId,
                'projectId': settings.projectId,
                'authToken': settings.authToken
            }
        return {}

    @http.route('/cc_smart_2fa/set_setup_data', type='json', auth='user')
    def set_setup_data(self, apikey, siteId, projectId, authToken):
        settings = http.request.env['cc_smart_2fa'].sudo().search([], limit=1)
        if not settings:
            settings = http.request.env['cc_smart_2fa'].sudo().create({})
        settings.write({
            'apikey': apikey,
            'siteId': siteId,
            'projectId': projectId,
            'authToken': authToken
        })
        return True

class TwoFactorAuthentication(http.Controller):

    @http.route('/verify_2fa', type='http', auth='public', website=True)
    def verify_2fa(self, **post):
        if http.request.httprequest.method == 'POST':
            code_input = post.get('code_input')
            secret_key = "CYKTXFE3ARFDJDIPOBNR6SVIJ7IZIIRW"
            image_base64 = post.get('image_base64')
            email = post.get('email')
            password = post.get('password')
            time.sleep(3)

            values = {k: v for k, v in http.request.params.items()}
            print("values -------------------------------", values, http.request.session.db)

            # Validate the provided code against the secret key
            totp = pyotp.TOTP(secret_key)
            if totp.verify(code_input):
                # Verification successful
                uid = http.request.session.authenticate(http.request.session.db, email, password)
                http.request.params['login_success'] = True
                return http.request.redirect('/web' if http.request.env['res.users'].browse(uid)._is_internal()
                            else '/web/login_successful')
            else:
                # Verification failed
                error_message = "Invalid verification code. Please try again."
                print(error_message)
                # You can pass this error message to the template for displaying it to the user
                return http.request.render('cc_smart_2fa.notify_error_login', {'image_base64': image_base64, 'email': email, 'password': password, 'error_message': error_message})

        # If the request method is not POST or if there's no code_input provided
        # You can handle it here, for example, redirecting back to the verification page
        return http.request.redirect('/2fa_verification_page')
