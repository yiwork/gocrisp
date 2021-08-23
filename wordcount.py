from flask import Flask, request, render_template_string, json
import logging, os, re
from binaryornot.check import is_binary
from time import strftime, gmtime
from random import choice

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = os.environ.get("UPLOAD_FOLDER") or "./uploaded" or "/tmp"
app.config['UPLOAD_EXTENSIONS'] = ['.txt','csv','rst', 'rtf']
app.config['MAX_CONTENT_LENGTH'] = os.environ.get("MAX_CONTENT_LENGTH") or 16 * 1000 * 1000

# for simplicity sake, embedding response html directy in code.
# This really should be in a separate template file
# Also all errors and responses will display this page as well

upload_form_template = '''
    <!DOCTYPE html>
    <html>
    {% if error_msg %} 
        <div style="color:red;background-color:#F6F6F6"">{{ error_msg }}</div>
    {% endif %}

    {% if word_count %}
        <h3><div style="color:green;background-color:#F6F6F6">File {{ file_name }} has {{ word_count }} words in it</div></h3>
    {% endif %}
    <h2>Go Crisp file upload service</h2>
    <h3>Form only takes plain text file</h3>
    <form action="/" method="post" enctype="multipart/form-data">
      <input type="file" name="destfile" accept="text/plain">
      <input type="submit" value="Upload Now!">
    </form>

    <h3>To submit via curl: curl -XPOST -F "destfile=@<file>" -H "accept-encoding=application/json" localhost:5000</h3>
    </html>

'''

# monitoring routes
@app.route("/ping")
def ping():
    return f"Pong! App Name: {__name__}", 200


@app.route("/", methods=['POST','GET'])
def get_word_count():

    if request.method == 'GET':
        return render_template_string(upload_form_template), 200
    if request.method == 'POST':

        if 'destfile' not in request.files:
            app.logger.warn("Posted form missing destfile field")
            return assemble_response(error_msg="Form submitted without file"), 400
        else:

            uploaded_file = request.files['destfile']
            if uploaded_file.filename == '':
                app.logger.warn("no files selected to be uploaded")
                return assemble_response(error_msg="Form submitted without file"), 400
            else:
                #new_file_name = strftime("%Y-%m-%dT%H:%M:%S,%f", gmtime())
                new_file_name = os.path.join(
                        app.config['UPLOAD_FOLDER'], 
                        uploaded_file.filename.rsplit('/',1).pop() + '-' + strftime("%Y%m%dT%H:%M:%S", gmtime())
                        )
                uploaded_file.save(new_file_name)                
                if is_binary(new_file_name):
                    app.logger.error("Binary file uploaded")
                    return assemble_response(
                                error_msg="Uploaded file is binary object. Cannot count words in binary file"
                            ), 400
                else:
                    word_count = 0
                    with open(new_file_name) as f:
                        for line in f:
                            # words = re.findall(r'[a-zA-Z0-9_-\']+',line)
                            words = line.split()
                            word_count += len(words)
                    return assemble_response(
                                file_name=str(uploaded_file.filename.rsplit('/',1).pop()), 
                                word_count=word_count
                            ), 200
    else:
        app.logger.error('Bad method!')
        return assemble_response(error_msg="Wrong method submitted with form"), 405 


def assemble_response(file_name=None, word_count=None, error_msg=None):
    if request.accept_mimetypes.accept_json:
        if error_msg:
            return json.dumps({"error": error_msg})
        else:
            return json.dumps({"word_count": word_count, "file_name": file_name})
    else:
        if error_msg:
            return render_template_string(upload_form_template, error_msg=error_msg)
        else:
            return render_template_string(upload_form_template, word_count=word_count, file_name=file_name)


#    return render_template_string(template,file_name=file_name, word_count=word_count, error_msg=error_msg)

if __name__ == "__main__":
    app.run()

