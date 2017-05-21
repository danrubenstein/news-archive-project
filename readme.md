## The News Archive Project

The high-level goal of this project is to systematically collect news headlines and article descriptions from a variety of sources, with the objective of making this data available for analysis.

#### Fetching the News

At present, the source for this information is [News API](https://newsapi.org/). This source gives a wide range of sources, (this project currently limits them to the English language ones), from which we can gather information about the top articles. 

Possible analytic projects include checking topic persistence, finding whether or not news organizations are clustering around stories, or determining whether individual organizations cluster around certain topics. 

#### Next steps

A few things off the top of the head

- An improved configuration for storing data over the S3 bucket. Storing these records as persistent json files seems suboptimal.
- Investigation additional sources to be scraped. Places with Developer APIs that haven't already been built into News API are few and far between, I imagine, so creativity will be good.
- Building up enough days to start generating meaningful data (sit, wait!)

#### Access to the data

Forthcoming, pending legality and interest. 




