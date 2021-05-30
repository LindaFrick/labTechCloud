const mongoose = require('mongoose');

const talk_schema = new mongoose.Schema({
    _id:String,
    title: String,
    url: String,
    details: String,
    main_speaker: String,
    watch_next_ids: Array,
    watch_next_urls: Array
}, { collection: 'tedx_data' });

module.exports = mongoose.model('talk', talk_schema);
