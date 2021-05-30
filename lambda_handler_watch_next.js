const connect_to_db = require('./db');

// GET BY TALK HANDLER

const talk = require('./talk');

module.exports.get_by_talk = (event, context, callback) => {
    context.callbackWaitsForEmptyEventLoop = false;
    console.log('Received event:', JSON.stringify(event, null, 2));
    let body = {}
    if (event.body) {
        body = JSON.parse(event.body)
    }
    // set default
    if(!body._id) {
        callback(null, {
                    statusCode: 500,
                    headers: { 'Content-Type': 'text/plain' },
                    body: 'Could not fetch the talks. Id is null.'
        })
    }
    
    connect_to_db().then(() => {
        console.log('=> get_all watch_next');
        var watch_next_ids
        var url_watch_next
        var titles = []
        var promises = []
        talk.find({_id: body._id})
            .then(talks => {
                watch_next_ids = talks[0].watch_next_ids;
                url_watch_next = talks[0].watch_next_urls;
                watch_next_ids.forEach(id => {
                    promises.push(talk.find({_id:id})
                        .then(talk2=> {
                            if(talk2 && talk2[0] && talk2[0].title){
                                titles.push(talk2[0].title)
                            }
                        })
                    )}
                )
                
                Promise.all(promises).then(val => {
                callback(null, {
                    statusCode: 200,
                    body: '{"ids":' + JSON.stringify(watch_next_ids) + ',\n"urls":' + JSON.stringify(url_watch_next) + ',\n"titles":'+JSON.stringify(titles)+'}'
                })})
            })
            .catch(err =>
                callback(null, {
                    statusCode: err.statusCode || 500,
                    headers: { 'Content-Type': 'text/plain' },
                    body: 'Could not fetch the talks.'
                })
            )
    });
};
