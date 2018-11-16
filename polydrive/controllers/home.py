from polydrive import app


@app.route('/', methods=['GET'])
def home_route():
    return 'PolyDrive v0.0.1'
