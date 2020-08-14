from controllers import app, index, upload

app.add_api_route('/', index)
app.add_api_route('/upload', upload)
