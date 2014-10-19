# Webapp Readme

## Structure

    paths/

Everything in this folder resolves to a URL path. For example, the file `paths/user/lcyrin.html` creates `http://quirell.TLD/user/lcyrin`. The primary purpose of the `paths/` folder is to generate URLs.

    static/

Static files go here. Like, CSS, JS, images, etc. One exception is that files that build into static files also go here, i.e. `static/scss/main.scss` which builds into `static/css/main.css`

    scripts/

Storage for python scripts.

    templates/

Similarly to the `paths/` folder, html files go in here. In contrast to `paths/`, though, `templates/` is where HTML that will get reused across several pages goes. `template/` contains page elements like the navigation bar, background, resource loading, etc. The primary purpose of the `templates/` folder is to reduce repition within `paths/`

    main.py

routing and sever initalization file

    config.yaml

holds sitewide configuration variables
