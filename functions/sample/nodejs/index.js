/**
 * Get all dealerships
 */

const COUCH_URL = "hidden";
const IAM_API_KEY = "hidden";

const Cloudant = require('@cloudant/cloudant');

function main() {

    const cloudant = Cloudant({
        url: COUCH_URL,
        plugins: { iamauth: { iamApiKey: IAM_API_KEY } }
    });

    let dbList = getDbs(cloudant);
    return { dbs: dbList };
}

function getDbs(cloudant) {
    dbList = [];
    cloudant.db.list().then((body) => {
        body.forEach((db) => {
            dbList.push(db);
        });
    }).catch((err) => { console.log(err); });
}

result = main(COUCH_URL, IAM_API_KEY);
console.log(result);