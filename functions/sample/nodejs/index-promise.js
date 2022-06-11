/**
 * Get all dealerships
 */

const COUCH_URL = "hidden";
const IAM_API_KEY = "hidden";

const Cloudant = require('@cloudant/cloudant');

function main(COUCH_URL, IAM_API_KEY) {

    const cloudant = Cloudant({
        url: COUCH_URL,
        plugins: { iamauth: { iamApiKey: IAM_API_KEY } }
    });

    let dbListPromise = getDbs(cloudant);
    return dbListPromise;
}

function getDbs(cloudant) {
    return new Promise((resolve, reject) => {
        cloudant.db.list()
            .then(body => {
                resolve({ dbs: body });
            })
            .catch(err => {
                reject({ err: err });
            });
    });
}

result = main(COUCH_URL, IAM_API_KEY);
console.log(result);

result.then(function(result) {
    console.log(result) // "Some User token"
 })