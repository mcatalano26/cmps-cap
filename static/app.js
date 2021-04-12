

const commentButton = document.getElementById('userCommentButton');
const mainDiv = document.getElementById('main');
const scoreHolder = document.createElement("P");
const inProgress = document.createElement('P');
mainDiv.appendChild(inProgress);
mainDiv.appendChild(scoreHolder);



var commentScore;

commentButton.addEventListener("click", function() {
    inProgress.innerHTML = "Model is thinking..."
    let comment = document.getElementById('userComment').value;
    console.log(comment);
    $.post('/scoreComment', 
    {comment : comment,
    reddit_url : reddit_link,
    cleaned_article_text : cleaned_article_text,
    no_url_article_text : no_url_article_text,
    no_stop_article_text : no_stop_article_text,
    no_stop_or_url_article_text : no_stop_or_url_article_text},
    function (data) {
        commentScore = data.score;
        scoreHolder.innerHTML = commentScore;
        inProgress.innerHTML = '';
        
    });

});


