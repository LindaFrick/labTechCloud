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
    
    async function search_by_tags(tags_combination){
        console.log("ciao search")
        //return talk.find(element => {tags_combination.every(v => element.tags.includes(v))})
        return talk.find({ tags: { $in: ["TED","talks"] }})
        .then(results => {
            console.log(results)
            results.sort(function(talk1,talk2){
                var comments1 = Number(talk1.comments_num.replace(".",""))
                var comments2 = Number(talk2.comments_num.replace(".",""))
                return comments1 - comments2;
            })
            
            return results[results.length-1]
        });
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
        var res = combine(body.tags,1)
        console.log(res)
        var talks_max_comments = []
        res.forEach(combination => {talks_max_comments.push(search_by_tags(combination))})
        Promise.all(talks_max_comments).then(value => console.log(value))
        
    });
};
