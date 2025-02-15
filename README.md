# analyst_copilot

# repo created on 10/31. Files to be added will include:

- Python files to handle fine-tuning steps
- Models that we deem to be "best-fitting"


# Getting setup with RSS feeds
see the `analyst_copilot/RSS` directory:

## Create a virtual environment
Run 
1. `python -m venv rss`  
2. `source rss/bin/activate`

## Install the required packages
1. `pip install -r requirements.txt`

## If you add any new packages to the environment needed for the code to run:
1. `pip freeze > requirements.txt`

## To exit the virtual environment
`deactivate`

## To create a kernel from which to run the notebook in vscode or cursor
`python -m ipykernel install --user --name=rss-kernel`


## Options we have for choosing what feed parsing software we're going to use
~~1. Five filters 
We have a few options with this one:
a. 9 bucks a month for the standard plan (this may not meet our needs, we'll see)
b. Developer: used based pricing, which hopefully wouldn't be too expensive to start out
c. Buy the source for 150 bucks and host it ourselves

2. tt-rss
Free to use, open source (GPL3'ed)
Need to self host~~

3. Just pay for PR newswire RSS feeds (they will provide an API)
Not sure how expensive this is, there's not an 
This is likely the best solution


