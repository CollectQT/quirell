def run():
    from quirell.webapp import app
    app.run(host='0.0.0.0', port=5000, debug=app.config['DEBUG'], use_reloader=False)
