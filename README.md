# Recordmend

Recordmend is a tool for music producers that recommends new songs for them to sample based off of their sampling history. 

## What is sampling?
![j dilla](images/j_dilla_searching.jpg)

Sampling is the process of reusing portions of older songs in new ones. Also called “crate-digging”, it can involve extensive searching to find a new sound. 

## Methodology

I created a producer-song utility matrix by scraping 200,000 links from whosampled.com into MongoDB using the Selenium Webdriver in Python. 

<img src="/images/whosampled_screenshot2.png"  width="320" height="320" align = "left">

I then decomposed the matrix with Singular Value Decomposition and optimized the two component matrices by Alternating Least Squares in Pandas and Numpy. Singular Value Decomposition is a method of decomposing a matrix into two component matrices, whose dimensions are determined by the number of latent factors in the data. 

![SVD visualized](images/svd.png)

The dot product of these matrices is an attempt to reconstitute the original utility matrix. Originally, these models were trained by stochastic gradient descent, in the form of the equation below:

<a href="https://www.codecogs.com/eqnedit.php?latex=\underset{x,y}min\underset{u,i}\sum&space;c_{ui}&space;(p_{ui}&space;-&space;x_u^Ty_i)^2&space;&plus;&space;\lambda&space;(\underset&space;u&space;\sum&space;\parallel&space;x_u&space;\parallel&space;^2&space;&plus;\underset&space;u&space;\sum&space;\parallel&space;y_i&space;\parallel&space;^2)" target="_blank"><img src="https://latex.codecogs.com/gif.latex?\underset{x,y}min\underset{u,i}\sum&space;c_{ui}&space;(p_{ui}&space;-&space;x_u^Ty_i)^2&space;&plus;&space;\lambda&space;(\underset&space;u&space;\sum&space;\parallel&space;x_u&space;\parallel&space;^2&space;&plus;\underset&space;u&space;\sum&space;\parallel&space;y_i&space;\parallel&space;^2)" title="\underset{x,y}min\underset{u,i}\sum c_{ui} (p_{ui} - x_u^Ty_i)^2 + \lambda (\underset u \sum \parallel x_u \parallel ^2 +\underset u \sum \parallel y_i \parallel ^2)" /></a>

##### Where:

* <a href="https://www.codecogs.com/eqnedit.php?latex=x_u" target="_blank"><img src="https://latex.codecogs.com/gif.latex?x_u" title="x_u" /></a> is the first matrix (termed the user vector).
* <a href="https://www.codecogs.com/eqnedit.php?latex=y_i" target="_blank"><img src="https://latex.codecogs.com/gif.latex?y_i" title="y_i" /></a> is the second matrix (termed the item vector).
* <a href="https://www.codecogs.com/eqnedit.php?latex=x_u^Ty_i" target="_blank"><img src="https://latex.codecogs.com/gif.latex?x_u^Ty_i" title="x_u^Ty_i" /></a> is their dot product.

* <a href="https://www.codecogs.com/eqnedit.php?latex=p_{ui}&space;=&space;1" target="_blank"><img src="https://latex.codecogs.com/gif.latex?p_{ui}&space;=&space;1" title="p_{ui} = 1" /></a> if producer sampled a song, 0 if producer did not sample a song.

* <a href="https://www.codecogs.com/eqnedit.php?latex=c_{ui}&space;=" target="_blank"><img src="https://latex.codecogs.com/gif.latex?c_{ui}&space;=" title="c_{ui} =" /></a> our confidence in the data; specifically, the number of times a producer sampled a song. This is calculated as <a href="https://www.codecogs.com/eqnedit.php?latex=c_{ui}&space;=1&space;&plus;&space;\alpha&space;*&space;r_{ui}" target="_blank"><img src="https://latex.codecogs.com/gif.latex?c_{ui}&space;=1&space;&plus;&space;\alpha&space;*&space;r_{ui}" title="c_{ui} =1 + \alpha * r_{ui}" /></a>, where
<a href="https://www.codecogs.com/eqnedit.php?latex=r_{ui}&space;=" target="_blank"><img src="https://latex.codecogs.com/gif.latex?r_{ui}&space;=" title="r_{ui} =" /></a># of interactions for a user-item pair, and <a href="https://www.codecogs.com/eqnedit.php?latex=\alpha" target="_blank"><img src="https://latex.codecogs.com/gif.latex?\alpha" title="\alpha" /></a> determines our confidence levels.

* <a href="https://www.codecogs.com/eqnedit.php?latex=\lambda" target="_blank"><img src="https://latex.codecogs.com/gif.latex?\lambda" title="\lambda" /></a> is the regularization term.

Like other gradient descent algorithms, this model begins with taking the squared error of our prediction <a href="https://www.codecogs.com/eqnedit.php?latex=(p_{ui}&space;-&space;x_u^Ty_i)^2" target="_blank"><img src="https://latex.codecogs.com/gif.latex?(p_{ui}&space;-&space;x_u^Ty_i)^2" title="(p_{ui} - x_u^Ty_i)^2" /></a>. It then multiplies our error by our confidence in this prediction, <a href="https://www.codecogs.com/eqnedit.php?latex=c_{ui}" target="_blank"><img src="https://latex.codecogs.com/gif.latex?c_{ui}" title="c_{ui}" /></a>, thus increasing the cost of errors on high confidence user-item interactions. Across all users <a href="https://www.codecogs.com/eqnedit.php?latex=x" target="_blank"><img src="https://latex.codecogs.com/gif.latex?x" title="x" /></a> and items <a href="https://www.codecogs.com/eqnedit.php?latex=y" target="_blank"><img src="https://latex.codecogs.com/gif.latex?y" title="y" /></a>, we minimize this cost.

In practice, however, implementing stochastic gradient descent is impractical for recommenders, because there are usually billions of user-item interactions to compute over, which is extremely computationally expensive.

## ALS

Therefore we modify the cost function to Alternating Least Squares, which works by holding either user vectors or item vectors constant and calculating the global minimum, then alternating to the other vector.

### Compute User factors
<a href="https://www.codecogs.com/eqnedit.php?latex=x_u&space;=&space;(Y^T&space;C^u&space;Y&space;&plus;&space;\lambda&space;I)^{-1}&space;Y^T&space;C^u&space;p(u)" target="_blank"><img src="https://latex.codecogs.com/gif.latex?x_u&space;=&space;(Y^T&space;C^u&space;Y&space;&plus;&space;\lambda&space;I)^{-1}&space;Y^T&space;C^u&space;p(u)" title="x_u = (Y^T C^u Y + \lambda I)^{-1} Y^T C^u p(u)" /></a>

##### Where:

<a href="https://www.codecogs.com/eqnedit.php?latex=Y" target="_blank"><img src="https://latex.codecogs.com/gif.latex?Y" title="Y" /></a> is <a href="https://www.codecogs.com/eqnedit.php?latex=n&space;*&space;f" target="_blank"><img src="https://latex.codecogs.com/gif.latex?n&space;*&space;f" title="n * f" /></a> matrix of item-factors. 

<a href="https://www.codecogs.com/eqnedit.php?latex=C^u" target="_blank"><img src="https://latex.codecogs.com/gif.latex?C^u" title="C^u" /></a> is a <a href="https://www.codecogs.com/eqnedit.php?latex=n*n" target="_blank"><img src="https://latex.codecogs.com/gif.latex?n*n" title="n*n" /></a> diagonal matrix for user <a href="https://www.codecogs.com/eqnedit.php?latex=u" target="_blank"><img src="https://latex.codecogs.com/gif.latex?u" title="u" /></a> where <a href="https://www.codecogs.com/eqnedit.php?latex=C^u_{ii}&space;=&space;c_{ui}" target="_blank"><img src="https://latex.codecogs.com/gif.latex?C^u_{ii}&space;=&space;c_{ui}" title="C^u_{ii} = c_{ui}" /></a>. Each <a href="https://www.codecogs.com/eqnedit.php?latex=C^u" target="_blank"><img src="https://latex.codecogs.com/gif.latex?C^u" title="C^u" /></a> is our confidence matrix for <a href="https://www.codecogs.com/eqnedit.php?latex=n" target="_blank"><img src="https://latex.codecogs.com/gif.latex?n" title="n" /></a> items for <a href="https://www.codecogs.com/eqnedit.php?latex=u" target="_blank"><img src="https://latex.codecogs.com/gif.latex?u" title="u" /></a> user.

<a href="https://www.codecogs.com/eqnedit.php?latex=p(u)" target="_blank"><img src="https://latex.codecogs.com/gif.latex?p(u)" title="p(u)" /></a> is vector of preferences for user <a href="https://www.codecogs.com/eqnedit.php?latex=u" target="_blank"><img src="https://latex.codecogs.com/gif.latex?u" title="u" /></a>.

### Recompute Item factors

<a href="https://www.codecogs.com/eqnedit.php?latex=y_i&space;=&space;(X^TC^iX&space;&plus;&space;\lambda&space;I)^-1&space;X^TC^ip(i)" target="_blank"><img src="https://latex.codecogs.com/gif.latex?y_i&space;=&space;(X^TC^iX&space;&plus;&space;\lambda&space;I)^-1&space;X^TC^ip(i)" title="y_i = (X^TC^iX + \lambda I)^-1 X^TC^ip(i)" /></a>

##### Where:
<a href="https://www.codecogs.com/eqnedit.php?latex=X&space;=&space;m&space;*&space;f" target="_blank"><img src="https://latex.codecogs.com/gif.latex?X&space;=&space;m&space;*&space;f" title="X = m * f" /></a> matrix  of user_factors. 

<a href="https://www.codecogs.com/eqnedit.php?latex=C^i&space;=&space;m&space;*&space;m" target="_blank"><img src="https://latex.codecogs.com/gif.latex?C^i&space;=&space;m&space;*&space;m" title="C^i = m * m" /></a> diagonal matrix for each item <a href="https://www.codecogs.com/eqnedit.php?latex=i" target="_blank"><img src="https://latex.codecogs.com/gif.latex?i" title="i" /></a> where <a href="https://www.codecogs.com/eqnedit.php?latex=C_{uu}^i&space;=&space;c_{ui}" target="_blank"><img src="https://latex.codecogs.com/gif.latex?C_{uu}^i&space;=&space;c_{ui}" title="C_{uu}^i = c_{ui}" /></a>

<a href="https://www.codecogs.com/eqnedit.php?latex=p(i)" target="_blank"><img src="https://latex.codecogs.com/gif.latex?p(i)" title="p(i)" /></a> is vector of preferences for item <a href="https://www.codecogs.com/eqnedit.php?latex=i" target="_blank"><img src="https://latex.codecogs.com/gif.latex?i" title="i" /></a>.

## Ranking the model

The model was ranked using a ranking algorithm adopted from [Hu 2008](https://ieeexplore.ieee.org/document/4781121). 


<a href="https://www.codecogs.com/eqnedit.php?latex=\overline{rank}&space;=&space;\frac{\sum_{u,i}&space;r^t_{ui}&space;*&space;rank_{ui}}{\sum_{u,i}&space;r^t_{ui}}" target="_blank"><img src="https://latex.codecogs.com/gif.latex?\overline{rank}&space;=&space;\frac{\sum_{u,i}&space;r^t_{ui}&space;*&space;rank_{ui}}{\sum_{u,i}&space;r^t_{ui}}" title="\overline{rank} = \frac{\sum_{u,i} r^t_{ui} * rank_{ui}}{\sum_{u,i} r^t_{ui}}" /></a>

##### where:

<a href="https://www.codecogs.com/eqnedit.php?latex=r^t_{ui}" target="_blank"><img src="https://latex.codecogs.com/gif.latex?r^t_{ui}" title="r^t_{ui}" /></a> is the # of interactions for observations in the test set.

<a href="https://www.codecogs.com/eqnedit.php?latex=rank_{ui}" target="_blank"><img src="https://latex.codecogs.com/gif.latex?rank_{ui}" title="rank_{ui}" /></a> are the percentile ranking of each item for each user.

How does this algorithm work? We can see that <a href="https://www.codecogs.com/eqnedit.php?latex=\sum_{u,i}&space;r^t_{ui}" target="_blank"><img src="https://latex.codecogs.com/gif.latex?\sum_{u,i}&space;r^t_{ui}" title="\sum_{u,i} r^t_{ui}" /></a>is in both the numerator and the denominator. If <a href="https://www.codecogs.com/eqnedit.php?latex=rank_{ui}" target="_blank"><img src="https://latex.codecogs.com/gif.latex?rank_{ui}" title="rank_{ui}" /></a> was not in the numerator, <a href="https://www.codecogs.com/eqnedit.php?latex=\overline{rank}" target="_blank"><img src="https://latex.codecogs.com/gif.latex?\overline{rank}" title="\overline{rank}" /></a> would simply equal 1. <a href="https://www.codecogs.com/eqnedit.php?latex=rank_{ui}" target="_blank"><img src="https://latex.codecogs.com/gif.latex?rank_{ui}" title="rank_{ui}" /></a> is the percentile ranking of each item for each user, such that the item most highly recommended has a <a href="https://www.codecogs.com/eqnedit.php?latex=rank_{ui}" target="_blank"><img src="https://latex.codecogs.com/gif.latex?rank_{ui}" title="rank_{ui}" /></a> of 0.00\% and the item least recommended has a <a href="https://www.codecogs.com/eqnedit.php?latex=rank_{ui}" target="_blank"><img src="https://latex.codecogs.com/gif.latex?rank_{ui}" title="rank_{ui}" /></a> of 100.00\%. Therefore, if the algorithm is correct, the low percentages will cancel out the higher <a href="https://www.codecogs.com/eqnedit.php?latex=r^t_{ui}" target="_blank"><img src="https://latex.codecogs.com/gif.latex?r^t_{ui}" title="r^t_{ui}" /></a>, making the <a href="https://www.codecogs.com/eqnedit.php?latex=\overline{rank}" target="_blank"><img src="https://latex.codecogs.com/gif.latex?\overline{rank}" title="\overline{rank}" /></a> go towards 0. Thus, the item most highly recommended has a <a href="https://www.codecogs.com/eqnedit.php?latex=rank_{ui}" target="_blank"><img src="https://latex.codecogs.com/gif.latex?rank_{ui}" title="rank_{ui}" /></a> of 0.00\% and the item least recommended has a <a href="https://www.codecogs.com/eqnedit.php?latex=rank_{ui}" target="_blank"><img src="https://latex.codecogs.com/gif.latex?rank_{ui}" title="rank_{ui}" /></a> of 100.00\%.

## Perform Test/Train Split

We can't do a traditional 70/30 split for recommendation systems, because the algorithm requires the entire
dataframe to train on. Instead, we create a test set by taking some percentage of the actual interactions, and 
replacing them with zeros- in other words, acting as if the producer has not sampled those artists.

We train the model on this `train` dataset with these specific values hidden. 

![Creating train and test set](images/train_test.png)


## Rank Score got better when producers with few sampled songs (training examples) were excluded.

![](images/rank_score_over_training_examples.png)


## Grid Searching the model

I found that 20 factors, a lambda of 30, and 50 iterations gave the best rank score. 

## Conclusion and Future steps
My model scores much better than random and is similar to popularity. However, it is not effective for producers with few sampled artists. A multi-level ensemble recommender with content filtering may help to address these problems. 

1. https://www.scientificamerican.com/article/the-tyranny-of-choice/

2. https://www.pbs.org/newshour/economy/is-the-famous-paradox-of-choic

3. https://www.sciencedirect.com/science/article/abs/pii/S1057740814000916
