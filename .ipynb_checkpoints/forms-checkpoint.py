from datetime import datetime
from flask_wtf import FlaskForm as Form
from wtforms import StringField, SelectField, SelectMultipleField, DateTimeField, BooleanField
from wtforms.validators import DataRequired, AnyOf, URL, ValidationError, Optional
import re
from enums import Genre, State

def validate_phone(form, field):
    pattern = r'^\(?([0-9]{3})\)?[-. ]?([0-9]{3})[-. ]?([0-9]{4})$'
    
    if not re.match(pattern, field.data):
        raise ValidationError('Invalid phone number. Accepted formats: 1234567890, 123.456.7890, 123-456-7890, 123 456 7890')

def validate_facebook_link(form, field):
    if field.data:
        if not field.data.startswith('https://www.facebook.com/'):
            raise ValidationError('Must be a valid Facebook URL starting with https://www.facebook.com/')

def validate_link(form, field):
    if field.data:
        if not field.data.startswith(('http://', 'https://')):
            raise ValidationError('Website link must start with http:// or https://')

class ShowForm(Form):
    artist_id = StringField(
        'artist_id'
    )
    venue_id = StringField(
        'venue_id'
    )
    start_time = DateTimeField(
        'start_time',
        validators=[DataRequired()],
        default= datetime.today()
    )

class VenueForm(Form):
    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = SelectField(
        'state', validators=[DataRequired()],
        choices=State.choices()
    )
    address = StringField(
        'address', validators=[DataRequired()]
    )
    phone = StringField(
        'phone',
        validators=[DataRequired(), validate_phone],
        description="Format: XXX-XXX-XXXX"
    )
    image_link = StringField(
        'image_link',
        validators=[Optional(), URL(), validate_link],
    )
    genres = SelectMultipleField(
        # TODO implement enum restriction
        'genres', validators=[DataRequired()],
        coerce=str,
        choices=Genre.choices()
    )
    facebook_link = StringField(
        'facebook_link', 
        validators=[Optional(), URL(), validate_facebook_link]
     )
    website_link = StringField(
        'website_link',
        validators=[Optional(), URL(), validate_link],
    )
    seeking_talent = BooleanField( 'seeking_talent' )

    seeking_description = StringField(
        'seeking_description'
    )



class ArtistForm(Form):
    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = SelectField(
        'state', validators=[DataRequired()],
        choices=State.choices()
    )
    phone = StringField(
        'phone',
        validators=[DataRequired(), validate_phone],
        description="Format: XXX-XXX-XXXX"
    )
    image_link = StringField(
        'image_link',
        validators=[Optional(), URL(), validate_link],
    )
    genres = SelectMultipleField(
        'genres', validators=[DataRequired()],
        coerce=str,
        choices=Genre.choices()
     )
    facebook_link = StringField(
        # TODO implement enum restriction
        'facebook_link', 
        validators=[Optional(), URL(), validate_facebook_link]
     )
    website_link = StringField(
        'website_link',
        validators=[Optional(), URL(), validate_link],
    )
    seeking_venue = BooleanField( 'seeking_venue' )

    seeking_description = StringField(
            'seeking_description'
     )