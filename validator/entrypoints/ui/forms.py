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

from validator.entrypoints.api.helpers import HTML_EXTENSION, TTL_EXTENSION, ZIP_EXTENSION


class BaseValidateForm(FlaskForm):
    report_extension = RadioField('Choose the report extension',
                                  choices=[(TTL_EXTENSION, 'Turtle report'), (HTML_EXTENSION, 'HTML report'),
                                           (ZIP_EXTENSION, 'Both reports')])
    schema_files = MultipleFileField('Data shape files', description="Current maximum accepted files: 5.")


class ValidateFromFileForm(BaseValidateForm):
    data_file = FileField('Data file', validators=[FileRequired()])


class ValidateSPARQLEndpointForm(BaseValidateForm):
    endpoint_url = StringField('Endpoint URL', validators=[DataRequired()])
    graphs = TextAreaField('Graphs', description='Separate them through spaces. example: graph1 graph2')
