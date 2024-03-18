# -*- encoding: utf-8 -*-

import logging
import werkzeug
import werkzeug.exceptions
import werkzeug.utils
import werkzeug.wrappers
import werkzeug.wsgi
from werkzeug.urls import url_encode, iri_to_uri
import odoo
import odoo.modules.registry
from odoo.tools.translate import _
from odoo import http, tools
from odoo.http import content_disposition, dispatch_rpc, request, Response
from odoo.service import security
from odoo.addons.web.controllers.home import Home
import qrcode
import pyotp
import base64
from io import BytesIO
import time
import requests as req

_logger = logging.getLogger(__name__)

# Shared parameters for all login/signup flows
SIGN_UP_REQUEST_PARAMS = {'db', 'login', 'debug', 'token', 'message', 'error', 'scope', 'mode',
                          'redirect', 'redirect_hostname', 'email', 'name', 'partner_id',
                          'password', 'confirm_password', 'city', 'country_id', 'lang', 'signup_email'}
LOGIN_SUCCESSFUL_PARAMS = set()

# ----------------------------------------------------------
# Odoo Web helpers
# ----------------------------------------------------------


def is_user_internal(uid):
    return request.env['res.users'].browse(uid)._is_internal()


# override
def _get_login_redirect_url(uid, redirect=None):
    """ Decide if user requires a specific post-login redirect, e.g. for 2FA, or if they are
    fully logged and can proceed to the requested URL
    """
    if request.session.uid:  # fully logged
        return redirect or ('/web' if is_user_internal(request.session.uid)
                            else '/web/login_successful')

    # partial session (MFA)
    url = request.env(user=uid)['res.users'].browse(uid)._mfa_url()
    print("url -------------------",  request.env(user=uid)['res.users'].browse(uid),url)
    if not redirect:
        return url

    parsed = werkzeug.urls.url_parse(url)
    qs = parsed.decode_query()
    qs['redirect'] = redirect
    return parsed.replace(query=werkzeug.urls.url_encode(qs)).to_url()


# override
def ensure_db(redirect='/web/database/selector', db=None):
    # This helper should be used in web client auth="none" routes
    # if those routes needs a db to work with.
    # If the heuristics does not find any database, then the users will be
    # redirected to db selector or any url specified by `redirect` argument.
    # If the db is taken out of a query parameter, it will be checked against
    # `http.db_filter()` in order to ensure it's legit and thus avoid db
    # forgering that could lead to xss attacks.
    if db is None:
        db = request.params.get('db') and request.params.get('db').strip()

    # Ensure db is legit
    if db and db not in http.db_filter([db]):
        db = None

    if db and not request.session.db:
        # User asked a specific database on a new session.
        # That mean the nodb router has been used to find the route
        # Depending on installed module in the database, the rendering of the page
        # may depend on data injected by the database route dispatcher.
        # Thus, we redirect the user to the same page but with the session cookie set.
        # This will force using the database route dispatcher...
        r = request.httprequest
        url_redirect = werkzeug.urls.url_parse(r.base_url)
        if r.query_string:
            # in P3, request.query_string is bytes, the rest is text, can't mix them
            query_string = iri_to_uri(r.query_string)
            url_redirect = url_redirect.replace(query=query_string)
        request.session.db = db
        werkzeug.exceptions.abort(request.redirect(url_redirect.to_url(), 302))

    # if db not provided, use the session one
    if not db and request.session.db and http.db_filter([request.session.db]):
        db = request.session.db

    # if no database provided and no database in session, use monodb
    if not db:
        all_dbs = http.db_list(force=True)
        if len(all_dbs) == 1:
            db = all_dbs[0]

    # if no db can be found til here, send to the database selector
    # the database selector will redirect to database manager if needed
    if not db:
        werkzeug.exceptions.abort(request.redirect(redirect, 303))

    # always switch the session to the computed db
    if db != request.session.db:
        request.session = http.root.session_store.new()
        request.session.update(http.get_default_session(), db=db)
        request.session.context['lang'] = request.default_lang()
        werkzeug.exceptions.abort(request.redirect(request.httprequest.url, 302))

# ----------------------------------------------------------
# Odoo Web web Controllers
# ----------------------------------------------------------


class CustomHome(Home):

    # override
    def _login_redirect(self, uid, redirect=None):
        return _get_login_redirect_url(uid, redirect)
    # override
    @http.route('/web/login', type='http', auth="none")
    def web_login(self, redirect=None, **kw):
        print("-------------***************________________")
        ensure_db()
        request.params['login_success'] = False
        if request.httprequest.method == 'GET' and redirect and request.session.uid:
            return request.redirect(redirect)

        # simulate hybrid auth=user/auth=public, despite using auth=none to be able
        # to redirect users when no db is selected - cfr ensure_db()
        if request.env.uid is None:
            if request.session.uid is None:
                # no user -> auth=public with specific website public user
                request.env["ir.http"]._auth_method_public()
            else:
                # auth=user
                request.update_env(user=request.session.uid)

        values = {k: v for k, v in request.params.items() if k in SIGN_UP_REQUEST_PARAMS}
        print("values ==============", values)
        try:
            values['databases'] = http.db_list()
        except odoo.exceptions.AccessDenied:
            values['databases'] = None

        if request.httprequest.method == 'POST':
            settings = http.request.env['cc_smart_2fa'].sudo().search([], limit=1)
            # url = "https://api-stg.crossclassify.com/projects/" + settings.projectId + "/fraudServices/takeover/makeFormDecision"
            # Define the payload (data) you want to send in the POST request
            # payload = {
            #     "account": {
            #         "email": request.params['email']
            #     }
            # }
            headers = {
                'Authorization': 'Bearer ' + settings.authToken,
                'Content-Type': 'application/json'  # Assuming the content type is JSON
            }
            # Make the POST request
            # response = req.post(url, json=payload, headers=headers)
            # Check the response
            # if response.status_code == 201 or response.status_code == 202:
                # print("Request successful!")
                # print("Response:", response.json())
                # result = response.json()
            new_url = "https://api-stg.crossclassify.com/projects/" + settings.projectId + "/fraudServices/takeover/makeFormDecision?where={%22account.email%22:%22" + request.params['email'] + "%22}&page=0&max_results=100"
            print(new_url)
            response = req.get(new_url, headers=headers)
            # Check the response
            if response.status_code == 201 or response.status_code == 202 or response.status_code == 200:
                print("Request Get successful!")
                print("Response Get:", response.json())
                result = response.json()
                # if (result['_items'] and result['_items'][0]):
                #     is_Blocked = result['_items'][0]['isBlocked']
                #     if (is_Blocked or not is_Blocked):
                secret_key = "CYKTXFE3ARFDJDIPOBNR6SVIJ7IZIIRW"
                totp = pyotp.totp.TOTP(secret_key)
                verification_code = totp.now()
                uri = totp.provisioning_uri(name=request.params['email'], issuer_name="Smart 2FA")
                qr_img = qrcode.make(uri)
                buffer = BytesIO()
                qr_img.save(buffer, format="PNG")
                image_base64 = base64.b64encode(buffer.getvalue()).decode()
                time.sleep(5)
                return request.render('cc_smart_2fa.notify_error_login', {"image_base64":image_base64, 'email': request.params['email'], 'password': request.params['password']})
            else: 
                print("Requestv Get failed with status code:", response.status_code)
                print("Response Get:", response.text)
                request.params['login_success'] = False
                secret_key = "CYKTXFE3ARFDJDIPOBNR6SVIJ7IZIIRW"
                totp = pyotp.totp.TOTP(secret_key)
                verification_code = totp.now()
                uri = totp.provisioning_uri(name=request.params['email'], issuer_name="Smart 2FA")
                qr_img = qrcode.make(uri)
                buffer = BytesIO()
                qr_img.save(buffer, format="PNG")
                image_base64 = base64.b64encode(buffer.getvalue()).decode()
                time.sleep(5)
                return request.render('cc_smart_2fa.notify_error_login', {"image_base64":image_base64, 'email': request.params['email'], 'password': request.params['password']})
            # else:
            #     print("Request failed with status code:", response.status_code)
            #     print("Response:", response.text)
            #     request.params['login_success'] = False
            #     secret_key = "CYKTXFE3ARFDJDIPOBNR6SVIJ7IZIIRW"
            #     totp = pyotp.totp.TOTP(secret_key)
            #     verification_code = totp.now()
            #     uri = totp.provisioning_uri(name=request.params['email'], issuer_name="Smart 2FA")
            #     qr_img = qrcode.make(uri)
            #     buffer = BytesIO()
            #     qr_img.save(buffer, format="PNG")
            #     image_base64 = base64.b64encode(buffer.getvalue()).decode()
            #     time.sleep(5)
            #     return request.render('cc_smart_2fa.notify_error_login', {"image_base64":image_base64, 'email': request.params['email'], 'password': request.params['password']})

                
            try:
                request.session['password'] = request.params['password']
                request.session['login'] = request.params['email']
                if 'login' in values and not request.session.get('auth_complete'):
                    user = request.env['res.users'].sudo().search([('login', '=', values['login'])], limit=1)
                    if user:
                        security.check(request.session.db, user.id, request.params['password'])
                    if user and user.user_2f_enable_status:
                        request.session['login_user'] = user.id
                        return http.redirect_with_hash('/web/auth_login')

                uid = request.session.authenticate(request.db, request.params['email'], request.params['password'])
                request.params['login_success'] = True
                return request.redirect(self._login_redirect(uid, redirect=redirect))
            except odoo.exceptions.AccessDenied as e:
                if e.args == odoo.exceptions.AccessDenied().args:
                    values['error'] = _("Wrong login/password")
                else:
                    values['error'] = e.args[0]
        else:
            if 'error' in request.params and request.params.get('error') == 'access':
                values['error'] = _('Only employees can access this database. Please contact the administrator.')

        if 'login' not in values and request.session.get('auth_login'):
            values['login'] = request.session.get('auth_login')

        if not odoo.tools.config['list_db']:
            values['disable_database_manager'] = True
        resultCon = request.env['cc_smart_2fa'].sudo().search([], limit=1)
        values['apikey'] = resultCon.apikey
        values['siteId'] = resultCon.siteId
        print("--------------------------------", resultCon.apikey, resultCon.siteId)
        response = request.render('web.login', values)
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['Content-Security-Policy'] = "frame-ancestors 'self'"
        return response


class Website(CustomHome):

    # override
    @http.route(website=True, auth="public", sitemap=False)
    def web_login(self, *args, **kw):
        return super().web_login(*args, **kw)