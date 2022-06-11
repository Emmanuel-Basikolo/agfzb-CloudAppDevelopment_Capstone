/**
 * Get all dealerships
 */

 const Cloudant = require('@cloudant/cloudant');
 const COUCH_URL = "hidden";
 const IAM_API_KEY = "hidden";

 async function main(params) {

    const cloudant = Cloudant({
        url: COUCH_URL,
        plugins: { iamauth: { iamApiKey: IAM_API_KEY } }
    });
 
 
     try {
         let dbList = await cloudant.db.list();
         return { "dbs": dbList };
     } catch (error) {
         return { error: error.description };
     }
 
 }

result = main(COUCH_URL, IAM_API_KEY);
console.log(result);

result.then(function(result) {
    console.log(result) // "Some User token"
 })