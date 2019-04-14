<style TYPE="text/css">
code.has-jax {font: inherit; font-size: 100%; background: inherit; border: inherit;}
</style>
<script type="text/x-mathjax-config">
MathJax.Hub.Config({
    tex2jax: {
        inlineMath: [['$','$'], ['\\(','\\)']],
        skipTags: ['script', 'noscript', 'style', 'textarea', 'pre'] // removed 'code' entry
    }
});
MathJax.Hub.Queue(function() {
    var all = MathJax.Hub.getAllJax(), i;
    for(i = 0; i < all.length; i += 1) {
        all[i].SourceElement().parentNode.className += ' has-jax';
    }
});
</script>
<script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.4/MathJax.js?config=TeX-AMS_HTML-full"></script>

# Recordmend

Recordmend is a tool for hip hop producers that recommends new songs for them to sample based off of their sampling history. 



## Rationale

Digging in the crates. Sampling. Flipping. Finding a gem in an old song to repurpose in a new one can be quite the thrill. It's like uncovering unburied treasure or an unknown gem.

Underlying discovery, however, is a whole lot of searching, meaning listening to song after song, trying to find the buried treasure. 

![https://www.stonesthrow.com/madlib/](images/madlib_records.jpg)

[Madlib](https://en.wikipedia.org/wiki/Madlib)

While the search is certainly one of the best parts of finding treasure, most searchers at least bring a map. This is where recordmender comes in.

## Methodology

A utility matrix $R$ was constructed, with `producers vector` $p$ rows and sampled artist vector $a$ columns. $R_{p,a}$ represents the number of times a given producer $p$ sampled an artist $a$, ranging from 0 to 131.

I used data from whosampled.com to construct the matrix.

Singular Value Decomposition is a latent factor model which causes dimensionality reduction. Two matrices are created, a user-factor matrix and an item-factor matrix, where the factor represents the number of latent factors in the data. The dot product of these matrices is an attempt to reconstitute the original utility matrix. Originally, these models were trained by stochastic gradient descent, in the form of the equation below:


$\underset{x,y}min\underset{u,i}\sum 
c_{ui} (p_{ui} - x_u^Ty_i)^2 + \lambda
(\underset u \sum \parallel x_u \parallel ^2
+\underset u \sum \parallel y_i \parallel ^2)$

##### Where:

* $x_u$ is user vector
* $y_i$ is item vector
* $x_u^Ty_i$ is their dot product.

* $p_{ui} = 1$ if interaction, 0 if no interaction.

* $c_{ui} =$ our confidence in the data; in our case, the number of times a producer sampled a artist. This is calculated as $c_{ui} =1 + \alpha * r_{ui}$, where
$r_{ui}$ = # of interactions for a user-item pair, and $\alpha$ determines our confidence levels.

* $\lambda$ is regularization term.

Like other gradient descent algorithms, this model begins with taking the squared error of our prediction $(p_{ui} - x_u^Ty_i)^2$. It then multiplies our error by our confidence in this prediction, $c_{ui}$, thus increasing the cost of errors on high confidence user-item interactions. Across all or a subset of users x and items y, we minimize this cost.

In practice, however, stochastic gradient descent is impossible in implicit feedback. There are often billions of user-item interactions to compute over.

## ALS

Therefore we modify the cost function to Alternating Least Squares, which works by holding either user vectors or item vectors constant and calculating the global minimum, then alternating to the other vector.

### Compute User factors
$x_u = (Y^T C^u Y + \lambda I)^{-1}  Y^T C^u p(u)$

##### Where:

$Y$ is $n * f$ matrix of item-factors. 

$C^u$ is a $n*n$ diagonal matrix for user $u$ where $C^u_{ii} = c_{ui}$. Each $C^u$ is our confidence matrix for $n$ items for $u$ user.

$p(u)$ is vector of preferences for user $u$.

### Recompute Item factors

$y_i = (X^TC^iX + \lambda I)^-1 X^TC^ip(i)$

##### Where:
$X$ = $m * f$ matrix  of user_factors. 

$C^i$ is $m * m$ diagonal matrix for each item $i$ where $C_{uu}^i = c_{ui}$

$p(i)$ is vector of preferences for item $i$.

## Data Collection

A Selenium class was created to scrape the data from whosampled.com

## EDA

![x](images/Distribution_of_Song_Sample_Years.jpg)

![x](images/Distribution_of_Sample_Types.png)

## Making model better

We found that lower # of factors lead to a better rank score. 12 worked the best.

Different regularization values of lambda were tried from 0.01 to 1000.

Different numbers of iterations from 10 to 210, in steps of 40. 

With these best values, different numbers of artists sampled and producers were tried.

Specific elements sampled were also examined.
#Specific to do's for Thursday/ Friday
1. Look at none listed for new song producer. Consider replacing with new_song_artist

3. Examine features of model. Clustering of items. Recommendations. 

4. Try with prod_song dataset.

Recommend a year to sample? An album?

Combine year + artist + album, or etc. 

Try other algorithms- random forest....

Make a playlist of the 6game on whosampled- it takes a random progression through music.

#Presentation

Discuss why factors is lower, why lambda is lower.