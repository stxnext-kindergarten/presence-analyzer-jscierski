# -*- coding: utf-8 -*-
"""
Presence analyzer. Registering blueprints here, not in main.py to avoid
circular imports (main imports blueprints, blueprints dependencies import
main etc.).
"""
from presence_analyzer.main import app
from presence_analyzer.blueprints.api_v1.views import api_v1
from presence_analyzer.blueprints.website.views import website

app.register_blueprint(website)
app.register_blueprint(api_v1, url_prefix='/api/v1')
