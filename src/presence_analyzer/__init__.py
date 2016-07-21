# -*- coding: utf-8 -*-
"""
Presence analyzer. Registering blueprints here, not in main.py to avoid
circular imports (main imports blueprints, blueprints dependencies import
main etc.).
"""
from presence_analyzer.main import app
from presence_analyzer.blueprints import website, api_v1

app.register_blueprint(website)
app.register_blueprint(api_v1, url_prefix='/api/v1')
