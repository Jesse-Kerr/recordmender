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

Digging in the crates. Sampling. Flipping. These are the terms for repurposing an old song as part of a new one, but none truly describe its thrill. It's the feeling of uncovering an unknown gem, 

Underlying discovery, howver, is a whole lot of searching, meaning listening to song after song, trying to find the buried treasure. 

[Madlib](https://en.wikipedia.org/wiki/Madlib)

![https://www.stonesthrow.com/madlib/](images/madlib_records.jpg)

While the search is certainly one of the best parts of finding treasure, most searchers at least bring a map. This is where recordmender comes in.

## Methodology

A utility matrix $R$ was constructed, with `producers vector` $p$ as rows and the sampled artist vector $a$ as columns. $R_{p,a}$ represents the number of times a given producer $p$ sampled an artist $a$. 
$\underset{x,y}min\underset{u,i}\sum 
c_{ui} (p_{ui} - x_u^Ty_i)^2 + \lambda
(\underset u \sum \parallel x_u \parallel ^2
+\underset u \sum \parallel y_i \parallel ^2)$