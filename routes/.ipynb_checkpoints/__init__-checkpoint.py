from flask import Blueprint
from .artist import artist_routes
from .venue import venue_routes
from .show import show_routes

def register_blueprints(app):
    app.register_blueprint(artist_routes)
    app.register_blueprint(venue_routes)
    app.register_blueprint(show_routes)