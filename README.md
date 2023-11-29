# Flask-API

swagger =>  https://ceydawebapp.azurewebsites.net/apidocs  
video link => https://youtu.be/Fem8ax_w1II
issues encountered;
When I deployed the project, I received an Application Error. In this case, I entered the azure web app. and I opened configuration in the web app I created. In this section, when I wrote this command "gunicorn --bind=0.0.0.0 --timeout 600 server:app" in the startup command section in the general settings section, my deploy problem was solved.
I had an authentication problem while doing the login part. Then I solved this problem.
I had a problem creating a token. but this problem has also been solved.
