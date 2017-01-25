.. raw:: html

   <p align="center">

.. raw:: html

   </p>

Zappa - Serverless Python Web Services
======================================

|Build Status| |Coverage| |Requirements Status| |PyPI| |Slack|

**Zappa** makes it super easy to deploy all Python WSGI applications on
AWS Lambda + API Gateway. Think of it as "serverless" web hosting for
your Python web apps.

    What do you mean "serverless"?

Okay, so there still is a server - but it only has a *40 millisecond*
life cycle! Serverless in this case means **"without any permanent
infrastucture."**

With a traditional HTTP server, the server is online 24/7, processing
requests one by one as they come in. If the queue of incoming requests
grows too large, some requests will time out. With Zappa, **each request
is given its own virtual HTTP "server"** by Amazon API Gateway. AWS
handles the horizontal scaling automatically, so no requests ever time
out. Each request then calls your application from a memory cache in AWS
Lambda and returns the response via Python's WSGI interface. After your
app returns, the "server" dies.

Better still, with Zappa you only pay for the milliseconds of server
time that you use, so it's many **orders of magnitude cheaper** than
VPS/PaaS hosts like Linode or Heroku - and in most cases, it's
completely free. Plus, there's no need to worry about load balancing or
keeping servers online ever again.

It's great for deploying serverless microservices with frameworks like
Flask and Bottle, and for hosting larger web apps and CMSes with Django.
Or, you can use any WSGI-compatible app you like! You **probably don't
need to change your existing applications** to use it, and you're not
locked into using it.

And finally, Zappa is **super easy to use**. You can deploy your
application with a single command out of the box.

Using **Zappa** means:

-  **No more** tedious web server configuration!
-  **No more** paying for 24/7 server uptime!
-  **No more** worrying about load balancing / scalability!
-  **No more** worrying about keeping servers online!

**Awesome!**

.. raw:: html

   <p align="center">

.. raw:: html

   </p>

Installation and Configuration
==============================

*Before you begin, make sure you have a valid AWS account and your `AWS
credentials
file <https://blogs.aws.amazon.com/security/post/Tx3D6U6WSFGOK2H/A-New-and-Standardized-Way-to-Manage-Credentials-in-the-AWS-SDKs>`__
is properly installed.*

**Zappa** can easily be installed through pip, like so:

::

    $ pip install zappa

If you're looking for Django-specific integration, you should probably
check out
***`django-zappa <https://github.com/Miserlou/django-zappa>`__***
instead.

Next, you'll need to define your local and server-side settings.

Settings
--------

Next, you'll need to define a few settings for your Zappa deployment
environments in a file named *zappa\_settings.json* in your project
directory. The simplest example is:

.. code:: javascript

    {
        "dev": { // The name of your environment
           "s3_bucket": "lmbda", // The name of your S3 bucket
           "app_function": "your_module.app" // The python path to your WSGI application function. In Flask, this is your 'app' object.
        }
    }

You can define as many environments as your like - we recommend having
*dev*, *staging*, and *production*.

Now, you're ready to deploy!

Basic Usage
===========

Initial Deployments
-------------------

Once your settings are configured, you can package and deploy your
application to an environment called "production" with a single command:

::

    $ zappa deploy production
    Deploying..
    Your application is now live at: https://7k6anj0k99.execute-api.us-east-1.amazonaws.com/production

And now your app is **live!** How cool is that?!

To explain what's going on, when you call 'deploy', Zappa will
automatically package up your application and local virtual environment
into a Lambda-compatible archive, replace any dependencies with versions
`precompiled for
Lambda <https://github.com/Miserlou/lambda-packages>`__, set up the
function handler and necessary WSGI Middleware, upload the archive to
S3, register it as a new Lambda function, create a new API Gateway
resource, create WSGI-compatible routes for it, link it to the new
Lambda function, and finally delete the archive from your S3 bucket.
Handy!

Updates
-------

If your application has already been deployed and you only need to
upload new Python code, but not touch the underlying routes, you can
simply:

::

    $ zappa update production
    Updating..
    Your application is now live at: https://7k6anj0k99.execute-api.us-east-1.amazonaws.com/production

This creates a new archive, uploads it to S3 and updates the Lambda
function to use the new code, but doesn't touch the API Gateway routes.

Rollback
--------

You can also rollback the deployed code to a previous version by
supplying the number of revisions to return to. For instance, to
rollback to the version deployed 3 versions ago:

::

    $ zappa rollback production -n 3

Scheduling
----------

Zappa can be used to easily schedule functions to occur on regular
intervals. Just list your functions and the expression to schedule them
using `cron or rate
syntax <http://docs.aws.amazon.com/lambda/latest/dg/tutorial-scheduled-events-schedule-expressions.html>`__
in your *zappa\_settings.json* file:

.. code:: javascript

         {
            "production": {
                ...
                "events": [{
                    "function": "your_module.your_function", // The function to execute
                    "expression": "rate(1 minute)" // When to execute it (in cron or rate format)
                }],
                ...
        }

And then:

::

    $ zappa schedule production

And now your function will execute every minute!

If you want to cancel these, you can simply use the 'unschedule'
command:

::

    $ zappa unschedule production

And now your scheduled event rules are deleted.

Undeploy
--------

If you need to remove the API Gateway and Lambda function that you have
previously published, you can simply:

::

    $ zappa undeploy production

You will be asked for confirmation before it executes.

Tailing Logs
------------

You can watch the logs of a deployment by calling the "tail" management
command.

::

    $ zappa tail production

Advanced Usage
==============

There are other settings that you can define in your local settings to
change Zappa's behavior. Use these at your own risk!

.. code:: javascript

     {
        "dev": {
            "aws_region": "us-east-1", // AWS Region (default US East),
            "cache_cluster_enabled": false, // Use APIGW cache cluster (default False)
            "cache_cluster_size": .5, // APIGW Cache Cluster size (default 0.5)
            "debug": true // Print Zappa configuration errors tracebacks in the 500
            "delete_zip": true // Delete the local zip archive after code updates
            "domain": "yourapp.yourdomain.com", // Required if you're using a domain
            "events": [{
                "function": "your_module.your_function", // The function to execute
                "expression": "rate(1 minute)" // When to execute it (in cron or rate format)
            }],
            "exclude": ["*.gz", "*.pem"], // A list of regex patterns to exclude from the archive
            "http_methods": ["GET", "POST"], // HTTP Methods to route,
            "integration_response_codes": [200, 301, 404, 500], // Integration response status codes to route
            "keep_warm": true, // Create CloudWatch events to keep the server warm.
            "lambda_handler": "your_custom_handler", // The name of Lambda handler. Default: handler.lambda_handler
            "log_level": "DEBUG", // Set the Zappa log level. Default DEBUG, can be one of CRITICAL, ERROR, WARNING, INFO and DEBUG.
            "memory_size": 512, // Lambda function memory in MB
            "method_response_codes": [200, 301, 404, 500], // Method response status codes to route
            "parameter_depth": 10, // Size of URL depth to route. Defaults to 8.
            "prebuild_script": "your_module.your_function", // Function to execute before uploading code
            "profile_name": "your-profile-name", // AWS profile credentials to use. Default 'default'.
            "project_name": "MyProject", // The name of the project as it appears on AWS. Defaults to a slugified `pwd`.
            "remote_env_bucket": "my-project-config-files", // optional s3 bucket where remote_env_file can be located.
            "remote_env_file": "filename.json", // file in remote_env_bucket containing a flat json object which will be used to set custom environment variables.
            "role_name": "MyLambdaRole", // Lambda execution Role
            "s3_bucket": "dev-bucket", // Zappa zip bucket,
            "settings_file": "~/Projects/MyApp/settings/dev_settings.py", // Server side settings file location,
            "timeout_seconds": 30, // Maximum lifespan for the Lambda function (default 30)
            "touch": false, // GET the production URL upon initial deployment (default True)
            "use_precompiled_packages": false, // If possible, use C-extension packages which have been pre-compiled for AWS Lambda
            "use_apigateway": true, // Set to false if you don't want to create API Gateway resource. Default true
            "vpc_config": { // Optional VPC configuration for Lambda function
                "SubnetIds": [ "subnet-12345678" ], // Note: not all availability zones support Lambda!
                "SecurityGroupIds": [ "sg-12345678" ]
            }
        }
    }

Keeping The Server Warm
-----------------------

Zappa will automatically set up a regularly occuring execution of your
application in order to keep the Lambda function warm. This can be
disabled via the 'keep\_warm' setting.

Enabling CORS
-------------

To enable Cross-Origin Resource Sharing (CORS) for your application,
follow the `AWS "How to CORS"
Guide <https://docs.aws.amazon.com/apigateway/latest/developerguide/how-to-cors.html>`__
to enable CORS via the API Gateway Console. Don't forget to enable CORS
per parameter and re-deploy your API after making the changes!

Deploying to a Domain With a Let's Encrypt Certificate
------------------------------------------------------

If you want to use Zappa on a domain with a free Let's Encrypt
certificate, you can follow `this
guide <https://github.com/Miserlou/Zappa/blob/master/docs/domain_with_free_ssl.md>`__.

Setting Environment Variables
-----------------------------

If you want to use environment variables to configure your application
(which is especially useful for things like sensitive credentials), you
can create a file and place it in an S3 bucket to which your Zappa
application has access to. To do this, add the ``remote_env_bucket`` and
``remote_env_file`` keys to zappa\_settings pointing to a file
containing a flat JSON object, so that each key-value pair on the object
will be set as an environment variable and value whenever a new lambda
instance spins up.

For example, to ensure your application has access to the database
credentials without storing them in your version control, you can add a
file to S3 with the connection string and load it into the lambda
environment using the ``remote_env_bucket`` and ``remote_env_file``
configuration settings.

super-secret-config.json (uploaded to my-config-bucket):

.. code:: javascript

    {
        "DB_CONNECTION_STRING": "super-secret:database"
    }

zappa\_settings.json:

.. code:: javascript

    {
        "dev": {
            ...
            "remote_env_bucket": "my-config-bucket",
            "remote_env_file": "super-secret-config.json"
        },
        ...
    }

Now in your application you can use:

.. code:: python

    import os
    db_string = os.environ('DB_CONNECTION_STRING')

Zappa Guides
============

-  `Django-Zappa tutorial
   screencast <https://www.youtube.com/watch?v=plUrbPN0xc8&feature=youtu.be>`__.
-  `Using Django-Zappa, Part
   1 <https://serverlesscode.com/post/zappa-wsgi-for-python/>`__.
-  `Using Django-Zappa, Part 2:
   VPCs <https://serverlesscode.com/post/zappa-wsgi-for-python-pt-2/>`__.
-  `Building Serverless Microservices with Zappa and
   Flask <https://gun.io/blog/serverless-microservices-with-zappa-and-flask/>`__
-  *Your guide here?*

Zappa in the Press
==================

-  *`Zappa Serves Python, Minus the
   Servers <http://www.infoworld.com/article/3031665/application-development/zappa-serves-python-web-apps-minus-the-servers.html>`__*
-  *`Zappa lyfter serverlösa applikationer med
   Python <http://computersweden.idg.se/2.2683/1.649895/zappa-lyfter-python>`__*
-  *`Interview: Rich Jones on
   Zappa <https://serverlesscode.com/post/rich-jones-interview-django-zappa/>`__*

Sites Using Zappa
=================

-  `zappa.gun.io <https://zappa.gun.io>`__ - A Zappa "Hello, World"
   (real homepage coming.. soon..)
-  `spheres.gun.io <https://spheres.gun.io>`__ - Spheres, a photosphere
   host and viewer
-  `Mailchimp Signup
   Utility <https://github.com/sasha42/Mailchimp-utility>`__ - A
   microservice for adding people to a mailing list via API.
-  `Serverless Image
   Host <https://github.com/Miserlou/serverless-imagehost>`__ - A
   thumbnailing service with Flask, Zappa and Pillow.
-  Your site here?

Hacks
=====

Zappa goes quite far beyond what Lambda and API Gateway were ever
intended to handle. As a result, there are quite a few hacks in here
that allow it to work. Some of those include, but aren't limited to..

-  Using VTL to map body, headers, method, params and query strings into
   JSON, and then turning that into valid WSGI.
-  Attaching response codes to response bodies, Base64 encoding the
   whole thing, using that as a regex to route the response code,
   decoding the body in VTL, and mapping the response body to that.
-  Packing and *Base58* encoding multiple cookies into a single cookie
   because we can only map one kind.
-  Turning cookie-setting 301/302 responses into 200 responses with HTML
   redirects, because we have no way to set headers on redirects.

Contributing
============

This project is still young, so there is still plenty to be done.
Contributions are more than welcome! Please file tickets before
submitting patches, and submit your patches to the "dev" branch.

.. |Build Status| image:: https://travis-ci.org/Miserlou/Zappa.svg
   :target: https://travis-ci.org/Miserlou/Zappa
.. |Coverage| image:: https://img.shields.io/coveralls/Miserlou/Zappa.svg
   :target: https://coveralls.io/github/Miserlou/Zappa
.. |Requirements Status| image:: https://requires.io/github/Miserlou/Zappa/requirements.svg?branch=master
   :target: https://requires.io/github/Miserlou/Zappa/requirements/?branch=master
.. |PyPI| image:: https://img.shields.io/pypi/v/Zappa.svg
   :target: https://pypi.python.org/pypi/zappa
.. |Slack| image:: https://img.shields.io/badge/chat-slack-ff69b4.svg
   :target: https://slackautoinviter.herokuapp.com/


