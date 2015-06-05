# Contributing to Quirell

## Adding a new capability to users

This section describes how to add a new capability to users, using the ability to create posts as an example. Here's how it went down:

1. Did several hours worth of design and architecture planning that I won't document here (because I did it too long ago at this point)

1. Updated the documentation about the user object inside of `readme-database.md` to show the new user attribute that would exist, that being `user.data.posts`

1. Added the previously mentioned attribute (i.e. `posts` onto `user.data`) onto the only user that currently exists via a short manually written python script. A note that this process should **definitely** be automated in the future, to prevent unforeseen errors. Further, in the future there should be scripts that automatically check every data object in the database to make sure that it fits the way users are supposed to be defined.

1. Added that same attribute to `quirell.webapp.user.create` so that newly created users will get it also

1. Added a database function (`quirell.database.Database.create_post`) to create posts. Database functions are the only ones allowed to interact directly with the neo4j database. This function is the endpoint in post creation.

1. Added a user function (`quirell.webapp.user.create_post`) to create posts. User functions are the only ones allowed to interact with the user object. This function calls `Database.create_post`.

1. Added a view funtion (`quirell.webapp.views.new_post_POST`) that HTML will post to. This function calls `user.create_post` and takes in a form (which will be defined next)

1. Added the python data (`quirell.webapp.forms.new_post`) that helps create a post input form

1. Made the previously mentioned form (ie. `forms.new_post`) available to our HTML templates, by adding `new_post=forms.new_post()` to `quirell.webapp.views.set_globals`.

1. Added the HTML data (`quirell.webapp.templates.forms.new_post`) that displays the post creation form. This uses renders the python data made accessible to it via `set_globals`

1. Added a line to the testing file (`quirell.test.test.webapp_test`) and run tests (`$ python -m quirell.test`). At this point we'll probably notice a bunch of broken things that have to be fixed (I know I did Q_Q). I used this code to help fix my legions of errors:

        new_post = {'content': 'rawr rawr candy'}
        assert session.post(quirell+'/new_post', data=new_post).status_code == 200

1. Eventually I stopped getting error code 500 and instead got code 200 and could verify that the code was working as intended! So the testing line was changed to this:

        assert session.post(quirell+'/new_post', data=new_post).status_code == 200

1. Assuming it still works (i.e. no assertion errors), yay we're finished ! Users can make posts ! Exciting ! Time to commit and get dinner

Some notes:

* I always try to update docs before I update code
* I generally write backend first, front end last. This for the most part avoids writing code where you are calling undefined attributes
* Code that I can write tests for is my favorite code ever, evvvveeeerrr
* Thanks for reading !!!!
