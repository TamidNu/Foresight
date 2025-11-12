'''

POST api/hotel
Creates a new hotel
Headers:
Authorization: Bearer <JWT>  // maybe if we restrict who can create/edit a hotel
Content-Type: application/json
Accept: application/json


PUT api/hotel/<hotel id>
Updates hotel information
Headers:
Authorization: Bearer <JWT>  // maybe if we restrict who can create/edit a hotel
Content-Type: application/json
Accept: application/json



DELETE api/hotel/<hotel id>
Deletes the hotel with the given id (or we could use hotel name)
Headers:
Authorization: Bearer <JWT>  // maybe if we restrict who can create/edit a hotel
Accept: application/json



GET api/hotel/<hotel id>
Gets information about the hotel given the hotel id (or name)
Headers:
Authorization: Bearer <JWT>  // maybe if we restrict who can create/edit a hotel
Content-Type: application/json
Accept: application/json
'''