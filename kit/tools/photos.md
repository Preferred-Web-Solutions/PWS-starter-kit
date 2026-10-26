# Getting a business's photos when the workspace can't reach the site

Ask the user for permission before any download. Photos belong to the business (or the photographer):
credit them in the footer, and list "confirm photo use with the owner" in the handoff.

1. Open the page in the built-in browser and collect image URLs with the javascript tool.
   - Wix originals: `static.wixstatic.com/media/<id>/v1/fit/w_2000,h_2000,q_90/f.jpg`
   - Google Maps owner photos (Photos → gallery): `lh3.googleusercontent.com/gps-cs-s/<id>` then append `=w2200`
   - Yelp: `s3-media0.fl.yelpcdn.com/bphoto/<id>/o.jpg`
2. For big galleries (hundreds of photos), first inject a numbered grid overlay of thumbnails
   (`<img src="...=w400">` with big index labels) and screenshot it, then pick the 20-60 best.
3. Fetch the picks in the page with `fetch(url,{credentials:'omit'})`, turn each into a data URL with FileReader,
   put them all in one object `{key: dataURL}`, and download ONE JSON file with a temporary `<a download>`.
4. The file lands in the user's Downloads as a `.tmp` name. List Downloads, take the newest by modified time,
   stage it, and decode with Python into `src/<key>.jpg`.
5. Look at every photo. Crop out faces of customers or bystanders, other businesses' brands and signs, and
   anything that doesn't match the business. The owner's own photo is fine on an About page with a "confirm" note.
