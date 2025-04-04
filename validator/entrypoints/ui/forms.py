#!/usr/bin/python3

# forms.py
# Date:  24/09/2020
# Author: Mihai Coșleț
# Email: coslet.mihai@gmail.com

"""
    Form classes for use in views.

"""
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import StringField, TextAreaField, RadioField, MultipleFileField
from wtforms.validators import DataRequired
from validator.service_layer.ap_manager import ApplicationProfileManager

from validator.utils.constants import HTML_EXTENSION, TTL_EXTENSION, ZIP_EXTENSION


# Base AP class
class ApplicationProfileForm(FlaskForm):
    choices = ApplicationProfileManager().list_aps()
    application_profile = RadioField('Application profile', choices=choices)


# Base SHACL Shapes class
class SHACLShapesForm(FlaskForm):
    schema_files = MultipleFileField('Data shape files', description="Current maximum accepted files: 5.")


class ApplicationProfileDataFileForm(ApplicationProfileForm):
    data_file = FileField('Data file', validators=[FileRequired()])


class ApplicationProfileURLForm(ApplicationProfileForm):
    endpoint_url = StringField('Endpoint URL', validators=[DataRequired()])
    graphs = TextAreaField('Graphs', description='Separate them through spaces. example: graph1 graph2')


class SHACLShapesDataFileForm(SHACLShapesForm):
    data_file = FileField('Data file', validators=[FileRequired()])


class SHACLShapesURLForm(SHACLShapesForm):
    endpoint_url = StringField('Endpoint URL', validators=[DataRequired()])
    graphs = TextAreaField('Graphs', description='Separate them through spaces. example: graph1 graph2')


class RequestReport(FlaskForm):
    report_type = RadioField('Choose the report extension',
                             choices=[(TTL_EXTENSION, 'Turtle report'), (HTML_EXTENSION, 'HTML report'),
                                      (ZIP_EXTENSION, 'Both reports')])
