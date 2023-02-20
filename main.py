from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import SubmitField
from wtforms.validators import DataRequired
from flask_ckeditor import CKEditor, CKEditorField
import boto3
import os
import sys
from tempfile import gettempdir
from contextlib import closing
from bs4 import BeautifulSoup



app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
ckeditor = CKEditor(app)
Bootstrap(app)


class TextForm(FlaskForm):
    text = CKEditorField("Enter text here", validators=[DataRequired()])
    submit = SubmitField("Read Text")


aws_access_key_id = os.environ.get('AWS_ACCESS_KEY_ID')
aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY')


@app.route("/", methods=["GET", "POST"])
def home():
    form = TextForm()

    if form.validate_on_submit():
        aws_mag_con = boto3.session.Session(aws_access_key_id=aws_access_key_id,
                                            aws_secret_access_key=aws_secret_access_key,)
        client = aws_mag_con.client(service_name="polly", region_name="us-east-1")
        print(form.text.data)
        ckeditor_input = form.text.data
        soup = BeautifulSoup(ckeditor_input, 'html.parser')
        stripped_text = soup.get_text()
        response = client.synthesize_speech(VoiceId="Joanna", OutputFormat="mp3", Text=stripped_text,
                                            Engine="neural")
        print(response)
        if "AudioStream" in response:
            with closing(response["AudioStream"]) as stream:
                output = os.path.join(gettempdir(), "speech.mp3")
                try:
                    with open(output, "wb") as file:
                        file.write(stream.read())
                except IOError as error:
                    print(error)
                    sys.exit(-1)
        else:
            print("could not find the stream!")
            sys.exit(-1)
        if sys.platform == "win32" or sys.platform == "win64":
            os.startfile(output)

    return render_template("index.html", form=form)


if __name__ == "__main__":
    app.run(debug=True)
