const connect_to_db = require('./db');

// GET BY TALK HANDLER

const talk = require('./talk');

module.exports.suggest = (event, context, callback) => {
    context.callbackWaitsForEmptyEventLoop = false;
    console.log('Received event:', JSON.stringify(event, null, 2));
    let body = {}
    if (event.body) {
        body = JSON.parse(event.body)
    }
    // set default
    if(!body.tags) {
        callback(null, {
                    statusCode: 500,
                    headers: { 'Content-Type': 'text/plain' },
                    body: 'Could not fetch the talks. Id is null.'
        })
    }
    if(!body.nums) {
        callback(null, {
                    statusCode: 500,
                    headers: { 'Content-Type': 'text/plain' },
                    body: 'Could not fetch the talks. Id is null.'
        })
    }
    
    function search_by_tags(tags_combination, documents){
        var results = []
        documents.forEach(element => 
        {if(tags_combination.every(v => element.tags.includes(v))){results.push(element)}})
        
            results.sort(function(talk1,talk2){
                var comments1 = 0
                var comments2 = 0
                if(talk1.comments_num){
                    comments1 = Number(talk1.comments_num.replace(".",""))
                }
                if(talk2.comments_num){
                    comments2 = Number(talk2.comments_num.replace(".",""))
                }
                return comments1 - comments2;
            })
            
            return results[results.length-1]
        
    }
    
        function combine(a, min) {
            var fn = function(n, src, got, all) {
                if (n == 0) {
                    if (got.length > 0) {
                        all[all.length] = got;
                    }
                    return;
                }
                for (var j = 0; j < src.length; j++) {
                    fn(n - 1, src.slice(j + 1), got.concat([src[j]]), all);
                }
                return;
            }
        var all = [];
        for (var i = min; i < a.length; i++) {
            fn(i, a, [], all);
        }
        all.push(a);
        return all;

    }
    
    connect_to_db().then(() => {
        var combinations = combine(body.tags,1)
        var map = {}
        var comb_points = []
        
        for(var i=0;i<body.tags.length;i++){
            map[body.tags[i]] = body.nums[i];
        }
        
        console.log(combinations)
        var talks_max_comments = []
        talk.find().then(documents => {
            
            combinations.forEach(combination => {
                talks_max_comments.push(search_by_tags(combination, documents));
                let points = 0
                combination.forEach(tag => {points += map[tag]})
                comb_points.push(points)
                
            })
            var max = 0
            var winnerID
            for(var i = 0; i<combinations.length;i++){
                if(talks_max_comments[i]){
                    if(!talks_max_comments[i].comments_num){
                        talks_max_comments[i].comments_num = 0
                    }
                    let score = talks_max_comments[i].comments_num * comb_points[i]
                    if(score>max){
                        max = score
                        winnerID = talks_max_comments[i].id
                    }
                }
            }
             callback(null, {
                    statusCode: 200,
                        body: "suggeriamo: " + winnerID
                })
        });
    })
     .catch(err =>
                callback(null, {
                    statusCode: err.statusCode || 500,
                    headers: { 'Content-Type': 'text/plain' },
                    body: 'Could not fetch the talks.'
                })
            );
};
