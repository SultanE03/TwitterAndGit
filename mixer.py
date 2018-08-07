from flask import Flask,render_template,request
from flask import Flask, request, render_template, redirect, abort, flash, jsonify
import requests
import json
import os
import time
from twitter import *
app = Flask(__name__)

base_url = "https://api.github.com/users/"
CONSUMER_KEY = "TDERv6FbgSEqfq0tayf9vdun0"
CONSUMER_SECRET = "fw7buieTk9hwm25OvetaSIMXR3SBBlzDjVB4FWpJ7DvCLk5vOs"
ACCESS_KEY = "1019518139648958464-ncrsX7jH6P52UDrtkmPBc7Dop9ej1T"
ACCESS_SECRET = "6oO3UrPo0xfqHeVSNHHooGzb5u6SHdOvZ0rV9CaZHGSuh"

twitter = Twitter(
            auth=OAuth(ACCESS_KEY, ACCESS_SECRET, CONSUMER_KEY, CONSUMER_SECRET))

list1=[]

@app.route("/",methods = ["GET","POST"])
def index():
    if request.method == "POST":
        githubname = request.form.get("githubname")
        print(githubname)
        response_user = requests.get(base_url + githubname)
        response_repos = requests.get(base_url + githubname + "/repos")
        user_info = response_user.json()
        repos = response_repos.json()

        def count_user_commits(githubname):
            r = requests.get('https://api.github.com/users/%s/repos' % githubname)
            repos2 = json.loads(r.content)
            for repo in repos2:
                if repo['fork'] is True:
                    # skip it
                    continue
                n = count_repo_commits(repo['url'] + '/commits')
                repo['num_commits'] = n
                yield repo

        def count_repo_commits(commits_url, _acc=0):
            r = requests.get(commits_url)
            commits = json.loads(r.content)
            n = len(commits)
            if n == 0:
                return _acc
            link = r.headers.get('link')
            if link is None:
                return _acc + n
            next_url = find_next(r.headers['link'])
            if next_url is None:
                return _acc + n
            # try to be tail recursive, even when it doesn't matter in CPython
            return count_repo_commits(next_url, _acc + n)


        # given a link header from github, find the link for the next url which they use for pagination
        def find_next(link):
            for l in link.split(','):
                a, b = l.split(';')
                if b.strip() == 'rel="next"':
                    return a.strip()[1:-1]


        for repo in count_user_commits(githubname):
            total = repo['num_commits']
            list1.append(total)

        if "message" in user_info:
            return render_template("index1.html",error = "NOT found")
        else:
            print(list1)
            return render_template("index1.html",profile = user_info,repos = repos,total_spice = list1)
    else:
        return render_template("index1.html")


@app.route('/sula')
def main():


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
	query = request.args.get('q','Search')

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
