# Crunchy-API
A dedicated API and Website for Crunchy, Handling our RSS Feeds and Webhooks
In production this API handles over 140,000 Requests daily and serves over 60,000 Images.

## Made for performance
Using the insanely powerful Sanic micro framework and webserver, creating a fast and efficent async webserver/framework.

## Modules

### Sanic
You can find out about the awsome Async framework built for performance [here](https://sanic.readthedocs.io/en/latest/sanic/getting_started.html)

### Flisk
Modified version of Flisk to support AsyncIO endpoints yet keep the simplistic URL routing.

### rss
Simple async RSS parser which calls a callback on content change in a RSS field.

