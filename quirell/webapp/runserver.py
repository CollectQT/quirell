def run():
    from quirell.webapp import app
    app.run(debug=True, use_reloader=False)
