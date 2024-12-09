#  Artists
#  ----------------------------------------------------------------
from flask import Blueprint, render_template, request, flash, redirect, url_for
from models import Venue, Artist, Show
from forms import ArtistForm
from extensions import db, csrf
from datetime import datetime

artist_routes = Blueprint('artist', __name__)

@artist_routes.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data = Artist.query.all()
  return render_template('pages/artists.html', artists=data)

# Create
@artist_routes.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@artist_routes.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
    # Student's Work add create func
    form = ArtistForm(request.form, meta={'csrf': False})

    if form.validate():
        try:
            artist = Artist(
                name=form.name.data,
                city=form.city.data,
                state=form.state.data,
                phone=form.phone.data,
                genres=form.genres.data,
                facebook_link=form.facebook_link.data,
                image_link=form.image_link.data,
                website_link=form.website_link.data,
                seeking_venues=True if form.seeking_venue.data else False,
                seeking_description=form.seeking_description.data
            )
            db.session.add(artist)
            db.session.commit()
            # on successful db insert, flash success
            flash('Artist ' + request.form['name'] + ' was successfully listed!')
            # TODO: on unsuccessful db insert, flash an error instead.
            # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
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
        return render_template('forms/new_artist.html', form=form)

# List
@csrf.exempt
@artist_routes.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
    search_term = request.form.get('search_term', '')
    
    artists = Artist.query.filter(
        db.or_(
            Artist.name.ilike(f'%{search_term}%'),
            Artist.city.ilike(f'%{search_term}%'),
            Artist.state.ilike(f'%{search_term}%')
        )
    ).all()

    response = {
        "count": len(artists),
        "data": []
    }

    current_time = datetime.now()
    
    for artist in artists:
        upcoming_shows = db.session.query(Show).filter(
            Show.artist_id == artist.id,
            Show.start_time > current_time
        ).count()

        response["data"].append({
            "id": artist.id,
            "name": artist.name,
            "num_upcoming_shows": upcoming_shows
        })

    return render_template('pages/search_artists.html', 
                         results=response, 
                         search_term=search_term)

@artist_routes.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
    artist = Artist.query.get_or_404(artist_id)
    current_time = datetime.now()
    
    past_shows_query = db.session.query(Show).join(Venue).\
        filter(Show.artist_id == artist_id).\
        filter(Show.start_time < current_time)
    past_shows = []
    for show in past_shows_query:
        past_shows.append({
            "venue_id": show.venue.id,
            "venue_name": show.venue.name,
            "venue_image_link": show.venue.image_link,
            "start_time": show.start_time.strftime('%Y-%m-%dT%H:%M:%S.000Z')
        })
    
    upcoming_shows_query = db.session.query(Show).join(Venue).\
        filter(Show.artist_id == artist_id).\
        filter(Show.start_time > current_time)
    upcoming_shows = []
    for show in upcoming_shows_query:
        upcoming_shows.append({
            "venue_id": show.venue.id,
            "venue_name": show.venue.name,
            "venue_image_link": show.venue.image_link,
            "start_time": show.start_time.strftime('%Y-%m-%dT%H:%M:%S.000Z')
        })
    
    data = {
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres if artist.genres else [],
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website": artist.website_link,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.seeking_venues,
        "seeking_description": artist.seeking_description,
        "image_link": artist.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows)
    }
    
    return render_template('pages/show_artist.html', artist=data)

# Update
@artist_routes.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    artist = Artist.query.get_or_404(artist_id)
    form = ArtistForm(obj=artist)
    
    if isinstance(artist.genres, str):
        form.genres.data = artist.genres.split(',')
    
    artist_data = {
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres.split(',') if isinstance(artist.genres, str) else artist.genres,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website_link": artist.website_link,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.seeking_venues,
        "seeking_description": artist.seeking_description,
        "image_link": artist.image_link
    }
    
    return render_template('forms/edit_artist.html', form=form, artist=artist_data)

@artist_routes.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    try:
        artist = Artist.query.get_or_404(artist_id)
        form = ArtistForm()

        if form.validate_on_submit():
            artist.name = form.name.data
            artist.city = form.city.data
            artist.state = form.state.data
            artist.phone = form.phone.data
            artist.facebook_link = form.facebook_link.data
            artist.website_link = form.website_link.data
            artist.image_link = form.image_link.data
            artist.seeking_venues = form.seeking_venue.data
            artist.seeking_description = form.seeking_description.data
            artist.genres = form.genres.data
            
            db.session.commit()
            flash(f'Artist {artist.name} was successfully updated!')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f'Error in {field}: {error}')
            return render_template('forms/edit_artist.html', form=form, artist=artist)
            
    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred. Artist {artist_id} could not be updated. Error: {str(e)}')
    finally:
        db.session.close()
    
    return redirect(url_for('artist.show_artist', artist_id=artist_id))