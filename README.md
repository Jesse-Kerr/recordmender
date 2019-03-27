# Recordmender

## What are you trying to do? Articulate your objectives using absolutely no jargon (i.e. as if you were explaining to a salesperson, executive, or recruiter).

I am trying to create a recommendation engine for music producers, mainly hip hop producers, that will recommend songs for them to sample (i.e., use parts of the song in their own beats), based off of the previous songs they've sampled. It may also take into account the beats they've produced, and their self-reported beat-making style.

### The steps of the project:

1. Scrape whosampled.com for, say, 1000 producers. We want a list of all the songs each producer has ever sampled (see below for more detail on database schema).

2. Separately, create a similarity matrix that tells how similar a given song is to another. This song dataset must include all of the songs in the whosampled dataset, and hopefully many more. (Details on how this will be done are below). 

3. Create recommendation engine, specific to each producer: Based on the songs you've sampled in the past, we recommend you try these songs for a new sample. This recommendation engine will include other factors, which will have to be scraped into a separate table (see details at bottom). 

4. Create interactive web app. Here, producers can upload the songs they've sampled in the past, and the algorithm will recommend new songs to look for samples in. Alternatively (experimentally) they can upload their beats, and the algorithm will find how similar they are to other producers based on their beats, and recommend them songs to sample based off of the list of songs other producers have sampled.

5. Deal with cold start problem. If a new producer has never sampled, what will we recommend?
     1. They can choose from a list of producers the one they are most similar to, and the algorithm will recommend based off of that producer.
     2. The algorithm can simply recommend 10 songs to sample, songs that are similar to others that have been sampled a lot, but have been sampled much less frequently. 

## How has this problem been solved before? If you feel like you are addressing a novel issue, what similar problems have been solved, and how are you borrowing from those?
    What is new about your approach, why do you think it will be successful?
    Who cares? If you're successful, what will the impact be?
    How will you present your work?

    Web app - where will you host it, what kind of information will you present?
    Visualization - what final visuals are you aiming to produce?
    Presentation - slides, interpretive dance?

    What are your data sources? What is the size of your dataset, and what is your storage format?
    What are potential problems with your capstone, and what have you done to mitigate these problems?
    What is the next thing you need to work on?

    Getting the data, not just some, likely all?
    Understanding the data?
    Building a minimum viable product?
    Gauging how much signal might be in the data?

### Structure of dataset from whosampled

The structure of the dataset from whosampled will be as such(for each sampled song for each new song for each producer): 
```
{
  New Song Producer: "string",    
  New Song Artist: "string",
  New Song Name: "string", 
  All Songs Sampled for this Song: "List"
  Sampled Song: "string",
  Sampled Artist: "string",
  Elements Sampled (Voice, Drums, Multiple Elements, etc. [available on whosampled.com]): "string",
  Time in Sampled Song where Sample Appears: "tmstmp" or "int",
  Overall Length of Song: "int",
  Name of Contributor: "string", 
  Presence/ Absence of "and throughout" in sample description: "Boolean"
}
```
![](whosampled_scrape.png)

### Reason for structure of whosampled dataset

1. Elements Sampled

This feature may make our recommendation engine much stronger/ more specific. It will allow the producer to specifically request an element (drums, voice, etc.) when asking the recordmender for a recommendation. 

2. Time in sample song where sample appears/ Overall Length of Songs: 
   
   1. General EDA: Plot where in songs samples are taken from, and see what type of distribution represents this. I'm guessing Poisson distribution, since most samples come from the beginning of songs, and the likelihood of a sample decreases as we move further through the song. We could plot this both as an absolute value, i.e., 99% of samples are within first 5 seconds, and as a fraction, i.e., 99% of samples come from the first tenth of the song. To determine the fraction, we need the entire length of the sample song. 
  
   2. We can see whether certain songs have sections that haven't been utilized. For example, a particular song may have been sampled 100 times, but what if it is only at the beginning, and there is much of it that appears unexplored?

3. Name of Contributor: 

May be useful for EDA purposes.

4. Presence/ Absence of "and throughout" in sample description:

This tells us how important the sample was to the song. If the sample only appears at one second, then it is less essential than one that appears throughout the entire song. 

## Details on Creating Song Similarity Matrix

Using unsupervised learning and dimensionality reduction techniques, do an item-item cosine similarity of a large song dataset. (This song dataset must include all of the songs sampled in the whosampled.com dataset).

How will this be done? Options include:

1. [Spotify API](https://developer.spotify.com/documentation/web-api/reference/tracks/get-audio-features/)

Through Spotify API, we can get audio features for any song, like so: `GET https://api.spotify.com/v1/audio-features/{id}`. Through this, we get features like key, energy, and tempo. This is a last resort, though, because I don't think these features will be helpful in finding new songs to sample. 

2.

## Sample Song Metadata Information Schema

```
{
  Record Label who owns the song (may tell us how much the song will cost to sample, i.e., royalties): "string",
  How many times song has been sampled (prefer more esoteric): "int",
  If you inputted a preferred sample element (voice, drums), is this song similar to other songs sampled for this element?: "float"
}
```

## References

* [klustr: Dim reduction on audio](https://medium.com/@hanoi7/klustr-a-tool-for-dimensionality-reduction-and-visualization-of-large-audio-datasets-c3e958c0856c)

Very useful article here. They tried to "find the optimal combination of feature extraction and dimensionality reduction techniques that produced a 2D map... Representations drarn from the high dimensional audio data...[are] typically in the form of STFT or MFCC features..."

* [](https://medium.com/@LeonFedden/comparative-audio-analysis-with-wavenet-mfccs-umap-t-sne-and-pca-cb8237bfce2f)




* [Million Song Dataset](https://labrosa.ee.columbia.edu/millionsong/)

Contains many features about each song, possibly useful, hopefully not. 

## Other Ideas


