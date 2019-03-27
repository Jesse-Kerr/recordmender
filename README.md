# recordmender


What are you trying to do? Articulate your objectives using absolutely no jargon (i.e. as if you were explaining to a salesperson, executive, or recruiter).

I am trying to create a recommendation engine for music producers, mostly hip hop producers, that will recommend songs for them to sample (i.e., use parts of the song in their own beats). 

Here are the steps of the project:

1. Scrape whosampled.com for, say, 1000 producers. The structure of the dataset from whosampled will be as such: 

    {
      Producer: "string",
      
      Artist: "string",
      
      Song Name: "string", 
  
  Sample Song: "string"
  
  Sample Artist: "string",
  
  Elements sampled (Voice, Drums, Multiple Elements, etc. This data is provided by whosampled.com): "string",
  
  Time in sample song where sample appears: "tmstmp" or "int",
  
  Overall Length of Song: "int"

}

The time in sample song where sample appears is important for two reasons: 1) General EDA: We can plot where in songs most samples are taken from. We could plot this both as an absolute value, i.e., 99% of samples are within first 5 seconds, and as a fraction, i.e., 99% of samples come from the first tenth of the song and 2) We can see if parts of songs are not being utilized. For example, a particular song may have been sampled 100 times, but what if it is only at the beginning, and there is much of it that appears unexplored?

How has this problem been solved before? If you feel like you are addressing a novel issue, what similar problems have been solved, and how are you borrowing from those?
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
