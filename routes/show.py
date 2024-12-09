#  Shows
#  ----------------------------------------------------------------
from flask import Blueprint, render_template, request, flash, redirect, url_for
from models import Show, Artist, Venue
from forms import ShowForm
from extensions import db, csrf
from datetime import datetime

show_routes = Blueprint('show', __name__)

@show_routes.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
    shows_query = db.session.query(Show, Venue, Artist)\
        .join(Venue, Show.venue_id == Venue.id)\
        .join(Artist, Show.artist_id == Artist.id)\
        .all()
    data = []
    for show, venue, artist in shows_query:
        data.append({
            "venue_id": venue.id,
            "venue_name": venue.name,
            "artist_id": artist.id,
            "artist_name": artist.name,
            "artist_image_link": artist.image_link,
            "start_time": show.start_time.strftime('%Y-%m-%dT%H:%M:%S.000Z')
        })
    
    return render_template('pages/shows.html', shows=data)

@show_routes.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@show_routes.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
    form = ShowForm(request.form, meta={'csrf': False})
    if form.validate():
        try:
            show = Show(
                artist_id=form.artist_id.data,
                venue_id=form.venue_id.data,
                start_time=form.start_time.data
            )
            db.session.add(show)
            db.session.commit()
            # on successful db insert, flash success
            flash('Show was successfully listed!')
            # TODO: on unsuccessful db insert, flash an error instead.
            # e.g., flash('An error occurred. Show could not be listed.')
            # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
        except Exception as e:
            db.session.rollback()
            flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
            print(e)
        finally:
            db.session.close()
        return render_template('pages/home.html')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'Error in {field}: {error}')
        return render_template('forms/new_show.html', form=form)