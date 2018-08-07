import os
import time
from twitter import *
from flask import Flask, request, render_template, redirect, abort, flash, jsonify

app = Flask(__name__)   # create our flask app

# configure Twitter API
CONSUMER_KEY = "TDERv6FbgSEqfq0tayf9vdun0"
CONSUMER_SECRET = "fw7buieTk9hwm25OvetaSIMXR3SBBlzDjVB4FWpJ7DvCLk5vOs"
ACCESS_KEY = "1019518139648958464-ncrsX7jH6P52UDrtkmPBc7Dop9ej1T"
ACCESS_SECRET = "6oO3UrPo0xfqHeVSNHHooGzb5u6SHdOvZ0rV9CaZHGSuh"

twitter = Twitter(
            auth=OAuth(ACCESS_KEY, ACCESS_SECRET, CONSUMER_KEY, CONSUMER_SECRET))

@app.route('/')
def main():

	# fetch 3 tweets from my account
	myTweets = twitter.statuses.user_timeline(count=10)

	# fetch 3 tweets from ITP_NYU
	itpTweets = twitter.statuses.user_timeline(screen_name='itp_nyu', count=10)

	# app.logger.debug(itpTweets)

	templateData = {
		'title' : 'My last three tweets',
		'myTweets' : myTweets,
		'itpTweets' : itpTweets
	}

	return render_template('index.html', **templateData)


@app.route('/search')
def search():

	# get search term from querystring 'q'
	query = request.args.get('q','#redburns')

	# search with query term and return 10
	results = twitter.search.tweets(q=query, count=10)

	# return jsonify(results)
	# app.logger.debug(results)

	templateData = {
		'query' : query,
		'tweets' : results.get('statuses')
	}

	return render_template('search.html', **templateData)


@app.route('/post', methods=['GET','POST'])
def post_to_twitter():

	if request.method == 'POST':
		result = twitter.statuses.update(status=request.form.get('status'))

		app.logger.debug(result)

		# redirect to new twitter status post
		return redirect('http://www.twitter.com/%s/status/%s' % (result['user']['screen_name'], result.get('id')))

	else:
		return render_template('post_to_twitter.html')


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


# This is a jinja custom filter
@app.template_filter('strftime')
def _jinja2_filter_datetime(date, fmt=None):
    pyDate = time.strptime(date,'%a %b %d %H:%M:%S +0000 %Y') # convert twitter date string into python date/time
    return time.strftime('%Y-%m-%d %H:%M:%S', pyDate) # return the formatted date.

# --------- Server On ----------
# start the webserver
if __name__ == "__main__":
    app.run(debug = True)
