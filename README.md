# Recordmend

## What are you trying to do? Articulate your objectives using absolutely no jargon (i.e. as if you were explaining to a salesperson, executive, or recruiter).

I am trying to create a recommendation engine for music producers, mainly hip hop producers, that will recommend songs for them to sample (i.e., use parts of the song in their own beats), based off of the previous songs they've sampled. It will recommend songs that are similar to what they have already sampled but that have been sampled much less frequently in total. It may also take into account the beats they've produced, their self-reported beat-making style, and other factors about the sample songs to make recommendations.

### Steps to a MVP:

1. WhoSampled Scrape:
  1. Scrape names of 600 American producers from Wikipedia. - [x]
    1. Later: Insert that into mongoDB - [ ]
  2. For each producer:
    1. Insert meta data (num_samples) - [ ]
    2. Insert links to the pages for each song they produced. - [ ]
    3. For each song page:
      1. Insert links to the song-sample pages (usually multiple) into
         song_sample_pages.db. Format of this collection should be 'link' :
         link. Don't list producer name in it because there may be duplication
         (when two producers are on same track). - [ ]
  3. Get just the distinct links from song_sample_pages_db. - [ ]
  4. For each link in song_sample_pages_db:
    1. Get list of producers credited on the page.
    2. For each producer credited on page:
      1. Insert data into db.main for producer listed. - [ ]
  2. Later: Repeat with more producers - [ ]

2. Get db.main into a sparse matrix format.

### Potential Problems
1. Multiple producers for one track:
   At step 1.3.1, what if multiple producers listed? I think best is to get the
   producers as a list, and insert the sample data for each producer.
   Because some of the producers may not be on my Wikipedia list, and this may
   be my only chance to get data on them. 

### The steps of the project:

1. Scrape whosampled.com for, say, 1000 producers. We want a list of all the songs each producer has ever sampled (see **Whosampled Dataset** section below for more detail on this database schema).

2. Separately, create a similarity matrix that tells how similar any given song is to another. This song dataset must include all of the songs in the whosampled dataset, and hopefully many more. (See **How has this problem been solved before?** below for details on how this will be done.) 

3. Create recommendation engine, specific to each producer: Based on the songs you've sampled in the past, we recommend you try these songs, which have not been sampled much, for a new sample. 

OPTIONAL (IF TIME ALLOWS- In order of importance):

4. Test the recommender: Take the first 75% of songs a producer has sampled (as training data) and see if the recommender recommends anything they sample after. 

5. Create interactive web app. Here, producers can upload the songs they've sampled in the past, and the algorithm will recommend new songs to look for samples in.

6. Allow users to input preferences into the web app (I want my sample to be more/ less esoteric (country of origin of sample song, time period, perhaps), I need this specific element for my song, etc.)

7. Create a database with other features about the sample songs that can be used in the recommendation engine. (See **Sample Song Metadata Schema** for more details.) 

8. Deal with cold start problem. If a new producer has never sampled, what will we recommend?
     1. They can manually choose from a list of producers the one they are most similar to, and the algorithm will recommend based off of that producer.
     2. The algorithm can simply recommend 10 songs to sample. It will use the most sampled songs, and recommend songs that are similar to those but have been sampled much less frequently. 

9. Alternatively, we could recommend songs for them to sample just by using the beats these producers have created. To do this, we would need to figure out which famous producer they are most similar to based on their beats. Then, we would recommend them songs to sample based off of that producer. To do this, however, we would need to create another similarity matrix of beats for producers. 

## How has this problem been solved before? If you feel like you are addressing a novel issue, what similar problems have been solved, and how are you borrowing from those?

The hardest part of this project will be creating the song-song similarity matrix. However, this seems to be an area with some amount of research and tools already produced. The first three links in **References** seem very helpful. The first two are on the `klustr` project, which reduces dimensionality of audio datasets. The third link discusses the merits of different features and different dimensionality reduction techniques.  

In essence, I will use unsupervised learning and dimensionality reduction techniques to do an item-item cosine similarity of a large song dataset, which must include all of the songs in the whosampled.com dataset.

## What is new about your approach, why do you think it will be successful?
    
I don't know of any song sample recommender systems out there. I think this will be a useful tool. I also think people will be excited to upload their past samples to the recommender, because the more they upload, the better the recommendations get (like collaborative filtering). The more beats you put in, the better we compare you to other producers and further suggest what you should sample. So producers have incentive to give their data. The web app also lends itself to a "freemium" payment scheme: We'll recommend 10 songs for you to listen to for samples a week for free- after that, you got to pay up. 

## Who cares? If you're successful, what will the impact be?

I used to make hip hop beats in high school. I started when my parents got their computer fixed, and our computer guy decided to put a near terabyte of music on our new computer (he was way overcharging us for the computer, and maybe wanted to distract us). Suddenly I had huge amounts of songs to search through and listen to, and I found that every once in a while, I would make a discovery: There was a perfect sample hidden in one of the songs. I loved those moments.

However, finding those gems could take hours of patient listening. This strategy remains the only way to find new samples, and it means that finding new samples requires a lot of leg work. This leads many producers to only sample the classics (James Brown, for example) and to leave the huge mass of work that is music unsearched.

Recordmender would help producers to narrow their search down to more promising songs. They would still have to do the leg work of listening through these songs, but the time of their search could be cut down a great deal. Getting producers to sample from new songs could have the effect of increasing diversity in modern music, introducing younger listeners to more wide selections of songs, and increasing cross-pollination across genres and generations.

## How will you present your work?

It will be a web app, an interactive one. I guess I could host on AWS.

The song-song similarity matrix should lend itself to nice visualizations. I would like to get the actual genres of the songs, and color code the songs based off of that, to see how well the dimensionality reduction/class-finding algorithm actually distinguishes between these genres.

I'd also like to have graphs of distributions: How many times a song is usually sampled? How skewed is that distribution? What year has the most samples taken from it? What artist was sampled most? What album?

Presentation: Probably slides, then go into the web app, if it's made. 

## What are your data sources? What is the size of your dataset, and what is your storage format?

### Whosampled Dataset 

The structure of the MongoDB from whosampled will be as such(for each sampled song for each new song for each producer): 
```
{
  New Song Producer: "string",    
  New Song Artist: "string",
  New Song Name: "string", 
  New Song Year: "int", (more information here is better! We need tmstmp data)
  All Songs Sampled for this Song: "List"
  Sampled Song: "string",
  Sampled Song Year: "int",
  Sampled Artist: "string",
  Sampled Album: "string",
  Elements Sampled (Voice, Drums, Multiple Elements, etc. [available on whosampled.com]): "string",
  Time in Sampled Song where Sample Appears: "tmstmp" or "int",
  Overall Length of Song: "int",
  Name of Contributor: "string", 
  Presence/ Absence of "and throughout" in sample description: "Boolean"
}
```
![](whosampled_scrape.png)

### Reason for elements of whosampled dataset

1. Elements Sampled

This feature may make our recommendation engine much stronger/ more specific. It will allow the producer to specifically request an element (drums, voice, etc.) when asking the recordmender for a recommendation. 

2. Time in sample song where sample appears/ Overall Length of Songs: 
   
   1. General EDA: Plot where in songs samples are taken from, and see what type of distribution represents this. I'm guessing Poisson distribution, since most samples come from the beginning of songs, and the likelihood of a sample decreases as we move further through the song. We could plot this both as an absolute value, i.e., 99% of samples are within first 5 seconds, and as a fraction, i.e., 99% of samples come from the first tenth of the song. To determine the fraction, we need the entire length of the sample song. 
  
   2. We can see whether certain songs have sections that haven't been utilized. For example, a particular song may have been sampled 100 times, but what if it is only at the beginning, and there is much of it that appears unexplored?

3. Name of Contributor: 

May be useful for EDA purposes.

4. Presence/ Absence of "and throughout" in sample description:

This tells us how important the sample was to the song. If the sample only appears at one second, then it is less essential than one that appears throughout the entire song. Will store data in MongoDB

### Sample Song Metadata Schema

```
{
  Record Label who owns the song (may tell us how much the song will cost to sample, i.e., royalties): "string",
  How many times song has been sampled (prefer more esoteric): "int",
  If you inputted a preferred sample element (voice, drums), is this song similar to other songs sampled for this element?: "float"
}
```

## What are potential problems with your capstone, and what have you done to mitigate these problems?

## What is the next thing you need to work on?

Scraping Whosampled and figuring out the song-song similarity matrix.

Will probably need to scrape a bunch of songs from Youtube or something, shit. Programatically do the youtubetomp3 thing?

To figure out the song-song similarity, work through the klustr jupyter notebook.

Creating the recommender. 

## References

1. [klustr: Dim reduction on audio](https://medium.com/@hanoi7/klustr-a-tool-for-dimensionality-reduction-and-visualization-of-large-audio-datasets-c3e958c0856c)

Very useful article here. They tried to "find the optimal combination of feature extraction and dimensionality reduction techniques that produced a 2D map... Representations drarn from the high dimensional audio data...[are] typically in the form of STFT or MFCC features..."

2.[Github Link to klustr project](https://github.com/lamtharnhantrakul/klustr)


3. [Comparative audio analysis](https://medium.com/@LeonFedden/comparative-audio-analysis-with-wavenet-mfccs-umap-t-sne-and-pca-cb8237bfce2f)
Leon walks through different algorithms on audio datasets very helpful.


4. [Music dim reduction](https://ieeexplore.ieee.org/document/6607550)
Seems like good useful paper.

5. [Million Song Dataset](https://labrosa.ee.columbia.edu/millionsong/)

Contains many features about each song, possibly useful, hopefully not. 

6. [Spotify API](https://developer.spotify.com/documentation/web-api/reference/tracks/get-audio-features/)

Through Spotify API, we can get audio features for any song, like so: `GET https://api.spotify.com/v1/audio-features/{id}`. Through this, we get features like key, energy, and tempo. This is a last resort, though, because I don't think these features will be helpful in finding new songs to sample. 

7. [Song similarity matrix using features from songs](http://cs229.stanford.edu/proj2017/final-reports/5218770.pdf)

8. [sample spotify work](https://medium.com/@chris.m.pease/automating-finding-music-samples-on-spotify-with-whosampled-54f86bcda1ee)

## Other Crazy Ideas

* The next-level shit would be getting into multiple song samples. They sampled these two together, what does that mean?

* Depending on how I get the song similarity data, even predict where in the song to sample.

* Use lyrics from the tracks made by users to help us learn about the user, thus making the comparison to other producers better, thus making the sample recommender better. 

* Make something that goes into producer's computer and sees what songs they've sampled, so they don't have to list them themselves. 





