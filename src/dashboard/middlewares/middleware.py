class ContentSecurityPolicyMiddleware(object):
    def process_response(self, request, response):
        response['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self'; font-src 'self'; connect-src 'self';"
        return response
