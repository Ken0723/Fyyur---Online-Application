#  Venues
#  ----------------------------------------------------------------
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from models import Venue, Artist, Show
from forms import VenueForm
from extensions import db, csrf
from datetime import datetime

venue_routes = Blueprint('venue', __name__)

@venue_routes.route('/venues')
def venues():
  # TODO: replace with real venues data.
    locations = db.session.query(Venue.city, Venue.state).distinct().all()
    currentTime = datetime.now()
    
    data = []
    for location in locations:
        venues_in_location = Venue.query.filter_by(
            city=location.city, 
            state=location.state
        ).all()
        
        venueData = []
        for venue in venues_in_location:
            upcoming_shows = db.session.query(Show).filter(
                Show.venue_id == venue.id,
                Show.start_time > currentTime
            ).count()
            
            venueData.append({
                "id": venue.id,
                "name": venue.name,
                "num_upcoming_shows": upcoming_shows
            })
        
        data.append({
            "city": location.city,
            "state": location.state,
            "venues": venueData
        })
    
    return render_template('pages/venues.html', areas=data)

@csrf.exempt
@venue_routes.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    search_term = request.form.get('search_term', '')
    
    venues = Venue.query.filter(
        db.or_(
            Venue.name.ilike(f'%{search_term}%'),
            Venue.city.ilike(f'%{search_term}%'),
            Venue.state.ilike(f'%{search_term}%')
        )
    ).all()

    response = {
        "count": len(venues),
        "data": []
    }

    current_time = datetime.now()
    
    for venue in venues:
        upcoming_shows = db.session.query(Show).filter(
            Show.venue_id == venue.id,
            Show.start_time > current_time
        ).count()

        response["data"].append({
            "id": venue.id,
            "name": venue.name,
            "num_upcoming_shows": upcoming_shows
        })

    return render_template('pages/search_venues.html', 
                         results=response, 
                         search_term=search_term)

@venue_routes.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
    venue = Venue.query.get_or_404(venue_id)

    current_time = datetime.now()

    past_shows_query = db.session.query(Show, Artist)\
        .join(Artist)\
        .filter(Show.venue_id == venue_id)\
        .filter(Show.start_time < current_time)\
        .all()

    upcoming_shows_query = db.session.query(Show, Artist)\
        .join(Artist)\
        .filter(Show.venue_id == venue_id)\
        .filter(Show.start_time >= current_time)\
        .all()

    past_shows = []
    for show, artist in past_shows_query:
        past_shows.append({
            "artist_id": artist.id,
            "artist_name": artist.name,
            "artist_image_link": artist.image_link,
            "start_time": show.start_time.strftime('%Y-%m-%dT%H:%M:%S.000Z')
        })

    upcoming_shows = []
    for show, artist in upcoming_shows_query:
        upcoming_shows.append({
            "artist_id": artist.id,
            "artist_name": artist.name,
            "artist_image_link": artist.image_link,
            "start_time": show.start_time.strftime('%Y-%m-%dT%H:%M:%S.000Z')
        })

    data = {
        "id": venue.id,
        "name": venue.name,
        "genres": venue.genres if venue.genres else [],
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website_link": venue.website_link,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.seeking_talent,
        "seeking_description": venue.seeking_description,
        "image_link": venue.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows)
    }
    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@venue_routes.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@venue_routes.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
    form = VenueForm(request.form, meta={'csrf': False})
    if form.validate():
        try:
            venue = Venue(
                name=form.name.data,
                city=form.city.data,
                state=form.state.data,
                address=form.address.data,
                phone=form.phone.data,
                genres=form.genres.data,
                facebook_link=form.facebook_link.data,
                image_link=form.image_link.data,
                website_link=form.website_link.data,
                seeking_talent=True if form.seeking_talent.data else False,
                seeking_description=form.seeking_description.data
            )
            db.session.add(venue)
            db.session.commit()
            # on successful db insert, flash success
            flash('Venue ' + request.form['name'] + ' was successfully listed!')
            # TODO: on unsuccessful db insert, flash an error instead.
            # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
            # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
        except Exception as e:
            db.session.rollback()
            flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
            print(e)
        finally:
            db.session.close()
        return render_template('pages/home.html')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'Error in {field}: {error}')
        return render_template('forms/new_venue.html', form=form)
    

@venue_routes.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
    error = False
    try:
        Show.query.filter_by(venue_id=venue_id).delete()
        venue = Venue.query.get(venue_id)
        venueName = venue.name
        
        db.session.delete(venue)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Venue {venueName} was successfully deleted!',
            'redirect_url': '/'
        })
    except Exception as e:
        error = True
        db.session.rollback()
        print(e)
        flash('An error occurred. Venue ' + vanueName + ' could not be deleted.')
        return jsonify({
            'success': False,
            'redirect_url': f'/venues/{venue_id}'
        })
    finally:
        db.session.close()


@venue_routes.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    venue = Venue.query.get_or_404(venue_id)
    form = VenueForm(obj=venue)
    
    if isinstance(venue.genres, str):
        form.genres.data = venue.genres.split(',')
    
    venue_data = {
        "id": venue.id,
        "name": venue.name,
        "genres": venue.genres if isinstance(venue.genres, str) else venue.genres,
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website_link": venue.website_link,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.seeking_talent,
        "seeking_description": venue.seeking_description,
        "image_link": venue.image_link
    }
    
    print(venue_data)
    
    return render_template('forms/edit_venue.html', form=form, venue=venue_data)

@venue_routes.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    try:
        venue = Venue.query.get_or_404(venue_id)
        form = VenueForm(request.form)
        
        if form.validate_on_submit():
            venue.name = form.name.data
            venue.city = form.city.data
            venue.state = form.state.data
            venue.address = form.address.data
            venue.phone = form.phone.data
            venue.facebook_link = form.facebook_link.data
            venue.website_link = form.website_link.data
            venue.image_link = form.image_link.data
            venue.seeking_talent = form.seeking_talent.data
            venue.seeking_description = form.seeking_description.data
            venue.genres = form.genres.data
            
            db.session.commit()
            flash(f'Venue {venue.name} was successfully updated!')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f'Error in {field}: {error}')
            return render_template('forms/edit_venue.html', form=form, venue=venue)
            
    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred. Venue {venue_id} could not be updated. Error: {str(e)}')
    finally:
        db.session.close()
    
    return redirect(url_for('venue.show_venue', venue_id=venue_id))