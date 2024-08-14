from chalice import Chalice

app = Chalice(app_name='FireflyCompanion')


@app.route('/')
def index():
    return {'hello': 'world'}
