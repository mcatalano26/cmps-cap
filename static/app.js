

const commentButton = document.getElementById('userCommentButton');
const mainDiv = document.getElementById('main');


var commentScore;

commentButton.addEventListener("click", function() {
    let comment = document.getElementById('userComment').value;
    console.log(comment);
    $.post('/scoreComment', 
    {comment : comment,
    reddit_url : reddit_link},
    function (data) {
        commentScore = data.score;
        console.log(data, commentScore);
        const scoreHolder = document.createElement("P");
        scoreHolder.innerHTML = commentScore;
        mainDiv.appendChild(scoreHolder);
        
    });

});


