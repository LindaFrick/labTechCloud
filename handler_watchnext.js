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
        talk.find({_id: body._id})
            .then(talks => {
                    callback(null, {
                        statusCode: 200,
                        //body: '{"ids":['+talks[0].watch_next_ids+'],"urls":"['+talks[0].watch_next_urls+']"}'
                        body: '{"ids":' + JSON.stringify(talks[0].watch_next_ids) + ',\n"urls":' + JSON.stringify(talks[0].watch_next_urls) + '}'
                    })
                }
            )
            .catch(err =>
                callback(null, {
                    statusCode: err.statusCode || 500,
                    headers: { 'Content-Type': 'text/plain' },
                    body: 'Could not fetch the talks.'
                })
            );
    });
};
